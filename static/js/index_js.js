document.addEventListener('DOMContentLoaded', function() {
    // Khởi tạo các biến global
    const isLoggedIn = document.body.dataset.loggedIn === 'true';
    const loginModal = document.getElementById('loginModal');
    const checkLoginButtons = document.querySelectorAll('.check-login');
    const navbar = document.querySelector('.navbar');
    let lastScrollTop = 0;
    let scrollTimeout;

    /**
     * Xử lý smooth scrolling cho các anchor link
     */
    function initializeSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
    }

    /**
     * Hiển thị modal đăng nhập và ngăn chặn điều hướng
     */
    function showLoginModal(e) {
        if (!isLoggedIn) {
            e.preventDefault();
            e.stopPropagation();
            loginModal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    }

    /**
     * Ẩn modal đăng nhập
     */
    function hideLoginModal(e) {
        if (e.target === loginModal) {
            loginModal.classList.remove('show');
            document.body.style.overflow = '';
        }
    }

    /**
     * Xử lý click vào feature card
     */
    function handleFeatureCardClick(card) {
        card.addEventListener('click', (e) => {
            // Bỏ qua nếu click vào nút "Bắt đầu"
            if (e.target.classList.contains('check-login') || e.target.closest('.check-login')) {
                return;
            }

            // Kiểm tra đăng nhập trước khi điều hướng
            const url = card.dataset.url;
            if (!isLoggedIn) {
                e.preventDefault();
                showLoginModal(e);
                return;
            }

            // Thêm hiệu ứng chuyển trang
            const transition = document.createElement('div');
            transition.className = 'page-transition';
            document.body.appendChild(transition);

            // Hiệu ứng fade out cho các card
            const cards = document.querySelectorAll('.feature-card');
            cards.forEach(card => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
            });

            // Điều hướng sau khi hoàn thành hiệu ứng
            setTimeout(() => {
                window.location.href = url;
            }, 500);
        });
    }

    /**
     * Khởi tạo các animation và event cho feature cards
     */
    function initializeFeatureCards() {
        const featureCards = document.querySelectorAll('.feature-card');
        featureCards.forEach(card => {
            // Hiệu ứng hover
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-10px)';
                this.style.boxShadow = '0 8px 16px rgba(0,0,0,0.2)';
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
            });

            // Xử lý click
            handleFeatureCardClick(card);
        });

        // Hiệu ứng fade in khi load trang
        featureCards.forEach((card, index) => {
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    /**
     * Xử lý scroll behavior của navbar
     */
    function handleNavbarScroll() {
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
    }

    /**
     * Khởi tạo dropdown menu behavior
     */
    function initializeDropdownMenu() {
        document.querySelectorAll('.dropdown').forEach(dropdown => {
            dropdown.addEventListener('show.bs.dropdown', function() {
                navbar.style.transform = 'translateY(0)';
            });
        });

        // Xử lý menu dropdown khi chưa đăng nhập
        const menuDropdown = document.querySelector('.dropdown-toggle');
        if (menuDropdown && !isLoggedIn) {
            menuDropdown.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                showLoginModal(e);
            });
        }
    }

    /**
     * Khởi tạo tooltips
     */
    function initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    /**
     * Khởi tạo các event listener cho nút đăng nhập
     */
    function initializeLoginButtons() {
        if (!isLoggedIn) {
            // Sử dụng capturing phase để đảm bảo xử lý trước khi bubble
            checkLoginButtons.forEach(button => {
                button.addEventListener('click', showLoginModal, true);
            });

            // Đóng modal khi click bên ngoài
            loginModal.addEventListener('click', hideLoginModal);
        }
    }

    // Khởi tạo tất cả các chức năng
    initializeSmoothScrolling();
    initializeFeatureCards();
    handleNavbarScroll();
    initializeDropdownMenu();
    initializeTooltips();
    initializeLoginButtons();
});
