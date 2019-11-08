import os

basedir = os.path.abspath(os.path.dirname(__file__))
# Ricky: these secret key should be put to the system env
class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'ricky'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '9321.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	ADMINS = ['rickyyuhaoqi@gmail.com']
