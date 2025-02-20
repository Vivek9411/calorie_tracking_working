from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField, SelectField, SubmitField
from wtforms.validators import InputRequired, Email, Length
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
from calculate_calories import findx, find_food
# Initialize app, database, and login manager
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Example API URL for food calorie lookup
API_URL = "https://api.spoonacular.com/food/ingredients/search"  # Replace with your API URL
API_KEY = 'your_api_key'  # Replace with your API key




## databases
# Create User and Calorie models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(150), nullable=False)

# class CalorieIntake(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.String(50), nullable=False)
#     time = db.Column(db.String(50), nullable=False)
#     calories = db.Column(db.Integer, nullable=False)
#     description = db.Column(db.String(200), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#
# class CalorieBurned(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.String(50), nullable=False)
#     time = db.Column(db.String(50), nullable=False)
#     calories_burned = db.Column(db.Integer, nullable=False)
#     description = db.Column(db.String(200), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class FoodIntake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    food = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Integer, nullable=True)
    calories = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f'<FoodIntake {self.food}>'

class ExerciseDone(db.Model):
    id = db.Column(db.Integer, primary_key=True , autoincrement=True)
    email = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    exercise = db.Column(db.String(200), nullable=False)
    calories_burned = db.Column(db.Float, nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f'<ExerciseDone {self.exercise}>'

# forms
# User registration form
class RegistrationForm(FlaskForm):
    name = StringField('What is your name?', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)])
    age = IntegerField('Age', validators=[InputRequired()])
    weight = FloatField('Weight (kg)', validators=[InputRequired()])
    height = FloatField('Height (cm)', validators=[InputRequired()])
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])

# User login form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])



class FoodIntakeForm(FlaskForm):
    food = StringField('Enter Food Item', validators=[InputRequired()])
    submit = SubmitField('Add Food Intake')

class ExerciseDoneForm(FlaskForm):
    exercise = StringField('Enter Exercise Name', validators=[InputRequired()])
    submit = SubmitField('Add Exercise')

with app.app_context():
    db.create_all()

# some neccesaary functions
from datetime import datetime, timedelta

def get_date_range(report_type):
    today = datetime.now().date()  # Only get the date part
    if report_type == 'daily':
        start_date = today
        end_date = today
    elif report_type == 'weekly':
        start_date = today - timedelta(days=today.weekday())  # Start of the week (Monday)
        end_date = today
    elif report_type == 'monthly':
        start_date = today.replace(day=1)  # Start of the month
        end_date = today
    else:
        raise ValueError("Invalid report type")
    return start_date, end_date






# basic login and logout


# Load user function for login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Home route after login
@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('home_logged_in.html', name=current_user.name)
    return render_template('home_not_logged_in.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name =form.name.data, email=form.email.data, password=form.password.data,
                    age=form.age.data, weight=form.weight.data,
                    height=form.height.data, gender=form.gender.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:  # Password check
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid login credentials. Please try again.', 'danger')
    return render_template('login.html', form=form)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))



# added functionality
# Add calorie intake route
@app.route('/add_calorie_intake', methods=['GET', 'POST'])
@login_required
def add_calorie_intake():
    form = FoodIntakeForm()

    if form.validate_on_submit():
        food_query = form.food.data
        print(food_query)

        # Make the API request to fetch food calorie data
        data = find_food(food_query)
        print(data)
        if data:
            for food in data:
                new_intake = FoodIntake(email=current_user.email,date = food['date'] , time = food['time'],food=food['food'], calories=food['calories'],
                                        description=food['description'], amount=food['amount'])
                db.session.add(new_intake)
                db.session.commit()

            flash('Food intake added successfully!', 'success')
            return redirect(url_for('home'))  # Redirect to home after adding intake
        else:
            flash('Food not found or API error occurred!', 'danger')

    return render_template('add_calorie_intake.html', form=form)




# Add calorie burned route
@app.route('/add_exercise_done', methods=['GET', 'POST'])
@login_required
def add_exercise_done():
    form = ExerciseDoneForm()

    if form.validate_on_submit():
        exercise_query = form.exercise.data

        # Example: Simple calories burned calculation based on exercise
        # This is a placeholder logic, adjust according to your needs
        exercise_calories_burned = findx(user_input=exercise_query, gender=current_user.gender, weight=current_user.weight,age=current_user.age, height=current_user.height)  # Replace with actual logic

        if exercise_calories_burned:
            # Create a new ExerciseDone record and save it to the database
            for exercise in exercise_calories_burned:
                new_exercise = ExerciseDone(email=current_user.email, exercise=exercise['exercise'], date=exercise['date'],time=exercise['time'],
                                            calories_burned=exercise['calories'], description=exercise_query, duration=exercise['duration'])
                db.session.add(new_exercise)
                db.session.commit()
            print(exercise_calories_burned)

            flash('Exercise added successfully!', 'success')
            return redirect(url_for('home'))  # Redirect to home after adding exercise
        else:
            flash('Exercise not recognized or error occurred!', 'danger')

    return render_template('add_exercise_done.html', form=form)


# viewing functions
@app.route('/daily_report')
@login_required
def daily_report():
    start_date, end_date = get_date_range('daily')

    food_intake = FoodIntake.query.filter(
        FoodIntake.email == current_user.email,
        FoodIntake.date >= start_date,
        FoodIntake.date <= end_date
    ).all()

    exercise_done = ExerciseDone.query.filter(
        ExerciseDone.email == current_user.email,
        ExerciseDone.date >= start_date,
        ExerciseDone.date <= end_date
    ).all()

    total_intake = round(sum(item.calories for item in food_intake), 2)
    total_burned = round(sum(item.calories_burned for item in exercise_done), 2)

    return render_template(
        'daily_report.html',
        food_intake=food_intake,
        exercise_done=exercise_done,
        total_intake=total_intake,
        total_burned=total_burned
    )


@app.route('/weekly_report')
@login_required
def weekly_report():
    start_date, end_date = get_date_range('weekly')

    food_intake = FoodIntake.query.filter(
        FoodIntake.email == current_user.email,
        FoodIntake.date >= start_date,
        FoodIntake.date <= end_date
    ).all()

    exercise_done = ExerciseDone.query.filter(
        ExerciseDone.email == current_user.email,
        ExerciseDone.date >= start_date,
        ExerciseDone.date <= end_date
    ).all()

    total_intake = round(sum(item.calories for item in food_intake), 2)
    total_burned = round(sum(item.calories_burned for item in exercise_done), 2)
    return render_template(
        'weekly_report.html',
        food_intake=food_intake,
        exercise_done=exercise_done,
        total_intake=total_intake,
        total_burned=total_burned
    )


@app.route('/monthly_report')
@login_required
def monthly_report():
    start_date, end_date = get_date_range('monthly')

    food_intake = FoodIntake.query.filter(
        FoodIntake.email == current_user.email,
        FoodIntake.date >= start_date,
        FoodIntake.date <= end_date
    ).all()

    exercise_done = ExerciseDone.query.filter(
        ExerciseDone.email == current_user.email,
        ExerciseDone.date >= start_date,
        ExerciseDone.date <= end_date
    ).all()

    total_intake = round(sum(item.calories for item in food_intake),2)
    total_burned = round(sum(item.calories_burned for item in exercise_done),2)

    return render_template(
        'monthly_report.html',
        food_intake=food_intake,
        exercise_done=exercise_done,
        total_intake=total_intake,
        total_burned=total_burned
    )


if __name__ == '__main__':
    app.run(debug=True)
