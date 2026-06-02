"""
Script to reset admin user password to default
Run locally: python reset_admin_password.py
"""
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def reset_admin_password():
    with app.app_context():
        # Find admin user by email
        admin = User.query.filter_by(email='admin@healspace.ai').first()
        
        if admin:
            print(f"Found admin user: {admin.username}")
            print(f"Current email: {admin.email}")
            
            # Update to correct credentials
            admin.username = 'admin'
            admin.password_hash = generate_password_hash('Admin@123456')
            admin.role = 'admin'
            admin.is_active = True
            
            db.session.commit()
            print("\n✅ Admin user updated successfully!")
            print("📧 Email: admin@healspace.ai")
            print("🔐 Password: Admin@123456")
            print("\n⚠️  IMPORTANT: Change this password after first login!")
        else:
            print("❌ Admin user not found. Creating new admin user...")
            
            admin = User(
                username='admin',
                email='admin@healspace.ai',
                role='admin',
                is_active=True
            )
            admin.set_password('Admin@123456')
            db.session.add(admin)
            db.session.commit()
            
            print("\n✅ Admin user created successfully!")
            print("📧 Email: admin@healspace.ai")
            print("🔐 Password: Admin@123456")

if __name__ == '__main__':
    reset_admin_password()
