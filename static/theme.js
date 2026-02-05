/**
 * MindCare Theme Management System
 * Handles light/dark mode persistence and toggle logic
 */

const ThemeManager = {
    init() {
        const savedTheme = localStorage.getItem('mindcare-theme') || 'light';
        this.setTheme(savedTheme);
        this.updateIcons(savedTheme);
    },

    toggle() {
        const currentTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
        localStorage.setItem('mindcare-theme', newTheme);
        this.updateIcons(newTheme);
    },

    setTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
    },

    updateIcons(theme) {
        const icons = document.querySelectorAll('.theme-toggle-icon');
        icons.forEach(icon => {
            if (theme === 'dark') {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            } else {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            }
        });
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
