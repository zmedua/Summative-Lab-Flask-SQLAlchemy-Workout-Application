from flask import Flask, request, make_response
from flask_migrate import Migrate
from marshmallow import ValidationError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import ExerciseSchema, WorkoutSchema, WorkoutExerciseSchema

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)
db.init_app(app)
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

workout_exercise_schema = WorkoutExerciseSchema()

@app.route("/workouts", methods=["GET"])
def get_workouts():
    workouts =Workout.query.all()
    return make_response(workouts_schema.dump(workouts), 200)

@app.route("/workouts/<int:id>", methods=["GET"])
def get_workout(id):
    workout = Workout.query.get(id)

    if not workout:
        return make_response({"error": "Workout not found"}, 404)
    return make_response(workout_schema.dump(workout), 200)

@app.route("/workouts", methods=["POST"])
def create_workout():
    try:
        data = workout_schema.load(request.get_json())

        workout = Workout(
            date=data["date"],
            duration_minutes=data["duration_minutes"],
            notes=data.get("notes")

        )

        db.session.add(workout)
        db.session.commit()

        return make_response(workout_schema.dump(workout), 201)
    
    except ValidationError as e:
        return make_response({"errors": e.messages}, 400)
    except ValueError as e:
        return make_response({"error": str(e)}, 400)
@app.route("/workouts/<int:id>", methods=["DELETE"])
def delete_workout(id):
    workout = Workout.query.get(id)

    if not workout:
        return make_response({"error": "Workout not found"}, 404)

    db.session.delete(workout)
    db.session.commit()

    return make_response({}, 204)
@app.route("/exercises", methods=["GET"])
def get_exercises():
    exercises = Exercise.query.all()
    return make_response(exercises_schema.dump(exercises), 200)

@app.route("/exercises/<int:id>", methods=["GET"])
def get_exercise(id):
    exercise = Exercise.query.get(id)

    if not exercise:
        return make_response({"error": "Exercise not found"}, 404)
    return make_response(exercise_schema.dump(exercise), 200)

@app.route("/exercises",methods=["POST"])
def create_exercise():
    try:
        data = exercise_schema.load(request.get_json())
        exercise = Exercise(
            name=data["name"],
            category=data["category"],
            equipment_needed=data.get("equipment_needed", False)
        )

        db.session.add(exercise)
        db.session.commit()

        return make_response(exercise_schema.dump(exercise), 201)
    except ValidationError as e:
        return make_response({"errors": e.messages}, 400)

    except ValueError as e:
        return make_response({"error": str(e)}, 400)

@app.route("/exercises/<int:id>", methods=["DELETE"])
def delete_exercise(id):
    exercise = Exercise.query.get(id)

    if not exercise:
        return make_response({"error": "Exercise not found"}, 404)
    
    db.session.delete(exercise)
    db.session.commit()

    return make_response({}, 204)

@app.route("/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises", methods=["POST"])
def add_exercise_to_workout(workout_id, exercise_id):
    workout = Workout.query.get(workout_id)
    exercise = Exercise.query.get(exercise_id)

    if not workout:
        return make_response({"error": "Workout not found"}, 404)
    
    if not exercise:
        return make_response({"error": "Exercise not found"}, 404)
    
    try:
        data = workout_exercise_schema.load(request.get_json())

        workout_exercise = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id,
            reps=data.get("reps"),
            sets=data.get("sets"),
            duration_seconds=data.get("duration_seconds")
        )

        db.session.add(workout_exercise)
        db.session.commit()

        return make_response(workout_exercise_schema.dump(workout_exercise), 201)
    except ValidationError as e:
        return make_response({"errors": e.messages}, 400)

    except ValueError as e:
        return make_response({"error": str(e)}, 400)

if __name__ == "__main__":
    app.run(port=5555, debug=True)