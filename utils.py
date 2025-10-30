from flask import app, request, jsonify, render_template, redirect, url_for, session
import os, secrets

def save_image(file):
    if not file or file.filename == '':
        return None
    ext = os.path.splitext(file.filename)[1]
    filename = secrets.token_hex(16) + ext
    folder = os.path.join(os.getcwd(), 'static/images')
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, filename))
    return filename


def delete_image(filename):
    file_path = os.path.join(os.getcwd(), 'static/images', filename)
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass