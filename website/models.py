# defines database schema, essentially decide what different users can see

# logs users in
# saves notes
# shows teams
# queries readiness / sleep / nutrition

# 2022, line 37 added 2026

# imports
from time import timezone
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType
from os.path import dirname
import pandas as pd
from datetime import datetime

# information from hawkins to take in
class Hawkins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date(), default=func.now())
    peak_force = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# user information to take in
class User(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    password = db.Column(db.String(150))
    role = db.Column(db.String(50), default='athlete')
    athlete_name = db.Column(db.String(50), nullable=True)
    team = db.Column(db.String(100)) 

    # relationships down here
    notes = db.relationship('Note')
    hawkins = db.relationship('Hawkins')
    nutrition = db.relationship('Nutrition')
    sleep = db.relationship('Sleep')
    readiness = db.relationship('Readiness')

# creates a table for users in the database
users_table = db.Table('users',
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                        db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True)
                        )

# team database
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    users = db.relationship('User', secondary=users_table, lazy='subquery',
        backref=db.backref('teams', lazy=True))

# Sports medicine notes
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(400))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# nutrition information
class Nutrition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    calories = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# sleep information
class Sleep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    TotalSleepScore = db.Column(db.Integer)
    TotalSleepDuration = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# readiness information
class Readiness(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    RecoveryIndexScore = db.Column(db.Integer)  # From Jonna's csv files
    ReadinessScore = db.Column(db.Integer)  # From Jonna's csv files

# function to parse the csv files so they are usable
def parse_csv(data_type: str, filename: str) -> None:
    """Parse a csv file."""
    # get the csv directory and merge it with filename
    csv_directory = f"{dirname(dirname(__file__))}/csvs"
    filepath = f"{csv_directory}/{filename}"
    # read the data from the csv
    csv_data = pd.read_csv(filepath_or_buffer=filepath, header=0)

    # conditional data ingestion
    if data_type == "user":
        data = []
        for row in csv_data.itertuples():
            # create a new User object
            user = User(
                email = row.email,
                first_name = row.first_name,
                last_name = row.last_name,
                password = row.password,
                role = row.role
            )
            # add the user to the database
            db.session.add(user)
            db.session.commit()

    elif data_type == "nutrition":
        data = []
        for row in csv_data.itertuples():
            # create a new Nutrition object
            nutrition = Nutrition(
                date = datetime.strptime(row.date, '%m/%d/%y'),
                calories = row.calories,
                protein = row.protein,
                carbohydrates = row.carbohydrates,
                fats = row.fats
            )
            # add the nutrition object to the database
            db.session.add(nutrition)
            db.session.commit()

    elif data_type == "readiness":
        data = []
        for row in csv_data.itertuples():
            # create a new Readiness object
            readiness = Readiness(
                date = datetime.strptime(row.date, '%m/%d/%y'),
                force = row.force
            )
            # add the readiness object to the database
            db.session.add(readiness)
            db.session.commit()

    # else, sleep data
    else:
        data = []
        for row in csv_data.itertuples():
            # create a new Sleep object
            sleep = Sleep(
                date = datetime.strptime(row.date, '%m/%d/%y'),
                total_duration = row.total_duration,
                REM = row.REM,
                deep_sleep = row.deep_sleep,
                light_sleep = row.light_sleep
            )
            # add the Sleep object to the database
            db.session.add(sleep)
            db.session.commit()