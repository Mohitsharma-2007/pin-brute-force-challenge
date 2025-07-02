# PIN Brute Force Challenge - Educational Cybersecurity Tool

## Overview

This is an educational cybersecurity application that demonstrates PIN brute-forcing techniques and defensive measures. The system consists of a Flask web server that hosts a PIN challenge and an advanced multi-threaded brute force tool to crack it. The application is designed for learning purposes to understand both attack vectors and security implementations.

## System Architecture

**Frontend:** HTML templates with Bootstrap dark theme and Font Awesome icons
**Backend:** Python Flask web server with PostgreSQL database
**Security Tool:** Multi-threaded PIN brute forcer with queue-based task distribution
**Database:** PostgreSQL for persistent storage of attack sessions, attempts, and statistics
**Deployment:** Designed for Replit hosting with configurable environment variables

The architecture follows a simple client-server model where the Flask application serves both the web interface and API endpoints, while the PIN cracker operates as a separate tool that can target the server's API.

## Key Components

### Web Server (server.py)
- **Purpose:** Hosts the PIN challenge with both web interface and API endpoints
- **Key Features:** 
  - Configurable secret PIN via environment variables
  - Request logging and monitoring
  - Thread-safe attempt tracking
  - Support for both form and JSON requests
- **Security:** Basic rate limiting awareness, attempt logging for monitoring

### PIN Brute Forcer (pin_cracker.py)
- **Purpose:** Demonstrates advanced brute-forcing techniques
- **Key Features:**
  - Multi-threaded execution for performance
  - Queue-based task distribution
  - Configurable delays for ethical testing
  - Progress tracking and verbose logging
  - Session reuse for connection optimization
- **Architecture:** Thread-safe design with locking mechanisms

### Web Interface
- **Templates:** Bootstrap-based responsive design with dark theme
- **Pages:** 
  - Home page with challenge description and safety warnings
  - Interactive challenge page for manual PIN attempts
  - Web-based attack tool for automated brute forcing
  - Database dashboard with real-time statistics and history
- **Styling:** Custom CSS with responsive design principles

### Database Models
- **AttackSession:** Tracks complete brute force attack sessions with configuration and results
- **AttemptLog:** Records individual PIN attempts during automated attacks
- **PinAttempt:** Logs manual PIN attempts via web interface
- **Statistics:** Stores application-wide statistics and metrics

## Data Flow

1. **Challenge Setup:** Server initializes with secret PIN from environment variable (default: "6942")
2. **Manual Attempts:** Users can submit PIN guesses through web form or API calls
3. **Automated Attacks:** Brute forcer generates PIN combinations and tests them via API
4. **Response Handling:** Server responds with success/failure and logs all attempts
5. **Monitoring:** All attempts are tracked with timestamps and IP addresses

## External Dependencies

**Python Packages:**
- Flask: Web framework for server implementation
- Flask-SQLAlchemy: ORM for database operations
- psycopg2-binary: PostgreSQL database adapter
- requests: HTTP client library for brute forcer
- threading: Built-in module for multi-threaded operations
- queue: Thread-safe task distribution

**Frontend Libraries:**
- Bootstrap Agent Dark Theme: UI framework
- Font Awesome: Icon library

**Environment Variables:**
- `SECRET_PIN`: Configurable target PIN (default: "6942")
- `SESSION_SECRET`: Flask session security key

## Deployment Strategy

The application is configured for Replit deployment with:
- Host binding to "0.0.0.0" for external access
- Port 5000 for standard Flask deployment
- Debug mode enabled for development
- Environment variable configuration for security settings

**File Structure:**
- `main.py`: Entry point that imports and runs the Flask app
- `server.py`: Main Flask application with all routes and logic
- `pin_cracker.py`: Standalone brute force tool
- `templates/`: HTML templates for web interface
- `static/`: CSS styling for frontend

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- July 02, 2025. Initial setup