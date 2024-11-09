document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Feature cards animation
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 8px 16px rgba(0,0,0,0.2)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
        });

        card.addEventListener('click', () => {
            const url = card.dataset.url;
            const transition = document.createElement('div');
            transition.className = 'page-transition';
            document.body.appendChild(transition);

            // Thêm hiệu ứng fade out cho card
            const cards = document.querySelectorAll('.feature-card');
            cards.forEach(card => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
            });

            setTimeout(() => {
                window.location.href = url;
            }, 500);
        });
    });

    // Hero section parallax effect
    const heroSection = document.querySelector('.hero-section');
    let ticking = false;

    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(function() {
                if (heroSection) {
                    const scrolled = window.pageYOffset;
                    const translateY = Math.max(0, scrolled * 0.5);
                    heroSection.style.transform = `translate3d(0, ${translateY}px, 0)`;
                }
                ticking = false;
            });
            ticking = true;
        }
    });

    // Navbar scroll behavior
    const navbar = document.querySelector('.navbar');
    let lastScrollTop = 0;
    let scrollTimeout;

    window.addEventListener('scroll', function() {
        if (scrollTimeout) {
            window.cancelAnimationFrame(scrollTimeout);
        }

        scrollTimeout = window.requestAnimationFrame(function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (!document.querySelector('.dropdown-menu.show')) {
                if (scrollTop > lastScrollTop && scrollTop > 100) {
                    // Scrolling down
                    navbar.style.transform = 'translateY(-100%)';
                } else {
                    // Scrolling up
                    navbar.style.transform = 'translateY(0)';
                }
            }
            
            if (scrollTop === 0) {
                navbar.classList.remove('navbar-scrolled');
            } else {
                navbar.classList.add('navbar-scrolled');
            }
            
            lastScrollTop = scrollTop;
        });
    });

    // Thêm xử lý cho dropdown menu
    document.querySelectorAll('.dropdown').forEach(dropdown => {
        dropdown.addEventListener('show.bs.dropdown', function () {
            navbar.style.transform = 'translateY(0)'; // Hiển thị navbar khi dropdown được mở
        });
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Kiểm tra trạng thái đăng nhập
    const isLoggedIn = document.body.dataset.loggedIn === 'true';
    const loginModal = document.getElementById('loginModal');
    const checkLoginButtons = document.querySelectorAll('.check-login');

    function showLoginModal(e) {
        // Chỉ hiện modal nếu chưa đăng nhập
        if (!isLoggedIn) {
            e.preventDefault();
            loginModal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    }

    function hideLoginModal(e) {
        if (e.target === loginModal) {
            loginModal.classList.remove('show');
            document.body.style.overflow = '';
        }
    }

    // Thêm event listeners chỉ khi chưa đăng nhập
    if (!isLoggedIn) {
        checkLoginButtons.forEach(button => {
            button.addEventListener('click', showLoginModal);
        });
        loginModal.addEventListener('click', hideLoginModal);
    }

    // Xử lý menu dropdown
    const menuDropdown = document.querySelector('.dropdown-toggle');
    if (menuDropdown && !isLoggedIn) {
        menuDropdown.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            showLoginModal(e);
        });
    }

    // Thêm hiệu ứng fade in khi load trang
    const cards = document.querySelectorAll('.feature-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});
