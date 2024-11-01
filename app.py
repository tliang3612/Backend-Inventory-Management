from backend.db.tabledef import app
from helpers.load_database_data import load_inventories_from_db
from backend.inventory import Inventory

from flask import Flask, Response, request, jsonify
from functools import wraps



class User:
    def __init__(self, name, user_name, password, inventory :list[Inventory] = None, index = 0):
        self.name = name
        self.user_name = user_name
        self.password = password
        try:
            self.inventory = inventory[index]
        except Exception:
            self.inventory = Inventory()
            print(f'Inventory doesnt exist yet for {name}. Creating inventory with id: {self.inventory.id}')
        self.id = self.inventory.id

    def serialize(self):
        return {'name' : self.name,
                'id' : self.id,
                'inventory' : self.inventory.serialize()}


def handle_invalid_inventory(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except IndexError:
            return jsonify({'error': f'No inventory exists with that id'}), 404
    return decorator


def populate_inventories(inventories_list:list[Inventory], usernames):

    for i in range(len(inventories_list)):
        inventories_list[i].create_item(f"{usernames[i]}'s Chips", 5, "2023-12-25", 1.00)
        inventories_list[i].create_item(f"{usernames[i]}'s Candy",10, "2023-12-25", 2.00)
        inventories_list[i].create_item(f"{usernames[i]}'s Soda",15, "2023-12-25", 3.00)
        inventories_list[i].create_item(f"{usernames[i]}'s Gum", 20, "2023-12-25", 4.00)


def init_users_and_inventories(existing_inventories:list[Inventory]):
    # each user's id will correspond to their associated inventory
    users = [User("John", "John22", "johnpassword", existing_inventories, 0),
             User("Jane", "Jane22", "janepassword", existing_inventories, 1),
             User("Bob", "Bob22", "bobpassword", existing_inventories, 2)]

    if not existing_inventories:
        populate_inventories([x.inventory for x in users], [x.name for x in users])
    return users

inventories = load_inventories_from_db()
users = init_users_and_inventories(inventories)


# ======== Routing =========================================================== #

@app.route('/login', methods=['POST'])
@handle_invalid_inventory
def user_login():
    username = request.json['username']
    password = request.json['password']

    matching_users = [x for x in users if x.user_name == username]
    user = matching_users[0] if matching_users else None


    if user is not None:
        if password == user.password:
            return jsonify({"user_info" : user.serialize() }), 200
        else:
            return Response(response=f'Invalid password for {username}', status=401)
    return Response(response=f'Invalid username: {username}', status=401)

#---------------------- Inventory Stuff -----------------------------#

@app.route('/inventory', methods=['GET'])
@handle_invalid_inventory
def get_inventory_ids():
    inventory_ids = []
    for inventory in inventories:
        inventory_ids.append(inventory.id)
    return inventory_ids

#------------------------ Items Stuff --------------------------------#

@app.route('/inventory/<int:inventory_id>', methods=['GET'])
@handle_invalid_inventory
def get_all_inventory_items(inventory_id):
    target_inventory = inventories[int(inventory_id)-1]
    return target_inventory.serialize()

@app.route('/inventory/<int:inventory_id>/<int:item_id>', methods=['GET'])
@handle_invalid_inventory
def get_inventory_item(inventory_id, item_id):
    target_inventory = inventories[int(inventory_id)-1]
    try:
        target_item = target_inventory.get_item(item_id)
    except Exception as e:
        return jsonify({'error' : str(e)}, 404)

    return jsonify({"item" : target_item.serialize() }), 200

@app.route('/inventory/<int:inventory_id>/<int:item_id>', methods=['PUT'])
@handle_invalid_inventory
def update_item_quantity(inventory_id, item_id):
    target_inventory = inventories[int(inventory_id)-1]
    quantity = request.json.get("item_quantity")
    try:
        updated_item = target_inventory.set_item_quantity(item_id, quantity)
    except Exception as e:
        return jsonify({'error' : str(e)}, 400)

    return jsonify({"item " : updated_item.serialize()}, 200)


@app.route('/inventory/<int:inventory_id>', methods=['POST'])
@handle_invalid_inventory
def create_item(inventory_id):
    target_inventory = inventories[int(inventory_id)-1]
    name = request.json.get("item_name")
    capacity = request.json.get("item_capacity")
    exp_date = request.json.get("item_exp_date")
    price = request.json.get("item_price")

    try:
        new_item = target_inventory.create_item(name, capacity, exp_date, price)
    except Exception as e:
        return jsonify({'error' : str(e)}, 400)

    return jsonify({"item" : new_item.serialize()}), 200

@app.route('/inventory/<int:inventory_id>/<int:item_id>', methods=['DELETE'])
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
