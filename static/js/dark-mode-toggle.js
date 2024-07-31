document.addEventListener('DOMContentLoaded', function () {
    const toggleButton = document.getElementById('darkModeToggle');
    const body = document.body;

    // Load dark mode preference from localStorage
    if (localStorage.getItem('darkMode') === 'enabled') {
        enableDarkMode();
    }

    toggleButton.addEventListener('click', function () {
        if (body.classList.contains('dark-mode')) {
            disableDarkMode();
        } else {
            enableDarkMode();
        }
    });

    function enableDarkMode() {
        body.classList.add('dark-mode');
        document.querySelector('.navbar').classList.add('dark-mode');
        document.querySelectorAll('.card').forEach(card => card.classList.add('dark-mode'));
        localStorage.setItem('darkMode', 'enabled');
    }

    function disableDarkMode() {
        body.classList.remove('dark-mode');
        document.querySelector('.navbar').classList.remove('dark-mode');
        document.querySelectorAll('.card').forEach(card => card.classList.remove('dark-mode'));
        localStorage.setItem('darkMode', 'disabled');
    }
});