document.addEventListener('DOMContentLoaded', function() {
  const fileInput = document.getElementById('fileInput');
  const uploadLocal = document.getElementById('uploadLocal');
  const captureCamera = document.getElementById('captureCamera');
  const imagePreview = document.getElementById('imagePreview');
  const scanButton = document.getElementById('scanButton');
  const dashboardButton = document.getElementById('dashboardButton');
  
  // Add subtle hover effects
  document.querySelectorAll('select, button, .upload-option').forEach(element => {
    element.addEventListener('mouseover', () => {
      element.style.transition = 'all 0.3s ease';
    });
  });
  
  // Upload from device
  uploadLocal.addEventListener('click', function() {
    fileInput.click();
  });
  
  fileInput.addEventListener('change', function(e) {
    if (e.target.files && e.target.files[0]) {
      const reader = new FileReader();
      
      // Show loading indicator
      imagePreview.innerHTML = `
        <div style="text-align: center;">
          <div class="loading"><div></div><div></div></div>
          <p style="margin-top: 10px;">Loading image...</p>
        </div>
      `;
      
      reader.onload = function(e) {
        setTimeout(() => {
          imagePreview.innerHTML = `<img src="${e.target.result}" style="max-width: 100%; max-height: 100%; border-radius: 8px;">`;
          imagePreview.style.border = 'none';
          
          // Add subtle fade-in effect
          const img = imagePreview.querySelector('img');
          img.style.opacity = '0';
          img.style.transition = 'opacity 0.5s ease';
          setTimeout(() => { img.style.opacity = '1'; }, 50);
        }, 500); // Simulate loading time
      }
      
      reader.readAsDataURL(e.target.files[0]);
    }
  });
  
  // Capture with camera
  captureCamera.addEventListener('click', function() {
    this.classList.add('active');
    setTimeout(() => this.classList.remove('active'), 300);
    
    Swal ? Swal.fire({
      title: 'Camera Access',
      text: 'In the full app, this would access your camera for a live scan.',
      icon: 'info',
      confirmButtonColor: '#9c27b0'
    }) : alert('Camera functionality would be implemented here in a real application.');
    
    imagePreview.innerHTML = `
      <div style="text-align: center;">
        <div class="loading"><div></div><div></div></div>
        <p style="margin-top: 10px;">Accessing camera...</p>
      </div>
    `;
    
    setTimeout(() => {
      imagePreview.innerHTML = `<img src="/api/placeholder/400/320" alt="Camera placeholder" style="max-width: 100%; max-height: 100%; border-radius: 8px;">`;
      imagePreview.style.border = 'none';
    }, 1000);
  });
  
  // Scan button
  scanButton.addEventListener('click', function(e) {
    e.preventDefault(); // Prevent any default form submission
    const bodyPart = document.getElementById('bodyPart').value;
    
    if (!bodyPart) {
      const select = document.getElementById('bodyPart');
      select.style.borderColor = 'var(--error)';
      select.style.animation = 'shake 0.5s ease';
      setTimeout(() => {
        select.style.borderColor = '';
        select.style.animation = '';
      }, 500);
      
      Swal ? Swal.fire({
        title: 'Missing Selection',
        text: 'Please select a body part first.',
        icon: 'warning',
        confirmButtonColor: '#9c27b0'
      }) : alert('Please select a body part first.');
      return;
    }
    
    if (imagePreview.querySelector('img')) {
      scanButton.disabled = true;
      scanButton.innerHTML = `
        <div class="loading"><div></div><div></div></div>
        <span>Analyzing...</span>
      `;
      
      const img = imagePreview.querySelector('img');
      img.style.filter = 'brightness(1.2) saturate(1.2)';
      
      const scanLine = document.createElement('div');
      scanLine.style.position = 'absolute';
      scanLine.style.left = '0';
      scanLine.style.top = '0';
      scanLine.style.width = '100%';
      scanLine.style.height = '2px';
      scanLine.style.backgroundColor = 'var(--primary)';
      scanLine.style.boxShadow = '0 0 10px 2px var(--primary)';
      scanLine.style.animation = 'scanMove 2s linear';
      scanLine.style.zIndex = '1';
      imagePreview.style.position = 'relative';
      imagePreview.appendChild(scanLine);
      
      const style = document.createElement('style');
      style.innerHTML = `
        @keyframes scanMove {
          0% { top: 0; }
          100% { top: 100%; }
        }
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          75% { transform: translateX(5px); }
        }
      `;
      document.head.appendChild(style);
      
      // Simulate scanning process
      setTimeout(function() {
        scanButton.disabled = false;
        scanButton.innerHTML = `
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M7 3H5a2 2 0 00-2 2v2m0 10v2a2 2 0 002 2h2m10 0h2a2 2 0 002-2v-2m0-10V5a2 2 0 00-2-2h-2M9 12a3 3 0 106 0 3 3 0 00-6 0z"/>
          </svg>
          Scan Image
        `;
        
        img.style.filter = '';
        if (scanLine.parentNode) {
          scanLine.parentNode.removeChild(scanLine);
        }
        
        // Instead of just showing an alert, submit the form to invoke get_skin_diagnosis
        document.getElementById('skinScanForm').submit();
      }, 2000);
    } else {
      Swal ? Swal.fire({
        title: 'No Image',
        text: 'Please upload or capture an image first.',
        icon: 'error',
        confirmButtonColor: '#9c27b0'
      }) : alert('Please upload or capture an image first.');
    }
  });
  
  // Dashboard button
  dashboardButton.addEventListener('click', function() {
    window.location.href = '/dashboard/';
    this.style.transform = 'scale(0.95)';
    setTimeout(() => this.style.transform = '', 150);
    
    Swal ? Swal.fire({
      title: 'Redirecting',
      text: 'Taking you to your personalized dashboard...',
      icon: 'info',
      timer: 1500,
      timerProgressBar: true,
      showConfirmButton: false,
      willOpen: () => { Swal.showLoading(); }
    }) : alert('Redirecting to dashboard...');
  });
});
