from osgeo import ogr, osr

def _BuildCollection(out,features):
	driver = ogr.GetDriverByName('ESRI Shapefile')
	dst = driver.

	srs = osr.SpatialReference()
	srs.ImportFromEPSG(28992)
	pass