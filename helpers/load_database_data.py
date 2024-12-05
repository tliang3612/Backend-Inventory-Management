from backend.db.sql_tabledef import ItemModel, InventoryModel, sql_db_session
from backend.db.mdb_tabledef import item_collection, inventory_collection
from backend.sql_item import SqlItem
from backend.sql_inventory import SqlInventory
from backend.mdb_inventory import MdbInventory
from backend.mdb_item import MdbItem

def load_sql_inventory_from_db(inventory_id) -> SqlInventory:
    with sql_db_session() as s:
        sql_inventory = s.query(InventoryModel).filter(InventoryModel.inventory_id == inventory_id).first()
        sql_items_dict = get_sql_items_dict(s, sql_inventory)
        loaded_inventory = SqlInventory(items_dict=sql_items_dict, id=sql_inventory.inventory_id)
        return loaded_inventory

def load_mdb_inventory_from_db(inventory_id) -> MdbInventory:
    mdb_inventory = inventory_collection.find_one({"inventory_id": inventory_id})
    mdb_items_dict = get_mdb_items_dict(mdb_inventory)
    loaded_inventory = MdbInventory(items_dict=mdb_items_dict, id=mdb_inventory["inventory_id"])
    return loaded_inventory

def get_sql_items_dict(s, db_inventory) ->dict[int, SqlItem]:
    items_dict = {}

    db_items = s.query(ItemModel).filter(ItemModel.inventory_id == db_inventory.inventory_id).all()

    for db_item in db_items:
        item = SqlItem(db_item.name, db_item.capacity, db_item.quantity, db_item.description,
                       db_item.price, db_item.inventory_id, id=db_item.item_id)
        items_dict[item.id] = item
    return items_dict

def get_mdb_items_dict(db_inventory) -> dict[int, MdbItem]:
    items_dict = {}

    # Query for items belonging to the specific inventory_id
    db_items = item_collection.find({"inventory_id": db_inventory["inventory_id"]})

    for db_item in db_items:
        # Create MdbItem instances for each item
        item = MdbItem(db_item["name"], db_item["capacity"], db_item["quantity"], db_item["description"],
            db_item["price"], db_item["inventory_id"], id=db_item["item_id"]
        )
        items_dict[item.id] = item

    return items_dict
def check_inventory_exists(db_type, inventory_id) -> bool:
    if inventory_id is None:
        return False

    if db_type == 'sql':
        with sql_db_session() as s:
            sql_db_exists = s.query(InventoryModel).filter(InventoryModel.inventory_id == inventory_id).first() is not None
        return sql_db_exists
    elif db_type == 'mdb':
        mdb_exists = inventory_collection.find_one({"inventory_id": int(inventory_id)}) is not None
        return mdb_exists

    return False





# def load_inventories_from_db():
#     with sql_db_session() as s:
#         db_inventories = s.query(InventoryModel).all()
#         inventories = get_sql_inventories(s, db_inventories)
#         return inventories

# def get_sql_inventories(s, db_inventories) -> list[Inventory]:
#     inventories = []
#     # search through existing inventory databases
#     for db_inventory in db_inventories:
#         items_dict = get_sql_items_dict(s, db_inventory)
#         # create new inventory objects and populate it with
#         inventory = Inventory(items_dict=items_dict, id=db_inventory.inventory_id)
#         inventories.append(inventory)
#     return inventories