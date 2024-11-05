from backend.db import tabledef
from backend.db.tabledef import db_session
from backend.item import Item
from helpers.error_handling import ItemNotFoundException


def handle_invalid_item(f):
    def decorator(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyError:
            raise ItemNotFoundException(args[1])
    return decorator


class Inventory:
    # do not put entry for id unless the id is a known inventory in the database
    def __init__(self, items_dict: dict[int, Item] = None, id: int = -1):

        if items_dict is None:
            self.items_dict = dict[int, Item]()
        else:
            self.items_dict = items_dict

        # create new table entry
        if id == -1:
            with db_session() as s:
                u = tabledef.InventoryModel()
                s.add(u)
                s.commit()
                self.id = u.inventory_id
        else:
            self.id = id

    # mutators
    def create_item(self, name: str, capacity: int, description: str, price: float):
        new_item = Item(name, capacity, description, price, self.id)
        self.items_dict[new_item.id] = new_item

        return new_item

    @handle_invalid_item
    def set_item_quantity(self, item_id: int, quantity: int):
        item = self.items_dict[item_id]
        if item is not None:
            item.set_quantity(quantity)
        return item

    @handle_invalid_item
    def delete_item(self, item_id: int):
        item = self.items_dict[item_id]
        if item is not None:
            self.items_dict.pop(item_id)
            item.delete()
        return item

    # converts the inventory dictionary to json format
    def serialize(self):
        inventory_json = {'items': [],'id':self.id}
        for item in self.items_dict.values():
            item_json = item.serialize()
            inventory_json['items'].append(item_json)
        return inventory_json

    @handle_invalid_item
    def get_item_price(self, item_id: int) -> float:
        return self.items_dict[item_id].get_price()

    @handle_invalid_item
    def get_item_quantity(self, item_id: int) -> int:
        return self.items_dict[item_id].get_quantity()

    @handle_invalid_item
    def get_item_name(self, item_id: int) -> str:
        return self.items_dict[item_id].get_name()

    @handle_invalid_item
    def get_item(self, item_id: int) -> Item:
        return self.items_dict[item_id]

    def get_item_description(self, item_id:int) -> Item:
        return self.items_dict[item_id].get






