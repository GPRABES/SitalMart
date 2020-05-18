from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegistrationForm, VegetableForm
from flask_login import LoginManager, UserMixin, login_user

app = Flask(__name__)
app.config['SECRET_KEY'] = '59db39ee7efedab67f3d397083f2d265'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
app.config['UPLOAD_FOLDER'] = '/uploads'
login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(60), default="user.png")
    role = db.Column(db.String(60), nullable=True)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.first_name} {self.last_name}', '{self.email}')"

    def name(self):
        return self.first_name + ' ' + self.last_name

class Vegetable(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(60), default="vegetable.png")
    price = db.Column(db.String(50), nullable=False)
    selling_unit = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Vegetable('{self.name}', '{self.price}')"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    vegetables = Vegetable.query.all()
    return render_template('home.html', vegetables=vegetables)

@app.route("/add-vegetable", methods=["GET", "POST"])
def add_vegetable():
    form = VegetableForm()
    if(form.validate_on_submit()):
        vegetable = Vegetable(name=form.name.data, price=form.price.data, selling_unit=form.selling_unit.data)
        db.session.add(vegetable)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add-vegetable.html', form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if(form.validate_on_submit()):
        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registered Successfully!", "success")
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if(form.validate_on_submit()):
        user = User.query.filter_by(email=form.email.data, password=form.password.data).first()
        if not user:
            return redirect(url_for('login'), error='user not found')
        login_user(user)
        flash("Successfully Logged In!", "success")
        return redirect(url_for('home'))
    return render_template("login.html", form=form)

@app.route("/vegetable/<int:id>")
def get_vegetable(id):
    vegi = Vegetable.query.filter_by(id=id).first()
    if(vegi):
        flash(vegi.name, "info")
    else:
        flash("Not Found", "warning")
    return redirect(url_for('home'))

@app.route("/vegetable/<int:id>/update", methods=["GET","POST"])
def update_vegetable(id):
    vegetable = Vegetable.query.get(int(id))
    form = VegetableForm()

    if(form.validate_on_submit()):
        vegetable.name = form.name.data
        vegetable.price = form.price.data
        vegetable.selling_unit = form.selling_unit.data
        db.session.commit()
        flash("Successfully Updated!", 'success')
        return redirect(url_for('home'))

    form.name.data = vegetable.name
    form.price.data = vegetable.price
    form.selling_unit.data = vegetable.selling_unit
    return render_template("update-vegetable.html", form=form, id=vegetable.id)

@app.route("/user/<int:id>")
def get_user(id):
    user = User.query.get(int(id))
    if not user:
        return "Not Found"
    return user.name()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
