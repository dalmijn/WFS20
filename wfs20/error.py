class WFSError(Exception):
	def __init__(self,base,code,message):
		self.base = base
		self.code = code
		self.message = message
		super(WFSError,self).__init__(self.base)
	def __str__(self):
		return f"{self.base} => {self.message} (status_code: {self.code})"

class WFSInternalError(Exception):
	def __init__(self,base,message):
		self.base = base
		self.message = message
		super(WFSInternalError, self).__init__(self.base)
	def __str__(self):
		return f"{self.base} => {self.message}"

class AUTHError(Exception):
	def __init__(self,msg):
		self.base = "Wrong authentication credentials."
		self.msg = msg
		super(AUTHError,self).__init__(self.base)
	def __str__(self):
		return f"{self.base} => {self.msg}"

if __name__ == "__main__":
	raise AUTHError("bla")