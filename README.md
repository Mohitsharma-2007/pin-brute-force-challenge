# PIN Brute Force Challenge - Educational Cybersecurity Tool

![Security](https://img.shields.io/badge/security-educational-yellow)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Flask](https://img.shields.io/badge/flask-latest-green)
![PostgreSQL](https://img.shields.io/badge/postgresql-supported-blue)

An advanced educational cybersecurity application that demonstrates PIN brute-forcing techniques and defensive measures. This project includes both a vulnerable PIN challenge server and sophisticated multi-threaded attack tools for learning purposes.

## 🎯 Features

### Web Application
- **Interactive PIN Challenge**: Manual PIN guessing interface
- **Web-based Attack Tool**: Real-time brute force attacks with live monitoring
- **Database Dashboard**: Comprehensive statistics and attack history
- **Responsive Design**: Bootstrap dark theme with mobile support

### Attack Tools
- **Multi-threaded Brute Forcer**: High-performance PIN cracking with configurable threads
- **Command Line Interface**: Advanced CLI tool with progress tracking
- **Real-time Monitoring**: Live attack progress with ETA calculations
- **Connection Testing**: Pre-attack target validation

### Database Features
- **PostgreSQL Integration**: Persistent storage of all attack data
- **Session Tracking**: Complete attack session history with configurations
- **Statistics Dashboard**: Real-time analytics and success rate tracking
- **Data Visualization**: Professional charts and tables for analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL database (optional - runs without database)
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pin-brute-force-challenge.git
   cd pin-brute-force-challenge
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables** (optional)
   ```bash
   export SECRET_PIN=6942                    # Target PIN to crack
   export SESSION_SECRET=your-secret-key     # Flask session key
   export DATABASE_URL=postgresql://...      # PostgreSQL connection
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   - Web interface: http://localhost:5000
   - Attack tool: http://localhost:5000/attack
   - Database dashboard: http://localhost:5000/database

## 📖 Usage

### Web Interface Attack

1. Navigate to `/attack` in your browser
2. Enter the target URL (e.g., `http://localhost:5000/check`)
3. Configure attack parameters:
   - **Threads**: Number of concurrent workers (5-50)
   - **Delay**: Time between requests (0-1 seconds)
   - **Timeout**: Request timeout (3-30 seconds)
4. Click "Test Connection" to verify target
5. Click "Start Attack" to begin brute forcing
6. Monitor real-time progress and results

### Command Line Attack

```bash
# Basic attack
python pin_cracker.py --url http://localhost:5000/check

# Advanced configuration
python pin_cracker.py \
  --url http://target.com/check \
  --threads 20 \
  --delay 0.1 \
  --timeout 10 \
  --verbose
```

### Manual PIN Testing

1. Visit `/challenge` for the interactive interface
2. Enter 4-digit PINs (0000-9999)
3. View immediate feedback on attempts
4. Track your manual guessing progress

## 🏗️ Architecture

### Backend Components
- **Flask Web Server**: Main application server with API endpoints
- **PostgreSQL Database**: Persistent storage for attack data and statistics
- **Multi-threaded Engine**: Queue-based task distribution for brute forcing
- **Session Management**: Thread-safe attack coordination

### Database Schema
- **AttackSession**: Complete attack session records with configuration
- **AttemptLog**: Individual PIN attempts during automated attacks
- **PinAttempt**: Manual PIN attempts via web interface
- **Statistics**: Application-wide metrics and analytics

### API Endpoints
- `POST /check`: PIN validation endpoint
- `GET /stats`: JSON statistics and metrics
- `POST /test-connection`: Target connectivity testing
- `GET /start-attack`: Server-sent events for live attack monitoring

## 🛡️ Security Features

### Educational Safeguards
- **Rate Limiting Awareness**: Configurable delays to prevent server overload
- **Connection Testing**: Pre-flight checks to validate targets
- **Error Handling**: Robust exception handling for network issues
- **Session Isolation**: Thread-safe operation with proper locking

### Monitoring & Logging
- **Real-time Progress**: Live attack monitoring with ETA calculations
- **Comprehensive Logging**: Detailed attempt logs with timestamps
- **Success Tracking**: Statistical analysis of attack effectiveness
- **IP Tracking**: Source identification for security analysis

## 📊 Dashboard Features

The database dashboard (`/database`) provides:

- **Live Statistics**: Real-time attack metrics and success rates
- **Attack History**: Complete session history with detailed results
- **Performance Analytics**: Thread utilization and timing analysis
- **Data Visualization**: Professional charts and responsive tables
- **Auto-refresh**: 30-second automatic updates

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_PIN` | Target PIN to crack | `6942` |
| `SESSION_SECRET` | Flask session encryption key | Generated |
| `DATABASE_URL` | PostgreSQL connection string | None (optional) |

### Attack Parameters
| Parameter | Range | Description |
|-----------|-------|-------------|
| Threads | 1-100 | Concurrent worker threads |
| Delay | 0-5s | Delay between requests |
| Timeout | 1-60s | Request timeout duration |
| Verbose | Boolean | Enable detailed logging |

## 🎓 Educational Objectives

This project demonstrates:

### Security Concepts
- **Brute Force Attacks**: Systematic password/PIN cracking
- **Rate Limiting**: Defense against automated attacks
- **Threading Optimization**: Performance optimization techniques
- **Session Management**: Secure state handling

### Technical Skills
- **HTTP Protocol**: POST requests and response handling
- **Multi-threading**: Concurrent programming patterns
- **Database Design**: Relational data modeling
- **Web Development**: Full-stack application architecture

## ⚠️ Legal Notice

**FOR EDUCATIONAL PURPOSES ONLY**

This tool is designed for cybersecurity education and authorized penetration testing. Users are responsible for ensuring they have explicit permission to test any systems. Unauthorized access to computer systems is illegal.

### Responsible Use Guidelines
- Only test systems you own or have written permission to test
- Respect rate limiting and server resources
- Use appropriate delays to prevent service disruption
- Document and report findings responsibly

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:

- Bug fixes and improvements
- New attack techniques or defenses
- Enhanced monitoring features
- Educational content and documentation

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for cybersecurity education and awareness
- Inspired by real-world penetration testing tools
- Designed with responsible disclosure principles
- Created to promote security best practices

## 📞 Support

For questions, issues, or educational discussions:

- Open an issue on GitHub
- Check the documentation in `/docs`
- Review the code comments for implementation details

---

**Remember**: Always use this tool responsibly and only on systems you own or have explicit permission to test.
