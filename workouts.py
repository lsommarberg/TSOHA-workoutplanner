from datetime import datetime
from sqlalchemy import text
from db import db


def add_example_exercises(exercise_data):
    for exercise_data in exercise_data:
        exercise_name = exercise_data["exercise_name"]
        muscle_group = exercise_data["muscle_group"]
        details = exercise_data["details"]
        sql_check_existing_exercise = text(
            "SELECT * FROM exercises WHERE exercise_name=:exercise_name"
        )
        result_existing_exercise = db.session.execute(
            sql_check_existing_exercise, {"exercise_name": exercise_name}
        )
        existing_exercise = result_existing_exercise.fetchone()

        if not existing_exercise:
            sql_insert_exercise = text(
                "INSERT INTO exercises (exercise_name, muscle_group, details) "
                "VALUES (:exercise_name, :muscle_group, :details)"
            )
            db.session.execute(
                sql_insert_exercise,
                {
                    "exercise_name": exercise_name,
                    "muscle_group": muscle_group,
                    "details": details,
                },
            )

    db.session.commit()


def get_exercises():
    sql = text("SELECT * FROM exercises")
    result = db.session.execute(sql)
    exercises = result.fetchall()
    return exercises


def exercise_names():
    sql = text("SELECT exercise_id, exercise_name FROM exercises")
    result = db.session.execute(sql)
    exercises = result.fetchall()
    return exercises


def get_exercise_by_name(exercise_name):
    sql = text("SELECT * FROM exercises WHERE exercise_name = :exercise_name")
    result = db.session.execute(sql, {"exercise_name": exercise_name})
    exercise = result.fetchone()
    return exercise


def create_workout(user_id):
    if user_id:
        sql_create_workout = text(
            "INSERT INTO user_workouts (user_id, workout_name, scheduled_dates, is_archived, is_completed) "
            "VALUES (:user_id, 'Your Workout Name', ARRAY[]::date[], false, false) "
            "RETURNING user_workout_id"
        )
        result_create_workout = db.session.execute(
            sql_create_workout, {"user_id": user_id}
        )

        user_workout_id = result_create_workout.fetchone()[0]

        return user_workout_id
    return None


def create_user_workout(selected_exercises, user_workout_id):
    if user_workout_id:
        workout_exercise_ids_and_names = []

        for exercise_id in selected_exercises:
            exercise_name = get_exercise_name_by_id(exercise_id)

            sql_insert = text(
                "INSERT INTO workout_exercises (user_workout_id, exercise_id, sets_number, weights_per_set, reps_per_set) "
                "VALUES (:user_workout_id, :exercise_id, 0, NULL, NULL) RETURNING workout_exercise_id"
            )

            result = db.session.execute(
                sql_insert,
                {"user_workout_id": user_workout_id, "exercise_id": exercise_id},
            )
            inserted_id = result.fetchone()[0]
            workout_exercise_ids_and_names.append((inserted_id, exercise_name))

        db.session.commit()

        return workout_exercise_ids_and_names

    return None


def update_workout_name(user_workout_id, workout_name):
    if user_workout_id:
        sql_update_workout_name = text(
            "UPDATE user_workouts SET workout_name=:workout_name "
            "WHERE user_workout_id=:user_workout_id"
        )
        db.session.execute(
            sql_update_workout_name,
            {"workout_name": workout_name, "user_workout_id": user_workout_id},
        )


def get_user_workout_by_id(user_workout_id):
    if user_workout_id:
        sql = text("SELECT * FROM user_workouts WHERE user_workout_id=:user_workout_id")
        result = db.session.execute(sql, {"user_workout_id": user_workout_id})
        user_workout = result.fetchone()
        return user_workout
    return None


def update_workout_exercises(workout_exercise_id, sets_number):
    if workout_exercise_id:
        sql = text(
            "UPDATE workout_exercises SET sets_number=:sets_number WHERE workout_exercise_id=:workout_exercise_id"
        )
        db.session.execute(
            sql,
            {"sets_number": sets_number, "workout_exercise_id": workout_exercise_id},
        )
        db.session.commit()

        sql = text(
            "SELECT * FROM workout_exercises WHERE workout_exercise_id=:workout_exercise_id"
        )
        result = db.session.execute(sql, {"workout_exercise_id": workout_exercise_id})
        updated_exercise = result.fetchone()

        return updated_exercise
    return None


def get_exercise_name_by_id(exercise_id):
    if exercise_id:
        sql = text("SELECT exercise_name FROM exercises WHERE exercise_id=:exercise_id")
        result = db.session.execute(sql, {"exercise_id": exercise_id})
        exercise = result.fetchone()
        if exercise:
            return exercise[0]
    return None


def save_workout(user_workout_id, reps_data, weight_data):
    if user_workout_id:
        user_workout = get_user_workout_by_id(user_workout_id)

        workout_exercises = get_workout_exercises_by_workout_id(user_workout_id)

        for exercise in workout_exercises:
            exercise_id = exercise[0]

            if exercise_id in reps_data:
                update_reps_sql = text(
                    "UPDATE workout_exercises SET reps_per_set=:reps_per_set WHERE workout_exercise_id=:exercise_id"
                )
                db.session.execute(
                    update_reps_sql,
                    {
                        "reps_per_set": list(reps_data[exercise_id].values()),
                        "exercise_id": exercise_id,
                    },
                )
            if exercise_id in weight_data:
                update_weights_sql = text(
                    "UPDATE workout_exercises SET weights_per_set=:weights_per_set WHERE workout_exercise_id=:exercise_id"
                )
                db.session.execute(
                    update_weights_sql,
                    {
                        "weights_per_set": list(weight_data[exercise_id].values()),
                        "exercise_id": exercise_id,
                    },
                )

        db.session.commit()

        return user_workout[0]
    return None


def user_workout_completed(user_workout_id):
    if user_workout_id:
        sql_update_completion = text(
            "UPDATE user_workouts SET is_completed=true WHERE user_workout_id=:user_workout_id"
        )
        db.session.execute(sql_update_completion, {"user_workout_id": user_workout_id})
        db.session.commit()


def delete_workout_exercise(item_id):
    if item_id:
        sql = text("DELETE FROM workout_exercises WHERE workout_exercise_id=:item_id")
        db.session.execute(sql, {"item_id": item_id})
        db.session.commit()


def delete_workout(workout_id):
    if workout_id:
        workout_id = int(workout_id)

        user_workout = get_user_workout_by_id(workout_id)

        if user_workout:
            workout_exercises = get_workout_exercises_by_workout_id(workout_id)

            for exercise in workout_exercises:
                delete_workout_exercise(exercise[0])

            sql_delete_user_workout = text(
                "DELETE FROM user_workouts WHERE user_workout_id=:user_workout_id"
            )
            db.session.execute(sql_delete_user_workout, {"user_workout_id": workout_id})
            db.session.commit()


def get_workout_exercises_by_workout_id(user_workout_id):
    if user_workout_id:
        workout = get_user_workout_by_id(user_workout_id)

        if workout:
            sql_workout_exercises = text(
                "SELECT * FROM workout_exercises WHERE user_workout_id=:user_workout_id"
            )
            result_workout_exercises = db.session.execute(
                sql_workout_exercises, {"user_workout_id": workout[0]}
            )
            workout_exercises = result_workout_exercises.fetchall()
            return workout_exercises

    return None


def get_workout_name(user_workout_id):
    workout_name_sql = text(
        "SELECT workout_name FROM user_workouts WHERE user_workout_id=:user_workout_id"
    )
    result_workout_name = db.session.execute(
        workout_name_sql, {"user_workout_id": user_workout_id}
    )

    return result_workout_name


def exercise_ids_and_names(user_workout_id):
    workout_exercises = []
    exercises = get_workout_exercises_by_workout_id(user_workout_id)
    for exercise in exercises:
        exercise_id = exercise[2]
        exercise_name = get_exercise_name_by_id(exercise_id)
        workout_exercises.append((exercise, exercise_name))

    return workout_exercises


def log_workout(user_workout_id, user_id):
    if user_workout_id:
        workout_exercises = get_workout_exercises_by_workout_id(user_workout_id)

        completion_date = datetime.now().date()
        get_name = get_workout_name(user_workout_id)
        workout_name = get_name.scalar()
        weight_lifted = []
        reps_completed = []

        for exercise in workout_exercises:
            reps = sum(exercise[4])
            weight = sum(exercise[5])

            reps_completed.append(reps)
            weight_lifted.append(weight)

        sql_insert_completed_workout = text(
            "INSERT INTO completed_workouts (user_workout_id, user_id, workout_name, completion_date, exercise_ids, weight_lifted, reps_completed) "
            "VALUES (:user_workout_id, :user_id, :workout_name, :completion_date, :exercise_ids, :weight_lifted, :reps_completed)"
        )
        db.session.execute(
            sql_insert_completed_workout,
            {
                "user_workout_id": user_workout_id,
                "user_id": user_id,
                "workout_name": workout_name,
                "completion_date": completion_date,
                "exercise_ids": [exercise[2] for exercise in workout_exercises],
                "weight_lifted": weight_lifted,
                "reps_completed": reps_completed,
            },
        )
        db.session.commit()


def hide_old_workout(user_workout_id):
    if user_workout_id:
        sql_update = text(
            "UPDATE user_workouts SET is_completed=false WHERE user_workout_id=:user_workout_id"
        )
        db.session.execute(sql_update, {"user_workout_id": user_workout_id})
        db.session.commit()


def get_completed_workout(workout_id):
    if workout_id:
        sql = text(
            "SELECT * FROM completed_workouts WHERE completed_workout_id=:workout_id"
        )
        result = db.session.execute(sql, {"workout_id": workout_id})
        user_workout = result.fetchone()
        return user_workout
    return None


def get_completed_exercises(workout_id):
    if workout_id:
        sql = text(
            "SELECT exercise_ids FROM completed_workouts WHERE completed_workout_id=:workout_id"
        )
        result = db.session.execute(sql, {"workout_id": workout_id})
        exercises = result.fetchone()
        if exercises:
            return exercises[0]
    return None


def get_completed_reps(workout_id):
    if workout_id:
        sql = text(
            "SELECT reps_completed FROM completed_workouts WHERE completed_workout_id=:workout_id"
        )
        result = db.session.execute(sql, {"workout_id": workout_id})
        reps = result.fetchone()
        if reps:
            return reps[0]
    return None


def get_completed_weights(workout_id):
    if workout_id:
        sql = text(
            "SELECT weight_lifted FROM completed_workouts WHERE completed_workout_id=:workout_id"
        )
        result = db.session.execute(sql, {"workout_id": workout_id})
        weight = result.fetchone()
        if weight:
            return weight[0]
    return None


def mark_workout_as_deleted(workout_id):
    if workout_id:
        sql = text(
            "UPDATE user_workouts SET is_deleted = TRUE WHERE user_workout_id = :workout_id"
        )
        db.session.execute(sql, {"workout_id": workout_id})
        db.session.commit()


def delete_completed(workout_id):
    sql_delete_user_workout = text(
        "DELETE FROM completed_workouts WHERE completed_workout_id=:workout_id"
    )
    db.session.execute(sql_delete_user_workout, {"workout_id": workout_id})
    db.session.commit()
