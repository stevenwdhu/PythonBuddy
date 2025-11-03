# PythonBuddy Frontend

React-based frontend for PythonBuddy online Python linter.

## Features

- Live Python code editing with CodeMirror
- Real-time syntax checking with Pylint
- Code execution with output display
- Multiple code examples
- Clean, modern UI

## Setup

### Install Dependencies

```bash
npm install
```

### Environment Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` to configure the backend API URL if needed (default is `http://localhost:5000`).

### Development Server

```bash
npm run dev
```

The application will start on `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The built files will be in the `build/` directory.

### Preview Production Build

```bash
npm run preview
```

## Technology Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **CodeMirror 5** - Code editor
- **Axios** - HTTP client
- **UUID** - Session ID generation

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── App.jsx         # Main application component
│   ├── App.css         # App-specific styles
│   ├── index.css       # Global styles
│   └── main.jsx        # Application entry point
├── index.html          # HTML template
├── package.json        # Dependencies and scripts
└── vite.config.js      # Vite configuration
```

## API Integration

The frontend communicates with the Flask backend via REST API:

- `POST /api/check_code` - Lint Python code
- `POST /api/run_code` - Execute Python code
- `POST /api/cleanup` - Clean up session files

Each request includes an `X-Session-ID` header for session management.

