# Hướng dẫn dùng plugin thời tiết

## Tổng quan

Plugin `get_weather` là một trong các chức năng cốt lõi của Xiaozhi, cho phép hỏi thời tiết bằng giọng nói. Nó dựa trên API của QWeather và hỗ trợ thời tiết hiện tại cùng dự báo 7 ngày.

## Cách lấy API key

### 1. Đăng ký tài khoản QWeather

1. Truy cập [QWeather Console](https://console.qweather.com/)
2. Đăng ký và xác minh email
3. Đăng nhập

### 2. Tạo project và lấy API Key

1. Vào `项目管理` -> `创建项目`
2. Đặt tên project
3. Tạo credentials
4. Chọn `API Key`
5. Copy `API Key`

### 3. Lấy API Host

Vào `设置` -> `API Host` và lấy host được cấp cho bạn.

## Cách cấu hình

### Cách 1: Dùng `智控台`

1. Đăng nhập `智控台`
2. Vào `角色配置`
3. Chọn agent
4. Bấm `编辑功能`
5. Tick plugin `天气查询`
6. Điền:
   - `天气插件 API 密钥` = `API Key`
   - `开发者 API Host` = `API Host`
7. Lưu lại

### Cách 2: Dùng file config cho đơn module

```yaml
plugins:
  get_weather:
    api_key: "your-qweather-api-key"
    api_host: "your-qweather-api-host"
    default_location: "your-city"
```

