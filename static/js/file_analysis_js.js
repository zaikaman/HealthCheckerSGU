document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('input[type="file"]');
    const submitButton = document.querySelector('button[type="submit"]');
    const form = document.querySelector('form');
    const previewContainer = document.createElement('div');
    previewContainer.className = 'preview-container mt-3';

    // File validation and preview
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Validate file
            if (!validateFile(file)) {
                fileInput.value = '';
                return;
            }
            
            // Show preview
            showFilePreview(file, previewContainer);
            
            // Add preview container after file input
            if (!document.querySelector('.preview-container')) {
                fileInput.parentElement.appendChild(previewContainer);
            }
        }
    });

    // Form submission
    form.addEventListener('submit', function(e) {
        if (!fileInput.value) {
            e.preventDefault();
            showAlert('Vui lòng chọn file để phân tích', 'warning');
            return;
        }
        
        showLoadingState(submitButton);
    });

    // Initialize results animation if present
    initializeResults();
});

// File validation
function validateFile(file) {
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    const maxSize = 5 * 1024 * 1024; // 5MB

    if (!validTypes.includes(file.type)) {
        showAlert('Vui lòng chọn file hình ảnh (JPG, JPEG hoặc PNG)', 'error');
        return false;
    }

    if (file.size > maxSize) {
        showAlert('File không được vượt quá 5MB', 'error');
        return false;
    }

    return true;
}

// Show file preview
function showFilePreview(file, container) {
    const reader = new FileReader();
    reader.onload = function(e) {
        container.innerHTML = `
            <img src="${e.target.result}" class="img-preview img-fluid rounded" 
                 style="max-height: 200px; margin-top: 10px;">
        `;
    };
    reader.readAsDataURL(file);
}

// Show loading state
function showLoadingState(button) {
    button.disabled = true;
    button.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        <span class="ms-2">Đang phân tích...</span>
    `;
}

// Show alert message
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show mt-3`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.querySelector('.container').insertBefore(
        alertDiv,
        document.querySelector('form')
    );

    setTimeout(() => alertDiv.remove(), 5000);
}

// Initialize results
function initializeResults() {
    const resultContainer = document.querySelector('.result-container');
    if (resultContainer) {
        setTimeout(() => {
            resultContainer.classList.add('visible');
        }, 100);
    }
}
