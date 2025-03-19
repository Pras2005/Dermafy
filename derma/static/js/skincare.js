document.addEventListener('DOMContentLoaded', function() {
    const reportForm = document.getElementById('reportForm');
    const routineSection = document.getElementById('routineSection');
    const reportSection = document.getElementById('reportSection');
    const loadingSpinner = document.getElementById('loading-spinner');
    const contentWrapper = document.getElementById('content-wrapper');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const dashboardLink = document.getElementById('dashboardLink');
    
    // Handle form submission
    reportForm.addEventListener('submit', function(e) {
        // Prevent default form submission
        e.preventDefault();
        
        // Hide routine section and show report section
        routineSection.style.display = 'none';
        reportSection.style.display = 'block';
        
        // Show loading spinner
        loadingSpinner.style.display = 'flex';
        contentWrapper.style.display = 'none';
        
        // Hide the report form and show the dashboard button
        reportForm.style.display = 'none';
        dashboardLink.style.display = 'inline-block';
        
        // Create FormData object
        const formData = new FormData(reportForm);
        
        // Use XMLHttpRequest instead of fetch for better compatibility
        const xhr = new XMLHttpRequest();
        xhr.open('POST', reportForm.action, true);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 400) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    
                    // Hide loading spinner and show content
                    loadingSpinner.style.display = 'none';
                    contentWrapper.style.display = 'block';
                    
                    // Update content with data
                    document.getElementById('routine-steps').innerHTML = data.routine || 'No routine data available';
                    document.getElementById('product-recommendations').innerHTML = data.products || 'No product recommendations available';
                    document.getElementById('key-ingredients').innerHTML = data.ingredients || 'No ingredient data available';
                    document.getElementById('ai-insight-content').innerHTML = data.analysis || 'Analysis not available';
                } catch (error) {
                    console.error('Error parsing JSON:', error);
                    
                    // Handle HTML response (non-JSON)
                    if (xhr.responseText.includes('<!DOCTYPE html>')) {
                        // If we got HTML back, show report section with iframe
                        loadingSpinner.style.display = 'none';
                        contentWrapper.style.display = 'block';
                        contentWrapper.innerHTML = '<iframe id="report-iframe" style="width:100%;height:600px;border:none;" srcdoc="' + xhr.responseText.replace(/"/g, '&quot;') + '"></iframe>';
                    } else {
                        // Show error message
                        handleError('Invalid response format');
                    }
                }
            } else {
                handleError('Server error: ' + xhr.status);
            }
        };
        
        xhr.onerror = function() {
            handleError('Network error');
        };
        
        xhr.send(formData);
        
        function handleError(message) {
            console.error('Error:', message);
            loadingSpinner.style.display = 'none';
            contentWrapper.style.display = 'block';
            contentWrapper.innerHTML = '<p class="error">Error generating report. Please try again later.</p><p class="error-details">' + message + '</p>';
        }
    });
    
    // Tab functionality
    tabBtns.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            tabBtns.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            
            // Get the tab to show
            const tabId = this.getAttribute('data-tab');
            
            // Hide all tab panes
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // Show the selected tab pane
            document.getElementById(tabId).classList.add('active');
        });
    });
});