from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_seeder import FlaskSeeder

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = "<4fdb3f0b1459bcf1f54b52bcea27bae24748d23fa31495b8>"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/flasksite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)
seeder = FlaskSeeder(app, db)

from AAT import routes
