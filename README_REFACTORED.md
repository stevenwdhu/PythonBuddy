# PythonBuddy - Refactored Architecture

**v3.0.0** - Refactored with separate backend and frontend

An online Python code editor with live syntax checking using Pylint and the ability to run Python code.

Originally created by [Ethan Chiu](https://github.com/ethanchewy)

## Architecture Overview

This project has been refactored into a modern client-server architecture:

- **Backend**: Flask REST API (`/backend`)
- **Frontend**: React SPA (`/frontend`)

```
PythonBuddy/
├── backend/                 # Flask REST API
│   ├── app.py              # Main Flask application
│   ├── pylint_errors/      # Pylint error definitions
│   ├── requirements.txt    # Python dependencies
│   └── README.md          # Backend documentation
│
├── frontend/               # React application
│   ├── src/               # Source code
│   │   ├── App.jsx        # Main component
│   │   ├── main.jsx       # Entry point
│   │   └── index.css      # Global styles
│   ├── public/            # Static assets
│   ├── package.json       # Node dependencies
│   ├── vite.config.js     # Vite configuration
│   └── README.md          # Frontend documentation
│
├── PythonBuddy/           # Legacy monolithic app (deprecated)
└── tests/                 # Test suite
```

## Quick Start

### Prerequisites

- Python 3.7+
- Node.js 16+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Backend will run on `http://localhost:5000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on `http://localhost:3000`

## Development

### Running Both Services

You'll need two terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open your browser to `http://localhost:3000`

### API Endpoints

The backend provides the following REST API endpoints:

- `POST /api/check_code` - Lint Python code with Pylint
- `POST /api/run_code` - Execute Python code
- `GET /health` - Health check
- `POST /api/cleanup` - Cleanup session files

See [backend/README.md](backend/README.md) for detailed API documentation.

## Production Deployment

### Backend

```bash
cd backend
pip install -r requirements.txt
# Use a production WSGI server like gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend

```bash
cd frontend
npm run build
# Serve the build/ directory with nginx or another web server
```

Configure the frontend to point to your production backend by setting `VITE_API_BASE` in the environment.

## Technology Stack

### Backend
- Flask 1.1.2
- Flask-CORS 3.0.10
- Pylint 2.6.0
- Python 3.7+

### Frontend
- React 18
- Vite 4
- CodeMirror 5
- Axios

## Features

- ✅ Live Python syntax checking with Pylint
- ✅ Code execution with output display
- ✅ Comprehensive error messages
- ✅ Multiple code examples
- ✅ Clean, modern UI
- ✅ Session management
- ✅ RESTful API architecture
- ✅ CORS support for cross-origin requests

## Migration from Legacy Version

The original monolithic application in `/PythonBuddy` has been split into:

1. **Backend** (`/backend`): All Flask routes, Python execution, and Pylint integration
2. **Frontend** (`/frontend`): React-based UI with CodeMirror

The legacy code is preserved for reference but is no longer actively maintained.

## Testing

```bash
# Run backend tests
cd tests
python -m pytest

# Or using the original test structure
python test_app.py
python test_linter.py
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

See [LICENSE.md](LICENSE.md)

## Acknowledgments

- Original creator: [Ethan Chiu](https://github.com/ethanchewy)
- Built with Flask, React, CodeMirror, and Pylint
- Refactored to modern architecture (v3.0.0)

## Support

For issues and questions, please use the [GitHub Issues](https://github.com/ethanchewy/PythonBuddy/issues) page.

