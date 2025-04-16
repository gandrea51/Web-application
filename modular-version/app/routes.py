from flask import Blueprint, render_template, url_for, flash, redirect, abort, request, session, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, or_
from app import db
from app.models import Users, Books, Courses, Messages, Questions, Loans, Bookings, Answers
from app.utils import CkEmail, CkName, CkPassword, CkKeys, ErrorRedirect, DateFormat, Convert
import math, random
from datetime import datetime, date, timedelta, timezone

function = Blueprint('routes', __name__)

@function.context_processor
def inject():
    if current_user.is_authenticated:
        return {'current': current_user}
    return {'current': None}

bads = {"drop", "alter", "create", "update", "delete", "insert", "shutdown", "truncate", "exec", "execute", "script", "cmd", "bash", "rm", "shutdown", "sudo", "reboot", "chown", "chmod"}

@function.route("/", methods=["GET"])
def welcome():
    '''Welcome page'''
    return render_template("welcome.html")

@function.route("/about", methods=["GET"])
@login_required
def about():
    '''About page'''
    return render_template("about.html")

@function.route('/contact', methods=["GET", "POST"])
@login_required
def contact():
    '''Write a new message for the library'''

    if request.method == "GET":
        return render_template('contact.html')
    
    name = request.form.get('name')
    message = request.form.get('message')

    is_valid, error_message = CkName(name)
    if not is_valid:
        flash(error_message, 'danger')
        return redirect(url_for('routes.contact'))

    error_message = CkKeys(message, bads)
    if error_message != "Valid input":
        flash(error_message, 'danger')
        return redirect(url_for('routes.contact'))
    
    try: 
        message = Messages(name=name, message=message, created_at=date.today())
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('routes.welcome'))
    except Exception as e:
        flash("An error occurred while sending your message. Please try again.", 'danger')
        return redirect(url_for('routes.contact'))

@function.route('/ask', methods=["POST"])
@login_required
def ask():
    '''Ask a new message for the library'''
    
    data = request.form.get('data')
    question = request.form.get('question')
    
    error_message = CkKeys(question, bads)
    if error_message != "Valid input":
        flash(error_message, 'danger')
        return redirect(url_for('routes.ask'))

    try: 
        question = Questions(data=data, question=question, created_at=date.today(), user_id=current_user.id)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('routes.explore'))
    except Exception as e:
        flash("An error occurred while sending your question. Please try again.", 'danger')
        return redirect(url_for('routes.explore'))

@function.route('/answer/<int:id>', methods=["POST"])
@login_required
def answer(id):
    '''Answer a question'''
    
    question = Questions.query.get(id)
    if not question:
        ErrorRedirect(404, "The request question can not be find! Try again.")

    object = request.form.get('object')
    body = request.form.get('body')

    try: 
        answer = Answers(object=object, body=body, created_at=date.today(), user_id=question.user_id, question_id=question.id)
        db.session.add(answer)
        db.session.commit()
        return redirect(url_for('routes.message'))
    except Exception as e:
        flash("An error occurred while sending your question. Please try again.", 'danger')
        return redirect(url_for('routes.message'))


@function.route('/message', methods=["GET"])
@login_required
def message():
    '''Message page'''

    messages = Messages.query.all()
    path = '/static/images/read_one.jpeg'
    unit = random.randint(1, 2)
    if unit == 1:
        path = '/static/images/read_two.jpeg'

    questions = Questions.query.all()
    return render_template('message.html', messages=messages, path=path, questions=questions)

@function.route('/message/<int:id>/drop', methods=["POST"])
@login_required
def mdrop(id):
    '''Delete an existing message'''

    message = Messages.query.get(id)
    if not message:
        ErrorRedirect(404, "The request message can not be find! Try again.")

    try:
        db.session.delete(message)
        db.session.commit()
        return redirect(url_for('routes.message'))
    except Exception as e:
        ErrorRedirect(500, "An error occurred while deleting the message. Please try again.")

@function.route('/explore', methods=["GET"])
@login_required
def explore():
    '''Explore page'''
    return render_template('explore.html')

@function.route('/signup', methods=['GET', 'POST'])
def signup():
    '''Sign up a new user'''
    
    if request.method == 'GET':
        first = random.randint(1, 10)
        second = random.randint(1, 10)
        question = f"How much is {first} + {second}?"
        session['answer'] = str(first + second)
        return render_template('signup.html', question=question)

    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm = request.form.get('confirm')
    genre = request.form.get('genre')
    answer = request.form.get('answer')

    if answer != session.get('answer'):
        flash("Incorrect CAPTCHA answer. Try again!", 'danger')
        return redirect(url_for('routes.signup'))

    is_valid, error_message = CkName(name)
    if not is_valid:
        flash(error_message, 'danger')
        return redirect(url_for('routes.signup'))
    
    is_valid, error_message = CkEmail(email)
    if not is_valid:
        flash(error_message, 'danger')
        return redirect(url_for('routes.signup'))
    
    is_valid, error_message = CkPassword(password)
    if not is_valid:
        flash(error_message, 'danger')
        return redirect(url_for('routes.signup'))
    
    if password != confirm:
        flash("The password not correspond", 'danger')
        return redirect(url_for('routes.signup'))

    try:
        encrypt = generate_password_hash(password)
        user = Users(name=name, email=email, password=encrypt, genre=genre, role='President', created_at=date.today())
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('routes.welcome'))
    except Exception as e:
        flash("An error occurred while creating your account. Please try again.", 'danger')
        return redirect(url_for('routes.signup'))

@function.route('/signin', methods=["GET", "POST"])
def signin():
    '''Sign in an existing user'''

    if request.method == 'GET':
        first = random.randint(1, 10)
        second = random.randint(1, 10)
        question = f"How much is {first} + {second}?"
        session['answer'] = str(first + second)
        return render_template('signin.html', question=question)
    
    email = request.form.get('email')
    password = request.form.get('password')   
    confirm = request.form.get('confirm')
    answer = request.form.get('answer')
    
    if answer != session.get('answer'):
        flash("Incorrect CAPTCHA answer. Try again!", 'danger')
        return redirect(url_for('routes.signup'))

    user = Users.query.filter_by(email=email).first()
    if user is None:
        flash("The email address is not registered. Try again!", 'danger')
        return redirect(url_for('routes.signin'))
    
    if check_password_hash(user.password, password) == False:
        flash("The password is incorrect. Try again!", 'danger')
        return redirect(url_for('routes.signin'))

    if password != confirm: 
        flash("The password not correspond", 'danger')
        return redirect(url_for('routes.signin')) 

    try:
        login_user(user)
        return redirect(url_for('routes.welcome'))       
    except Exception as e:
        flash("An error occurred while acceding your account. Please try again.", 'danger')
        return redirect(url_for('routes.signin'))

@function.route('/signout')
@login_required
def signout():
    '''Sign out the current user'''
    logout_user()
    return redirect(url_for('routes.welcome'))

@function.route('/user/<int:id>', methods=["GET"])
@login_required
def profile(id):
    '''User profile page'''
    
    user = db.session.get(Users, id)
    if not user:
        ErrorRedirect(404, "The request user can not be find! Try again.")

    loans = Loans.query.filter_by(user_id=user.id).all()
    bookings = Bookings.query.filter_by(user_id=user.id).all()
   
    return render_template('profile.html', loans=loans, bookings=bookings)

@function.route('/book', methods=["GET"])
@login_required
def book():
    '''Book page'''

    genres = Books.query.with_entities(Books.genre, func.count(Books.genre)).group_by(Books.genre).order_by(Books.genre).all()
    realise = Books.query.filter_by(author="Albert Camus").order_by(Books.title).first()
    classic = Books.query.filter_by(author="Virginia Woolf").order_by(Books.title).first()
    new = Books.query.filter_by(author="Gabriel García Márquez").order_by(Books.title).first()
    return render_template('book.html', genres=genres, realise=realise, classic=classic, new=new)

@function.route('/book/genre', methods=["POST"])
def genre():
    if request.method not in ["POST"]: 
        abort(405)

    selected = request.form.get('genre')
    books = Books.query.filter_by(genre=selected).order_by(Books.title).all()
    return render_template('bgenre.html', books=books, genre=selected)

@function.route('/book/keyword', methods=["POST"])
@login_required
def bkeywords():
    '''Search books by keywords'''

    keywords = request.form.get('keywords')    

    validation_result = CkKeys(keywords, bads)
    if validation_result != "Valid input":
        flash(validation_result, 'danger')
        return redirect(url_for('routes.book'))

    search_keywords = [word.strip() for word in keywords.split(',')]
    books = Books.query.filter(or_(*[Books.keywords.ilike(f'%{keyword}%') for keyword in search_keywords])).all()
    return render_template('bkey.html', books=books, keywords=keywords)

@function.route('/book/manager', methods=["GET"])
@login_required
def manage_book():
    '''Book manager page'''

    books = Books.query.all()
    return render_template('bmanager.html', books=books)

@function.route('/book/create', methods=["GET", "POST"])
@login_required
def create_book():
    '''Create a new book'''
    if request.method == 'GET':
        return render_template('bpost.html')
    
    book = Books(
        title = request.form['title'],
        author = request.form['author'],
        genre = request.form['genre'],        
        publisher = request.form['publisher'],        
        publication_date = request.form['publication_date'],
        language = request.form['language'],
        description = request.form['description'],
        keywords = request.form['keywords'],
        position = request.form['position'],
        copy = request.form['copy'],
        note = request.form['note'],
        created_at = date.today()
    )

    try:
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('routes.manager_book')) 
    except Exception as e:
        ErrorRedirect(500, "An error occurred while creating the book. Please try again.")
    
@function.route('/book/<int:id>/edit', methods=["GET", "POST"])
@login_required
def edit_book(id):
    '''Edit an existing book'''

    book = Books.query.get(id)
    if not book:
        ErrorRedirect(404, "The request book can not be find! Try again.")  
    
    if request.method == 'GET':
        return render_template('bput.html', book=book)
    
    book.title = request.form['title']
    book.author = request.form['author']
    book.genre = request.form['genre']
    book.publisher = request.form['publisher']
    book.publication_date = request.form['publication_date']
    book.language = request.form['language']
    book.description = request.form['description']
    book.keywords = request.form['keywords']
    book.position = request.form['position']
    book.copy = request.form['copy']
    book.note = request.form['note']

    try:
        db.session.commit()
        return redirect(url_for('routes.manage_book')) 
    except Exception as e:
        ErrorRedirect(500, "An error occurred while updating the book. Please try again.")
    
@function.route('/book/<int:id>/drop', methods=["POST"])
@login_required
def delete_book(id):
    '''Delete an existing book'''

    book = Books.query.get(id)
    if not book:
        ErrorRedirect(404, "The request book can not be find! Try again.")

    try:
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for('routes.manage_book'))
    except Exception as e:
        ErrorRedirect(500, "An error occurred while deleting the book. Please try again.")

@function.route('/borrow/<int:id>', methods=["GET"])
@login_required
def borrow_it(id):
    '''Borrow a book'''

    book = Books.query.get(id)
    if not book:
        ErrorRedirect(404, "The request book can not be find! Try again.")
    book.copy -= 1

    start = date.today()
    loan = Loans(start = start, end = None, status = "Pending confirmation", book_id = book.id, user_id = current_user.id)
    db.session.add(loan)
    db.session.commit()
    return redirect(url_for('routes.book'))

'''Status of the loans: "Pending confirmation", "Confirmed", "Soon to expire", "Expired", "Extended", "Terminated"'''

@function.route('/loan', methods=["GET"])
@login_required
def loan():
    '''Loan page'''
    pendings = Loans.query.filter_by(status="Pending confirmation").all()  
    confirmeds = Loans.query.filter_by(status="Confirmed").all()
    soons = Loans.query.filter_by(status="Soon to expire").all()
    expireds = Loans.query.filter_by(status="Expired").all()
    extendeds = Loans.query.filter_by(status="Extended").all()
    terminateds = Loans.query.filter_by(status="Terminated").all()
    return render_template('loan.html', pendings=pendings, confirmeds=confirmeds, soons=soons, expireds=expireds, extendeds=extendeds, terminateds=terminateds)

@function.route('/loan/<int:id>/confirm', methods=["GET"])
@login_required
def lconfirm(id):
    '''Confirm a loan'''
    
    loan = db.session.get(Loans, id)
    if not loan:
        ErrorRedirect(404, "The request loan can not be find! Try again.")
    
    loan.status = "Confirmed"
    loan.end = loan.start + timedelta(days = 30)
    db.session.commit()
    return redirect(url_for('routes.loan'))

@function.route('/loan/<int:id>/extend', methods=["GET"])
@login_required
def lextend(id):
    '''Extend a loan'''

    loan = db.session.get(Loans, id)
    if not loan:
        ErrorRedirect(404, "The request loan can not be find! Try again.")
    
    loan.status = "Extended"
    loan.end += timedelta(days = 20)
    db.session.commit()
    return redirect(url_for('routes.loan'))

@function.route('/loan/<int:id>/expire', methods=["GET"])
@login_required
def lexpire(id):
    '''Expire a loan'''

    loan = db.session.get(Loans, id)
    if not loan:
        ErrorRedirect(404, "The request loan can not be find! Try again.")
    
    loan.status = "Expired"
    db.session.commit()
    return redirect(url_for('routes.loan'))

@function.route('/loan/<int:id>/term', methods=["GET"])
@login_required
def lterm(id):
    '''Terminate a loan'''

    loan = db.session.get(Loans, id)
    if not loan:
        ErrorRedirect(404, "The request loan can not be find! Try again.")
    
    loan.status = "Terminated"
    loan.end = date.today()
    book = Books.query.get(loan.book_id)
    book.copy += 1
    db.session.commit()
    return redirect(url_for('routes.loan'))

@function.route('/school', methods=["GET"])
@login_required
def school():
    '''School page'''

    advanced = Courses.query.filter_by(level="Advanced").first()
    german = Courses.query.filter_by(language="German").first()
    return render_template('school.html', advanced=advanced, german=german)

@function.route('/discover', methods=["GET"])
@login_required
def discover():
    '''Discover page'''

    courses = Courses.query.all()
    return render_template('sdiscover.html', courses=courses)

@function.route('/school/manager', methods=["GET"])
@login_required
def manage_school():
    '''School manager page'''

    courses = Courses.query.all()
    return render_template('smanager.html', courses=courses)

@function.route('/school/create', methods=["GET", "POST"])
@login_required
def create_school():
    '''Create a new course'''
    if request.method == 'GET':
        return render_template('spost.html')
    
    course = Courses(
        name = request.form['name'],
        subtitle = request.form['subtitle'],        
        description = request.form['description'],
        teacher = request.form['teacher'],
        language = request.form['language'],
        level = request.form['level'],
        period = request.form['period'],
        place = request.form['place'],
        price = request.form['price'],
        seats = request.form['seats']
    )

    try:
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('routes.manage_school')) 
    except Exception as e:
        ErrorRedirect(500, "An error occurred while creating the course. Please try again.")
    
@function.route('/school/<int:id>/edit', methods=["GET", "POST"])
@login_required
def edit_school(id):
    '''Edit an existing course'''

    course = Courses.query.get(id)
    if not course:
        ErrorRedirect(404, "The request course can not be find! Try again.")  
    
    if request.method == 'GET':
        return render_template('sput.html', course=course)
    
    course.name = request.form['name']
    course.subtitle = request.form['subtitle']    
    course.description = request.form['description']
    course.teacher = request.form['teacher']
    course.language = request.form['language']
    course.level = request.form['level']
    course.period = request.form['period']
    course.place = request.form['place']
    course.price = request.form['price']
    course.seats = request.form['seats']

    try:
        db.session.commit()
        return redirect(url_for('routes.manage_school')) 
    except Exception as e:
        ErrorRedirect(500, "An error occurred while updating the course. Please try again.")

@function.route('/school/<int:id>/drop', methods=["POST"])
@login_required
def delete_school(id):
    '''Delete an existing course'''

    course = Courses.query.get(id)
    if not course:
        ErrorRedirect(404, "The request course can not be find! Try again.")

    try:
        db.session.delete(course)
        db.session.commit()
        return redirect(url_for('routes.manage_school'))
    except Exception as e:
        ErrorRedirect(500, "An error occurred while deleting the course. Please try again.")

@function.route('/reserve/<int:id>', methods=["GET"])
@login_required
def reserve(id):
    '''Reserve a course'''
    
    course = db.session.get(Courses, id)
    if not course:
        ErrorRedirect(404, "The request course can not be find! Try again.")

    bookings = Bookings(created_at = date.today(), status = "Reservation pending", course_id = course.id, user_id = current_user.id)
    course.seats -= 1

    db.session.add(bookings) 
    db.session.commit()
    return redirect(url_for('routes.school'))

'''State of the bookings: "Reservation pending", "Payment requested", "Payment received", "Reservation confirmed", "Reservation cancelled"'''

@function.route('/booking', methods=["GET"])
@login_required
def booking():
    '''Booking page'''
    pendings = Bookings.query.filter_by(status="Reservation pending").all()  
    nopays = Bookings.query.filter_by(status="Payment requested").all()
    pays = Bookings.query.filter_by(status="Payment received").all()
    confirmeds = Bookings.query.filter_by(status="Reservation confirmed").all()
    cancelleds = Bookings.query.filter_by(status="Reservation cancelled").all()
    return render_template('booking.html', pendings=pendings, nopays=nopays, pays=pays, confirmeds=confirmeds, cancelleds=cancelleds)

@function.route('/request/<int:id>', methods=["GET"])
@login_required
def brequest(id):
    '''Request the payment'''
    
    booking = Bookings.query.get(id)
    if not booking:
        ErrorRedirect(404, "The request course can not be find! Try again.")

    booking.status = "Payment requested"
    db.session.commit()
    return redirect(url_for('routes.school'))

@function.route('/booking/<int:id>/pay', methods=["GET"])
@login_required
def bpay(id):
    '''Payment receive'''
    
    booking = Bookings.query.get(id)
    if not booking:
        ErrorRedirect(404, "The request course can not be find! Try again.")

    booking.status = "Payment received"
    db.session.commit()
    return redirect(url_for('routes.school'))

@function.route('/booking/<int:id>/confirm', methods=["GET"])
@login_required
def bconfirm(id):
    '''Confirm a booking'''
    
    booking = Bookings.query.get(id)
    if not booking:
        ErrorRedirect(404, "The request course can not be find! Try again.")

    booking.status = "Reservation confirmed"
    db.session.commit()
    return redirect(url_for('routes.school'))

@function.route('/booking/<int:id>/cancel', methods=["GET"])
@login_required
def bcancel(id):
    '''Cancelling a booking'''

    booking = Bookings.query.get(id)
    if not booking:
        ErrorRedirect(404, "The request course can not be find! Try again.")
    course = db.session.get(Courses, booking.course_id)
    if not course:
        ErrorRedirect(404, "The request course can not be find! Try again.")

    booking.status = "Reservation cancelled"
    course.seats += 1
    db.session.commit()
    return redirect(url_for('routes.school'))

