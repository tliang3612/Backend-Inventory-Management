from typing_extensions import override

from backend.base_item import BaseItem
from helpers.error_handling import *
from backend.db import sql_tabledef
from backend.db.sql_tabledef import sql_db_session


class SqlItem(BaseItem):
    def __init__(self, name: str, capacity: int, quantity: int, description: str, price: float, inventory_id: int, id=-1):
        super().__init__(name, capacity, quantity, description, price, inventory_id, id)
        self.name = name
        self.quantity = quantity
        self.capacity = capacity
        self.price = price
        self.description = description
        self.inventory_id = inventory_id

        if id == -1:
            with sql_db_session() as s:

                existing_item = s.query(sql_tabledef.ItemModel).filter_by(name=name).first()
                if existing_item:
                    raise DuplicateItemException(name)

                u = sql_tabledef.ItemModel(name=self.name, quantity=self.quantity, capacity=self.capacity,
                                       description=self.description, price=self.price,
                                       inventory_id=self.inventory_id)
                s.add(u)
                s.commit()

                self.id = u.item_id
        else:
            self.id = id

    @override
    def set_quantity(self, quantity: int):
        if quantity < 0 or quantity > self.capacity:
            raise InvalidQuantityException(quantity, self.name)

        with sql_db_session() as s:
            model = sql_tabledef.ItemModel
            item = s.query(model).filter(model.item_id == self.id).first()
            setattr(item, 'quantity', quantity)
            s.commit()
        self.quantity = quantity
        return self

    @override
    def set_price(self, price: float):
        if price < 0:
            raise InvalidPriceException(price, self.name)

        with sql_db_session() as s:
            model = sql_tabledef.ItemModel
            item = s.query(model).filter(model.item_id == self.id).first()
            setattr(item, 'price', price)
            s.commit()

        self.price = price
        return self

    @override
    def delete(self):
        with sql_db_session() as s:
            model = sql_tabledef.ItemModel
            item = s.query(model).filter(model.item_id == self.id).first()
            s.delete(item)
            s.commit()
