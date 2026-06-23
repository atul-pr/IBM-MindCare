"""
HealSpace AI - Mental Health Support Chatbot with Authentication
Provides 24/7 emotional support with crisis detection for Indian users
"""

# ── Set ALL environment variables FIRST — before any library imports ──────────
# This prevents FutureWarnings from transformers about deprecated cache vars.
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'       # Disable CUDA/GPU
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'        # Suppress TensorFlow/transformers warnings
# HF_HOME is the single source of truth for all HuggingFace caches (transformers v5+)
os.environ.setdefault('HF_HOME', '/tmp/hf_cache')
os.environ.setdefault('SENTENCE_TRANSFORMERS_HOME', '/tmp/hf_cache')
# Silence the FutureWarning about TRANSFORMERS_CACHE deprecation
import warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='transformers')
# ─────────────────────────────────────────────────────────────────────────────

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models and database
from models import db, init_db, User, Message, Mood, CrisisEvent
from config import get_config

# Import authentication
from auth import auth_bp, init_auth

# Import AI and crisis detection
from ai import get_ai_response
from crisis import detect_crisis, get_crisis_response

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(get_config())

# Initialize extensions
init_auth(app)

# Register blueprints
app.register_blueprint(auth_bp)

# Initialize database and create tables
try:
    with app.app_context():
        init_db(app)
except Exception as _db_err:
    print(f"⚠️  Database init warning: {_db_err}")

# Initialize RAG system synchronously.
# Fast path: loads existing faiss_index.pkl from disk (~27KB, <1s).
# The SentenceTransformer model is lazy-loaded only on first chat query.
try:
    from rag import initialize_rag
    initialize_rag()
    print("✅ RAG system ready")
except Exception as _rag_err:
    print(f"⚠️  RAG init error: {_rag_err} — falling back to pattern responses")

# Startup: log which AI providers are active
_groq_key = os.getenv('GROQ_API_KEY', '').strip()
if _groq_key and _groq_key not in ('', 'your-groq-api-key-here'):
    print(f"✅ GROQ_API_KEY detected: {_groq_key[:8]}...  ← PRIMARY provider")
else:
    print("⚠️  GROQ_API_KEY not set — falling back to HuggingFace.")

_hf_key = os.getenv('HF_API_KEY', '').strip()
if _hf_key and _hf_key not in ('', 'your-huggingface-api-key-here'):
    print(f"✅ HF_API_KEY detected: {_hf_key[:8]}...  ← FALLBACK provider")
else:
    print("⚠️  HF_API_KEY not set — chatbot will use pattern fallback only.")



# ============================================================================
# PUBLIC ROUTES
# ============================================================================

@app.route('/')
@app.route('/index.html')
def index():
    """Landing page - public entrance"""
    return render_template('index.html')


@app.route('/health')
def health_check():
    """Health check endpoint for deployment — always returns 200 immediately."""
    groq_key = os.getenv('GROQ_API_KEY', '')
    hf_key   = os.getenv('HF_API_KEY', '')
    return jsonify({
        'status': 'healthy',
        'service': 'HealSpace AI',
        'groq_key_set': bool(groq_key and groq_key not in ('', 'your-groq-api-key-here')),
        'hf_key_set':   bool(hf_key and hf_key not in ('', 'your-huggingface-api-key-here')),
    })


@app.route('/api/status')
@login_required
def api_status():
    """Debug endpoint — admin-only, shows which API keys are loaded."""
    if not current_user.is_admin():
        return jsonify({'error': 'forbidden'}), 403
    groq_key = os.getenv('GROQ_API_KEY', '').strip()
    hf_key   = os.getenv('HF_API_KEY', '').strip()
    secret   = os.getenv('SECRET_KEY', '').strip()
    return jsonify({
        'groq_api_key':   f"{groq_key[:8]}..." if groq_key else 'NOT SET ❌',
        'hf_api_key':     f"{hf_key[:8]}..."   if hf_key   else 'NOT SET ❌',
        'secret_key':     'SET ✅'              if secret   else 'NOT SET ❌',
        'flask_env':      os.getenv('FLASK_ENV', 'NOT SET'),
        'database_url':   'SET ✅' if os.getenv('DATABASE_URL') else 'using SQLite',
    })


# ============================================================================
# USER ROUTES (PROTECTED)
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with stats"""
    # Calculate user stats
    total_chats = Message.query.filter_by(user_id=current_user.id, sender='user').count()
    
    moods = Mood.query.filter_by(user_id=current_user.id).all()
    avg_mood = sum(m.mood_score for m in moods) / len(moods) if moods else 0
    
    days_active = (datetime.utcnow() - current_user.created_at).days
    
    stats = {
        'total_chats': total_chats,
        'avg_mood': avg_mood,
        'days_active': days_active
    }
    
    return render_template('dashboard.html', stats=stats)


@app.route('/chat')
@login_required
def chat_page():
    """Chat interface"""
    return render_template('chat.html')


@app.route('/chat', methods=['POST'])
@login_required
def chat():
    """Handle chat messages with crisis detection and AI response"""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Invalid request'}), 400

        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        # Limit message length to prevent API token abuse
        if len(user_message) > 2000:
            user_message = user_message[:2000]

        # Save user message to database
        if current_user.is_authenticated:
            message = Message(
                user_id=current_user.id,
                sender='user',
                message=user_message
            )
            db.session.add(message)
            db.session.commit()

        # CRITICAL: Check for crisis BEFORE AI response
        is_crisis, crisis_type = detect_crisis(user_message)
        print(f"[chat] user={current_user.id} crisis={is_crisis} type={crisis_type}")
        
        if is_crisis:
            # Log crisis event (only if logged in)
            if current_user.is_authenticated:
                crisis_event = CrisisEvent(
                    user_id=current_user.id,
                    crisis_type=crisis_type
                )
                db.session.add(crisis_event)
                db.session.commit()
            
            # Crisis detected - override normal AI response
            bot_response = get_crisis_response(crisis_type)
            
            # Save bot response (only if logged in)
            if current_user.is_authenticated:
                bot_message = Message(
                    user_id=current_user.id,
                    sender='bot',
                    message=bot_response
                )
                db.session.add(bot_message)
                db.session.commit()
            
            return jsonify({
                'response': bot_response,
                'crisis': True,
                'crisis_type': crisis_type,
                'timestamp': datetime.now().strftime('%H:%M')
            })
        
        # Normal conversation - get AI response with conversation history
        # Fetch last 10 messages for context (user + bot interleaved)
        chat_history = []
        if current_user.is_authenticated:
            recent_msgs = Message.query.filter_by(user_id=current_user.id)\
                .order_by(Message.timestamp.desc())\
                .limit(10)\
                .all()
            # Reverse to chronological order, exclude the message we just saved
            for m in reversed(recent_msgs[:-1] if len(recent_msgs) > 1 else []):
                chat_history.append({
                    'role': 'user' if m.sender == 'user' else 'assistant',
                    'content': m.message[:500]  # limit each message to 500 chars
                })

        bot_response = get_ai_response(user_message, history=chat_history)
        
        # Save bot response (only if logged in)
        if current_user.is_authenticated:
            bot_message = Message(
                user_id=current_user.id,
                sender='bot',
                message=bot_response
            )
            db.session.add(bot_message)
            db.session.commit()
        
        return jsonify({
            'response': bot_response,
            'crisis': False,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'response': "I'm having trouble right now. Please try again or reach out to Kiran helpline: 1800-599-0019",
            'crisis': False,
            'timestamp': datetime.now().strftime('%H:%M')
        }), 500


@app.route('/mood', methods=['POST'])
@login_required
def log_mood():
    """Save user's mood rating (1-5 scale)"""
    try:
        data = request.get_json()
        mood_score = data.get('mood')
        
        if not mood_score or not (1 <= int(mood_score) <= 5):
            return jsonify({'error': 'Invalid mood score'}), 400
        
        # Save mood
        mood = Mood(
            user_id=current_user.id,
            mood_score=int(mood_score)
        )
        db.session.add(mood)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Mood logged successfully'})
        
    except Exception as e:
        print(f"Error logging mood: {e}")
        return jsonify({'error': 'Failed to log mood'}), 500


@app.route('/mood-history')
@login_required
def mood_history():
    """Get mood history with trend analysis"""
    try:
        # Get user's mood history
        moods = Mood.query.filter_by(user_id=current_user.id)\
                          .order_by(Mood.timestamp.desc())\
                          .limit(30)\
                          .all()
        
        if not moods:
            return jsonify({
                'history': [],
                'trend': 'No mood data yet. Start tracking your mood!',
                'average': 0
            })
        
        # Convert to dict
        history = [m.to_dict() for m in reversed(moods)]
        
        # Calculate average and trend
        mood_scores = [m.mood_score for m in moods]
        average = sum(mood_scores) / len(mood_scores)
        
        # Simple trend analysis
        if len(mood_scores) >= 3:
            recent_avg = sum(mood_scores[:3]) / 3
            older_avg = sum(mood_scores[3:]) / len(mood_scores[3:]) if len(mood_scores) > 3 else average
            
            if recent_avg > older_avg + 0.5:
                trend = "📈 Your mood is improving! Keep it up!"
            elif recent_avg < older_avg - 0.5:
                trend = "📉 Your mood seems lower lately. Consider talking to someone."
            else:
                trend = "➡️ Your mood is relatively stable."
        else:
            trend = "Keep tracking to see trends over time."
        
        return jsonify({
            'history': history,
            'trend': trend,
            'average': round(average, 1)
        })
        
    except Exception as e:
        print(f"Error fetching mood history: {e}")
        return jsonify({'error': 'Failed to fetch mood history'}), 500


@app.route('/mood-history-page')
@login_required
def mood_history_page():
    """Mood history page"""
    return render_template('mood_history.html')


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(401)
def unauthorized(e):
    """Handle unauthorized access"""
    return redirect(url_for('auth.login'))


@app.errorhandler(403)
def forbidden(e):
    """Handle forbidden access"""
    return render_template('error.html', 
                         error_code=403, 
                         error_message='You do not have permission to access this page.'), 403


@app.errorhandler(404)
def not_found(e):
    """Handle page not found"""
    return render_template('error.html',
                         error_code=404,
                         error_message='The page you are looking for does not exist.'), 404


@app.errorhandler(500)
def server_error(e):
    """Handle server error"""
    return render_template('error.html',
                         error_code=500,
                         error_message='Something went wrong on our end. Please try again later.'), 500


# ============================================================================
# IMPORT ADMIN ROUTES
# ============================================================================

try:
    from admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
except ImportError:
    print("Admin module not yet created")


if __name__ == '__main__':
    # Run on all interfaces for deployment compatibility
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
