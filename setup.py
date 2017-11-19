from setuptools import setup


setup(
  name = 'olympus',
  packages = ['olympus'],
  version = '0.3',
  description = 'A tool for creating a REST API for any machine learning model, in seconds.',
  author = 'Galiboo',
  author_email = 'hello@galiboo.com',
  url = 'https://github.com/galiboo/olympus', # use the URL to the github repo
  download_url = 'https://github.com/galiboo/olympus/archive/0.3.tar.gz', 
  py_modules=['olympus'],
  keywords = ['machine learning', 'python', 'rest', 'api', 'deep learning'],
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
  "tensorflow",
  "tinydb"]
)