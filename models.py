from db import get_all_models

import os, glob, numpy as np, tensorflow as tf

all_models = {
	
}

model_input_spec = {
	
}

tf_graph = None

def get_model_id(name, version):
	return "%s_v%d" % (name, version)

def load_all_models():
	from adapters.utils import get_adapter_by_framework
	global all_models, model_input_spec, tf_graph

	for model in get_all_models():

		# Skip deactivated models and prevent them from being loaded
		if not model['activated']:
			continue

		model_id = get_model_id(model['name'], model['version'])
		adapter = get_adapter_by_framework(model['adapter'])

		success, extras = adapter.validate_model_files(model['path'])
		
		if not success:
			# Skip this model if we can't load it.
			continue

		model = extras[1]

		all_models[model_id] = model

		# Generate an input spec for this model
		input_names_x_input_shapes = dict(
			zip(model.input_names, 
				[[-1 if i is None else i for i in t.shape.as_list()] for t in model.inputs]))
		input_names_x_input_types = dict(zip(model.input_names, [t.dtype.as_numpy_dtype for t in model.inputs]))

		assert input_names_x_input_shapes.keys() == input_names_x_input_types.keys()

		input_spec = {}

		for input_name in input_names_x_input_shapes:
			input_spec[input_name] = {
				'shape' : input_names_x_input_shapes[input_name],
				'dtype' : input_names_x_input_types[input_name]
			}

		# Save this model's input spec.
		model_input_spec[model_id] = input_spec

	# Load TF's default graph
	tf_graph = tf.get_default_graph()

def format_input(input, shape, dtype):
	return np.array(input, dtype=dtype).reshape(shape)

def get_predictions_for_model(name, version, input):
	global tf_graph

	def return_error(msg):
		return {'success' : False, 'message' : msg}

	model_id = get_model_id(name, version)

	if model_id not in all_models:
		return return_error("The requested model either does not exist or is deactivated.")

	num_inputs = len(input)

	if isinstance(input, list):
		if num_inputs == 1:
			input = input[0]
			try:
				input = format_input(input, model_input_spec[model_id].values()[0]['shape'], 
					model_input_spec[model_id].values()[0]['dtype'])
			except Exception as e:
				return return_error('Input error: ' + str(e))
		else:
			if num_inputs != len(model_input_spec[model_id]):
				return return_error("Received %d inputs but the model has %d inputs." % 
					(num_inputs, len(model_input_spec[model_id])))
			
			input_dict = {}
			for idx, input_name in enumerate(model_input_spec[model_id]):
				input_array = input[idx]
				try:
					input_array = format_input(input_array, 
						model_input_spec[model_id][input_name]['shape'],
						model_input_spec[model_id][input_name]['dtype'])
				except Exception as e:
					return return_error('Input error: ' + str(e))
				input_dict[input_name] = input_array
			input = input_dict

	elif isinstance(input, dict):
		if num_inputs == 1:
			try:
				input = format_input(input.values()[0], model_input_spec[model_id].values()[0]['shape'], 
					model_input_spec[model_id].values()[0]['dtype'])
			except Exception as e:
				return return_error('Input error: ' + str(e))
		else:
			if num_inputs != len(model_input_spec[model_id]):
				return return_error("Received %d inputs but the model has %d inputs." % 
					(num_inputs, len(model_input_spec[model_id])))
			input_dict = {}
			for input_name in model_input_spec[model_id]:
				
				try:
					input_array = input[input_name]
				except:
					return return_error("The following input was missing from the request: '%s'" % input_name)
				
				try:
					input_array = format_input(input_array, 
						model_input_spec[model_id][input_name]['shape'],
						model_input_spec[model_id][input_name]['dtype'])
				except Exception as e:
					return return_error('Input error: ' + str(e))
				input_dict[input_name] = input_array
			input = input_dict
	else:
		return return_error("Unexpected input type: %s" % type(input))

	with tf_graph.as_default():	
		preds = all_models[model_id].predict(input)

	output_dict = {}

	for idx, output_layer_name in enumerate(all_models[model_id].output_names):
		output_dict[output_layer_name] = preds[idx].tolist()

	return output_dict