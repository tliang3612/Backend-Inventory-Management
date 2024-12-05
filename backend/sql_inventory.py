from backend.base_inventory import BaseInventory, handle_invalid_item
from backend.db import sql_tabledef
from backend.db.sql_tabledef import sql_db_session
from backend.sql_item import SqlItem

class SqlInventory(BaseInventory):
    # do not put entry for id unless the id is a known inventory in the database
    def __init__(self, items_dict: dict[int, SqlItem] = None, id: int = -1):
        super().__init__(items_dict, id)

        # create new table entry
        if id == -1:
            with sql_db_session() as s:
                u = sql_tabledef.InventoryModel()
                s.add(u)
                s.commit()
                self.id = u.inventory_id
        else:
            self.id = id

    # mutators
    def create_item(self, name: str, capacity: int, quantity: int,  description: str, price: float):
        new_item = SqlItem(name, capacity, quantity, description, price, self.id)
        self.items_dict[new_item.id] = new_item

        return new_item








