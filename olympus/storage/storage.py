import os, shutil


STORAGE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'model_storage/')

def create_storage_dir(override=False):
	if override or not os.path.exists(STORAGE_DIR):
		os.makedirs(STORAGE_DIR)
	return STORAGE_DIR

def get_model_dir(name, version=1, create_if_needed=False):
	path = os.path.join(STORAGE_DIR, name, 'v%d' % version)
	
	if create_if_needed:
		os.makedirs(path)

	return path

def delete_model_storage(name, version=1):
	model_dir = get_model_dir(name, version)
	
	if os.path.exists(model_dir):
		shutil.rmtree(model_dir)
		os.rmdir(os.path.dirname(model_dir))