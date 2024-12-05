import datetime
import re

import jwt
from backend.db.flask_app import app
from helpers.load_database_data import *
from backend.sql_inventory import SqlInventory
from backend.mdb_inventory import MdbInventory
from backend.user import User, UserFactory
from flask import request, jsonify, session, make_response
from functools import wraps

def handle_invalid_inventory(f):
    @wraps(f)
    def decorator(db_type, inventory_id, *args, **kwargs):
        inventory_ids = [users[index].id for index in range(len(users))]
        if not isinstance(inventory_id, int):
            return jsonify({'error': f'Inventory id of {inventory_id} must be an integer'}), 404
        if inventory_id not in inventory_ids:
            return jsonify({'error': f'No inventory exists with ID {inventory_id}'}), 404
        if db_type != 'sql' and db_type != 'mdb':
            return jsonify({'error': f'Incorrect database type chosen {db_type}'}), 404
        return f(db_type, inventory_id, *args, **kwargs)

    return decorator
def handle_user_authentication(f):
    @wraps(f)
    def decorator(db_type, inventory_id, *args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Session has expired please login again."}), 401
        if session.get('user_id') != inventory_id:
            return jsonify({"error": "Unauthorized access to inventory"}), 403
        return f(db_type, inventory_id, *args, **kwargs)

    return decorator
def handle_invalid_field(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400

    return decorator
def get_target_user(user_id):
    for user in users:
        if user.id == user_id:
            return user
    return None

# ----------------- User Authentication -------------------------------------------- #


@app.route('/register', methods=['POST'])
@handle_invalid_field
def user_register():
    username = request.json["username"]
    password = request.json["password"]
    name = request.json["name"]
    email = request.json["email"]

    email_regex = r".+@.+\..+" # .+ -> one or more chars
                               # @ -> @ symbol
                               # .+\. -> one or more char follows @, then dot
                               # .+ -> one or more char after .

    if not re.match(email_regex, email):
        return jsonify({"error": "bad email"}), 400

    if username in [x.username for x in users]:
        return jsonify({"error": f"Username already exists for {username}"}), 409

    new_user = UserFactory.create_user(name, username, password, email, False)
    users.append(new_user)

    return jsonify({"user_info": new_user.serialize()}), 201

@app.route('/login', methods=['POST'])
@handle_invalid_field
def user_login():
    username = request.json['username']
    password = request.json['password']

    matching_users = [x for x in users if x.username == username]
    user = matching_users[0] if matching_users else None

    if user and user.password == password:
        session.permanent = True
        session['user_id'] = user.id
        token = jwt.encode(
            {
                #payload
                'iss': "https://inventory-management.com",
                'aud': "inventory-management-client",
                'sub': user.id,
                'user_id': user.id,
                'exp': datetime.datetime.now() + datetime.timedelta(hours=1)
            },
            app.config['SECRET_KEY'], #signature
            algorithm="HS256" #head
        )

        response = make_response(jsonify({"login message": "Login successful"}))
        response.set_cookie(
            'auth_token',token,
            httponly=True, secure=True,
            samesite='Strict', max_age=1800
        )
        return response, 200
    return jsonify({'error': "Invalid credentials"}), 401


@app.route('/logout', methods=['POST'])
@handle_invalid_field
def user_logout():
    temp_user_id = session['user_id']
    response = make_response(jsonify({"message": f"Successfully logged out user of id {temp_user_id}"}))
    response.delete_cookie('auth_token')
    session.clear()  # remove session data and log out the user
    return response, 200

# ---------------------- Inventory Stuff -----------------------------#

@app.route('/inventory', methods=['GET'])
@handle_invalid_field
def get_all_inventory_ids():
    inventory_ids = [users[index].id for index in range(len(users)) ]
    return jsonify(inventory_ids)

@app.route('/inventory/<string:db_type>/<int:inventory_id>', methods=['GET'])
@handle_user_authentication
@handle_invalid_inventory
def get_all_inventory_items(db_type, inventory_id):
    target_user = get_target_user(inventory_id)
    target_inventory = target_user.get_inventory_of_type(db_type)
    return jsonify(target_inventory.serialize())

@app.route('/inventory/<string:db_type>/<int:inventory_id>/<int:item_id>', methods=['GET'])
@handle_user_authentication
@handle_invalid_inventory
def get_inventory_item(db_type, inventory_id, item_id):
    target_user = get_target_user(inventory_id)
    target_inventory = target_user.get_inventory_of_type(db_type)
    try:
        target_item = target_inventory.get_item(item_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

    return jsonify({"item": target_item.serialize()}), 200


@app.route('/inventory/<string:db_type>/<int:inventory_id>/<int:item_id>', methods=['PUT'])
@handle_user_authentication
@handle_invalid_inventory
def update_item_quantity(db_type, inventory_id, item_id):
    target_user = get_target_user(inventory_id)
    target_inventory = target_user.get_inventory_of_type(db_type)
    quantity = request.json["item_quantity"]
    try:
        updated_item = target_inventory.set_item_quantity(item_id, quantity)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    return jsonify({"item": updated_item.serialize()}), 200


@app.route('/inventory/<string:db_type>/<int:inventory_id>', methods=['POST'])
@handle_user_authentication
@handle_invalid_inventory
def create_item(db_type, inventory_id):
    target_user = get_target_user(inventory_id)
    target_inventory = target_user.get_inventory_of_type(db_type)

    name = request.json["item_name"]
    quantity = request.json["item_quantity"]
    capacity = request.json["item_capacity"]
    description = request.json["item_description"]
    price = request.json["item_price"]

    try:
        new_item = target_inventory.create_item(name, capacity, quantity, description, price)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({"item": new_item.serialize()}), 200


@app.route('/inventory/<string:db_type>/<int:inventory_id>/<int:item_id>', methods=['DELETE'])
@handle_invalid_inventory
@handle_user_authentication
def delete_item(db_type, inventory_id, item_id):
    target_user = get_target_user(inventory_id)
    target_inventory = target_user.get_inventory_of_type(db_type)

    try:
        target_inventory.delete_item(item_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'success': 'Item deleted'}), 200

# ======== Main ============================================================== #
if __name__ == "__main__":
    users = UserFactory.create_users_from_names(['John', 'Bob', "Mary"])
    app.run(debug=True, use_reloader=False, port=5000)
