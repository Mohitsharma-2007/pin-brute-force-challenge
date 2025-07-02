from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, Response
import os
import logging
from datetime import datetime
import threading
import time
import requests
import json
from queue import Queue, Empty
from models import db, AttackSession, AttemptLog, PinAttempt, Statistics

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Database configuration
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize database
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
else:
    logger.warning("DATABASE_URL not set - running without database functionality")

# Secret PIN to guess - configurable via environment variable
SECRET_PIN = os.getenv("SECRET_PIN", "6942")
logger.info(f"Server started with secret PIN protection enabled")

# Track attempts for monitoring
attempt_log = []
attempt_lock = threading.Lock()

# Global attack state
attack_active = False
attack_queue = None
attack_threads = []
attack_stats = {
    'attempts': 0,
    'start_time': None,
    'found_pin': None
}
current_session = None

def log_attempt(pin, success, ip_address):
    """Log PIN attempts for monitoring purposes"""
    with attempt_lock:
        attempt_log.append({
            'timestamp': datetime.now().isoformat(),
            'pin': pin,
            'success': success,
            'ip': ip_address
        })
        # Keep only last 1000 attempts
        if len(attempt_log) > 1000:
            attempt_log.pop(0)
    
    # Save to database if available
    if database_url:
        try:
            pin_attempt = PinAttempt()
            pin_attempt.pin = pin
            pin_attempt.success = success
            pin_attempt.ip_address = ip_address
            pin_attempt.user_agent = request.headers.get('User-Agent', '')
            
            db.session.add(pin_attempt)
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to save PIN attempt to database: {e}")
            db.session.rollback()

@app.route('/')
def home():
    """Main page with challenge description"""
    return render_template('index.html')

@app.route('/challenge')
def challenge():
    """Interactive PIN challenge page"""
    return render_template('challenge.html')

@app.route('/attack')
def attack():
    """Brute force attack tool page"""
    return render_template('attack.html')

@app.route('/database')
def database():
    """Database dashboard page"""
    return render_template('database.html')

@app.route('/check', methods=['POST'])
def check_pin():
    """API endpoint for PIN checking - used by both web interface and brute forcer"""
    # Get PIN from form data or JSON
    if request.is_json:
        data = request.get_json()
        pin = data.get('pin') if data else None
    else:
        pin = request.form.get('pin')
    
    client_ip = request.remote_addr
    
    if not pin:
        logger.warning(f"Empty PIN attempt from {client_ip}")
        return jsonify({"error": "PIN is required"}), 400
    
    # Validate PIN format (4 digits)
    if not pin.isdigit() or len(pin) != 4:
        logger.warning(f"Invalid PIN format '{pin}' from {client_ip}")
        log_attempt(pin, False, client_ip)
        return jsonify({"result": "incorrect", "error": "PIN must be 4 digits"}), 403
    
    # Check if PIN is correct
    if pin == SECRET_PIN:
        logger.info(f"✅ CORRECT PIN FOUND: {pin} from {client_ip}")
        log_attempt(pin, True, client_ip)
        return jsonify({
            "result": "correct", 
            "pin": pin,
            "message": "Congratulations! You've successfully cracked the PIN!"
        }), 200
    else:
        logger.debug(f"❌ Incorrect PIN attempt: {pin} from {client_ip}")
        log_attempt(pin, False, client_ip)
        return jsonify({"result": "incorrect"}), 403

@app.route('/check-web', methods=['POST'])
def check_pin_web():
    """Web interface PIN checking with user feedback"""
    pin = request.form.get('pin')
    
    if not pin:
        flash('Please enter a PIN', 'error')
        return redirect(url_for('challenge'))
    
    if not pin.isdigit() or len(pin) != 4:
        flash('PIN must be exactly 4 digits', 'error')
        return redirect(url_for('challenge'))
    
    if pin == SECRET_PIN:
        flash(f'🎉 Congratulations! You cracked the PIN: {pin}', 'success')
    else:
        flash(f'❌ Incorrect PIN: {pin}. Try again!', 'error')
    
    return redirect(url_for('challenge'))

@app.route('/stats')
def stats():
    """Statistics page showing attempt logs (for educational monitoring)"""
    # In-memory stats
    with attempt_lock:
        memory_total = len(attempt_log)
        memory_successful = sum(1 for attempt in attempt_log if attempt['success'])
        recent_attempts = attempt_log[-20:] if attempt_log else []
    
    # Database stats
    db_stats = {}
    if database_url:
        try:
            # PIN attempt stats
            total_pins = db.session.query(PinAttempt).count()
            successful_pins = db.session.query(PinAttempt).filter_by(success=True).count()
            
            # Attack session stats
            total_sessions = db.session.query(AttackSession).count()
            successful_sessions = db.session.query(AttackSession).filter_by(success=True).count()
            
            # Recent sessions
            recent_sessions = db.session.query(AttackSession).order_by(AttackSession.created_at.desc()).limit(10).all()
            
            # Recent PIN attempts
            recent_pins = db.session.query(PinAttempt).order_by(PinAttempt.timestamp.desc()).limit(20).all()
            
            db_stats = {
                'total_pin_attempts': total_pins,
                'successful_pin_attempts': successful_pins,
                'pin_success_rate': (successful_pins / total_pins * 100) if total_pins > 0 else 0,
                'total_attack_sessions': total_sessions,
                'successful_attack_sessions': successful_sessions,
                'session_success_rate': (successful_sessions / total_sessions * 100) if total_sessions > 0 else 0,
                'recent_sessions': [session.to_dict() for session in recent_sessions],
                'recent_pin_attempts': [attempt.to_dict() for attempt in recent_pins]
            }
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            db_stats = {'error': 'Failed to retrieve database statistics'}
    
    return jsonify({
        'memory_stats': {
            'total_attempts': memory_total,
            'successful_attempts': memory_successful,
            'success_rate': (memory_successful / memory_total * 100) if memory_total > 0 else 0,
            'recent_attempts': recent_attempts
        },
        'database_stats': db_stats,
        'database_enabled': database_url is not None
    })

@app.route('/api-docs')
def api_docs():
    """API documentation for educational purposes"""
    docs = {
        'endpoints': {
            '/check': {
                'method': 'POST',
                'description': 'Check if a PIN is correct',
                'parameters': {
                    'pin': 'string (4 digits) - The PIN to check'
                },
                'responses': {
                    '200': 'PIN is correct',
                    '403': 'PIN is incorrect',
                    '400': 'Invalid request'
                }
            },
            '/stats': {
                'method': 'GET',
                'description': 'Get attempt statistics',
                'responses': {
                    '200': 'Statistics data'
                }
            }
        },
        'example_usage': {
            'curl': 'curl -X POST http://localhost:5000/check -d "pin=1234"',
            'python': 'requests.post("http://localhost:5000/check", data={"pin": "1234"})'
        }
    }
    return jsonify(docs)

@app.route('/test-connection', methods=['POST'])
def test_connection():
    """Test connection to a target URL"""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400
    
    try:
        # Test with a dummy PIN
        response = requests.post(url, data={'pin': '0000'}, timeout=10)
        return jsonify({
            'success': True,
            'status': response.status_code,
            'response_time': response.elapsed.total_seconds()
        })
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def attack_worker(worker_id, target_url, delay, timeout, verbose, event_queue):
    """Worker thread for brute force attack"""
    global attack_active, attack_queue, attack_stats, current_session
    
    session = requests.Session()
    
    while attack_active and attack_queue and not attack_queue.empty():
        try:
            pin = attack_queue.get(timeout=1)
            
            if delay > 0:
                time.sleep(delay)
            
            try:
                response = session.post(target_url, data={'pin': pin}, timeout=timeout)
                
                with attempt_lock:
                    attack_stats['attempts'] += 1
                    attempts = attack_stats['attempts']
                
                if verbose:
                    event_queue.put({
                        'type': 'log',
                        'message': f'Worker {worker_id}: Tried {pin} - Status: {response.status_code}',
                        'level': 'info'
                    })
                
                # Progress update every 100 attempts
                if attempts % 100 == 0:
                    elapsed = time.time() - attack_stats['start_time']
                    rate = attempts / elapsed if elapsed > 0 else 0
                    remaining = attack_queue.qsize() if attack_queue else 0
                    eta = remaining / rate if rate > 0 else 0
                    
                    event_queue.put({
                        'type': 'progress',
                        'attempts': attempts,
                        'percentage': round((attempts / 10000) * 100, 1),
                        'rate': round(rate, 1),
                        'eta': round(eta, 1)
                    })
                
                # Check for success
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        if response_data.get('result') == 'correct':
                            with attempt_lock:
                                if not attack_stats['found_pin']:  # First to find it
                                    attack_stats['found_pin'] = pin
                                    elapsed = time.time() - attack_stats['start_time']
                                    
                                    event_queue.put({
                                        'type': 'success',
                                        'pin': pin,
                                        'attempts': attempts,
                                        'time': round(elapsed, 2),
                                        'rate': round(attempts / elapsed, 1),
                                        'target': target_url
                                    })
                                    
                                    attack_active = False
                                    return
                    except:
                        pass
                        
            except requests.exceptions.RequestException as e:
                if verbose:
                    event_queue.put({
                        'type': 'log',
                        'message': f'Worker {worker_id}: Error for PIN {pin}: {str(e)}',
                        'level': 'warning'
                    })
            
            if attack_queue:
                attack_queue.task_done()
            
        except Empty:
            break
        except Exception as e:
            event_queue.put({
                'type': 'log',
                'message': f'Worker {worker_id}: Unexpected error: {str(e)}',
                'level': 'error'
            })

@app.route('/start-attack')
def start_attack():
    """Start brute force attack with server-sent events"""
    global attack_active, attack_queue, attack_threads, attack_stats, current_session
    
    # Get parameters
    target_url = request.args.get('target_url')
    threads = int(request.args.get('threads', 10))
    delay = float(request.args.get('delay', 0))
    timeout = int(request.args.get('timeout', 5))
    verbose = request.args.get('verbose') == 'true'
    
    def generate():
        global attack_active, attack_queue, attack_threads, attack_stats
        
        if attack_active:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Attack already in progress'})}\n\n"
            return
        
        # Initialize attack
        attack_active = True
        attack_queue = Queue()
        attack_threads = []
        attack_stats = {
            'attempts': 0,
            'start_time': time.time(),
            'found_pin': None
        }
        
        # Fill queue with PINs
        for i in range(10000):
            attack_queue.put(f"{i:04d}")
        
        yield f"data: {json.dumps({'type': 'log', 'message': f'Attack initialized: {threads} threads, {delay}s delay', 'level': 'info'})}\n\n"
        yield f"data: {json.dumps({'type': 'log', 'message': f'Generated 10,000 PINs to test', 'level': 'info'})}\n\n"
        
        # Event queue for thread communication
        event_queue = Queue()
        
        # Start worker threads
        for i in range(threads):
            thread = threading.Thread(
                target=attack_worker,
                args=(i+1, target_url, delay, timeout, verbose, event_queue)
            )
            thread.daemon = True
            thread.start()
            attack_threads.append(thread)
        
        yield f"data: {json.dumps({'type': 'log', 'message': f'Started {len(attack_threads)} worker threads', 'level': 'info'})}\n\n"
        
        # Monitor attack progress
        while attack_active:
            # Check for events from workers
            try:
                while not event_queue.empty():
                    event = event_queue.get_nowait()
                    yield f"data: {json.dumps(event)}\n\n"
                    
                    if event.get('type') == 'success':
                        attack_active = False
                        break
            except:
                pass
            
            # Check if threads are still alive
            alive_threads = [t for t in attack_threads if t.is_alive()]
            if not alive_threads and attack_active:
                # All threads finished without success
                elapsed = time.time() - attack_stats['start_time']
                yield f"data: {json.dumps({'type': 'complete', 'success': False, 'time': round(elapsed, 2), 'attempts': attack_stats['attempts']})}\n\n"
                attack_active = False
                break
            
            time.sleep(0.1)  # Small delay to prevent CPU spinning
        
        # Clean up
        for thread in attack_threads:
            if thread.is_alive():
                thread.join(timeout=1)
        
        attack_threads = []
        attack_queue = None
    
    return Response(generate(), mimetype='text/plain', headers={
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'text/event-stream'
    })

@app.route('/stop-attack', methods=['POST'])
def stop_attack():
    """Stop the current attack"""
    global attack_active
    attack_active = False
    return jsonify({'success': True})

if __name__ == '__main__':
    logger.info("Starting PIN Challenge Server...")
    logger.info("Educational cybersecurity demonstration - Use responsibly!")
    app.run(host="0.0.0.0", port=5000, debug=True)
