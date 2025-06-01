// gợi ý tự động 
let suggestionTimeout;
let currentSuggestionIndex = -1;

document.addEventListener("DOMContentLoaded", function() {
    const destinationInput = document.getElementById("destinationInput");
    const searchButton = document.getElementById("searchButton");
    
    if (destinationInput) {
        // tạo dropdown gợi ý
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.id = 'suggestions-container';
        suggestionsContainer.className = 'suggestions-dropdown';
        destinationInput.parentNode.appendChild(suggestionsContainer);
        
        // sự kiện input cho gợi ý tự động
        destinationInput.addEventListener("input", function() {
            const query = this.value.trim();
            
            // xóa timeout trước đó
            clearTimeout(suggestionTimeout);
            
            if (query.length >= 2) {
                // tối ưu hóa gọi API
                suggestionTimeout = setTimeout(() => {
                    fetchSuggestions(query);
                }, 300);
            } else {
                hideSuggestions();
            }
        });
        
        // xử lý điều hướng bàn phím
        destinationInput.addEventListener("keydown", function(event) {
            const suggestions = document.querySelectorAll('.suggestion-item');
            
            if (event.key === "ArrowDown") {
                event.preventDefault();
                currentSuggestionIndex = Math.min(currentSuggestionIndex + 1, suggestions.length - 1);
                updateSuggestionSelection(suggestions);
            } else if (event.key === "ArrowUp") {
                event.preventDefault();
                currentSuggestionIndex = Math.max(currentSuggestionIndex - 1, -1);
                updateSuggestionSelection(suggestions);
            } else if (event.key === "Enter") {
                event.preventDefault();
                if (currentSuggestionIndex >= 0 && suggestions[currentSuggestionIndex]) {
                    selectSuggestion(suggestions[currentSuggestionIndex].textContent);
                } else {
                    performSearch();
                }
            } else if (event.key === "Escape") {
                hideSuggestions();
            }
        });
        
        // ẩn gợi ý khi click ngoài
        document.addEventListener("click", function(event) {
            if (!destinationInput.contains(event.target) && !suggestionsContainer.contains(event.target)) {
                hideSuggestions();
            }
        });
    }
    
    // sự kiện cho nút tìm kiếm
    if (searchButton) {
        searchButton.addEventListener("click", performSearch);
    }
    
    function fetchSuggestions(query) {
        fetch(`/suggest-provinces?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(suggestions => {
                displaySuggestions(suggestions);
            })
            .catch(error => {
                console.error('Error fetching suggestions:', error);
                hideSuggestions();
            });
    }
    
    // hiển thị danh sách đề xuất
    function displaySuggestions(suggestions) {
        const container = document.getElementById('suggestions-container');
        container.innerHTML = '';
        currentSuggestionIndex = -1;
        
        if (suggestions.length === 0) {
            hideSuggestions();
            return;
        }
        
        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.textContent = suggestion;
            item.addEventListener('click', () => selectSuggestion(suggestion));
            container.appendChild(item);
        });
        
        container.style.display = 'block';
    }
    
    function updateSuggestionSelection(suggestions) {
        suggestions.forEach((item, index) => {
            if (index === currentSuggestionIndex) {
                item.classList.add('selected');
                destinationInput.value = item.textContent;
            } else {
                item.classList.remove('selected');
            }
        });
    }
    
    function selectSuggestion(suggestion) {
        destinationInput.value = suggestion;
        hideSuggestions();
        performSearch();
    }
    
    function hideSuggestions() {
        const container = document.getElementById('suggestions-container');
        if (container) {
            container.style.display = 'none';
            container.innerHTML = '';
        }
        currentSuggestionIndex = -1;
    }
    
    function performSearch() {
        const province = destinationInput.value.trim();
        
        if (province) {
            window.location.href = '/page3?province=' + encodeURIComponent(province);
        } else {
            alert("Vui lòng nhập địa điểm du lịch.");
        }
    }
});

const backToTopButton = document.getElementById("backToTop");
        
        window.addEventListener("scroll", () => {
            if (window.pageYOffset > 300) {
                backToTopButton.classList.add("visible");
            } else {
                backToTopButton.classList.remove("visible");
            }
        });

        backToTopButton.addEventListener("click", (e) => {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: "smooth" });
        });

        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                if (this.getAttribute('href') !== "#") {
                    e.preventDefault();
                    
                    document.querySelector(this.getAttribute('href')).scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            });
        });

document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM Loaded - Toggle Init");
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navLinks = document.getElementById('navLinks');
    const containerList = document.getElementById('containerList');
    
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            // Toggle navigation links
            if (navLinks) {
                navLinks.classList.toggle('show');
            }
            
            // Toggle container list (search and popular destinations)
            if (containerList) {
                containerList.classList.toggle('show');
            }
        });
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        const isClickInsideNav = navLinks?.contains(event.target);
        const isClickInsideContainer = containerList?.contains(event.target);
        const isClickOnToggle = mobileMenuToggle?.contains(event.target);
        
        if (!isClickInsideNav && !isClickInsideContainer && !isClickOnToggle && 
            (navLinks?.classList.contains('show') || containerList?.classList.contains('show'))) {
            navLinks?.classList.remove('show');
            containerList?.classList.remove('show');
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            navLinks?.classList.remove('show');
            containerList?.classList.remove('show');
        }
    });
});


        document.addEventListener('DOMContentLoaded', function() {
            // Tự động ẩn flash messages sau 5 giây
            const flashMessages = document.querySelectorAll('.flash-message');
            
            flashMessages.forEach(function(message) {
                setTimeout(function() {
                    // Thêm class fade-out để có hiệu ứng mượt mà
                    message.classList.add('fade-out');
                    
                    // Xóa element sau khi animation hoàn thành
                    setTimeout(function() {
                        if (message.parentNode) {
                            message.parentNode.removeChild(message);
                        }
                    }, 500); // 500ms cho animation fade-out
                }, 5000); // 5000ms = 5 giây
            });
            
            // tắt thông báo
            const closeButtons = document.querySelectorAll('.flash-message .btn-close');
            closeButtons.forEach(function(button) {
                button.addEventListener('click', function() {
                    const message = button.closest('.flash-message');
                    message.classList.add('fade-out');
                    
                    setTimeout(function() {
                        if (message.parentNode) {
                            message.parentNode.removeChild(message);
                        }
                    }, 500);
                });
            });
        });