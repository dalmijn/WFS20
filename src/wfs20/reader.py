"""DataReader object."""
import requests

from wfs20.request import get_response
from wfs20.util import build_response_meta


def read_service(
    url: str,
    timeout: int,
) -> "requests.models.Response":
    """Return a respone from the WFS service URL."""
    r = get_response(url, timeout=timeout)
    return r


class DataReader:
    """Response reader of a geospatial data request.

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

    def __init__(
        self,
        url: str,
        keyword: str,
        method: str = "GET",
        data: str = None,
    ):
        # General stuff
        self.url = url
        self.keyword = keyword
        self.request_method = method
        self.request_data = data

        # Declarations
        self.features = None
        self.layer_meta = None

        # substance
        build_response_meta(
            self,
            get_response(self.url, timeout=30, method=method, data=data),
            self.keyword,
        )

    def __repr__(self):
        return super().__repr__()

    def __iadd__(self, other):
        if isinstance(self, other.__class__):
            self.features += other.features
            self.layer_meta |= other.layer_meta
            return self
        else:
            raise TypeError(
                f"unsupported operand type(s) for +=: \
'{self.__class__}' and '{other.__class__}'"
            )
