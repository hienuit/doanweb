
let map, directionsService, directionsRenderer, carMarker;
let routeCoords = [], stepIndex = 0;
let speed = 100;
let hotelMarkers = [];
let infoWindows = [];
let totalDistance = 0;
let totalDuration = 0;
let animationInProgress = false;
let animationTimeout = null;
let currentInfoWindow = null;

const storedLocations = JSON.parse(localStorage.getItem('locations')) || [];
const activityNames = JSON.parse(localStorage.getItem('activityNames')) || [];
console.log("Storage data - locations:", storedLocations);
console.log("Storage data - activityNames:", activityNames);
let coords = [];

// Map styles
const mapStyles = {
  default: null,
  satellite: "satellite",
  terrain: "terrain",
  night: [
    {elementType: "geometry", stylers: [{color: "#242f3e"}]},
    {elementType: "labels.text.stroke", stylers: [{color: "#242f3e"}]},
    {elementType: "labels.text.fill", stylers: [{color: "#746855"}]},
    {
      featureType: "administrative.locality",
      elementType: "labels.text.fill",
      stylers: [{color: "#d59563"}],
    },
    {
      featureType: "poi",
      elementType: "labels.text.fill",
      stylers: [{color: "#d59563"}],
    },
    {
      featureType: "poi.park",
      elementType: "geometry",
      stylers: [{color: "#263c3f"}],
    },
    {
      featureType: "poi.park",
      elementType: "labels.text.fill",
      stylers: [{color: "#6b9a76"}],
    },
    {
      featureType: "road",
      elementType: "geometry",
      stylers: [{color: "#38414e"}],
    },
    {
      featureType: "road",
      elementType: "geometry.stroke",
      stylers: [{color: "#212a37"}],
    },
    {
      featureType: "road",
      elementType: "labels.text.fill",
      stylers: [{color: "#9ca5b3"}],
    },
    {
      featureType: "road.highway",
      elementType: "geometry",
      stylers: [{color: "#746855"}],
    },
    {
      featureType: "road.highway",
      elementType: "geometry.stroke",
      stylers: [{color: "#1f2835"}],
    },
    {
      featureType: "road.highway",
      elementType: "labels.text.fill",
      stylers: [{color: "#f3d19c"}],
    },
    {
      featureType: "transit",
      elementType: "geometry",
      stylers: [{color: "#2f3948"}],
    },
    {
      featureType: "transit.station",
      elementType: "labels.text.fill",
      stylers: [{color: "#d59563"}],
    },
    {
      featureType: "water",
      elementType: "geometry",
      stylers: [{color: "#17263c"}],
    },
    {
      featureType: "water",
      elementType: "labels.text.fill",
      stylers: [{color: "#515c6d"}],
    },
    {
      featureType: "water",
      elementType: "labels.text.stroke",
      stylers: [{color: "#17263c"}],
    },
  ]
};

// Hàm tạo mới biểu tượng khách sạn tùy chỉnh
function createHotelMarker(index) {
  const div = document.createElement('div');
  div.className = 'hotel-icon';
  div.textContent = 'H';
  
  return {
    url: 'https://cdn-icons-png.flaticon.com/512/484/484167.png',
    size: new google.maps.Size(34, 34),
    scaledSize: new google.maps.Size(34, 34),
    origin: new google.maps.Point(0, 0),
    anchor: new google.maps.Point(17, 17)
  };
}

// Phân tích tọa độ từ localStorage
function parseCoordinates() {
  console.log("Parsing coordinates from storedLocations:", storedLocations);
  
  if (storedLocations.length === 0) {
    alert("Không có địa điểm nào được lưu. Vui lòng chọn lại điểm đến.");
    return;
  }
  
  for (let i = 0; i < storedLocations.length; i++) {
    const coordParts = storedLocations[i].split(',');
    if (coordParts.length === 2) {
      const lng = parseFloat(coordParts[0].trim());
      const lat = parseFloat(coordParts[1].trim());
      if (!isNaN(lng) && !isNaN(lat)) {
        coords.push({ lat, lng });
      }
    }
  }
  
  console.log("Parsed coordinates:", coords);
  
  if (coords.length >= 2) {
    initMapWithCoords();
  } else {
    alert("Không đủ tọa độ hợp lệ để tạo tuyến đường.");
  }
}

// Khởi tạo map và các thành phần - Cần được gọi tự động khi Google Maps API load xong
function initMap() {
  // Khởi tạo map với tọa độ mặc định (Hà Nội)
  map = new google.maps.Map(document.getElementById("map"), {
    center: {lat: 21.0278, lng: 105.8388},
    zoom: 14,
    mapTypeControl: true,
    mapTypeControlOptions: {
      style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
      position: google.maps.ControlPosition.TOP_LEFT
    }
  });
  
  // Xử lý slider tốc độ
  document.getElementById("speedSlider").addEventListener("input", e => {
    speed = parseInt(e.target.value);
    document.getElementById("speedLabel").textContent = speed;
  });
  
  // Xử lý nút tìm khách sạn
  document.getElementById("findHotelsBtn").addEventListener("click", function() {
    this.style.display = "block"; // Hiển thị nút hiện tại
    const currentPosition = carMarker ? carMarker.getPosition() : coords[coords.length - 1];
    findNearbyHotels(currentPosition);
  });
  
  // Xử lý chuyển đổi kiểu bản đồ
  const styleButtons = document.querySelectorAll('.style-button');
  styleButtons.forEach(button => {
    button.addEventListener('click', function() {
      const style = this.getAttribute('data-style');
      
      // Cập nhật kiểu bản đồ
      if (style === 'satellite') {
        map.setMapTypeId(google.maps.MapTypeId.SATELLITE);
      } else if (style === 'terrain') {
        map.setMapTypeId(google.maps.MapTypeId.TERRAIN);
      } else if (style === 'night') {
        map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
        map.setOptions({styles: mapStyles.night});
      } else {
        map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
        map.setOptions({styles: null});
      }
      
      // Cập nhật trạng thái nút
      styleButtons.forEach(btn => btn.classList.remove('active'));
      this.classList.add('active');
    });
  });
  
  // Xử lý nút gợi ý
  const tipsButton = document.getElementById('tips-button');
  const tipsContainer = document.getElementById('tips-container');
  const tipsCloseBtn = document.getElementById('tips-close');
  
  // Kiểm tra xem người dùng đã xem gợi ý chưa
  const tipsViewed = localStorage.getItem('tipsViewed') === 'true';
  if (tipsViewed) {
    // Nếu đã xem, ẩn chấm đỏ nhấp nháy
    const notificationDot = tipsButton.querySelector('.notification-dot');
    notificationDot.classList.remove('blink');
    notificationDot.style.display = 'none';
  }
  
  tipsButton.addEventListener('click', function() {
    tipsContainer.style.display = 'block';
    
    // Đánh dấu đã xem gợi ý
    localStorage.setItem('tipsViewed', 'true');
    const notificationDot = this.querySelector('.notification-dot');
    notificationDot.classList.remove('blink');
    notificationDot.style.display = 'none';
  });
  
  tipsCloseBtn.addEventListener('click', function() {
    tipsContainer.style.display = 'none';
  });
  
  // Đóng gợi ý khi click bên ngoài
  window.addEventListener('click', function(event) {
    if (!tipsContainer.contains(event.target) && event.target !== tipsButton) {
      tipsContainer.style.display = 'none';
    }
  });
  
  // Xử lý nút bắt đầu hành trình
  document.getElementById("start-trip-btn").addEventListener("click", function() {
  this.classList.remove("visible");
  this.classList.add("hidden");
  document.getElementById("reset-trip-btn").classList.remove("hidden");
  document.getElementById("reset-trip-btn").classList.add("visible");

  if (!animationInProgress) {
    animationInProgress = true;

    if (!carMarker) {
      startAnimation();
    } else {
      animateMarker();
    }
  }
});

  
  // Xử lý nút đặt lại hành trình
  document.getElementById("reset-trip-btn").addEventListener("click", function() {
  this.classList.remove("visible");
  this.classList.add("hidden");
  document.getElementById("start-trip-btn").classList.remove("hidden");
  document.getElementById("start-trip-btn").classList.add("visible");

  if (animationTimeout) clearTimeout(animationTimeout);
  if (carMarker) {
    carMarker.setMap(null);
    carMarker = null;
  }

  stepIndex = 0;
  animationInProgress = false;
  document.getElementById("progress").textContent = "0%";

  showModal("Hành trình đã được đặt lại");
});

  
  // Phân tích tọa độ
  parseCoordinates();
  
  // Hiển thị gợi ý tự động khi lần đầu truy cập
  if (!tipsViewed) {
    setTimeout(() => {
      tipsContainer.style.display = 'block';
    }, 2000); // Hiển thị sau 2 giây
  }
}

function initMapWithCoords() {
  // Thiết lập map với tọa độ đầu tiên
  if (coords.length > 0) {
    map.setCenter(coords[0]);
  }
  const sharedInfoWindow = new google.maps.InfoWindow();

  coords.forEach((coord, i) => {
    const marker = new google.maps.Marker({
      position: coord,
      map: map,
      label: {
        text: (i + 1).toString(),
        color: 'white'
      },
      title: activityNames[i] || `Điểm ${i + 1}`
    });

    marker.addListener('click', () => {
      sharedInfoWindow.setContent(`<div><strong>Điểm ${i + 1}</strong><br>${activityNames[i] || ''}</div>`);
      sharedInfoWindow.open(map, marker);
    });

  });
  
  // Cập nhật số điểm dừng
  document.getElementById('total-stops').textContent = coords.length;
  
  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer({ 
    suppressMarkers: true,
    polylineOptions: {
      strokeColor: '#4285F4',
      strokeWeight: 5
    }
  });
  directionsRenderer.setMap(map);
  calcRoute();
}

function calcRoute() {
  if (coords.length < 2) {
    console.error("Not enough coordinates to calculate route");
    return;
  }
  
  console.log("Calculating route with coordinates:", coords);
  console.log("Origin:", coords[0]);
  console.log("Destination:", coords[coords.length - 1]);
  console.log("Waypoints:", coords.slice(1, coords.length - 1));
  
  const waypoints = coords.slice(1, coords.length - 1).map(loc => ({ location: loc, stopover: true }));
  directionsService.route({
    origin: coords[0],
    destination: coords[coords.length - 1],
    waypoints: waypoints,
    travelMode: google.maps.TravelMode.DRIVING
  }, (response, status) => {
    console.log("Direction service response status:", status);
    if (status === 'OK') {
      directionsRenderer.setDirections(response);
      // Lấy tất cả các điểm từ route
      routeCoords = [];
      totalDistance = 0;
      totalDuration = 0;
      
      // Tính tổng quãng đường và thời gian
      response.routes[0].legs.forEach(leg => {
        totalDistance += leg.distance.value;
        totalDuration += leg.duration.value;
        
        leg.steps.forEach(step => {
          step.path.forEach(p => routeCoords.push(p));
        });
      });
      
      // Cập nhật thông tin chuyến đi
      document.getElementById('total-distance').textContent = 
        (totalDistance / 1000).toFixed(1) + ' km';
      
      document.getElementById('total-duration').textContent = 
        formatDuration(totalDuration);
      
      // KHÔNG tự động bắt đầu animation nữa
      // startAnimation();
    } else {
      console.error("Could not calculate route:", status);
      alert("Không thể tính toán tuyến đường: " + status);
    }
  });
}

// Định dạng thời gian từ giây sang giờ:phút
function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (hours > 0) {
    return `${hours} giờ ${minutes} phút`;
  } else {
    return `${minutes} phút`;
  }
}

function startAnimation() {
  carMarker = new google.maps.Marker({
    position: routeCoords[0],
    map: map,
    icon: { 
      url: 'https://cdn-icons-png.flaticon.com/512/684/684908.png', 
      scaledSize: new google.maps.Size(32, 32) 
    }
  });
  animateMarker();
}

function animateMarker() {
  if (stepIndex >= routeCoords.length) {
    showModal("Đã đến đích!"); 
    animationInProgress = false;
    document.getElementById("start-trip-btn").style.display = "block";
    document.getElementById("reset-trip-btn").style.display = "none";
    return;
  }
  
  carMarker.setPosition(routeCoords[stepIndex]);
  map.panTo(routeCoords[stepIndex]);
  
  // Cập nhật tiến độ
  const progress = Math.floor((stepIndex / routeCoords.length) * 100);
  document.getElementById('progress').textContent = progress + '%';
  
  coords.forEach((pt, i) => {
    const dx = Math.abs(routeCoords[stepIndex].lat() - pt.lat);
    const dy = Math.abs(routeCoords[stepIndex].lng() - pt.lng);
    if (dx < 0.0005 && dy < 0.0005) {
      showModal(`Đã đến điểm ${i + 1} ${activityNames[i] ? '(' + activityNames[i] + ')' : ''}`);
      if ((i - 1) % 2 === 0 && i !== 0) setTimeout(showGifSmall, 1000);
    }
  });
  
  stepIndex++;
  // Lưu timeout để có thể hủy nếu cần
  animationTimeout = setTimeout(animateMarker, speed);
}

function showModal(msg) {
  const modal = document.getElementById("myModal");
  document.getElementById("modalMessage").textContent = msg;
  modal.style.display = "block";
  setTimeout(() => modal.style.display = "none", 2000);
}

function showGifSmall() {
  const gif = document.getElementById("gifSmall");
  gif.style.display = "block";
  setTimeout(() => gif.style.display = "none", 3000);
}

// Tìm khách sạn gần đó
function findNearbyHotels(location) {
  // Xóa các marker khách sạn cũ
  clearHotelMarkers();
  
  // Hiển thị thông báo đang tìm kiếm
  showModal("Đang tìm kiếm khách sạn gần đây...");
  
  try {
    const request = {
      query: 'khách sạn',
      location: location,
      radius: 2000,
      fields: ['name', 'geometry', 'rating', 'photos', 'place_id'],
    };
    
    const service = new google.maps.places.PlacesService(document.createElement('div'));
    
    service.textSearch(request, (results, status) => {
      if (status === google.maps.places.PlacesServiceStatus.OK && results && results.length > 0) {
        results.slice(0, 10).forEach((place, index) => {
          if (place.geometry && place.geometry.location) {
            const marker = new google.maps.Marker({
              map: map,
              position: place.geometry.location,
              icon: createHotelMarker(index),
              title: place.name,
              animation: google.maps.Animation.DROP
            });
            
            hotelMarkers.push(marker);
            
            const photoUrl = place.photos && place.photos.length > 0 
              ? place.photos[0].getUrl({ maxWidth: 200 }) 
              : 'https://via.placeholder.com/200x120?text=No+Image';
              
            const contentString = `
              <div class="hotel-info-window">
                <img src="${photoUrl}" alt="${place.name}" style="width: 100%; height: auto; border-radius: 4px;">
                <h4>${place.name}</h4>
                <p>⭐ ${place.rating || 'Chưa có đánh giá'}</p>
                <a href="https://www.google.com/maps/place/?q=place_id:${place.place_id}" target="_blank">
                  🔗 Xem trên Google Maps
                </a>
              </div>
            `;
            
            const infowindow = new google.maps.InfoWindow({
              content: contentString,
              maxWidth: 300
            });
            
            infoWindows.push(infowindow);
            
            marker.addListener('click', () => {
              // Đóng InfoWindow hiện tại nếu có
              if (currentInfoWindow) {
                currentInfoWindow.close();
              }
              // Mở InfoWindow mới
              infowindow.open(map, marker);
              // Lưu trữ InfoWindow hiện tại
              currentInfoWindow = infowindow;
            });
          }
        });
        
        showModal(`Đã tìm thấy ${Math.min(results.length, 10)} khách sạn gần đây`);
      } else {
        console.error("Lỗi tìm khách sạn:", status);
        showModal("Không tìm thấy khách sạn nào trong khu vực này");
      }
    });
  } catch (error) {
    console.error("Lỗi khi tìm khách sạn:", error);
    showModal("Có lỗi xảy ra khi tìm khách sạn");
  }
}

// Xóa tất cả marker khách sạn
function clearHotelMarkers() {
  hotelMarkers.forEach(marker => marker.setMap(null));
  hotelMarkers = [];
  infoWindows = [];
}

// Hàm để ẩn tất cả các nút
function hideAllButtons() {
  document.getElementById("findHotelsBtn").style.display = "none";
  document.getElementById("tips-button").style.display = "none";
  document.getElementById("start-trip-btn").style.display = "none";
  document.getElementById("reset-trip-btn").style.display = "none";
}

// Hàm để hiển thị lại tất cả các nút cơ bản
function showDefaultButtons() {
  document.getElementById("findHotelsBtn").style.display = "block";
  document.getElementById("tips-button").style.display = "block";
  document.getElementById("start-trip-btn").style.display = "block";
  document.getElementById("reset-trip-btn").style.display = "none"; // Mặc định ẩn nút reset
}
