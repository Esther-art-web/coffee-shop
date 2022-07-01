import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db, db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
@requires_auth('get:drinks')
def get_all_drinks(payload):
    try:
        drinks = Drink.query.all()
    except Exception:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })
# '''
# @TODO implement endpoint
#     GET /drinks-detail
#         it should require the 'get:drinks-detail' permission
#         it should contain the drink.long() data representation
#         returns status code 200 and json {"success": True, "drinks": drinks}
#         where drinks is the list of drinks
#         or appropriate status code indicating reason for failure
# '''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.all()
    except Exception:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True,
        "drinks": drink} where drink an array containing only
        the newly created drink or appropriate status code
        indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_new_drink(payload):
    drinks = []
    try:
        body = request.get_json()
        title = body.get('title')
        recipe = body.get('recipe')
        recipe = json.dumps(recipe)
        new_drink = Drink(title=title, recipe=recipe)
        new_drink.insert()
        drinks.append(new_drink.long())
    except Exception:
        db.session.rollback()
        abort(400)
    finally:
        db.session.close()
    return jsonify({
        'success': True,
        'drinks': drinks
    })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True,
        "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink_detail(payload, id):
    drinks = []
    try:
        drink = Drink.query.get(id)
        body = request.get_json()
        if drink:
            for data in body:
                if data == 'recipe':
                    setattr(drink, data, json.dumps(body[data]))
                else:
                    setattr(drink, data, body[data])
            drink.update()
            drinks.append(drink.long())
        else:
            abort(404)
    except Exception:
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()
    return jsonify({
        'success': True,
        'drinks': drinks
    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True,
        "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drinks = []
    try:
        drink = Drink.query.get(id)
        drinks.append(drink.long())
        drink.delete()
    except Exception:
        db.session.rollback()
        abort(404)
    finally:
        db.session.close()
    return jsonify({
        'success': True,
        'drinks': drinks
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "resource not found"
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
