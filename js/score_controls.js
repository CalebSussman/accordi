/**
 * Score Display and Playback Controls
 * Manages OSMD rendering options, playback, and view customization
 */

// OSMD instance (will be set after score loads)
let osmdInstance = null;
let playbackState = {
    isPlaying: false,
    tempo: 1.0,
    currentTime: 0,
    totalTime: 0
};

// View settings (saved to localStorage)
let viewSettings = {
    sansSerif: false,
    noteColor: '#000000',
    zoom: 1.0,
    showNoteNames: false,
    showChordSymbols: true,
    showFingerings: false // Phase 5
};

/**
 * Initialize score controls after OSMD loads
 * @param {OpenSheetMusicDisplay} osmd - OSMD instance
 */
export function initializeScoreControls(osmd) {
    osmdInstance = osmd;

    // Load saved settings
    loadViewSettings();

    // Show controls
    showControls();

    // Set up event listeners
    setupPlaybackControls();
    setupViewControls();

    // Apply initial settings
    applyViewSettings();

    // Calculate total duration
    calculateDuration();
}

/**
 * Show playback and view controls
 */
function showControls() {
    document.getElementById('playbackControls')?.classList.remove('hidden');
    document.getElementById('viewMenuBtn')?.classList.remove('hidden');
}

/**
 * Hide controls when no score is loaded
 */
export function hideControls() {
    document.getElementById('playbackControls')?.classList.add('hidden');
    document.getElementById('viewMenuBtn')?.classList.add('hidden');
}

/**
 * Set up playback control event listeners
 */
function setupPlaybackControls() {
    const playPauseBtn = document.getElementById('playPauseBtn');
    const stopBtn = document.getElementById('stopBtn');
    const tempoSlider = document.getElementById('tempoSlider');
    const tempoValue = document.getElementById('tempoValue');

    // Play/Pause
    playPauseBtn?.addEventListener('click', togglePlayback);

    // Stop
    stopBtn?.addEventListener('click', stop);

    // Tempo slider
    tempoSlider?.addEventListener('input', (e) => {
        const value = parseInt(e.target.value);
        playbackState.tempo = value / 100;
        tempoValue.textContent = `${value}%`;

        // TODO: Update OSMD playback speed when implemented
        // osmdInstance.PlaybackManager?.setPlaybackSpeed(playbackState.tempo);
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Space = play/pause (only when not typing in input)
        if (e.code === 'Space' && e.target.tagName !== 'INPUT') {
            e.preventDefault();
            togglePlayback();
        }
    });
}

/**
 * Set up view control event listeners
 */
function setupViewControls() {
    const viewMenuBtn = document.getElementById('viewMenuBtn');
    const viewPanel = document.getElementById('viewPanel');

    // Toggle view panel
    viewMenuBtn?.addEventListener('click', () => {
        viewPanel?.classList.toggle('open');
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
        if (!viewPanel?.contains(e.target) &&
            !viewMenuBtn?.contains(e.target) &&
            viewPanel?.classList.contains('open')) {
            viewPanel.classList.remove('open');
        }
    });

    // Sans-serif toggle
    document.getElementById('sansSerifToggle')?.addEventListener('change', (e) => {
        viewSettings.sansSerif = e.target.checked;
        applyFontSettings();
        saveViewSettings();
    });

    // Note color picker
    document.getElementById('noteColorPicker')?.addEventListener('change', (e) => {
        viewSettings.noteColor = e.target.value;
        applyNoteColor();
        saveViewSettings();
    });

    // Zoom slider
    const zoomSlider = document.getElementById('zoomSlider');
    const zoomValue = document.getElementById('zoomValue');
    zoomSlider?.addEventListener('input', (e) => {
        const value = parseInt(e.target.value);
        viewSettings.zoom = value / 100;
        zoomValue.textContent = `${value}%`;
        applyZoom();
        saveViewSettings();
    });

    // Note names toggle
    document.getElementById('noteNamesToggle')?.addEventListener('change', (e) => {
        viewSettings.showNoteNames = e.target.checked;
        applyNoteNames();
        saveViewSettings();
    });

    // Chord symbols toggle
    document.getElementById('chordSymbolsToggle')?.addEventListener('change', (e) => {
        viewSettings.showChordSymbols = e.target.checked;
        applyChordSymbols();
        saveViewSettings();
    });
}

/**
 * Toggle play/pause
 */
function togglePlayback() {
    const playIcon = document.getElementById('playIcon');
    const pauseIcon = document.getElementById('pauseIcon');

    if (playbackState.isPlaying) {
        pause();
        playIcon?.classList.remove('hidden');
        pauseIcon?.classList.add('hidden');
    } else {
        play();
        playIcon?.classList.add('hidden');
        pauseIcon?.classList.remove('hidden');
    }
}

/**
 * Start playback
 */
function play() {
    playbackState.isPlaying = true;

    // TODO: Implement OSMD playback when available
    // OSMD 1.8.6 has experimental playback support
    // For now, just show placeholder
    console.log('Playback started (TODO: implement OSMD PlaybackManager)');

    // Placeholder: simulate playback
    startTimeUpdate();
}

/**
 * Pause playback
 */
function pause() {
    playbackState.isPlaying = false;
    console.log('Playback paused');
}

/**
 * Stop playback
 */
function stop() {
    playbackState.isPlaying = false;
    playbackState.currentTime = 0;

    const playIcon = document.getElementById('playIcon');
    const pauseIcon = document.getElementById('pauseIcon');
    playIcon?.classList.remove('hidden');
    pauseIcon?.classList.add('hidden');

    updateTimeDisplay();

    console.log('Playback stopped');
}

/**
 * Start time update interval (placeholder until OSMD playback)
 */
function startTimeUpdate() {
    const interval = setInterval(() => {
        if (!playbackState.isPlaying) {
            clearInterval(interval);
            return;
        }

        playbackState.currentTime += 0.1;
        if (playbackState.currentTime >= playbackState.totalTime) {
            stop();
            clearInterval(interval);
        }

        updateTimeDisplay();
    }, 100);
}

/**
 * Update time display
 */
function updateTimeDisplay() {
    const currentTimeEl = document.getElementById('currentTime');
    const totalTimeEl = document.getElementById('totalTime');

    if (currentTimeEl) {
        currentTimeEl.textContent = formatTime(playbackState.currentTime);
    }
    if (totalTimeEl) {
        totalTimeEl.textContent = formatTime(playbackState.totalTime);
    }
}

/**
 * Format time in M:SS
 */
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Calculate score duration (placeholder)
 */
function calculateDuration() {
    // TODO: Calculate from OSMD sheet data
    // For now, estimate based on measures and tempo
    playbackState.totalTime = 120; // Placeholder: 2 minutes
    updateTimeDisplay();
}

/**
 * Apply all view settings to OSMD
 */
function applyViewSettings() {
    applyFontSettings();
    applyNoteColor();
    applyZoom();
    applyNoteNames();
    applyChordSymbols();
}

/**
 * Apply sans-serif font setting
 */
function applyFontSettings() {
    if (!osmdInstance) return;

    const container = document.getElementById('osmd-container');
    if (viewSettings.sansSerif) {
        container?.style.setProperty('font-family', 'system-ui, -apple-system, sans-serif');
    } else {
        container?.style.removeProperty('font-family');
    }
}

/**
 * Apply note color
 */
function applyNoteColor() {
    const container = document.getElementById('osmd-container');
    if (container) {
        container.style.setProperty('--note-color', viewSettings.noteColor);
    }

    // Apply to SVG elements
    const noteheads = container?.querySelectorAll('.vf-notehead, .vf-stem, .vf-beam');
    noteheads?.forEach(el => {
        el.style.fill = viewSettings.noteColor;
        el.style.stroke = viewSettings.noteColor;
    });
}

/**
 * Apply zoom level
 */
function applyZoom() {
    if (!osmdInstance) return;

    try {
        osmdInstance.zoom = viewSettings.zoom;
        osmdInstance.render();
    } catch (e) {
        console.error('Error applying zoom:', e);
    }
}

/**
 * Apply note names setting
 */
function applyNoteNames() {
    if (!osmdInstance) return;

    // TODO: OSMD EngravingRules.RenderNoteNames
    // Requires re-render
    console.log('Note names:', viewSettings.showNoteNames ? 'shown' : 'hidden');
}

/**
 * Apply chord symbols setting
 */
function applyChordSymbols() {
    if (!osmdInstance) return;

    // TODO: OSMD has chord symbol rendering options
    console.log('Chord symbols:', viewSettings.showChordSymbols ? 'shown' : 'hidden');
}

/**
 * Load view settings from localStorage
 */
function loadViewSettings() {
    const saved = localStorage.getItem('akkordio_view_settings');
    if (saved) {
        try {
            viewSettings = { ...viewSettings, ...JSON.parse(saved) };

            // Update UI elements
            document.getElementById('sansSerifToggle').checked = viewSettings.sansSerif;
            document.getElementById('noteColorPicker').value = viewSettings.noteColor;
            document.getElementById('zoomSlider').value = viewSettings.zoom * 100;
            document.getElementById('zoomValue').textContent = `${Math.round(viewSettings.zoom * 100)}%`;
            document.getElementById('noteNamesToggle').checked = viewSettings.showNoteNames;
            document.getElementById('chordSymbolsToggle').checked = viewSettings.showChordSymbols;
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
    osmdInstance = null;
    playbackState = {
        isPlaying: false,
        tempo: 1.0,
        currentTime: 0,
        totalTime: 0
    };
    hideControls();
}
