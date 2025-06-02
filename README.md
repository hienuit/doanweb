# Hướng dẫn tải và sử dụng trang web

## 1. Tải source code từ GitHub

- Có 2 cách tải:


  -  Cách 1: Clone repo bằng Git (nếu bạn đã cài Git)  
    Mở terminal/cmd và chạy lệnh:  
    ```
    https://github.com/hienuit/doanweb
    ```
    Sau đó vào thư mục dự án:  
    ```
    cd repository
    ```
  - Cách 2: tải trực tiếp từ trang này bằng cách truy cập trang https://github.com/hienuit/doanweb và ấn nút download
## 2. Cài đặt môi trường và thư viện cần thiết
- Trong thư mục dự án mới down về, dùng lệnh: pip install -r requirements.txt
  để tải các thư viện cần thiết
- Tạo file .evn để thêm chứa các biến môi trường cần thiết để chạy các api
- Nội dung file .evn bao gồm:
``` lấy api trên trang openweather map, đăng kí và vô trang cá nhân rồi vô mục myapi key ```
    + WEATHER_API_KEY  
      WEATHER_BASE_URL=http://api.openweathermap.org/data/2.5
``` lấy apikey cho phần đăng nhập google, vô google console control và lấy api gồm  ```
    + CLIENT_ID
      CLIENT_SECRET
``` Lấy đường dẫn cho database ```
    +SQLALCHEMY_DATABASE_URI=postgresql://postgres:yourpass@localhost:port/yourdb
``` Bao gồm yourpass là pass db của bạn , port là port trong db của bạn, mặc định là 5432, yourdb là tên db của bạn ```
    + MAIL_USERNAME=youremail: là tài khoản email của bạn
      MAIL_PASSWORD: lưu ý là app password , không phải là mật khẩu email của bạn, nếu có dấu cách thì thêm ngoặc kép vô giữa
      SECRET_KEY_SESSION=7b9f2c8d-ea41-4f6b-9a3e-1d5c0b8f3e9a-2h5k9m3n7p8r4t6w ``` ngẫu nhiên, là key cho mỗi session ```


- **Windows:**
