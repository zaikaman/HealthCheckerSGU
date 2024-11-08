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

// Initialize history cards
function initializeHistoryCards() {
    const historyCards = document.querySelectorAll('.history-card');
    
    historyCards.forEach(card => {
        // Add hover effect
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
            card.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.12)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.08)';
        });

        // Format dates
        const dateElement = card.querySelector('.history-date');
        if (dateElement) {
            const date = new Date(dateElement.textContent.trim());
            if (!isNaN(date)) {
                dateElement.innerHTML = `
                    <i class="far fa-clock"></i> 
                    ${date.toLocaleDateString('vi-VN', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit'
                    })}
                `;
            }
        }

        // Format content
        const resultContainer = card.querySelector('.result-container');
        if (resultContainer) {
            // Clean up and format the content
            let content = resultContainer.innerHTML;
            content = content.replace(/\n/g, '<br>');
            content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            resultContainer.innerHTML = content;
        }

        // Add copy button for text content
        const textContent = card.querySelector('.history-content');
        if (textContent) {
            const copyButton = document.createElement('button');
            copyButton.className = 'btn btn-sm btn-outline-primary mt-2';
            copyButton.innerHTML = '<i class="fas fa-copy"></i> Sao chép';
            copyButton.onclick = () => {
                const text = textContent.textContent.trim();
                navigator.clipboard.writeText(text)
                    .then(() => {
                        copyButton.innerHTML = '<i class="fas fa-check"></i> Đã sao chép';
                        setTimeout(() => {
                            copyButton.innerHTML = '<i class="fas fa-copy"></i> Sao chép';
                        }, 2000);
                    })
                    .catch(err => console.error('Copy failed:', err));
            };
            textContent.appendChild(copyButton);
        }
    });
}

// Rest of your existing functions...
