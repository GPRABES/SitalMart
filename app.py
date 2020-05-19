import os
import secrets
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegistrationForm, VegetableForm
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '59db39ee7efedab67f3d397083f2d265'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(60), default="user.png")
    role = db.Column(db.String(60), nullable=True)
    phone = db.Column(db.String(20), unique=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.first_name} {self.last_name}', '{self.email}')"

    def name(self):
        return self.first_name + ' ' + self.last_name

class Vegetable(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(20), default="default.png")
    price = db.Column(db.String(50), nullable=False)
    selling_unit = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"Vegetable('{self.name}', '{self.price}')"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    vegetables = Vegetable.query.all()
    username = session.get('username')
    return render_template('home.html', vegetables=vegetables, username=username, page_title="Home")

@app.route("/settings")
@login_required
def settings():
    username = session.get('username')
    return  render_template("settings.html", username=username, page_title="Settings")

def save_vegetable_image(form_image):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_filename = random_hex + f_ext
    image_path = os.path.join(app.root_path, 'static/uploads', image_filename)
    form_image.save(image_path)

    return image_filename


@app.route("/add-vegetable", methods=["GET", "POST"])
@login_required
def add_vegetable():
    form = VegetableForm()
    if(form.validate_on_submit()):
        if form.image.data:
            veg_image = save_vegetable_image(form.image.data)

        if veg_image:
            vegetable = Vegetable(name=form.name.data, price=form.price.data, selling_unit=form.selling_unit.data, image=veg_image)
        else:
            vegetable = Vegetable(name=form.name.data, price=form.price.data, selling_unit=form.selling_unit.data, image="default.png")

        db.session.add(vegetable)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add-vegetable.html', form=form,  username = session.get('username'), page_title="Add Vegetable")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    password=hashed_pwd)
        db.session.add(user)
        db.session.commit()
        flash("Registered Successfully!", "success")
        return redirect(url_for('login'))
    return render_template("register.html", form=form, page_title="Register")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if not user and bcrypt.check_password_hash(user.password, form.password.data):
            flash("Please check your login details and try again", "danger")
            return redirect(url_for('login'))

        login_user(user)
        session['username'] = user.name()
        flash("Successfully Logged In!", "success")
        return redirect(url_for('home'))
    return render_template("login.html", form=form, page_title="Login")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('username')
    flash('Logged out!', "success")
    return redirect(url_for('home'))


@app.route("/vegetable/<int:id>")
def get_vegetable(id):
    vegi = Vegetable.query.filter_by(id=id).first()
    if vegi:
        flash(vegi.name, "info")
    else:
        flash("Not Found", "warning")
    return redirect(url_for('home'))

@app.route("/vegetable/<int:id>/update", methods=["GET","POST"])
@login_required
def update_vegetable(id):
    vegetable = Vegetable.query.get(int(id))
    form = VegetableForm()

    if form.validate_on_submit():
        vegetable.name = form.name.data
        vegetable.price = form.price.data
        vegetable.selling_unit = form.selling_unit.data
        db.session.commit()
        flash("Successfully Updated!", 'success')
        return redirect(url_for('home'))

    form.name.data = vegetable.name
    form.price.data = vegetable.price
    form.selling_unit.data = vegetable.selling_unit
    return render_template("update-vegetable.html", form=form, id=vegetable.id, username = session.get('username'),page_title="Update Vegetable")

@app.route("/user/<int:id>")
@login_required
def get_user(id):
    user = User.query.get(int(id))
    if not user:
        return "Not Found"
    return user.name()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
