from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class AttackSession(db.Model):
    """Database model for tracking brute force attack sessions"""
    __tablename__ = 'attack_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    target_url = db.Column(db.String(500), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='running')  # running, completed, failed, stopped
    threads_used = db.Column(db.Integer, default=10)
    delay_used = db.Column(db.Float, default=0.0)
    timeout_used = db.Column(db.Integer, default=5)
    verbose_mode = db.Column(db.Boolean, default=False)
    
    # Results
    total_attempts = db.Column(db.Integer, default=0)
    found_pin = db.Column(db.String(10))
    success = db.Column(db.Boolean, default=False)
    duration_seconds = db.Column(db.Float)
    average_rate = db.Column(db.Float)  # attempts per second
    
    # Metadata
    user_ip = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    attempts = db.relationship('AttemptLog', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'target_url': self.target_url,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'threads_used': self.threads_used,
            'delay_used': self.delay_used,
            'timeout_used': self.timeout_used,
            'verbose_mode': self.verbose_mode,
            'total_attempts': self.total_attempts,
            'found_pin': self.found_pin,
            'success': self.success,
            'duration_seconds': self.duration_seconds,
            'average_rate': self.average_rate,
            'user_ip': self.user_ip,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AttemptLog(db.Model):
    """Database model for logging individual PIN attempts"""
    __tablename__ = 'attempt_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('attack_sessions.id'), nullable=False)
    pin_attempted = db.Column(db.String(10), nullable=False)
    success = db.Column(db.Boolean, default=False)
    response_code = db.Column(db.Integer)
    response_time_ms = db.Column(db.Float)
    error_message = db.Column(db.Text)
    worker_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'pin_attempted': self.pin_attempted,
            'success': self.success,
            'response_code': self.response_code,
            'response_time_ms': self.response_time_ms,
            'error_message': self.error_message,
            'worker_id': self.worker_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class PinAttempt(db.Model):
    """Database model for tracking manual PIN attempts via web interface"""
    __tablename__ = 'pin_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    pin = db.Column(db.String(10), nullable=False)
    success = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'pin': self.pin,
            'success': self.success,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class Statistics(db.Model):
    """Database model for storing application statistics"""
    __tablename__ = 'statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    stat_name = db.Column(db.String(100), unique=True, nullable=False)
    stat_value = db.Column(db.Text)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def get_stat(name, default=None):
        """Get a statistic value"""
        stat = Statistics.query.filter_by(stat_name=name).first()
        if stat:
            try:
                return json.loads(stat.stat_value)
            except:
                return stat.stat_value
        return default
    
    @staticmethod
    def set_stat(name, value):
        """Set a statistic value"""
        stat = Statistics.query.filter_by(stat_name=name).first()
        if not stat:
            stat = Statistics()
            stat.stat_name = name
        
        if isinstance(value, (dict, list)):
            stat.stat_value = json.dumps(value)
        else:
            stat.stat_value = str(value)
        
        stat.last_updated = datetime.utcnow()
        db.session.add(stat)
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'stat_name': self.stat_name,
            'stat_value': self.stat_value,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }