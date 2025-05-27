from app import create_app, db
from app.admin.models import Admin

def create_admin():
    app = create_app()
    with app.app_context():
        # Kiểm tra xem admin đã tồn tại chưa
        admin = Admin.query.filter_by(email='admin@example.com').first()
        if admin is None:
            # Tạo tài khoản admin mới
            admin = Admin(
                email='admin@example.com'  # Thay thế bằng email thật của bạn
            )
            admin.set_password('admin123')  # Thay đổi mật khẩu này trong môi trường thực tế
            db.session.add(admin)
            db.session.commit()
            print('Tài khoản admin đã được tạo thành công!')
            print('Email: admin@example.com')
            print('Mật khẩu: admin123')
        else:
            print('Tài khoản admin đã tồn tại!')

if __name__ == '__main__':
    create_admin() 