    document.addEventListener('DOMContentLoaded', function() {
    // Elements
        const moodSelect = document.getElementById('moodSelect');
        const destinationContainer = document.getElementById('destinationContainer');
        const destinationSelect = document.getElementById('locationSelect');
        const nextButtonElement = document.getElementById('nextButtonElement');
        const tab1 = document.getElementById('Tab1');
        const tab2 = document.getElementById('Tab2');
        const placesList = document.getElementById('placesList');
        const placesDiv = document.getElementById('Places');
        
        // Location options
        const beachButton = document.getElementById('beachButton');
        const mountainButton = document.getElementById('mountainButton');
        const cityButton = document.getElementById('cityButton');
        
        // Add back button to tab2
        const backButton = document.createElement('button');
        backButton.type = 'button';
        backButton.className = 'btn btn-outline-secondary mt-4';
        backButton.innerHTML = '<i class="fas fa-arrow-left me-2"></i> Quay lại';
        
        // Insert back button before the location options
        const locationOptions = document.querySelector('.location-options');
        tab2.insertBefore(backButton, locationOptions);
        
        // Initially hide tab2
        tab2.style.display = 'none';
        
        // Show destination select when mood is selected
        moodSelect.addEventListener('change', function() {
            if (this.value) {
                destinationContainer.classList.remove('hidden');
                destinationContainer.style.display = 'block';
            } else {
                destinationContainer.classList.add('hidden');
                destinationContainer.style.display = 'none';
                nextButtonElement.classList.add('hidden');
                nextButtonElement.style.display = 'none';
            }
        });
        
        // Show next button when destination is selected
        destinationSelect.addEventListener('change', function() {
            if (this.value) {
                nextButtonElement.classList.remove('hidden');
                nextButtonElement.style.display = 'inline-block';
            } else {
                nextButtonElement.classList.add('hidden');
                nextButtonElement.style.display = 'none';
            }
        });
        
        // Move to next tab and show location options
        nextButtonElement.addEventListener('click', function() {
            tab1.style.display = 'none';
            tab2.style.display = 'block';
            tab2.classList.remove('hidden');
            
            // Show the location options
            document.querySelector('.location-options').style.display = 'flex';
            
            // Hide the places section until a location is selected
            placesDiv.style.display = 'none';
        });
        
        // Handle back button click
        backButton.addEventListener('click', function() {
            tab2.style.display = 'none';
            tab1.style.display = 'block';
            
            // Reset the active state of location buttons
            [beachButton, mountainButton, cityButton].forEach(btn => btn.classList.remove('active'));
            
            // Hide the places section
            placesDiv.style.display = 'none';
        });
        
        // Handle location button clicks
        beachButton.addEventListener('click', function() {
            [beachButton, mountainButton, cityButton].forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            showSuggestedPlaces('beach');
        });
        
        mountainButton.addEventListener('click', function() {
            [beachButton, mountainButton, cityButton].forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            showSuggestedPlaces('mountain');
        });
        
        cityButton.addEventListener('click', function() {
            [beachButton, mountainButton, cityButton].forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            showSuggestedPlaces('river');
        });
        
        // Function to fetch suggested places based on location type
        let selectedDestination = null; // Store the selected destination
        
        function showSuggestedPlaces(locationType) {
            const mood = moodSelect.value;
            const location = destinationSelect.value;
            
            // Show loading indicator
            placesList.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Đang tải...</div>';
            placesDiv.style.display = 'block';
            placesDiv.classList.remove('hidden');
            
            // Fetch data from backend
            fetch(`/search?mood=${mood}&place=${locationType}&location=${location}`)
                .then(response => response.json())
                .then(data => {
                    placesList.innerHTML = "";
                    
                    if (data.length === 0) {
                        placesList.innerHTML = '<p class="text-center">Không tìm thấy địa điểm phù hợp.</p>';
                        return;
                    }
                    
                    // Create list items for each destination
                    data.forEach(destination => {
                        const li = document.createElement('li');
                        li.className = 'place-item';
                        li.innerHTML = `
                            <div>
                                <div class="place-name">${destination.name}</div>
                                <div class="place-details">Phù hợp với lựa chọn của bạn</div>
                            </div>
                            <i class="fas fa-arrow-right place-arrow"></i>
                        `;
                        
                        // Add click event to each item
                        li.addEventListener('click', function() {
                            selectedDestination = {
                                id: destination.id,
                                name: destination.name
                            };
                            
                            console.log("Đã chọn:", selectedDestination);
                            
                            // Store selected destination in localStorage
                            localStorage.setItem('selectedDestination', JSON.stringify(selectedDestination));
                            
                            // Redirect to destination details page
                            window.location.href = `/page3?province=${encodeURIComponent(destination.name)}`;
                        });
                        
                        placesList.appendChild(li);
                    });
                })
                .catch(error => {
                    console.error("Lỗi khi tải dữ liệu:", error);
                    placesList.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-circle"></i> 
                            Có lỗi xảy ra khi tải dữ liệu. Vui lòng thử lại sau.
                        </div>
                    `;
                });
        }
        
        // Back to top button functionality
        const backToTopButton = document.getElementById('backToTop');
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.classList.add('visible');
            } else {
                backToTopButton.classList.remove('visible');
            }
        });
        
        backToTopButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
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

