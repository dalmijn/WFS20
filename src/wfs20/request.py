from wfs20.error import WFSError

import sys
import requests
from lxml import etree
from urllib.parse import parse_qsl, urlencode

def _BaseRequestURL(url):
	"""
	Separate the url in a base-url and parameters
	"""
	par = []
	if url.find("?") != -1:
		par = parse_qsl(url.split("?")[1])
	return url.split("?")[0],par

def _ServiceURL(url,version):
	"""
	Ensure a suitable url for the service GetCapabilities request
	"""
	base,par = _BaseRequestURL(url)
	key = [item[0] for item in par]
	if "service" not in key:
		par += [("service","WFS")]
	if "request" not in key:
		par += [("request","GetCapabilities")]
	if "version" not in key:
		par += [("version",version)]
	urlpar = urlencode(par)
	return "?".join([url.split("?")[0],urlpar])

def GetResponse(url,timeout):
	"""
	Get the response from a url to be requested

	Parameters
	----------
	url: str
		url to be requested
	timeout: int
		Allowed timeout after which an Exception is raised

	Returns
	-------
	Response
	"""
	params = {}
	params["timeout"] = timeout

	r = requests.request("GET",url,**params)

	if r.status_code in range(400,451,1):
		raise WFSError("Client Error", r.status_code, r.text)
	elif r.status_code in range(500,511,1):
		raise WFSError("Server Error", r.status_code, r.text)

	if "Content-Type" in r.headers and \
			r.headers['Content-Type'] in ['text/xml', 'application/xml', 'application/vnd.ogc.se_xml']:
		wfse = etree.fromstring(r.content)
		exceptions = [
            '{http://www.opengis.net/ows}Exception',
            '{http://www.opengis.net/ows/1.1}Exception',
            '{http://www.opengis.net/ogc}ServiceException',
            'ServiceException'
        ]

		if any(map(wfse.find,exceptions)):
			raise WFSError("WFS Error", r.status_code, r.text)

	# sys.stdout.write(f"Status Code: {r.status_code}\n")

	return r

def BBOXGet(bbox,crs):
	"""
	Translate a list or tuple of coordinates to request material

	Parameters
	----------
	bbox: list of tuple
	crs: wfs20.crs.CRS
	"""
	if crs.encoding == "urn":
		if crs.order == "xy":
			return "{},{},{},{},{}".format(
				*bbox,
				crs.GetURNCode()
				)
		else:
			return "{},{},{},{},{}".format(
				bbox[1],
				bbox[0],
				bbox[3],
				bbox[2],
				crs.GetURNCode()
				)
	else:
		return "{},{},{},{},{}".format(
			*bbox,
			crs.GetURICode1()
			)

def CreateGetRequest(
	url,
	version,
	featuretype,
	bbox,
	crs,
	startindex=None
	):
	"""
	Create a geospatial data request-url

	Parameters
	----------
	url: str
		Service url
	version: str
		Service version
	featuretype: str
		Layer to be requested, mostly in the format of 'xxx:xxx'
	bbox: list or tuple
		Bounding box wherein the spatial data lies that is requested,
		e.g. (x1,y1,x2,y2)
	crs: wfs20.crs.CRS
		Object containing projection information
	startindex: int
		Starting index of the feature count

	Returns
	-------
	url: str
		request url
	"""
	base,_ = _BaseRequestURL(url)
	params = {
		"service":"WFS","version":f"{version}",
		"request":"GetFeature"
		}
	params["typenames"] = [featuretype] 
	params["bbox"] = BBOXGet(bbox, crs)
	if startindex is not None:
		params["startindex"] = startindex
	p = urlencode(params,doseq=True)
	return f"{base}?{p}"

# ToDo: Fix post requests for this library
def CreatePostRequest():
	"""
	"""
	return "This now does nothing, thanks for trying out"

