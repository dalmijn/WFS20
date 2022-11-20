from wfs20.error import WFSError

import warnings
import importlib.util

try:
	from osgeo import ogr, osr
	_FieldTypes = {
	int:ogr.OFTInteger64,
	float:ogr.OFTReal,
	str:ogr.OFTString
	}
except ModuleNotFoundError:
	warnings.warn("osgeo package not installed. Writing to shapefile is not available.",ImportWarning)

def _WriteShapeFile(reader,out):
	"""
	"""
	if not importlib.util.find_spec("osgeo"):
		raise ModuleNotFoundError("Cannot execute function as osgeo is not installed.")
	Driver = ogr.GetDriverByName('ESRI Shapefile')

	srs = osr.SpatialReference()
	srs.ImportFromEPSG(28992)

	dst = Driver.CreateDataSource(f"{out}\\{reader.Keyword}.shp")
	Layer = dst.CreateLayer(reader.Keyword,srs)

	# Create Fields of Layer
	FieldTypes = reader.LayerMeta.FieldTypes
	LinkTable = reader.LayerMeta.LinkTable

	for header,t in FieldTypes.items():
		field = ogr.FieldDefn(
			LinkTable[header],
			_FieldTypes[t]
			)
		if t == str:
			field.SetWidth(100)
		Layer.CreateField(field)

	# Create and add Features to Layer
	for f in reader.Features:
		Feature = ogr.Feature(Layer.GetLayerDefn())
		Geometry = ogr.CreateGeometryFromGML(f.Geometry.decode())
		for header,v in f.Fields.items():
			Feature.SetField(
				LinkTable[header],
				v
				)
		Feature.SetGeometry(Geometry)
		Layer.CreateFeature(Feature)

	# Garbage collection by force
	FieldTypes = None
	LinkTable = None
	reader = None
	Feature = None
	Layer = None
	dst = None