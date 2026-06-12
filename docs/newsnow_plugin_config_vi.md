# Hướng dẫn cấu hình nguồn tin tức cho plugin `get_news_from_newsnow`

## Tổng quan

Plugin `get_news_from_newsnow` hiện hỗ trợ cấu hình nguồn tin tức trực tiếp từ giao diện web, không cần sửa code. Bạn có thể cấu hình nguồn khác nhau cho từng agent.

## Cách cấu hình

### 1. Qua giao diện web

1. Đăng nhập `智控台`
2. Vào trang `角色配置`
3. Chọn agent cần cấu hình
4. Bấm `编辑功能`
5. Ở phần tham số bên phải tìm plugin `newsnow新闻聚合`
6. Nhập tên nguồn tin tức tiếng Trung, phân tách bằng dấu chấm phẩy

### 2. Qua file cấu hình

Trong `config.yaml`:

```yaml
plugins:
  get_news_from_newsnow:
    url: "https://newsnow.busiyi.world/api/s?id="
    news_sources: "澎湃新闻;百度热搜;财联社;微博;抖音"
```

## Định dạng nguồn tin tức

```text
中文名称1;中文名称2;中文名称3
```

Ví dụ:

```text
澎湃新闻;百度热搜;财联社;微博;抖音;知乎;36氪
```

## Nguồn hỗ trợ

Một số nguồn phổ biến:

- 澎湃新闻
- 百度热搜
- 财联社
- 微博
- 抖音
- 知乎
- 36氪
- 华尔街见闻
- IT之家
- 今日头条
- 虎扑
- 哔哩哔哩
- 快手
- 雪球
- 格隆汇
- 金十数据
- 以及更多

## Mặc định

Nếu không cấu hình gì, plugin sẽ dùng:

```text
澎湃新闻;百度热搜;财联社
```

## Cách dùng

1. Cấu hình nguồn tin tức bằng UI hoặc file
2. Gọi plugin bằng câu như "đọc tin tức" hoặc "lấy tin"
3. Chỉ định nguồn bằng câu như "đọc tin 澎湃新闻"
4. Hỏi chi tiết một tin nếu cần

## Cách hoạt động

1. Plugin nhận tên nguồn tiếng Trung
2. Chuyển sang ID nguồn tương ứng
3. Gọi API lấy dữ liệu
4. Trả tin tức cho người dùng

## Lưu ý

- Tên nguồn phải khớp chính xác với `CHANNEL_MAP`
- Đổi cấu hình xong cần restart hoặc reload
- Nếu nguồn không hợp lệ, plugin sẽ dùng mặc định
- Các nguồn cách nhau bằng dấu chấm phẩy ASCII `;`
