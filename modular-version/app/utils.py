from flask import render_template
from xhtml2pdf import pisa
from .models import Users
import tempfile, re

def CkName(name: str):
    errors = []
    if not name: 
        errors.append("The name can't be empty.")    
    if len(name) < 2 or len(name) > 50: 
        errors.append("There are no names of only 2 letters.")
    if not re.match(r"^[A-Za-z\s]+$", name): 
        errors.append("There is an error in the name.")
    if errors: 
        return False, " ".join(errors)
    return True, ""

def CkPassword(password: str):
    errors = []
    if len(password) < 8: 
        errors.append("The password must contain at least 8 characters.")
    if not re.search("[a-z]", password): 
        errors.append("The password must contain at least one lowercase letter.")
    if not re.search("[A-Z]", password): 
        errors.append("The password must contain at least one uppercase letter.")
    if not re.search("[0-9]", password): 
        errors.append("The password must contain at least one number.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): 
        errors.append("The password must contain at least one special character.")
    if " " in password: 
        errors.append("The password must not contain spaces.")
    if re.search(r"(.)\1{3,}", password): 
        errors.append("The password must not contain 4 or more consecutive identical characters.")
    common_passwords = {"password", "12345678", "qwerty", "abc123", "letmein", "welcome"}
    if password.lower() in common_passwords: 
        errors.append("The password is too common and easily guessable. Please choose a stronger password.")
    if errors: 
        return False, " ".join(errors)
    return True, ""

def CkEmail(email: str):
    errors = []
    if not re.match(r"^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$", email): 
        errors.append("The email address format is invalid.")
    if Users.query.filter(Users.email.ilike(email)).first(): 
        errors.append("The email address already exists.")
    blacklist = {"tempmail.com", "10minutemail.com", "mailinator.com", "example.com", "email.com", "email.it"}
    domain = email.split('@')[-1].lower()
    if domain in blacklist: 
        errors.append("Email addresses from this domain are not allowed.")
    if errors: 
        return False, " ".join(errors)
    return True, ""

def ErrorRedirect(code, message):
    return render_template('error.html', code=code, message=message)

def DateFormat(date):
    return date.strftime('%B %d, %Y')

def CkKeys(keywords, bad_words):
    if not keywords:
        return "Error: The search input cannot be empty."
    keywords = keywords.lower()
    for word in bad_words:
        if word in keywords:
            return f"Error: The input contains a forbidden word: {word}"
    return "Valid input"

def Convert(html):
    file = tempfile.NamedTemporaryFile(delete = False, suffix = ".pdf")
    pisa_status = pisa.CreatePDF(html, dest = file)
    if pisa_status.err:
        print("Error in the creation of the file:", pisa_status.err)
    file.close()
    return file.name
