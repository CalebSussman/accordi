/**
 * Akkordio - Theme Toggle
 * Light/dark mode switching with localStorage persistence
 */

(function() {
    'use strict';

    // Get theme from localStorage or default to light
    const getStoredTheme = () => localStorage.getItem('theme') || 'light';
    const setStoredTheme = (theme) => localStorage.setItem('theme', theme);

    // Apply theme to HTML element
    const applyTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        updateToggleButtons(theme);
    };

    // Update toggle button states
    const updateToggleButtons = (theme) => {
        const lightBtn = document.getElementById('themeLight');
        const darkBtn = document.getElementById('themeDark');

        if (!lightBtn || !darkBtn) return;

        if (theme === 'light') {
            lightBtn.classList.add('active');
            darkBtn.classList.remove('active');
        } else {
            lightBtn.classList.remove('active');
            darkBtn.classList.add('active');
        }
    };

    // Initialize theme on page load
    const initTheme = () => {
        const theme = getStoredTheme();
        applyTheme(theme);
    };

    // Set up event listeners when DOM is ready
    const setupEventListeners = () => {
        const lightBtn = document.getElementById('themeLight');
        const darkBtn = document.getElementById('themeDark');

        if (lightBtn) {
            lightBtn.addEventListener('click', () => {
                setStoredTheme('light');
                applyTheme('light');
            });
        }

        if (darkBtn) {
            darkBtn.addEventListener('click', () => {
                setStoredTheme('dark');
                applyTheme('dark');
            });
        }
    };

    // Initialize on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initTheme();
            setupEventListeners();
        });
    } else {
        initTheme();
        setupEventListeners();
    }
})();
