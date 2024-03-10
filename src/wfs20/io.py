"""I/O of WFS20."""
import importlib.util
import warnings
from pathlib import Path

from wfs20.error import WFSInternalError

GDAL_INSTALLED = False

_SUPPORTED_DRIVERS = {
    "ESRI Shapefile": ".shp",
    "GeoJSON": ".geojson",
    "GML": ".gml",
    "netCDF": ".nc",
}

try:
    from osgeo import ogr, osr

    _FieldTypes = {int: ogr.OFTInteger64, float: ogr.OFTReal, str: ogr.OFTString}
    GDAL_INSTALLED = True
except ModuleNotFoundError:
    warnings.warn(
        "osgeo package not installed. \
Writing to shapefile is not available.",
        ImportWarning,
    )


def _WriteGeometries(
    reader,
    driver: str,
    out: Path | str,
):
    """Write geometries to a file.

    Parameters
    ----------
    reader : DataReader
        A DataReader object containing geospatial data
    driver : str
        ogr driver (e.g. 'GeoJSON')
    out : Path | str
        output directory

    Raises
    ------
    ModuleNotFoundError
        _description_
    """
    if not importlib.util.find_spec("osgeo"):
        raise ModuleNotFoundError("Cannot execute function as osgeo is not installed.")
    if driver not in _SUPPORTED_DRIVERS:
        raise WFSInternalError(
            "Driver not found", f"'{driver}' not in list of available drivers for wfs20"
        )
    Driver = ogr.GetDriverByName(driver)
    _ext = _SUPPORTED_DRIVERS[driver]

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(28992)

    dst = Driver.CreateDataSource(str(Path(out, f"{reader.Keyword}{_ext}")))
    Layer = dst.CreateLayer(reader.Keyword, srs)

    # Create Fields of Layer
    FieldTypes = reader.LayerMeta.FieldTypes
    LinkTable = reader.LayerMeta.LinkTable

    for header, t in FieldTypes.items():
        field = ogr.FieldDefn(LinkTable[header], _FieldTypes[t])
        if t == str:
            field.SetWidth(100)
        Layer.CreateField(field)

    # Create and add Features to Layer
    for f in reader.Features:
        Feature = ogr.Feature(Layer.GetLayerDefn())
        Geometry = ogr.CreateGeometryFromGML(f.Geometry.decode())
        for header, v in f.Fields.items():
            Feature.SetField(LinkTable[header], v)
        Feature.SetGeometry(Geometry)
        Layer.CreateFeature(Feature)

    # Clearing memory
    FieldTypes = None
    LinkTable = None
    reader = None
    Feature = None
    Layer = None
    dst = None
