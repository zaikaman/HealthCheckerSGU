// File Upload Preview
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('input[type="file"]');
    const submitButton = document.querySelector('button[type="submit"]');
    const form = document.querySelector('form');

    // Validate file input
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Check file type
            const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
            if (!validTypes.includes(file.type)) {
                alert('Vui lòng chọn file hình ảnh (JPG, JPEG hoặc PNG)');
                fileInput.value = '';
                return;
            }

            // Check file size (max 5MB)
            const maxSize = 5 * 1024 * 1024; // 5MB in bytes
            if (file.size > maxSize) {
                alert('File không được vượt quá 5MB');
                fileInput.value = '';
                return;
            }
        }
    });

    // Form submission handling
    form.addEventListener('submit', function(e) {
        if (!fileInput.value) {
            e.preventDefault();
            alert('Vui lòng chọn file để phân tích');
            return;
        }
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Đang phân tích...';
    });
});

// Result container animation
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

// Call animation when results are loaded
if (document.querySelector('.result-container')) {
    animateResults();
}
