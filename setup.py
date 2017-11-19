from setuptools import setup
from pip.req import parse_requirements
from pip.download import PipSession
import os

def read_requirements():
    '''parses requirements from requirements.txt'''
    reqs_path = os.path.join(__location__, 'requirements.txt')
    install_reqs = parse_requirements(reqs_path, session=PipSession())
    reqs = [str(ir.req) for ir in install_reqs]
    return reqs

setup(
  name = 'olympus',
  packages = ['olympus'],
  version = '0.2',
  description = 'A tool for creating a REST API for any machine learning model, in seconds.',
  author = 'Galiboo',
  author_email = 'hello@galiboo.com',
  url = 'https://github.com/galiboo/olympus', # use the URL to the github repo
  download_url = 'https://github.com/galiboo/olympus/archive/0.2.tar.gz', 
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
  install_requires=read_requirements()
)