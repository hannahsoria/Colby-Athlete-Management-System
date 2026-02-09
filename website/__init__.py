# Creates the Flask app, 
# Configures the app
# Registers blueprints
# Initializes the database
# Optionally seeds dummy data
# 2022 revised in 2026

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

db = SQLAlchemy()
DB_NAME = "database.db"
UPLOAD_FOLDER = "./csvs"


# create app
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///database.db")
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    db.init_app(app)

    from .models import User, Team

    # create and populate database
    create_database(app)
    populate(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


# database setup
def create_database(app):
    with app.app_context():
        db.create_all()
    print("Created Database!")


# populate the database with users
def populate(app):
    with app.app_context():
        from .models import User, Team
        from werkzeug.security import generate_password_hash

        # users
        def get_or_create_user(email,first_name,last_name,password,role,athlete_name=None,team=None):
            user = User.query.filter_by(email=email).first()

            if not user:
                user = User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=generate_password_hash(password, method="sha256"),
                    role=role,
                    athlete_name=athlete_name,
                    team=team.lower() if team else None
                )
                db.session.add(user)
                db.session.commit()

            return user

        # dummy data for demo purposes
        # admin
        admin = get_or_create_user(
            email="anne@colby.edu",
            first_name="Anne",
            last_name="Doctor",
            password="1234",
            role="admin"
        )

        # coach
        coach = get_or_create_user(
            email="john@colby.edu",
            first_name="John",
            last_name="Doe",
            password="1234",
            role="coach",
            team="Football"
        )

        # athlete
        athlete = get_or_create_user(
            email="athlete1@colby.edu",
            first_name="Athlete",
            last_name="1",
            password="1234",
            role="athlete",
            athlete_name="1"
        )

        # team
        team_name = "Default Team"
        team = Team.query.filter_by(name=team_name).first()
        if not team:
            team = Team(name=team_name)
            db.session.add(team)

        # link users to team
        for user in [admin, coach, athlete]:
            if user not in team.users:
                team.users.append(user)

        db.session.commit()

# drop database
def drop_database(app):
    with app.app_context():
        db.session.remove()
        db.drop_all()
    print("Dropped Database!")
