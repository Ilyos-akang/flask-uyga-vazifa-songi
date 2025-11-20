from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "secret123"

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# File uploads
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)

# ---------------------------------------
# MODELS
# ---------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    parol = db.Column(db.String(50), nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return self.name


class Telefon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nomi = db.Column(db.String(100), nullable=False)
    narxi = db.Column(db.String(50), nullable=False)
    soni = db.Column(db.Integer, nullable=False)
    malumot = db.Column(db.String(200), nullable=False)
    tel_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rasm = db.Column(db.String(100), default="default.png")
    create_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return self.nomi


# ---------------------------------------
# ROUTES
# ---------------------------------------

@app.route("/")
def index():
    if "name" not in session:
        return redirect(url_for('login'))

    tel = Telefon.query.all()
    return render_template("index.html", tel=tel, nomi=session['name'])


@app.route("/add-tel", methods=["GET", "POST"])
def create_phone():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if request.method == "GET":
        return render_template('create.html')

    nomi = request.form.get('nomi')
    narxi = request.form.get('narxi')
    soni = request.form.get('soni')
    malumot = request.form.get('malumot')

    file = request.files.get('rasm')
    if not file or file.filename == '':
        filename = "default.png"
    else:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    post = Telefon(
        nomi=nomi,
        narxi=narxi,
        soni=soni,
        malumot=malumot,
        rasm=filename,
        tel_id=session["user_id"]
    )

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('index'))


@app.route("/edit-tel/<int:id>", methods=["GET", "POST"])
def edit_phone(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    tel = Telefon.query.get_or_404(id)

    if request.method == "GET":
        return render_template("edit.html", tel=tel)

    # POST
    tel.nomi = request.form.get('nomi')
    tel.narxi = request.form.get('narxi')
    tel.soni = request.form.get('soni')
    tel.malumot = request.form.get('malumot')

    file = request.files.get('rasm')
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        tel.rasm = filename

    db.session.commit()
    return redirect(url_for('index'))


@app.route("/delete-tel/<int:id>")
def delete_phone(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    tel = Telefon.query.get_or_404(id)
    db.session.delete(tel)
    db.session.commit()
    return redirect(url_for('index'))


@app.route("/login", methods=['GET', "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    phone_number = request.form.get("phone")
    password = request.form.get("parol")

    user = User.query.filter_by(phone_number=phone_number, parol=password).first()

    if user:
        session['name'] = user.name
        session['user_id'] = user.id
        return redirect(url_for('index'))
    
    return redirect(url_for('login'))


@app.route("/register", methods=['GET', "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("ism")
    phone_number = request.form.get("phone")
    password = request.form.get("parol")

    user = User(name=name, phone_number=phone_number, parol=password)
    db.session.add(user)
    db.session.commit()

    session['name'] = user.name
    session['user_id'] = user.id

    return redirect(url_for('index'))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


# Run
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
