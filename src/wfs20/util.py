from wfs20.crs import CRS

from collections import defaultdict
from lxml import etree

WFS_NAMESPACE = 'http://www.opengis.net/wfs/2.0'
OWS_NAMESPACE = 'http://www.opengis.net/ows/1.1'
OGC_NAMESPACE = 'http://www.opengis.net/ogc'
GML_NAMESPACE = 'http://www.opengis.net/gml/3.2'
FES_NAMESPACE = 'http://www.opengis.net/fes/2.0'
XSI_NAMESPACE = 'http://www.w3.org/2001/XMLSchema-instance'

def _BuildServiceMeta(wfs,r):
	"""
	Method to build the metadata etc. of the service itself
	"""
	t = etree.fromstring(r.content)
	# Some indentifiers
	# ToDo
	# General Keywords
	wfs.Keywords = [item.text for item in t.findall(_ElementKey(OWS_NAMESPACE, "Keywords/Keyword"))]
	# Featuretypes (Layers) and Featuretype Meta
	wfs.FeatureTypeMeta = {}
	for elem in t.findall(_ElementKey(WFS_NAMESPACE, "FeatureTypeList/FeatureType")):
		tnm = FeatureTypeMeta(elem)
		wfs.FeatureTypeMeta[tnm.FeatureType] = tnm
	wfs.FeatureTypes = tuple(
		wfs.FeatureTypeMeta.keys()
		)
	# Service contraints
	wfs.Constraints = {}
	for elem in t.findall(_ElementKey(OWS_NAMESPACE, "OperationsMetadata/Constraint")):
		dv = elem.find(_ElementKey(OWS_NAMESPACE, "DefaultValue"))
		if dv is not None:
			wfs.Constraints[elem.attrib["name"]] = dv.text
		else:
			try:
				av = elem.findall(_ElementKey(OWS_NAMESPACE, "AllowedValues/Value"))
				wfs.Constraints[elem.attrib["name"]] = [
				v.text for v in av
				]
			except Exception:
				wfs.Constraints[elem.attrib["name"]] = None
	t = None

def _BuildResonseMeta(reader, r, keyword):
	"""
	Method to build the metadata etc. of the geospatial data request
	"""
	t = etree.fromstring(r.content)
	# Generate Local NameSpace
	_GetLocalNS(t.nsmap)
	# Some identifiers
	reader.gml = r.content
	# Get the requested feature xml's
	reader.Features = []
	for elem in t.iter(_ElementKey(LOC_NAMESPACE, keyword)):
		reader.Features.append(Feature(elem))
	# Get the Layer meta data
	reader.LayerMeta = LayerMeta(t,keyword)	
	t = None

def _GetLocalNS(nsmap):
	"""
	Local Namespace of the GetCapabilities and GetFeature Response
	"""
	global LOC_NAMESPACE
	nb = ["w3.org","opengis.net"]
	b_list = [all([item not in master for item in nb]) for master in list(nsmap.values())]
	try:
		LOC_NAMESPACE = list(nsmap.values())[b_list.index(True)]
	except ValueError:
		LOC_NAMESPACE = ""

def _ElementKey(ns,sub):
	"""
	Return key in xml format
	"""
	def ns_string(ns,s):
		return f"{{{ns}}}{s}"
	subs = sub.split("/")
	return "/".join(tuple(map(ns_string,[ns]*len(subs),subs)))

def _IsType(elem):
	val = elem.text
	try:
		s = eval(val)
	except Exception:
		s = val
	return type(s)

def _IsFieldType(lst):
	if float in lst:
		type = float
	else:
		type = int
	if str in lst:
		type = str
	return type

class _PostElement(etree.ElementBase):
	"""
	"""
	def __init__(self,ns,sub):
		# Supercharge the ElementBase class
		super(_PostElement,self).__init__(nsmap={"ns0":ns})
		self.tag = _ElementKey(ns, sub)
		self.set("service","WFS")
		self.set("version","2.0.0")
		self._query = etree.SubElement(self,_ElementKey(GML_NAMESPACE, "Query"))

	def FeatureType(self,featuretype):
		"""
		Set the featuretype
		"""
		self._query.set("typenames",featuretype)

	def BBOXPost(self,bbox,crs):
		"""
		Set the bbox for the post request
		"""
		# Nested part
		f_elem = etree.SubElement(self._query, _ElementKey(FES_NAMESPACE, "Filter")) 
		bb_elem = etree.SubElement(f_elem, _ElementKey(FES_NAMESPACE, "BBOX"))
		c_elem = etree.SubElement(bb_elem, _ElementKey(GML_NAMESPACE, "Envelope"))
		# Filling it in
		c_elem.set("srsName",crs.GetURNCode())
		# Setting the bounding box coordinates
		ll = etree.SubElement(c_elem, _ElementKey(GML_NAMESPACE, "LowerCorner"))
		ll.text = f"{bbox[0]} {bbox[1]}"
		ur = etree.SubElement(c_elem, _ElementKey(GML_NAMESPACE, "UpperCorner"))
		ur.text = f"{bbox[2]} {bbox[3]}"

	def StartIndex(si):
		"""
		Set the starting index of the request
		"""
		self.set("startindex",str(si))

	def ToString(self):
		"""
		Return the data in xml format for the post request
		"""
		return etree.tostring(self)

class FeatureTypeMeta:
	"""
	Create metadata of a featuretype

	Parameters
	----------
	elem: lxml.etree._Element
		Data corresponding to the featuretype in xml format
		parsed by lxml.etree

	Returns
	-------
	FeatureType metadata object
	"""
	def __init__(self,elem):
		# Identifiers
		self.FeatureType = elem.find(_ElementKey(WFS_NAMESPACE, "Name")).text
		self.Title = elem.find(_ElementKey(WFS_NAMESPACE, "Title")).text
		# Bounding Box
		self.BBOX84 = None
		bbox = elem.find(_ElementKey(OWS_NAMESPACE, "WGS84BoundingBox"))
		if bbox is not None:
			try:
				ll = bbox.find(_ElementKey(OWS_NAMESPACE, "LowerCorner"))
				ur = bbox.find(_ElementKey(OWS_NAMESPACE, "UpperCorner"))
				self.BBOX84 = tuple(
					[float(d) for d in ll.text.split()] 
					+ [float(d) for d in ur.text.split()]
					)
			except Exception:
				self.BBOX84 = None
		# CRS
		self.CRS = tuple(
			[CRS(elem.find(_ElementKey(WFS_NAMESPACE, "DefaultCRS")).text)]
			+ [CRS(item.text) for item in elem.findall(_ElementKey(WFS_NAMESPACE, "OtherCRS"))]
			)
		# Output Formats
		self.OutputFormats = tuple(
			[item.text for item in elem.findall(_ElementKey(WFS_NAMESPACE, "OutputFormats/Format"))]
			)
		# Metadata URL
		self.MetaDataURLs = []
		for url in elem.findall(_ElementKey(WFS_NAMESPACE, "MetadataURL")):
			self.MetaDataURLs.append(url.attrib["{http://www.w3.org/1999/xlink}href"])

class Feature:
	"""
	Holds data of individual features returned by the request
	for geospatial data

	Parameters
	----------
	elem: lxml.etree._Element
		Data corresponding to the feature

	Returns
	-------
	Feature Object
	"""
	def __init__(self,elem):
		self.Fields = {}
		for e in elem.findall(_ElementKey(LOC_NAMESPACE, "*")):
			if e.text and e.text.strip():
				self.Fields[e.tag.replace(f"{{{LOC_NAMESPACE}}}","")] = e.text
			if e.tag.replace(f"{{{LOC_NAMESPACE}}}","").lower() \
			in ("geom","geometry","geometrie","shape"):
				self.Geometry = etree.tostring(e[0])

	def __repr__(self):
		return super().__repr__()

class LayerMeta:
	"""
	Metadata for a shapefile layer based on gml data

	Parameters
	----------
	t: lxml.etree._Element
		gml data parsed by lxml.etree
	keyword: str
		string associated with feature dependent values
	"""
	def __init__(self,t,keyword):
		# Headers
		self.FieldHeaders = set(
			(item.tag.replace(f"{{{LOC_NAMESPACE}}}","") 
				for item in t.iter(_ElementKey(LOC_NAMESPACE, "*")) 
				if item.text and not item.text.strip() == "")
			)
		try:
			self.FieldHeaders.remove(keyword)
		except KeyError:
			pass
		finally:
			# self.FieldHeaders = list(self.FieldHeaders)
			pass
		# Field types 
		self.FieldTypes = {}
		for header in self.FieldHeaders:
			type_list = tuple(
				map(_IsType,t.iter(_ElementKey(LOC_NAMESPACE,header)))
				)
			self.FieldTypes[header] = _IsFieldType(type_list)
		type_list = None
		# Create Header link table (max len 10 for shapefile attribute table headers)
		self.LinkTable = {}
		count = dict(zip(
			[item[0:10] for item in self.FieldHeaders],
			[0]*len(self.FieldHeaders)
			))
		for item in self.FieldHeaders:
			ab = item[0:10]
			if count[ab] >= 1:
				n = ab[:-1] + f"{count[ab]}"
			else:
				n = ab
			self.LinkTable[item] = n
			count[ab] += 1

	def __repr__(self):
		return super().__repr__()

	def __eq__(self,other):
		if isinstance(self, other.__class__):
			return sorted(self.FieldHeaders) == sorted(other.FieldHeaders)
		else:
			return False

	def __or__(self,other):
		if isinstance(self, other.__class__):
			pass
		else:
			raise TypeError(f"unsupported operand type(s) for |: '{self.__class__}' and '{other.__class__}'")

	def __ior__(self,other):
		if isinstance(self, other.__class__):
			self.FieldHeaders |= other.FieldHeaders 
			dd = defaultdict(list)
			for d in (self.FieldTypes,other.FieldTypes):
				for k,v in d.items():
					dd[k].append(v)
			for k,v in dd.items():
				self.FieldTypes.update({k:_IsFieldType(v)})
			dd = None
			self.LinkTable |= other.LinkTable
			return self
		else:
			raise TypeError(f"unsupported operand type(s) for |=: '{self.__class__}' and '{other.__class__}'")

if __name__ == "__main__":
	from wfs20.request import CreatePostRequest, GetResponse
	crs = CRS.from_epsg(28992)
	base, data = CreatePostRequest(
		r"https://service.pdok.nl/lv/bag/wfs/v2_0?request=getCapabilities&service=WFS", 
		"2.0.0",
		"bag:pand",
		(110000,451000,111000,452000), 
		crs
		)
	r = GetResponse(base, 30, method="POST", data=data)
	class aap:
		pass
	_BuildResonseMeta(aap, r, "pand")
	print(aap.Features[0].Fields)