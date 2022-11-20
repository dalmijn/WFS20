from wfs20.request import parse_qsl, GetResponse 
from wfs20.util import _BuildResonseMeta

def _ServiceReader(url,timeout):
	"""
	Service Reader
	"""
	r = GetResponse(url,timeout=timeout)
	return r

class DataReader:
	"""
	Response Reader
	"""
	def __init__(
		self,
		url,
		):

		# General stuff
		self.DataURL = url
		self.Keyword = dict(parse_qsl(self.DataURL))["typenames"].split(":")[1]

		# substance
		_BuildResonseMeta(self, GetResponse(self.DataURL, timeout=30), self.Keyword)

	def __repr__(self):
		return super().__repr__()

	def __iadd__(self,other):
		if isinstance(self, other.__class__):
			self.Features += other.Features
			self.LayerMeta |= other.LayerMeta
		else:
			raise TypeError(f"unsupported operand type(s) for +=: '{self.__class__}' and '{other.__class__}'")