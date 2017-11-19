#!/Users/subby/.virtualenvs/olympus/bin/python
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

    from prettytable import PrettyTable
    from storage import storage
    from database import db
    from adapters import Adapter
    from adapters.utils import get_adapter_by_framework
    from utils import generate_random_model_name, convert_dt_to_epoch
    from models import load_all_models
    from api import app

    import click, os, datetime

supported_frameworks = ['keras']
custom_adapters = []

def run_sanity_checks():
	storage.create_storage_dir(override=False)

@click.group()
def cli():
	run_sanity_checks()
	print '\n\n'

@cli.command()
@click.option('--host', default='localhost')
@click.option('--port', default=7878)
@click.option('--debug/--no-debug', default=True)
def up(host='localhost', port=7878, debug=True, log=True):
	""" Start the API model server. """
	start_server(host, port, debug, log)

@cli.command()
def list():
	""" List all deployed models. """
	models = db.get_all_models()
	if not models:
		print 'No models have been deployed yet.'
		return
	print 'Your models:\n'
	table = PrettyTable(['Name', 'Version', 'Last Deployed', 'Activated?'])
	for model in models:
		table.add_row([model['name'], model['version'], model['last_deployed'], model['activated']])
	print table


@cli.command()
@click.option('--name', default=lambda : generate_random_model_name(), prompt=True)	
@click.argument('path', type=click.Path(exists=True, resolve_path=True))
@click.option('--version', default=1, help='The version number of this model instance', prompt=True)
@click.option('--framework', default='keras', 
	help='The framework used to train & save the model',
	type=click.Choice(supported_frameworks), prompt=True)
def deploy(name, path, version=1, framework='keras'):
	""" Deploy a model. """
	global custom_adapters

	# Check for valid framework
	if framework not in supported_frameworks:
		print 'The specified framework must be one of: ' + ", ".join(supported_frameworks)
		return

	# Check if the model/version already exists
	if db.does_model_exist(name, version):
		# This model/version already exists. Alert user and abort
		print """
		Oops!

		A model with the same name/version already exists.

		To upload a new version of this model, either:

			(1) specify the version using the '--version' option, or
			(2) delete this model version and retry.

		"""
		return

	adapter = get_adapter_by_framework(framework, custom_adapters = custom_adapters)

	is_validation_ok, validation_extra = adapter.validate_model_files(path)

	if not is_validation_ok:
		print 'The given model path could not be successfully validated for the %s framework:' % framework
		print validation_extra
		return

	model = validation_extra[1]

	# Validation is OK, so copy the necessary model's files at this path to Olympus's internal model storage.
	adapter.copy_model_files_to_internal_storage(name, version)

	# Save the model to the database
	adapter.save_model_to_db(name = name, version = version, activated=True, 
		last_deployed = convert_dt_to_epoch(datetime.datetime.now()))

	print '\n\nYour "%s" model (version: %s) has been successfully deployed.' % (name, version)
	print 'You can now access it at the following endpoint:'
	print '\n\n\t\t/models/' + name + '/v' + str(version) + '/predict\n\n'

@cli.command()
@click.argument('name')
@click.option('--version', default=1)
@click.confirmation_option(help="Are you sure you want to expose this model via the API?")
def activate(name, version=1):
	""" Expose a model via the API model server. """
	if not db.does_model_exist(name, version):
		print 'The specified model/version doesn\'t exist!'
		return
	db.update_model(name, version, {'activated' : True})
	print 'Successfully activated the model\'s API.\nPlease restart Olympus for these changes to take effect.'

@cli.command()
@click.argument('name')
@click.option('--version', default=1)
@click.confirmation_option(help="Are you sure you want to hide this model from the API?")
def deactivate(name, version=1):
	""" Remove a model from the API model server. """
	if not db.does_model_exist(name, version):
		print 'The specified model/version doesn\'t exist!'
		return
	db.update_model(name, version, {'activated' : False})
	print 'Successfully deactivated the model\'s API.\nPlease restart Olympus for these changes to take effect.'

@cli.command()
@click.argument('name')
@click.option('--version', default=1)
@click.confirmation_option(help="Are you sure you want to delete this model version's instance?")
def delete(name, version=1):
	"""
	Delete a specific model version.
	"""
	if not db.does_model_exist(name, version):
		print 'The specified model/version doesn\'t exist!'
		return

	# delete the model from the db
	db.delete_model_from_db(name, version)

	# delete the model from the file storage
	storage.delete_model_storage(name, version)

	print 'The model (v%d) and its files were successfully deleted.' % version


# Olympus library extension methods
# TODO: Implement way to use the olympus library to deploy a model instance directly from code!
def add_adapter(adapter):
	global supported_frameworks, custom_adapters

	if adapter.name not in supported_frameworks:
		supported_frameworks.append(adapter.name)

	custom_adapters.append(adapter)

def start_server(host='localhost', port=7878, debug_server=True, log=True):
	if log:
		print 'Loading models from disk...\t',
	load_all_models(custom_adapters)
	if log:
		print 'OK.\n'
		print '\nStarting Olympus server at %s:%d\n' % (host, port)
	app.run(host=host, port=port, debug=debug_server)

if __name__ == '__main__':
	cli()