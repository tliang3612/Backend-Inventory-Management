from backend.db.flask_app import app
from flask_pymongo import PyMongo

app.config['MONGO_URI'] = 'mongodb://localhost:27017/inventory_db'

mdb = PyMongo(app)

db = mdb.db
item_collection = db['item']
inventory_collection = db['inventory']
