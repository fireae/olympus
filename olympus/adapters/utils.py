from keras_adapter import KerasAdapter

def get_adapter_by_framework(framework, custom_adapters=[]):
	
	# First, check if the frameworks are in any of the custom-defined adapters.
	for adapter in custom_adapters:
		if adapter.name == framework:
			return adapter

	# Now, check for the built-in adapters
	if 'keras' in framework:
		return KerasAdapter()

	return None