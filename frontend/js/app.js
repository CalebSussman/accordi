/**
 * Akkordio Main Application Controller
 *
 * Handles application initialization, state management, and coordination
 * between upload, processing, and visualization modules.
 */

// Application Configuration
const CONFIG = {
    apiBaseUrl: 'http://localhost:8000',
    maxFileSize: 10 * 1024 * 1024, // 10MB
    pollInterval: 1000, // 1 second
    supportedFormats: ['.pdf']
};

// Application State
const state = {
    currentJobId: null,
    currentFile: null,
    selectedTrebleLayout: 'c_system_5row_standard',
    selectedBassLayout: 'stradella_120_standard',
    isProcessing: false,
    processingData: null
};

// DOM Elements
const elements = {
    uploadArea: document.getElementById('uploadArea'),
    fileInput: document.getElementById('fileInput'),
    fileInfo: document.getElementById('fileInfo'),
    fileName: document.getElementById('fileName'),
    fileSize: document.getElementById('fileSize'),
    trebleLayout: document.getElementById('trebleLayout'),
    bassLayout: document.getElementById('bassLayout'),
    processBtn: document.getElementById('processBtn'),
    progressSection: document.getElementById('progressSection'),
    progressFill: document.getElementById('progressFill'),
    progressText: document.getElementById('progressText'),
    visualizationSection: document.getElementById('visualizationSection'),
    playBtn: document.getElementById('playBtn'),
    pauseBtn: document.getElementById('pauseBtn'),
    stopBtn: document.getElementById('stopBtn'),
    tempoSlider: document.getElementById('tempoSlider'),
    tempoValue: document.getElementById('tempoValue'),
    currentMeasure: document.getElementById('currentMeasure'),
    keySignature: document.getElementById('keySignature'),
    timeSignature: document.getElementById('timeSignature'),
    errorMessage: document.getElementById('errorMessage'),
    errorText: document.getElementById('errorText'),
    closeError: document.getElementById('closeError')
};

/**
 * Initialize the application
 */
function init() {
    setupEventListeners();
    checkBackendConnection();
}

/**
 * Set up all event listeners
 */
function setupEventListeners() {
    // File upload events
    elements.uploadArea.addEventListener('click', () => elements.fileInput.click());
    elements.uploadArea.addEventListener('dragover', handleDragOver);
    elements.uploadArea.addEventListener('dragleave', handleDragLeave);
    elements.uploadArea.addEventListener('drop', handleDrop);
    elements.fileInput.addEventListener('change', handleFileSelect);

    // Layout selection events
    elements.trebleLayout.addEventListener('change', (e) => {
        state.selectedTrebleLayout = e.target.value;
    });
    elements.bassLayout.addEventListener('change', (e) => {
        state.selectedBassLayout = e.target.value;
    });

    // Process button
    elements.processBtn.addEventListener('click', handleProcess);

    // Playback controls
    elements.playBtn.addEventListener('click', handlePlay);
    elements.pauseBtn.addEventListener('click', handlePause);
    elements.stopBtn.addEventListener('click', handleStop);

    // Tempo control
    elements.tempoSlider.addEventListener('input', (e) => {
        elements.tempoValue.textContent = e.target.value;
    });

    // Error message close
    elements.closeError.addEventListener('click', hideError);
}

/**
 * Check backend API connection
 */
async function checkBackendConnection() {
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/health`);
        if (!response.ok) {
            throw new Error('Backend not responding');
        }
    } catch (error) {
        showError('Cannot connect to backend server. Please ensure it is running on port 8000.');
    }
}

/**
 * Handle drag over event
 */
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    elements.uploadArea.classList.add('drag-over');
}

/**
 * Handle drag leave event
 */
function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    elements.uploadArea.classList.remove('drag-over');
}

/**
 * Handle file drop event
 */
function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    elements.uploadArea.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

/**
 * Handle file selection from input
 */
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

/**
 * Process selected file
 */
function handleFile(file) {
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showError('Please select a PDF file.');
        return;
    }

    // Validate file size
    if (file.size > CONFIG.maxFileSize) {
        showError(`File size exceeds 10MB limit. Selected file: ${formatFileSize(file.size)}`);
        return;
    }

    // Update state
    state.currentFile = file;

    // Update UI
    elements.fileName.textContent = file.name;
    elements.fileSize.textContent = formatFileSize(file.size);
    elements.fileInfo.style.display = 'block';
    elements.processBtn.disabled = false;
}

/**
 * Handle process button click
 */
async function handleProcess() {
    if (!state.currentFile) {
        showError('Please select a file first.');
        return;
    }

    if (state.isProcessing) {
        return;
    }

    state.isProcessing = true;
    elements.processBtn.disabled = true;

    try {
        // Upload file
        showProgress(0, 'Uploading file...');
        const jobId = await uploadFile(state.currentFile);
        state.currentJobId = jobId;

        // Start processing
        showProgress(10, 'Starting processing...');
        await startProcessing(jobId);

        // Poll for status
        await pollProcessingStatus(jobId);

    } catch (error) {
        showError(error.message || 'An error occurred during processing.');
        resetProcessing();
    }
}

/**
 * Upload file to backend
 */
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${CONFIG.apiBaseUrl}/upload`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
    }

    const data = await response.json();
    return data.job_id;
}

/**
 * Start processing
 */
async function startProcessing(jobId) {
    const response = await fetch(`${CONFIG.apiBaseUrl}/process/${jobId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            treble_layout: state.selectedTrebleLayout,
            bass_layout: state.selectedBassLayout,
            options: {}
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Processing failed to start');
    }

    return await response.json();
}

/**
 * Poll processing status
 */
async function pollProcessingStatus(jobId) {
    return new Promise((resolve, reject) => {
        const interval = setInterval(async () => {
            try {
                const response = await fetch(`${CONFIG.apiBaseUrl}/status/${jobId}`);

                if (!response.ok) {
                    clearInterval(interval);
                    reject(new Error('Failed to check status'));
                    return;
                }

                const status = await response.json();
                showProgress(status.progress, status.message);

                if (status.status === 'completed') {
                    clearInterval(interval);
                    await loadResults(jobId);
                    resolve();
                } else if (status.status === 'failed') {
                    clearInterval(interval);
                    reject(new Error(status.error || 'Processing failed'));
                }
            } catch (error) {
                clearInterval(interval);
                reject(error);
            }
        }, CONFIG.pollInterval);
    });
}

/**
 * Load processing results
 */
async function loadResults(jobId) {
    const response = await fetch(`${CONFIG.apiBaseUrl}/results/${jobId}`);

    if (!response.ok) {
        throw new Error('Failed to load results');
    }

    const data = await response.json();
    state.processingData = data;

    // Hide progress, show visualization
    elements.progressSection.style.display = 'none';
    elements.visualizationSection.style.display = 'block';

    // Update metadata display
    if (data.metadata) {
        if (data.metadata.key_signature) {
            elements.keySignature.textContent = data.metadata.key_signature;
        }
        if (data.metadata.time_signature) {
            elements.timeSignature.textContent = data.metadata.time_signature;
        }
    }

    // TODO: Render keyboards and prepare playback
    // This will be implemented in subsequent modules
}

/**
 * Show progress
 */
function showProgress(percentage, message) {
    elements.progressSection.style.display = 'block';
    elements.progressFill.style.width = `${percentage}%`;
    elements.progressText.textContent = message;
}

/**
 * Reset processing state
 */
function resetProcessing() {
    state.isProcessing = false;
    elements.processBtn.disabled = false;
    elements.progressSection.style.display = 'none';
}

/**
 * Handle play button
 */
function handlePlay() {
    elements.playBtn.style.display = 'none';
    elements.pauseBtn.style.display = 'inline-flex';
    // TODO: Implement playback
}

/**
 * Handle pause button
 */
function handlePause() {
    elements.pauseBtn.style.display = 'none';
    elements.playBtn.style.display = 'inline-flex';
    // TODO: Implement pause
}

/**
 * Handle stop button
 */
function handleStop() {
    elements.pauseBtn.style.display = 'none';
    elements.playBtn.style.display = 'inline-flex';
    elements.currentMeasure.textContent = '1';
    // TODO: Implement stop
}

/**
 * Show error message
 */
function showError(message) {
    elements.errorText.textContent = message;
    elements.errorMessage.style.display = 'flex';

    // Auto-hide after 5 seconds
    setTimeout(hideError, 5000);
}

/**
 * Hide error message
 */
function hideError() {
    elements.errorMessage.style.display = 'none';
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes < 1024) {
        return `${bytes} B`;
    } else if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    } else {
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }
}

// Initialize application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
