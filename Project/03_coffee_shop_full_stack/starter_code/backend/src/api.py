import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS


from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

"""
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
"""
# db_drop_and_create_all()

# ROUTES
"""
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks")
def get_drinks():
    return jsonify(
        {"success": True, "drinks": list(map(lambda x: x.short(), Drink.query.all()))}
    )


"""
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drink_detail(jwt):
    try:
        drinks_result = list(map(lambda x: x.long(), Drink.query.all()))
    except:
        abort(422)
    return jsonify({"success": True, "drinks": drinks_result})


"""
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def add_drink(jwt):
    drink_req = request.get_json()
    if drink_req is None:
        abort(400)
    try:
        recipe = drink_req.get("recipe")
        if isinstance(recipe, dict):
            recipe = [recipe]
        elif not isinstance(recipe, list):
            abort(422)
        drink_result = Drink(title=drink_req.get("title"), recipe=json.dumps(recipe))
        drink_result.insert()
    except Exception as error:
        abort(422)
    return jsonify({"success": True, "drinks": [drink_result.long()]})


"""
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def edit_drink(jwt, drink_id):
    drink_req = request.get_json()
    drink_original = Drink.query.get(drink_id)

    if drink_req is None:
        abort(400)

    if drink_original is None:
        abort(404)
    try:
        drink_original.title = drink_req.get("title")
        recipe = drink_req.get("recipe")
        if isinstance(recipe, dict):
            recipe = [recipe]
        if isinstance(recipe, list):
            drink_original.recipe = json.dumps(recipe)
        drink_original.update()
    except:
        abort(422)
    return jsonify({"success": True, "drinks": [drink_original.long()]})


"""
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
"""


@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth("patch:drinks")
def remove_drink(jwt, drink_id):
    drink_original = Drink.query.get(drink_id)
    if drink_original is None:
        abort(404)
    try:
        drink_original.delete()
    except:
        abort(422)
    return jsonify({"success": True, "deleted": drink_id})


# Error Handling
"""
Example error handling for unprocessable entity
"""


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": 400, "message": "bad request"}), 400


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404, "message": "resource not found"}),
        404,
    )


@app.errorhandler(401)
def unauthorize(error):
    return jsonify({"success": False, "error": 401, "message": "unauthorize"}), 401


@app.errorhandler(500)
def internal_server(error):
    return (
        jsonify({"success": False, "error": 500, "message": "internal server"}),
        500,
    )


"""
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

"""

"""
@TODO implement error handler for 404
    error handler should conform to general task above
"""


"""
@TODO implement error handler for AuthError
    error handler should conform to general task above
"""
