from datetime import datetime, timedelta
from flask_login import UserMixin
from app import db
class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(80),nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(255),nullable=False)
    image=db.Column(db.String(255),default='default_profile.png')
    role=db.Column(db.String(20),default='user')
    jobs=db.relationship('Job',backref='author',lazy=True)
class Job(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(150),nullable=False)
    short_desc=db.Column(db.String(300),nullable=False)
    full_desc=db.Column(db.Text,nullable=False)
    company=db.Column(db.String(120),nullable=False)
    salary=db.Column(db.String(80))
    location=db.Column(db.String(120))
    category=db.Column(db.String(50))
    date_posted=db.Column(db.DateTime,default=datetime.utcnow)
    expire_date=db.Column(db.DateTime,default=lambda: datetime.utcnow()+timedelta(days=7))
    is_pinned=db.Column(db.Boolean,default=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
