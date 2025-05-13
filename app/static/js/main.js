// Main JavaScript file for PDF Quiz Generator

// Enable tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Add animation classes to elements when they come into view
function animateOnScroll() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;
        
        if (elementPosition < windowHeight - 50) {
            const animationClass = element.dataset.animation || 'animate__fadeIn';
            element.classList.add('animate__animated', animationClass);
        }
    });
}

// Listen for scroll events
window.addEventListener('scroll', animateOnScroll);
window.addEventListener('load', animateOnScroll);

// Handle file input styling
const fileInputs = document.querySelectorAll('input[type="file"]');
fileInputs.forEach(input => {
    input.addEventListener('change', function() {
        const fileName = this.files[0]?.name;
        const label = this.nextElementSibling;
        
        if (fileName) {
            label.textContent = fileName;
        } else {
            label.textContent = 'Choose a file or drag it here';
        }
    });
});

// Add drag and drop functionality for file uploads
const dropAreas = document.querySelectorAll('.custom-file-upload');
dropAreas.forEach(area => {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        area.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        area.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        area.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        area.classList.add('border-primary');
    }
    
    function unhighlight() {
        area.classList.remove('border-primary');
    }
    
    area.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        const fileInput = area.querySelector('input[type="file"]');
        
        if (fileInput && files.length > 0) {
            fileInput.files = files;
            
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(event);
        }
    }
});
