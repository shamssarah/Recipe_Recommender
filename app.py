from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy


# def create_app():
app = Flask(__name__)
    #Configuration


db = SQLAlchemy()

@app.route("/", methods=["GET"])
def index():
    return jsonify(message="Recipe Recommender API", status="ok")

#MODELS

#CRUD
"""
Recipe Creators
"""
class User (db.Model):
    id = db.Column (db.Integer, primary_key=True)
    name = db.Column (db.String(100), unique= True, nullable=False)
    
# def create_user():
# def delete_user():
# def update_user():
# def get_user():

"""
Recipe
"""
class Recipe (db.Model):
    creator_id =  db.relationship('User', backref='creator', lazy=True)
    id = db.Column (db.Integer, primary_key=True)
    name = db.Column (db.String(100), unique= True, nullable=False)

# def create_recipe ():
# def delete_recipe():
# def update_recipe():
# def get_recipe():

# @app.route("/fetch-all-recipes",methods=['GET,'POST'])
# def get_recipes(): #all recipes fetched that match the ingredients inserted into 'search engine'

@app.route("/recipes", methods=["GET"])
def list_recipes():
    # placeholder sample data
    sample_recipes = [
        {"id": 1, "name": "Pancakes", "ingredients": ["flour", "milk", "egg"]},
        {"id": 2, "name": "Omelette", "ingredients": ["egg", "cheese", "salt"]},
    ]
    return jsonify(recipes=sample_recipes)

@app.route("/recipes", methods=["POST"])
def create_recipe():
    data = request.get_json(silent=True) or {}
    # echo back received data with a fake id (replace with DB logic later)
    recipe = {"id": 999, **data}
    return jsonify(recipe=recipe), 201

if __name__ == "__main__":
    # app = create_app()
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(host="127.0.0.1", port=5000, debug=True)