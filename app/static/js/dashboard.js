document.addEventListener('alpine:init', () => {
    // Log dữ liệu gốc từ server để debug
    
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
        userFeedbacks: [],
        feedbackForm: {
            subject: '',
            message: '',
            isSubmitting: false
        },
        // Thêm properties cho experiences
        experiencesToDelete: null,
        showDeleteExperienceModal: false,
        currentExperiencesPage: 1,
        experiencesData: [],
        experiencesTotal: 0,
        experiencesPages: 0,
        destinationChart: null,
        travelStyleChart: null,
        chartsInitialized: false, // Flag để đảm bảo charts chỉ khởi tạo một lần
        
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
            // Store global reference for onclick handlers
            window.dashboardInstance = this;
            
            // Đảm bảo history được khởi tạo
            if (!this.history) this.history = [];
            
            
            if (this.user.birth_date && this.user.birth_date.trim()) {
                const birthDateParts = this.user.birth_date.split('-');
                console.log("Birth date parts:", birthDateParts);
                if (birthDateParts.length === 3) {
                    this.user.birthYear = String(birthDateParts[0]);
                    this.user.birthMonth = String(parseInt(birthDateParts[1])); // Bỏ số 0 đầu
                    this.user.birthDay = String(parseInt(birthDateParts[2])); // Bỏ số 0 đầu
                } else {
                    // Fallback nếu format không đúng
                    this.user.birthYear = String(this.user.birthYear || '');
                    this.user.birthMonth = String(this.user.birthMonth || '');
                    this.user.birthDay = String(this.user.birthDay || '');
                }
            } else {
                // Nếu không có birth_date, sử dụng giá trị riêng biệt từ server nếu có
                this.user.birthYear = String(this.user.birthYear || '');
                this.user.birthMonth = String(this.user.birthMonth || '');
                this.user.birthDay = String(this.user.birthDay || '');
            }
            

            // Force DOM update để đảm bảo Alpine.js bind đúng giá trị
            this.$nextTick(() => {
                // Force refresh dropdowns nếu giá trị không khớp
                if (this.user.birthDay || this.user.birthMonth || this.user.birthYear) {
                    setTimeout(() => {
                        this.refreshBirthDateDropdowns();
                    }, 0);
                }
            });

            // Load danh sách góp ý khi khởi tạo
            this.loadFeedbackList();
            
            // Watch for tab changes to load experiences
            this.$watch('activeTab', (newTab) => {
                if (newTab === 'experiences') {
                    this.loadUserExperiences();
                    // Chỉ khởi tạo charts nếu chưa có và chưa được khởi tạo
                    if (!this.chartsInitialized) {
                        this.initCharts();
                        this.chartsInitialized = true;
                    }
                }
            });
            
            // Tự động cập nhật lịch sử mỗi 30 giây
            setInterval(() => {
                if (this.activeTab === 'history') {
                    this.updateHistory();
                }
            }, 30000);
        },
        
        // Thêm methods cho experiences
        async loadUserExperiences(page = 1) {
            try {
                const response = await fetch(`/get-user-experiences?page=${page}&per_page=5`);
                const data = await response.json();
                
                if (data.success) {
                    this.experiencesData = data.experiences;
                    this.experiencesTotal = data.total;
                    this.experiencesPages = data.pages;
                    this.currentExperiencesPage = data.current_page;
                    this.renderExperiences();
                    this.renderExperiencesPagination();
                }
            } catch (error) {
                console.error('Error loading experiences:', error);
            }
        },
        
        renderExperiences() {
            const container = document.getElementById('experiencesContainer');
            if (!container) return;
            
            if (this.experiencesData.length === 0) {
                container.innerHTML = `
                    <div class="text-center py-8">
                        <i class="fas fa-map-marked-alt text-4xl text-gray-400 mb-4"></i>
                        <h3 class="text-lg font-medium text-gray-900 mb-2">Chưa có bài đăng nào</h3>
                        <p class="text-gray-500 mb-4">Hãy chia sẻ trải nghiệm du lịch đầu tiên của bạn!</p>
                        <a href="/share-experience" class="bg-primary text-white px-6 py-3 rounded-lg hover:bg-amber-600 transition">
                            <i class="fas fa-plus mr-2"></i>Tạo bài đăng đầu tiên
                        </a>
                    </div>
                `;
                return;
            }
            
            const experiencesHtml = this.experiencesData.map(exp => `
                <div class="border rounded-lg p-4 mb-4 hover:shadow-md transition">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <h5 class="font-medium text-lg mb-2">${exp.title}</h5>
                            <p class="text-gray-600 text-sm mb-2">
                                <i class="fas fa-map-marker-alt mr-1"></i>${exp.destination}
                                <span class="ml-4"><i class="fas fa-calendar mr-1"></i>${exp.travel_date || 'Chưa cập nhật'}</span>
                            </p>
                            <p class="text-gray-700 mb-3">${exp.content}</p>
                            
                            <div class="flex items-center space-x-4 text-sm text-gray-500">
                                <span><i class="fas fa-star text-yellow-500 mr-1"></i>${exp.rating}/5</span>
                                <span><i class="fas fa-heart text-red-500 mr-1"></i>${exp.likes}</span>
                                <span><i class="fas fa-eye text-blue-500 mr-1"></i>${exp.views}</span>
                                <span><i class="fas fa-comments text-green-500 mr-1"></i>${exp.comments_count}</span>
                                <span><i class="fas fa-images text-purple-500 mr-1"></i>${exp.images_count}</span>
                            </div>
                            
                            ${exp.travel_style ? `
                                <div class="mt-2">
                                    <span class="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                                        ${this.getTravelStyleText(exp.travel_style)}
                                    </span>
                                </div>
                            ` : ''}
                            
                            ${exp.budget ? `
                                <div class="mt-2 text-sm text-gray-600">
                                    <i class="fas fa-wallet mr-1"></i>Ngân sách: ${new Intl.NumberFormat('vi-VN').format(exp.budget)}đ
                                </div>
                            ` : ''}
                        </div>
                        
                        <div class="flex flex-col space-y-2 ml-4">
                            <a href="/experience/${exp.id}" class="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 transition text-center">
                                <i class="fas fa-eye mr-1"></i>Xem
                            </a>
                            <button onclick="window.open('/experience/${exp.id}', '_blank')" class="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600 transition">
                                <i class="fas fa-external-link-alt mr-1"></i>Mở
                            </button>
                            <button onclick="window.dashboardInstance.deleteExperience(${exp.id})" class="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600 transition">
                                <i class="fas fa-trash mr-1"></i>Xóa
                            </button>
                        </div>
                    </div>
                    
                    <div class="mt-3 pt-3 border-t text-xs text-gray-500">
                        Tạo lúc: ${exp.created_at}
                        ${exp.is_featured ? '<span class="ml-2 bg-yellow-100 text-yellow-800 px-2 py-1 rounded">Nổi bật</span>' : ''}
                        ${!exp.is_approved ? '<span class="ml-2 bg-red-100 text-red-800 px-2 py-1 rounded">Chờ duyệt</span>' : ''}
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = experiencesHtml;
        },
        
        renderExperiencesPagination() {
            const container = document.getElementById('experiencesPagination');
            if (!container || this.experiencesPages <= 1) {
                container.style.display = 'none';
                return;
            }
            
            container.style.display = 'flex';
            
            let paginationHtml = '';
            
            // Previous button
            if (this.currentExperiencesPage > 1) {
                paginationHtml += `
                    <button onclick="window.dashboardInstance.loadUserExperiences(${this.currentExperiencesPage - 1})" 
                            class="px-3 py-2 mx-1 bg-white border rounded hover:bg-gray-50">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                `;
            }
            
            // Page numbers
            for (let i = 1; i <= this.experiencesPages; i++) {
                if (i === this.currentExperiencesPage) {
                    paginationHtml += `
                        <button class="px-3 py-2 mx-1 bg-primary text-white border rounded">
                            ${i}
                        </button>
                    `;
                } else {
                    paginationHtml += `
                        <button onclick="window.dashboardInstance.loadUserExperiences(${i})" 
                                class="px-3 py-2 mx-1 bg-white border rounded hover:bg-gray-50">
                            ${i}
                        </button>
                    `;
                }
            }
            
            // Next button
            if (this.currentExperiencesPage < this.experiencesPages) {
                paginationHtml += `
                    <button onclick="window.dashboardInstance.loadUserExperiences(${this.currentExperiencesPage + 1})" 
                            class="px-3 py-2 mx-1 bg-white border rounded hover:bg-gray-50">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                `;
            }
            
            container.innerHTML = paginationHtml;
        },
        
        getTravelStyleText(style) {
            const styles = {
                'solo': 'Du lịch một mình',
                'couple': 'Du lịch đôi',
                'family': 'Du lịch gia đình',
                'group': 'Du lịch nhóm'
            };
            return styles[style] || style;
        },
        
        deleteExperience(experienceId) {
            this.experiencesToDelete = experienceId;
            this.showDeleteExperienceModal = true;
        },
        
        async confirmDeleteExperience() {
            if (!this.experiencesToDelete) return;
            
            try {
                const response = await fetch('/delete-experience', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        experience_id: this.experiencesToDelete
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.showNotification('Xóa bài đăng thành công!', 'success');
                    this.loadUserExperiences(this.currentExperiencesPage);
                } else {
                    this.showNotification(data.message || 'Có lỗi xảy ra', 'error');
                }
            } catch (error) {
                this.showNotification('Có lỗi xảy ra khi xóa bài đăng', 'error');
            }
            
            this.showDeleteExperienceModal = false;
            this.experiencesToDelete = null;
        },
        
        initCharts() {
            // Khởi tạo charts sau khi DOM được render và chỉ khi chưa có charts
            this.$nextTick(() => {
                if (!this.destinationChart) {
                    this.createDestinationChart();
                }
                if (!this.travelStyleChart) {
                    this.createTravelStyleChart();
                }
            });
        },
        
        createDestinationChart() {
            const ctx = document.getElementById('destinationChart');
            if (!ctx) return;
            
            // Destroy existing chart if exists
            if (this.destinationChart) {
                this.destinationChart.destroy();
                this.destinationChart = null;
            }
            
            // Get data from template variables (will be available globally)
            const destinationData = window.destinationStatsData || [];
            
            if (destinationData.length === 0) {
                ctx.getContext('2d').clearRect(0, 0, ctx.width, ctx.height);
                return;
            }
            
            this.destinationChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: destinationData.map(d => d.destination || d[0]),
                    datasets: [{
                        data: destinationData.map(d => d.count || d[1]),
                        backgroundColor: [
                            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                            '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 0 // Tắt animation để tránh vấn đề
                    },
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        },
        
        createTravelStyleChart() {
            const ctx = document.getElementById('travelStyleChart');
            if (!ctx) return;
            
            // Destroy existing chart if exists
            if (this.travelStyleChart) {
                this.travelStyleChart.destroy();
                this.travelStyleChart = null;
            }
            
            // Get data from template variables (will be available globally)
            const travelStyleData = window.travelStyleStatsData || [];
            
            if (travelStyleData.length === 0) {
                ctx.getContext('2d').clearRect(0, 0, ctx.width, ctx.height);
                return;
            }
            
            const styleLabels = {
                'solo': 'Du lịch một mình',
                'couple': 'Du lịch đôi', 
                'family': 'Du lịch gia đình',
                'group': 'Du lịch nhóm'
            };
            
            this.travelStyleChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: travelStyleData.map(d => styleLabels[d.travel_style || d[0]] || (d.travel_style || d[0])),
                    datasets: [{
                        data: travelStyleData.map(d => d.count || d[1]),
                        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 0 // Tắt animation để tránh vấn đề
                    },
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        },
        
        toggleEdit() {
            this.isEditMode = !this.isEditMode;
        },
        saveChanges() {
            // Lưu giá trị ngày sinh thành chuỗi birth_date trước khi gửi
            if (this.user.birthDay && this.user.birthMonth && this.user.birthYear) {
                // Kiểm tra tính hợp lệ của ngày sinh
                const day = parseInt(this.user.birthDay);
                const month = parseInt(this.user.birthMonth);
                const year = parseInt(this.user.birthYear);
                
                if (day >= 1 && day <= 31 && month >= 1 && month <= 12 && year >= 1900 && year <= new Date().getFullYear()) {
                    // Đảm bảo tháng và ngày có 2 chữ số
                    const monthStr = month.toString().padStart(2, '0');
                    const dayStr = day.toString().padStart(2, '0');
                    this.user.birth_date = `${year}-${monthStr}-${dayStr}`;
                    console.log("Formatted birth_date for server:", this.user.birth_date);
                } else {
                    console.warn("Invalid birth date values:", {day, month, year});
                    // Không set birth_date nếu giá trị không hợp lệ
                    this.user.birth_date = null;
                }
            } else if (!this.user.birthDay && !this.user.birthMonth && !this.user.birthYear) {
                // Nếu tất cả đều trống, gửi chuỗi rỗng để xóa birth_date
                this.user.birth_date = "";
                console.log("Clearing birth_date");
            } else {
                // Nếu chỉ một số trường được điền, không cập nhật birth_date
                console.warn("Incomplete birth date information, not updating birth_date");
                delete this.user.birth_date; // Không gửi birth_date trong request
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
                    this.showNotification('Có lỗi xảy ra: ' + data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error updating profile:', error);
                this.showNotification('Có lỗi xảy ra khi cập nhật thông tin', 'error');
            });
        },
        showNotification(message, type = 'success') {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            
            // Xóa các class màu cũ
            notification.classList.remove('bg-green-500', 'bg-red-500', 'bg-blue-500');
            
            // Thêm class màu mới dựa trên type
            switch(type) {
                case 'error':
                    notification.classList.add('bg-red-500');
                    break;
                case 'info':
                    notification.classList.add('bg-blue-500');
                    break;
                default:
                    notification.classList.add('bg-green-500');
            }
            
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
        async deleteAccount() {
            console.log('Delete account function called');
            
            try {
                // Đầu tiên kiểm tra dữ liệu liên quan
                const checkResponse = await fetch('/check_user_data');
                const checkData = await checkResponse.json();
                
                if (checkData.success) {
                    console.log('User data check:', checkData.data);
                    this.showNotification('Đang xóa tài khoản...', 'info');
                }
                
                // Thực hiện xóa tài khoản
                const response = await fetch('/delete_account', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                console.log('Delete account response status:', response.status);
                const data = await response.json();
                console.log('Delete account response data:', data);
                
                if (data.success) {
                    this.showNotification('Tài khoản đã được xóa thành công!');
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 1500);
                } else {
                    this.showNotification('Có lỗi xảy ra: ' + data.message, 'error');
                    console.error('Delete account failed:', data.message);
                }
            } catch (error) {
                this.showNotification('Có lỗi xảy ra khi xóa tài khoản', 'error');
                console.error('Delete account error:', error);
            }
            
            this.showDeleteModal = false;
        },
        async submitFeedback() {
            try {
                // Kiểm tra dữ liệu đầu vào
                if (!this.feedbackForm.subject.trim() || !this.feedbackForm.message.trim()) {
                    this.showNotification('Vui lòng điền đầy đủ thông tin', 'error');
                    return;
                }

                // Bắt đầu loading
                this.feedbackForm.isSubmitting = true;

                const response = await fetch('/submit-feedback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        subject: this.feedbackForm.subject,
                        message: this.feedbackForm.message
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Reset form
                    this.feedbackForm.subject = '';
                    this.feedbackForm.message = '';
                    
                    this.showNotification('Góp ý của bạn đã được gửi thành công!', 'success');
                    
                    // Cập nhật danh sách góp ý mà không reload trang
                    await this.loadFeedbackList();
                } else {
                    this.showNotification('Có lỗi xảy ra: ' + (data.error || 'Không thể gửi góp ý'), 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                this.showNotification('Có lỗi xảy ra khi gửi góp ý', 'error');
            } finally {
                // Kết thúc loading
                this.feedbackForm.isSubmitting = false;
            }
        },
        
        // Thêm hàm mới để load danh sách góp ý
        async loadFeedbackList() {
            try {
                const response = await fetch('/get-user-feedbacks');
                const data = await response.json();
                
                if (data.success) {
                    this.userFeedbacks = data.feedbacks;
                }
            } catch (error) {
                console.error('Error loading feedbacks:', error);
            }
        },
        async uploadAvatar(event) {
            const file = event.target.files[0];
            if (!file) return;

            // Kiểm tra kích thước file (giới hạn 5MB)
            if (file.size > 5 * 1024 * 1024) {
                this.showNotification('File quá lớn. Vui lòng chọn file nhỏ hơn 5MB', 'error');
                return;
            }

            const formData = new FormData();
            formData.append('avatar', file);

            try {
                const response = await fetch('/upload-avatar', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                
                if (response.ok) {
                    // Cập nhật avatar trong giao diện
                    this.user.avatar_url = result.avatar_url + '?t=' + new Date().getTime();
                    this.showNotification('Cập nhật ảnh đại diện thành công!');
                } else {
                    throw new Error(result.error || 'Có lỗi xảy ra');
                }
            } catch (error) {
                console.error('Error:', error);
                this.showNotification(error.message, 'error');
            }
        },
        // Thêm method để force refresh birth date dropdowns
        refreshBirthDateDropdowns() {
            console.log("Forcing birth date dropdown refresh...");
            
            this.$nextTick(() => {
                const daySelect = document.querySelector('select[x-model="user.birthDay"]');
                const monthSelect = document.querySelector('select[x-model="user.birthMonth"]');
                const yearSelect = document.querySelector('select[x-model="user.birthYear"]');
                
                if (daySelect && this.user.birthDay) {
                    daySelect.value = this.user.birthDay;
                    console.log("Set day select to:", this.user.birthDay);
                }
                if (monthSelect && this.user.birthMonth) {
                    monthSelect.value = this.user.birthMonth;
                    console.log("Set month select to:", this.user.birthMonth);
                }
                if (yearSelect && this.user.birthYear) {
                    yearSelect.value = this.user.birthYear;
                    console.log("Set year select to:", this.user.birthYear);
                }
                
                // Trigger change events để đảm bảo Alpine.js nhận biết
                [daySelect, monthSelect, yearSelect].forEach(select => {
                    if (select) {
                        select.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                });
            });
        },
        // Thêm method để handle khi chuyển đến tab profile
        activateProfileTab() {
            this.activeTab = 'profile';
            setTimeout(() => {
                if (this.refreshBirthDateDropdowns) {
                    this.refreshBirthDateDropdowns();
                }
            }, 100);
        },
        // Debug function để kiểm tra toàn bộ quá trình
        debugBirthDate() {
            console.log("=== COMPREHENSIVE BIRTH DATE DEBUG ===");
            console.log("1. User object:", this.user);
            console.log("2. Birth date components:", {
                birthDay: this.user.birthDay,
                birthMonth: this.user.birthMonth,
                birthYear: this.user.birthYear,
                birth_date: this.user.birth_date
            });
            
            // Kiểm tra DOM elements
            const daySelect = document.querySelector('select[x-model="user.birthDay"]');
            const monthSelect = document.querySelector('select[x-model="user.birthMonth"]');
            const yearSelect = document.querySelector('select[x-model="user.birthYear"]');
            
            console.log("3. DOM Elements found:", {
                daySelect: !!daySelect,
                monthSelect: !!monthSelect,
                yearSelect: !!yearSelect
            });
            
            if (daySelect) {
                console.log("4. Day select details:", {
                    value: daySelect.value,
                    selectedIndex: daySelect.selectedIndex,
                    options: Array.from(daySelect.options).map(opt => opt.value),
                    bindingValue: this.user.birthDay
                });
            }
            
            if (monthSelect) {
                console.log("5. Month select details:", {
                    value: monthSelect.value,
                    selectedIndex: monthSelect.selectedIndex,
                    options: Array.from(monthSelect.options).map(opt => opt.value),
                    bindingValue: this.user.birthMonth
                });
            }
            
            if (yearSelect) {
                console.log("6. Year select details:", {
                    value: yearSelect.value,
                    selectedIndex: yearSelect.selectedIndex,
                    optionsCount: yearSelect.options.length,
                    bindingValue: this.user.birthYear
                });
            }
            
            console.log("=== END COMPREHENSIVE DEBUG ===");
        }
    }));
});