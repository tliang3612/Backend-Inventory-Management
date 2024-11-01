from backend.db.tabledef import ItemModel, InventoryModel, db_session
from backend.item import Item
from backend.inventory import Inventory


def load_inventories_from_db():
    with db_session() as s:
        db_inventories = s.query(InventoryModel).all()
        inventories = get_inventories(s, db_inventories)
        return inventories


def get_inventories(s, db_inventories) -> list[Inventory]:
    inventories = []
    # search through existing inventory databases
    for db_inventory in db_inventories:
        items_dict = get_items_dict(s, db_inventory)
        # create new inventory objects and populate it with
        inventory = Inventory(items_dict=items_dict, id=db_inventory.inventory_id)
        inventories.append(inventory)
    return inventories


def get_items_dict(s, db_inventory) ->dict[int, Item]:
    items_dict = {}

    db_items = s.query(ItemModel).filter(ItemModel.inventory_id == db_inventory.inventory_id).all()

    for db_item in db_items:
        item = Item(db_item.name, db_item.capacity, db_item.exp_date,
                    db_item.price, db_item.inventory_id, id=db_item.item_id)
        items_dict[item.id] = item
    return items_dict

