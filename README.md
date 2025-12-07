# Akkordio

**Free, open-source web application for converting PDF music scores into interactive accordion fingerings with synchronized playback.**

Akkordio helps accordion players learn music by converting PDF scores into visual button fingerings with MIDI playback. Supports chromatic button accordions (C-System and B-System) and multiple bass systems (Stradella, Free-bass, Converter).

## Features

- **PDF Score Processing**: Upload PDF music scores for automatic conversion
- **OMR Integration**: Uses Audiveris for Optical Music Recognition
- **Multiple Accordion Systems**:
  - Treble: C-System and B-System (3, 4, 5-row variants)
  - Bass: Stradella (48, 72, 96, 120-bass), Free-bass, Converter
- **Interactive Visualization**: SVG-based accordion keyboard visualization
- **MIDI Playback**: Synchronized audio playback with visual feedback
- **Touch-Optimized**: Designed for iPad and touch devices

## Technology Stack

### Backend
- **Python 3.9+**
- **FastAPI** - Modern web framework
- **music21** - Music analysis and processing
- **Audiveris** - Optical Music Recognition
- **Pydantic** - Data validation

### Frontend
- **Vanilla JavaScript (ES6+)** - No frameworks
- **SVG** - Keyboard visualization
- **Tone.js / Web Audio API** - MIDI playback
- **CSS3** - Responsive design with custom properties

## Project Structure

```
akkordio/
├── backend/                 # Python backend
│   ├── main.py             # FastAPI application
│   ├── models.py           # Pydantic models
│   ├── omr.py              # Audiveris integration
│   ├── parser.py           # MusicXML processing
│   ├── treble_mapping.py   # Right-hand mapping
│   ├── bass_mapping.py     # Left-hand mapping
│   ├── layouts/            # Accordion layout JSONs
│   │   ├── treble/
│   │   └── bass/
│   ├── uploads/            # Temporary uploads
│   └── processed/          # Processed files
├── frontend/               # Frontend application
│   ├── index.html         # Main page
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript modules
│   └── assets/            # Images and samples
├── test_data/             # Test files
├── session_logs/          # Development logs
└── docs/                  # Documentation
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Audiveris CLI (for OMR processing)
- Modern web browser (Chrome, Safari, Firefox)

### Backend Setup

1. Create and activate virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn main:app --reload
```

The backend API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Open `index.html` in your browser, or use a local server:
```bash
python -m http.server 3000
```

The frontend will be available at `http://localhost:3000`

### API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Development

### Coding Guidelines

This project follows strict coding standards. See [ref/coding_guidelines.md](ref/coding_guidelines.md) for:
- Session logging requirements
- Python and JavaScript standards
- Testing requirements
- Git practices

### Application Requirements

Complete specifications are in [ref/application_requirements.md](ref/application_requirements.md).

## Current Status

**Phase 1: Basic Infrastructure** ✅ Complete
- FastAPI server with CORS
- File upload handling
- Basic frontend interface
- Pydantic models for API

**Next Steps:**
- Phase 2: OMR Integration (Audiveris)
- Phase 3: Music Processing (music21)
- Phase 4: Mapping Logic
- Phase 5: Visualization
- Phase 6: Playback
- Phase 7: Polish

## Contributing

This is an open-source project. Contributions are welcome! Please:

1. Read the coding guidelines in `ref/coding_guidelines.md`
2. Create a session log for your changes
3. Follow the established patterns
4. Test thoroughly on iPad Safari
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- **Audiveris** - Open-source OMR engine
- **music21** - Music analysis toolkit
- Accordion community for layout specifications

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check documentation in `docs/` directory
- Review troubleshooting guide

## Roadmap

### Current Focus (v1.0)
- Core PDF to fingering conversion
- Basic visualization and playback
- Support for standard layouts

### Future Features (Post v1.0)
- Custom layout editor
- Fingering optimization AI
- Practice tracking
- Community layout sharing
- Bellows direction indicators
- Score following

---

**Akkordio** - Making accordion music more accessible, one button at a time.
