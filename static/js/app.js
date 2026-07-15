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
        const sidebar = document.getElementById('sidebar');
        if (sidebarToggle && sidebar) {
            const backdrop = document.getElementById('sidebarBackdrop');
            sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('show');
                backdrop?.classList.toggle('show');
            });
            backdrop?.addEventListener('click', function() {
                sidebar.classList.remove('show');
                backdrop.classList.remove('show');
            });
        }
    });
})();
