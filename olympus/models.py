from database.db import get_all_models

import os, glob, numpy as np, tensorflow as tf

all_models = {
	
}

model_input_spec = {
	
}

model_adapters = {
	
}

def get_model_id(name, version):
	return "%s_v%d" % (name, version)

def load_all_models(custom_adapters):
	from adapters.utils import get_adapter_by_framework
	global all_models, model_input_spec, model_adapters

	for model in get_all_models():

		# Skip deactivated models and prevent them from being loaded
		if not model['activated']:
			continue

		model_id = get_model_id(model['name'], model['version'])
		adapter = get_adapter_by_framework(model['adapter'], custom_adapters)

		success, extras = adapter.validate_model_files(model['path'])
		
		if not success:
			# Skip this model if we can't load it.
			continue

		adapter.set_model_obj(model)

		ml_model = extras[1]

		all_models[model_id] = ml_model
		model_input_spec[model_id] = model['input_spec']
		model_adapters[model_id] = adapter


def get_predictions_for_model(name, version, input):
	global model_input_spec, model_adapters

	model_id = get_model_id(name, version)

	if model_id not in all_models:
		return {'success' : False, 'message' : "The requested model either does not exist or is deactivated."}

	# TODO: Also add a way to define and add custom adapters using the Olympus library, from the dev
	# application end.

	success, results_dict = model_adapters[model_id].parse_input(input)

	if not success:
		# There was a problem parsing the given inputs.
		return results_dict

	# Run model inference
	success, preds = model_adapters[model_id].run_inference(results_dict)

	if not success:
		return preds

	output_dict = model_adapters[model_id].prepare_output(preds)

	return output_dict