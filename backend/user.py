from backend.base_inventory import BaseInventory
from helpers.load_database_data import *

class User:
    def __init__(self, name, user_name, password, email,sql_inventory, mdb_inventory):
        self.name = name
        self.username = user_name
        self.password = password
        self.email = email
        self.sql_inventory = sql_inventory
        self.mdb_inventory = mdb_inventory
        self.id = sql_inventory.id

    def serialize(self):
        return {
                'name': self.name,
                'id': self.id,
                'email': self.email,
                'mysql_inventory': self.sql_inventory.serialize(),
                'mdb_inventory' : self.mdb_inventory.serialize()
                }

    def get_inventory_of_type(self, db_type) -> BaseInventory:
        if db_type == 'sql':
            return self.sql_inventory
        elif db_type == 'mdb':
            return self.mdb_inventory
        else:
            return None

class UserFactory:
    @staticmethod
    def create_users_from_names(names: list[str]) -> list[User]:
        created_users = []
        #each users id will correspond to their associated inventory
        for i in range(len(names)):
            user = UserFactory.create_user(names[i], f'{names[i]}22', f'{names[i]}_password',
                                                        f'{names[i]}_email', True, i + 1)
            created_users.append(user)

        return created_users

    @staticmethod
    def create_user(name: str, username: str, password: str, email: str, should_populate: bool = False, user_id: int = None):
        #check if the inventory exists in both mdb and sql
        mdb_inventory_exists = check_inventory_exists('mdb', user_id)
        sql_inventory_exists = check_inventory_exists('sql', user_id)
        print(f"Does Inventory Exist for {name}?\n MongoDB: {mdb_inventory_exists}\n MySQL: {sql_inventory_exists}\n")

        if not mdb_inventory_exists:
            mdb_inventory = MdbInventory()  # inventory doesn't exist yet, create it for user
            if should_populate:
                UserFactory.populate_mdb_inventory(name, mdb_inventory)
            print(f"MongoDB inventory doesn't exist for {name}. Created a new inventory with ID: {mdb_inventory.id}\n")
        else:
            mdb_inventory = load_mdb_inventory_from_db(user_id)  # inventory already exists, load it

        if not sql_inventory_exists:
            sql_inventory = SqlInventory()
            if should_populate:
                UserFactory.populate_sql_inventory(name, sql_inventory)
            print(f"MySQL Inventory doesn't exist for {name}. Created a new inventory with ID: {sql_inventory.id}\n")
        else:
            sql_inventory = load_sql_inventory_from_db(user_id)

        return User(name, username, password, email, sql_inventory, mdb_inventory)

    @staticmethod
    def populate_sql_inventory(name: str, sql_inventory: SqlInventory):
        sql_inventory.create_item(f"{name}'s Chips", 20, 20, f"These are {name}'s Chips", 1.00)
        sql_inventory.create_item(f"{name}'s Candy", 20, 20, f"These are {name}'s Candy", 2.00)
        sql_inventory.create_item(f"{name}'s Chocolate", 20, 20, f"These are {name}'s Chocolate", 3.00)
        sql_inventory.create_item(f"{name}'s Gum", 20, 20, f"These are {name}'s Gum", 4.00)

    @staticmethod
    def populate_mdb_inventory(name: str, mdb_inventory: MdbInventory):
        mdb_inventory.create_item(f"{name}'s Sprite", 20, 20, f"These are {name}'s Sprite", 4.00)
        mdb_inventory.create_item(f"{name}'s Coke", 20, 20, f"These are {name}'s Coke", 4.00)
