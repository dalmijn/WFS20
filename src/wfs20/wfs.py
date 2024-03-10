"""Main submodule of WFS20."""

from wfs20.crs import CRS
from wfs20.error import WFSInternalError
from wfs20.io import _WriteGeometries
from wfs20.reader import DataReader, read_service
from wfs20.request import create_get_request, service_url
from wfs20.util import build_service_meta


class WebFeatureService:
    """WebFeatureService.

    Parameters
    ----------
    url : str
        Service url
    version : str
        WebFeatureService version

    Returns
    -------
    wfs20.WebFeatureService
        Object containing the metadata of the service
    """

    def __init__(self, url: str, version: str = "2.0.0") -> "WebFeatureService":
        # Basic object variables
        self.url = url
        self.version = version
        self.service_url = service_url(self.url, version)

        # Declarations
        self.data_reader = None

        # Substance
        build_service_meta(self, read_service(self.service_url, timeout=30))

    def __repr__(self):
        return f"<wfs20.WebFeatureService object ({self.url})>"

    def get_data(
        self,
        featuretype: str,
        bbox: tuple,
        epsg: int,
    ):
        """Request spatial data from the WebFeatureService.

        Parameters
        ----------
        featuretype : str
            Layer to be requested, mostly in the format of 'xxx:xxx'
        bbox : tuple
            Bounding box wherein the spatial data lies that is requested,
            e.g. (x1,y1,x2,y2)
        epsg : int
            The projection code of the requested data and the bounding box
            according to EPSG, e.g. 4326 (WGS84)

        Returns
        -------
        wfs20.reader.DataReader
            Contains the requested data
        """
        if featuretype not in self.feature_types:
            raise WFSInternalError(
                "Request Error",
                f"<{featuretype}> not in list of available featuretypes \
(see <class>.FeatureTypes)",
            )
        crs = CRS.from_epsg(epsg)
        if crs not in self.feature_type_meta[featuretype].crs:
            raise WFSInternalError(
                "Request Error",
                f"<{epsg}> not in list of available projections \
(see <class>.FeatureTypeMeta[<id>].CRS)",
            )
        url = create_get_request(self.url, self.version, featuretype, bbox, crs)
        keyword = self.feature_type_meta[featuretype].title
        self.data_reader = DataReader(url, keyword)
        return self.data_reader

    def to_file(
        self,
        out: str,
        driver: str = "GeoJSON",
    ):
        """Write geospatial data held in reader to file.

        Parameters
        ----------
        out : str
            path of where the file should be written to
        driver : str
            ogr driver for writing the geometries
            E.g. 'GeoJSON' if one wants to write the data
            in the geojson format
        """
        if self.data_reader is None or not self.data_reader.features:
            raise WFSInternalError(
                "Writing to file", "No features collected from WebFeatureService"
            )
        _WriteGeometries(self.data_reader, driver, out)
