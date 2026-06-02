"""
Script to create an admin user
Run locally: python create_admin.py
"""
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("❌ Admin user already exists!")
            return
        
        # Create new admin user
        admin_user = User(
            username='admin',
            email='admin@healspace.ai',
            password_hash=generate_password_hash('Admin@123456'),
            role='admin'
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("✅ Admin user created successfully!")
        print("📧 Username: admin")
        print("🔐 Password: Admin@123456")
        print("\n⚠️  IMPORTANT: Change this password after first login!")

if __name__ == '__main__':
    create_admin()
