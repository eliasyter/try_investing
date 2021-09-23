import bcrypt
from flask import Flask, render_template, url_for, request,redirect,session

#database imports
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,login_manager,logout_user,login_required,current_user

#login and registrasion imports
from flask_wtf import FlaskForm
from flask_wtf.form import FlaskForm
from flask_wtf.recaptcha import validators
from sqlalchemy.orm import session
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import InputRequired,Length,ValidationError

#for hashing passwords
from flask_bcrypt import Bcrypt

#datetime for the login form to later say how long you have had the user
from datetime import datetime

app = Flask(__name__)
#init Sqlalchemy so i can use it later inn the app 
db = SQLAlchemy(app)
#making the hashing veriable 
bcrypt= Bcrypt(app)
#making a sqlite database
app.config['SECRET_KEY'] = 'Eliaserdaddy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'


login_manager= login_manager.LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key= True)
    username=db.Column(db.String(20),nullable=False, unique=True)
    password= db.Column(db.String(80),nullable=False)
    #date_created does not work 
    # if i have time in a later time i want to add the time tha user was made
class RegisterForm(FlaskForm):
    username= StringField(validators=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder":"Username"})

    password= PasswordField(validators=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder":"Password"})

    submit=SubmitField("Register")

    

    def validate_username(self, username):
        existing_user_username=User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists. Please choose a different one')


class LoginForm(FlaskForm):
    username= StringField(validators=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder":"Username"})

    password= PasswordField(validators=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder":"Password"})

    submit=SubmitField("Login")

    



class Coin(db.Model):
    id = db.Column(db.Integer,primary_key= True)
    tag = db.Column(db.String(200),nullable=False)
    amount =db.Column(db.Integer,nullable=False)
    owner =db.Column(db.String(20))
    date_created=db.Column(db.DateTime, default=datetime.utcnow)


    def __repr__(self):
        return 'You have added <crypto %r>'% self.tag




@app.route("/")
def index():
    return render_template('index.html')


@app.route("/SignUp",methods=['GET','POST'])
def SignUp():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user=User(username=form.username.data,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('SignUp.html',form=form)




@app.route("/login",methods=['GET','POST'])
def login():
    form = LoginForm()
    #is this user in the database
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user)
                return redirect(url_for('invest'))
    return render_template('login.html',form=form)


@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/invest',methods=['GET','POST'])
@login_required
def invest():
    name=current_user.username

    prices=Coin.query.filter_by(owner=current_user.username)
    return render_template('invest.html',prices=prices,name=name)


@app.route('/add_coin',methods=['GET','POST'])
@login_required
def add_coin():

    if request.method== "POST":
        form_tag=request.form['tag']
        form_amount=request.form['amount']
        print(form_amount,form_tag)
        new_coin=Coin(tag=str(form_tag),amount=int(form_amount),owner=current_user.username)

        #push to database
        try:
            db.session.add(new_coin)
            db.session.commit()
            return redirect('/invest')
        except:
            return"There was an error"
    else:
        return render_template('add_coin.html')




if __name__ == '__main__':
    app.run(debug=True)