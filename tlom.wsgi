import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/tlom/")

from main import application

if __name__ == '__main__':
	application.run()
