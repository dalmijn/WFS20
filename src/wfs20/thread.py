from wfs20.reader import DataReader
from wfs20.request import CreateGetRequest

import os
import sys
import queue
import time
import concurrent.futures

def aap():
	sys.stdout.write(f"non\n")
	time.sleep(20)

def looped_request():
	core_count = os.cpu_count()
	sys.stdout.write(f"{core_count}\n")
	with concurrent.futures.ThreadPoolExecutor(max_workers=core_count) as t:
		while True:
			t.submit(aap)
	pass

def dumbass_looping():
	for item in [1,2,3,4,5]:
		sys.stdout.write(f"{item}\n")
	pass

if __name__ == "__main__":
	looped_request()
	pass