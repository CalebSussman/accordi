/**
 * Note Name Renderer
 * Displays note names (e.g., "C4", "D#5") above notes in OSMD rendering
 */

export class NoteNameRenderer {
    constructor(osmdInstance) {
        this.osmd = osmdInstance;
        this.noteTextElements = [];
    }

    /**
     * Convert pitch data to note name string
     * @param {number} fundamentalNote - 0-11 (C to B)
     * @param {number} octave - Octave number (4 = middle C octave)
     * @param {number} accidental - -2=bb, -1=b, 0=natural, 1=#, 2=##
     * @returns {string} Note name (e.g., "C4", "F#3", "Bb5")
     */
    getNoteNameFromPitch(fundamentalNote, octave, accidental) {
        // Base note names (natural notes)
        const noteNames = ['C', 'D', 'E', 'F', 'G', 'A', 'B'];

        // Get the base note name (0=C, 1=D, 2=E, etc.)
        const baseName = noteNames[fundamentalNote % 7];

        // Handle accidentals
        let accidentalSymbol = '';
        if (accidental === -2) accidentalSymbol = 'bb';
        else if (accidental === -1) accidentalSymbol = 'b';
        else if (accidental === 1) accidentalSymbol = '#';
        else if (accidental === 2) accidentalSymbol = '##';

        return `${baseName}${accidentalSymbol}${octave}`;
    }

    /**
     * Render note names above all notes in the score
     */
    renderNoteNames() {
        console.log('[NoteNames] renderNoteNames() called');

        // Clear any existing labels first
        this.clearNoteNames();

        if (!this.osmd || !this.osmd.GraphicalMusicSheet) {
            console.warn('[NoteNames] OSMD instance not ready for note name rendering');
            return;
        }

        try {
            const container = document.getElementById('osmd-container');
            if (!container) {
                console.error('[NoteNames] OSMD container not found');
                return;
            }

            const svg = container.querySelector('svg');
            if (!svg) {
                console.error('[NoteNames] SVG element not found in OSMD container');
                return;
            }

            console.log('[NoteNames] Found SVG, creating label group');

            // Create a group for all note labels
            const labelGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            labelGroup.setAttribute('class', 'note-name-labels');
            svg.appendChild(labelGroup);

            const musicSheet = this.osmd.GraphicalMusicSheet;
            const zoom = this.osmd.zoom || 1.0;

            console.log(`[NoteNames] MusicSheet has ${musicSheet.MusicPages.length} pages`);

            // Iterate through all pages in the score
            for (const page of musicSheet.MusicPages) {
                console.log(`[NoteNames] Processing page with ${page.MusicSystems.length} systems`);

                for (const system of page.MusicSystems) {
                    for (const staffLine of system.StaffLines) {
                        for (const measure of staffLine.Measures) {
                            // Iterate through all staff entries in the measure
                            for (const staffEntry of measure.staffEntries) {
                                // Each staff entry can have multiple voice entries
                                for (const graphicalVoiceEntry of staffEntry.graphicalVoiceEntries) {
                                    if (!graphicalVoiceEntry.notes) continue;

                                    // Iterate through all notes in the voice entry
                                    for (const graphicalNote of graphicalVoiceEntry.notes) {
                                        this.addNoteLabel(labelGroup, graphicalNote, zoom);
                                    }
                                }
                            }
                        }
                    }
                }
            }

            console.log(`[NoteNames] ✅ Rendered ${this.noteTextElements.length} note labels`);
        } catch (error) {
            console.error('[NoteNames] Error rendering note names:', error);
        }
    }

    /**
     * Add a single note label to the SVG
     * @param {SVGElement} labelGroup - SVG group to append to
     * @param {object} graphicalNote - OSMD graphical note object
     * @param {number} zoom - Current zoom level
     */
    addNoteLabel(labelGroup, graphicalNote, zoom) {
        try {
            // Skip rest notes
            if (!graphicalNote.sourceNote || graphicalNote.sourceNote.isRest()) {
                return;
            }

            const pitch = graphicalNote.sourceNote.Pitch;
            if (!pitch) return;

            // Get note name
            const noteName = this.getNoteNameFromPitch(
                pitch.FundamentalNote,
                pitch.Octave,
                pitch.Accidental || 0
            );

            // Get position from graphical note
            const position = graphicalNote.PositionAndShape.RelativePosition;
            const boundingBox = graphicalNote.PositionAndShape.BoundingRectangle;

            // Calculate pixel coordinates (OSMD uses units, multiply by 10 * zoom)
            const unitToPixel = 10 * zoom;
            const x = position.x * unitToPixel;
            const y = position.y * unitToPixel - 15; // Offset above the note

            // Create SVG text element
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', x);
            text.setAttribute('y', y);
            text.setAttribute('class', 'note-name-label');
            text.setAttribute('fill', '#d4af37'); // Gold color
            text.setAttribute('font-size', `${9 * zoom}px`);
            text.setAttribute('font-family', 'system-ui, -apple-system, sans-serif');
            text.setAttribute('font-weight', '500');
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('pointer-events', 'none');
            text.textContent = noteName;

            labelGroup.appendChild(text);
            this.noteTextElements.push(text);
        } catch (error) {
            console.error('Error adding note label:', error);
        }
    }

    /**
     * Clear all note name labels from the display
     */
    clearNoteNames() {
        console.log(`[NoteNames] Clearing ${this.noteTextElements.length} note labels`);

        // Remove all individual text elements
        this.noteTextElements.forEach(el => {
            if (el.parentNode) {
                el.parentNode.removeChild(el);
            }
        });
        this.noteTextElements = [];

        // Also remove the label group if it exists
        const container = document.getElementById('osmd-container');
        if (container) {
            const labelGroup = container.querySelector('.note-name-labels');
            if (labelGroup && labelGroup.parentNode) {
                labelGroup.parentNode.removeChild(labelGroup);
            }
        }

        console.log('[NoteNames] ✅ Cleared all note labels');
    }

    /**
     * Update note name positions after zoom or spacing change
     * This is equivalent to re-rendering
     */
    updatePositions() {
        this.renderNoteNames();
    }
}
