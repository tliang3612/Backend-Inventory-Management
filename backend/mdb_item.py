from typing_extensions import override
from backend.base_item import BaseItem
from backend.db.mdb_tabledef import item_collection, inventory_collection
from helpers.error_handling import *


class MdbItem(BaseItem):
    def __init__(self, name: str, capacity: int, quantity: int, description: str, price: float, inventory_id: int, id: int = -1):
        super().__init__(name, capacity, quantity, description, price, inventory_id, id)

        self.name = name
        self.quantity = quantity
        self.capacity = capacity
        self.description = description
        self.price = price
        self.inventory_id = inventory_id

        if id == -1:
            max_id_item = item_collection.find_one(sort=[("item_id", -1)])  # Find the item with the highest ID
            self.id = (max_id_item["item_id"] + 1) if max_id_item else 1

            #check for duplicate
            existing_item = item_collection.find_one({"name": name})
            if existing_item:
                raise DuplicateItemException(name)

            item_data = {
                "item_id": self.id,
                "name": self.name,
                "quantity": self.quantity,
                "capacity": self.capacity,
                "description": self.description,
                "price": self.price,
                "inventory_id": self.inventory_id,
            }
            item_collection.insert_one(item_data)
        else:
            self.id = id

    @override
    def set_quantity(self, quantity: int):
        if quantity < 0:
            raise InvalidQuantityException(quantity, self.name)

        item_collection.update_one(
            {"item_id": self.id},
            {"$set": {"quantity": quantity}}
        )
        self.quantity = quantity
        return self

    @override
    def set_price(self, price: float):
        if price < 0:
            raise InvalidPriceException(price, self.name)

        item_collection.update_one(
            {"item_id": self.id},
            {"$set": {"price": price}}
        )
        self.price = price
        return self

    @override
    def delete(self):
        item_collection.delete_one({"item_id": self.id})