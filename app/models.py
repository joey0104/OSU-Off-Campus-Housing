from app.__init__ import db

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    fullname = db.Column(db.String(100), nullable=False, unique=True)
    password= db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    liked=db.Column(db.String(500))
    pic_address=db.Column(db.Text)
    bio=db.Column(db.Text)
    post_address=db.Column(db.Text)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address=db.Column(db.String(200), nullable=False, unique=True)
    rent = db.Column(db.String(200), nullable=False)
    bathroom = db.Column(db.String(200), nullable=False)
    bedroom = db.Column(db.String(200), nullable=False)
    detail_url = db.Column(db.String(200), nullable=False, unique=False)
    amenities= db.Column(db.String(200), nullable=False)
    info=db.Column(db.Text)
    liked = db.Column(db.String(500))
    type= db.Column(db.String(200), nullable=False)
    pic_address = db.Column(db.Text)