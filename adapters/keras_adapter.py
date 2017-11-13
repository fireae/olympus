from keras.models import load_model, model_from_yaml, model_from_json
from storage import get_model_dir
from db import does_model_exist, create_new_model
from models import format_input, model_input_spec
from . import Adapter

from distutils.dir_util import copy_tree
from datetime import datetime

import os, glob, shutil, numpy as np

class KerasAdapter(Adapter):

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
			except:
				return (False, "The model could not be loaded from the specified file.")

		# At this point, we have successfully loaded the user-specified model.
		return (True, (None, self.model))

	def copy_model_files_to_internal_storage(self, name, version=1):
		
		model_dir = get_model_dir(name, version, create_if_needed=True)

		if os.path.isdir(self.path):
			# Copy the original model directory into its corresponding internal model storage folder
			copy_tree(self.path, model_dir)
		else:
			# Copy the model file to its corresponding internal model storage folder
			shutil.copy2(self.path, model_dir)

	def prepare_input_for_model(self, name, version=1, input=[]):
		model_id = get_model_id(name, version)

		input_spec = model_input_spec[model_id]

		num_inputs = len(input_spec)

		assert len(input) == num_inputs

		if isinstance(input, list):
			input = dict(zip(self.model.input_names, input))

		input_dict = {}

		for input_name in input_spec:
			shape = input_spec[input_name]['shape']
			dtype = input_spec[input_name]['dtype']
			input_dict[input_name] = format_input(input[input_name], shape, dtype)

		return input_dict

	def save_model_to_db(self, name, version=1, activated=True, last_deployed=None):
		
		model_obj = {
			'name' : name,
			'version' : version,
			'activated' : activated,
			'path' : get_model_dir(name, version),
			'adapter' : 'keras_adapter'
		}
		
		model_obj['last_deployed'] = last_deployed

		# Check if this model/version already exists in the db.
		# If it doesn't, store this model's metadata in the db.
		if not does_model_exist(name, version):
			create_new_model(model_obj)
		else:
			return (False, 'Model/version already exists.')

		return (True, None)