class Adapter(object):

	def choose_file_from_glob(self, files_glob):

		if len(files_glob) == 0:
			raise ValueError("There are no files to choose from!")

		file = files_glob[0]

		if len(files_glob) > 1:
			# Prompt user to select a single file.
			pass

		return file