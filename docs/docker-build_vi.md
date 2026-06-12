# Cách build image Docker local

Hiện dự án đã có cơ chế build Docker tự động trên GitHub. Tài liệu này dành cho những ai muốn tự build image Docker tại máy local.

1. Cài Docker:
```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

2. Build image:
```bash
echo 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 | docker login ghcr.io -u tungpv90 --password-stdin

docker build -t xiaozhi-esp32-server:server-base -f ./Dockerfile-server-base .
docker tag xiaozhi-esp32-server:server-base ghcr.io/tungpv90/xiaozhi-esp32-server:server-base
docker push ghcr.io/tungpv90/xiaozhi-esp32-server:server-base

docker build -t xiaozhi-esp32-server:server_latest -f ./Dockerfile-server .
docker tag xiaozhi-esp32-server:server_latest ghcr.io/tungpv90/xiaozhi-esp32-server:server_latest
docker push ghcr.io/tungpv90/xiaozhi-esp32-server:server_latest

docker build -t xiaozhi-esp32-server:web_latest -f ./Dockerfile-web .
docker tag xiaozhi-esp32-server:web_latest ghcr.io/tungpv90/xiaozhi-esp32-server:web_latest
docker push ghcr.io/tungpv90/xiaozhi-esp32-server:web_latest
```

Sau khi build xong, bạn có thể dùng `docker-compose` để khởi động dự án. Hãy nhớ sửa `docker-compose.yml` để trỏ tới image bạn tự build.

```bash
cd main/xiaozhi-server
docker-compose up -d
```

## Dọn dẹp

```bash
docker compose -f docker-compose_all.yml down

docker stop xiaozhi-esp32-server
docker rm xiaozhi-esp32-server

docker stop xiaozhi-esp32-server-web
docker rm xiaozhi-esp32-server-web

docker stop xiaozhi-esp32-server-db
docker rm xiaozhi-esp32-server-db

docker stop xiaozhi-esp32-server-redis
docker rm xiaozhi-esp32-server-redis

docker rmi ghcr.io/tungpv90/xiaozhi-esp32-server:server_latest
docker rmi ghcr.io/tungpv90/xiaozhi-esp32-server:web_latest
```
