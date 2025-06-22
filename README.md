# 🇻🇳 Du Lịch Việt Nam với AI - Travel Vietnam with AI

## 📖 Mô tả dự án

Ứng dụng web du lịch thông minh sử dụng AI để gợi ý địa điểm du lịch tại Việt Nam. Hệ thống giúp người dùng tìm kiếm và lập kế hoạch du lịch dựa trên sở thích cá nhân, thời gian và ngân sách.

### ✨ Tính năng chính

- 🤖 **AI Travel Assistant**: Gợi ý địa điểm và lịch trình du lịch thông minh
- 🗺️ **Bản đồ tương tác**: Hiển thị các địa điểm du lịch trên bản đồ
- 🌤️ **Dự báo thời tiết**: Thông tin thời tiết realtime cho các địa điểm
- 📅 **Lập lịch du lịch**: Tạo và quản lý lịch trình du lịch cá nhân
- 👤 **Quản lý tài khoản**: Đăng ký, đăng nhập với email hoặc OAuth (Google, Facebook)
- 📝 **Chia sẻ trải nghiệm**: Người dùng có thể chia sẻ kinh nghiệm du lịch
- 📊 **Dashboard admin**: Quản lý người dùng, nội dung và feedback
- 📱 **Responsive Design**: Giao diện thân thiện trên mọi thiết bị

## 🛠️ Công nghệ sử dụng

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login, OAuth (Google, Facebook)
- **AI**: Google Generative AI (Gemini)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Email**: Flask-Mail (SMTP)
- **Migration**: Flask-Migrate (Alembic)
- **Weather API**: OpenWeatherMap

## 📋 Yêu cầu hệ thống

- Python 3.8+
- PostgreSQL 12+
- Node.js (để chạy frontend nếu cần)
- Git

## 🚀 Hướng dẫn cài đặt

### 1. Clone repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Tạo môi trường ảo (Virtual Environment)

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Trên Windows:
venv\Scripts\activate
# Trên macOS/Linux:
source venv/bin/activate
```

### 3. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 4. Cấu hình cơ sở dữ liệu PostgreSQL

#### Cài đặt PostgreSQL:
- **Windows**: Tải từ [postgresql.org](https://www.postgresql.org/download/windows/)
- **macOS**: `brew install postgresql`
- **Ubuntu/Debian**: `sudo apt-get install postgresql postgresql-contrib`

#### Tạo database:
```bash
# Đăng nhập PostgreSQL
psql -U postgres

# Tạo database
CREATE DATABASE travel_vietnam_db;

# Tạo user (tùy chọn)
CREATE USER travel_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE travel_vietnam_db TO travel_user;

# Thoát
\q
```

### 5. Tạo file .env

Tạo file `.env` trong thư mục gốc của project với nội dung sau:

```env
# Database Configuration
SQLALCHEMY_DATABASE_URI=postgresql://postgres:your_password@localhost:5432/travel_vietnam_db

# Flask Secret Keys
SECRET_KEY=your-very-secret-key-here-change-this-in-production
SECRET_KEY_SESSION=another-secret-key-for-sessions

# Email Configuration (Gmail SMTP)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Google OAuth (Tùy chọn)
CLIENT_ID=your-google-client-id.googleusercontent.com
CLIENT_SECRET=your-google-client-secret

# Facebook OAuth (Tùy chọn)
FACEBOOK_CLIENT_ID=your-facebook-app-id
FACEBOOK_CLIENT_SECRET=your-facebook-app-secret

# Weather API (Tùy chọn)
WEATHER_API_KEY=your-openweathermap-api-key
WEATHER_BASE_URL=http://api.openweathermap.org/data/2.5

# Google AI API Key (Bắt buộc cho tính năng AI)
GOOGLE_AI_API_KEY=your-google-ai-api-key
```

### 6. Khởi tạo database

```bash
# Khởi tạo migration
flask db init

# Tạo migration đầu tiên
flask db migrate -m "Initial migration"

# Áp dụng migration
flask db upgrade
```

### 7. Tạo dữ liệu mẫu

```bash
# Chạy script tạo dữ liệu địa điểm du lịch
python seed.py
```

### 8. Tạo tài khoản admin

```bash
# Chạy script tạo admin
python create_admin.py
```

**Thông tin admin mặc định:**
- Email: `admin@example.com`
- Mật khẩu: `admin123`

> ⚠️ **Quan trọng**: Hãy thay đổi thông tin admin này ngay sau khi cài đặt!

### 9. Chạy ứng dụng

```bash
# Chạy ở chế độ development
python run.py

# Hoặc sử dụng Flask CLI
flask run
```

Truy cập ứng dụng tại: `http://localhost:5000`

## 🔧 Cấu hình nâng cao

### 🔑 Hướng dẫn lấy API Keys chi tiết

#### 1. Google AI API Key (Bắt buộc)

**Bước 1**: Truy cập [Google AI Studio](https://aistudio.google.com/)
**Bước 2**: Đăng nhập bằng tài khoản Google
**Bước 3**: Click "Get API Key" ở góc phải trên
**Bước 4**: Click "Create API Key in new project" hoặc chọn project có sẵn
**Bước 5**: Copy API key và paste vào file `.env`:
```env
GOOGLE_AI_API_KEY=AIzaSyABC123DEF456GHI789JKL012MNO345PQR
```

#### 2. Google OAuth Credentials (Tùy chọn)

**Bước 1**: Truy cập [Google Cloud Console](https://console.cloud.google.com/)
**Bước 2**: Tạo project mới:
   - Click "Select a project" → "New Project"
   - Nhập tên project → Create

**Bước 3**: Bật APIs cần thiết:
   - Vào "APIs & Services" → "Library"
   - Tìm và bật "Google+ API" và "People API"

**Bước 4**: Tạo OAuth 2.0 Credentials:
   - Vào "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Chọn "Web application"
   - Thêm Authorized redirect URIs: `http://localhost:5000/authorize/google`
   - Click "Create"

**Bước 5**: Copy Client ID và Client Secret:
```env
CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
```

#### 3. Facebook OAuth Credentials (Tùy chọn)

**Bước 1**: Truy cập [Facebook Developers](https://developers.facebook.com/)
**Bước 2**: Click "My Apps" → "Create App"
**Bước 3**: Chọn "Consumer" → "Next"
**Bước 4**: Nhập App Display Name → "Create App"
**Bước 5**: Thêm Facebook Login:
   - Click "Add Product" → Tìm "Facebook Login" → "Set Up"
   - Chọn "Web" platform
   - Nhập Site URL: `http://localhost:5000`

**Bước 6**: Cấu hình OAuth Redirect URLs:
   - Vào "Facebook Login" → "Settings"
   - Thêm Valid OAuth Redirect URIs: `http://localhost:5000/auth/facebook/callback`

**Bước 7**: Lấy App ID và App Secret:
   - Vào "Settings" → "Basic"
   - Copy App ID và App Secret
```env
FACEBOOK_CLIENT_ID=1234567890123456
FACEBOOK_CLIENT_SECRET=abcdef1234567890abcdef1234567890
```

#### 4. Gmail App Password (Cho tính năng Email)

**Bước 1**: Đăng nhập Gmail và vào [Google Account Settings](https://myaccount.google.com/)
**Bước 2**: Vào "Security" → Bật "2-Step Verification" nếu chưa có
**Bước 3**: Sau khi bật 2FA, vào "App Passwords":
   - Search "App passwords" trong account settings
   - Chọn "Mail" và "Other (custom name)"
   - Nhập tên như "Flask Travel App"
   - Click "Generate"

**Bước 4**: Copy 16-digit password:
```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=abcd efgh ijkl mnop
```

#### 5. OpenWeatherMap API Key (Tùy chọn)

**Bước 1**: Truy cập [OpenWeatherMap](https://openweathermap.org/api)
**Bước 2**: Click "Sign Up" để tạo tài khoản miễn phí
**Bước 3**: Xác nhận email đăng ký
**Bước 4**: Đăng nhập và vào "My API Keys"
**Bước 5**: Copy Default API key hoặc tạo mới:
```env
WEATHER_API_KEY=abcdef1234567890abcdef1234567890
WEATHER_BASE_URL=http://api.openweathermap.org/data/2.5
```

> ⚠️ **Lưu ý quan trọng**: 
> - **KHÔNG** commit file `.env` lên Git
> - Thêm `.env` vào file `.gitignore`
> - Các API key này chỉ dùng cho development
> - Sử dụng environment variables cho production

### 🔐 Bảo mật API Keys

```bash
# Thêm vào .gitignore
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
```

### 🧪 Test API Keys

Sau khi cấu hình, bạn có thể test các API:

```bash
# Test Google AI
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=YOUR_API_KEY"

# Test Weather API
curl "http://api.openweathermap.org/data/2.5/weather?q=Hanoi&appid=YOUR_WEATHER_API_KEY"
```

## 📁 Cấu trúc thư mục

```
chinhsua1/
├── app/
│   ├── __init__.py                 # Factory pattern cho Flask app
│   ├── extension.py                # Khởi tạo extensions (DB, OAuth, Mail)
│   ├── utils.py                    # Utility functions
│   ├── admin/                      # Module admin
│   │   ├── __init__.py
│   │   ├── models.py              # Model Admin
│   │   └── routes.py              # Routes admin
│   ├── models/                     # Database models
│   │   ├── destinations.py        # Model địa điểm du lịch
│   │   ├── users.py               # Model người dùng
│   │   ├── experiences.py         # Model trải nghiệm du lịch
│   │   ├── feedback.py            # Model feedback
│   │   ├── history.py             # Model lịch sử hoạt động
│   │   └── settings.py            # Model cài đặt hệ thống
│   ├── routes/                     # Blueprint routes
│   │   ├── __init__.py
│   │   ├── main_routes.py         # Routes chính
│   │   ├── auth_routes.py         # Routes xác thực
│   │   ├── api_routes.py          # API endpoints
│   │   ├── experience_routes.py   # Routes trải nghiệm
│   │   ├── weather_routes.py      # Routes thời tiết
│   │   └── ...
│   ├── static/                     # File static
│   │   ├── css/                   # Stylesheets
│   │   ├── js/                    # JavaScript files
│   │   ├── images/                # Hình ảnh
│   │   └── uploads/               # Upload files
│   └── templates/                  # Jinja2 templates
│       ├── base.html              # Template gốc
│       ├── index.html             # Trang chủ
│       ├── login.html             # Trang đăng nhập
│       ├── dashboard.html         # Dashboard người dùng
│       └── admin/                 # Templates admin
├── migrations/                     # Database migrations
├── config.py                      # Cấu hình ứng dụng
├── requirements.txt               # Python dependencies
├── run.py                         # Entry point
├── create_admin.py               # Script tạo admin
├── seed.py                       # Script tạo dữ liệu mẫu
└── .env                          # Biến môi trường (tạo riêng)
```

## 🔌 API Endpoints

### Authentication
- `POST /login` - Đăng nhập
- `POST /register` - Đăng ký
- `GET /logout` - Đăng xuất
- `GET /login/google` - Đăng nhập Google
- `GET /auth/facebook` - Đăng nhập Facebook

### Travel API
- `GET /search?mood=active&place=beach&location=south` - Tìm kiếm địa điểm
- `POST /api/itinerary` - Tạo lịch trình du lịch
- `GET /api/weather/current/<city>` - Thời tiết hiện tại
- `GET /api/weather/forecast/<city>` - Dự báo thời tiết

### User Management
- `GET /dashboard` - Dashboard người dùng
- `POST /upload-avatar` - Upload avatar
- `GET /get-user-experiences` - Lấy trải nghiệm của user

## 🛡️ Bảo mật

- **CSRF Protection**: Flask-WTF CSRF tokens
- **Password Hashing**: Werkzeug security
- **Session Management**: Flask-Login
- **OAuth Integration**: Authlib
- **Environment Variables**: python-dotenv
- **SQL Injection Protection**: SQLAlchemy ORM

## 📊 Database Schema

### Bảng chính:
- `user2` - Thông tin người dùng
- `destinations` - Địa điểm du lịch
- `destination_images` - Hình ảnh địa điểm
- `experiences` - Trải nghiệm du lịch
- `experience_images` - Hình ảnh trải nghiệm
- `feedback` - Phản hồi người dùng
- `user_activity` - Lịch sử hoạt động
- `admin` - Quản trị viên

## 🚀 Triển khai (Deployment)

### Sử dụng Gunicorn (Production)

```bash
# Cài đặt Gunicorn (đã có trong requirements.txt)
pip install gunicorn

# Chạy với Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Biến môi trường Production

Đảm bảo thay đổi các giá trị sau cho production:
- `SECRET_KEY` - Key bí mật mạnh
- `SQLALCHEMY_DATABASE_URI` - Database production
- Disable `debug=True` trong `run.py`

### Nginx Configuration (Tùy chọn)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/your/app/static;
    }
}
```

## 🐛 Troubleshooting

### Lỗi Database Connection
```bash
# Kiểm tra PostgreSQL đang chạy
sudo service postgresql status

# Kiểm tra connection string trong .env
echo $SQLALCHEMY_DATABASE_URI
```

### Lỗi Import Module
```bash
# Đảm bảo virtual environment được kích hoạt
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Cài đặt lại dependencies
pip install -r requirements.txt
```

### Lỗi OAuth
- Kiểm tra redirect URIs trong cấu hình OAuth
- Đảm bảo domain callback đúng
- Verify API keys trong file `.env`

## 📝 TODO / Roadmap

- [ ] Thêm tính năng chat với AI
- [ ] Tích hợp thanh toán online
- [ ] Mobile app với React Native
- [ ] Thêm nhiều ngôn ngữ (i18n)
- [ ] Tối ưu performance với Redis cache
- [ ] API rate limiting
- [ ] Unit tests và integration tests

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Liên hệ

- **Email**: your-email@example.com
- **GitHub**: [your-github-username](https://github.com/your-github-username)
- **LinkedIn**: [your-linkedin-profile](https://linkedin.com/in/your-profile)

## 🙏 Acknowledgments

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [Google AI](https://ai.google.dev/)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Bootstrap](https://getbootstrap.com/)

---

⭐ **Don't forget to star this repository if you found it helpful!** ⭐ 
