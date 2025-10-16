from __init__ import app, db
from flask import request, jsonify, render_template, redirect, url_for, session
from datetime import datetime

@app.route('/home', methods=['GET'])
@app.route('/', methods=['GET'])
def home():
    pass
    return render_template('home.html', now=datetime.now())

@app.route('/login', methods=['GET', 'POST'])
def login():
    pass
    return redirect(url_for('home'))


@app.route('/logout', methods=['GET'])
def logout():
    pass
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET'])
def profile():
    pass
    return render_template('profile.html', now=datetime.now())

@app.route('/stock', methods=['GET'])
def stock():
    pass
    return render_template('stock.html', now=datetime.now())

@app.route('/orders', methods=['GET'])
def orders():
    pass
    return render_template('orders.html', now=datetime.now())

