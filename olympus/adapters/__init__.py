import numpy as np, os, shutil
from distutils.dir_util import copy_tree
from olympus.storage.storage import get_model_dir

class Adapter(object):

	def __init__(self, name):
		self.name = name

	def choose_file_from_glob(self, files_glob):

		if len(files_glob) == 0:
			raise ValueError("There are no files to choose from!")

		file = files_glob[0]

		if len(files_glob) > 1:
			# Prompt user to select a single file.
			pass

		return file

	def copy_model_files_to_internal_storage(self, name, version=1):
		
		model_dir = get_model_dir(name, version, create_if_needed=True)

		if os.path.isdir(self.path):
			# Copy the original model directory into its corresponding internal model storage folder
			copy_tree(self.path, model_dir)
		else:
			# Copy the model file to its corresponding internal model storage folder
			shutil.copy2(self.path, model_dir)

	def format_input(self, input, shape, dtype):
		return np.array(input, dtype=dtype).reshape(shape)

	def return_error(self, msg):
		return {'success' : False, 'message' : msg}

	def set_model_obj(self, model_obj_json):
		self.model_obj = model_obj_json

	def parse_input(self, input):
		"""
		Default input parsing method for models.
		It's highly recommended to implement your own input parsing function for your custom models.
		"""
		
		input_spec = self.model_obj['input_spec']

		num_inputs = len(input_spec)

		assert len(input) == num_inputs

		if isinstance(input, list):
			input = dict(zip(self.model.input_names, input))

		input_dict = {}

		for input_name in input_spec:
			shape = input_spec[input_name]['shape']
			dtype = input_spec[input_name]['dtype']
			input_dict[input_name] = self.format_input(input[input_name], shape, dtype)

		return input_dict

	def prepare_output(self, preds):
		# By default, just return the raw preds.
		return {'predictions' : preds.tolist()}