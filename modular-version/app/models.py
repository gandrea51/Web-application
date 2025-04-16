from datetime import datetime
from flask_login import UserMixin
from . import db

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    genre = db.Column(db.Enum('Man', 'Woman', 'Other'), nullable=False)
    role = db.Column(db.Enum('President', 'Staff', 'Client'), nullable=False)
    created_at = db.Column(db.DateTime)

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    publication_date = db.Column(db.Date, nullable=False)
    language = db.Column(db.Enum('English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text, nullable=False)
    position = db.Column(db.String(50), nullable=False)
    copy = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.Date, nullable=False)

class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(100), nullable=False) 
    description = db.Column(db.Text, nullable=False)
    teacher = db.Column(db.String(100), nullable=False)
    language = db.Column(db.Enum('English', 'Spanish', 'French', 'German', 'Italian'), nullable=False)
    level = db.Column(db.Enum('Beginner', 'Intermediate', 'Advanced'), nullable=False)
    period = db.Column(db.Text, nullable=False)
    place = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    seats = db.Column(db.Integer, nullable=False) 

class Loans(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum("Pending confirmation", "Confirmed", "Soon to expire", "Expired", "Extended", "Terminated"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    book = db.relationship('Books', backref=db.backref('loans', lazy=True))
    user = db.relationship('Users', backref=db.backref('loans', lazy=True))

class Bookings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum("Reservation pending", "Payment requested", "Payment received", "Reservation confirmed", "Reservation cancelled"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    course = db.relationship('Courses', backref=db.backref('bookings', lazy=True))
    user = db.relationship('Users', backref=db.backref('bookings', lazy=True))   

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.Date, nullable=False)

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.Text, nullable=False)
    question = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    user = db.relationship('Users', backref=db.backref('questions', lazy=True))

class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    object = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    
    user = db.relationship('Users', backref=db.backref('answers', lazy=True))    
    question = db.relationship('Questions', backref=db.backref('answers', lazy=True))
