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

// Day-based navigation variables
let itineraryData = null;
let currentDay = 1;
let totalDays = 1;
let dayRoutes = {}; // Store routes for each day
let dayCoords = {}; // Store coordinates for each day
let dayActivityNames = {}; // Store activity names for each day
let autoPlayMode = false;
let autoPlayTimeout = null;

// Legacy variables - kept for compatibility but not used in day-based system
const storedLocations = JSON.parse(localStorage.getItem('locations')) || [];
const activityNames = JSON.parse(localStorage.getItem('activityNames')) || [];
let coords = []; // Legacy - use dayCoords instead

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

// Legacy function - kept for compatibility but not used in day-based navigation
function parseCoordinates() {
  // This function is no longer used in the new day-based system
  // All coordinate parsing is now handled by parseItineraryData()
  console.log("Legacy parseCoordinates called - redirecting to new system");
}

// Initialize map and components
function initMap() {
  // Initialize map with default coordinates (Hanoi)
  map = new google.maps.Map(document.getElementById("map"), {
    center: {lat: 21.0278, lng: 105.8388},
    zoom: 14,
    mapTypeControl: true,
    mapTypeControlOptions: {
      style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
      position: google.maps.ControlPosition.TOP_LEFT
    }
  });
  
  directionsService = new google.maps.DirectionsService();
  
  // Parse itinerary data
  if (!parseItineraryData()) {
    return;
  }
  
  // Initialize day navigation
  updateDayNavigation();
  loadDayRoute();
  
  // Event listeners for day navigation
  document.getElementById("prevDayBtn").addEventListener("click", goToPreviousDay);
  document.getElementById("nextDayBtn").addEventListener("click", goToNextDay);
  
  // Speed slider
  document.getElementById("speedSlider").addEventListener("input", e => {
    speed = parseInt(e.target.value);
    document.getElementById("speedLabel").textContent = speed;
  });
  
  // Hotel search button
  document.getElementById("findHotelsBtn").addEventListener("click", function() {
    const currentPosition = carMarker ? carMarker.getPosition() : 
                           (dayCoords[currentDay] && dayCoords[currentDay].length > 0 ? 
                            dayCoords[currentDay][0] : map.getCenter());
    findNearbyHotels(currentPosition);
  });
  
  // Map style controls
  const styleButtons = document.querySelectorAll('.style-button');
  styleButtons.forEach(button => {
    button.addEventListener('click', function() {
      const style = this.getAttribute('data-style');
      
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
      
      styleButtons.forEach(btn => btn.classList.remove('active'));
      this.classList.add('active');
    });
  });
  
  // Tips functionality
  const tipsButton = document.getElementById('tips-button');
  const tipsContainer = document.getElementById('tips-container');
  const tipsCloseBtn = document.getElementById('tips-close');
  
  const tipsViewed = localStorage.getItem('tipsViewed') === 'true';
  if (tipsViewed) {
    const notificationDot = tipsButton.querySelector('.notification-dot');
    notificationDot.classList.remove('blink');
    notificationDot.style.display = 'none';
  }
  
  tipsButton.addEventListener('click', function() {
    tipsContainer.style.display = 'block';
    localStorage.setItem('tipsViewed', 'true');
    const notificationDot = this.querySelector('.notification-dot');
    notificationDot.classList.remove('blink');
    notificationDot.style.display = 'none';
  });
  
  tipsCloseBtn.addEventListener('click', function() {
    tipsContainer.style.display = 'none';
  });
  
  window.addEventListener('click', function(event) {
    if (!tipsContainer.contains(event.target) && event.target !== tipsButton) {
      tipsContainer.style.display = 'none';
    }
  });
  
  // Trip control buttons
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
  
  document.getElementById("reset-trip-btn").addEventListener("click", function() {
    resetAnimation();
    showModal("Hành trình ngày này đã được đặt lại");
  });
  
  document.getElementById("auto-play-btn").addEventListener("click", function() {
    if (autoPlayMode) {
      stopAutoPlay();
      showModal("Đã dừng chế độ tự động");
    } else {
      startAutoPlay();
      showModal("Bắt đầu chế độ tự động chạy tất cả ngày");
    }
  });
  
  // Show tips automatically for first-time users
  if (!tipsViewed) {
    setTimeout(() => {
      tipsContainer.style.display = 'block';
    }, 2000);
  }
}

// Legacy function - no longer used in day-based system
function initMapWithCoords() {
  console.log("Legacy initMapWithCoords called - not used in new system");
}

// Legacy function - replaced by calcDayRoute
function calcRoute() {
  console.log("Legacy calcRoute called - use calcDayRoute instead");
}

// Calculate distance between two points (km) - utility function
function calculateDistance(coord1, coord2) {
  const R = 6371; // Earth radius (km)
  const dLat = (coord2.lat - coord1.lat) * Math.PI / 180;
  const dLng = (coord2.lng - coord1.lng) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(coord1.lat * Math.PI / 180) * Math.cos(coord2.lat * Math.PI / 180) *
            Math.sin(dLng/2) * Math.sin(dLng/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

// Giảm số waypoints bằng cách chọn các điểm quan trọng
function reduceWaypoints(coords, maxWaypoints) {
  if (coords.length <= maxWaypoints + 2) return coords;
  
  const result = [coords[0]]; // Luôn giữ điểm đầu
  const step = Math.floor((coords.length - 2) / maxWaypoints);
  
  for (let i = step; i < coords.length - 1; i += step) {
    result.push(coords[i]);
  }
  
  result.push(coords[coords.length - 1]); // Luôn giữ điểm cuối
  return result;
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

// Start animation for current day
function startAnimation() {
  if (!routeCoords || routeCoords.length === 0) {
    showModal("Không có lộ trình để hiển thị cho ngày này.");
    return;
  }
  
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

// Animate marker along route
function animateMarker() {
  if (stepIndex >= routeCoords.length) {
    showModal(`Đã hoàn thành ngày ${currentDay}!`); 
    animationInProgress = false;
    
    // Auto advance to next day if in auto-play mode
    if (autoPlayMode && currentDay < totalDays) {
      autoPlayTimeout = setTimeout(() => {
        goToNextDay();
        setTimeout(() => {
          if (autoPlayMode) {
            startAnimation();
          }
        }, 2000);
      }, 3000);
    } else {
      // Reset buttons
      document.getElementById("start-trip-btn").classList.remove("hidden");
      document.getElementById("start-trip-btn").classList.add("visible");
      document.getElementById("reset-trip-btn").classList.remove("visible");
      document.getElementById("reset-trip-btn").classList.add("hidden");
      
      if (autoPlayMode) {
        autoPlayMode = false;
        document.getElementById("auto-play-btn").classList.remove("visible");
        document.getElementById("auto-play-btn").classList.add("hidden");
        showModal("Đã hoàn thành tất cả các ngày!");
      }
    }
    return;
  }
  
  carMarker.setPosition(routeCoords[stepIndex]);
  map.panTo(routeCoords[stepIndex]);
  
  // Update day progress
  const dayProgress = Math.floor((stepIndex / routeCoords.length) * 100);
  document.getElementById('day-progress').textContent = dayProgress + '%';
  updateTotalProgress();
  
  // Check if reached any activity points
  const coords = dayCoords[currentDay];
  const activityNames = dayActivityNames[currentDay];
  
  if (coords) {
    coords.forEach((pt, i) => {
      const dx = Math.abs(routeCoords[stepIndex].lat() - pt.lat);
      const dy = Math.abs(routeCoords[stepIndex].lng() - pt.lng);
      if (dx < 0.0005 && dy < 0.0005) {
        showModal(`Đã đến điểm ${i + 1} - ${activityNames[i] || ''} (Ngày ${currentDay})`);
        if ((i - 1) % 2 === 0 && i !== 0) setTimeout(showGifSmall, 1000);
      }
    });
  }
  
  stepIndex++;
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

// Parse itinerary data from localStorage
function parseItineraryData() {
  console.log("Parsing itinerary data...");
  
  const storedItinerary = localStorage.getItem('itinerary');
  if (!storedItinerary) {
    alert("Không có dữ liệu lịch trình. Vui lòng tạo lịch trình trước.");
    return false;
  }
  
  try {
    itineraryData = JSON.parse(storedItinerary);
    console.log("Itinerary data:", itineraryData);
    
    if (!itineraryData.days || itineraryData.days.length === 0) {
      alert("Dữ liệu lịch trình không hợp lệ.");
      return false;
    }
    
    totalDays = itineraryData.days.length;
    
    // Parse coordinates and activities for each day
    itineraryData.days.forEach((day, dayIndex) => {
      const dayNum = day.day || (dayIndex + 1);
      dayCoords[dayNum] = [];
      dayActivityNames[dayNum] = [];
      
      const scheduleItems = day.schedule || day.activities || [];
      
      scheduleItems.forEach(item => {
        // Only process activities with locations
        if ((item.type === "activity" || !item.type) && item.location) {
          const coordParts = item.location.split(',');
          if (coordParts.length === 2) {
            const lat = parseFloat(coordParts[0].trim());
            const lng = parseFloat(coordParts[1].trim());
            
            if (!isNaN(lat) && !isNaN(lng) && 
                lat >= -90 && lat <= 90 && 
                lng >= -180 && lng <= 180) {
              dayCoords[dayNum].push({ lat, lng });
              
              // Extract activity name
              let activityName = '';
              if (item.description) {
                activityName = item.description.split(":")[0];
              } else if (item.name) {
                activityName = item.name;
              }
              dayActivityNames[dayNum].push(activityName);
            }
          }
        }
      });
      
      console.log(`Day ${dayNum}: ${dayCoords[dayNum].length} activities`);
    });
    
    return true;
  } catch (error) {
    console.error("Error parsing itinerary:", error);
    alert("Lỗi khi đọc dữ liệu lịch trình.");
    return false;
  }
}

// Update day navigation UI
function updateDayNavigation() {
  document.getElementById('currentDayLabel').textContent = `Ngày ${currentDay}`;
  document.getElementById('dayCounter').textContent = `${currentDay} / ${totalDays}`;
  document.getElementById('current-day-info').textContent = `Ngày ${currentDay}`;
  
  // Update navigation buttons
  document.getElementById('prevDayBtn').disabled = (currentDay <= 1);
  document.getElementById('nextDayBtn').disabled = (currentDay >= totalDays);
  
  // Update day summary
  const currentDayData = itineraryData.days.find(d => d.day === currentDay) || itineraryData.days[currentDay - 1];
  if (currentDayData) {
    const activitiesCount = dayCoords[currentDay] ? dayCoords[currentDay].length : 0;
    document.getElementById('activitiesCount').textContent = activitiesCount;
    
    const cost = Number(currentDayData.estimated_cost) || 0;
    document.getElementById('dayCost').textContent = cost.toLocaleString('vi-VN') + ' VND';
  }
}

// Load and display route for current day
function loadDayRoute() {
  console.log(`Loading route for day ${currentDay}`);
  
  const coords = dayCoords[currentDay];
  const activityNames = dayActivityNames[currentDay];
  
  if (!coords || coords.length < 2) {
    showModal(`Ngày ${currentDay} không có đủ điểm để tạo lộ trình (cần ít nhất 2 điểm).`);
    document.getElementById('day-stops').textContent = coords ? coords.length : 0;
    document.getElementById('day-distance').textContent = "N/A";
    document.getElementById('day-duration').textContent = "N/A";
    return;
  }
  
  // Clear existing markers and routes
  if (directionsRenderer) {
    directionsRenderer.setMap(null);
  }
  
  // Create new directions renderer
  directionsRenderer = new google.maps.DirectionsRenderer({ 
    suppressMarkers: true,
    polylineOptions: {
      strokeColor: '#4285F4',
      strokeWeight: 5
    }
  });
  directionsRenderer.setMap(map);
  
  // Add markers for current day
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
      sharedInfoWindow.setContent(`<div><strong>Ngày ${currentDay} - Điểm ${i + 1}</strong><br>${activityNames[i] || ''}</div>`);
      sharedInfoWindow.open(map, marker);
    });
  });
  
  // Update stops count
  document.getElementById('day-stops').textContent = coords.length;
  
  // Calculate route
  calcDayRoute(coords);
}

// Check if coordinates are over water/sea
function checkIfOverWater(coords, callback) {
  const geocoder = new google.maps.Geocoder();
  let waterPoints = [];
  let checkedCount = 0;
  
  coords.forEach((coord, index) => {
    geocoder.geocode({ location: coord }, (results, status) => {
      checkedCount++;
      
      if (status === 'OK' && results[0]) {
        const types = results[0].types;
        const addressComponents = results[0].address_components;
        
        // Check if point is over water
        const isOverWater = types.includes('natural_feature') || 
                           types.includes('establishment') ||
                           addressComponents.some(component => 
                             component.types.includes('natural_feature') &&
                             (component.long_name.toLowerCase().includes('sea') ||
                              component.long_name.toLowerCase().includes('ocean') ||
                              component.long_name.toLowerCase().includes('bay') ||
                              component.long_name.toLowerCase().includes('biển'))
                           );
        
        if (isOverWater) {
          waterPoints.push({
            index: index,
            coord: coord,
            name: results[0].formatted_address
          });
        }
      }
      
      // When all points are checked
      if (checkedCount === coords.length) {
        callback(waterPoints);
      }
    });
  });
}

// Optimize route for mixed land/water destinations
function optimizeRouteForWaterPoints(coords, waterPoints) {
  if (waterPoints.length === 0) {
    return coords; // No water points, return original
  }
  
  console.log("Water points detected:", waterPoints);
  
  // Group consecutive land points
  const segments = [];
  let currentSegment = [];
  
  coords.forEach((coord, index) => {
    const isWaterPoint = waterPoints.some(wp => wp.index === index);
    
    if (isWaterPoint) {
      // End current land segment if exists
      if (currentSegment.length > 0) {
        segments.push({ type: 'land', coords: [...currentSegment] });
        currentSegment = [];
      }
      // Add water point as separate segment
      segments.push({ type: 'water', coords: [coord] });
    } else {
      currentSegment.push(coord);
    }
  });
  
  // Add final land segment if exists
  if (currentSegment.length > 0) {
    segments.push({ type: 'land', coords: currentSegment });
  }
  
  return segments;
}

// Get detailed water point information
function getWaterPointDetails(waterPoints) {
  const waterTypes = waterPoints.map(wp => {
    const name = wp.name.toLowerCase();
    if (name.includes('sea') || name.includes('biển')) return 'biển';
    if (name.includes('ocean') || name.includes('đại dương')) return 'đại dương';
    if (name.includes('bay') || name.includes('vịnh')) return 'vịnh';
    if (name.includes('island') || name.includes('đảo')) return 'đảo';
    return 'vùng nước';
  });
  
  const uniqueTypes = [...new Set(waterTypes)];
  return uniqueTypes.join(', ');
}

// Calculate route for current day
function calcDayRoute(coords) {
  if (coords.length < 2) {
    console.error("Not enough coordinates to calculate route");
    return;
  }
  
  console.log("Calculating route with coordinates:", coords);
  
  // First, check if any points are over water
  checkIfOverWater(coords, (waterPoints) => {
    if (waterPoints.length > 0) {
      console.log(`Found ${waterPoints.length} water points, using optimized routing`);
      calculateMixedRoute(coords, waterPoints);
    } else {
      calculateStandardRoute(coords);
    }
  });
}

// Calculate mixed route (land + water segments)
function calculateMixedRoute(coords, waterPoints) {
  console.log("Calculating mixed route with all points connected");
  
  // Instead of complex segmentation, create a simple approach that connects all points
  let totalRouteCoords = [];
  let processedSegments = 0;
  const totalSegments = coords.length - 1;
  
  // Process each pair of consecutive points
  function processSegmentPair(index) {
    if (index >= coords.length - 1) {
      // All segments processed
      routeCoords = totalRouteCoords;
      dayRoutes[currentDay] = [...routeCoords];
      
      // Calculate total distance
      totalDistance = 0;
      for (let i = 0; i < coords.length - 1; i++) {
        totalDistance += calculateDistance(coords[i], coords[i + 1]) * 1000;
      }
      
      // Update UI
      document.getElementById('day-distance').textContent = 
        `🌊 ${(totalDistance / 1000).toFixed(1)} km (hỗn hợp)`;
      
      totalDuration = (totalDistance / 1000) * 72; // Estimate
      document.getElementById('day-duration').textContent = 
        `~${formatDuration(totalDuration)} (ước tính)`;
      
      // Center map
      const bounds = new google.maps.LatLngBounds();
      coords.forEach(coord => bounds.extend(coord));
      map.fitBounds(bounds);
      
      // Enhanced message
      const waterCount = waterPoints.length;
      const waterDetails = getWaterPointDetails(waterPoints);
      const message = `🌊 Đã tạo tuyến đường kết nối ${coords.length} điểm cho ngày ${currentDay}. 
      
📍 Bao gồm ${waterCount} điểm trên ${waterDetails}.
      
💡 Các đoạn màu đỏ đứt nét cần di chuyển bằng tàu thủy hoặc máy bay.`;
      
      showModal(message);
      return;
    }
    
    const start = coords[index];
    const end = coords[index + 1];
    
    // Check if either point is a water point
    const startIsWater = waterPoints.some(wp => wp.index === index);
    const endIsWater = waterPoints.some(wp => wp.index === index + 1);
    
    if (startIsWater || endIsWater) {
      // Use straight line for water connections
      addStraightLineSegment(start, end, totalRouteCoords);
      processSegmentPair(index + 1);
    } else {
      // Try to calculate driving route for land connections
      directionsService.route({
        origin: start,
        destination: end,
        travelMode: google.maps.TravelMode.DRIVING
      }, (response, status) => {
        if (status === 'OK') {
          // Add driving route
          response.routes[0].legs.forEach(leg => {
            leg.steps.forEach(step => {
              step.path.forEach(p => totalRouteCoords.push(p));
            });
          });
        } else {
          // Fallback to straight line
          addStraightLineSegment(start, end, totalRouteCoords);
        }
        processSegmentPair(index + 1);
      });
    }
  }
  
  // Draw comprehensive route visualization
  drawComprehensiveRouteVisualization(coords, waterPoints);
  
  // Start processing segments
  processSegmentPair(0);
}

// Draw comprehensive route visualization that connects all points
function drawComprehensiveRouteVisualization(coords, waterPoints) {
  // Clear existing route
  if (directionsRenderer) {
    directionsRenderer.setMap(null);
  }
  
  // Create connections between all consecutive points
  for (let i = 0; i < coords.length - 1; i++) {
    const start = coords[i];
    const end = coords[i + 1];
    
    // Check if either point is a water point
    const startIsWater = waterPoints.some(wp => wp.index === i);
    const endIsWater = waterPoints.some(wp => wp.index === i + 1);
    
    // Determine line style based on connection type
    let color, strokeWeight, strokePattern, icons;
    
    if (startIsWater || endIsWater) {
      // Water connection - red dashed line
      color = '#FF6B6B';
      strokeWeight = 4;
      strokePattern = [10, 5];
      icons = [{
        icon: {
          path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
          scale: 3,
          strokeColor: color
        },
        offset: '100%',
        repeat: '40px'
      }];
    } else {
      // Land connection - blue solid line
      color = '#4285F4';
      strokeWeight = 5;
      strokePattern = null;
      icons = [{
        icon: {
          path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
          scale: 2,
          strokeColor: color
        },
        offset: '100%',
        repeat: '60px'
      }];
    }
    
    const polyline = new google.maps.Polyline({
      path: [start, end],
      geodesic: true,
      strokeColor: color,
      strokeOpacity: 1.0,
      strokeWeight: strokeWeight,
      strokeDashArray: strokePattern,
      icons: icons
    });
    
    polyline.setMap(map);
  }
}

// Add straight line segment between two points
function addStraightLineSegment(start, end, targetArray) {
  const steps = 10;
  for (let j = 0; j <= steps; j++) {
    const lat = start.lat + (end.lat - start.lat) * (j / steps);
    const lng = start.lng + (end.lng - start.lng) * (j / steps);
    targetArray.push(new google.maps.LatLng(lat, lng));
  }
}

// Calculate standard route (original logic)
function calculateStandardRoute(coords) {
  console.log("Calculating standard route for all points");
  
  // First try the complete route with all waypoints
  const waypoints = coords.slice(1, coords.length - 1).map(loc => ({ location: loc, stopover: true }));
  
  // Try different travel modes in order of preference
  const travelModes = [
    google.maps.TravelMode.DRIVING,
    google.maps.TravelMode.TRANSIT,
    google.maps.TravelMode.WALKING
  ];
  
  let currentModeIndex = 0;
  
  function tryCalculateRoute(modeIndex = 0) {
    if (modeIndex >= travelModes.length) {
      // If all travel modes fail, create point-to-point connections
      console.log("All travel modes failed, creating point-to-point connections");
      createPointToPointRoute(coords);
      return;
    }
    
    const travelMode = travelModes[modeIndex];
    console.log(`Trying travel mode: ${travelMode}`);
    
    directionsService.route({
      origin: coords[0],
      destination: coords[coords.length - 1],
      waypoints: waypoints,
      travelMode: travelMode,
      avoidHighways: false,
      avoidTolls: false
    }, (response, status) => {
      console.log(`Direction service response status for ${travelMode}:`, status);
      
      if (status === 'OK') {
        directionsRenderer.setDirections(response);
        
        // Store route for current day
        routeCoords = [];
        totalDistance = 0;
        totalDuration = 0;
        
        // Calculate total distance and duration
        response.routes[0].legs.forEach(leg => {
          totalDistance += leg.distance.value;
          totalDuration += leg.duration.value;
          
          leg.steps.forEach(step => {
            step.path.forEach(p => routeCoords.push(p));
          });
        });
        
        // Store route for this day
        dayRoutes[currentDay] = [...routeCoords];
        
        // Update day info with travel mode indicator
        const modeText = travelMode === google.maps.TravelMode.DRIVING ? "🚗" : 
                        travelMode === google.maps.TravelMode.TRANSIT ? "🚌" : "🚶";
        
        document.getElementById('day-distance').textContent = 
          `${modeText} ${(totalDistance / 1000).toFixed(1)} km`;
        
        document.getElementById('day-duration').textContent = 
          formatDuration(totalDuration);
        
        // Center map on route
        if (coords.length > 0) {
          map.setCenter(coords[0]);
        }
        
        // Show success message for non-driving modes
        if (travelMode !== google.maps.TravelMode.DRIVING) {
          showModal(`Đã tìm thấy tuyến đường bằng ${modeText === "🚌" ? "phương tiện công cộng" : "đi bộ"} cho ngày ${currentDay}`);
        }
        
      } else {
        console.error(`Could not calculate route with ${travelMode}:`, status);
        
        // Handle specific error cases
        if (waypoints.length > 8 && status === 'MAX_WAYPOINTS_EXCEEDED') {
          console.log("Too many waypoints, trying with fewer points...");
          const reducedCoords = reduceWaypoints(coords, 8);
          calcDayRoute(reducedCoords);
          return;
        }
        
        // Try next travel mode
        tryCalculateRoute(modeIndex + 1);
      }
    });
  }
  
  // Start with the first travel mode
  tryCalculateRoute(0);
}

// Create point-to-point route when standard routing fails
function createPointToPointRoute(coords) {
  console.log("Creating point-to-point route for all coordinates");
  
  // Clear existing route
  if (directionsRenderer) {
    directionsRenderer.setMap(null);
  }
  
  let totalRouteCoords = [];
  let processedConnections = 0;
  const totalConnections = coords.length - 1;
  
  // Process each pair of consecutive points
  function processConnection(index) {
    if (index >= coords.length - 1) {
      // All connections processed
      routeCoords = totalRouteCoords;
      dayRoutes[currentDay] = [...routeCoords];
      
      // Calculate total distance
      totalDistance = 0;
      for (let i = 0; i < coords.length - 1; i++) {
        totalDistance += calculateDistance(coords[i], coords[i + 1]) * 1000;
      }
      
      // Update UI
      document.getElementById('day-distance').textContent = 
        `🔗 ${(totalDistance / 1000).toFixed(1)} km (kết nối trực tiếp)`;
      
      totalDuration = (totalDistance / 1000) * 72; // Estimate
      document.getElementById('day-duration').textContent = 
        `~${formatDuration(totalDuration)} (ước tính)`;
      
      // Center map
      const bounds = new google.maps.LatLngBounds();
      coords.forEach(coord => bounds.extend(coord));
      map.fitBounds(bounds);
      
      showModal(`🔗 Đã tạo kết nối trực tiếp giữa ${coords.length} điểm cho ngày ${currentDay}. Một số đoạn có thể cần phương tiện đặc biệt.`);
      return;
    }
    
    const start = coords[index];
    const end = coords[index + 1];
    
    // Try to get driving directions for this segment
    directionsService.route({
      origin: start,
      destination: end,
      travelMode: google.maps.TravelMode.DRIVING
    }, (response, status) => {
      if (status === 'OK') {
        // Add driving route for this segment
        response.routes[0].legs.forEach(leg => {
          leg.steps.forEach(step => {
            step.path.forEach(p => totalRouteCoords.push(p));
          });
        });
      } else {
        // Fallback to straight line for this segment
        addStraightLineSegment(start, end, totalRouteCoords);
      }
      processConnection(index + 1);
    });
  }
  
  // Draw visual connections between all points
  drawAllPointConnections(coords);
  
  // Start processing connections
  processConnection(0);
}

// Draw visual connections between all consecutive points
function drawAllPointConnections(coords) {
  // Create connections between all consecutive points
  for (let i = 0; i < coords.length - 1; i++) {
    const start = coords[i];
    const end = coords[i + 1];
    
    const polyline = new google.maps.Polyline({
      path: [start, end],
      geodesic: true,
      strokeColor: '#FF9800',
      strokeOpacity: 0.8,
      strokeWeight: 4,
      strokeDashArray: [5, 5],
      icons: [{
        icon: {
          path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
          scale: 2,
          strokeColor: '#FF9800'
        },
        offset: '100%',
        repeat: '50px'
      }]
    });
    
    polyline.setMap(map);
  }
}

// Navigate to previous day
function goToPreviousDay() {
  if (currentDay > 1) {
    currentDay--;
    updateDayNavigation();
    loadDayRoute();
    resetAnimation();
  }
}

// Navigate to next day
function goToNextDay() {
  if (currentDay < totalDays) {
    currentDay++;
    updateDayNavigation();
    loadDayRoute();
    resetAnimation();
  }
}

// Reset animation state
function resetAnimation() {
  if (animationTimeout) clearTimeout(animationTimeout);
  if (carMarker) {
    carMarker.setMap(null);
    carMarker = null;
  }
  stepIndex = 0;
  animationInProgress = false;
  document.getElementById("day-progress").textContent = "0%";
  updateTotalProgress();
  
  // Update button states
  document.getElementById("start-trip-btn").classList.remove("hidden");
  document.getElementById("start-trip-btn").classList.add("visible");
  document.getElementById("reset-trip-btn").classList.remove("visible");
  document.getElementById("reset-trip-btn").classList.add("hidden");
}

// Update total progress across all days
function updateTotalProgress() {
  let completedDays = currentDay - 1;
  let currentDayProgress = 0;
  
  if (routeCoords.length > 0) {
    currentDayProgress = stepIndex / routeCoords.length;
  }
  
  const totalProgress = ((completedDays + currentDayProgress) / totalDays) * 100;
  document.getElementById('total-progress').textContent = Math.floor(totalProgress) + '%';
}

// Start auto-play mode
function startAutoPlay() {
  autoPlayMode = true;
  currentDay = 1;
  updateDayNavigation();
  loadDayRoute();
  
  // Wait for route to load then start animation
  setTimeout(() => {
    if (routeCoords.length > 0) {
      startAnimation();
    }
  }, 1000);
  
  // Update button states
  document.getElementById("start-trip-btn").classList.remove("visible");
  document.getElementById("start-trip-btn").classList.add("hidden");
  document.getElementById("auto-play-btn").classList.remove("hidden");
  document.getElementById("auto-play-btn").classList.add("visible");
}

// Stop auto-play mode
function stopAutoPlay() {
  autoPlayMode = false;
  if (autoPlayTimeout) {
    clearTimeout(autoPlayTimeout);
    autoPlayTimeout = null;
  }
  resetAnimation();
  
  document.getElementById("auto-play-btn").classList.remove("visible");
  document.getElementById("auto-play-btn").classList.add("hidden");
}