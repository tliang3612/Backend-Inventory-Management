from abc import abstractmethod

from helpers.error_handling import ItemNotFoundException


def handle_invalid_item(f):
    def decorator(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyError:
            raise ItemNotFoundException(args[1])
    return decorator


class BaseInventory:
    def __init__(self, items_dict=None, id=None):
        if items_dict is None:
            self.items_dict = {}
        else:
            self.items_dict = items_dict

        self.id = id

    @abstractmethod
    def create_item(self, name: str, capacity: int, quantity: int,  description: str, price: float):
        pass

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

    def serialize(self):
        inventory_json = {"id": self.id, "items": []}
        for item in self.items_dict.values():
            item_json = item.serialize()
            inventory_json["items"].append(item_json)
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
    def get_item(self, item_id: int):
        return self.items_dict[item_id]

    @handle_invalid_item
    def get_item_description(self, item_id: int) -> str:
        return self.items_dict[item_id].get_description()
