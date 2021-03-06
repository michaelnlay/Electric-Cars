from flask_bcrypt import Bcrypt
from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

bcrypt = Bcrypt(app)


class User:
    db = "ev_schema"

    def __init__(self, data):
        self.id = data["id"]

        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.email = data["email"]
        self.password = data["password"]

        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]

    @staticmethod
    def validate_register(form_data):
        is_valid = True  # we assume this is ture

        if len(form_data["first_name"]) < 3:
            flash("First name must be at least 3 characters long!")
            is_valid = False

        if len(form_data["last_name"]) < 3:
            flash("Last name must be at least 3 characters long!")
            is_valid = False

        if len(form_data["password"]) < 8:
            flash("Password must be at least 8 characters long!")
            is_valid = False

        if (form_data["password"]) != form_data["password_confirmation"]:
            flash("Password and Password Confirmation must match! ")
            is_valid = False

        if not EMAIL_REGEX.match(form_data["email"]):
            flash("Please enter a valid email address!")
            is_valid = False

        return is_valid

    @staticmethod
    def validate_login(form_data):
        is_valid = True

        user_from_db = User.get_by_email(form_data)

        if not user_from_db:
            flash("Invalid Email/Password")
            is_valid = False

        elif not bcrypt.check_password_hash(user_from_db.password, form_data['password']):
            # if we get False after checking the password
            flash("Invalid Email/Password")
            is_valid = False

        return is_valid

    @classmethod
    def create_user(cls, data):
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW(), NOW());"

        results = connectToMySQL(cls.db).query_db(query, data)

        return results  # the resuls will kick back up to the new_user_id in user_controller

    @classmethod
    def get_by_id(cls, data):
        query = "SELECT * FROM users WHERE id = %(user_id)s;"
        result = connectToMySQL(cls.db).query_db(query, data)
        # Didn't find a matching user
        if len(result) < 1:
            return False
        return cls(result[0])

    @classmethod
    def get_by_email(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        result = connectToMySQL(cls.db).query_db(query, data)
        # Didn't find a matching user
        if len(result) < 1:
            return False
        return cls(result[0])
