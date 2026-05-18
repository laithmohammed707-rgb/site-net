
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime 

db = SQLAlchemy() 











class User(UserMixin, db.Model):
    __tablename__ = 'users' 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
    # إضافة نوع المركز
    center_type = db.Column(db.String(50)) # رئيسي أو فرعي
    
    # إضافة أعمدة الصلاحيات (0 تعني لا، 1 تعني نعم)
    can_add_user = db.Column(db.Integer, default=0)
    can_transfer = db.Column(db.Integer, default=0)
    can_wallet_address = db.Column(db.Integer, default=0)
    can_view_users = db.Column(db.Integer, default=0)
    can_financial_trans = db.Column(db.Integer, default=0)
    can_active_wallet = db.Column(db.Integer, default=0)

    transactions = db.relationship('Transaction', backref='owner', lazy=True)







class Transaction(db.Model):
    __tablename__ = 'transactions' 
    id = db.Column(db.Integer, primary_key=True)
    card_last4 = db.Column(db.String(4), nullable=False)
    cardholder_name = db.Column(db.String(200))
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(120))
    zip_code = db.Column(db.String(20))
    expiry_date = db.Column(db.String(10)) # لتخزين MM/YY
    
    phone = db.Column(db.String(20)) 
    # ربط العملية بالمستخدم بشكل صحيح
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)



# -----------------------------------
# جدول المحافظ
# -----------------------------------
class Wallet(db.Model):

    __tablename__ = 'wallets'

    id = db.Column( db.Integer, primary_key=True)
    address = db.Column(db.String(200), nullable=False, default="0x000...000")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    wallet_name = db.Column( db.String(100), nullable=False )

    wallet_address = db.Column( db.String(255),  nullable=False )

    network = db.Column(  db.String(50),   nullable=False )
    created_at = db.Column(  db.DateTime,  default=datetime.utcnow
    )
