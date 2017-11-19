import os
from tinydb import TinyDB, Query
from tinydb.operations import set

DB_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'olympus_db.json')
TABLE = 'models'

db = TinyDB(DB_PATH)

Model = Query()

def get_all_models():
	return db.table(TABLE).all()

def create_new_model(model_object):
	db.table(TABLE).insert(model_object)

def does_model_exist(name, version):
	return db.table(TABLE).contains((Model.name == name) & (Model.version == version))

def update_model(name, version, updates):
	for update_key, update_val in updates.items():
		db.table(TABLE).update(
			set(update_key, update_val), 
			(Model.name == name) & (Model.version == version))

def get_model(name, version=1):
	if not does_model_exist(name, version):
		return None
	return db.table(TABLE).search((Model.name == name) & (Model.version == version))[0]

def delete_model_from_db(name, version=1):
	if does_model_exist(name, version):
		db.table(TABLE).remove((Model.name == name) & (Model.version == version))