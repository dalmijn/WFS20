from wfs20.request import parse_qsl, GetResponse 
from wfs20.util import _BuildResonseMeta

def _ServiceReader(
	url: str,
	timeout: int,
) -> 'requests.models.Response':
	"""Method to return response data for WFS service url
	"""

	r = GetResponse(url,timeout=timeout)
	return r

class DataReader:
	def __init__(
		self,
		url: str,
		keyword: str,
		method: str="GET",
		data: str=None,
	):
		"""Response reader of a geospatial data request

		Parameters
		----------
		url : str
			request url for geospatial data
		keyword : str
			Designation of the requested layer
		method : str
			Request method, either 'GET' or 'POST'
		data : str
			Params in xml format

		Returns
		-------
		DataReader
		"""

		# General stuff
		self.URL = url
		self.Keyword = keyword
		self.RequestMethod = method
		self.RequestData = data

		# substance
		_BuildResonseMeta(self, GetResponse(self.URL, timeout=30, method=method, data=data), self.Keyword)

	def __repr__(self):
		return super().__repr__()

	def __iadd__(self, other):
		if isinstance(self, other.__class__):
			self.Features += other.Features
			self.LayerMeta |= other.LayerMeta
			return self
		else:
			raise TypeError(f"unsupported operand type(s) for +=: '{self.__class__}' and '{other.__class__}'")
		