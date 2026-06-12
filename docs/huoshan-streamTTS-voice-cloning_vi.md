# Hướng dẫn cấu hình clone giọng + TTS streaming của Volcengine trên智控台

Tài liệu này chia thành 4 giai đoạn: chuẩn bị, cấu hình, clone và sử dụng.

## Giai đoạn 1: Chuẩn bị

Siêu quản trị viên cần kích hoạt dịch vụ Volcengine trước, lấy `App Id` và `Access Token`. Mỗi tài nguyên giọng có một `声音ID (S_xxxxx)`.

Nếu muốn clone nhiều giọng, bạn phải mua nhiều tài nguyên giọng và gán từng `S_xxxxx` cho tài khoản hệ thống.

### 1. Kích hoạt dịch vụ Volcengine

Truy cập:
https://console.volcengine.com/speech/app

Trong ứng dụng, bật `语音合成大模型` và `声音复刻大模型`.

### 2. Lấy ID tài nguyên giọng

Truy cập:
https://console.volcengine.com/speech/service/9999

Sao chép 3 thông tin:

- `App Id`
- `Access Token`
- `声音ID(S_xxxxx)`

## Giai đoạn 2: Cấu hình Volcengine

### 1. Điền thông tin Volcengine

Đăng nhập `智控台`, vào `模型配置` -> `语音合成`, tìm `火山双流式语音合成`, bấm `修改` và điền:

- `App Id` vào `应用ID`
- `Access Token` vào `访问令牌`

Lưu lại.

### 2. Gán tài nguyên giọng cho tài khoản

Đăng nhập `智控台`, vào `参数字典` -> `系统功能配置`, tick `音色克隆`, lưu lại.

Sau đó vào `音色克隆` -> `音色资源`:

- `平台名称`: chọn `火山双流式语音合成`
- `音色资源ID`: nhập `S_xxxxx`
- `归属账号`: chọn tài khoản cần gán

Lưu lại.

## Giai đoạn 3: Clone

Nếu vào `音色克隆` mà thấy thông báo chưa có tài nguyên, nghĩa là bạn chưa gán giọng cho tài khoản đó.

Khi đã thấy danh sách giọng:

1. Chọn một tài nguyên giọng
2. Bấm `上传音频`
3. Nghe thử, cắt đoạn nếu cần, rồi xác nhận upload
4. Sau upload, trạng thái sẽ thành `待复刻`
5. Bấm `立即复刻`

Nếu thất bại, xem `错误信息`.

Nếu thành công, trạng thái sẽ là `训练成功`. Bạn có thể đổi tên ở cột `声音名称`.

## Giai đoạn 4: Sử dụng

Vào `智能体管理`, chọn agent, bấm `配置角色`.

Chọn TTS là `火山双流式语音合成`, sau đó chọn giọng clone mong muốn và lưu.

Sau đó đánh thức Xiaozhi và trò chuyện.
