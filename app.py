from backend.db.tabledef import app
from helpers.load_database_data import load_inventories_from_db
from backend.inventory import Inventory
from flask import Flask, Response, request, jsonify, session
from functools import wraps

class User:
    def __init__(self, name, user_name, password, email, inventory :list[Inventory] = None, index = 0):
        self.name = name
        self.username = user_name
        self.password = password
        self.email = email
        try:
            self.inventory = inventory[index]
        except Exception:
            self.inventory = Inventory()
            print(f'Inventory doesnt exist yet for {name}. Creating inventory with id: {self.inventory.id}')
        self.id = self.inventory.id

    def serialize(self):
        return {'name' : self.name,
                'id' : self.id,
                'email' : self.email,
                'inventory' : self.inventory.serialize()
                }


def handle_invalid_inventory(f):
    @wraps(f)
    def decorator(inventory_id, *args, **kwargs):
        if not (0 <= inventory_id - 1 < len(inventories)):
            return jsonify({'error': f'No inventory exists with ID {inventory_id}'}), 404
        return f(inventory_id, *args, **kwargs)
    return decorator


def handle_user_authentication(f):
    @wraps(f)
    def decorator(inventory_id, *args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Session has expired please login again."}), 401
        if session.get('user_id') != inventory_id:
            return jsonify({"error": "Unauthorized access to inventory"}), 403
        return f(inventory_id, *args, **kwargs)
    return decorator


def handle_invalid_field(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {e.args[0]}"}), 400
    return decorator


def populate_inventories(inventories_list:list[Inventory], usernames:list[str]):
    for i in range(len(inventories_list)):
        inventories_list[i].create_item(f"{usernames[i]}'s Chips", 5, "2023-12-25", 1.00)
        inventories_list[i].create_item(f"{usernames[i]}'s Candy",10, "2023-12-25", 2.00)
        inventories_list[i].create_item(f"{usernames[i]}'s Soda",15, "2023-12-25", 3.00)
        inventories_list[i].create_item(f"{usernames[i]}'s Gum", 20, "2023-12-25", 4.00)


def init_users_and_inventories(existing_inventories:list[Inventory]):
    # each user's id will correspond to their associated inventory
    users = [User("John", "John22", "john_password", "john_email", existing_inventories, 0),
             User("Jane", "Jane22", "jane_password", "jane_email", existing_inventories, 1),
             User("Bob", "Bob22", "bob_password", "bob_email", existing_inventories, 2)]

    if not existing_inventories:
        populate_inventories([x.inventory for x in users], [x.name for x in users])
    return users

inventories = load_inventories_from_db()
users = init_users_and_inventories(inventories)


# ----------------- User Authentication -------------------------------------------- #


@app.route('/register', methods=['POST'])
@handle_invalid_field
def user_register():
    username = request.json["username"]
    password = request.json["password"]
    name = request.json["name"]
    email = request.json["email"]

    if username in [x.username for x in users]:
        return jsonify({"error": f"Username already exists for {username}"}), 409  #

    new_user = User(name,username, password,email)
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
        return jsonify({"user_info": user.serialize()}), 200
    return Response("Invalid credentials", status=401)


@app.route('/logout', methods=['POST'])
def user_logout():
    temp_user_id = session['user_id']
    session.clear() # remove session data and log out the user
    return jsonify({"logout message": f"Logged out user with id of {temp_user_id}"}), 200

#---------------------- Inventory Stuff -----------------------------#

@app.route('/inventory', methods=['GET'])
def get_inventory_ids():
    inventory_ids = []
    for inventory in inventories:
        inventory_ids.append(inventory.id)
    return inventory_ids


#------------------------ Items Stuff --------------------------------#


@app.route('/inventory/<int:inventory_id>', methods=['GET'])
@handle_user_authentication
@handle_invalid_inventory
def get_all_inventory_items(inventory_id):
    target_inventory = inventories[int(inventory_id)-1]
    return target_inventory.serialize()


@app.route('/inventory/<int:inventory_id>/<int:item_id>', methods=['GET'])
@handle_user_authentication
@handle_invalid_inventory
def get_inventory_item(inventory_id, item_id):
    target_inventory = inventories[int(inventory_id)-1]
    try:
        target_item = target_inventory.get_item(item_id)
    except Exception as e:
        return jsonify({'error' : str(e)}, 404)

    return jsonify({"item" : target_item.serialize() }), 200


@app.route('/inventory/<int:inventory_id>/<int:item_id>', methods=['PUT'])
@handle_user_authentication
@handle_invalid_inventory
@handle_invalid_field
def update_item_quantity(inventory_id, item_id):
    target_inventory = inventories[int(inventory_id)-1]
    quantity = request.json["item_quantity"]
    try:
        updated_item = target_inventory.set_item_quantity(item_id, quantity)
    except Exception as e:
        return jsonify({'error' : str(e)}, 400)
    return jsonify({"item " : updated_item.serialize()}, 200)


@app.route('/inventory/<int:inventory_id>', methods=['POST'])
@handle_user_authentication
@handle_invalid_inventory
@handle_invalid_field
def create_item(inventory_id):
    target_inventory = inventories[int(inventory_id)-1]
    name = request.json["item_name"]
    capacity = request.json["item_capacity"]
    exp_date = request.json["item_exp_date"]
    price = request.json["item_price"]

    try:
        new_item = target_inventory.create_item(name, capacity, exp_date, price)
    except Exception as e:
        return jsonify({'error' : str(e)}, 400)

    return jsonify({"item" : new_item.serialize()}), 200


@app.route('/inventory/<int:inventory_id>/<int:item_id>', methods=['DELETE'])
@handle_user_authentication
@handle_invalid_inventory
def delete_item(inventory_id, item_id):
    target_inventory = inventories[int(inventory_id)-1]
    try:
        target_inventory.delete_item(item_id)
    except Exception as e:
        return jsonify({'error' : str(e)}, 400)

    return jsonify({'success': 'Item deleted'}), 200


# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=5000)
