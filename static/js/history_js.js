// Document ready handler
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tab functionality
    initializeTabs();
    
    // Add animation to history cards
    initializeHistoryCards();
    
    // Initialize audio players
    initializeAudioPlayers();
    
    // Handle image preview
    initializeImagePreviews();
});

// Initialize tabs with animation
function initializeTabs() {
    const tabLinks = document.querySelectorAll('.nav-link');
    
    tabLinks.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs
            tabLinks.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Show corresponding content with animation
            const targetId = this.getAttribute('href');
            const targetContent = document.querySelector(targetId);
            
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('show', 'active');
                pane.style.opacity = '0';
            });
            
            setTimeout(() => {
                targetContent.classList.add('show', 'active');
                targetContent.style.opacity = '1';
            }, 150);
        });
    });
}

// Initialize history cards with animation
function initializeHistoryCards() {
    const cards = document.querySelectorAll('.history-card');
    
    cards.forEach((card, index) => {
        // Add animation delay based on card position
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
        
        // Add hover effect
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 16px rgba(0,0,0,0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
        });
    });
}

// Initialize audio players
function initializeAudioPlayers() {
    const audioPlayers = document.querySelectorAll('audio');
    
    audioPlayers.forEach(player => {
        // Add custom styling and controls
        player.addEventListener('play', function() {
            this.closest('.history-card').classList.add('playing');
        });
        
        player.addEventListener('pause', function() {
            this.closest('.history-card').classList.remove('playing');
        });
        
        player.addEventListener('ended', function() {
            this.closest('.history-card').classList.remove('playing');
        });
    });
}

// Initialize image previews
function initializeImagePreviews() {
    const images = document.querySelectorAll('.history-file img');
    
    images.forEach(img => {
        img.addEventListener('click', function() {
            openImagePreview(this.src);
        });
    });
}

// Open image preview modal
function openImagePreview(src) {
    const modal = document.createElement('div');
    modal.className = 'image-preview-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close-button">&times;</span>
            <img src="${src}" alt="Preview">
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close modal on click outside or close button
    modal.addEventListener('click', function(e) {
        if (e.target === modal || e.target.className === 'close-button') {
            modal.remove();
        }
    });
}

// Add scroll to top button functionality
window.addEventListener('scroll', function() {
    const scrollButton = document.querySelector('.scroll-to-top');
    if (window.pageYOffset > 300) {
        scrollButton?.classList.add('show');
    } else {
        scrollButton?.classList.remove('show');
    }
});
