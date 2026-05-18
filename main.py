
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
#from database import db, User
from database import db, User, Transaction, Wallet
from werkzeug.security import generate_password_hash
#from database import db, User, Transaction
main_bp = Blueprint('main', __name__)

# الصفحة الرئيسية (Dashboard)
@main_bp.route('/dashboard')
@login_required
def dashboard():
    # الحل: نرسل current_user إلى القالب باسم المتغير user
    return render_template('dashboard.html', user=current_user)



# مسار عرض المستخدمين (موجود مسبقاً)
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
# افترضنا استيراد db و User من ملفاتك



@main_bp.route('/users')
@login_required
def users():
    # جلب جميع المستخدمين، الفلترة ستتم في الـ HTML كما طلبتم
    all_users = User.query.order_by(User.id.desc()).all()
    return render_template('users.html', users=all_users)

@main_bp.route('/edit_user/<int:user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    target_user = User.query.get_or_404(user_id)
    
    # حماية إضافية: منع تعديل حساب النظام من هذا المسار حتى لو حاول شخص عبر الأدوات
    if target_user.email == 'admin@test.com':
        flash('لا يمكن تعديل حساب النظام الأساسي من هنا!', 'danger')
        return redirect(url_for('main.users'))

    target_user.username = request.form.get('username')
    target_user.email = request.form.get('email')
    target_user.center_type = request.form.get('center_type')

    # تحديث كلمة المرور فقط إذا تم إدخال شيء جديد
    new_password = request.form.get('password')
    if new_password and new_password.strip() != "":
        target_user.password = generate_password_hash(new_password)

    # معالجة الصلاحيات
    target_user.can_add_user = 1 if request.form.get('can_add_user') else 0
    target_user.can_transfer = 1 if request.form.get('can_transfer') else 0
    target_user.can_wallet_address = 1 if request.form.get('can_wallet_address') else 0
    target_user.can_view_users = 1 if request.form.get('can_view_users') else 0
    target_user.can_financial_trans = 1 if request.form.get('can_financial_trans') else 0
    target_user.can_active_wallet = 1 if request.form.get('can_active_wallet') else 0

    try:
        db.session.commit()
        flash(f'تم تحديث بيانات {target_user.username} بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('خطأ: ربما البريد الإلكتروني مستخدم مسبقاً', 'danger')
    
    return redirect(url_for('main.users'))

@main_bp.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    target_user = User.query.get_or_404(user_id)
    
    # حماية: منع حذف الأدمن الأساسي أو حذف المستخدم لنفسه
    if target_user.email == 'admin@test.com' or current_user.id == user_id:
        flash('غير مسموح بحذف هذا الحساب!', 'danger')
        return redirect(url_for('main.users'))

    db.session.delete(target_user)
    db.session.commit()
    flash('تم حذف المستخدم بنجاح', 'success')
    return redirect(url_for('main.users'))
























# صفحة إضافة مستخدم
@main_bp.route('/add-user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        center_type = request.form.get('center_type')

        # منطق الـ Checkbox: إذا لم يتم تحديد المربع، فلن يرسل المتصفح القيمة، لذا نستخدم get ونعيد 1 إذا وجدت
        can_add_user = 1 if request.form.get('can_add_user') else 0
        can_transfer = 1 if request.form.get('can_transfer') else 0
        can_wallet_address = 1 if request.form.get('can_wallet_address') else 0
        can_view_users = 1 if request.form.get('can_view_users') else 0
        can_financial_trans = 1 if request.form.get('can_financial_trans') else 0
        can_active_wallet = 1 if request.form.get('can_active_wallet') else 0

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('البريد الإلكتروني مستخدم مسبقاً', 'danger')
            return redirect(url_for('main.add_user'))

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            center_type=center_type,
            can_add_user=can_add_user,
            can_transfer=can_transfer,
            can_wallet_address=can_wallet_address,
            can_view_users=can_view_users,
            can_financial_trans=can_financial_trans,
            can_active_wallet=can_active_wallet
        )

        db.session.add(new_user)
        db.session.commit()

        flash('تم إنشاء المستخدم وتحديد الصلاحيات بنجاح', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('add_user.html', user=current_user)




















# -----------------------------------
# صفحة عنوان المحفظة
# -----------------------------------
@main_bp.route('/wallet')
@login_required
def wallet():

    wallet_address = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"

    return render_template(
        'wallet.html',
        user=current_user,
        wallet_address=wallet_address
    )



# -----------------------------------
# صفحة التحويلات
# -----------------------------------
@main_bp.route('/transactions')
@login_required
def transactions():

    # جلب جميع العمليات من قاعدة البيانات
    all_transactions = Transaction.query.order_by(
        Transaction.created_at.desc()
    ).all()

    # حساب إجمالي المبالغ
    total_amount = sum(
        t.amount for t in all_transactions
    )

    return render_template(
        'transactions.html',
        user=current_user,
        transactions=all_transactions,
        total_amount=total_amount
    )




# -----------------------------------
# إدارة المحافظ
# -----------------------------------
@main_bp.route('/wallets', methods=['GET', 'POST'])
@login_required
def wallets():

    # إضافة محفظة جديدة
    if request.method == 'POST':

        wallet_name = request.form.get(
            'wallet_name'
        )

        wallet_address = request.form.get(
            'wallet_address'
        )

        network = request.form.get(
            'network'
        )

        # إنشاء محفظة
        new_wallet = Wallet(
            wallet_name=wallet_name,
            wallet_address=wallet_address,
            network=network
        )

        db.session.add(new_wallet)

        db.session.commit()

        flash(
            'تم إضافة المحفظة بنجاح',
            'success'
        )

        return redirect(
            url_for('main.wallets')
        )

    # جلب المحافظ
    all_wallets = Wallet.query.order_by(
        Wallet.id.desc()
    ).all()

    return render_template(
        'wallets.html',
        user=current_user,
        wallets=all_wallets
    )









@main_bp.route('/active-wallet', methods=['GET', 'POST'])
@login_required
def active_wallet():
    # 1. معالجة إضافة محفظة جديدة عند إرسال النموذج
    if request.method == 'POST':
        wallet_name = request.form.get('wallet_name')
        wallet_address = request.form.get('wallet_address')
        network = request.form.get('network')
        
        # إنشاء كائن المحفظة الجديد
        new_wallet = Wallet(
            wallet_name=wallet_name, 
            wallet_address=wallet_address, 
            network=network
        )
        
        db.session.add(new_wallet)
        db.session.commit()
        
        flash('تم إضافة المحفظة بنجاح', 'success')
        return redirect(url_for('main.active_wallet'))
    
    # 2. جلب جميع المحافظ وترتيبها من الأحدث للأقدم لعرضها في الجدول
    all_active_wallets = Wallet.query.order_by(Wallet.id.desc()).all()
    
    # تم تغيير اسم المتغير المرسل هنا إلى 'wallets' ليتطابق تماماً مع ملف HTML
    return render_template('active_wallet.html', user=current_user, wallets=all_active_wallets)
