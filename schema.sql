CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username TEXT,
    password_hash TEXT
);

CREATE TABLE exercises (
    exercise_id SERIAL PRIMARY KEY,
    exercise_name TEXT,
    muscle_group TEXT,
    details TEXT
);

CREATE TABLE user_workouts (
    user_workout_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    workout_name TEXT,
    scheduled_dates DATE[],
    is_archived BOOLEAN DEFAULT FALSE,
    is_completed BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE

);

CREATE TABLE workout_exercises (
    workout_exercise_id SERIAL PRIMARY KEY,
    user_workout_id INTEGER REFERENCES user_workouts(user_workout_id),
    exercise_id INTEGER REFERENCES exercises(exercise_id),
    sets_number INTEGER,
    reps_per_set INTEGER[],
    weights_per_set FLOAT[],
    rest_period INTEGER
);

CREATE TABLE completed_workouts (
    completed_workout_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    user_workout_id INTEGER REFERENCES user_workouts(user_workout_id),
    workout_name TEXT,
    exercise_ids INTEGER[],
    completion_date DATE,
    weight_lifted FLOAT[],
    reps_completed INTEGER[]
);