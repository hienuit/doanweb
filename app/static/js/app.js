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

        // Additional JavaScript functionality can be added here
        // For example, animation on scroll, filter functionality, etc.
        
        // Example of smooth scrolling for all anchor links
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


// Login form submission
// $('#loginForm').submit(function (e) {
//     e.preventDefault();
//     var user = $('#user').val();
//     var password = $('#passwordLogin').val();
    
//     $.post('/login', { user: user, password: password }, function(response) {
//         if (response == '1') {
//             $('#noequalkey').show(); // Show error message
//         } else {
//             // Redirect or perform other actions on successful login
//             window.location.href = '/welcome/' + email;
//         }
//     });
// });


// const noEqualKeyt = document.getElementById("noequalkeyt");
// const registered = document.getElementById("registered");
// const registerSuccess = document.getElementById("registersuccess");

// document.getElementById("registerForm").addEventListener('submit', function (e) {
//     e.preventDefault();

//     // Lấy giá trị từ các input trong form
//     const fullName = document.getElementById("fullName").value;
//     const username = document.getElementById("username").value;
//     const password = document.getElementById("passwordRegister").value;
//     const confirmPassword = document.getElementById("confirmPassword").value;

//     console.log(fullName);
//     console.log(username);
//     console.log(password);
//     console.log(confirmPassword);

//     // Tạo payload gửi đi
//     const payload = {
//         fullName: fullName,
//         username: username,
//         passwordRegister: password,
//         confirmPassword: confirmPassword
//     };

//     // Gửi request POST sử dụng Fetch API
//     fetch('/register', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify(payload)
//     })
//     .then(response => response.text())
//     .then(response => {
//         // Kiểm tra các phản hồi và hiển thị thông báo tương ứng
//         if (response === '1') {
            
//             if (noEqualKeyt) {
//                 registered.style.display = 'none';
//                 registerSuccess.style.display = 'none';
//                 noEqualKeyt.style.display = 'block';
                
//             }
//         } else if (response === '2') {
           
//             if (registered) {
//                 noEqualKeyt.style.display = 'none';
//                 registerSuccess.style.display = 'none';
//                 registered.style.display = 'block';
//             }
//         } else if (response === '3') {
            
//             if (registerSuccess) {
//                 noEqualKeyt.style.display = 'none';
//                 registered.style.display = 'none';
//                 registerSuccess.style.display = 'block';
               
//             }
//         }
//     })
//     .catch(error => {
//         console.error('Error:', error);
//     });
// });


// Add this to your app.js file or create a new script
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