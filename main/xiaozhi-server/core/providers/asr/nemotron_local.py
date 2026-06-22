import asyncio
import json
import os
import time
import wave
from typing import Dict, List, Optional, Tuple

import numpy as np

from config.logger import setup_logging
from core.providers.asr.base import ASRProviderBase
from core.providers.asr.dto.dto import InterfaceType

TAG = __name__
logger = setup_logging()


class ASRProvider(ASRProviderBase):
    def __init__(self, config: dict, delete_audio_file: bool):
        super().__init__()
        self.interface_type = InterfaceType.LOCAL
        self.model_dir = config.get("model_dir")
        self.output_dir = config.get("output_dir", "tmp/")
        self.backend = config.get("backend", "sherpa_onnx")
        self.model_type = config.get("model_type", "nemo_ctc")
        self.sample_rate = int(config.get("sample_rate", 16000))
        self.num_threads = int(config.get("num_threads", 4))
        self.blank_id = int(config.get("blank_id", 0))
        self.max_symbols_per_step = int(config.get("max_symbols_per_step", 5))
        self.delete_audio_file = delete_audio_file

        if not self.model_dir:
            raise ValueError("NemotronASR.model_dir is required")

        os.makedirs(self.output_dir, exist_ok=True)

        if self.backend == "sherpa_onnx":
            self.model = self._init_sherpa_onnx(config)
        elif self.backend == "onnxruntime":
            self.model = self._init_onnxruntime(config)
        else:
            raise ValueError(
                f"Unsupported NemotronASR backend: {self.backend}. "
                "Use 'sherpa_onnx' or 'onnxruntime'."
            )

    def requires_file(self) -> bool:
        return True

    def _path(self, *names: str) -> str:
        return os.path.join(self.model_dir, *names)

    def _first_existing(self, *names: str) -> Optional[str]:
        for name in names:
            path = self._path(name)
            if os.path.isfile(path):
                return path
        return None

    def _init_sherpa_onnx(self, config: dict):
        try:
            import sherpa_onnx
        except ImportError as e:
            raise ImportError(
                "NemotronASR backend 'sherpa_onnx' requires sherpa_onnx. "
                "Install requirements.txt first."
            ) from e

        tokens = config.get("tokens") or self._first_existing("tokens.txt", "vocab.txt")
        if not tokens:
            raise FileNotFoundError(
                "NemotronASR requires tokens.txt or vocab.txt in model_dir "
                "when using sherpa_onnx."
            )

        model = config.get("model") or self._first_existing(
            "model.int8.onnx",
            "model.int4.onnx",
            "model.onnx",
            "encoder.int8.onnx",
            "encoder.onnx",
        )
        if not model:
            raise FileNotFoundError("No ONNX model file found in NemotronASR.model_dir")

        kwargs = {
            "tokens": tokens,
            "num_threads": self.num_threads,
            "sample_rate": self.sample_rate,
            "feature_dim": int(config.get("feature_dim", 80)),
            "decoding_method": config.get("decoding_method", "greedy_search"),
            "debug": bool(config.get("debug", False)),
        }

        if self.model_type == "nemo_ctc":
            factory = getattr(sherpa_onnx.OfflineRecognizer, "from_nemo_ctc", None)
            if factory is None:
                raise RuntimeError(
                    "Installed sherpa_onnx does not expose OfflineRecognizer.from_nemo_ctc"
                )
            return factory(model=model, **kwargs)

        if self.model_type == "sense_voice":
            return sherpa_onnx.OfflineRecognizer.from_sense_voice(
                model=model, use_itn=bool(config.get("use_itn", True)), **kwargs
            )

        if self.model_type == "paraformer":
            return sherpa_onnx.OfflineRecognizer.from_paraformer(
                paraformer=model, **kwargs
            )

        if self.model_type == "transducer":
            encoder = config.get("encoder") or self._first_existing(
                "encoder.int8.onnx", "encoder.onnx"
            )
            decoder = config.get("decoder") or self._first_existing(
                "decoder.int8.onnx", "decoder.onnx"
            )
            joiner = config.get("joiner") or self._first_existing(
                "joiner.int8.onnx", "joiner.onnx"
            )
            if not all([encoder, decoder, joiner]):
                raise FileNotFoundError(
                    "Transducer model requires encoder, decoder, and joiner ONNX files."
                )
            return sherpa_onnx.OfflineRecognizer.from_transducer(
                encoder=encoder, decoder=decoder, joiner=joiner, **kwargs
            )

        raise ValueError(f"Unsupported sherpa_onnx model_type: {self.model_type}")

    def _init_onnxruntime(self, config: dict):
        try:
            import onnxruntime as ort
        except ImportError as e:
            raise ImportError(
                "NemotronASR backend 'onnxruntime' requires onnxruntime. "
                "Install it with: pip install onnxruntime"
            ) from e

        session_options = ort.SessionOptions()
        session_options.intra_op_num_threads = self.num_threads
        session_options.inter_op_num_threads = max(1, int(config.get("inter_op_threads", 1)))

        encoder_path = config.get("encoder") or self._first_existing("encoder.onnx")
        decoder_joiner_path = config.get("decoder_joiner") or self._first_existing(
            "decoder_joiner.onnx"
        )
        if encoder_path and decoder_joiner_path:
            return self._init_nemotron_streaming_onnx(
                config, ort, encoder_path, decoder_joiner_path, session_options
            )

        model_path = config.get("model") or self._first_existing(
            "model.int8.onnx", "model.int4.onnx", "model.onnx"
        )
        if not model_path:
            raise FileNotFoundError("No ONNX model file found in NemotronASR.model_dir")

        providers = config.get("providers") or ["CPUExecutionProvider"]
        session = ort.InferenceSession(
            model_path, sess_options=session_options, providers=providers
        )

        tokens_path = config.get("tokens") or self._first_existing("tokens.txt", "vocab.txt")
        tokens = self._load_tokens(tokens_path) if tokens_path else None
        return {"layout": "ctc", "session": session, "tokens": tokens}

    def _init_nemotron_streaming_onnx(
        self, config: dict, ort, encoder_path: str, decoder_joiner_path: str, session_options
    ):
        providers = config.get("providers") or ["CPUExecutionProvider"]
        encoder = ort.InferenceSession(
            encoder_path, sess_options=session_options, providers=providers
        )
        decoder_joiner = ort.InferenceSession(
            decoder_joiner_path, sess_options=session_options, providers=providers
        )

        tokenizer_path = config.get("tokenizer") or self._first_existing(
            "tokenizer.model"
        )
        tokenizer = self._load_sentencepiece(tokenizer_path) if tokenizer_path else None

        config_path = self._first_existing("config.json")
        model_config = {}
        if config_path:
            with open(config_path, "r", encoding="utf-8") as f:
                model_config = json.load(f)

        vocab_size = int(
            config.get(
                "vocab_size",
                model_config.get(
                    "vocab_size",
                    tokenizer.get_piece_size() if tokenizer is not None else 0,
                ),
            )
        )
        blank_id = int(config.get("blank_id", model_config.get("blank_id", vocab_size)))

        logger.bind(tag=TAG).info(
            "Loaded Nemotron streaming ONNX: encoder inputs={}, decoder_joiner inputs={}",
            self._describe_onnx_io(encoder.get_inputs()),
            self._describe_onnx_io(decoder_joiner.get_inputs()),
        )

        return {
            "layout": "nemotron_streaming",
            "encoder": encoder,
            "decoder_joiner": decoder_joiner,
            "tokenizer": tokenizer,
            "blank_id": blank_id,
            "vocab_size": vocab_size,
            "config": model_config,
        }

    def _describe_onnx_io(self, values) -> List[str]:
        return [f"{value.name}:{value.shape}:{value.type}" for value in values]

    def _load_sentencepiece(self, path: str):
        try:
            import sentencepiece as spm
        except ImportError as e:
            raise ImportError(
                "NemotronASR tokenizer.model requires sentencepiece. "
                "Install requirements.txt first."
            ) from e

        tokenizer = spm.SentencePieceProcessor()
        tokenizer.load(path)
        return tokenizer

    def _load_tokens(self, path: str) -> List[str]:
        tokens = []
        with open(path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 2 and parts[-1].isdigit():
                    tokens.append(" ".join(parts[:-1]))
                else:
                    tokens.append(parts[0])
        return tokens

    def _read_wave(self, wave_filename: str) -> Tuple[np.ndarray, int]:
        with wave.open(wave_filename) as f:
            if f.getnchannels() != 1:
                raise ValueError("NemotronASR expects mono wav input")
            if f.getsampwidth() != 2:
                raise ValueError("NemotronASR expects 16-bit wav input")
            samples = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)
            return samples.astype(np.float32) / 32768.0, f.getframerate()

    def _resample_if_needed(self, samples: np.ndarray, sample_rate: int) -> np.ndarray:
        if sample_rate == self.sample_rate:
            return samples
        target_len = int(round(len(samples) * self.sample_rate / sample_rate))
        if target_len <= 0:
            return samples
        old_x = np.linspace(0, 1, num=len(samples), endpoint=False)
        new_x = np.linspace(0, 1, num=target_len, endpoint=False)
        return np.interp(new_x, old_x, samples).astype(np.float32)

    def _decode_ids(self, ids: np.ndarray, tokens: Optional[List[str]]) -> str:
        if tokens is None:
            return " ".join(str(int(i)) for i in ids if int(i) != self.blank_id)

        pieces = []
        previous = None
        for raw_id in ids:
            token_id = int(raw_id)
            if token_id == self.blank_id or token_id == previous:
                previous = token_id
                continue
            previous = token_id
            if token_id >= len(tokens):
                continue
            token = tokens[token_id]
            if token in {"<blk>", "<blank>", "<eps>", "<pad>", "<s>", "</s>"}:
                continue
            pieces.append(token)

        text = "".join(pieces)
        return text.replace("▁", " ").replace("@@ ", "").strip()

    def _recognize_with_onnxruntime(self, file_path: str) -> str:
        samples, sample_rate = self._read_wave(file_path)
        samples = self._resample_if_needed(samples, sample_rate)

        if self.model.get("layout") == "nemotron_streaming":
            return self._recognize_with_nemotron_streaming(file_path)

        session = self.model["session"]
        tokens = self.model["tokens"]
        inputs = session.get_inputs()
        feed = {}

        audio = samples.reshape(1, -1).astype(np.float32)
        length = np.asarray([audio.shape[1]], dtype=np.int64)
        for inp in inputs:
            name = inp.name.lower()
            if "length" in name or name in {"x_lens", "audio_lens"}:
                feed[inp.name] = length
            else:
                feed[inp.name] = audio

        outputs = session.run(None, feed)
        result = outputs[0]
        if result.ndim == 3:
            ids = np.argmax(result[0], axis=-1)
        elif result.ndim == 2:
            ids = result[0]
        else:
            ids = result.reshape(-1)

        return self._decode_ids(ids, tokens)

    def _make_zeros_for_input(self, inp):
        shape = []
        for dim in inp.shape:
            if isinstance(dim, int) and dim > 0:
                shape.append(dim)
            else:
                shape.append(1)

        dtype = np.float32
        if "int64" in inp.type:
            dtype = np.int64
        elif "int32" in inp.type:
            dtype = np.int32
        elif "bool" in inp.type:
            dtype = bool
        return np.zeros(shape, dtype=dtype)

    def _run_encoder_streaming(self, samples: np.ndarray):
        encoder = self.model["encoder"]
        inputs = encoder.get_inputs()
        feed = {}
        audio = samples.reshape(1, -1).astype(np.float32)
        length = np.asarray([audio.shape[1]], dtype=np.int64)

        for inp in inputs:
            name = inp.name.lower()
            if "length" in name or "len" in name:
                feed[inp.name] = length
            elif "audio" in name or "signal" in name or name in {"x", "input"}:
                feed[inp.name] = audio
            else:
                feed[inp.name] = self._make_zeros_for_input(inp)

        try:
            return encoder.run(None, feed)
        except Exception as e:
            raise RuntimeError(
                "Nemotron encoder ONNX input mapping failed. "
                f"Inputs: {self._describe_onnx_io(inputs)}. Original error: {e}"
            ) from e

    def _run_decoder_joiner_step(self, enc_frame: np.ndarray, last_token: int):
        decoder_joiner = self.model["decoder_joiner"]
        inputs = decoder_joiner.get_inputs()
        feed = {}
        token = np.asarray([[last_token]], dtype=np.int64)
        token_len = np.asarray([1], dtype=np.int64)

        if enc_frame.ndim == 1:
            enc_frame = enc_frame.reshape(1, 1, -1)
        elif enc_frame.ndim == 2:
            enc_frame = enc_frame.reshape(1, 1, enc_frame.shape[-1])

        for inp in inputs:
            name = inp.name.lower()
            if "target" in name or "token" in name or "label" in name or "y" == name:
                feed[inp.name] = token
            elif "length" in name or "len" in name:
                feed[inp.name] = token_len
            elif "encoder" in name or "audio" in name or "frame" in name or name in {"x"}:
                feed[inp.name] = enc_frame.astype(np.float32)
            else:
                feed[inp.name] = self._make_zeros_for_input(inp)

        try:
            outputs = decoder_joiner.run(None, feed)
        except Exception as e:
            raise RuntimeError(
                "Nemotron decoder_joiner ONNX input mapping failed. "
                f"Inputs: {self._describe_onnx_io(inputs)}. Original error: {e}"
            ) from e

        logits = outputs[0]
        return np.asarray(logits).reshape(-1)

    def _decode_sentencepiece(self, token_ids: List[int]) -> str:
        tokenizer = self.model.get("tokenizer")
        if tokenizer is None:
            return " ".join(str(token_id) for token_id in token_ids)
        return tokenizer.decode(token_ids).strip()

    def _recognize_with_nemotron_streaming(self, file_path: str) -> str:
        samples, sample_rate = self._read_wave(file_path)
        samples = self._resample_if_needed(samples, sample_rate)

        encoder_outputs = self._run_encoder_streaming(samples)
        encoded = np.asarray(encoder_outputs[0])
        if encoded.ndim == 3:
            encoded = encoded[0]
        elif encoded.ndim > 3:
            encoded = encoded.reshape(-1, encoded.shape[-1])

        blank_id = int(self.model["blank_id"])
        last_token = blank_id
        token_ids = []

        for enc_frame in encoded:
            for _ in range(self.max_symbols_per_step):
                logits = self._run_decoder_joiner_step(enc_frame, last_token)
                next_token = int(np.argmax(logits))
                if next_token == blank_id:
                    break
                token_ids.append(next_token)
                last_token = next_token

        return self._decode_sentencepiece(token_ids)

    def _recognize_with_sherpa_onnx(self, file_path: str) -> str:
        samples, sample_rate = self._read_wave(file_path)
        stream = self.model.create_stream()
        stream.accept_waveform(sample_rate, samples)
        self.model.decode_stream(stream)
        return stream.result.text

    async def speech_to_text(
        self,
        opus_data: List[bytes],
        session_id: str,
        audio_format="opus",
        artifacts=None,
    ) -> Tuple[Optional[str], Optional[str]]:
        if artifacts is None or not artifacts.file_path:
            return "", None

        file_path = artifacts.file_path
        try:
            start_time = time.time()
            if self.backend == "onnxruntime":
                text = await asyncio.to_thread(
                    self._recognize_with_onnxruntime, file_path
                )
            else:
                text = await asyncio.to_thread(
                    self._recognize_with_sherpa_onnx, file_path
                )

            logger.bind(tag=TAG).debug(
                f"NemotronASR cost: {time.time() - start_time:.3f}s | result: {text}"
            )
            return text, file_path
        except Exception as e:
            logger.bind(tag=TAG).error(f"NemotronASR failed: {e}", exc_info=True)
            return "", file_path
