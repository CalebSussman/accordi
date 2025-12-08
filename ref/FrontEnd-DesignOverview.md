# Akkordio Implementation Plan for Claude Code

## Core Design Philosophy

The score is the foundational layer (like paper on a desk). All UI elements float above it using liquid glass design with **squircle shapes** (rounded rectangles with continuous curvature, not standard border-radius).

---

## 1. Layer Hierarchy (Bottom to Top)

### Layer 0: Background (Ambient)
- Subtle texture or gradient
- Minimal visual weight
- Just enough to separate score from viewport edges

### Layer 1: Score (Base - OSMD Container)
- **Pure white background** (light mode) or **off-white/cream** (#fafaf8)
- **Dark gray/black** (#1a1a1a) background (dark mode)
- Full-width, full-height container
- No borders, no shadows - completely flat
- OSMD renders directly here
- This is the "paper" - everything else floats on top

### Layer 2: Floating UI Elements (Liquid Glass)
All UI elements use:
- **Frosted glass effect**: `backdrop-filter: blur(40px) saturate(180%)`
- **Squircle shapes**: Use CSS with `border-radius: 20px` or SVG masks for true squircles
- **Subtle shadows**: Multi-layer shadows for depth
- **Semi-transparent backgrounds**
- **Gold accent borders** (1px, low opacity)

---

## 2. Top Navigation Bar (Floating Squircle)

### Design Specs:
- **Shape**: Wide squircle (continuous curve, not sharp rounded corners)
- **Position**: Fixed top, centered, with 16-24px margin from viewport edges
- **Width**: Max-width 1400px, responsive
- **Padding**: 12-16px vertical, 24px horizontal

### Glass Properties (Light Mode):
```css
background: rgba(255, 255, 255, 0.7)
backdrop-filter: blur(40px) saturate(180%)
border: 1px solid rgba(212, 175, 55, 0.15)
box-shadow: 
  0 8px 32px rgba(0, 0, 0, 0.06),
  0 1px 0 rgba(255, 255, 255, 0.8) inset,
  0 0 0 1px rgba(212, 175, 55, 0.05)
```

### Glass Properties (Dark Mode):
```css
background: rgba(20, 20, 20, 0.7)
backdrop-filter: blur(40px) saturate(180%)
border: 1px solid rgba(212, 175, 55, 0.25)
box-shadow: 
  0 8px 32px rgba(0, 0, 0, 0.4),
  0 1px 0 rgba(212, 175, 55, 0.1) inset,
  0 0 0 1px rgba(212, 175, 55, 0.05)
```

### Contents:
- Left: "Akkordio" logo (gold gradient text)
- Right: "Load Previous" button, "Upload New Score" button (gold primary), Settings gear icon
- Settings panel expands downward as separate floating squircle

---

## 3. Accordion Panel (Floating Squircle)

### Design Specs:
- **Shape**: Squircle with continuous curve
- **Modes**: 
  - **Split mode**: Static position on right side or below (responsive)
  - **Floating mode**: Draggable, resizable, positioned over score
- **Padding**: 24-32px
- **Border-radius**: 24px (or true squircle with CSS/SVG)

### Glass Properties:
Same as nav bar but with adjusted opacity:
```css
Light mode: rgba(255, 255, 255, 0.85)
Dark mode: rgba(20, 20, 20, 0.9)
```

### Header (Draggable):
- Drag indicator (three dots in gold)
- "Right Hand" / "Left Hand" / "Both" title
- Hand toggle (Right/Left/Both buttons)
- Cursor: `grab` when hovering, `grabbing` when dragging

### Body:
- CBA keyboard centered
- White buttons (chromatic): Pearl white gradients
- Black buttons (incidentals): Deep black gradients
- Active state: Gold gradient glow
- Suggested state: Subtle gold tint

---

## 4. Playback Bar (Floating Squircle)

### Design Specs:
- **Shape**: Wide squircle at bottom
- **Position**: Fixed bottom, centered, 16-24px margin from edges
- **Width**: Max-width 1400px
- **Padding**: 16-20px vertical, 24px horizontal

### Glass Properties:
Same multi-layer approach as nav bar

### Contents:
- Gold play/pause button (circular, 52px)
- Progress bar with gold fill
- Time stamps (tabular-nums font)
- Tempo display (♩ = 120)

---

## 5. Theme System (Light & Dark Mode)

### Light Mode Palette:
```css
--bg-ambient: #f5f5f7
--score-bg: #ffffff
--glass-bg: rgba(255, 255, 255, 0.7)
--glass-border: rgba(212, 175, 55, 0.15)
--text-primary: #1d1d1f
--text-secondary: #86868b
--gold-primary: #d4af37
--gold-secondary: #b8860b
--gold-highlight: #f4d03f
--button-white: linear-gradient(145deg, #ffffff, #f5f5f5)
--button-black: linear-gradient(145deg, #3d3d3f, #2d2d2f)
--shadow-soft: rgba(0, 0, 0, 0.06)
--shadow-medium: rgba(0, 0, 0, 0.12)
```

### Dark Mode Palette:
```css
--bg-ambient: #0a0a0a
--score-bg: #1a1a1a
--glass-bg: rgba(20, 20, 20, 0.7)
--glass-border: rgba(212, 175, 55, 0.25)
--text-primary: #ffffff
--text-secondary: #999999
--gold-primary: #d4af37
--gold-secondary: #b8860b
--gold-highlight: #f4d03f
--button-white: linear-gradient(145deg, #ffffff, #f0f0f0)
--button-black: linear-gradient(145deg, #2d2d2f, #0a0a0a)
--shadow-soft: rgba(0, 0, 0, 0.3)
--shadow-medium: rgba(0, 0, 0, 0.5)
```

### Toggle Implementation:
- Add theme toggle button in settings panel
- Use `data-theme="light"` or `data-theme="dark"` on `<html>` element
- CSS variables update automatically
- Save preference to localStorage

---

## 6. OSMD Integration

### Installation:
```bash
npm install opensheetmusicdisplay
```

### Basic Setup:
```javascript
import { OpenSheetMusicDisplay } from 'opensheetmusicdisplay';

// Initialize
const osmd = new OpenSheetMusicDisplay('score-container', {
  autoResize: true,
  backend: 'svg',
  drawTitle: false,
  drawComposer: false,
  drawingParameters: 'compact'
});

// Load MusicXML
await osmd.load('/path/to/musicxml.xml');
osmd.render();

// Cursor for playback sync
osmd.cursor.show();
osmd.cursor.next(); // Advance during MIDI playback
```

### Styling OSMD Output:
```css
#score-container {
  width: 100%;
  height: 100%;
  background: var(--score-bg);
  padding: 60px 80px;
  overflow: auto;
}

/* OSMD SVG styling */
#score-container svg {
  max-width: 100%;
  height: auto;
}
```

### Cursor Sync with MIDI:
- Listen to MIDI events
- Call `osmd.cursor.next()` on each note
- Highlight current measure with gold tint overlay

---

## 7. Squircle Implementation

### Option A: CSS (Simple)
```css
.squircle {
  border-radius: 20px; /* Approximation */
}
```

### Option B: True Squircle (SVG Mask)
```css
.squircle {
  -webkit-mask-image: url('data:image/svg+xml,...');
  mask-image: url('data:image/svg+xml,...');
}
```

Use **Option A** for speed, **Option B** for pixel-perfect Apple-style squircles.

---

## 8. Draggable & Resizable Panel

### Draggable (Floating Mode Only):
```javascript
let isDragging = false;
let startX, startY, offsetX, offsetY;

header.addEventListener('mousedown', (e) => {
  if (!isFloatingMode) return;
  isDragging = true;
  startX = e.clientX - offsetX;
  startY = e.clientY - offsetY;
});

document.addEventListener('mousemove', (e) => {
  if (!isDragging) return;
  offsetX = e.clientX - startX;
  offsetY = e.clientY - startY;
  panel.style.transform = `translate3d(${offsetX}px, ${offsetY}px, 0)`;
});

document.addEventListener('mouseup', () => {
  isDragging = false;
});
```

### Resizable (CSS):
```css
.accordion-panel.floating {
  resize: both;
  overflow: auto;
  min-width: 350px;
  max-width: 600px;
  min-height: 400px;
}
```

---

## 9. Layout Toggle (Split vs Floating)

### Split Mode:
- Desktop: Score 60%, Accordion 40% (side-by-side)
- Tablet: Stacked vertically
- No dragging/resizing

### Floating Mode:
- Accordion panel absolutely positioned over score
- Draggable by header
- Resizable with CSS `resize: both`
- Initial position: top-right with 40px margin

### Toggle Buttons:
- Two buttons: "Split View" | "Floating View"
- Active state: Gold background
- Located top-right below nav bar

---

## 10. Responsive Breakpoints

```css
/* Desktop: 1200px+ */
Split mode: Side-by-side
Floating mode: Full draggable

/* Tablet: 768px - 1199px */
Split mode: Stacked vertical
Floating mode: Disabled (auto-stack)

/* Mobile: < 768px */
Always stacked
Accordion panel full-width
No floating mode
```

---

## 11. Animations & Transitions

### Button Press:
```css
@keyframes goldPulse {
  0% { transform: scale(1); }
  50% { 
    transform: scale(1.15); 
    box-shadow: 0 0 30px rgba(212, 175, 55, 0.8); 
  }
  100% { transform: scale(1.1); }
}
```

### Panel Transitions:
```css
.accordion-panel {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

### Glass Shimmer (Subtle):
```css
@keyframes shimmer {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}
```

---

## 12. File Structure

```
frontend/
├── index.html
├── css/
│   ├── variables.css       # Theme variables
│   ├── base.css            # Reset, typography
│   ├── glass.css           # Liquid glass components
│   ├── score.css           # OSMD container styles
│   ├── accordion.css       # CBA keyboard styles
│   └── responsive.css      # Media queries
├── js/
│   ├── app.js              # Main app logic
│   ├── osmd-loader.js      # OSMD integration
│   ├── theme-toggle.js     # Light/dark mode
│   ├── draggable.js        # Drag functionality
│   ├── midi-player.js      # Playback sync
│   └── api.js              # Backend communication
└── assets/
    └── layouts/            # JSON layout files
```

---

## 13. Key Implementation Notes

1. **Score as foundation**: OSMD container has no visual chrome - just content
2. **All UI floats**: Nav, accordion panel, playback bar are separate glass layers
3. **Squircles everywhere**: Consistent shape language (20-24px radius or SVG)
4. **Gold accents only**: No purple, pink, or other colors
5. **Theme-aware**: Every element respects light/dark mode
6. **Touch-friendly**: 44px minimum tap targets for iPad
7. **Smooth performance**: Use `transform` for animations, not position/margins
8. **OSMD cursor sync**: Update on every MIDI note event

---

## 14. Priority Order for Implementation

1. Set up theme system (CSS variables, toggle)
2. Create base score container (OSMD placeholder)
3. Build floating nav bar (squircle glass)
4. Implement accordion panel (glass, draggable)
5. Add playback bar (glass, MIDI controls)
6. Integrate OSMD (load MusicXML, render)
7. Connect MIDI playback with cursor
8. Add CBA button mapping logic
9. Polish animations and interactions
10. Test responsive behavior

---

## Design Rules (CRITICAL)

### Absolutely NO Emojis
- Use Unicode musical symbols only (𝄞, 𝄢, ♯, ♩)
- Use SVG icons for UI elements
- Use text labels where appropriate
- Never use emoji characters anywhere in the frontend

### Color Palette
- **Primary**: Black, White, Gold only
- **Gold shades**: #d4af37 (primary), #b8860b (secondary), #f4d03f (highlight)
- **No other accent colors**: No purple, pink, blue, etc.
- **Grayscale**: For non-gold elements only

### Glass Effect Standards
- **Blur**: Always 40px minimum
- **Saturation**: 180%
- **Opacity**: 0.7-0.9 depending on element
- **Borders**: Gold tinted, 1px, low opacity (0.15-0.25)
- **Shadows**: Multi-layer for depth

### Button States
- **White buttons (chromatic)**: Pearl white with realistic gradients
- **Black buttons (incidentals)**: Deep black with subtle highlights
- **Active**: Gold gradient (#d4af37 → #f4d03f) with glow
- **Suggested**: Subtle gold tint
- **Hover**: Slight lift (translateY -2px)

### Typography
- **Font**: -apple-system, SF Pro Display/Text
- **Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
- **Sizes**: Responsive, minimum 11px for small text
- **Numbers**: Use `font-variant-numeric: tabular-nums` for time displays

---

**Ready to hand this to Claude Code for implementation!**