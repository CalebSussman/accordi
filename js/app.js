/**
 * Akkordio - Main Application Controller
 * Handles UI interactions, file upload, and application state
 */

import * as API from './api.js';
import { renderTrebleKeyboard, renderBassKeyboard, addButtonClickHandlers } from './accordion_svg.js';

// OSMD is loaded from CDN in index.html
const { OpenSheetMusicDisplay } = window.opensheetmusicdisplay;

// Application state
const state = {
    currentJobId: null,
    currentHand: 'right', // 'right', 'left', or 'both'
    trebleLayout: null,
    bassLayout: null,
    results: null,
    isProcessing: false
};

// DOM elements
const elements = {
    // Navigation
    uploadBtn: document.getElementById('uploadBtn'),
    loadPreviousBtn: document.getElementById('loadPreviousBtn'),
    settingsBtn: document.getElementById('settingsBtn'),
    settingsPanel: document.getElementById('settingsPanel'),

    // Upload
    uploadZone: document.getElementById('uploadZone'),
    fileInput: document.getElementById('fileInput'),
    emptyState: document.getElementById('emptyState'),
    testMusicXMLBtn: document.getElementById('testMusicXMLBtn'),
    musicxmlInput: document.getElementById('musicxmlInput'),

    // Processing
    processingOverlay: document.getElementById('processingOverlay'),
    processingText: document.getElementById('processingText'),
    processingProgress: document.getElementById('processingProgress'),

    // Accordion panel
    accordionPanel: document.getElementById('accordionPanel'),
    toggleRight: document.getElementById('toggleRight'),
    toggleLeft: document.getElementById('toggleLeft'),
    toggleBoth: document.getElementById('toggleBoth'),
    trebleKeyboard: document.getElementById('trebleKeyboard'),
    bassKeyboard: document.getElementById('bassKeyboard'),
    currentLayout: document.getElementById('currentLayout'),
    layoutRange: document.getElementById('layoutRange'),

    // Playback
    playbackBar: document.getElementById('playbackBar'),
    playBtn: document.getElementById('playBtn'),
    playIcon: document.getElementById('playIcon'),
    pauseIcon: document.getElementById('pauseIcon'),
    progressFill: document.getElementById('progressFill'),
    currentTime: document.getElementById('currentTime'),
    tempo: document.getElementById('tempo'),

    // Settings
    trebleLayoutSelect: document.getElementById('trebleLayoutSelect'),
    bassLayoutSelect: document.getElementById('bassLayoutSelect'),
    omrEngineSelect: document.getElementById('omrEngineSelect'),

    // Error
    errorToast: document.getElementById('errorToast'),
    errorText: document.getElementById('errorText'),
    closeError: document.getElementById('closeError')
};

// Debug: Log MusicXML elements on load
console.log('=== MusicXML Upload Debug ===');
console.log('testMusicXMLBtn:', elements.testMusicXMLBtn);
console.log('musicxmlInput:', elements.musicxmlInput);

/**
 * Initialize application
 */
function init() {
    setupEventListeners();
    checkBackendHealth();
    loadSavedJobId();
}

/**
 * Set up all event listeners
 */
function setupEventListeners() {
    // Upload button
    elements.uploadBtn?.addEventListener('click', () => {
        elements.fileInput?.click();
    });

    // Upload zone (drag & drop)
    elements.uploadZone?.addEventListener('click', () => {
        elements.fileInput?.click();
    });

    elements.uploadZone?.addEventListener('dragover', handleDragOver);
    elements.uploadZone?.addEventListener('dragleave', handleDragLeave);
    elements.uploadZone?.addEventListener('drop', handleDrop);

    // File input
    elements.fileInput?.addEventListener('change', handleFileSelect);

    // MusicXML test upload
    elements.testMusicXMLBtn?.addEventListener('click', () => {
        console.log('MusicXML button clicked');
        console.log('musicxmlInput element:', elements.musicxmlInput);
        if (elements.musicxmlInput) {
            elements.musicxmlInput.click();
        } else {
            console.error('musicxmlInput element not found!');
        }
    });
    elements.musicxmlInput?.addEventListener('change', handleMusicXMLSelect);

    // Settings panel toggle
    elements.settingsBtn?.addEventListener('click', toggleSettingsPanel);

    // Click outside to close settings
    document.addEventListener('click', (e) => {
        if (!elements.settingsPanel?.contains(e.target) &&
            !elements.settingsBtn?.contains(e.target) &&
            elements.settingsPanel?.classList.contains('open')) {
            elements.settingsPanel.classList.remove('open');
        }
    });

    // Hand toggles
    elements.toggleRight?.addEventListener('click', () => setHand('right'));
    elements.toggleLeft?.addEventListener('click', () => setHand('left'));
    elements.toggleBoth?.addEventListener('click', () => setHand('both'));

    // Playback
    elements.playBtn?.addEventListener('click', togglePlayback);

    // Error close
    elements.closeError?.addEventListener('click', hideError);

    // Layout selection
    elements.trebleLayoutSelect?.addEventListener('change', handleLayoutChange);
    elements.bassLayoutSelect?.addEventListener('change', handleLayoutChange);
}

/**
 * Check backend health
 */
async function checkBackendHealth() {
    try {
        const health = await API.healthCheck();
        console.log('Backend health:', health);
    } catch (error) {
        console.warn('Backend not available:', error.message);
        showError('Backend server not available. Please start the server.');
    }
}

/**
 * Load saved job ID from localStorage
 */
function loadSavedJobId() {
    const savedJobId = localStorage.getItem('lastJobId');
    if (savedJobId) {
        console.log('Found saved job:', savedJobId);
        // Could auto-load results here
    }
}

/**
 * Handle drag over
 */
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    elements.uploadZone?.classList.add('drag-over');
}

/**
 * Handle drag leave
 */
function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    elements.uploadZone?.classList.remove('drag-over');
}

/**
 * Handle file drop
 */
function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    elements.uploadZone?.classList.remove('drag-over');

    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
        handleFile(files[0]);
    }
}

/**
 * Handle file select from input
 */
function handleFileSelect(e) {
    const files = e.target?.files;
    if (files && files.length > 0) {
        handleFile(files[0]);
    }
}

/**
 * Handle MusicXML file upload for direct testing
 */
async function handleMusicXMLSelect(e) {
    const files = e.target?.files;
    if (files && files.length > 0) {
        const file = files[0];

        // Validate file extension
        const validExtensions = ['.musicxml', '.mxl', '.xml'];
        const hasValidExtension = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));

        if (!hasValidExtension) {
            showError('Please upload a .musicxml, .mxl, or .xml file');
            return;
        }

        try {
            // Hide empty state, show processing
            elements.emptyState?.classList.add('hidden');
            elements.processingOverlay?.classList.remove('hidden');
            updateProcessingStatus('Uploading MusicXML file...', 10);

            // Upload to backend
            const uploadResult = await API.uploadMusicXML(file);
            console.log('MusicXML upload successful:', uploadResult);

            state.currentJobId = uploadResult.job_id;
            localStorage.setItem('lastJobId', uploadResult.job_id);

            updateProcessingStatus('Fetching MusicXML from server...', 50);

            // Fetch the MusicXML from the server
            const musicxmlUrl = API.getMusicXMLUrl(uploadResult.job_id);
            const response = await fetch(musicxmlUrl);

            if (!response.ok) {
                throw new Error(`Failed to fetch MusicXML: ${response.statusText}`);
            }

            const musicXmlText = await response.text();

            updateProcessingStatus('Rendering score...', 80);

            // Render with OSMD
            await renderScoreFromString(musicXmlText);

            // Hide processing overlay
            elements.processingOverlay?.classList.add('hidden');

            console.log('MusicXML rendered successfully from backend');
        } catch (error) {
            console.error('Error loading MusicXML:', error);
            showError(`Failed to load MusicXML: ${error.message}`);
            elements.processingOverlay?.classList.add('hidden');
            elements.emptyState?.classList.remove('hidden');
        }
    }
}

/**
 * Handle file upload and processing
 */
async function handleFile(file) {
    // Validate file
    if (!file.name.endsWith('.pdf')) {
        showError('Please upload a PDF file');
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        showError('File size exceeds 10MB limit');
        return;
    }

    try {
        state.isProcessing = true;

        // Show processing overlay
        elements.emptyState?.classList.add('hidden');
        elements.processingOverlay?.classList.remove('hidden');
        updateProcessingStatus('Uploading file...', 0);

        // Upload file
        const uploadResult = await API.uploadPDF(file);
        console.log('Upload successful:', uploadResult);
        state.currentJobId = uploadResult.job_id;

        // Save job ID
        localStorage.setItem('lastJobId', uploadResult.job_id);

        // Get selected layouts and OMR engine
        const trebleLayout = elements.trebleLayoutSelect?.value || 'c_system_5row';
        const bassLayout = elements.bassLayoutSelect?.value || 'stradella_120';
        const omrEngine = elements.omrEngineSelect?.value || 'oemer';

        // Start processing
        updateProcessingStatus(`Starting OMR processing (${omrEngine})...`, 10);
        await API.startProcessing(uploadResult.job_id, {
            treble_layout: { preset: trebleLayout },
            bass_layout: { preset: bassLayout },
            omr_engine: omrEngine
        });

        // Poll for completion
        await API.pollStatus(uploadResult.job_id, (status) => {
            updateProcessingStatus(status.message, status.progress);
        });

        // Get results
        updateProcessingStatus('Loading results...', 95);
        const results = await API.getResults(uploadResult.job_id);
        console.log('Results:', results);

        // Store results
        state.results = results;
        state.trebleLayout = results.treble_layout;
        state.bassLayout = results.bass_layout;

        // Render score with OSMD
        updateProcessingStatus('Rendering score...', 98);
        await renderScore(uploadResult.job_id);

        // Hide processing, show results
        elements.processingOverlay?.classList.add('hidden');
        showResults(results);

    } catch (error) {
        console.error('Processing error:', error);
        showError(error.message);
        elements.processingOverlay?.classList.add('hidden');
        elements.emptyState?.classList.remove('hidden');
        state.isProcessing = false;
    }
}

/**
 * Update processing status with progress bar and step indicators
 */
function updateProcessingStatus(message, progress) {
    if (elements.processingText) {
        elements.processingText.textContent = message;
    }
    if (elements.processingProgress) {
        elements.processingProgress.textContent = `${Math.round(progress)}%`;
    }

    // Update progress bar fill
    const progressFillElement = document.getElementById('progressFill');
    if (progressFillElement) {
        progressFillElement.style.width = `${progress}%`;
    }

    // Update step indicators based on progress
    const uploadStep = document.getElementById('step-upload');
    const omrStep = document.getElementById('step-omr');
    const renderStep = document.getElementById('step-render');

    // Reset all steps
    [uploadStep, omrStep, renderStep].forEach(step => {
        if (step) {
            step.classList.remove('active', 'completed');
        }
    });

    // Set active/completed states based on progress
    if (progress < 20) {
        // Uploading phase
        uploadStep?.classList.add('active');
    } else if (progress < 95) {
        // OMR processing phase
        uploadStep?.classList.add('completed');
        omrStep?.classList.add('active');
    } else {
        // Rendering phase
        uploadStep?.classList.add('completed');
        omrStep?.classList.add('completed');
        renderStep?.classList.add('active');
    }
}

/**
 * Render MusicXML string directly with OpenSheetMusicDisplay
 * @param {string} musicXmlString - MusicXML content as string
 */
async function renderScoreFromString(musicXmlString) {
    try {
        const osmdContainer = document.getElementById('osmd-container');
        if (!osmdContainer) {
            console.error('OSMD container not found');
            return;
        }

        // Clear existing content
        osmdContainer.innerHTML = '';

        // Initialize OSMD
        if (!OpenSheetMusicDisplay) {
            throw new Error('OpenSheetMusicDisplay not loaded');
        }

        const osmd = new OpenSheetMusicDisplay(osmdContainer, {
            autoResize: true,
            backend: 'svg',
            drawTitle: true
        });

        // Load and render from string
        await osmd.load(musicXmlString);
        osmd.render();

        console.log('Score rendered successfully from string');
    } catch (error) {
        console.error('Error rendering score:', error);
        throw error;
    }
}

/**
 * Render MusicXML score with OpenSheetMusicDisplay (from backend)
 */
async function renderScore(jobId) {
    try {
        const osmdContainer = document.getElementById('osmd-container');
        if (!osmdContainer) {
            console.error('OSMD container not found');
            return;
        }

        // Clear existing content
        osmdContainer.innerHTML = '';

        // Fetch MusicXML
        const musicXmlUrl = API.getMusicXMLUrl(jobId);
        const response = await fetch(musicXmlUrl);

        if (!response.ok) {
            throw new Error(`Failed to fetch MusicXML: ${response.statusText}`);
        }

        const musicXml = await response.text();

        // Use the common rendering function
        await renderScoreFromString(musicXml);

        console.log('Score rendered successfully from backend');
    } catch (error) {
        console.error('Error rendering score:', error);
        showError(`Failed to display score: ${error.message}`);
    }
}


/**
 * Show results
 */
function showResults(results) {
    // Show accordion panel and playback bar
    elements.accordionPanel?.classList.remove('hidden');
    elements.playbackBar?.classList.remove('hidden');

    // Render keyboards
    console.log('Rendering keyboards...', results);

    // Render treble keyboard
    if (results.treble_layout && results.treble_events) {
        renderTrebleKeyboard(
            elements.trebleKeyboard,
            results.treble_layout,
            results.treble_events
        );

        // Add click handlers for interactive testing
        addButtonClickHandlers(elements.trebleKeyboard, (button) => {
            console.log('Treble button clicked:', button);
        });
    }

    // Render bass keyboard
    if (results.bass_layout && results.bass_events) {
        renderBassKeyboard(
            elements.bassKeyboard,
            results.bass_layout,
            results.bass_events
        );

        addButtonClickHandlers(elements.bassKeyboard, (button) => {
            console.log('Bass button clicked:', button);
        });
    }

    // Update layout info
    if (elements.currentLayout && results.treble_layout) {
        elements.currentLayout.textContent = results.treble_layout.system.toUpperCase();
    }

    if (elements.layoutRange && results.treble_layout) {
        const buttons = results.treble_layout.buttons;
        if (buttons && buttons.length > 0) {
            const firstNote = buttons[0].note;
            const lastNote = buttons[buttons.length - 1].note;
            elements.layoutRange.textContent = `${firstNote}-${lastNote}`;
        }
    }

    state.isProcessing = false;
}

/**
 * Toggle settings panel
 */
function toggleSettingsPanel(e) {
    e.stopPropagation();
    elements.settingsPanel?.classList.toggle('open');
}

/**
 * Set active hand
 */
function setHand(hand) {
    state.currentHand = hand;

    // Update button states
    elements.toggleRight?.classList.toggle('active', hand === 'right' || hand === 'both');
    elements.toggleLeft?.classList.toggle('active', hand === 'left' || hand === 'both');
    elements.toggleBoth?.classList.toggle('active', hand === 'both');

    // Show/hide keyboards
    if (hand === 'right') {
        elements.trebleKeyboard.style.display = 'block';
        elements.bassKeyboard.style.display = 'none';
    } else if (hand === 'left') {
        elements.trebleKeyboard.style.display = 'none';
        elements.bassKeyboard.style.display = 'block';
    } else {
        elements.trebleKeyboard.style.display = 'block';
        elements.bassKeyboard.style.display = 'block';
    }
}

/**
 * Handle layout change
 */
async function handleLayoutChange() {
    // If we have current results, could re-fetch with new layouts
    console.log('Layout changed');
}

/**
 * Toggle playback
 */
function togglePlayback() {
    const isPlaying = elements.playIcon?.style.display === 'none';

    if (isPlaying) {
        // Pause
        elements.playIcon.style.display = 'block';
        elements.pauseIcon.style.display = 'none';
        console.log('Pausing playback');
    } else {
        // Play
        elements.playIcon.style.display = 'none';
        elements.pauseIcon.style.display = 'block';
        console.log('Starting playback');
    }
}

/**
 * Show error message
 */
function showError(message) {
    if (elements.errorText) {
        elements.errorText.textContent = message;
    }
    elements.errorToast?.classList.remove('hidden');

    // Auto-hide after 5 seconds
    setTimeout(hideError, 5000);
}

/**
 * Hide error message
 */
function hideError() {
    elements.errorToast?.classList.add('hidden');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Export for use in other modules
export { state, elements };
