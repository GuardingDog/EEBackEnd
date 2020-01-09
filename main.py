# -*- coding: utf-8 -*-

import resource
import sys

if __name__ == '__main__':
	# reload(sys)
	# sys.setdefaultencoding('utf-8')
	app = resource.create_app()
	app.run(host="0.0.0.0")
