from keras_adapter import KerasAdapter

def get_adapter_by_framework(framework):
	if 'keras' in framework:
		return KerasAdapter()
	return None