document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeTabs();
    initializeHistoryCards();
    initializeAudioPlayers();
    initializeImagePreviews();
    initializeScrollToTop();
    
    // Add intersection observer for animations
    initializeScrollAnimations();
});

// Initialize tabs with smooth transitions
function initializeTabs() {
    const tabLinks = document.querySelectorAll('.nav-link');
    const tabContents = document.querySelectorAll('.tab-pane');
    
    tabLinks.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Update active tab
            tabLinks.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Show content with animation
            const targetId = this.getAttribute('href');
            const targetContent = document.querySelector(targetId);
            
            tabContents.forEach(content => {
                content.style.opacity = '0';
                setTimeout(() => {
                    content.classList.remove('show', 'active');
                }, 300);
            });
            
            setTimeout(() => {
                targetContent.classList.add('show', 'active');
                targetContent.style.opacity = '1';
            }, 300);
        });
    });
}

// Initialize scroll animations
function initializeScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1
    });
    
    document.querySelectorAll('.history-card').forEach(card => {
        observer.observe(card);
    });
}

// Enhanced image preview
function initializeImagePreviews() {
    document.querySelectorAll('.history-file img').forEach(img => {
        img.addEventListener('click', function() {
            const modal = createImageModal(this.src);
            document.body.appendChild(modal);
            
            setTimeout(() => modal.classList.add('visible'), 50);
            
            modal.addEventListener('click', e => {
                if (e.target === modal) {
                    modal.classList.remove('visible');
                    setTimeout(() => modal.remove(), 300);
                }
            });
        });
    });
}

// Create image modal
function createImageModal(src) {
    const modal = document.createElement('div');
    modal.className = 'image-preview-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <img src="${src}" alt="Preview">
            <button class="close-button">&times;</button>
        </div>
    `;
    return modal;
}

// Initialize custom audio players
function initializeAudioPlayers() {
    document.querySelectorAll('audio').forEach(audio => {
        const wrapper = document.createElement('div');
        wrapper.className = 'audio-player';
        audio.parentNode.insertBefore(wrapper, audio);
        wrapper.appendChild(audio);
        
        audio.addEventListener('play', () => {
            wrapper.classList.add('playing');
        });
        
        audio.addEventListener('pause', () => {
            wrapper.classList.remove('playing');
        });
    });
}

// Initialize scroll to top
function initializeScrollToTop() {
    const scrollButton = document.createElement('div');
    scrollButton.className = 'scroll-to-top';
    scrollButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(scrollButton);
    
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollButton.classList.add('show');
        } else {
            scrollButton.classList.remove('show');
        }
    });
    
    scrollButton.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Rest of your existing functions...
