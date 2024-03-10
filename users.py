import os
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
from flask import abort, request, session
from sqlalchemy import text


def login(username, password):
    sql = text("SELECT user_id, password_hash FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username": username})
    user_data = result.fetchone()

    if not user_data or not check_password_hash(user_data[1], password):
        return False

    session["user_id"] = user_data[0]
    return True


def logout():
    del session["user_id"]


def get_user_by_id(user_id):
    sql = text("SELECT * FROM users WHERE user_id=:user_id")
    result = db.session.execute(sql, {"user_id": user_id})
    user = result.fetchone()
    return user


def get_user_workouts(user_id):
    sql = text(
        "SELECT * FROM user_workouts WHERE user_id=:user_id AND is_completed=true AND is_deleted=false"
    )
    result_user_workouts = db.session.execute(sql, {"user_id": user_id})
    user_workouts = result_user_workouts.fetchall()
    return user_workouts


def register_account(username, password, confirm_password):
    if password != confirm_password:
        return False
    else:
        password_hash = generate_password_hash(password)
        sql = text(
            "INSERT INTO users (username, password_hash) VALUES (:username, :password_hash)"
        )
        db.session.execute(sql, {"username": username, "password_hash": password_hash})
        db.session.commit()
        return True


def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)


def get_completed_workouts(user_id):
    sql = text("SELECT * FROM completed_workouts WHERE user_id=:user_id")
    result_user_workouts = db.session.execute(sql, {"user_id": user_id})
    completed_workouts = result_user_workouts.fetchall()
    return completed_workouts
