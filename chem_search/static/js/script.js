// Script for Chemical Element Search Website

document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('elementSearchForm');
    const resultsContainer = document.querySelector('.results-container');
    const loadingSpinner = document.createElement('div');
    loadingSpinner.className = 'spinner';
    loadingSpinner.style.display = 'none';
    
    // Insert spinner after the form
    const searchContainer = document.querySelector('.search-container');
    searchContainer.appendChild(loadingSpinner);
    
    // Form validation and submission handling
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            const input = document.getElementById('element_symbol').value.trim();
            
            if (!input) {
                event.preventDefault();
                showMessage('error', 'Please enter an element symbol');
                return;
            }
            
            // Show loading spinner
            if (!resultsContainer || !resultsContainer.innerHTML.trim()) {
                loadingSpinner.style.display = 'block';
            }
        });
    }
    
    // Function to display messages
    function showMessage(type, text) {
        // Remove any existing messages
        const existingMessages = document.querySelectorAll('.error-message, .success-message');
        existingMessages.forEach(msg => msg.remove());
        
        // Create new message
        const message = document.createElement('div');
        message.className = type === 'error' ? 'error-message' : 'success-message';
        message.textContent = text;
        
        // Insert after input group
        const inputGroup = document.querySelector('.input-group');
        if (inputGroup) {
            inputGroup.parentNode.insertBefore(message, inputGroup.nextSibling);
            
            // Auto-hide message after 5 seconds
            setTimeout(() => {
                message.style.opacity = '0';
                message.style.transition = 'opacity 0.5s';
                setTimeout(() => message.remove(), 500);
            }, 5000);
        }
    }
});