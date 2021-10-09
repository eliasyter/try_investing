import bcrypt
from flask import Flask, render_template, url_for, request,redirect,session,flash

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

#liberies for web scraping 
from urllib.request import urlopen as uReq
import urllib
from bs4 import BeautifulSoup as soup

#os to find database adress
import os 
import re

app = Flask(__name__)
#init Sqlalchemy so i can use it later inn the app 
db = SQLAlchemy(app)
#making the hashing veriable 
bcrypt= Bcrypt(app)
#making a sql database

app.config['SECRET_KEY'] = 'Eliaserdaddy'
uri = os.getenv("DATABASE_URL")  # or other relevant config var
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
#'postgresql://ymsscqozdtvhsm:a9e6e2f2e8fd15b0d7da786a585423cf2859d1946ef02e8afdd995101bc4e96f@ec2-44-194-201-94.compute-1.amazonaws.com:5432/ddh44n1qq86kau'





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

    


#id is id og the coin 
#tag is full name of the coin('bitcoin)
#short_tag is short name of the coin('BTC')
#input_amount is the monay first put inn 
#owner is the user that made it 
#data_created is the date the data was maid
class Coin(db.Model):
    id = db.Column(db.Integer,primary_key= True)
    tag = db.Column(db.String(200),nullable=False)
    short_tag=db.Column(db.String(200),nullable=False)
    amount =db.Column(db.Float,nullable=False)
    input_amount=db.Column(db.Float,nullable=False)
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
                flash('You were successfully logged in', category='success')
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
    cu_user=current_user.username

    #getting all the coins that the loged inn user has made
    coins=Coin.query.filter_by(owner=current_user.username)
    values=[]
    total =0
    investment=0
    for data in coins:
        try:
                uClient = uReq(f'https://coinmarketcap.com/no/currencies/{data.tag}/')
                html=uClient.read()
                uClient.close()
                page_soup= soup(html, "html.parser")
                try:
                    price = page_soup.find_all("div", class_="priceValue")[0].text[2:]
                    if ',' in price:
                        price = price.replace(',','')
                    tall=float(price)
                    value=tall*data.amount
                    value=str(round(value,2))
                    values.append((value,data.short_tag))
                    total += float(value)
                    investment+=data.input_amount
                except IndexError:
                    flash('Something went wrong out of your controll', category='alert')
                    return redirect('/')
            

        except urllib.error.HTTPError as exception:
            flash('This Coin does not exsist', category='error')

    values.reverse()
    income = round(total-investment,2)
    profit =(income>0)
    return render_template('invest.html',values=values,cu_user=cu_user,total=round(total,2),income=income,profit=profit)


@app.route('/add_coin',methods=['GET','POST'])
@login_required
def add_coin():

    if request.method== "POST":

        #getting amount and the name of the coin
        form_tag=request.form['tag'].strip()
        form_amount=float(request.form['amount'])

        # check if the coin already exists
        exist=False
        exsisting_tags=[]
        for data in Coin.query.filter_by(owner=current_user.username):
            exsisting_tags.append(data.tag)
        
        


        #getting the URL making it into soup and looking for prise and name of coin 
        #sending the data to database 
        try:
            uClient = uReq(f'https://coinmarketcap.com/no/currencies/{form_tag}/')
            html=uClient.read()
            uClient.close()
            page_soup= soup(html, "html.parser")
            try:
                price = page_soup.find_all("div", class_="priceValue")[0].text[2:]
                if ',' in price:
                    price = price.replace(',','')
                name =page_soup.find_all("small", class_="nameSymbol")[0].text
                tall=float(price)
                amount_of_coin=form_amount/tall


                if form_tag in exsisting_tags:
                    coin_to_update=Coin.query.filter_by(tag=str(form_tag)).first()
                    coin_to_update.amount+=amount_of_coin
                    try:
                        db.session.commit()
                        return redirect('/invest')
                    except:
                        flash('There was an error commiting to datbase', category='alert')
                        return redirect('/invest')
                    
                else: 
                    #making a new coin
                    new_coin=Coin(tag=str(form_tag),
                    amount=float(amount_of_coin),
                    owner=current_user.username,
                    short_tag=name,
                    input_amount=form_amount)

                    #push to database
                    #this should happen if the coin does not already exist
                    try:
                        db.session.add(new_coin)
                        db.session.commit()
                        print('success')
                        return redirect('/invest')
                    except:
                        flash('There was an error commiting to datbase', category='alert')
                        return redirect('/invest')
            except IndexError:
                flash('Something went wrong out of your controll', category='alert')
                return redirect('/invest')
        

        except:
            flash('This Coin does not exsist', category='error')

        
        

        
    else:
        return render_template('add_coin.html')




if __name__ == '__main__':
    app.run(debug=True)