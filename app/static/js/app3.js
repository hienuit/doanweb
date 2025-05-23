document.addEventListener("DOMContentLoaded", function () {
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


    document.getElementById("destinationInput").addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            const province = event.target.value.trim();

            if (province) {
                // Gửi kèm tên tỉnh trên URL
                window.location.href = '/page3?province=' + encodeURIComponent(province);
            } else {
                alert("Please enter a valid destination.");
            }
        }
});



document.getElementById("submitDetails").addEventListener("click", function() {
    // Blur input focus to hide mobile keyboard
    document.getElementById("days").blur();
    
    // loadingoverlay = document.getElementById("loadingOverlay");
    // loadingoverlay.style.display = "flex";


    const videoOverlay = document.getElementById("videoOverlay");
    const skipBtn = document.getElementById("skipBtn");
    const skipcountdown = document.getElementById("skipcountdown");

    const urlParams = new URLSearchParams(window.location.search);
    const province = urlParams.get("province");
    const destination = province;

    const days = document.getElementById("days").value;
    const budget = document.getElementById("budget").value;

    if (!destination || !days || !budget) {
        // loadingoverlay.style.display = "none";
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
    skipcountdown.style.display =  "block";
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
        // loadingoverlay.style.display = "none";
        if (data.success) {
            // Lưu dữ liệu vào localStorage
            localStorage.setItem('itinerary', JSON.stringify(data.itinerary));
            videoOverlay.style.display = "none";

        // Chuyển sang trang HTML mới để hiển thị
        window.location.href = `/schedule?destination=${encodeURIComponent(destination)}`;
        } 
        
        else {
            alert("Có lỗi xảy ra: " + data.error);
            videoOverlay.style.display = "none";
        }
    })
    .catch(error => {
        // loadingoverlay.style.display = "none";
        console.error("Error:", error);
        alert("Đã xảy ra lỗi khi gửi yêu cầu.");
        videoOverlay.style.display = "none";
    });
});


function displayItinerary(itinerary) {
    const Feature = document.getElementById("Feature");
    Feature.innerHTML = "";
    
    let itineraryHTML = "<h2>Itinerary for Your Trip</h2>";

    
    itinerary.days.forEach(day => {
        itineraryHTML += `<div class="day-schedule"><h3>Day ${day.day}</h3>`;
        itineraryHTML += `<ul class="activities-list">`;

        day.activities.forEach(activity => {
            itineraryHTML += `<li>
                                <strong>${activity.name}</strong>: ${activity.description}
                                <br><strong>Cost:</strong> ${activity.cost}
                              </li>`;
        });

        itineraryHTML += `</ul>`;
        itineraryHTML += `<p><strong>Estimated Cost for Day ${day.day}:</strong> ${day.estimated_cost}</p></div>`;
    });

    itineraryHTML += `<h3>Total Estimated Cost: ${itinerary.total_estimated_cost}</h3>`;
    Feature.innerHTML = itineraryHTML;
}


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




