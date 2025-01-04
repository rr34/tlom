import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/tlom")

activate_this = '/var/www/tlom/py3123_venv/bin/activate'
with open(activate_this) as file_:
	exec(file.read(), dict(__file__=activate_this))

from main import application

if __name__ == '__main__':
	application.run()
