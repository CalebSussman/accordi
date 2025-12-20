/**
 * Akkordio - API Client
 * Handles all communication with FastAPI backend
 */

const API_BASE_URL = 'https://akkordio.onrender.com';

/**
 * Upload PDF file to backend
 * @param {File} file - PDF file to upload
 * @returns {Promise<{job_id: string, filename: string, size: number}>}
 */
export async function uploadPDF(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
    }

    return await response.json();
}

/**
 * Start processing for uploaded file
 * @param {string} jobId - Job ID from upload
 * @param {Object} config - Processing configuration (treble_layout, bass_layout, omr_engine, options)
 * @returns {Promise<{job_id: string, status: string, progress: number}>}
 */
export async function startProcessing(jobId, config = {}) {
    const response = await fetch(`${API_BASE_URL}/process/${jobId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            treble_layout: config.treble_layout?.preset || 'c_system_5row_standard',
            bass_layout: config.bass_layout?.preset || 'stradella_120_standard',
            omr_engine: config.omr_engine || 'oemer',
            options: config.options || {}
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Processing failed to start');
    }

    return await response.json();
}

/**
 * Get processing status
 * @param {string} jobId - Job ID
 * @returns {Promise<{job_id: string, status: string, progress: number, message: string}>}
 */
export async function getStatus(jobId) {
    const response = await fetch(`${API_BASE_URL}/status/${jobId}`);

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get status');
    }

    return await response.json();
}

/**
 * Poll status until processing is complete
 * @param {string} jobId - Job ID
 * @param {Function} onProgress - Callback for progress updates
 * @returns {Promise<{status: string}>}
 */
export async function pollStatus(jobId, onProgress) {
    return new Promise((resolve, reject) => {
        const pollInterval = setInterval(async () => {
            try {
                const status = await getStatus(jobId);

                // Call progress callback
                if (onProgress) {
                    onProgress(status);
                }

                // Check if completed or failed
                if (status.status === 'completed') {
                    clearInterval(pollInterval);
                    resolve(status);
                } else if (status.status === 'failed') {
                    clearInterval(pollInterval);
                    reject(new Error(status.error || 'Processing failed'));
                }
            } catch (error) {
                clearInterval(pollInterval);
                reject(error);
            }
        }, 1000); // Poll every second
    });
}

/**
 * Get processed results
 * @param {string} jobId - Job ID
 * @returns {Promise<{treble_events: Array, bass_events: Array, treble_layout: Object, bass_layout: Object}>}
 */
export async function getResults(jobId) {
    const response = await fetch(`${API_BASE_URL}/results/${jobId}`);

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get results');
    }

    return await response.json();
}

/**
 * Get list of available layout presets
 * @returns {Promise<{treble: Array, bass: Array}>}
 */
export async function getLayoutPresets() {
    const response = await fetch(`${API_BASE_URL}/layouts/presets`);

    if (!response.ok) {
        throw new Error('Failed to fetch layout presets');
    }

    return await response.json();
}

/**
 * Get specific preset layout
 * @param {string} presetName - Preset name (e.g., 'c_system_5row')
 * @returns {Promise<Object>} - Layout configuration
 */
export async function getPresetLayout(presetName) {
    const response = await fetch(`${API_BASE_URL}/layouts/preset/${presetName}`);

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch layout');
    }

    return await response.json();
}

/**
 * Generate custom layout
 * @param {Object} config - Layout configuration
 * @returns {Promise<Object>} - Generated layout
 */
export async function generateLayout(config) {
    const response = await fetch(`${API_BASE_URL}/layouts/generate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to generate layout');
    }

    return await response.json();
}

/**
 * Get MIDI file URL
 * @param {string} jobId - Job ID
 * @returns {string} - MIDI file URL
 */
export function getMidiUrl(jobId) {
    return `${API_BASE_URL}/midi/${jobId}`;
}

/**
 * Get MusicXML file URL
 * @param {string} jobId - Job ID
 * @returns {string} - MusicXML file URL
 */
export function getMusicXMLUrl(jobId) {
    return `${API_BASE_URL}/musicxml/${jobId}`;
}

/**
 * Upload MusicXML file directly (bypasses OMR processing)
 * @param {File} file - MusicXML file (.mxl, .musicxml, .xml)
 * @returns {Promise<{success: boolean, job_id: string, musicxml_url: string}>}
 */
export async function uploadMusicXML(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload_musicxml`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'MusicXML upload failed');
    }

    return await response.json();
}

/**
 * Health check
 * @returns {Promise<{status: string}>}
 */
export async function healthCheck() {
    const response = await fetch(`${API_BASE_URL}/health`);
    return await response.json();
}
