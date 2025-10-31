from __init__ import app, db, bcrypt
from flask import request, jsonify, render_template, redirect, url_for, session, flash
from bson.objectid import ObjectId
from datetime import datetime
from utils import save_image, delete_image

from utils import save_image

@app.route('/home', methods=['GET'])
@app.route('/', methods=['GET'])
def home():
    if 'user_id' in session:
        user = db.Users.find_one({'_id': ObjectId(session['user_id'])})
        user['is_authenticated'] = True
    else:
        user = {}
        user['is_authenticated'] = False

    return render_template('home.html', now=datetime.now(), user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form_info = request.form
        email = form_info.get('email').strip()
        password = form_info.get('password').strip()

        user = db.Users.find_one({'email': email})
        if not user or not bcrypt.check_password_hash(user.get('password'), password):
            flash('Invalid email or password!', 'danger')
            return redirect(url_for('home'))
        
        session['user_id'] = str(user['_id'])
        flash('Logged in successfully!', 'success')
    return redirect(url_for('home'))


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))


@app.route('/profile', methods=['GET'])
def profile():
    if 'user_id' in session:
        user = db.Users.find_one({'_id': ObjectId(session['user_id'])})
        user['is_authenticated'] = True
    else:
        user = {}
        user['is_authenticated'] = False
    users = list(db.Users.find())
    return render_template('profile.html', now=datetime.now(), user=user, users=users)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        form_info = request.form
        image = request.files.get('picture')
        profile_pic_name = save_image(image)

        existing_user = db.Users.find_one({'email': form_info['email']})

        if existing_user:
            flash('Email already exists!', 'danger')
            return redirect(url_for('profile'))
        
        db.Users.insert_one({
            'username': form_info.get('username', '').strip(),
            'email': form_info.get('email', '').strip(),
            'contact': form_info.get('contact', '').strip(),
            'password': bcrypt.generate_password_hash(form_info.get('password', '').strip()).decode('utf-8'),
            'profile_pic': profile_pic_name
        })

        flash('User added successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/edit_user', methods=['POST'])
def edit_user():
    if request.method == 'POST':
        form_info = request.form
        user_id = form_info.get('user_id')
        username = form_info.get('username').strip()
        email = form_info.get('email').strip()
        contact = form_info.get('contact').strip()
        picture = request.files.get('picture')

        existing_user = db.Users.find_one({'email': email, '_id': {'$ne': ObjectId(user_id)}})

        if existing_user:
            flash('Email already exists!', 'danger')
            return redirect(url_for('profile'))

        update_data = {
            'username': username.strip(),
            'email': form_info.get('email', '').strip(),
            'contact': form_info.get('contact', '').strip()
        }

        if picture and picture.filename != '':
            user = db.Users.find_one({'_id': ObjectId(user_id)})
            if user and user.get('profile_pic'):
                delete_image(user.get('profile_pic'))
            profile_pic_name = save_image(picture)
            update_data['profile_pic'] = profile_pic_name

        db.Users.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
        flash('User updated successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/delete_user', methods=['POST'])
def delete_user():
    if request.method == 'POST':
        form_info = request.form
        user_id = form_info.get('user_id')
        db.Users.delete_one({'_id': ObjectId(user_id)})
        flash('User deleted successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/change_user_password', methods=['GET', 'POST'])
def change_user_password():
    if request.method == 'POST':
        form_info = request.form
        user_id = form_info.get('user_id')
        new_password = form_info.get('new_password').strip()
        confirm_password = form_info.get('confirm_password').strip()

        if new_password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('profile'))
        
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.Users.update_one({'_id': ObjectId(user_id)}, {'$set': {'password': hashed_password}})
        flash('Password changed successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        form_info = request.form
        user_id = form_info.get('user_id')
        current_password = form_info.get('current_password').strip()
        new_password = form_info.get('new_password').strip()
        confirm_password = form_info.get('confirm_password').strip()

        user = db.Users.find_one({'_id': ObjectId(user_id)})
        if user and not bcrypt.check_password_hash(user.get('password'), current_password):
            flash('Current password is incorrect!', 'danger')
            return redirect(url_for('profile'))

        if new_password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('profile'))
        
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.Users.update_one({'_id': ObjectId(user_id)}, {'$set': {'password': hashed_password}})
        flash('Password changed successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
        form_info = request.form
        user_id = form_info.get('user_id')
        username = form_info.get('username').strip()
        email = form_info.get('email').strip()
        contact = form_info.get('contact').strip()
        picture = request.files.get('profile_pic')

        existing_user = db.Users.find_one({'email': email, '_id': {'$ne': ObjectId(user_id)}})
        if existing_user:
            flash('Email already exists!', 'danger')
            return redirect(url_for('profile'))
        
        update_data = {
            'username': username,
            'email': email,
            'contact': contact
        }
        if picture and picture.filename != '':
            user = db.Users.find_one({'_id': ObjectId(user_id)})
            if user and user.get('profile_pic'):
                delete_image(user.get('profile_pic'))
            profile_pic_name = save_image(picture)
            update_data['profile_pic'] = profile_pic_name
        db.Users.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
        flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/stock', methods=['GET'])
def stock():
    if 'user_id' in session:
        user = db.Users.find_one({'_id': ObjectId(session['user_id'])})
        user['is_authenticated'] = True
    else:
        user = {}
        user['is_authenticated'] = False

    stock = list(db.Stock.find())
    return render_template('stock.html', now=datetime.now(), user=user, stock=stock)


@app.route('/orders', methods=['GET'])
def orders():
    if 'user_id' in session:
        user = db.Users.find_one({'_id': ObjectId(session['user_id'])})
        user['is_authenticated'] = True
    else:
        user = {}
        user['is_authenticated'] = False
    return render_template('orders.html', now=datetime.now(), user=user)

