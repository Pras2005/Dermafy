document.addEventListener("DOMContentLoaded", function () {
    let isLoggedIn = localStorage.getItem("loggedIn"); 
    let loginBtn = document.getElementById("login-btn");
    let userIcon = document.getElementById("user-icon");

    if (isLoggedIn === "true") {
        loginBtn.classList.add("hidden");
        userIcon.classList.remove("hidden");
    }

    function logInUser() {
        localStorage.setItem("loggedIn", "true");
        loginBtn.classList.add("hidden");
        userIcon.classList.remove("hidden");
    }

    function logOutUser() {
        localStorage.removeItem("loggedIn");
        loginBtn.classList.remove("hidden");
        userIcon.classList.add("hidden");
    }
});

document.addEventListener("DOMContentLoaded", function () {
    fetch("/get-user-data/")
        .then(response => response.json())
        .then(data => {
            if (data.username) {
                document.getElementById("login-tab").style.display = "none";
                document.getElementById("user-icon").classList.remove("hidden");
                document.getElementById("username-display").textContent = data.username;
            }
        });

    document.getElementById("user-icon").addEventListener("click", function (event) {
        event.stopPropagation();
        let dropdown = document.getElementById("profile-dropdown");
        dropdown.classList.toggle("hidden");
    });

    document.addEventListener("click", function (event) {
        let dropdown = document.getElementById("profile-dropdown");
        if (!event.target.closest("#user-icon")) {
            dropdown.classList.add("hidden");
        }
    });
    
    document.getElementById("logout-btn").addEventListener("click", function (event) {
        event.preventDefault();
        fetch("/logout/")
            .then(() => {
                window.location.reload();
            });
    });
    function playVideo() {
        // Hide Play Button
        document.getElementById("playButton").style.display = "none";
    
        // Show Video Container
        document.getElementById("videoContainer").style.display = "block";
    
        // Set Video Source and Auto-Play
        document.getElementById("videoFrame").src = "dermatologist_tips.mp4";
    }
});

document.addEventListener("DOMContentLoaded", function() {
    // Check if user has moved past landing page
    const hasVisitedLanding = localStorage.getItem('hasVisitedLanding');

    // If this is the landing page, mark that user has visited it
    if (window.location.pathname.includes('landing'),  
        window.location.pathname === '/'  ,
        window.location.pathname === '/index.html') {
        localStorage.setItem('hasVisitedLanding', 'true');
    } 
    // For any other page, check if they've visited landing and load consult
    else if (hasVisitedLanding === 'true') {
        loadConsultScript();
    }

    function loadConsultScript() {
        console.log("Loading consult script...");
        // Create script element
        var script = document.createElement("script");
        script.src = "{% static 'js/consult.js' %}";
        script.async = true;
        script.defer = true;

        // Append to document head
        if (document.head) {
            document.head.appendChild(script);
            console.log("Consult script loaded successfully!");
        } else {
            console.error("document.head is not found!");
        }
    }
});