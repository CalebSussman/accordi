/**
 * Score Display and View Controls
 * Manages OSMD rendering with clean icon-based interface
 */

import { NoteNameRenderer } from './note_names.js';

// OSMD instance (will be set after score loads)
let osmdInstance = null;

// Note name renderer instance
let noteNameRenderer = null;

// View settings
let viewSettings = {
    zoom: 1.0,
    spacing: 1.0, // Normal spacing
    showNoteNames: false,
    showFingerings: false
};

/**
 * Initialize score controls after OSMD loads
 * @param {OpenSheetMusicDisplay} osmd - OSMD instance
 */
export function initializeScoreControls(osmd) {
    osmdInstance = osmd;

    // Initialize note name renderer
    noteNameRenderer = new NoteNameRenderer(osmd);

    // Load saved settings
    loadViewSettings();

    // Show view controls
    showControls();

    // Set up event listeners
    setupViewControls();

    // Apply initial settings
    applyViewSettings();
}

/**
 * Show view button
 */
function showControls() {
    document.getElementById('viewBtn')?.classList.remove('hidden');
}

/**
 * Hide controls when no score is loaded
 */
export function hideControls() {
    document.getElementById('viewBtn')?.classList.add('hidden');
    document.getElementById('viewDrawer')?.classList.remove('open');
}

/**
 * Set up view control event listeners
 */
function setupViewControls() {
    const viewBtn = document.getElementById('viewBtn');
    const viewDrawer = document.getElementById('viewDrawer');
    const zoomOutBtn = document.getElementById('zoomOutBtn');
    const zoomInBtn = document.getElementById('zoomInBtn');
    const zoomLevel = document.getElementById('zoomLevel');
    const spacingNarrowBtn = document.getElementById('spacingNarrowBtn');
    const spacingWideBtn = document.getElementById('spacingWideBtn');
    const spacingLevel = document.getElementById('spacingLevel');
    const noteNamesToggle = document.getElementById('noteNamesToggle');
    const fingeringsToggle = document.getElementById('fingeringsToggle');

    // Toggle drawer
    viewBtn?.addEventListener('click', () => {
        viewDrawer?.classList.toggle('open');
    });

    // Close drawer when clicking outside
    document.addEventListener('click', (e) => {
        if (viewDrawer?.classList.contains('open') &&
            !viewDrawer.contains(e.target) &&
            !viewBtn?.contains(e.target)) {
            viewDrawer.classList.remove('open');
        }
    });

    // Zoom out
    zoomOutBtn?.addEventListener('click', () => {
        viewSettings.zoom = Math.max(0.5, viewSettings.zoom - 0.1);
        zoomLevel.textContent = `${Math.round(viewSettings.zoom * 100)}%`;
        applyZoom();
        saveViewSettings();
    });

    // Zoom in
    zoomInBtn?.addEventListener('click', () => {
        viewSettings.zoom = Math.min(2.0, viewSettings.zoom + 0.1);
        zoomLevel.textContent = `${Math.round(viewSettings.zoom * 100)}%`;
        applyZoom();
        saveViewSettings();
    });

    // Narrow spacing
    spacingNarrowBtn?.addEventListener('click', () => {
        viewSettings.spacing = Math.max(0.6, viewSettings.spacing - 0.1);
        updateSpacingDisplay();
        applySpacing();
        saveViewSettings();
    });

    // Widen spacing
    spacingWideBtn?.addEventListener('click', () => {
        viewSettings.spacing = Math.min(1.4, viewSettings.spacing + 0.1);
        updateSpacingDisplay();
        applySpacing();
        saveViewSettings();
    });

    // Toggle note names
    noteNamesToggle?.addEventListener('click', () => {
        viewSettings.showNoteNames = !viewSettings.showNoteNames;
        noteNamesToggle.classList.toggle('active', viewSettings.showNoteNames);
        applyNoteNames();
        saveViewSettings();
    });

    // Toggle fingerings
    fingeringsToggle?.addEventListener('click', () => {
        if (!fingeringsToggle.disabled) {
            viewSettings.showFingerings = !viewSettings.showFingerings;
            fingeringsToggle.classList.toggle('active', viewSettings.showFingerings);
            applyFingerings();
            saveViewSettings();
        }
    });

    function updateSpacingDisplay() {
        if (viewSettings.spacing < 0.9) {
            spacingLevel.textContent = 'Narrow';
        } else if (viewSettings.spacing > 1.1) {
            spacingLevel.textContent = 'Wide';
        } else {
            spacingLevel.textContent = 'Normal';
        }
    }
}

/**
 * Apply all view settings to OSMD
 */
function applyViewSettings() {
    applyZoom();
    applySpacing();
    applyNoteNames();
}

/**
 * Apply zoom level
 */
function applyZoom() {
    if (!osmdInstance) return;

    try {
        osmdInstance.zoom = viewSettings.zoom;
        osmdInstance.render();

        // Re-render note names if enabled (positions change with zoom)
        if (viewSettings.showNoteNames && noteNameRenderer) {
            noteNameRenderer.renderNoteNames();
        }

        console.log(`Zoom: ${Math.round(viewSettings.zoom * 100)}%`);
    } catch (e) {
        console.error('Error applying zoom:', e);
    }
}

/**
 * Apply spacing setting
 */
function applySpacing() {
    if (!osmdInstance) return;

    try {
        // OSMD EngravingRules control note spacing
        // Base values are multiplied by the spacing factor
        const baseMinDistance = 3;
        const baseMaxDistance = 10;

        osmdInstance.EngravingRules.MinimumDistanceBetweenNotes = baseMinDistance * viewSettings.spacing;
        osmdInstance.EngravingRules.MaximumDistanceBetweenNotes = baseMaxDistance * viewSettings.spacing;

        osmdInstance.render();

        // Re-render note names if enabled (positions change with spacing)
        if (viewSettings.showNoteNames && noteNameRenderer) {
            noteNameRenderer.renderNoteNames();
        }

        console.log(`Spacing: ${Math.round(viewSettings.spacing * 100)}%`);
    } catch (e) {
        console.error('Error applying spacing:', e);
    }
}

/**
 * Apply note names setting
 */
function applyNoteNames() {
    if (!osmdInstance || !noteNameRenderer) return;

    try {
        if (viewSettings.showNoteNames) {
            noteNameRenderer.renderNoteNames();
        } else {
            noteNameRenderer.clearNoteNames();
        }
        console.log('Note names:', viewSettings.showNoteNames ? 'enabled' : 'disabled');
    } catch (e) {
        console.error('Error applying note names:', e);
    }
}

/**
 * Apply fingerings setting (Phase 5)
 */
function applyFingerings() {
    if (!osmdInstance) return;

    // TODO: Implement fingering display (Phase 5)
    console.log('Fingerings:', viewSettings.showFingerings ? 'enabled' : 'disabled');
}

/**
 * Load view settings from localStorage
 */
function loadViewSettings() {
    const saved = localStorage.getItem('akkordio_view_settings');
    if (saved) {
        try {
            const loaded = JSON.parse(saved);
            viewSettings = { ...viewSettings, ...loaded };

            // Update UI elements
            const zoomLevel = document.getElementById('zoomLevel');
            const spacingLevel = document.getElementById('spacingLevel');
            const noteNamesToggle = document.getElementById('noteNamesToggle');
            const fingeringsToggle = document.getElementById('fingeringsToggle');

            // Update zoom display
            if (zoomLevel) {
                zoomLevel.textContent = `${Math.round(viewSettings.zoom * 100)}%`;
            }

            // Update spacing display
            if (spacingLevel) {
                if (viewSettings.spacing < 0.9) {
                    spacingLevel.textContent = 'Narrow';
                } else if (viewSettings.spacing > 1.1) {
                    spacingLevel.textContent = 'Wide';
                } else {
                    spacingLevel.textContent = 'Normal';
                }
            }

            // Update button states
            noteNamesToggle?.classList.toggle('active', viewSettings.showNoteNames);
            fingeringsToggle?.classList.toggle('active', viewSettings.showFingerings);
        } catch (e) {
            console.error('Error loading view settings:', e);
        }
    }
}

/**
 * Save view settings to localStorage
 */
function saveViewSettings() {
    localStorage.setItem('akkordio_view_settings', JSON.stringify(viewSettings));
}

/**
 * Reset controls when score is unloaded
 */
export function resetControls() {
    // Clear note names if they exist
    if (noteNameRenderer) {
        noteNameRenderer.clearNoteNames();
        noteNameRenderer = null;
    }

    osmdInstance = null;
    hideControls();
}
