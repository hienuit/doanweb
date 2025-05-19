document.addEventListener('alpine:init', () => {
    // Log dữ liệu gốc từ server để debug
    console.log("User data received from server:", userFromServer);
    
    
    Alpine.data('dashboard', () => ({
        historyLimit: 4,
        showAllHistory: false,
        activeTab: 'profile',
        showDeleteModal: false,
        isEditMode: false,
        showPasswordModal: false,
        isGoogleUser: userFromServer.is_google_user,
        user: userFromServer,
        history: historyFromServer || [],
        getBirthYears() {
            const currentYear = new Date().getFullYear();
            const years = [];
            for (let i = 0; i < 40; i++) {
                years.push(currentYear - i);
            }
            return years;
        },
        toggleHistoryView() {
            this.showAllHistory = !this.showAllHistory;
        },
        updateHistory() {
            fetch('/get_latest_activities')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.history = data.history || [];
                    }
                })
                .catch(error => {
                    console.error('Error fetching activities:', error);
                });
        },

        init() {
            // Đảm bảo history được khởi tạo
            if (!this.history) this.history = [];
            
            // Xử lý ngày sinh từ chuỗi birth_date (nếu có)
            console.log("Birth date from server:", this.user.birth_date);
            
            this.user.birthYear = String(this.user.birthYear || '');
            this.user.birthMonth = String(this.user.birthMonth || '');
            this.user.birthDay = String(this.user.birthDay || '');

            
            // Tự động cập nhật lịch sử mỗi 30 giây
            setInterval(() => {
                if (this.activeTab === 'history') {
                    this.updateHistory();
                }
            }, 30000);
        },
        toggleEdit() {
            this.isEditMode = !this.isEditMode;
        },
        saveChanges() {
            // Lưu giá trị ngày sinh thành chuỗi birth_date trước khi gửi
            if (this.user.birthDay && this.user.birthMonth && this.user.birthYear) {
                // Đảm bảo tháng và ngày có 2 chữ số
                const month = this.user.birthMonth.toString().padStart(2, '0');
                const day = this.user.birthDay.toString().padStart(2, '0');
                this.user.birth_date = `${this.user.birthYear}-${month}-${day}`;
                console.log("Formatted birth_date for server:", this.user.birth_date);
            }
            
            this.isEditMode = false;
            fetch('/update_profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.user)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.showNotification('Đã lưu thông tin thành công!');
                } else {
                    this.showNotification('Có lỗi xảy ra: ' + data.message);
                }
            });
        },
        showNotification(message) {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.classList.remove('opacity-0');
            notification.classList.add('opacity-100');
            setTimeout(() => {
                notification.classList.remove('opacity-100');
                notification.classList.add('opacity-0');
            }, 3000);
        },
        changePassword() {
            this.showPasswordModal = true;
        },
        savePassword() {
            const currentPassword = document.getElementById('current-password').value;
            const newPassword = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;

            if (newPassword !== confirmPassword) {
                this.showNotification('Mật khẩu mới không khớp!');
                return;
            }

            fetch('/change_password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            })
            .then(response => response.json())
            .then(data => {
                this.showPasswordModal = false;
                if (data.success) {
                    this.showNotification('Đã thay đổi mật khẩu thành công!');
                    this.updateHistory();
                } else {
                    this.showNotification('Có lỗi xảy ra: ' + data.message);
                }
            });
        },
        confirmDeleteAccount() {
            this.showDeleteModal = true;
        },
        deleteAccount() {
            fetch('/delete_account', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.showNotification('Tài khoản đã được xóa thành công!');
                    setTimeout(() => window.location.href = '/login', 1500);
                } else {
                    this.showNotification('Có lỗi xảy ra: ' + data.message);
                }
            })
            .catch(error => {
                this.showNotification('Có lỗi xảy ra khi xóa tài khoản');
                console.error('Error:', error);
            });
            this.showDeleteModal = false;
        }
    }));
});