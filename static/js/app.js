// Theme toggle
(function() {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark') document.documentElement.setAttribute('data-bs-theme', 'dark');

    document.addEventListener('DOMContentLoaded', function() {
        const toggle = document.getElementById('theme-toggle');
        if (toggle) {
            const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
            toggle.querySelector('i').className = isDark ? 'bi bi-sun' : 'bi bi-moon-stars';
            toggle.querySelector('span').textContent = isDark ? 'Light Mode' : 'Dark Mode';

            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                const current = document.documentElement.getAttribute('data-bs-theme');
                const next = current === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-bs-theme', next);
                localStorage.setItem('theme', next);
                toggle.querySelector('i').className = next === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
                toggle.querySelector('span').textContent = next === 'dark' ? 'Light Mode' : 'Dark Mode';
            });
        }

        // Sidebar toggle on mobile
        const sidebarToggle = document.getElementById('sidebarToggle');
        const closeSidebar = document.getElementById('closeSidebar');
        const sidebar = document.getElementById('sidebar');
        const backdrop = document.getElementById('sidebarBackdrop');
        
        function openSidebar() {
            sidebar.classList.add('show');
            backdrop?.classList.add('show');
            document.body.classList.add('sidebar-open');
            sidebarToggle?.setAttribute('aria-expanded', 'true');
        }
        
        function closeSidebarFn() {
            sidebar.classList.remove('show');
            backdrop?.classList.remove('show');
            document.body.classList.remove('sidebar-open');
            sidebarToggle?.setAttribute('aria-expanded', 'false');
        }
        
        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', openSidebar);
        }
        
        if (closeSidebar) {
            closeSidebar.addEventListener('click', closeSidebarFn);
        }
        
        backdrop?.addEventListener('click', closeSidebarFn);

        // Close sidebar on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && sidebar?.classList.contains('show')) {
                closeSidebarFn();
            }
        });

        // Close sidebar when clicking a nav link on mobile
        const navLinks = sidebar?.querySelectorAll('.nav-link');
        navLinks?.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    closeSidebarFn();
                }
            });
        });

        // Close sidebar on window resize to desktop
        window.addEventListener('resize', function() {
            if (window.innerWidth >= 992) {
                closeSidebarFn();
            }
        });
    });
})();
