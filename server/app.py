#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

# Flask app creation: Initializes the Flask application.
app = Flask(__name__)

# Database URI: Specifies the SQLite database location.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///plants.db"

# Track Modifications: Disables tracking modifications to save memory.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Compact JSON: Configures JSON output to not be compact.
app.json.compact = False


# Migrate: Binds the Flask application and SQLAlchemy database
# instance for handling migrations.
migrate = Migrate(app, db)

# db.init_app(app): Initializes the database with the Flask application.
db.init_app(app)

# Api(app): Initializes the Flask-RESTful API with the Flask app.
api = Api(app)


class Plants(Resource):
    # get method: Fetches all plants from the database,
    # converts them to dictionaries, and returns them
    # as a JSON response with a 200 status code.
    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    # post method: Receives JSON data, creates a new Plant
    # instance, adds it to the database, commits the
    # transaction, and returns the new plant as JSON with a 201 status code.
    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data["name"],
            image=data["image"],
            price=data["price"],
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)


api.add_resource(Plants, "/plants")


class PlantByID(Resource):
    # get method: Fetches a plant by its ID, returns
    # it as JSON if found, or returns a 404 error if not found.
    def get(self, id):
        plant = Plant.query.filter_by(id=id).first()

        if plant is None:
            return make_response(jsonify({"error": "Plant not found"}), 404)

        return make_response(jsonify(plant.to_dict()), 200)

    # patch method: Receives JSON data, updates the is_in_stock
    # attribute of the plant if found, commits the change, and returns
    # the updated plant as JSON. Returns a 404 error if the plant is not found.
    def patch(self, id):
        data = request.get_json()
        plant = Plant.query.filter_by(id=id).first()

        if plant is None:
            return make_response(jsonify({"error": "Plant not found"}), 404)

        if "is_in_stock" in data:
            plant.is_in_stock = data["is_in_stock"]

        db.session.add(plant)
        db.session.commit()

        return make_response(jsonify(plant.to_dict()), 200)

    # delete method: Deletes a plant by its ID, commits the transaction,
    # and returns a 204 status code. Returns a 404 error if the plant is not found.
    def delete(self, id):
        plant = Plant.query.filter_by(id=id).first()

        if plant is None:
            return make_response(jsonify({"error": "Plant not found"}), 404)

        db.session.delete(plant)
        db.session.commit()

        return make_response("", 204)


api.add_resource(PlantByID, "/plants/<int:id>")


# Main block: Runs the Flask application on port
# 5555 in debug mode, which provides detailed error
# messages and automatic reloading during development.
if __name__ == "__main__":
    app.run(port=5555, debug=True)
