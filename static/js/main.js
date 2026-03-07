document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const htmlElement = document.documentElement;

    // Use relative paths to ensure they resolve correctly from the static folder
    const sunIcon = "/static/images/sun_icon.png"; 
    const moonIcon = "/static/images/moon_icon.png";

    const updateIcon = (theme) => {
        // Show sun icon in dark mode (to switch to light), moon icon in light mode (to switch to dark)
        themeIcon.src = (theme === 'dark') ? sunIcon : moonIcon;
    };

    const updateTheme = (theme) => {
        htmlElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        updateIcon(theme);
    };

    // Loads saved theme on page load
    const savedTheme = localStorage.getItem('theme') || 'light';
    updateTheme(savedTheme);

    // Handle theme toggle click
    themeToggle.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-bs-theme');
        const newTheme = (currentTheme === 'dark') ? 'light' : 'dark';
        updateTheme(newTheme);
    });

    // Optional: Listen for system theme changes
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addListener((e) => {
            if (!localStorage.getItem('theme')) {
                updateTheme(e.matches ? 'dark' : 'light');
            }
        });
    }
});