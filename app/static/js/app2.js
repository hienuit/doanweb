// Show destination options when mood is selected
document.getElementById("moodSelect").addEventListener("change", function () {
    document.getElementById("destinationContainer").classList.remove("hidden");
});

// Show 'Next' button when destination is selected
document.getElementById("destinationSelect").addEventListener("change", function () {
    document.getElementById("nextButtonElement").classList.remove("hidden");
});

// Show the next tab when 'Next' is clicked


function nextTab(currentTab){
    // Hide the current tab
    document.getElementById(currentTab).classList.add("hidden");

    // Show the next tab
    var nextTab = "Tab" + (parseInt(currentTab.replace('Tab', '')) + 1); // Get next tab id
    var nextTabElement = document.getElementById(nextTab);
    
    if (nextTabElement) {
        nextTabElement.classList.remove("hidden");
    }
}

// Handle button clicks for location types
document.getElementById("beachButton").addEventListener("click", function () {
    showSuggestedPlaces("beach");
});

document.getElementById("mountainButton").addEventListener("click", function () {
    showSuggestedPlaces("mountain");
});

document.getElementById("cityButton").addEventListener("click", function () {
    showSuggestedPlaces("city");
});


// Function to fetch suggested places based on location type
let selectedDestination = null; // Store the selected destination

function showSuggestedPlaces(locationType) {
    const mood = document.getElementById("moodSelect").value;
    const place = document.getElementById("destinationSelect").value;

    fetch(`http://127.0.0.1:5000/search?mood=${mood}&place=${place}&location=${locationType}`)
        .then(response => response.json())
        .then(data => {
            const placesList = document.getElementById("placesList");
            placesList.innerHTML = "";

            if (data.length === 0) {
                placesList.innerHTML = "<p>No places found.</p>";
                return;
            }

            data.forEach(destination => {
                let listItem = document.createElement("li");
                listItem.textContent = destination.name;

                // When a place is clicked, store the selected destination in localStorage
                listItem.addEventListener("click", function () {
                    selectedDestination = {
                        id: destination.id,
                        name: destination.name
                    };

                    console.log("You selected:", selectedDestination); // Debug log

                    // Store selected destination in localStorage
                    localStorage.setItem('selectedDestination', JSON.stringify(selectedDestination));

                    // Redirect to the destination details page
                    window.location.href='/page3';
                });

                placesList.appendChild(listItem);
            });

            document.getElementById("Places").classList.remove("hidden");
        })
        .catch(error => console.error("Error fetching data:", error));
}


document.addEventListener("DOMContentLoaded", function () {
    let scrollTopBtn = document.getElementById("scrollbutton");

    // Hiển thị nút khi cuộn xuống 100px
    window.onscroll = function () {
        if (document.body.scrollTop > 500 || document.documentElement.scrollTop > 500) {
            scrollTopBtn.style.display = "block";
        } else {
            scrollTopBtn.style.display = "none";
        }
    };

    // Cuộn lên đầu khi bấm nút
    scrollTopBtn.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
});



// if (!province || !num_days) {
//     alert("Vui lòng nhập đầy đủ thông tin.");
//     return;
// }

// // Gửi AJAX request tới Flask server
// fetch('/create-itinerary', {
//     method: 'POST',
//     headers: {
//         'Content-Type': 'application/json'
//     },
//     body: JSON.stringify({ province: province, num_days: num_days })
// })
// .then(response => response.json())
// .then(data => {
//     // Hiển thị kết quả từ server
//     if (data.success) {
//         document.getElementById('result-container').style.display = 'block';
//         document.getElementById('itinerary-content').innerText = data.itinerary;
//     } else {
//         alert('Đã có lỗi xảy ra. Vui lòng thử lại.');
//     }
// })
// .catch(error => {
//     alert('Lỗi kết nối đến server.');
//     console.error('Error:', error);
// });
