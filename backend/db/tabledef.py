from contextlib import contextmanager
from datetime import timedelta
import secrets

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.session import Session

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///mydb.db' #using sqlite db
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30) #clears session after certain amount of time
app.config['SESSION_COOKIE_HTTPONLY'] = True # makes cookies accessible through http requests only
app.config['SESSION_COOKIE_SECURE'] = True # secures sending of cookies

db = SQLAlchemy(app)
CORS(app)

@contextmanager
def db_session():
    with app.app_context():
        s = Session(db)
        s.expire_on_commit = False
        try:
            yield s
            s.commit()
        except:
            s.rollback()
            raise
        finally:
            s.close()


class InventoryModel(db.Model):
    __tablename__ = "inventory"

    inventory_id = db.Column(db.Integer, primary_key=True)
    items = db.relationship("ItemModel", back_populates="inventory")


class ItemModel(db.Model):
    __tablename__ = "item"

    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column("name", db.String)
    quantity = db.Column("quantity", db.Integer)
    capacity = db.Column("capacity", db.Integer)
    description = db.Column("description", db.String)
    price = db.Column("price", db.Float)
    inventory_id = db.Column(db.Integer, db.ForeignKey("inventory.inventory_id"))
    inventory = db.relationship("InventoryModel", back_populates="items")


with app.app_context():
    db.create_all()
    db.session.commit()
