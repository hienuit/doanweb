// Auto-suggestion functionality for destination search in page3
let suggestionTimeout;
let currentSuggestionIndex = -1;

// gợi ý tự động cho phần nhập địa điểm
function initializeAutoSuggestion() {
    const destinationInput = document.getElementById("destinationInput");
    
    if (destinationInput) {
        // tạp dropdown cho phần gợi ý, xổ suống
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.id = 'suggestions-container';
        suggestionsContainer.className = 'suggestions-dropdown';
        destinationInput.parentNode.appendChild(suggestionsContainer);
        
        // khi nhấp vào gợi ý thì chuyển qua mới luôn
        destinationInput.addEventListener("input", function() {
            const query = this.value.trim();
            
            clearTimeout(suggestionTimeout);
            
            if (query.length >= 2) {
                // đợi API trả lời xong
                suggestionTimeout = setTimeout(() => {
                    fetchSuggestions(query);
                }, 300);
            } else {
                hideSuggestions();
            }
        });
        
        // xử lí điều hướng
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
                    performSearchPage3();
                }
            } else if (event.key === "Escape") {
                hideSuggestions();
            }
        });
        
        // ẩn gợi ý khi nhấp vào chỗ khác
        document.addEventListener("click", function(event) {
            if (!destinationInput.contains(event.target) && !suggestionsContainer.contains(event.target)) {
                hideSuggestions();
            }
        });
    }
}

// hàm lấy gợi ý từ routes
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

// Hiển thị gợi ý 
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
            document.getElementById("destinationInput").value = item.textContent;
        } else {
            item.classList.remove('selected');
        }
    });
}

function selectSuggestion(suggestion) {
    document.getElementById("destinationInput").value = suggestion;
    hideSuggestions();
    performSearchPage3();
}

function hideSuggestions() {
    const container = document.getElementById('suggestions-container');
    if (container) {
        container.style.display = 'none';
        container.innerHTML = '';
    }
    currentSuggestionIndex = -1;
}

function performSearchPage3() {
    const province = document.getElementById("destinationInput").value.trim();
    
    if (province) {
        window.location.href = '/page3?province=' + encodeURIComponent(province);
    } else {
        alert("Please enter a valid destination.");
    }
}

document.addEventListener("DOMContentLoaded", function () {
        // Initialize auto-suggestion
        initializeAutoSuggestion();
        
        const urlParams = new URLSearchParams(window.location.search);
        const province = urlParams.get('province');

        const destinationDetails = document.getElementById("destinationDetails");
        const Feature = document.getElementById("Feature");
        const videoOverlay = document.getElementById("videoOverlay");

        if (!province) {
            destinationDetails.textContent = "No destination selected.";
            videoOverlay.style.display = "none";
            return;
        }



        fetch(`/describe?province=${encodeURIComponent(province)}`)
            .then(response => response.json())
            .then(data => {
                Feature.innerHTML = "";
                destinationDetails.textContent = `Tỉnh: ${data.name}`;

                if (data.places && Array.isArray(data.places)) {
                    const locations = [];
                    const names = [];

                    data.places.forEach(place => {
                        const [lng, lat] = place.location.split(',').map(Number);
                        if (!isNaN(lat) && !isNaN(lng)) {
                            locations.push({ lat, lng });
                            names.push(place.name);
                        }
                    });

                    localStorage.setItem('locations', JSON.stringify(locations));
                    localStorage.setItem('activityNames', JSON.stringify(names));
                }

                if (data && data.describe) {
                    const MAX_LENGTH = 105;
                    let shortText = data.describe.substring(0, MAX_LENGTH);
                    let fullText = data.describe;

                    Feature.innerHTML = `
                        <p style="color:white; font-weight:bold; display: inline;">
                            <strong>Mô tả:</strong> 
                            <span id="short-text">${shortText}</span>...
                            <button id="toggle-popup" style="color: yellow; background: none; border: none; cursor: pointer; padding: 0; font-weight: bold;"><u>Xem thêm</u></button>
                        </p>

                        <!-- Hộp popup (sẽ bị ghi đè bởi modal mới) -->
                        <div id="popup-container" class="popup-hidden">
                            <div class="popup-content">
                                <span id="close-popup">&times;</span>
                                <h3>Mô tả chi tiết</h3>
                                <p>${fullText}</p>
                            </div>
                        </div>
                    `;
                    
                    // Lưu thông tin popup để modal mới có thể sử dụng
                    window.fullDescriptionText = fullText;

                    // Xử lý popup cũ (sẽ bị ghi đè bởi popup-modal.js)
                    const popup = document.getElementById("popup-container");
                    const openPopupBtn = document.getElementById("toggle-popup");
                    const closePopupBtn = document.getElementById("close-popup");

                    // Lưu function gốc để popup-modal.js có thể ghi đè
                    window.originalTogglePopup = function() {
                        popup.classList.remove("popup-hidden");
                    };

                    if (openPopupBtn) {
                        openPopupBtn.addEventListener("click", window.originalTogglePopup);
                    }

                    if (closePopupBtn) {
                        closePopupBtn.addEventListener("click", () => {
                            popup.classList.add("popup-hidden");
                        });
                    }

                    if (popup) {
                        window.addEventListener("click", (event) => {
                            if (event.target === popup) {
                                popup.classList.add("popup-hidden");
                            }
                        });
                        
                        window.addEventListener("touchend", (event) => {
                            if (event.target === popup) {
                                popup.classList.add("popup-hidden");
                            }
                        });
                    }
                } else {
                    Feature.innerHTML = "<p class='text-white'>No description found for this destination.</p>";
                }
            })
            .catch(error => {
                console.error("Error fetching description:", error);
                Feature.innerHTML = "<p class='text-white'>Error fetching data. Please try again.</p>";
            });

        videoOverlay.style.display = "none";
    });


document.addEventListener("DOMContentLoaded", function () {
    let background = document.querySelector(".container_vien");
    let carousel = document.getElementById("carouselExample");

    function updateBackground() {
        let activeSlide = document.querySelector(".carousel-item.active img");
        if (activeSlide) {
            background.style.backgroundImage = `url(${activeSlide.src})`;
        }
    }

    carousel.addEventListener("slid.bs.carousel", updateBackground);
    updateBackground();
});



document.getElementById("submitDetails").addEventListener("click", function() {
    // Blur input focus to hide mobile keyboard
    document.getElementById("days").blur();
    
    const videoOverlay = document.getElementById("videoOverlay");
    const skipBtn = document.getElementById("skipBtn");
    const skipcountdown = document.getElementById("skipcountdown");
    const loadingContainer = document.getElementById("loadingContainer");
    let isApiRequestComplete = false;

    const urlParams = new URLSearchParams(window.location.search);
    const province = urlParams.get("province");
    const destination = province;

    const days = document.getElementById("days").value;
    const budget = document.getElementById("budget").value;

    if (!destination || !days || !budget) {
        alert("Vui lòng điền đầy đủ thông tin!");
        videoOverlay.style.display = "none";
        return;
    }

    localStorage.setItem('selectedDestination', JSON.stringify({
        name: destination,
        budget: budget,
        days: days
    }));

    const requestData = {
        destination: destination,
        days: days,
        budget: budget
    };
    
    videoOverlay.style.display = "flex";
    skipcountdown.style.display = "block";
    let countdown = 5;
    skipcountdown.textContent = 'Bỏ qua sau 5s';

    const timer = setInterval(() => {
        countdown--;
        if (countdown > 0) {
            skipcountdown.innerHTML = `Bỏ qua sau ${countdown}s`;
        } else {
            clearInterval(timer);
            skipcountdown.style.display = "none"; // Ẩn bộ đếm
            skipBtn.style.display = "flex"; // Hiện nút bỏ qua
        }
    }, 1000); 

    skipBtn.onclick = function() {
        videoOverlay.style.display = "none"; // Ẩn video khi bấm bỏ qua
        if (!isApiRequestComplete) {
            loadingContainer.style.display = "flex";
        }
    };

    const apiURL = `${window.location.origin}/create-itinerary`;
    fetch(apiURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        isApiRequestComplete = true;
        loadingContainer.style.display = "none";
        
        if (data.success) {
            localStorage.setItem('itinerary', JSON.stringify(data.itinerary));
            videoOverlay.style.display = "none";
            window.location.href = `/schedule?destination=${encodeURIComponent(destination)}`;
        } else {
            alert("Có lỗi xảy ra: " + data.error);
            videoOverlay.style.display = "none";
        }
    })
    .catch(error => {
        isApiRequestComplete = true;
        loadingContainer.style.display = "none";
        
        console.error("Error:", error);

        alert("Đã xảy ra lỗi khi gửi yêu cầu.");
        videoOverlay.style.display = "none";
    });
});




const backToTopButton = document.getElementById('backToTop');
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
                backToTopButton.classList.add('visible');
        } 
        else {
                backToTopButton.classList.remove('visible');
        }
});
        
backToTopButton.addEventListener('click', function(e) {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
});




