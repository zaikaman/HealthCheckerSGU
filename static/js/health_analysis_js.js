// Document ready handler
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('input[type="file"]');
    const submitButton = document.querySelector('button[type="submit"]');
    const form = document.querySelector('form');

    // File validation
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Validate file type
            const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
            if (!validTypes.includes(file.type)) {
                alert('Vui lòng chọn file hình ảnh (JPG, JPEG hoặc PNG)');
                fileInput.value = '';
                return;
            }

            // Validate file size (max 5MB)
            const maxSize = 5 * 1024 * 1024;
            if (file.size > maxSize) {
                alert('File không được vượt quá 5MB');
                fileInput.value = '';
                return;
            }

            // Preview image
            previewImage(file);
        }
    });

    // Form submission handler
    form.addEventListener('submit', function(e) {
        if (!fileInput.value) {
            e.preventDefault();
            alert('Vui lòng chọn hình ảnh để phân tích');
            return;
        }
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Đang phân tích...';
    });
});

// Image preview function
function previewImage(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.createElement('img');
        preview.src = e.target.result;
        preview.className = 'img-preview img-fluid mb-3';
        preview.style.maxHeight = '300px';
        
        const previewContainer = document.querySelector('.preview-container');
        if (previewContainer) {
            previewContainer.innerHTML = '';
            previewContainer.appendChild(preview);
        } else {
            const newPreviewContainer = document.createElement('div');
            newPreviewContainer.className = 'preview-container text-center';
            newPreviewContainer.appendChild(preview);
            document.querySelector('.mb-3').appendChild(newPreviewContainer);
        }
    };
    reader.readAsDataURL(file);
}

// Result animation
function animateResults() {
    const resultContainer = document.querySelector('.result-container');
    if (resultContainer) {
        resultContainer.style.opacity = '0';
        resultContainer.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            resultContainer.style.transition = 'all 0.5s ease';
            resultContainer.style.opacity = '1';
            resultContainer.style.transform = 'translateY(0)';
        }, 100);
    }
}

// Initialize result animation if results exist
if (document.querySelector('.result-container')) {
    animateResults();
}
