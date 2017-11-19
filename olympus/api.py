from flask import Flask, jsonify, request

from database.db import get_all_models, get_model
from models import get_predictions_for_model


app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'status' : 'OK'})

@app.route('/models/list')
def models_list():
	
	models = get_all_models()
	num_models = len(models)

	list_of_models = [{
		'name' : model['name'], 
		'version' : model['version'], 
		'last_deployed' : model['last_deployed'], 
		'api_activated' : model['activated'], 
		'backend_adapter' : model['adapter']} for model in models]

	return jsonify({'num_models' : num_models, 'models' : list_of_models})

@app.route('/models/<string:name>/v<int:version>/')
def model_detail(name, version=1):
	
	model = get_model(name, version)
	del model['path']

	if not model['activated']:
		return jsonify({'success':False, 'message' : 'The specified model is deactivated.'})

	return jsonify(model)

@app.route('/models/<string:name>/v<int:version>/predict', methods=['POST'])
def model_predict(name, version=1):	

	request.get_data()

	preds = get_predictions_for_model(name, version, request.json)

	return jsonify(preds)