import atexit
import os
import sys
import queue
import threading
import time
import weakref

atexit.register(_Destruction)

def _Destruction():
	pass

class WorkerItem:
	def __init__(self, oid, fn, *args, **kwargs):
		self.oid = oid
		self.fn = fn
		self.args
		self.kwargs

def Worker():
	while True:
		break

def Manager():
	while True:
		break
	pass

class ThreadPool:
	def __init__(self):
		self.
		self._callQueue = queue.SimpleQueue()
		pass
	# Context manager	
	def __enter__(self):
		pass
	def __exit__(self):
		pass

	def Run(self):
		pass
	def Clean(self):
		pass

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