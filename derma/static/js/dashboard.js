// Toggle sidebar
const menuToggle = document.getElementById('menu-toggle');
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('main-content');

menuToggle.addEventListener('click', () => {
    sidebar.classList.toggle('active');
    mainContent.classList.toggle('sidebar-active');
});

// Toggle user dropdown
const userProfile = document.getElementById('user-profile');
const userDropdown = document.getElementById('user-dropdown');

userProfile.addEventListener('click', (e) => {
    e.stopPropagation();
    userDropdown.classList.toggle('active');
});

// Close dropdown when clicking outside
document.addEventListener('click', () => {
    if (userDropdown.classList.contains('active')) {
        userDropdown.classList.remove('active');
    }
});

// Prevent dropdown from closing when clicked on directly
userDropdown.addEventListener('click', (e) => {
    e.stopPropagation();
});

// Navigation
const navLinks = document.querySelectorAll('.sidebar-link');

navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        // e.preventDefault();
        
        // Remove active class from all links
        navLinks.forEach(navLink => {
            navLink.classList.remove('active');
        });
        
        // Add active class to clicked link
        this.classList.add('active');
        
        // On mobile, close sidebar after navigation
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('active');
            mainContent.classList.remove('sidebar-active');
        }
        
        // Here you would normally navigate to the page
        // For this demo, we'll just show an alert
        const pageName = this.textContent.trim();
        // if (pageName !== 'Dashboard') {
        //     alert(`Navigating to ${pageName} page`);
        // }
    });
});