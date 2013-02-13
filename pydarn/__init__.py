# Main DaViT-py module __init__.py
"""
*******************************
            pydarn
*******************************
Module for everything SuperDARN

This includes the following submodules:
	* **sdio**: SuperDARN data I/O
	* **radar**:SuperDARN radars information
	* **plot**: plotting routines
	* **proc**: misc
	* **utils**: general utilities

*******************************
"""

try: import dmapio 
except Exception, e: 
	print e
	'problem importing dmapio'

try: import radar 
except Exception, e: 
	print e
	'problem importing radar'

try: import sdio 
except Exception, e: 
	print e
	'problem importing sdio'

try: import plot 
except Exception, e: 
	print e
	'problem importing plot'

try: import proc 
except Exception, e: 
	print e
	'problem importing proc'

from dmapio import *
from radar import *
from sdio import *
from plot import *
from proc import *
from datetime import *
from utils import *
from vtrad import *
import dmapio 
import radar 
import sdio 
import plot 
import proc 
import datetime 
import utils
