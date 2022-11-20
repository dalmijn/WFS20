from wfs20.crs import CRS

from collections import defaultdict
from lxml import etree

WFS_NAMESPACE = 'http://www.opengis.net/wfs/2.0'
OWS_NAMESPACE = 'http://www.opengis.net/ows/1.1'
OGC_NAMESPACE = 'http://www.opengis.net/ogc'
GML_NAMESPACE = 'http://www.opengis.net/gml'
FES_NAMESPACE = 'http://www.opengis.net/fes/2.0'
XSI_NAMESPACE = 'http://www.w3.org/2001/XMLSchema-instance'

def _BuildServiceMeta(wfs,r):
	"""
	"""
	t = etree.fromstring(r.content)
	# Some indentifiers
	# ToDo
	# General Keywords
	wfs.Keywords = [item.text for item in t.findall(_ElementKey(OWS_NAMESPACE, "Keywords/Keyword"))]
	# Featuretypes (Layers) and Featuretype Meta
	wfs.FeatureTypeMeta = {}
	for elem in t.findall(_ElementKey(WFS_NAMESPACE, "FeatureTypeList/FeatureType")):
		tnm = FeatureTypeMeta(elem, None)
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

class FeatureTypeMeta:
	def __init__(self,elem,parent):
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
		self.MetaDataURL = elem.find(_ElementKey(WFS_NAMESPACE, "MetadataURL")).attrib["{http://www.w3.org/1999/xlink}href"]

class Feature:
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
		gml data parsed by lml.etree
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