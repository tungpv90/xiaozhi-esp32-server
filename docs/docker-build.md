# 本地编译docker镜像方法

现在本项目已经使用github自动编译docker功能，本文档是提供给有本地编译docker镜像需求的朋友准备的。

1、安装docker
```
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
2、编译docker镜像
```
echo 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 | docker login ghcr.io -u tungpv90 --password-stdin

docker build -t xiaozhi-esp32-server:server-base -f ./Dockerfile-server-base .
docker tag xiaozhi-esp32-server:server-base ghcr.io/tungpv90/xiaozhi-esp32-server:server-base
docker push ghcr.io/tungpv90/xiaozhi-esp32-server:server-base
#进入项目根目录
# 编译server
docker build -t xiaozhi-esp32-server:server_latest -f ./Dockerfile-server .
docker tag xiaozhi-esp32-server:server_latest ghcr.io/tungpv90/xiaozhi-esp32-server:server_latest

# Push đúng
docker push ghcr.io/tungpv90/xiaozhi-esp32-server:server_latest
# 编译web
docker build -t xiaozhi-esp32-server:web_latest -f ./Dockerfile-web .
docker tag xiaozhi-esp32-server:web_latest ghcr.io/tungpv90/xiaozhi-esp32-server:web_latest
docker push ghcr.io/tungpv90/xiaozhi-esp32-server:web_latest
# 编译完成后，可以使用docker-compose启动项目
# docker-compose.yml你需要修改成自己编译的镜像版本
cd main/xiaozhi-server
docker-compose up -d
docker pull ghcr.io/tungpv90/xiaozhi-esp32-server:web_latest
cd /home/server.minica.vn/public_html/xiaozhi-server
docker compose -f docker-compose_all.yml up -d

```


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
