
        let itinerary = null;
        let totalCost = 0;
        let particleSystem = null;

        // load dữ liệu từ AI
        window.addEventListener('load', function() {
            initParticleSystem();
            showLoading();
            setTimeout(() => {
                loadItinerary();
            }, 2000);
        });

        // hiện loading
        function showLoading() {
            document.getElementById('loadingAnimation').style.display = 'block';
            document.getElementById('scheduleContainer').style.display = 'none';
        }

        // ẩn loading 
        function hideLoading() {
            document.getElementById('loadingAnimation').style.display = 'none';
            document.getElementById('scheduleContainer').style.display = 'block';
        }

        // khởi tạo hệ thống hạt
        function initParticleSystem() {
            const canvas = document.getElementById('particleCanvas');
            const ctx = canvas.getContext('2d');
            
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            
            const particles = [];
            const particleCount = 50;
            
            // Create particles
            for (let i = 0; i < particleCount; i++) {
                particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    vx: (Math.random() - 0.5) * 0.5,
                    vy: (Math.random() - 0.5) * 0.5,
                    size: Math.random() * 3 + 1,
                    opacity: Math.random() * 0.5 + 0.3,
                    color: `hsl(${Math.random() * 60 + 200}, 70%, 70%)`
                });
            }
            
            function animateParticles() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                particles.forEach(particle => {
                    particle.x += particle.vx;
                    particle.y += particle.vy;
                    
                    if (particle.x < 0) particle.x = canvas.width;
                    if (particle.x > canvas.width) particle.x = 0;
                    if (particle.y < 0) particle.y = canvas.height;
                    if (particle.y > canvas.height) particle.y = 0;
                    
                    ctx.beginPath();
                    ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                    ctx.fillStyle = particle.color;
                    ctx.globalAlpha = particle.opacity;
                    ctx.fill();
                });
                
                ctx.globalAlpha = 1;
                requestAnimationFrame(animateParticles);
            }
            
            animateParticles();
            
            // Resize handler
            window.addEventListener('resize', () => {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            });
        }

        // tải dữ liệu lịch trình
        function loadItinerary() {
            try {
                itinerary = JSON.parse(localStorage.getItem('itinerary'));
                
                if (!itinerary || !itinerary.days) {
                    throw new Error('Không có dữ liệu lịch trình');
                }

                hideLoading();
                generateTripSummary();
                generateJourneyPreview();
                generateTimeline();
                generateFunFacts();
                setupEventListeners();
                startAnimations();
                
            } catch (error) {
                console.error('Lỗi:', error);
                hideLoading();
                alert('Không có dữ liệu hành trình hoặc dữ liệu không hợp lệ.');
            }
        }

        // tạo bảng tóm tắt chuyến đi
        function generateTripSummary() {
            const summaryContainer = document.getElementById('tripSummary');
            
            // Tính chi phí 
            totalCost = itinerary.days.reduce((sum, day) => sum + (Number(day.estimated_cost) || 0), 0);
            
            // tính số ngày 
            const totalActivities = itinerary.days.reduce((sum, day) => {
                const scheduleItems = day.schedule || day.activities || [];
                return sum + scheduleItems.filter(item => item.type === 'activity' || !item.type).length;
            }, 0);

            const summaryData = [
                {
                    icon: 'fas fa-calendar-alt',
                    value: itinerary.days.length,
                    label: 'Ngày du lịch'
                },
                {
                    icon: 'fas fa-map-marker-alt',
                    value: totalActivities,
                    label: 'Điểm tham quan'
                },
                {
                    icon: 'fas fa-coins',
                    value: formatCurrency(totalCost),
                    label: 'Tổng chi phí'
                },
                {
                    icon: 'fas fa-heart',
                    value: itinerary.destination || 'Việt Nam',
                    label: 'Điểm đến'
                }
            ];

            summaryContainer.innerHTML = summaryData.map((item, index) => `
                <div class="summary-card fade-in" style="animation-delay: ${index * 0.2}s">
                    <div class="icon">
                        <i class="${item.icon}"></i>
                    </div>
                    <div class="value">${item.value}</div>
                    <div class="label">${item.label}</div>
                </div>
            `).join('');
        }

        // tạo bản xem trước chuyến đi
        function generateJourneyPreview() {
            const journeyPath = document.getElementById('journeyPath');
            const journeyInfo = document.getElementById('journeyInfo');
            const days = itinerary.days.length;
            
            // tạo điểm chuyến đi
            let pathHTML = '';
            for (let i = 0; i < days; i++) {
                pathHTML += `
                    <div class="journey-point fade-in" style="animation-delay: ${i * 0.3}s" title="Ngày ${i + 1}">
                        ${i + 1}
                    </div>
                `;
            }
            
            // tính toán thống kê cho thông tin chuyến đi
            const totalActivities = itinerary.days.reduce((sum, day) => {
                const scheduleItems = day.schedule || day.activities || [];
                return sum + scheduleItems.filter(item => item.type === 'activity' || !item.type).length;
            }, 0);
            
            const totalDistance = Math.round(days * 150 + Math.random() * 100); // Simulated distance
            const estimatedTime = days * 8; // Estimated hours
            
            // tạo thông tin chuyến đi
            const infoHTML = `
                <div class="journey-stat fade-in" style="animation-delay: ${days * 0.3 + 0.2}s">
                    <span class="stat-number counter" data-target="${totalActivities}">${totalActivities}</span>
                    <span class="stat-label">Điểm đến</span>
                </div>
                <div class="journey-stat fade-in" style="animation-delay: ${days * 0.3 + 0.4}s">
                    <span class="stat-number counter" data-target="${totalDistance}">${totalDistance}</span>
                    <span class="stat-label">Km di chuyển</span>
                </div>
                <div class="journey-stat fade-in" style="animation-delay: ${days * 0.3 + 0.6}s">
                    <span class="stat-number counter" data-target="${estimatedTime}">${estimatedTime}</span>
                    <span class="stat-label">Giờ trải nghiệm</span>
                </div>
            `;
            
            journeyPath.innerHTML = pathHTML;
            journeyInfo.innerHTML = infoHTML;
        }

        function generateFunFacts() {
            const factsGrid = document.getElementById('factsGrid');
            
            const totalDays = itinerary.days.length;
            const totalActivities = itinerary.days.reduce((sum, day) => {
                const scheduleItems = day.schedule || day.activities || [];
                return sum + scheduleItems.filter(item => item.type === 'activity' || !item.type).length;
            }, 0);
            
            const totalMeals = itinerary.days.reduce((sum, day) => {
                const scheduleItems = day.schedule || day.activities || [];
                return sum + scheduleItems.filter(item => item.type === 'meal').length;
            }, 0);
            
            const avgCostPerDay = Math.round(totalCost / totalDays);
            
            const facts = [
                {
                    icon: 'fas fa-walking',
                    text: `Bạn sẽ trải nghiệm ${totalActivities} hoạt động thú vị trong chuyến đi này!`
                },
                {
                    icon: 'fas fa-utensils',
                    text: `Chuẩn bị thưởng thức ${totalMeals} bữa ăn đặc sắc trong hành trình.`
                },
                {
                    icon: 'fas fa-chart-line',
                    text: `Chi phí trung bình mỗi ngày là ${formatCurrency(avgCostPerDay)} VND.`
                },
                {
                    icon: 'fas fa-star',
                    text: `Đây là một chuyến đi ${totalDays} ngày đầy ý nghĩa và đáng nhớ!`
                }
            ];
            
            factsGrid.innerHTML = facts.map((fact, index) => `
                <div class="fact-card fade-in" style="animation-delay: ${index * 0.2 + 0.5}s">
                    <div class="fact-icon">
                        <i class="${fact.icon}"></i>
                    </div>
                    <div class="fact-text">${fact.text}</div>
                </div>
            `).join('');
        }

        function generateTimeline() {
            const timelineContainer = document.getElementById('timeline');
            const activityNames = [];
            const locations = [];

            const timelineHTML = itinerary.days.map((day, dayIndex) => {
                const scheduleItems = day.schedule || day.activities || [];
                
                const activitiesHTML = scheduleItems.map(item => {
                    if (item.type === "activity" || !item.type) {
                        if (item.description) {
                            activityNames.push(item.description.split(":")[0]);
                        } else if (item.name) {
                            activityNames.push(item.name);
                        }
                        if (item.location) {
                            locations.push(item.location);
                        }
                    }

                    const cost = Number(item.cost) || 0;
                    const typeClass = item.type || 'activity';
                    const icon = getActivityIcon(typeClass);
                    
                    return `
                        <li class="activity-item ${typeClass}">
                            <div class="activity-time">
                                <i class="${icon}"></i>
                                ${item.time || 'N/A'}
                            </div>
                            <div class="activity-details">
                                <div class="activity-name">
                                    ${item.description || item.name || 'Hoạt động'}
                                </div>
                                ${cost > 0 ? `<div class="activity-cost">
                                    <i class="fas fa-money-bill-wave"></i>
                                    Chi phí: ${formatCurrency(cost)} VND
                                </div>` : ''}
                            </div>
                        </li>
                    `;
                }).join('');

                const dayCost = Number(day.estimated_cost) || 0;

                return `
                    <div class="day-card" data-day="${dayIndex + 1}">
                        <div class="day-number">${day.day || dayIndex + 1}</div>
                        <div class="day-content">
                            <div class="day-title">
                                <i class="fas fa-sun"></i>
                                Ngày ${day.day || dayIndex + 1}
                            </div>
                            <ul class="activity-list">
                                ${activitiesHTML}
                            </ul>
                            <div class="day-cost">
                                <i class="fas fa-calculator"></i>
                                Chi phí ngày: <span class="counter" data-target="${dayCost}">${formatCurrency(dayCost)}</span> VND
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

            timelineContainer.innerHTML = timelineHTML;

            localStorage.setItem('activityNames', JSON.stringify(activityNames));
            localStorage.setItem('locations', JSON.stringify(locations));
        }

        function getActivityIcon(type) {
            const icons = {
                'activity': 'fas fa-camera',
                'meal': 'fas fa-utensils',
                'rest': 'fas fa-bed',
                'transport': 'fas fa-car'
            };
            return icons[type] || 'fas fa-map-marker-alt';
        }

        // đỏi sang tiền việt, đổi sang 500000 thành 500.000
        function formatCurrency(amount) {
            return new Intl.NumberFormat('vi-VN').format(amount);
        }

        // Start animations
        function startAnimations() {
            // Animate timeline items
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('show');
                    }
                });
            }, { threshold: 0.1 });

            document.querySelectorAll('.day-card').forEach(card => {
                observer.observe(card);
            });

            // Animate counters
            setTimeout(() => {
                animateCounters();
            }, 1000);

            // Update progress bar on scroll
            window.addEventListener('scroll', updateProgressBar);
        }

        // Animate counters
        function animateCounters() {
            document.querySelectorAll('.counter').forEach(counter => {
                const target = parseInt(counter.getAttribute('data-target')) || 
                              parseInt(counter.textContent.replace(/[^\d]/g, ''));
                
                if (target > 0) {
                    animateCounter(counter, target);
                }
            });

            // Animate total cost
            const totalCostElement = document.getElementById('totalCostValue');
            animateCounter(totalCostElement, totalCost);
        }

        // Animate individual counter
        function animateCounter(element, target) {
            let current = 0;
            const increment = target / 100;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                element.textContent = formatCurrency(Math.floor(current));
            }, 20);
        }

        // Update progress bar
        function updateProgressBar() {
            const scrollTop = window.pageYOffset;
            const docHeight = document.body.offsetHeight - window.innerHeight;
            const scrollPercent = (scrollTop / docHeight) * 100;
            
            document.getElementById('progressBar').style.width = scrollPercent + '%';
        }

        // Setup event listeners
        function setupEventListeners() {
            // Map button
            document.getElementById('mapBtn').addEventListener('click', function() {
                addRippleEffect(this);
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Đang chuyển...</span>';
                setTimeout(() => {
                    window.location.href = '/map';
                }, 1000);
            });

            // Save history button
            const saveBtn = document.getElementById('saveHistoryBtn');
            if (saveBtn) {
                saveBtn.addEventListener('click', function() {
                    addRippleEffect(this);
                    saveToHistory();
                });
            }

            // Share button
            const shareBtn = document.getElementById('shareBtn');
            if (shareBtn) {
                shareBtn.addEventListener('click', function() {
                    addRippleEffect(this);
                    shareItinerary();
                });
            }

            const fabMenu = document.getElementById('fabMenu');
            const fabMain = fabMenu.querySelector('.fab-main');
            
            fabMain.addEventListener('click', function() {
                fabMenu.classList.toggle('active');
            });

            const fabOptions = document.querySelectorAll('.fab-option');
            fabOptions.forEach(option => {
                option.addEventListener('click', function() {
                    const action = this.dataset.action;
                    handleFabAction(action);
                    fabMenu.classList.remove('active');
                });
            });
        }

        // Add ripple effect to buttons
        function addRippleEffect(button) {
            const ripple = button.querySelector('.btn-ripple');
            if (ripple) {
                ripple.style.animation = 'none';
                ripple.offsetHeight; // Trigger reflow
                ripple.style.animation = 'ripple 0.6s linear';
            }
        }

        // Handle floating action button actions
        function handleFabAction(action) {
            switch(action) {
                case 'weather':
                    showWeatherInfo();
                    break;
                case 'notes':
                    openNotes();
                    break;
                case 'photos':
                    openPhotoGallery();
                    break;
            }
        }

        // chia s lịch trình
        function shareItinerary() {
            if (navigator.share) {
                navigator.share({
                    title: 'Lịch trình Du lịch',
                    text: `Chia sẻ lịch trình du lịch ${itinerary.days.length} ngày tuyệt vời!`,
                    url: window.location.href
                });
            } else {
                const shareText = `Lịch trình du lịch ${itinerary.days.length} ngày tuyệt vời! ${window.location.href}`;
                navigator.clipboard.writeText(shareText).then(() => {
                    alert('Đã sao chép link chia sẻ vào clipboard!');
                }).catch(() => {
                    prompt('Sao chép link này để chia sẻ:', shareText);
                });
            }
        }

        function showWeatherInfo() {
            const weatherWidget = document.getElementById('weatherWidget');
            weatherWidget.style.animation = 'pulse 1s ease-in-out';
            alert('Tính năng thời tiết sẽ được cập nhật trong phiên bản tiếp theo!');
        }

        function openNotes() {
            alert('Tính năng ghi chú sẽ được cập nhật trong phiên bản tiếp theo!');
        }

        function openPhotoGallery() {
            alert('Tính năng thư viện ảnh sẽ được cập nhật trong phiên bản tiếp theo!');
        }

        //  Lưu lịch sử 
        function saveToHistory() {
            const saveBtn = document.getElementById('saveHistoryBtn');
            const originalHTML = saveBtn.innerHTML;
            
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang lưu...';
            saveBtn.disabled = true;

            const activityNames = JSON.parse(localStorage.getItem('activityNames')) || [];
            
            const data = {
                activityNames: activityNames,
                days: itinerary.days.length,
                budget: totalCost.toString(),
                destination: itinerary.destination || "Không rõ"
            };

            fetch('/save-history', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.message); });
                }
                return response.json();
            })
            .then(result => {
                saveBtn.innerHTML = '<i class="fas fa-check"></i> Đã lưu!';
                setTimeout(() => {
                    window.location.href = '/history';
                }, 1500);
            })
            .catch(error => {
                console.error('Lỗi:', error);
                saveBtn.innerHTML = originalHTML;
                saveBtn.disabled = false;
                alert('Lỗi khi lưu lịch sử: ' + error.message);
            });
        }

        document.addEventListener('DOMContentLoaded', function() {
            document.addEventListener('mouseover', function(e) {
                if (e.target.closest('.activity-item')) {
                    e.target.closest('.activity-item').style.transform = 'translateX(10px) scale(1.02)';
                }
            });

            document.addEventListener('mouseout', function(e) {
                if (e.target.closest('.activity-item')) {
                    e.target.closest('.activity-item').style.transform = '';
                }
            });
        });
