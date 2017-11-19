from setuptools import setup, find_packages


setup(
  name = 'olympus',
  version = '0.4',
  description = 'A tool for creating a REST API for any machine learning model, in seconds.',
  author = 'Galiboo',
  author_email = 'hello@galiboo.com',
  url = 'https://github.com/galiboo/olympus', # use the URL to the github repo
  download_url = 'https://github.com/galiboo/olympus/archive/0.4.tar.gz', 
  py_modules=['olympus'],
  keywords = ['machine learning', 'python', 'rest', 'api', 'deep learning'],
  packages=find_packages(),
  classifiers = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python'
  ],
  entry_points={
  'console_scripts': [
    'olympus = olympus.olympus:cli'
    ]
  },
  install_requires=[
  "click",
  "coolname",
  "Flask",
  "haikunator",
  "Keras",
  "numpy",
  "python-dateutil",
  "pytz",
  "scipy",
  "h5py",
  "tensorflow",
  "prettytable",
  "tinydb"]
)