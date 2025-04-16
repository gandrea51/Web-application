from flask import *
from flask_sqlalchemy import *
from flask_login import *
from werkzeug.security import *
from sqlalchemy import *
from datetime import *
from xhtml2pdf import pisa
import math
import tempfile
import re

'''
    CONFIGURAZIONI
'''
app = Flask(__name__)
app.config['SECRET_KEY'] = 'why would I tell you my secret key?'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://andrea:password@localhost/Ancescao'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)

'''
    CLASSI
'''
class Utente(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    telefono = db.Column(db.String(100))
    ruolo = db.Column(db.String(100))

class Libro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(255), nullable=False)
    anno = db.Column(db.String(255), nullable=False)
    classificazione = db.Column(db.String(255), nullable=False)
    posizione = db.Column(db.String(255), nullable=False)
    autore = db.Column(db.String(255), nullable=False)
    genere = db.Column(db.String(255), nullable=False)
    collana = db.Column(db.String(255))
    editore = db.Column(db.String(255), nullable=False)
    note = db.Column(db.Text)
    copie = db.Column(db.Integer, nullable=False)
    disponibile = db.Column(db.String(255), nullable=False)
    libro_mese = db.Column(db.String(255), nullable=False, default='No')
    rivista = db.Column(db.String(255), nullable=False, default='No')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    viste = db.Column(db.Integer, default=0)
    download = db.Column(db.Integer, default=0)

class Prestito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uscita = db.Column(db.Date, nullable=False)
    rientro = db.Column(db.Date, nullable=False)
    terminato = db.Column(db.String(2), nullable=False)
    prorogato = db.Column(db.String(2), nullable=False)
    libro_id = db.Column(db.BigInteger, db.ForeignKey('libro.id'), nullable=False)
    utente_id = db.Column(db.BigInteger, db.ForeignKey('utente.id'), nullable=False)

    libro = db.relationship('Libro', backref=db.backref('prestiti', lazy=True))
    utente = db.relationship('Utente', backref=db.backref('prestiti', lazy=True))

class Corso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False, unique=True)
    programma = db.Column(db.Text, nullable=False)
    docente = db.Column(db.String(255), nullable=False)
    giorno = db.Column(db.String(255), nullable=False)
    lezioni = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text)
    partenza = db.Column(db.Date)
    minimo = db.Column(db.Integer, nullable=False)
    massimo = db.Column(db.Integer, nullable=False)
    contributo = db.Column(db.Numeric(5,2), nullable=False)
    tessera = db.Column(db.Numeric(5,2), nullable=False)
    prenotazioni = db.Column(db.Integer, nullable=False)
    iscrizioni = db.Column(db.Integer, nullable=False)
    viste = db.Column(db.Integer, default=0)

class Prenotazioni(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stato = db.Column(db.String(255), nullable=False)
    corso_id = db.Column(db.Integer, db.ForeignKey('corso.id'), nullable=False)
    utente_id = db.Column(db.Integer, db.ForeignKey('utente.id'), nullable=False)

    corso = db.relationship('Corso', backref=db.backref('prenotazioni_corso', lazy=True))
    utente = db.relationship('Utente', backref=db.backref('prenotazioni_utente', lazy=True))   

'''
    FUNZIONI GENERICHE
'''

@app.context_processor
def inject_user():
    if current_user.is_authenticated:
        return {'current_user': current_user}
    return {'current_user': None}

@login_manager.user_loader
def load_user(user_id):
    user_id = int(user_id)
    return db.session.get(Utente, user_id)

def convert(html):
    file = tempfile.NamedTemporaryFile(delete = False, suffix = ".pdf")
    pisa_status = pisa.CreatePDF(html, dest = file)
    if pisa_status.err:
        print("Errore durante la creazione del PDF:", pisa_status.err)
    file.close()
    return file.name

def is_password_valid(password):
    if len(password) < 8:
        return False, "La password deve contenere almeno 8 caratteri."
    if not re.search("[a-z]", password):
        return False, "La password deve contenere almeno una lettera minuscola."
    if not re.search("[A-Z]", password):
        return False, "La password deve contenere almeno una lettera maiuscola."
    if not re.search("[0-9]", password):
        return False, "La password deve contenere almeno un numero."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): 
        return False, "La password deve contenere almeno un simbolo."
    return True, ""

def is_email_valid(email):
    if Utente.query.filter_by(email = email).first() is not None:
        return False, "L'indirizzo email è già presente."
    return True, ""

'''
    HOME PAGE
'''
@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/home')
@login_required
def home():
    if current_user.is_authenticated:
        if current_user.ruolo == 'Amministratore':
            user_count = Utente.query.filter_by(ruolo = 'Socio').count()
            prestiti_in_corso = Prestito.query.filter_by(terminato = "No").count()
            prenotazioni_count = Prenotazioni.query.count()
            return render_template('home.html', utente = current_user, user_count = user_count,
                prestiti_in_corso = prestiti_in_corso,
                prenotazioni_count = prenotazioni_count)
        else:
            return render_template('home.html', utente = current_user)
    else:
        return redirect(url_for(login))

@app.route('/documentazione')
@login_required
def info():
    return render_template('documentazione.html')

@app.route('/gruppo_lettura')
@login_required
def gruppo_lettura():
    month = Libro.query.filter_by(libro_mese = 'Si').first()   
    return render_template('gruppo_lettura.html', month = month)

'''
    UTENTI
'''
@app.route('/registrazione', methods=['GET', 'POST'])
def registrazione():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        is_valid, error_message = is_email_valid(email)
        if not is_valid:
            flash(error_message, 'danger')
            return redirect(url_for('registrazione'))
        
        password = request.form.get('password')
        is_valid, error_message = is_password_valid(password)
        if not is_valid:
            flash(error_message, 'danger')
            return redirect(url_for('registrazione'))
        password = generate_password_hash(password)

        telefono = request.form.get('telefono')
        ruolo = request.form.get('ruolo')
        utente = Utente(nome = nome, email = email, password = password, telefono = telefono, ruolo = ruolo)
        db.session.add(utente)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('registrazione.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        utente = Utente.query.filter_by(email = email).first()
        if utente and check_password_hash(utente.password, password):
            login_user(utente)
            return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('welcome'))

@app.route('/cambia_password', methods=['GET', 'POST'])
def cambia_password():
    if request.method == 'POST':
        vecchia = request.form.get('vecchia')
        nuova = request.form.get('nuova')
        is_valid, error_message = is_password_valid(nuova)
        if not is_valid:
            flash(error_message, 'danger')
            return redirect(url_for('cambia_password'))
        nuova = generate_password_hash(nuova)

        if check_password_hash(current_user.password, vecchia):
            current_user.password = generate_password_hash(nuova)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return render_template('error.html', error_message="Errore! La vecchia password non è corretta.")
    return render_template('cambia_password.html')

@app.route('/cambia_email', methods=['GET', 'POST'])
def cambia_email():
    if request.method == 'POST':
        nuova = request.form.get('nuova')
        if Utente.query.filter_by(email = nuova).first() is not None:
           return render_template('error.html', error_message="Errore! L\'email inserita è già in uso.")

        current_user.email = nuova
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('cambia_email.html')

@app.route('/cambia_telefono', methods=['GET', 'POST'])
def cambia_telefono():
    if request.method == 'POST':
        nuovo = request.form.get('nuovo')

        current_user.telefono = nuovo
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('cambia_telefono.html')

@app.route('/utenti', methods=['GET'])
@login_required
def index_utente():
    utenti = Utente.query.all()
    for utente in utenti:
        utente.prestiti_count = Prestito.query.filter_by(utente_id=utente.id).count()
        utente.prenotazioni_count = Prenotazioni.query.filter_by(utente_id=utente.id).count()
    return render_template('utente_index.html', utenti = utenti)

@app.route('/utente/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def utente_edit(id):
    utente = db.session.get(Utente, id)
    if not utente:
        return render_template('error.html', error_message="Errore! L\'utente richiesto non è stato trovato.")
    if request.method == 'POST':
        utente.email = request.form['email'],
        utente.telefono = request.form['telefono']
        db.session.commit()
        return redirect(url_for('index_utente'))    
    return render_template('utente_edit.html', utente = utente)

@app.route('/utenti/pdf')
@login_required
def utente_pdf():
    utenti = Utente.query.all()
    for utente in utenti:
        utente.prestiti_count = Prestito.query.filter_by(utente_id=utente.id).count()
        utente.prenotazioni_count = Prenotazioni.query.filter_by(utente_id=utente.id).count()
    html = render_template('utente_pdf.html', utenti = utenti)
    pdf = convert(html)    
    return send_file(pdf, as_attachment=True)

@app.route('/utente/<int:utente_id>')
@login_required
def gestisci_profilo(utente_id):      
    utente = db.session.get(Utente, utente_id)  
    messaggio_prestiti, messaggio_prenotazioni = "", ""
    prestiti_attivi = []
    prenotazioni_attive = []

    prestiti = Prestito.query.filter_by(utente_id=utente.id, terminato="No").all()
    if prestiti:
        prestiti_attivi = prestiti
    else:
        messaggio_prestiti = "Non hai ancora effettuato prestiti.<br><br>Scopri la nostra selezione di titoli e approfitta delle offerte esclusive per il tuo prossimo prestito!"

    prenotazioni = Prenotazioni.query.filter_by(utente_id=utente.id).all()
    if prenotazioni:
        prenotazioni_attive = prenotazioni
    else:
        messaggio_prenotazioni = "Non hai ancora effettuato prenotazioni.<br><br>Esplora i corsi disponibili e prenota subito le tue lezioni per approfittare delle offerte speciali!"

    return render_template('utente_profilo.html', utente=current_user,
        prestiti_attivi=prestiti_attivi, prenotazioni_attive=prenotazioni_attive,
        messaggio_prestiti=messaggio_prestiti, messaggio_prenotazioni=messaggio_prenotazioni)

'''
    LIBRI
'''
@app.route('/libri')
def libro_index():
    if current_user.is_authenticated:
        month = Libro.query.filter_by(libro_mese = 'Si').first()
        generi = Libro.query.with_entities(Libro.genere, func.count(Libro.genere)).group_by(Libro.genere).order_by(Libro.genere).all()
        # Statistiche
        total_books = Libro.query.count()
        total_view = db.session.query(db.func.sum(Libro.viste)).scalar() or 0
        total_downloads = db.session.query(db.func.sum(Libro.download)).scalar() or 0
        most_viewed_books = Libro.query.order_by(Libro.viste.desc()).limit(5).all()
        stats = {
            'total_books': total_books,
            'total_views': total_view,
            'total_downloads': total_downloads,
            'most_viewed_books': most_viewed_books
        }
        return render_template('libro_index.html', month = month, generi = generi, stats = stats)
    else:
        # Guest User
        generi = Libro.query.with_entities(Libro.genere, func.count(Libro.genere)).group_by(Libro.genere).order_by(Libro.genere).all()
        return render_template('libro_non_loggato.html', generi = generi)

@app.route('/libri/<genere>')
@login_required
def libro_genere(genere):
    # Query
    libri = Libro.query.filter_by(genere = genere).order_by(Libro.titolo).all()    
    return render_template('libro_genere.html', libri = libri)

@app.route('/libri/<genere>/pdf')
@login_required
def libro_pdf(genere):
    libri = Libro.query.filter_by(genere = genere).order_by(Libro.titolo).all()
    html = render_template('libro_generePDF.html', libri = libri)
    pdf = convert(html)    
    return send_file(pdf, as_attachment=True)

@app.route('/libri/titolo', methods=['POST'])
@login_required
def libro_titolo():
    titolo = request.form.get('titolo')
    libri = Libro.query.filter(Libro.titolo.like(f'%{titolo}%')).all()    
    return render_template('libro_titolo.html', libri = libri)

@app.route('/libri/autore', methods=['POST'])
@login_required
def libro_autore():
    autore = request.form.get('nome')
    libri = Libro.query.filter(Libro.autore.like(f'%{autore}%')).all()    
    return render_template('libro_autore.html', libri = libri)

@app.route('/libri/genere', methods=['POST'])
@login_required
def libro_rgenere():
    genere = request.form.get('nome')
    # Query
    libri = Libro.query.filter(Libro.genere.like(f'%{genere}%')).all()    
    return render_template('libro_rgenere.html', libri = libri)

@app.route('/libro/<int:id>')
@login_required
def libro_show(id):
    libro = db.session.get(Libro, id)
    if not libro:
        return render_template('error.html', error_message="Errore! Il libro richiesto non è stato trovato.")
    prestiti = Prestito.query.filter_by(libro_id = libro.id).all()
    libro.viste += 1
    db.session.commit()
    copie, rientro = '', ''
    inPrestito = False
    for prestito in prestiti:
        if prestito.terminato == "No":
            rientro = prestito.rientro.strftime('%d-%m-%Y')
            inPrestito = True

    if libro.copie == 1 and not inPrestito:
        copie = "Attualmente è disponibile solo una copia di questo libro."
    elif libro.copie == 0 and not inPrestito:
        copie = "Al momento non abbiamo copie disponibili di questo libro."
    elif inPrestito and libro.copie > 0:
        copie = "Il libro è attualmente in prestito, ma ci sono altre copie disponibili. La data di rientro prevista è: " + rientro
    elif inPrestito:
        copie = "Il libro è attualmente in prestito e non ci sono altre copie disponibili. La data di rientro prevista è: " + rientro
    else:
        copie = "Sono disponibili " + str(libro.copie) + " copie di questo libro."
    return render_template('libro_show.html', libro = libro, copie = copie, rientro = rientro)

@app.route('/libro/<int:id>/pdf')
@login_required
def scheda_libro(id):
    libro = db.session.get(Libro, id)
    if not libro:
        return render_template('error.html', error_message="Errore! Il libro richiesto non è stato trovato.")
    libro.download += 1
    db.session.commit()
    html = render_template('libro_scheda.html', libro = libro)
    pdf = convert(html)    
    return send_file(pdf, as_attachment=True)

@app.route('/libro/create', methods=['GET', 'POST'])
@login_required
def libro_create():
    if request.method == 'POST':
        nuovo = Libro(
            titolo = request.form['titolo'],
            anno = request.form['anno'],
            classificazione = request.form['classificazione'],
            posizione = request.form['posizione'],
            autore = request.form['autore'],
            genere = request.form['genere'],
            collana = request.form['collana'],
            editore = request.form['editore'],
            note = request.form['note'],
            copie = request.form['copie'],
            disponibile = request.form['disponibile'],
            libro_mese = request.form['libro_mese'],
            rivista = request.form['rivista']
        )
        db.session.add(nuovo)
        db.session.commit()        
        return redirect(url_for('libro_index'))    
    return render_template('libro_create.html')

@app.route('/libro/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def libro_edit(id):
    libro = Libro.query.get(id)
    if not libro:
        return render_template('error.html', error_message="Errore! Il libro richiesto non è stato trovato.")
    if request.method == 'POST':
        libro.titolo = request.form['titolo']
        libro.anno = request.form['anno']
        libro.classificazione = request.form['classificazione']
        libro.posizione = request.form['posizione']
        libro.autore = request.form['autore']
        libro.genere = request.form['genere']
        libro.collana = request.form['collana']
        libro.editore = request.form['editore']
        libro.note = request.form['note']
        libro.copie = request.form['copie']
        libro.disponibile = request.form['disponibile']
        libro.libro_mese = request.form['libro_mese']
        libro.rivista = request.form['rivista']
        db.session.commit()        
        return redirect(url_for('libro_index'))    
    return render_template('libro_edit.html', libro = libro)

@app.route('/libro/<int:id>/delete', methods=['POST'])
@login_required
def libro_delete(id):
    libro = Libro.query.get(id)
    if not libro:
        return render_template('error.html', error_message="Errore! Il libro richiesto non è stato trovato.")
    db.session.delete(libro)
    db.session.commit()
    return redirect(url_for('libro_index'))

@app.route('/libro/<genere>/modifica', methods=['POST'])
@login_required
def modifica_genere(genere):
    if request.method == 'POST':
        nuovo = request.form.get('genere')
        libri = Libro.query.filter_by(genere = genere).all()
        for libro in libri:
            libro.genere = nuovo
        db.session.commit()        
        return redirect(url_for('libro_index'))

@app.route('/imposta_no')
@login_required
def imposta_no():
    libri = Libro.query.all()
    for libro in libri:
        libro.rivista = "No"
    db.session.commit()    
    return redirect(url_for('libro_index'))

@app.route('/imposta_si')
@login_required
def imposta_si():
    libri = Libro.query.filter(Libro.genere.like("%ivista%")).all()
    for libro in libri:
        libro.rivista = "Si"
    db.session.commit()    
    return redirect(url_for('libro_index'))

'''
    PRESTITI
'''
@app.route('/prestiti')
@login_required
def index():
    if current_user.ruolo == "Socio":
        prestiti = Prestito.query.filter_by(utente_id = current_user.id).all()
    else:
        prestiti = Prestito.query.all()
    days_remaining = {}
    for prestito in prestiti:
        if prestito.terminato == "Si":
            days_remaining[prestito.id] = prestito.rientro.strftime('%d-%m-%Y')
        else:
            oggi = datetime.today().date()
            fine = prestito.rientro
            days_remaining[prestito.id] = math.ceil((fine - oggi).days)    
    return render_template('prestito_index.html', prestiti = prestiti, days_remaining = days_remaining)

@app.route('/prestiti/pdf')
@login_required
def prestiti_pdf():
    prestiti = Prestito.query.filter_by(utente_id = current_user.id).all()
    html = render_template('prestito_pdf.html', prestiti = prestiti)
    pdf = convert(html)    
    return send_file(pdf, as_attachment=True)

@app.route('/prestiti/admin/pdf')
@login_required
def prestiti_admin_pdf():
    prestiti = Prestito.query.all()
    html = render_template('prestito_admin_pdf.html', prestiti = prestiti)
    pdf = convert(html)    
    return send_file(pdf, as_attachment=True)

@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('query', '')
    suggestions = []
    if query:
        books = Libro.query.filter(Libro.titolo.ilike(f'%{query}%')).all()
        suggestions = [book.titolo for book in books]
    return jsonify(suggestions)

@app.route('/prestito/create', methods=['GET', 'POST'])
@login_required
def create_prestito():
    if request.method == 'POST':
        titolo = request.form.get('titolo')
        uscita = datetime.strptime(request.form.get('uscita'), '%Y-%m-%d')
        libro = Libro.query.filter(Libro.titolo.like('%' + titolo + '%')).first()
        if not libro:
            return render_template('error.html', error_message="Errore! Il libro richiesto non è stato trovato.")
        rientro = uscita + timedelta(days = 30 if libro.rivista == 'No' else 15)
        prestito = Prestito(
            uscita = uscita,
            rientro = rientro,
            terminato = 'No',
            prorogato = 'No',
            libro_id = libro.id,
            utente_id = current_user.id
        )
        db.session.add(prestito)
        libro.copie -= 1
        if libro.copie == 0:
            libro.disponibile = 'No'
        db.session.commit()        
        return redirect(url_for('index'))    
    return render_template('prestito_create.html')

@app.route('/prestito/<int:id>/extend')
@login_required
def extend(id):
    prestito = db.session.get(Prestito, id)
    if not prestito:
        return render_template('error.html', error_message="Errore! Il prestito non è stato trovato.")
    if prestito.prorogato == "Si":
        flash('Il prestito per il libro "{}" è stato già prorogato.'.format(prestito.libro.titolo), 'error')
        return redirect(url_for('index'))
    prestito.rientro = prestito.rientro + timedelta(days=15)
    prestito.terminato = "No"
    prestito.prorogato = "Si"
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/prestito/<int:id>/termina')
@login_required
def termina(id):
    prestito = db.session.get(Prestito, id)
    if not prestito:
        return render_template('error.html', error_message="Errore! Il prestito non è stato trovato.")
    prestito.terminato = "Si"
    prestito.rientro = date.today()
    libro = db.session.get(Libro, prestito.libro_id)
    if not libro:
        return render_template('error.html', error_message="Errore! Il libro richiesto non è stato trovato.")
    libro.copie += 1
    if libro.copie > 0:
        libro.disponibile = "Si"
    db.session.commit()    
    return redirect(url_for('index'))

@app.route('/prestito/<int:id>/delete', methods=['POST'])
@login_required
def prestito_delete(id):
    prestito = db.session.get(Prestito, id)
    if not prestito:
        return render_template('error.html', error_message="Errore! Il prestito richiesto non è stato trovato.")
    libro = db.session.get(Libro, prestito.libro_id)
    if not libro:
        return render_template('error.html', error_message="Errore! Il libro richiesto non è stato trovato.")
    if prestito.terminato == 'No':
        libro.copie += 1
        if libro.copie > 0:
            libro.disponibile = 'Si'
    db.session.delete(prestito)
    db.session.commit()    
    return redirect(url_for('index'))

'''
    CORSI
'''
@app.route('/corsi')
def corso_index():
    if current_user.is_authenticated:
        corsi = Corso.query.all()
        for corso in corsi:
            corso.posti_rimasti = corso.massimo - corso.prenotazioni        
        # Statistiche
        total_view = db.session.query(db.func.sum(Corso.viste)).scalar() or 0
        top_courses = Corso.query.order_by(Corso.viste.desc()).limit(3).all()
        stats = {
            'total_views': total_view,
            'top_courses': top_courses,
        }
        return render_template('corso_index.html', corsi = corsi, stats = stats)
    else:
        corsi = Corso.query.all()        
        return render_template('corso_non_loggato.html', corsi = corsi)

@app.route('/corso/<int:id>/incrementa_visite', methods=['POST'])
def incrementa_visite(id):
    corso = db.session.get(Corso, id)
    if not corso:
        return render_template('error.html', error_message="Errore! Il corso richiesto non è stato trovato.")
    else:
        corso.viste += 1
        db.session.commit()
    return '', 204

@app.route('/corsi/pdf')
@login_required
def corsi_pdf():
    corsi = Corso.query.all()
    html = render_template('corso_pdf.html', corsi = corsi)
    pdf = convert(html)
    return send_file(pdf, as_attachment=True)

@app.route('/corso/create', methods=['GET', 'POST'])
@login_required
def corso_create():
    if request.method == 'POST':        
        nuovo = Corso(
            nome = request.form['nome'],
            programma = request.form['programma'],
            docente = request.form['docente'],
            giorno = request.form['giorno'],
            lezioni = request.form['lezioni'],
            note = request.form['note'],
            partenza = request.form['partenza'],
            minimo = request.form['minimo'],
            massimo = request.form['massimo'],
            contributo = request.form['contributo'],
            tessera = request.form['tessera'],
            prenotazioni = request.form['prenotazioni'],
            iscrizioni = request.form['iscrizioni']
        )
        db.session.add(nuovo)
        db.session.commit()
        return redirect(url_for('corso_index'))    
    return render_template('corso_create.html')

@app.route('/corso/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def corso_edit(id):
    corso = db.session.get(Corso, id)
    if not corso:
        return render_template('error.html', error_message="Errore! Il corso richiesto non è stato trovato.")
    if request.method == 'POST':        
        corso.nome = request.form['nome'],
        corso.programma = request.form['programma'],
        corso.docente = request.form['docente'],
        corso.giorno = request.form['giorno'],
        corso.lezioni = request.form['lezioni'],
        corso.note = request.form['note'],
        corso.partenza = request.form['partenza'],      
        corso.minimo = request.form['minimo'],
        corso.massimo = request.form['massimo'],
        corso.contributo = request.form['contributo'],
        corso.tessera = request.form['tessera'],
        corso.prenotazioni = request.form['prenotazioni'],
        corso.iscrizioni = request.form['iscrizioni']
        db.session.commit()        
        return redirect(url_for('corso_index'))    
    return render_template('corso_edit.html', corso = corso)

@app.route('/corso/<int:id>/delete', methods=['POST'])
@login_required
def corso_delete(id):
    corso = Corso.query.get(id)
    if not corso:
        return render_template('error.html', error_message="Errore! Il corso richiesto non è stato trovato.")
    db.session.delete(corso)
    db.session.commit()    
    return redirect(url_for('corso_index'))

'''
    PRENOTAZIONI
'''
@app.route('/prenotazioni')
@login_required
def booking_index():
    titolo = ""
    if current_user.ruolo == "Socio":
        prenotazioni = Prenotazioni.query.filter_by(utente_id = current_user.id).all()
        titolo = "I Miei Percorsi Formativi - " + current_user.nome
    else:
        prenotazioni = Prenotazioni.query.all()
        titolo = "Panoramica delle Prenotazioni ai Corsi"
    prenotazioni_per_corso = {}
    for prenotazione in prenotazioni:
        if prenotazione.corso_id not in prenotazioni_per_corso:
            prenotazioni_per_corso[prenotazione.corso_id] = []
        prenotazioni_per_corso[prenotazione.corso_id].append(prenotazione)
    
    return render_template('prenotazioni_index.html', prenotazioni_per_corso = prenotazioni_per_corso, titolo = titolo)

@app.route('/suggerimento', methods=['GET'])
def suggerimento():
    query = request.args.get('query', '')
    suggestions = []
    if query:
        corsi = Corso.query.filter(Corso.nome.like(f'%{query}%')).all()
        suggestions = [corso.nome for corso in corsi]
    return jsonify(suggestions)

@app.route('/prenotazione/create', methods=['GET', 'POST'])
@login_required
def create_prenotazione():
    error, nome = "", ""
    if request.method == 'POST':
        nome = request.form.get('nome')
        corso = Corso.query.filter(Corso.nome.like('%' + nome + '%')).first()
        if not corso:
            return render_template('error.html', error_message="Errore! Il corso richiesto non è stato trovato.")
        else:
            prenotazione = Prenotazioni(
                stato = "Prenotato",
                corso_id = corso.id,
                utente_id = current_user.id
            )
            db.session.add(prenotazione)
            corso.prenotazioni += 1
            db.session.commit()            
            return redirect(url_for('booking_index'))    
    return render_template('prenotazioni_create.html', error = error, nome = nome)

@app.route('/prenotazione/<int:id>/delete', methods=['POST'])
@login_required
def prenotazione_delete(id):
    prenotazione = db.session.get(Prenotazioni, id)
    if not prenotazione:
        return render_template('error.html', error_message="Errore! La prenotazione richiesta non è stata trovata.")
    corso = db.session.get(Corso, prenotazione.corso_id)
    if not corso:
        return render_template('error.html', error_message="Errore! Il corso richiesto non è stato trovato.")
    if prenotazione.stato == 'Prenotato':
        corso.prenotazioni -= 1
    else: 
        corso.iscrizioni -= 1
    db.session.delete(prenotazione)
    db.session.commit()    
    return redirect(url_for('booking_index'))

@app.route('/prenotazione/<int:id>/conferma', methods=['GET'])
@login_required
def conferma(d):
    prenotazione = db.session.get(Prenotazioni, id)
    if not prenotazione:
        return render_template('error.html', error_message="Errore! La prenotazione richiesta non è stata trovata.")
    prenotazione.stato = "Iscritto"
    db.session.commit()
    corso = db.session.get(Corso, prenotazione.corso_id)
    if corso is not None:
        corso.prenotazioni -= 1
        corso.iscrizioni += 1
        db.session.commit()    
    return redirect(url_for('booking_index'))

@app.route('/prenotazione/<int:id>/pdf')
@login_required
def prenotazione_pdf(id):
    prenotazioni = Prenotazioni.query.filter_by(corso_id = id).all()
    html = render_template('prenotazioni_pdf.html', prenotazioni = prenotazioni)
    pdf = convert(html)    
    return send_file(pdf, as_attachment=True)

@app.route('/prenotazioni/<int:id>/pdf')
@login_required
def prenotazione_admin_pdf(id):
    prenotazioni = Prenotazioni.query.filter_by(corso_id = id).all()
    html = render_template('prenotazioni_admin_pdf.html', prenotazioni = prenotazioni)
    pdf = convert(html)    
    return send_file(pdf, as_attachment=True)

if __name__ == '__main__':
    app.run()