
import os
import sys
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from dotenv import load_dotenv
from database import db, User



import secrets
from werkzeug.security import generate_password_hash
# استيراد مكتبة حماية البيئة (تأكد من تثبيتها عبر pip install python-dotenv)
from dotenv import load_dotenv
import logging  # 👈 هنا


# ✅ إعداد Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)




# تصحيح استخدام __file__ بالخطوط السفلية المزدوجة
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT) 

def create_app():
    app = Flask(__name__, template_folder=os.path.join(PROJECT_ROOT, 'templates'))
    
    # جلب المفتاح السري من السيرفر أو استخدام مفتاح افتراضي مؤقت
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev-key-safe-123")
    
    # استخدام DATABASE_URL من السيرفر
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    from auth import auth_bp
    from handlers.main import main_bp
    from handlers.transfer import transfer_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp, url_prefix='/dashboard')
    app.register_blueprint(transfer_bp, url_prefix='/transfer')
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
        
    return app 

app = create_app()

# تصحيح استخدام __name__ و "__main__" ليعمل السيرفر بشكل صحيح
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
        # جلب بريد الأدمن وكلمة المرور من بيئة السيرفر لحماية النظام من الاختراق
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@test.com")
        admin_password = os.environ.get("ADMIN_PASSWORD", "123") # يفضل تغيير 123 من لوحة الاستضافة
        
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            db.session.add(User(
                username="admin",
                email=admin_email,
                password=generate_password_hash(admin_password),
                can_add_user=1
            ))
            db.session.commit()
            print("✅ تم فحص وإنشاء حساب الأدمن بنجاح")
            
    # تشغيل مرن يدعم السيرفر السحابي المحلي والخارجي عبر الـ Port الممرر تلقائياً
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)),debug=True)

