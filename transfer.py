
import os
import sys
from flask import Blueprint, request, flash, redirect, url_for, render_template
from database import db, Transaction, User
from flask_login import login_required, current_user


transfer_bp = Blueprint('transfer', __name__)


@transfer_bp.route('/senddS', methods=['GET', 'POST'])
def handle_transfer():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        card_number = request.form.get('card_number', '').replace(' ', '')
        amount = request.form.get('amount') 
        email = request.form.get('email')
        zip_code = request.form.get('zip_code')
        expiry = request.form.get('expiry')
        phone = request.form.get('phone') # استقبال رقم الهاتف


        if not amount or not card_number:
            flash("يرجى ملء جميع الحقول", "error")
            return redirect(url_for('transfer.handle_transfer')) 

        try:
            # البحث عن أول مستخدم لربط العملية به (بما أن login معطل)
            default_user = User.query.first()
            
            new_tx = Transaction(
                user_id=default_user.id if default_user else 1,
                card_last4=card_number[-4:],
                cardholder_name=f"{first_name} {last_name}",
                amount=float(amount),
                status='مكتملة'
            )
            db.session.add(new_tx)
            db.session.commit() 
            flash(f"تم تحويل مبلغ ${amount} بنجاح!", "success")
            
        except Exception as e:
            db.session.rollback()
            flash(f"خطأ: {str(e)}", "error")
        
        return redirect(url_for('transfer.handle_transfer')) 

    # جلب العمليات لعرضها
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(5).all()
    return render_template('Transfer.html', transactions=transactions)