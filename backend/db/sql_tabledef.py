from backend.db.flask_app import app
from contextlib import contextmanager

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.session import Session

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///mydb.db' #using sqlite db
sql_db = SQLAlchemy(app)
CORS(app)

@contextmanager
def sql_db_session():
    with app.app_context():
        s = Session(sql_db)
        s.expire_on_commit = False
        try:
            yield s
            s.commit()
        except:
            s.rollback()
            raise
        finally:
            s.close()


class InventoryModel(sql_db.Model):
    __tablename__ = "inventory"

    inventory_id = sql_db.Column(sql_db.Integer, primary_key=True)
    items = sql_db.relationship("ItemModel", back_populates="inventory")


class ItemModel(sql_db.Model):
    __tablename__ = "item"

    item_id = sql_db.Column(sql_db.Integer, primary_key=True)
    name = sql_db.Column("name", sql_db.String)
    quantity = sql_db.Column("quantity", sql_db.Integer)
    capacity = sql_db.Column("capacity", sql_db.Integer)
    description = sql_db.Column("description", sql_db.String)
    price = sql_db.Column("price", sql_db.Float)
    inventory_id = sql_db.Column(sql_db.Integer, sql_db.ForeignKey("inventory.inventory_id"))
    inventory = sql_db.relationship("InventoryModel", back_populates="items")


with app.app_context():
    sql_db.create_all()
    sql_db.session.commit()
