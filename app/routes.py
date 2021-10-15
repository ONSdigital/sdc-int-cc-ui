from app import app
from flask import render_template


@app.route('/')
async def home():
    return render_template('home.html')
