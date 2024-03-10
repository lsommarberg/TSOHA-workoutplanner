import os
from collections import defaultdict
from flask import request, redirect, render_template, session
from app import app
import users
import workouts
from exercise_data import exercise_data


@app.route("/")
def index():
    workouts.add_example_exercises(exercise_data)
    return render_template("login.html")


@app.before_request
def generate_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = os.urandom(16).hex()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        users.check_csrf()
        username = request.form["username"]
        password = request.form["password"]

        if not users.login(username, password):
            return render_template(
                "login.html", error_message="Invalid username or password"
            )

    return redirect("/profile")


@app.route("/create_account")
def create_account():
    return render_template("create_account.html")


@app.route("/register_account", methods=["POST"])
def register_account():
    if request.method == "POST":
        users.check_csrf()

        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if len(username) > 20:
            error_message = "Username is too long. Please use a shorter username."
            return render_template("create_account.html", error_message=error_message)

        if len(password) > 50:
            error_message = "Password is too long. Please use a shorter password."
            return render_template("create_account.html", error_message=error_message)

        if users.register_account(username, password, confirm_password):
            message = "Account created, you can now log in."
            return render_template("login.html", message=message)

        error_message = "Failed to create account. Please try again."
        return render_template("create_account.html", error_message=error_message)


@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")


@app.route("/exercises")
def exercises_list():
    exercises = workouts.get_exercises()
    exercise_names = [exercise[1] for exercise in exercises]
    return render_template("exercises_list.html", exercise_names=exercise_names)


@app.route("/exercise_details")
def exercise_details():
    exercise_name = request.args.get("exercise_name")

    exercise = workouts.get_exercise_by_name(exercise_name)
    if exercise:
        return render_template("exercise_details.html", exercise=exercise)
    else:
        return "Exercise not found", 404


@app.route("/profile")
def profile():
    if "user_id" in session:
        user_id = session["user_id"]
        user = users.get_user_by_id(user_id)
        user_workouts = users.get_user_workouts(user_id)

        completed_workouts = users.get_completed_workouts(user_id)

        return render_template(
            "profile.html",
            user=user,
            user_workouts=user_workouts,
            completed_workouts=completed_workouts,
        )

    return render_template("/login.html")


@app.route("/workout_exercises_list")
def workout_exercises_list():
    exercises = workouts.exercise_names()
    return render_template("workout_exercises_list.html", exercises=exercises)


@app.route("/create_workout", methods=["POST"])
def create_workout():
    if request.method == "POST":
        users.check_csrf()
        selected_exercises = request.form.getlist("selected_exercises[]")

        session["selected_exercises"] = selected_exercises
        user_id = session.get("user_id")

        user_workout_id = workouts.create_workout(user_id)

        session["user_workout_id"] = user_workout_id
        workout_exercises = workouts.create_user_workout(
            selected_exercises, user_workout_id
        )
        session["workout_exercises"] = workout_exercises
        return render_template(
            "create_workout.html",
            workout_exercises=workout_exercises,
            user_workout_id=user_workout_id,
        )


@app.route("/add_sets_page", methods=["POST"])
def add_sets_page():
    if request.method == "POST":
        users.check_csrf()
        user_workout_id = session.get("user_workout_id")
        workout_name = request.form.get("workout_name")

        workouts.update_workout_name(user_workout_id, workout_name)
        exercises = session.get("workout_exercises")
        workout_exercises = []
        error_message = None
        for key in request.form.keys():
            if key.startswith("sets_number_"):
                parts = key.split("_")
                if len(parts) >= 3 and parts[2]:
                    workout_exercise_id = int(parts[2])
                    sets_number = request.form[key] or None
                    if sets_number == None:
                        error_message = "Sets number is required."
                        break
                    sets_number = int(request.form[key])
                    updated_exercise = workouts.update_workout_exercises(
                        workout_exercise_id, sets_number
                    )
                    if updated_exercise:
                        exercise_id = updated_exercise[2]
                        exercise_name = workouts.get_exercise_name_by_id(exercise_id)
                        workout_exercises.append((updated_exercise, exercise_name))

        if error_message:
            return render_template(
                "create_workout.html",
                error_message=error_message,
                workout_exercises=exercises,
                user_workout_id=user_workout_id,
            )

        return render_template(
            "add_sets.html",
            workout_name=workout_name,
            workout_exercises=workout_exercises,
            user_workout_id=user_workout_id,
        )


@app.route("/process_workout", methods=["POST"])
def process_workout():
    if request.method == "POST":
        users.check_csrf()
        user_id = session.get("user_id")
        reps_data = defaultdict(dict)
        weight_data = defaultdict(dict)

        error_message = None
        for key, value in request.form.items():
            parts = key.split("_")
            value = value or None
            if len(parts) >= 3 and parts[0] in {"reps", "weight"}:
                data_type, exercise_id, set_num = parts[:3]
                if data_type == "reps":
                    if value == None:
                        error_message = "Reps number is required."
                        break
                    reps_data[int(exercise_id)][int(set_num)] = int(value)
                elif data_type == "weight":
                    if value == None:
                        error_message = "Weight number is required."
                        break
                    weight_data[int(exercise_id)][int(set_num)] = float(value)

        user_workout_id = session.get("user_workout_id")
        completed_workouts = users.get_completed_workouts(user_id)
        workout_exercises = workouts.exercise_ids_and_names(user_workout_id)

        get_workout_name = workouts.get_workout_name(user_workout_id)
        workout_name = get_workout_name.scalar()

        if error_message:
            return render_template(
                "add_sets.html",
                workout_name=workout_name,
                workout_exercises=workout_exercises,
                user_workout_id=user_workout_id,
                error_message=error_message,
            )

        if user_workout_id:
            workouts.save_workout(user_workout_id, reps_data, weight_data)
            workouts.user_workout_completed(user_workout_id)

        user_workouts = users.get_user_workouts(user_id)

        return render_template(
            "profile.html",
            user_workouts=user_workouts,
            user=user_id,
            completed_workouts=completed_workouts,
            message="Workout saved successfully!",
        )


@app.route("/delete_workout")
def delete_workout():
    user_workout_id = request.args.get("workout_id")
    workouts.delete_workout(user_workout_id)

    return redirect("/profile")


@app.route("/view_workout")
def view_workout():
    user_workout_id = request.args.get("workout_id")

    session["user_workout_id"] = user_workout_id

    workout_exercises = workouts.get_workout_exercises_by_workout_id(user_workout_id)
    get_workout_name = workouts.get_workout_name(user_workout_id)
    workout_name = get_workout_name.scalar()

    user_workout_data = []
    for exercise_data in workout_exercises:
        exercise_id = exercise_data[2]
        exercise_name = workouts.get_exercise_name_by_id(exercise_id)
        user_workout_data.append((exercise_data, exercise_name))

    return render_template(
        "view_workout.html", user_workout=user_workout_data, workout_name=workout_name
    )


@app.route("/log_workout")
def log_workout():
    user_id = session.get("user_id")

    user_workouts = users.get_user_workouts(user_id)

    user_workout_id = session.get("user_workout_id")

    workouts.log_workout(user_workout_id, user_id)
    completed_workouts = users.get_completed_workouts(user_id)

    return render_template(
        "profile.html",
        user_workouts=user_workouts,
        user=user_id,
        completed_workouts=completed_workouts,
        message="Workout logged successfully!",
    )


@app.route("/modify_workout")
def modify_workout():
    user_id = session.get("user id")
    user_workout_id = session.get("user_workout_id")
    user_workout = workouts.get_user_workout_by_id(user_workout_id)

    workout_exercises = workouts.get_workout_exercises_by_workout_id(user_workout_id)
    get_exercises = workouts.get_exercises()
    workout_exercise_ids = [exercise[2] for exercise in workout_exercises]

    return render_template(
        "add_new_exercises.html",
        exercises=get_exercises,
        workout_exercise_ids=workout_exercise_ids,
        user_id=user_id,
        user_workout_id=user_workout_id,
        user_workout=user_workout,
    )


@app.route("/add_to_existing_workout", methods=["POST"])
def add_to_existing_workout():
    if request.method == "POST":
        selected_exercises = request.form.getlist("selected_exercises[]")

        session["selected_exercises"] = selected_exercises

        user_workout_id = session.get("user_workout_id")
        original_workout = workouts.get_user_workout_by_id(user_workout_id)

        user_id = session.get("user_id")

        modified_workout_id = workouts.create_workout(user_id)
        modified_workout = workouts.create_user_workout(
            selected_exercises, modified_workout_id
        )
        get_workout_name = workouts.get_workout_name(user_workout_id)
        workout_name = get_workout_name.scalar()
        session["workout_name"] = workout_name
        session["modified_workout_id"] = modified_workout_id
        session["workout_exercises"] = modified_workout

        return render_template(
            "modify_set_num.html",
            workout_name=workout_name,
            workout_exercises=modified_workout,
            user_workout_id=modified_workout_id,
            original_workout=original_workout,
        )


@app.route("/modify_sets_page", methods=["POST"])
def modify_sets_page():
    if request.method == "POST":
        users.check_csrf()
        user_workout_id = session.get("modified_workout_id")
        workout_name = session.get("workout_name")
        original_workout = session.get("user_workout_id")
        workouts.update_workout_name(user_workout_id, workout_name)
        error_message = None

        workout_exercises = []
        for key in request.form.keys():
            if key.startswith("sets_number_"):
                parts = key.split("_")
                if len(parts) >= 3 and parts[2]:
                    workout_exercise_id = int(parts[2])
                    sets_number = request.form[key] or None
                    if sets_number == None:
                        error_message = "Sets number is required."
                        break
                    sets_number = int(request.form[key])
                    updated_exercise = workouts.update_workout_exercises(
                        workout_exercise_id, sets_number
                    )
                    if updated_exercise:
                        exercise_id = updated_exercise[2]
                        exercise_name = workouts.get_exercise_name_by_id(exercise_id)
                        workout_exercises.append((updated_exercise, exercise_name))

        exercises = session.get("workout_exercises")
        if error_message:
            return render_template(
                "modify_set_num.html",
                workout_name=workout_name,
                error_message=error_message,
                workout_exercises=exercises,
                user_workout_id=user_workout_id,
                original_workout=original_workout,
            )
        return render_template(
            "add_new_sets.html",
            workout_name=workout_name,
            workout_exercises=workout_exercises,
            user_workout_id=user_workout_id,
            original_workout=original_workout,
        )


@app.route("/save_modifed_workout", methods=["POST"])
def save_modified_workout():
    if request.method == "POST":
        users.check_csrf()
        reps_data = defaultdict(dict)
        weight_data = defaultdict(dict)
        error_message = None
        for key, value in request.form.items():
            parts = key.split("_")
            value = value or None
            if len(parts) >= 3 and parts[0] in {"reps", "weight"}:
                data_type, exercise_id, set_num = parts[:3]
                if data_type == "reps":
                    if value == None:
                        error_message = "Reps number is required."
                        break
                    reps_data[int(exercise_id)][int(set_num)] = int(value)
                elif data_type == "weight":
                    if value == None:
                        error_message = "Weight number is required."
                        break
                    weight_data[int(exercise_id)][int(set_num)] = float(value)

        user_workout_id = session.get("modified_workout_id")
        old_workout_id = session.get("user_workout_id")
        session["user_workout_id"] = user_workout_id

        workout_name = session.get("workout_name")
        workouts.save_workout(user_workout_id, reps_data, weight_data)
        user_workout_data = workouts.exercise_ids_and_names(user_workout_id)

        if error_message:
            return render_template(
                "add_new_sets.html",
                workout_name=workout_name,
                error_message=error_message,
                workout_exercises=user_workout_data,
                user_workout_id=user_workout_id,
                original_workout=old_workout_id,
            )

        if user_workout_id:
            workouts.user_workout_completed(user_workout_id)
            workouts.hide_old_workout(old_workout_id)

        return render_template(
            "view_workout.html",
            user_workout=user_workout_data,
            workout_name=workout_name,
            message="Workout saved successfully!",
        )


@app.route("/completed_workouts")
def completed_workouts():
    user_id = session.get("user_id")
    completed_workouts = users.get_completed_workouts(user_id)

    return render_template(
        "completed_workouts.html", completed_workouts=completed_workouts
    )


@app.route("/view_completed_workouts")
def view_completed_workouts():
    completed_workout_id = request.args.get("workout_id")
    completed_workout = workouts.get_completed_workout(completed_workout_id)
    workout_exercises = workouts.get_completed_exercises(completed_workout_id)
    weight_lifted = workouts.get_completed_weights(completed_workout_id)
    reps_completed = workouts.get_completed_reps(completed_workout_id)
    weight_lifted = workouts.get_completed_weights(completed_workout_id)
    exercise_data = list(zip(workout_exercises, reps_completed, weight_lifted))
    user_workout_data = []
    for exercise_data in exercise_data:
        exercise_id, reps, weight = exercise_data
        exercise_name = workouts.get_exercise_name_by_id(exercise_id)
        user_workout_data.append(
            ((exercise_id, int(reps), float(weight)), exercise_name)
        )

    return render_template(
        "view_completed_workout.html",
        user_workout=user_workout_data,
        completed_workout=completed_workout,
    )


@app.route("/delete_user_workout")
def delete_user_workout():
    user_workout_id = request.args.get("workout_id")
    user_workout = workouts.get_user_workout_by_id(user_workout_id)

    if user_workout:
        workouts.mark_workout_as_deleted(user_workout_id)

    return redirect("/profile")


@app.route("/delete_completed_workout")
def delete_completed_workout():
    workout_id = request.args.get("workout_id")
    user_workout = workouts.get_completed_workout(workout_id)
    if user_workout:
        workouts.delete_completed(workout_id)

    return redirect("/completed_workouts")
