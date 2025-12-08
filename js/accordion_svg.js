/**
 * Akkordio - SVG Keyboard Renderer
 * Dynamically generates accordion keyboard visualizations
 */

/**
 * Render treble (chromatic) keyboard
 * @param {SVGElement} svg - Target SVG element
 * @param {Object} layout - Layout configuration from backend
 * @param {Array} events - Mapped events (optional)
 */
export function renderTrebleKeyboard(svg, layout, events = []) {
    // Clear existing content
    svg.innerHTML = '';

    const { buttons, geometry, rows, columns } = layout;
    const {
        buttonRadius = 8,
        rowSpacing = 15,
        columnSpacing = 18,
        staggered = true,
        staggerOffset = 9
    } = geometry || {};

    // Calculate SVG dimensions
    const padding = 20;
    const width = columns * columnSpacing + padding * 2;
    const height = rows * rowSpacing + padding * 2;

    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);

    // Create active notes map for highlighting
    const activeNotes = new Set();
    events.forEach(event => {
        if (event.selected_position) {
            const key = `${event.selected_position.row}-${event.selected_position.column}`;
            activeNotes.add(key);
        }
    });

    // Render buttons
    buttons.forEach(button => {
        const { row, column, note, midi, color } = button;

        // Calculate position
        const x = padding + column * columnSpacing + (staggered && row % 2 === 1 ? staggerOffset : 0);
        const y = padding + row * rowSpacing;

        // Check if active
        const isActive = activeNotes.has(`${row}-${column}`);

        // Create button group
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.classList.add('cba-button');
        g.classList.add(color === 'white' || !color ? 'white' : 'black');
        if (isActive) g.classList.add('active');
        g.setAttribute('data-row', row);
        g.setAttribute('data-column', column);
        g.setAttribute('data-midi', midi);
        g.setAttribute('data-note', note);

        // Create button circle
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.classList.add('button-face');
        circle.setAttribute('cx', x);
        circle.setAttribute('cy', y);
        circle.setAttribute('r', buttonRadius);

        // Create label (note name without octave)
        const noteBase = note.replace(/\d+$/, '');
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.classList.add('button-label');
        text.setAttribute('x', x);
        text.setAttribute('y', y + 3); // Center vertically
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dominant-baseline', 'middle');
        text.textContent = noteBase;

        // Add tooltip
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = `${note} (MIDI ${midi})`;

        g.appendChild(circle);
        g.appendChild(text);
        g.appendChild(title);
        svg.appendChild(g);
    });
}

/**
 * Render bass keyboard (Stradella or Free-bass)
 * @param {SVGElement} svg - Target SVG element
 * @param {Object} layout - Layout configuration from backend
 * @param {Array} events - Mapped events (optional)
 */
export function renderBassKeyboard(svg, layout, events = []) {
    // Clear existing content
    svg.innerHTML = '';

    const { buttons, geometry, rows, columns, system } = layout;

    if (system === 'stradella') {
        renderStradellaKeyboard(svg, layout, events);
    } else {
        // Free-bass uses same rendering as treble
        renderTrebleKeyboard(svg, layout, events);
    }
}

/**
 * Render Stradella bass keyboard
 * @param {SVGElement} svg - Target SVG element
 * @param {Object} layout - Layout configuration
 * @param {Array} events - Mapped events
 */
function renderStradellaKeyboard(svg, layout, events = []) {
    const { buttons, geometry, rows, columns } = layout;
    const {
        buttonRadius = 6,
        rowSpacing = 12,
        columnSpacing = 14,
        staggered = false
    } = geometry || {};

    // Calculate SVG dimensions
    const padding = 20;
    const width = columns * columnSpacing + padding * 2;
    const height = rows * rowSpacing + padding * 2;

    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);

    // Create active notes map
    const activeButtons = new Set();
    events.forEach(event => {
        if (event.button_position) {
            const key = `${event.button_position.row}-${event.button_position.column}`;
            activeButtons.add(key);
        }
    });

    // Row type labels
    const rowLabels = {
        0: 'Counter',
        1: 'Root',
        2: 'Major',
        3: 'Minor',
        4: '7th',
        5: 'Dim'
    };

    // Render buttons
    buttons.forEach(button => {
        const { row, column, type, label, note } = button;

        // Calculate position
        const x = padding + column * columnSpacing;
        const y = padding + row * rowSpacing;

        // Check if active
        const isActive = activeButtons.has(`${row}-${column}`);

        // Create button group
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.classList.add('bass-button');
        g.classList.add(type);
        if (isActive) g.classList.add('active');
        g.setAttribute('data-row', row);
        g.setAttribute('data-column', column);
        g.setAttribute('data-type', type);

        // Create button circle
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.classList.add('button-face');
        circle.setAttribute('cx', x);
        circle.setAttribute('cy', y);
        circle.setAttribute('r', buttonRadius);

        // Create label
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.classList.add('button-label');
        text.setAttribute('x', x);
        text.setAttribute('y', y + 2);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dominant-baseline', 'middle');
        text.setAttribute('font-size', '8px');
        text.textContent = label || note;

        // Add tooltip
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = `${label || note} (${rowLabels[row] || 'Row ' + row})`;

        g.appendChild(circle);
        g.appendChild(text);
        g.appendChild(title);
        svg.appendChild(g);
    });
}

/**
 * Highlight specific buttons on keyboard
 * @param {SVGElement} svg - SVG element
 * @param {Array} positions - Array of {row, column} positions
 */
export function highlightButtons(svg, positions) {
    // Remove existing highlights
    svg.querySelectorAll('.cba-button, .bass-button').forEach(btn => {
        btn.classList.remove('active', 'suggested');
    });

    // Add new highlights
    positions.forEach(({ row, column, state = 'active' }) => {
        const button = svg.querySelector(
            `[data-row="${row}"][data-column="${column}"]`
        );
        if (button) {
            button.classList.add(state); // 'active' or 'suggested'
        }
    });
}

/**
 * Add click handlers to buttons
 * @param {SVGElement} svg - SVG element
 * @param {Function} callback - Callback function (button) => {}
 */
export function addButtonClickHandlers(svg, callback) {
    svg.querySelectorAll('.cba-button, .bass-button').forEach(button => {
        button.style.cursor = 'pointer';
        button.addEventListener('click', () => {
            const row = parseInt(button.getAttribute('data-row'));
            const column = parseInt(button.getAttribute('data-column'));
            const midi = button.getAttribute('data-midi');
            const note = button.getAttribute('data-note');
            const type = button.getAttribute('data-type');

            callback({
                row,
                column,
                midi: midi ? parseInt(midi) : null,
                note,
                type
            });
        });
    });
}

/**
 * Animate button press
 * @param {SVGElement} svg - SVG element
 * @param {number} row - Button row
 * @param {number} column - Button column
 */
export function animateButtonPress(svg, row, column) {
    const button = svg.querySelector(
        `[data-row="${row}"][data-column="${column}"]`
    );

    if (button) {
        button.classList.add('gold-pulse');
        setTimeout(() => {
            button.classList.remove('gold-pulse');
        }, 600);
    }
}

/**
 * Clear all highlights
 * @param {SVGElement} svg - SVG element
 */
export function clearHighlights(svg) {
    svg.querySelectorAll('.cba-button, .bass-button').forEach(btn => {
        btn.classList.remove('active', 'suggested');
    });
}

/**
 * Get button at position
 * @param {SVGElement} svg - SVG element
 * @param {number} row - Row number
 * @param {number} column - Column number
 * @returns {Object|null} - Button data or null
 */
export function getButtonAt(svg, row, column) {
    const button = svg.querySelector(
        `[data-row="${row}"][data-column="${column}"]`
    );

    if (!button) return null;

    return {
        row: parseInt(button.getAttribute('data-row')),
        column: parseInt(button.getAttribute('data-column')),
        midi: button.getAttribute('data-midi') ? parseInt(button.getAttribute('data-midi')) : null,
        note: button.getAttribute('data-note'),
        type: button.getAttribute('data-type')
    };
}
