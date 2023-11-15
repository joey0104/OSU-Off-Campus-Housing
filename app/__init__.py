from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#create flask instance
UPLOAD_FOLDER='static/images/'
app=Flask(__name__)

#add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db' # can adjust the name
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

#initialize the databse
db = SQLAlchemy(app)

from app import view
from app import models