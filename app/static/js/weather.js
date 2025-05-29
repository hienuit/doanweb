// Weather Widget JavaScript
class WeatherWidget {
    constructor() {
        this.cache = new Map();
        this.cacheTimeout = 10 * 60 * 1000; // 10 phút
        this.init();
    }

    init() {
        this.loadDestinationWeather();
        this.loadWeatherSection();
        this.setupEventListeners();
        
        // Cập nhật thời tiết mỗi 15 phút
        setInterval(() => {
            this.refreshWeather();
        }, 15 * 60 * 1000);
    }

    setupEventListeners() {
        // Click vào weather widget để xem chi tiết
        document.addEventListener('click', (e) => {
            if (e.target.closest('.weather-widget')) {
                const widget = e.target.closest('.weather-widget');
                const city = widget.dataset.city;
                if (city) {
                    this.showWeatherModal(city);
                }
            }
        });

        // Refresh button
        document.addEventListener('click', (e) => {
            if (e.target.closest('.weather-refresh')) {
                e.preventDefault();
                this.refreshWeather();
            }
        });
    }

    async loadDestinationWeather() {
        const destinationCards = document.querySelectorAll('.destination-card');
        
        destinationCards.forEach(async (card) => {
            const cityElement = card.querySelector('.destination-location span');
            if (!cityElement) return;
            
            const cityText = cityElement.textContent.trim();
            const city = this.extractCityName(cityText);
            
            if (city) {
                await this.addWeatherToCard(card, city);
            }
        });
    }

    extractCityName(locationText) {
        // Trích xuất tên thành phố từ text như "Ninh Bình, Việt Nam"
        const cityMappings = {
            // Có dấu
            'Ninh Bình': 'Ninh Bình',
            'Quảng Ninh': 'Quảng Ninh', 
            'Hà Nội': 'Hà Nội',
            'Hồ Chí Minh': 'Hồ Chí Minh',
            'Đà Nẵng': 'Đà Nẵng',
            'Nha Trang': 'Nha Trang',
            'Đà Lạt': 'Đà Lạt',
            'Phú Quốc': 'Phú Quốc',
            'Sa Pa': 'Sa Pa',
            'Hạ Long': 'Hạ Long',
            'Huế': 'Huế',
            'Quy Nhơn': 'Quy Nhơn',
            'Vũng Tàu': 'Vũng Tàu',
            'Phan Thiết': 'Phan Thiết',
            'Cần Thơ': 'Cần Thơ',
            'Hải Phòng': 'Hải Phòng',
            'Cao Bằng': 'Cao Bằng',
            'Hà Giang': 'Hà Giang',
            'Bắc Ninh': 'Bắc Ninh',
            'Cà Mau': 'Cà Mau',
            
            // Không dấu
            'Ninh Binh': 'Ninh Bình',
            'Quang Ninh': 'Quảng Ninh',
            'Ha Noi': 'Hà Nội',
            'Ho Chi Minh': 'Hồ Chí Minh',
            'Da Nang': 'Đà Nẵng',
            'Da Lat': 'Đà Lạt',
            'Phu Quoc': 'Phú Quốc',
            'Ha Long': 'Hạ Long',
            'Hue': 'Huế',
            'Quy Nhon': 'Quy Nhơn',
            'Vung Tau': 'Vũng Tàu',
            'Phan Thiet': 'Phan Thiết',
            'Can Tho': 'Cần Thơ',
            'Hai Phong': 'Hải Phòng',
            'Cao Bang': 'Cao Bằng',
            'Ha Giang': 'Hà Giang',
            'Bac Ninh': 'Bắc Ninh',
            'Ca Mau': 'Cà Mau',
            
            // Viết tắt và tên khác
            'TP.HCM': 'Hồ Chí Minh',
            'TPHCM': 'Hồ Chí Minh',
            'HCM': 'Hồ Chí Minh',
            'Sài Gòn': 'Hồ Chí Minh',
            'Saigon': 'Hồ Chí Minh',
            'HN': 'Hà Nội',
            'Hanoi': 'Hà Nội',
            'DN': 'Đà Nẵng',
            'Danang': 'Đà Nẵng'
        };

        // Tìm kiếm chính xác trước
        for (const [key, value] of Object.entries(cityMappings)) {
            if (locationText.includes(key)) {
                return value;
            }
        }
        
        // Nếu không tìm thấy, lấy phần đầu trước dấu phẩy
        const cityName = locationText.split(',')[0].trim();
        
        // Thử tìm kiếm lại với tên đã tách
        for (const [key, value] of Object.entries(cityMappings)) {
            if (cityName.toLowerCase().includes(key.toLowerCase()) || key.toLowerCase().includes(cityName.toLowerCase())) {
                return value;
            }
        }
        
        return cityName;
    }

    async addWeatherToCard(card, city) {
        // Tạo weather badge
        const weatherBadge = document.createElement('div');
        weatherBadge.className = 'destination-weather loading';
        weatherBadge.innerHTML = `
            <div class="weather-spinner"></div>
            <span>Đang tải...</span>
        `;
        
        card.style.position = 'relative';
        card.appendChild(weatherBadge);

        try {
            const weather = await this.getWeatherData(city);
            
            if (weather.success) {
                const data = weather.data;
                weatherBadge.className = 'destination-weather';
                weatherBadge.innerHTML = `
                    <i class="${data.icon}"></i>
                    <span>${data.temperature}°C</span>
                `;
                weatherBadge.title = `${data.description} - Cảm giác như ${data.feels_like}°C`;
            } else {
                weatherBadge.className = 'destination-weather error';
                weatherBadge.innerHTML = `
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>N/A</span>
                `;
            }
        } catch (error) {
            console.error('Error loading weather for', city, error);
            weatherBadge.className = 'destination-weather error';
            weatherBadge.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                <span>N/A</span>
            `;
        }
    }

    getPopularTouristCities() {
        return {
            'Miền Bắc': [
                'Hà Nội', 'Hạ Long', 'Sa Pa', 'Ninh Bình', 'Hà Giang', 
                'Cao Bằng', 'Hải Phòng', 'Bắc Ninh'
            ],
            'Miền Trung': [
                'Đà Nẵng', 'Huế', 'Hội An', 'Quy Nhơn', 'Phan Thiết',
                'Nha Trang', 'Đà Lạt', 'Phú Yên', 'Bình Định'
            ],
            'Miền Nam': [
                'Hồ Chí Minh', 'Vũng Tàu', 'Cần Thơ', 'Phú Quốc', 
                'Cà Mau', 'An Giang', 'Đồng Tháp', 'Tiền Giang'
            ]
        };
    }

    getDefaultCities() {
        // Lấy từ localStorage hoặc sử dụng mặc định
        const saved = localStorage.getItem('selectedWeatherCities');
        if (saved) {
            try {
                return JSON.parse(saved);
            } catch (e) {
                console.error('Error parsing saved cities:', e);
            }
        }
        
        // Mặc định: các thành phố du lịch nổi tiếng nhất
        return ['Hà Nội', 'Hồ Chí Minh', 'Đà Nẵng', 'Nha Trang', 'Hạ Long', 'Sa Pa'];
    }

    saveSelectedCities(cities) {
        localStorage.setItem('selectedWeatherCities', JSON.stringify(cities));
    }

    async loadWeatherSection() {
        const weatherSection = document.getElementById('weatherSection');
        if (!weatherSection) return;

        // Tạo city selector nếu chưa có
        this.createCitySelector(weatherSection);

        const cities = this.getDefaultCities();
        const weatherGrid = weatherSection.querySelector('.weather-grid');
        
        if (!weatherGrid) return;

        // Tạo loading widgets
        weatherGrid.innerHTML = cities.map(city => `
            <div class="weather-widget loading" data-city="${city}">
                <div class="weather-loading">
                    <div class="weather-spinner"></div>
                    <span>Đang tải thời tiết ${city}...</span>
                </div>
            </div>
        `).join('');

        // Load weather data cho từng thành phố
        for (const city of cities) {
            try {
                const weather = await this.getWeatherData(city);
                const widget = weatherGrid.querySelector(`[data-city="${city}"]`);
                
                if (weather.success && widget) {
                    this.renderWeatherWidget(widget, weather.data);
                } else if (widget) {
                    this.renderWeatherError(widget, city);
                }
            } catch (error) {
                console.error('Error loading weather for', city, error);
                const widget = weatherGrid.querySelector(`[data-city="${city}"]`);
                if (widget) {
                    this.renderWeatherError(widget, city);
                }
            }
        }
    }

    createCitySelector(weatherSection) {
        // Kiểm tra xem đã có selector chưa
        if (weatherSection.querySelector('.city-selector')) return;

        const selectorHTML = `
            <div class="city-selector mb-4">
                <div class="row justify-content-center align-items-center">
                    <div class="col-12 text-center">
                        <h3 class="section-title mb-0">
                            <i class="fas fa-cloud-sun me-3"></i>
                            Thời Tiết Các Điểm Đến
                        </h3>
                    </div>
                </div>
                <div class="row justify-content-center mt-3">
                    <div class="col-12 text-center">
                        <div class="quick-cities">
                            <span class="text-light me-3">Nhanh:</span>
                            <button class="btn btn-sm btn-outline-light me-2" onclick="weatherWidget.loadQuickCities('popular')">
                                <i class="fas fa-star me-1"></i>Phổ Biến
                            </button>
                            <button class="btn btn-sm btn-outline-light me-2" onclick="weatherWidget.loadQuickCities('north')">
                                <i class="fas fa-mountain me-1"></i>Miền Bắc
                            </button>
                            <button class="btn btn-sm btn-outline-light me-2" onclick="weatherWidget.loadQuickCities('central')">
                                <i class="fas fa-water me-1"></i>Miền Trung
                            </button>
                            <button class="btn btn-sm btn-outline-light me-2" onclick="weatherWidget.loadQuickCities('south')">
                                <i class="fas fa-sun me-1"></i>Miền Nam
                            </button>
                        </div>
                    </div>
                </div>
                <div class="row justify-content-center mt-2">
                    <div class="col-12 text-center">
                        <button class="btn btn-outline-light btn-sm" onclick="weatherWidget.showCityModal()">
                            <i class="fas fa-cog me-2"></i>Chọn Tỉnh/Thành Phố
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Thêm selector vào đầu section
        const titleElement = weatherSection.querySelector('.section-title');
        if (titleElement) {
            titleElement.remove(); // Xóa title cũ
        }
        
        weatherSection.insertAdjacentHTML('afterbegin', selectorHTML);
    }

    renderWeatherWidget(widget, data) {
        const weatherClass = this.getWeatherClass(data.icon);
        
        // Kiểm tra xem có phải demo data không (thời gian cập nhật giống nhau)
        const isDemoData = data.last_updated && data.last_updated.includes(':');
        const demoIndicator = isDemoData ? '<span class="demo-indicator" title="Dữ liệu demo"><i class="fas fa-flask"></i></span>' : '';
        
        widget.className = `weather-widget ${weatherClass}`;
        widget.innerHTML = `
            <div class="weather-header">
                <h3 class="weather-city">${data.city} ${demoIndicator}</h3>
                <span class="weather-time">Cập nhật: ${data.last_updated}</span>
            </div>
            
            <div class="weather-main">
                <h2 class="weather-temp">${data.temperature}°C</h2>
                <i class="${data.icon} weather-icon"></i>
            </div>
            
            <p class="weather-description">${data.description}</p>
            
            <div class="weather-details">
                <div class="weather-detail">
                    <i class="fas fa-thermometer-half"></i>
                    <span>Cảm giác: ${data.feels_like}°C</span>
                </div>
                <div class="weather-detail">
                    <i class="fas fa-tint"></i>
                    <span>Độ ẩm: ${data.humidity}%</span>
                </div>
                <div class="weather-detail">
                    <i class="fas fa-wind"></i>
                    <span>Gió: ${data.wind_speed} m/s</span>
                </div>
                <div class="weather-detail">
                    <i class="fas fa-eye"></i>
                    <span>Tầm nhìn: ${data.visibility} km</span>
                </div>
                <div class="weather-detail">
                    <i class="fas fa-sunrise"></i>
                    <span>Bình minh: ${data.sunrise}</span>
                </div>
                <div class="weather-detail">
                    <i class="fas fa-sunset"></i>
                    <span>Hoàng hôn: ${data.sunset}</span>
                </div>
            </div>
        `;
    }

    renderWeatherError(widget, city) {
        widget.className = 'weather-widget';
        widget.innerHTML = `
            <div class="weather-error">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Không thể tải thời tiết</h3>
                <p>Thành phố: ${city}</p>
                <button class="btn btn-sm btn-light weather-refresh" data-city="${city}">
                    <i class="fas fa-redo"></i> Thử lại
                </button>
            </div>
        `;
    }

    getWeatherClass(icon) {
        if (icon.includes('sun')) return 'weather-sunny';
        if (icon.includes('cloud-rain') || icon.includes('rain')) return 'weather-rainy';
        if (icon.includes('cloud')) return 'weather-cloudy';
        if (icon.includes('snow')) return 'weather-snowy';
        if (icon.includes('bolt')) return 'weather-stormy';
        return 'weather-cloudy';
    }

    async getWeatherData(city) {
        // Kiểm tra cache
        const cacheKey = `weather_${city}`;
        const cached = this.cache.get(cacheKey);
        
        if (cached && (Date.now() - cached.timestamp) < this.cacheTimeout) {
            return cached.data;
        }

        try {
            const response = await fetch(`/api/weather/current/${encodeURIComponent(city)}`);
            const data = await response.json();
            
            // Lưu vào cache
            this.cache.set(cacheKey, {
                data: data,
                timestamp: Date.now()
            });
            
            return data;
        } catch (error) {
            console.error('Error fetching weather data:', error);
            return {
                success: false,
                message: 'Không thể kết nối đến server'
            };
        }
    }

    async getForecastData(city) {
        const cacheKey = `forecast_${city}`;
        const cached = this.cache.get(cacheKey);
        
        if (cached && (Date.now() - cached.timestamp) < this.cacheTimeout) {
            return cached.data;
        }

        try {
            const response = await fetch(`/api/weather/forecast/${encodeURIComponent(city)}`);
            const data = await response.json();
            
            this.cache.set(cacheKey, {
                data: data,
                timestamp: Date.now()
            });
            
            return data;
        } catch (error) {
            console.error('Error fetching forecast data:', error);
            return {
                success: false,
                message: 'Không thể kết nối đến server'
            };
        }
    }

    async showWeatherModal(city) {
        // Tạo modal nếu chưa có
        let modal = document.getElementById('weatherModal');
        if (!modal) {
            modal = this.createWeatherModal();
            document.body.appendChild(modal);
        }

        // Hiển thị modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Load dữ liệu
        const modalBody = modal.querySelector('.modal-body');
        modalBody.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Đang tải...</span>
                </div>
                <p class="mt-3">Đang tải thông tin thời tiết chi tiết cho ${city}...</p>
            </div>
        `;

        try {
            const [weather, forecast] = await Promise.all([
                this.getWeatherData(city),
                this.getForecastData(city)
            ]);

            if (weather.success) {
                modalBody.innerHTML = this.renderModalContent(weather.data, forecast.success ? forecast.data : null);
            } else {
                modalBody.innerHTML = `
                    <div class="weather-error">
                        <i class="fas fa-exclamation-triangle"></i>
                        <h4>Không thể tải thông tin thời tiết</h4>
                        <p>${weather.message}</p>
                    </div>
                `;
            }
        } catch (error) {
            modalBody.innerHTML = `
                <div class="weather-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h4>Có lỗi xảy ra</h4>
                    <p>Không thể tải thông tin thời tiết. Vui lòng thử lại sau.</p>
                </div>
            `;
        }
    }

    createWeatherModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade weather-modal';
        modal.id = 'weatherModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-cloud-sun me-2"></i>
                            Thông Tin Thời Tiết Chi Tiết
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <!-- Content will be loaded here -->
                    </div>
                </div>
            </div>
        `;
        return modal;
    }

    renderModalContent(weather, forecast) {
        let content = `
            <div class="weather-widget mb-4">
                <div class="weather-header">
                    <h3 class="weather-city">${weather.city}</h3>
                    <span class="weather-time">Cập nhật: ${weather.last_updated}</span>
                </div>
                
                <div class="weather-main">
                    <h2 class="weather-temp">${weather.temperature}°C</h2>
                    <i class="${weather.icon} weather-icon"></i>
                </div>
                
                <p class="weather-description">${weather.description}</p>
                
                <div class="weather-details">
                    <div class="weather-detail">
                        <i class="fas fa-thermometer-half"></i>
                        <span>Cảm giác: ${weather.feels_like}°C</span>
                    </div>
                    <div class="weather-detail">
                        <i class="fas fa-tint"></i>
                        <span>Độ ẩm: ${weather.humidity}%</span>
                    </div>
                    <div class="weather-detail">
                        <i class="fas fa-compress-arrows-alt"></i>
                        <span>Áp suất: ${weather.pressure} hPa</span>
                    </div>
                    <div class="weather-detail">
                        <i class="fas fa-wind"></i>
                        <span>Gió: ${weather.wind_speed} m/s</span>
                    </div>
                    <div class="weather-detail">
                        <i class="fas fa-eye"></i>
                        <span>Tầm nhìn: ${weather.visibility} km</span>
                    </div>
                    <div class="weather-detail">
                        <i class="fas fa-sunrise"></i>
                        <span>Bình minh: ${weather.sunrise}</span>
                    </div>
                    <div class="weather-detail">
                        <i class="fas fa-sunset"></i>
                        <span>Hoàng hôn: ${weather.sunset}</span>
                    </div>
                </div>
            </div>
        `;

        if (forecast && forecast.forecasts) {
            content += `
                <div class="weather-forecast">
                    <h4 class="forecast-title">Dự báo 5 ngày tới</h4>
                    <div class="forecast-grid">
                        ${forecast.forecasts.map(day => `
                            <div class="forecast-item">
                                <div class="forecast-day">${day.day_name}</div>
                                <div class="forecast-date">${day.date}</div>
                                <i class="${day.icon} forecast-icon"></i>
                                <div class="forecast-temp">${day.temperature}°C</div>
                                <div class="forecast-desc">${day.description}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        return content;
    }

    async loadQuickCities(type) {
        let cities = [];
        const touristCities = this.getPopularTouristCities();
        
        switch(type) {
            case 'popular':
                cities = ['Hà Nội', 'Hồ Chí Minh', 'Đà Nẵng', 'Nha Trang', 'Hạ Long', 'Sa Pa'];
                break;
            case 'north':
                cities = touristCities['Miền Bắc'].slice(0, 6);
                break;
            case 'central':
                cities = touristCities['Miền Trung'].slice(0, 6);
                break;
            case 'south':
                cities = touristCities['Miền Nam'].slice(0, 6);
                break;
        }
        
        this.saveSelectedCities(cities);
        await this.reloadWeatherGrid(cities);
        this.showNotification(`Đã tải thời tiết ${this.getRegionName(type)}!`, 'success');
    }

    getRegionName(type) {
        const names = {
            'popular': 'các điểm đến phổ biến',
            'north': 'miền Bắc',
            'central': 'miền Trung', 
            'south': 'miền Nam'
        };
        return names[type] || '';
    }

    async reloadWeatherGrid(cities) {
        const weatherGrid = document.querySelector('.weather-grid');
        if (!weatherGrid) return;

        // Tạo loading widgets
        weatherGrid.innerHTML = cities.map(city => `
            <div class="weather-widget loading" data-city="${city}">
                <div class="weather-loading">
                    <div class="weather-spinner"></div>
                    <span>Đang tải thời tiết ${city}...</span>
                </div>
            </div>
        `).join('');

        // Load weather data cho từng thành phố
        for (const city of cities) {
            try {
                const weather = await this.getWeatherData(city);
                const widget = weatherGrid.querySelector(`[data-city="${city}"]`);
                
                if (weather.success && widget) {
                    this.renderWeatherWidget(widget, weather.data);
                } else if (widget) {
                    this.renderWeatherError(widget, city);
                }
            } catch (error) {
                console.error('Error loading weather for', city, error);
                const widget = weatherGrid.querySelector(`[data-city="${city}"]`);
                if (widget) {
                    this.renderWeatherError(widget, city);
                }
            }
        }
    }

    showCityModal() {
        // Tạo modal nếu chưa có
        let modal = document.getElementById('citySelectionModal');
        if (!modal) {
            modal = this.createCitySelectionModal();
            document.body.appendChild(modal);
        }

        // Hiển thị modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Load danh sách thành phố hiện tại
        this.loadCurrentCitiesInModal();
    }

    createCitySelectionModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'citySelectionModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-map-marked-alt me-2"></i>
                            Chọn Tỉnh/Thành Phố Hiển Thị Thời Tiết
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-8">
                                <h6>Chọn từ danh sách các điểm du lịch nổi tiếng:</h6>
                                <div class="city-tabs">
                                    <ul class="nav nav-pills mb-3" id="cityTabs">
                                        <li class="nav-item">
                                            <button class="nav-link active" data-bs-toggle="pill" data-bs-target="#northCities">
                                                <i class="fas fa-mountain me-1"></i>Miền Bắc
                                            </button>
                                        </li>
                                        <li class="nav-item">
                                            <button class="nav-link" data-bs-toggle="pill" data-bs-target="#centralCities">
                                                <i class="fas fa-water me-1"></i>Miền Trung
                                            </button>
                                        </li>
                                        <li class="nav-item">
                                            <button class="nav-link" data-bs-toggle="pill" data-bs-target="#southCities">
                                                <i class="fas fa-sun me-1"></i>Miền Nam
                                            </button>
                                        </li>
                                    </ul>
                                    <div class="tab-content" id="cityTabContent">
                                        ${this.generateCityTabContent()}
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <h6>Đã chọn (<span id="selectedCount">0</span>/8):</h6>
                                <div id="selectedCitiesList" class="selected-cities-list">
                                    <!-- Selected cities will appear here -->
                                </div>
                                <div class="mt-3">
                                    <button class="btn btn-sm btn-outline-secondary w-100" onclick="weatherWidget.clearSelectedCities()">
                                        <i class="fas fa-trash me-1"></i>Xóa Tất Cả
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
                        <button type="button" class="btn btn-primary" onclick="weatherWidget.applyCitySelection()">
                            <i class="fas fa-check me-2"></i>Áp Dụng
                        </button>
                    </div>
                </div>
            </div>
        `;
        return modal;
    }

    generateCityTabContent() {
        const touristCities = this.getPopularTouristCities();
        let content = '';
        
        Object.entries(touristCities).forEach(([region, cities], index) => {
            const regionId = region === 'Miền Bắc' ? 'northCities' : 
                           region === 'Miền Trung' ? 'centralCities' : 'southCities';
            const activeClass = index === 0 ? 'show active' : '';
            
            content += `
                <div class="tab-pane fade ${activeClass}" id="${regionId}">
                    <div class="row">
                        ${cities.map(city => `
                            <div class="col-md-6 mb-2">
                                <div class="form-check">
                                    <input class="form-check-input city-checkbox" type="checkbox" value="${city}" id="city_${city.replace(/\s+/g, '_')}">
                                    <label class="form-check-label" for="city_${city.replace(/\s+/g, '_')}">
                                        ${city}
                                    </label>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        });
        
        return content;
    }

    loadCurrentCitiesInModal() {
        const currentCities = this.getDefaultCities();
        const checkboxes = document.querySelectorAll('.city-checkbox');
        
        // Reset tất cả checkbox
        checkboxes.forEach(cb => cb.checked = false);
        
        // Check các thành phố hiện tại
        currentCities.forEach(city => {
            const checkbox = document.getElementById(`city_${city.replace(/\s+/g, '_')}`);
            if (checkbox) {
                checkbox.checked = true;
            }
        });
        
        this.updateSelectedCitiesList();
        this.setupCityCheckboxListeners();
    }

    setupCityCheckboxListeners() {
        const checkboxes = document.querySelectorAll('.city-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateSelectedCitiesList();
            });
        });
    }

    updateSelectedCitiesList() {
        const selectedCities = Array.from(document.querySelectorAll('.city-checkbox:checked')).map(cb => cb.value);
        const selectedList = document.getElementById('selectedCitiesList');
        const selectedCount = document.getElementById('selectedCount');
        
        selectedCount.textContent = selectedCities.length;
        
        selectedList.innerHTML = selectedCities.map(city => `
            <span class="badge bg-primary me-1 mb-1">
                ${city}
                <button type="button" class="btn-close btn-close-white ms-1" style="font-size: 0.7em;" onclick="weatherWidget.removeCityFromSelection('${city}')"></button>
            </span>
        `).join('');
        
        // Disable checkbox nếu đã chọn quá 8 thành phố
        const checkboxes = document.querySelectorAll('.city-checkbox');
        checkboxes.forEach(checkbox => {
            if (!checkbox.checked && selectedCities.length >= 8) {
                checkbox.disabled = true;
            } else {
                checkbox.disabled = false;
            }
        });
    }

    removeCityFromSelection(city) {
        const checkbox = document.getElementById(`city_${city.replace(/\s+/g, '_')}`);
        if (checkbox) {
            checkbox.checked = false;
            this.updateSelectedCitiesList();
        }
    }

    clearSelectedCities() {
        const checkboxes = document.querySelectorAll('.city-checkbox');
        checkboxes.forEach(cb => cb.checked = false);
        this.updateSelectedCitiesList();
    }

    async applyCitySelection() {
        const selectedCities = Array.from(document.querySelectorAll('.city-checkbox:checked')).map(cb => cb.value);
        
        if (selectedCities.length === 0) {
            alert('Vui lòng chọn ít nhất 1 thành phố!');
            return;
        }
        
        if (selectedCities.length > 8) {
            alert('Chỉ được chọn tối đa 8 thành phố!');
            return;
        }
        
        // Lưu lựa chọn
        this.saveSelectedCities(selectedCities);
        
        // Đóng modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('citySelectionModal'));
        modal.hide();
        
        // Reload weather grid
        await this.reloadWeatherGrid(selectedCities);
        this.showNotification(`Đã cập nhật thời tiết cho ${selectedCities.length} thành phố!`, 'success');
    }

    async refreshWeather() {
        // Xóa cache
        this.cache.clear();
        
        // Reload weather data
        await this.loadDestinationWeather();
        await this.loadWeatherSection();
        
        // Hiển thị thông báo
        this.showNotification('Đã cập nhật thông tin thời tiết!', 'success');
    }

    showNotification(message, type = 'info') {
        // Tạo notification toast
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Tự động ẩn sau 3 giây
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 3000);
    }
}

// Khởi tạo Weather Widget khi DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.weatherWidget = new WeatherWidget();
});

// Export cho sử dụng global
window.WeatherWidget = WeatherWidget; 