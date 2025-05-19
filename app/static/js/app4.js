
        const recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognitionInstance = null;

        if (recognition) {
            recognitionInstance = new recognition();
            recognitionInstance.lang = 'vi-VN';
            recognitionInstance.continuous = false;
            recognitionInstance.interimResults = false;

            recognitionInstance.onstart = function () {
                document.getElementById("output-text").textContent = "Đang nghe...";
                console.log("Đang nhận diện giọng nói...");
                document.getElementById("result").innerHTML = `
                    <div class='loading'>Đang nhận diện giọng nói</div>`;
            };

            recognitionInstance.onerror = function (event) {
                console.log("Lỗi nhận diện giọng nói: ", event.error);
                document.getElementById("result").innerHTML = `
                    <div class='error'>
                        <strong>Lỗi!</strong> Không thể nhận diện giọng nói. Vui lòng thử lại.
                    </div>`;
                stopRecording();
            };

            recognitionInstance.onresult = function (event) {
                let transcript = "";
                for (let i = 0; i < event.results.length; i++) {
                    transcript += event.results[i][0].transcript + " ";
                } 
                document.getElementById("output-text").textContent = transcript.trim();
                console.log("Bạn đã nói: ", transcript);
                document.getElementById("result").innerHTML = `
                    <div class='loading'>Đang tìm kiếm địa điểm phù hợp</div>`;
                
                fetch('/du-lich', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ question: transcript })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        let resultHTML = '';
                        data.itinerary.provinces.forEach(province => {
                            resultHTML += `
                                <div class="province-box">
                                    <h3>${province.province}</h3>
                                    <div>
                                        ${province.places.map(place => `
                                            <div class="place">
                                                <strong>${place.name}</strong>
                                                <p>${place.description}</p>
                                            </div>
                                        `).join('')}
                                    </div>
                                    <button class="province-btn" onclick="selectProvince('${province.province}')">
                                        Xem chi tiết về ${province.province}
                                    </button>
                                </div>
                            `;
                        });

                        document.getElementById("result").innerHTML = resultHTML;
                        stopRecording();
                    } else {
                        document.getElementById("result").innerHTML = `
                            <div class='error'>
                                <strong>Rất tiếc!</strong> ${data.error || "Không tìm thấy thông tin phù hợp. Vui lòng thử lại với địa điểm khác."}
                            </div>`;
                        stopRecording();
                    }
                })
                .catch(error => {
                    console.error('Lỗi khi gửi câu hỏi lên server:', error);
                    document.getElementById("result").innerHTML = `
                        <div class='error'>
                            <strong>Đã có lỗi xảy ra!</strong> Không thể kết nối với máy chủ. Vui lòng thử lại sau.
                        </div>`;
                    stopRecording();
                });
            };

            recognitionInstance.onend = function() {
                console.log("Đã dừng nhận diện giọng nói.");
            };
        } else {
            document.getElementById("result").innerHTML = `
                <div class='error'>
                    <strong>Không hỗ trợ!</strong> Trình duyệt của bạn không hỗ trợ tính năng Nhận diện Giọng nói. Vui lòng sử dụng Chrome, Edge hoặc Safari mới nhất.
                </div>`;
        }

        document.getElementById('start-btn').addEventListener('click', toggleRecording);
        document.getElementById('mic').addEventListener('click', stopRecording);
        document.getElementById('close-overlay').addEventListener('click', stopRecording);

        let isRecording = false; 

        function toggleRecording() {
            const overlay = document.getElementById('overlay');
            const mic = document.getElementById('mic');

            if (!isRecording) {
                // Bắt đầu ghi âm
                recognitionInstance.start();
                overlay.classList.add('active');
                mic.classList.add('active');
                isRecording = true;
                
                // Add a slight delay for animation purposes
                setTimeout(() => {
                    document.getElementById("output-text").textContent = "Đang nghe...";
                }, 300);
            } 
            else {
                stopRecording();
            }
        }

        function stopRecording() {
            const overlay = document.getElementById('overlay');
            const mic = document.getElementById('mic');

            recognitionInstance.stop();
            overlay.classList.remove('active');
            mic.classList.remove('active');
            isRecording = false;
        }

        function selectProvince(provinceName) {
            const cleanedProvince = provinceName.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
            const encodedProvince = encodeURIComponent(cleanedProvince);
            window.location.href = `/page3?province=${encodedProvince}`;
        }