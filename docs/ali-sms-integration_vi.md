# Hướng dẫn tích hợp SMS của Alibaba Cloud

Đăng nhập vào bảng điều khiển Alibaba Cloud và mở trang "Dịch vụ SMS":
https://dysms.console.aliyun.com/overview

## Bước 1: Thêm chữ ký
![Bước](images/alisms/sms-01.png)
![Bước](images/alisms/sms-02.png)

Sau bước này, bạn sẽ có `sign_name`. Hãy điền giá trị đó vào tham số:
`aliyun.sms.sign_name`

## Bước 2: Thêm mẫu tin nhắn
![Bước](images/alisms/sms-11.png)

Sau bước này, bạn sẽ có `sms_code_template_code`. Hãy điền giá trị đó vào tham số:
`aliyun.sms.sms_code_template_code`

Lưu ý: chữ ký cần chờ 7 ngày làm việc để nhà mạng duyệt xong thì mới gửi SMS thành công.

Bạn có thể chờ duyệt xong rồi mới tiếp tục làm các bước tiếp theo.

## Bước 3: Tạo tài khoản SMS và cấp quyền

Đăng nhập Alibaba Cloud, vào trang "RAM / Quyền truy cập":
https://ram.console.aliyun.com/overview?activeTab=overview

![Bước](images/alisms/sms-21.png)
![Bước](images/alisms/sms-22.png)
![Bước](images/alisms/sms-23.png)
![Bước](images/alisms/sms-24.png)
![Bước](images/alisms/sms-25.png)

Sau bước này, bạn sẽ có `access_key_id` và `access_key_secret`. Hãy điền chúng vào:
`aliyun.sms.access_key_id`, `aliyun.sms.access_key_secret`

## Bước 4: Bật tính năng đăng ký bằng số điện thoại

1. Bình thường, sau khi điền đủ thông tin ở trên, bạn sẽ thấy giao diện như hình. Nếu không thấy, có thể bạn đã bỏ sót một bước.

![Bước](images/alisms/sms-31.png)

2. Bật cho phép người dùng không phải quản trị viên đăng ký, đặt `server.allow_user_register` thành `true`.

3. Bật tính năng đăng ký bằng điện thoại, đặt `server.enable_mobile_register` thành `true`.
![Bước](images/alisms/sms-32.png)
