from abc import abstractmethod

from helpers.error_handling import *

class BaseItem:
    def __init__(self, name: str, capacity: int, quantity: int, description: str, price: float, inventory_id: int, id: int = -1):
        if not isinstance(price, (int, float)) or price < 0:
            raise InvalidPriceException(price, name)

        if not isinstance(capacity, int) or capacity <= 0:
            raise InvalidQuantityException(capacity, name)

        if not isinstance(quantity, int) or quantity < 0 or quantity > capacity:
            raise InvalidQuantityException(quantity, name)

        self.name = name
        self.quantity = quantity
        self.capacity = capacity
        self.price = price
        self.description = description
        self.inventory_id = inventory_id
        self.id = id

    @abstractmethod
    def set_quantity(self, quantity: int):
        pass

    @abstractmethod
    def set_price(self, price: float):
        pass

    @abstractmethod
    def delete(self):
        pass

    def serialize(self):
        return {
            "item_id": self.id,
            "name": self.name,
            "quantity": self.quantity,
            "capacity": self.capacity,
            "description": self.description,
            "price": self.price,
            "inventory_id": self.inventory_id
        }

    def get_name(self) -> str:
        return self.name

    def get_id(self) -> int:
        return self.id

    def get_quantity(self) -> int:
        return self.quantity

    def get_price(self) -> float:
        return self.price

    def get_description(self) -> str:
        return self.description
