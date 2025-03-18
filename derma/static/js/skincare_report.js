document.addEventListener("DOMContentLoaded", () => {
    const loadingSpinner = document.getElementById('loading-spinner');
    const contentWrapper = document.getElementById('content-wrapper');

    // Simulate loading delay
    setTimeout(() => {
        loadingSpinner.style.display = 'none';
        contentWrapper.style.display = 'block';
    }, 2000);

    // Tab Switching Logic
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active states from other buttons and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));

            // Activate the selected tab
            button.classList.add('active');
            const target = document.getElementById(button.getAttribute('data-tab'));
            target.classList.add('active');
        });
    });
});
