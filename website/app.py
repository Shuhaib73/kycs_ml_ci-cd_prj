import os
from dotenv import load_dotenv

from flask import Flask, Blueprint, render_template, request, flash, get_flashed_messages, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from flask import make_response

import pandas as pd
from model import PipelineTester, PipelineTesterMulticlass

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

# Initialize MySQL
mysql = MySQL(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)

# User Loader Function
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


class User(UserMixin):
    def __init__(self, user_id, name, email):
        self.id = user_id
        self.name = name
        self.email = email

    @staticmethod
    def get(user_id):
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT name, email from users where id = %s', (user_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return User(user_id, result[0], result[1])
        

# Views / route
@app.route('/')
@app.route('/home')
def home():
    response = make_response(render_template('home.html'))

    return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()

        cursor.execute('SELECT id, name, email, password from users where email = %s', (email,))

        user_data = cursor.fetchone()
        cursor.close()

        if user_data and bcrypt.check_password_hash(user_data[3], password):
            user = User(user_data[0], user_data[1], user_data[2])

            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Email/Password', category='error')
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_psw = request.form['psw']

        if password != confirm_psw:
            flash('Password and Confirm Password must match', category='error')
        elif len(password) < 6:
            flash('Password must be greater than 5 character!', category='error')
        else :
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            cursor = mysql.connection.cursor()

            try: 
                cursor.execute('INSERT INTO users (name, email, password) values(%s, %s, %s)', (name, email, hashed_password))

                mysql.connection.commit()
                cursor.close()

                flash('Registration Successful! Login.', category='success')

                # return redirect(url_for('login'))
            except mysql.connection.IntegrityError as e:
                error_msg = "This email address is already registered!"
                flash(error_msg, category='error')
                cursor.close()

    return render_template('signup.html')


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':

        flash_fill = request.form.get('flash_fill')
        model_type = request.form.get('option')

        if flash_fill:
            try:
                values = [x for x in flash_fill.split(',')]

                (Category,Founded_Year,Country_Code,First_Funding_Year,Funding_Rounds,Funding_Total_USD,First_Milestone_Year,Milestone,Relationships,Latitude,Longitude,Active_Years) = values

            except:
                pass 
        
        else:

            Category = request.form['category']
            Country_Code = request.form['country']
            Founded_Year = int(request.form['founded_at'])
            Active_Years = int(request.form['active_years'])
            First_Funding_Year = int(request.form['first_funding_at'])
            First_Milestone_Year = int(request.form['first_milestone_at'])
            Funding_Rounds = float(request.form['funding_rounds'])
            Milestone = float(request.form['milestones'])
            Relationships = float(request.form['relationships'])
            Funding_Total_USD = float(request.form['funding_total_usd'])
            Latitude = float(request.form['lat'])
            Longitude = float(request.form['lng'])

        # Retrieve the email of the logged-in user   
        email = current_user.email

        # Creating a DataFrame with the input data
        input_data = pd.DataFrame({
            'category_code' : [Category],
            'founded_at': [Founded_Year],
            'country_code': [Country_Code],
            'first_funding_at': [First_Funding_Year],
            'funding_rounds': [Funding_Rounds],
            'funding_total_usd': [Funding_Total_USD],
            'first_milestone_at': [First_Milestone_Year],
            'milestones': [Milestone],
            'relationships': [Relationships],
            'lat': [Latitude],
            'lng': [Longitude],
            'active_years': [Active_Years]
        })

        cursor = mysql.connection.cursor()

        try:
            cursor.execute('INSERT INTO company_details (email, category, country, founded_year, active_years, first_funding_year, first_milestone_year, funding_rounds, milestone, relationship, funding_total_usd, latitude, longitude) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (email, Category, Country_Code, Founded_Year, Active_Years, First_Funding_Year, First_Milestone_Year, Funding_Rounds, Milestone, Relationships, Funding_Total_USD, Latitude, Longitude))

            mysql.connection.commit()
            cursor.close()
        except mysql.connection.IntegrityError as e:
            flash(e, category='error')
            cursor.close()

        try:

            if model_type == 'binary_classification':

                # Initialize the PipelineTester with the trained pipeline and input data
                model_pipe = PipelineTester('binary_pipeline.pkl', input_data)

                prediction_prob = model_pipe.predict()

                # Set a threshold for classification
                threshold = 0.5

                # Apply a threshold to classify the sample
                if prediction_prob > threshold:
                    msg = "The Company is either Closed/Acquired"
                    flash(msg, category='error')
                else:
                    msg = "The Company is either Operating/IPO"
                    flash(msg, category='success')
            
            elif model_type == 'multiclass_classification':
                print('Multiclass')

                model_pipeline = PipelineTesterMulticlass('multiclass_pipeline.pkl', input_data)

                predicted_class = model_pipeline.predict()

                # Apply a Condition to classify the sample
                if predicted_class == 0:
                    msg = "The Company is Acquired"
                    flash(msg, category='error')
                elif predicted_class == 1:
                    msg = "The Company is Closed"
                    flash(msg, category='error')
                elif predicted_class == 2:
                    msg = "The Company is IPO"
                    flash(msg, category='success')
                else:
                    msg = "The Company is Operating"
                    flash(msg, category='success')

        except Exception as e:
            flash(f"Prediction failed: {str(e)}", category='error')

    return render_template('dashboard.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_psw = request.form['psw']

        cursor = mysql.connection.cursor()

        #Check if the email exists in the database 
        cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
        user_email = cursor.fetchone()

        if not user_email:
            flash('Invalid Email!', category='error')
        elif password != confirm_psw:
            flash('Password and Confirm Password must match', category='error')
        elif len(password) < 6:
            flash('Password must be greater than 5 character!', category='error')
        else:
            # Update password in the database
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            cursor.execute('UPDATE users SET password = %s WHERE email = %s', (hashed_password, email))
            mysql.connection.commit()

            flash('Password updated successfully', category='success')
            cursor.close()

    return render_template('reset_psw.html')


@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')


@app.route('/github')
@login_required
def github():
    return redirect('https://github.com/Technocolabs100/Building-Machine-Learning-Pipeline-on-Startups-Acquisition-Status', code=301)


@app.route('/about')
@login_required
def about():
    return render_template('about.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
