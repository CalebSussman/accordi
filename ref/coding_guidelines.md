coding_guidelines.mdmarkdown# CODING GUIDELINES FOR AKKORDIO
## MANDATORY: READ THIS FIRST
Claude Code MUST read this file before any coding session and follow ALL guidelines.

## SESSION LOGGING REQUIREMENTS

### CRITICAL: Session Documentation
1. **Before ANY code changes**, create or update a session log file:
   - Format: `session_logs/YYYYMMDD_Session.md`
   - If multiple sessions in one day, append to the same file with timestamps

2. **Session log MUST include:**
markdownSession: HH:MM AM/PMChanges Made:

[List every file created/modified]
[Describe the specific changes]
[Note any dependencies added]
Testing Performed:

[What was tested]
[Results]
Issues Encountered:

[Any problems or errors]
[How they were resolved]
Next Steps:

[What remains to be done]
[Any blockers or dependencies]


3. **Commit the session log** alongside code changes

## GOOGLE CLOUD CLI SETUP

### Initial Setup (one-time per machine)
If `gcloud` is not installed, install it with:
```bash
curl https://sdk.cloud.google.com | bash -s -- --disable-prompts --install-dir=$HOME
```

### Session Setup (required each Claude Code session)
Add gcloud to PATH and authenticate:
```bash
# Add to PATH
export PATH="$HOME/google-cloud-sdk/bin:$PATH"

# Authenticate (first time or when credentials expire)
gcloud auth login

# Set the correct project
gcloud config set project accordi-481103
```

### Viewing Cloud Run Logs
```bash
# View recent logs
gcloud run services logs read audiveris-omr --region us-central1 --limit 50

# View logs with timestamps
gcloud run services logs read audiveris-omr --region us-central1 --limit 100 --format="table(timestamp,severity,textPayload)"

# Tail logs in real-time (alternative: use Cloud Console)
# https://console.cloud.google.com/run/detail/us-central1/audiveris-omr/logs?project=accordi-481103
```

### Project Information
- **Project ID**: `accordi-481103`
- **Project Number**: `972258254932`
- **Project Name**: Accordi
- **Cloud Run Region**: `us-central1`
- **Audiveris Service Name**: `audiveris-omr`

## CODING STANDARDS

### General Principles
1. **Complete, Runnable Code Only**
   - NO pseudocode
   - NO placeholders like "// implement later"
   - NO stub functions without implementation
   - Every module must be functional when created

2. **Modular Architecture**
   - Single responsibility per module
   - Clear separation of concerns
   - Backend logic stays in backend
   - Frontend logic stays in frontend
   - No mixing of responsibilities

3. **Documentation**
   - Every function needs a docstring/comment
   - Complex logic requires inline comments
   - API endpoints need clear descriptions
   - Include usage examples for utilities

### Python Backend Standards
1. **Style:**
   - Follow PEP 8
   - Use type hints for all functions
   - Handle exceptions explicitly
   - Use async/await for I/O operations

2. **Structure:**
pythonfrom typing import Dict, List, Optional, Tupleasync def function_name(param: str) -> Dict[str, any]:
"""
Brief description of what the function does.   Args:
       param: Description of parameter   Returns:
       Description of return value   Raises:
       SpecificException: When this happens
   """
   try:
       # Implementation
       pass
   except SpecificException as e:
       # Handle appropriately
       raise

3. **FastAPI Endpoints:**
   - Use proper HTTP status codes
   - Implement request/response models with Pydantic
   - Include OpenAPI documentation
   - Handle CORS properly

### JavaScript Frontend Standards
1. **Style:**
   - Use ES6+ features
   - Prefer const over let, avoid var
   - Use arrow functions for callbacks
   - Implement proper error handling

2. **Structure:**
javascript/**
* Brief description of function
* @param {string} param - Parameter description
* @returns {Object} Return value description
*/
const functionName = (param) => {
try {
// Implementation
} catch (error) {
console.error('Descriptive error message:', error);
// Handle appropriately
}
};

3. **Module Pattern:**
javascript// Each module should export a clear interface
export const ModuleName = {
init: () => { /* Initialization logic / },
publicMethod: () => { / Public API */ },
// Private functions not exported
};

### HTML/CSS Standards
1. **HTML:**
   - Semantic HTML5 elements
   - Proper ARIA labels for accessibility
   - Mobile-first responsive design
   - Touch-friendly elements for iPad

2. **CSS:**
   - Use CSS custom properties for theming
   - Mobile-first media queries
   - Flexbox/Grid for layouts
   - BEM naming convention for classes

### JSON Layout Standards
1. **Structure:**
   - Consistent key naming
   - Clear, self-documenting structure
   - Include metadata (name, version, system type)
   - Use arrays for ordered data

2. **Example:**
json{
"name": "Layout Name",
"version": "1.0.0",
"system": "C",
"rows": 5,
"metadata": {
"description": "Standard C-system layout",
"author": "Akkordio",
"date": "2024-01-01"
},
"buttons": []
}

## FILE ORGANIZATION

### Naming Conventions
- Python: `snake_case.py`
- JavaScript: `camelCase.js` for files, `PascalCase` for classes
- CSS: `kebab-case.css`
- JSON: `snake_case.json`

### Import Order
1. Standard library imports
2. Third-party imports
3. Local application imports
4. Alphabetical within each group

## TESTING REQUIREMENTS

1. **Before committing:**
   - Backend: Test all endpoints with curl or Postman
   - Frontend: Test in Chrome, Safari, and iPad Safari
   - Verify CORS works correctly
   - Check console for errors

2. **Test data:**
   - Include sample PDF files in `test_data/`
   - Include test MIDI files
   - Document expected outputs

## GIT PRACTICES

1. **Commit messages:**[Component] Brief description
Detailed change 1
Detailed change 2
Refs: #issue-number (if applicable)

2. **Branch naming:**
   - `feature/description`
   - `fix/description`
   - `refactor/description`

## DEPLOYMENT READINESS

1. **Environment variables:**
   - Never hardcode secrets
   - Use `.env` files locally
   - Document all required env vars

2. **Dependencies:**
   - Keep requirements.txt updated
   - Pin version numbers
   - No unnecessary dependencies

3. **Production considerations:**
   - Implement proper logging
   - Add health check endpoints
   - Include error monitoring
   - Optimize for performance

## FORBIDDEN PRACTICES

1. **NEVER:**
   - Leave console.log in production code
   - Hardcode API URLs
   - Skip error handling
   - Use synchronous file operations in Node
   - Include API keys in code
   - Mix tabs and spaces
   - Use inline styles except for dynamic values
   - Create functions over 50 lines without refactoring unless unavoidable (must justify in session log)

2. **ALWAYS:**
   - Validate user input
   - Sanitize file uploads
   - Check for null/undefined
   - Close resources properly
   - Use HTTPS in production
   - Test on actual iPad device

## REVIEW CHECKLIST

Before considering any task complete:
- [ ] Code runs without errors
- [ ] All functions have documentation
- [ ] Error handling is comprehensive
- [ ] Session log is updated
- [ ] Tested on target platforms
- [ ] No hardcoded values
- [ ] Dependencies documented
- [ ] Code follows these guidelines