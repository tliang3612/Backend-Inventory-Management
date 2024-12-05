from backend.base_inventory import BaseInventory, handle_invalid_item
from backend.db.mdb_tabledef import inventory_collection, item_collection
from backend.mdb_item import MdbItem

class MdbInventory(BaseInventory):
    def __init__(self, items_dict: dict[int, MdbItem] = None, id: int = None):
        super().__init__(items_dict, id)

        if id is None:
            max_id_inventory = inventory_collection.find_one(sort=[("inventory_id", -1)])  #find inventory with the highest id then increment
            self.id = (max_id_inventory["inventory_id"] + 1) if max_id_inventory else 1

            inventory_data = {"inventory_id": self.id, "items": []}
            inventory_collection.insert_one(inventory_data)
        else:
            self.id = id

    def create_item(self, name: str, capacity: int, quantity: int,  description: str, price: float):
        new_item = MdbItem(name, capacity, quantity, description, price, self.id)

        self.items_dict[new_item.id] = new_item

        inventory_collection.update_one(
            {"inventory_id": self.id},
            {"$push": {"items": new_item.id}}
        )

        return new_item
