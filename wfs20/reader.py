from urllib.parse import parse_qsl, urlencode
from lxml import etree

class _ServiceReader:
	"""Service Reader"""
	def __init__(self,version):
		self._version = version
		pass
	def _UsableURL(self,url):
		par = []
		if url.find("?") != -1:
		    par = parse_qsl(url.split("?")[1])
		key = [item[0] for item in par]

		if "service" not in key:
			par += [("service",WFS)]
		if "request" not in key:
			par += [("request","GetCapabilities")]
		if "version" not in key:
			par += [("version",self._version)]
		
		urlpar = urlencode(par)
		return "?".join([url.split("?")[0],urlpar])
	def Read(self):
		pass

if __name__ == "__main__":
	aap = _ServiceReader("2.0.0")
	url = aap._UsableURL(r"https://service.pdok.nl/lv/bag/wfs/v2_0?request=getCapabilities&service=WFS")
	print(url)