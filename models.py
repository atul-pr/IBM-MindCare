"""
Database Models - SQLAlchemy ORM models for HealSpace AI
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and user management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'user' or 'admin'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    messages = db.relationship('Message', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    moods = db.relationship('Mood', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    crisis_events = db.relationship('CrisisEvent', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    admin_actions = db.relationship('AdminAction', foreign_keys='AdminAction.admin_id', backref='admin', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'


class Message(db.Model):
    """Chat message model"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'bot'
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'sender': self.sender,
            'message': self.message,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<Message {self.id} from {self.sender}>'


class Mood(db.Model):
    """Mood tracking model"""
    __tablename__ = 'moods'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    mood_score = db.Column(db.Integer, nullable=False)  # 1-5 scale
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Add constraint for mood_score range
    __table_args__ = (
        db.CheckConstraint('mood_score >= 1 AND mood_score <= 5', name='mood_score_range'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'mood': self.mood_score,
            'date': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<Mood {self.mood_score} at {self.timestamp}>'


class CrisisEvent(db.Model):
    """Crisis event logging for analytics"""
    __tablename__ = 'crisis_events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)  # Nullable for anonymous
    crisis_type = db.Column(db.String(50), nullable=False)  # 'suicide', 'self_harm', 'extreme_distress'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'crisis_type': self.crisis_type,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<CrisisEvent {self.crisis_type} at {self.timestamp}>'


class AdminAction(db.Model):
    """Admin action logging for audit trail"""
    __tablename__ = 'admin_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(100), nullable=False)  # 'deactivate_user', 'delete_user', 'view_user_data'
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    details = db.Column(db.Text)  # Additional context
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationship to target user
    target_user = db.relationship('User', foreign_keys=[target_user_id], backref='actions_received')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'action': self.action,
            'target_user_id': self.target_user_id,
            'details': self.details,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<AdminAction {self.action} by admin {self.admin_id}>'


def init_db(app):
    """Initialize database and create tables"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default admin user if not exists (check by email only)
        admin_user = User.query.filter_by(email='admin@healspace.ai').first()
        
        if not admin_user:
            admin = User(
                username='admin',
                email='admin@healspace.ai',
                role='admin',
                is_active=True
            )
            admin.set_password('Admin@123456')
            db.session.add(admin)
            db.session.commit()
            print("✓ Default admin user created (email: admin@healspace.ai, password: Admin@123456)")
        elif admin_by_user and not admin_by_email:
            # Username exists but email is different? Update it or just skip
            pass
        elif not admin_by_user and admin_by_email:
            # Email exists but username is different? Update the username
            admin_by_email.username = 'healspace_admin'
            admin_by_email.set_password('HealSpace@123')
            db.session.commit()
            print("✓ Updated existing user with admin email to new admin username.")
        
        print("✓ Database initialized successfully")


def seed_test_data(app):
    """Seed database with test data for development"""
    with app.app_context():
        # Check if test user exists
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(
                username='testuser',
                email='test@example.com',
                role='user',
                is_active=True
            )
            test_user.set_password('Test@123')
            db.session.add(test_user)
            db.session.commit()
            
            # Add sample messages
            messages = [
                Message(user_id=test_user.id, sender='user', message='Hello, I need help'),
                Message(user_id=test_user.id, sender='bot', message='Hi! I\'m here to listen. How are you feeling?'),
                Message(user_id=test_user.id, sender='user', message='I\'m feeling anxious'),
                Message(user_id=test_user.id, sender='bot', message='I hear that you\'re feeling anxious. That must be difficult.'),
            ]
            db.session.add_all(messages)
            
            # Add sample moods
            moods = [
                Mood(user_id=test_user.id, mood_score=3),
                Mood(user_id=test_user.id, mood_score=4),
                Mood(user_id=test_user.id, mood_score=2),
            ]
            db.session.add_all(moods)
            
            db.session.commit()
            print("✓ Test data seeded successfully")
