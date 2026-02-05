"""
Admin Panel Module - User management and analytics
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from auth import admin_required, log_admin_action
from models import db, User, Message, Mood, CrisisEvent, AdminAction
from datetime import datetime, timedelta
from sqlalchemy import func

# Create admin blueprint
admin_bp = Blueprint('admin', __name__)

# ============================================================================
# ADMIN DASHBOARD
# ============================================================================

@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard with overview stats"""
    # Get statistics
    total_users = User.query.filter_by(role='user').count()
    active_users = User.query.filter_by(role='user', is_active=True).count()
    total_chats = Message.query.filter_by(sender='user').count()
    crisis_events = CrisisEvent.query.count()
    
    # Recent user activity
    recent_users = User.query.filter_by(role='user')\
                            .order_by(User.last_login.desc())\
                            .limit(10)\
                            .all()
    
    # Recent crisis events
    recent_crises = CrisisEvent.query.order_by(CrisisEvent.timestamp.desc())\
                                     .limit(5)\
                                     .all()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'total_chats': total_chats,
        'crisis_events': crisis_events
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_users=recent_users,
                         recent_crises=recent_crises)


# ============================================================================
# USER MANAGEMENT
# ============================================================================

@admin_bp.route('/users')
@admin_required
def users():
    """List all users"""
    search = request.args.get('search', '')
    
    query = User.query.filter_by(role='user')
    
    if search:
        query = query.filter(
            (User.username.contains(search)) | 
            (User.email.contains(search))
        )
    
    users = query.order_by(User.created_at.desc()).all()
    
    return render_template('admin/users.html', users=users, search=search)


@admin_bp.route('/user/<int:user_id>')
@admin_required
def user_detail(user_id):
    """View user details and history"""
    user = User.query.get_or_404(user_id)
    
    # Get user's chat history
    messages = Message.query.filter_by(user_id=user_id)\
                           .order_by(Message.timestamp.desc())\
                           .limit(50)\
                           .all()
    
    # Get user's mood history
    moods = Mood.query.filter_by(user_id=user_id)\
                     .order_by(Mood.timestamp.desc())\
                     .limit(30)\
                     .all()
    
    # Get crisis events
    crises = CrisisEvent.query.filter_by(user_id=user_id)\
                             .order_by(CrisisEvent.timestamp.desc())\
                             .all()
    
    # Calculate stats
    total_chats = Message.query.filter_by(user_id=user_id, sender='user').count()
    avg_mood = db.session.query(func.avg(Mood.mood_score))\
                        .filter_by(user_id=user_id)\
                        .scalar() or 0
    
    user_stats = {
        'total_chats': total_chats,
        'avg_mood': round(avg_mood, 1),
        'total_moods': len(moods),
        'crisis_count': len(crises)
    }
    
    # Log admin action
    log_admin_action('view_user_data', target_user_id=user_id, 
                    details=f'Accessed full profile and history for {user.username}')
    
    return render_template('admin/user_detail.html',
                         user=user,
                         messages=messages,
                         moods=moods,
                         crises=crises,
                         stats=user_stats)


@admin_bp.route('/user/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Activate or deactivate user"""
    user = User.query.get_or_404(user_id)
    
    if user.role == 'admin':
        flash('Cannot deactivate admin users.', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    action = 'activate_user' if user.is_active else 'deactivate_user'
    log_admin_action(action, target_user_id=user_id)
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user and all associated data"""
    user = User.query.get_or_404(user_id)
    
    if user.role == 'admin':
        flash('Cannot delete admin users.', 'danger')
        return redirect(url_for('admin.users'))
    
    username = user.username
    
    # Log action before deletion
    log_admin_action('delete_user', target_user_id=user_id, 
                    details=f'Deleted user: {username}')
    
    # Delete user (cascade will delete related data)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} has been permanently deleted.', 'success')
    return redirect(url_for('admin.users'))


# ============================================================================
# ANALYTICS
# ============================================================================

@admin_bp.route('/analytics')
@admin_required
def analytics():
    """System-wide analytics"""
    # Mood trends
    mood_data = db.session.query(
        func.date(Mood.timestamp).label('date'),
        func.avg(Mood.mood_score).label('avg_mood')
    ).group_by(func.date(Mood.timestamp))\
     .order_by(func.date(Mood.timestamp).desc())\
     .limit(30)\
     .all()
    
    # Crisis events by type
    crisis_stats = db.session.query(
        CrisisEvent.crisis_type,
        func.count(CrisisEvent.id).label('count')
    ).group_by(CrisisEvent.crisis_type).all()
    
    # User growth
    user_growth = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter_by(role='user')\
     .group_by(func.date(User.created_at))\
     .order_by(func.date(User.created_at).desc())\
     .limit(30)\
     .all()
    
    # Active users (logged in within last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_users_count = User.query.filter(
        User.role == 'user',
        User.last_login >= week_ago
    ).count()
    
    return render_template('admin/analytics.html',
                         mood_data=mood_data,
                         crisis_stats=crisis_stats,
                         user_growth=user_growth,
                         active_users_count=active_users_count)


# ============================================================================
# ADMIN ACTIONS LOG
# ============================================================================

@admin_bp.route('/actions')
@admin_required
def admin_actions():
    """View admin action log"""
    actions = AdminAction.query.order_by(AdminAction.timestamp.desc())\
                               .limit(100)\
                               .all()
    
    return render_template('admin/actions.html', actions=actions)
