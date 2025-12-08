# Akkordio Dynamic Keyboard Layout System

## Overview

Akkordio does not rely on static JSON files for each accordion keyboard layout. Instead, it uses a **dynamic layout generator** that can produce any treble, free-bass, or Stradella system automatically based on a few inputs:

- **System type** (C-system, B-system, free-bass, Stradella, etc.)
- **Number of rows and columns**
- **Starting MIDI note**
- **Chromatic intervals for rows and columns**
- **Geometric properties (stagger, spacing)**
- **Color strategy (pitch-class colors, finger colors, etc.)**

This gives Akkordio the flexibility to support **every accordion variant in the world** without maintaining hundreds of static layout files.

---

## 1. Dynamic Chromatic Systems (C-System, B-System, Free-Bass)

### Core Principle
Chromatic layouts follow predictable interval patterns. The generator constructs the keyboard by applying:

```
note = startMidi + rowOffset[row] + colOffset[column]
```

### Example: C-System Intervals

- Row intervals (in semitones):  
  `rowOffsets = [0, +1, +2, +3, +4]`
- Column offset:  
  `colOffset = column * 2` (each column = whole tone)

### Example: B-System Intervals

- Row intervals:  
  `rowOffsets = [0, +2, +4, +6, +8]`
- Columns alternate:  
  `colOffset = column % 2 === 0 ? 1 : 2`

### Free-Bass
Free-bass **uses the same logic as the treble system**, but simply starts at a lower register (e.g., C1 instead of C3).

---

## 2. Stradella Generator (Algorithmic)

Stradella is not chromatic. It follows musical relationships:

- X-axis: circle of fifths  
- Y-axis rows:
  - Counterbass = major third above root
  - Root bass
  - Major chord (root M3 P5)
  - Minor chord (root m3 P5)
  - Seventh chord (root M3 P5 m7)
  - Diminished (root m3 d5)

The generator computes:

```
root = startMidi + fifthSteps[column]
counterbass = root + 4 semitones
```

Chord buttons store only:
```
type: "major" | "minor" | "dim" | "7"
root: <note>
```

All chord voicings are generated later by the playback engine.

---

## 3. Dynamic Colors

Initially, Akkordio uses **pitch-class colors** (same for treble and free-bass):

- C = white  
- C#/Db = dark  
- D = blue  
- D#/Eb = dark  
- E = green  
- F = yellow  
- F#/Gb = orange  
- G = red  
- G#/Ab = gray  
- A = purple  
- A#/Bb = purple  
- B = teal  

Later, Akkordio overlays:

- Fingering-based color maps  
- Dynamic highlights for MIDI playback  
- Animated finger indicators

---

## 4. Output Format Returned by Generator

The generated layout always follows this structure:

```json
{
  "system": "c-system",
  "rows": 5,
  "columns": 12,
  "startMidi": 60,
  "buttons": [
    {
      "row": 0,
      "column": 0,
      "note": "C3",
      "midi": 48,
      "color": "white",
      "type": "note"
    }
  ],
  "noteIndex": {
    "48": [{ "row": 0, "column": 0 }]
  },
  "geometry": {
    "buttonRadius": 8,
    "rowSpacing": 15,
    "columnSpacing": 18,
    "staggered": true,
    "staggerOffset": 9
  }
}
```

---

## 5. Advantages of Dynamic Layout Generation

### ✔ Supports any accordion immediately
- 3-row, 5-row, 6-row chromatic
- Any number of columns
- B, C, or custom systems
- Converter instruments
- Any size Stradella (48–185 bass)
- Free-bass systems from student to professional bayan

### ✔ Cleaner codebase
No redundancy. One generator handles all systems.

### ✔ Easy for users
Akkordio lets users specify:

- Instrument type
- Starting pitch
- Row/column count

And the system handles the rest.

### ✔ Perfect for score-based fingering training
Because every button’s pitch is computed programmatically, Akkordio can:

- Map notes in a score directly to buttons
- Animate fingerings
- Display correct hand shapes
- Adapt to any user’s accordion

---

## 6. Example: Minimal Chromatic Generator (Pseudo-JS)

```js
export function generateChromaticLayout({
  system,
  rows,
  columns,
  startMidi,
  rowOffsets,
  colOffsets,
  geometry
}) {
  const buttons = [];
  const noteIndex = {};

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < columns; c++) {
      const midi =
        startMidi +
        rowOffsets[r] +
        (typeof colOffsets === "function" ? colOffsets(c) : colOffsets[c]);

      const note = midiToNoteName(midi);

      const button = {
        row: r,
        column: c,
        note,
        midi,
        color: pitchClassColor(note),
        type: "note"
      };

      buttons.push(button);
      if (!noteIndex[midi]) noteIndex[midi] = [];
      noteIndex[midi].push({ row: r, column: c });
    }
  }

  return { system, rows, columns, buttons, noteIndex, geometry };
}
```

---

## 7. Summary

Akkordio’s layout engine is designed to be:

- **Flexible** — supports every known accordion system  
- **Unified** — same structure for all layouts  
- **Extendable** — fingering, color overlays, playback mapping  
- **Accurate** — computed pitches and enharmonics  
- **Lightweight** — no massive JSON files to maintain  

This architecture allows Akkordio to become the first truly universal accordion fingering and learning tool.

---

If you'd like, I can also generate:

- A companion `.ts` layout generator file  
- A `layouts.config.json` defining all preset systems  
- Diagrams for each system  
- A README for your GitHub repo

Just let me know!
