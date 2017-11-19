from keras.models import load_model, model_from_yaml, model_from_json
from olympus.storage.storage import get_model_dir
from olympus.database.db import does_model_exist, create_new_model
from . import Adapter

from datetime import datetime

import os, glob, numpy as np, tensorflow as tf

class KerasAdapter(Adapter):

	def __init__(self):
		self.tf_graph = tf.get_default_graph()
		self.name = 'keras'

	def validate_model_files(self, path):
		"""
		Check if the file(s)/folder(s) at the given path are valid for this framework. 
		Returns (Success, Extras)
		"""
		self.path = path

		if os.path.isdir(self.path):
			# Check if there's an .hdf5 file in the directory.
			# If there is, check if it contains the whole model
			# If it only has the weights, check if there's a model definition JSON/YAML file
			# in the same directory.
			hdf5_files = []
			for ext in ('*.hdf5', '*.h5'):
				hdf5_files.extend(glob.glob(os.path.join(self.path, ext)))
			hdf5_files = list(set(hdf5_files)) # deduplicate

			if len(hdf5_files) == 0:
				return (False, "Could not locate any HDF5 files (.hdf5, .h5) in: %s" % self.path)

			model_file = self.choose_file_from_glob(hdf5_files)

			# Try loading the whole model with just the hdf5 file
			try:

				self.model = load_model(model_file)

			except:
				
				# This file only contains the weights, so check for a JSON/YAML file
				model_architecture_files = [glob.glob(os.path.join(self.path, ext)) for ext in ('*.json', '*.yaml', '*.yml')]
				model_architecture_files = list(set(model_architecture_files)) # deduplicate 

				if len(model_architecture_files) == 0:
					return (False, "There are no JSON nor YAML files describing "
						+ "your model's architecture in the given direcotry.")

				model_architecture_file = self.choose_file_from_glob(model_architecture_files)

				if '.json' in model_architecture_file:
					# This is a JSON file
					try:
						self.model = model_from_json(model_architecture_file)
					except:
						return (False, "The JSON model architecture file could not be loaded successfully.")
				else:
					# This is a YAML file
					try:
						self.model = model_from_yaml(model_architecture_file)
					except:
						return (False, "The YAML model architecture file could not be loaded successfully.")

				try:
					# Try to load the weights into this model
					self.model.load_weights(model_file)
				except:
					return (False, "The weights could not be loaded into the specified model successfully.")

		else:
			# This is a file, not a directory.

			# Try loading the whole model with just the hdf5 file
			model_file = self.path

			try:
				self.model = load_model(model_file)
			except Exception as e:
				return (False, "The model could not be loaded from the specified file.")

		# At this point, we have successfully loaded the user-specified model.
		return (True, (None, self.model))

	def parse_input(self, input):
		"""
		Override default input parsing method with one that's better suited for Keras.
		"""
		num_inputs = len(input)

		if isinstance(input, list):
			if num_inputs == 1:
				input = input[0]
				try:
					input = self.format_input(input, self.model_obj['input_spec'].values()[0]['shape'], 
						self.model_obj['input_spec'].values()[0]['dtype'])
				except Exception as e:
					return (False, self.return_error('Input error: ' + str(e)))
			else:
				if num_inputs != len(self.model_obj['input_spec']):
					return (False, self.return_error("Received %d inputs but the model has %d inputs." % 
						(num_inputs, len(self.model_obj['input_spec']))))
				
				input_dict = {}
				for idx, input_name in enumerate(self.model_obj['input_spec']):
					input_array = input[idx]
					try:
						input_array = self.format_input(input_array, 
							self.model_obj['input_spec'][input_name]['shape'],
							self.model_obj['input_spec'][input_name]['dtype'])
					except Exception as e:
						return (False, self.return_error('Input error: ' + str(e)))
					input_dict[input_name] = input_array
				input = input_dict

		elif isinstance(input, dict):
			if num_inputs == 1:
				try:
					input = self.format_input(input.values()[0], self.model_obj['input_spec'].values()[0]['shape'], 
						self.model_obj['input_spec'].values()[0]['dtype'])
				except Exception as e:
					return (False, self.return_error('Input error: ' + str(e)))
			else:
				if num_inputs != len(self.model_obj['input_spec']):
					return (False, self.return_error("Received %d inputs but the model has %d inputs." % 
						(num_inputs, len(self.model_obj['input_spec']))))
				input_dict = {}
				for input_name in self.model_obj['input_spec']:
					
					try:
						input_array = input[input_name]
					except:
						return (False, self.return_error("The following input was missing from the request: '%s'" % input_name))
					
					try:
						input_array = self.format_input(input_array, 
							self.model_obj['input_spec'][input_name]['shape'],
							self.model_obj['input_spec'][input_name]['dtype'])
					except Exception as e:
						return (False, self.return_error('Input error: ' + str(e)))

					input_dict[input_name] = input_array
				input = input_dict
		else:
			return (False, self.return_error("Unexpected input type: %s" % type(input)))

		return (True, input)

	def run_inference(self, inputs):

		try:
			preds = self.model.predict(inputs)
		except:
			try:
				with self.tf_graph.as_default():
					preds = self.model.predict(inputs)
			except Exception as e:
				return (False, {'success':False, 'msg': "Inference failed: " + str(e)})

		return (True, preds)

	def prepare_output(self, preds):
		output_dict = {}

		for idx, output_layer_name in enumerate(self.model.output_names):
			output_dict[output_layer_name] = preds[idx].tolist()

		return output_dict

	def save_model_to_db(self, name, version=1, activated=True, last_deployed=None):

		model = self.model
		
		model_obj = {
			'name' : name,
			'version' : version,
			'activated' : activated,
			'path' : get_model_dir(name, version),
			'adapter' : self.name # 'keras'
		}
		
		model_obj['last_deployed'] = last_deployed

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
				'dtype' : str(input_names_x_input_types[input_name]).replace("<type 'numpy.","").replace("'>","")
			}

		model_obj['input_spec'] = input_spec

		# Check if this model/version already exists in the db.
		# If it doesn't, store this model's metadata in the db.
		if not does_model_exist(name, version):
			create_new_model(model_obj)
		else:
			return (False, 'Model/version already exists.')

		return (True, None)