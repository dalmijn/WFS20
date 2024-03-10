"""Utility."""
from collections import defaultdict

from lxml import etree

from wfs20.crs import CRS

WFS_NAMESPACE = "http://www.opengis.net/wfs/2.0"
OWS_NAMESPACE = "http://www.opengis.net/ows/1.1"
OGC_NAMESPACE = "http://www.opengis.net/ogc"
GML_NAMESPACE = "http://www.opengis.net/gml/3.2"
FES_NAMESPACE = "http://www.opengis.net/fes/2.0"
XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
XLI_NAMESPACE = "http://www.w3.org/1999/xlink"


def build_service_meta(wfs, r):
    """Build the metadata of the service itself."""
    t = etree.fromstring(r.content)
    # General Keywords
    wfs.keywords = [
        item.text
        for item in t.findall(
            element_key(OWS_NAMESPACE, "ServiceIdentification/Keywords/Keyword")
        )
    ]
    # Some service meta like allowed wfs versions etc
    for elem in t.findall(element_key(OWS_NAMESPACE, "OperationsMetadata/Operation")):
        if elem.attrib["name"] == "GetCapabilities":
            wfs.get_capabilities_meta = CapabilitiesMeta(elem)
        elif elem.attrib["name"] == "GetFeature":
            wfs.get_feature_meta = FeatureMeta(elem)
    # Featuretypes (Layers) and Featuretype Meta
    wfs.feature_type_meta = {}
    for elem in t.findall(element_key(WFS_NAMESPACE, "FeatureTypeList/FeatureType")):
        tnm = FeatureTypeMeta(elem)
        wfs.feature_type_meta[tnm.feature_type] = tnm
    wfs.feature_types = tuple(wfs.feature_type_meta.keys())
    # Service contraints
    wfs.constraints = {}
    for elem in t.findall(element_key(OWS_NAMESPACE, "OperationsMetadata/Constraint")):
        dv = elem.find(element_key(OWS_NAMESPACE, "DefaultValue"))
        if dv is not None:
            wfs.constraints[elem.attrib["name"]] = dv.text
        else:
            try:
                av = elem.findall(element_key(OWS_NAMESPACE, "AllowedValues/Value"))
                wfs.constraints[elem.attrib["name"]] = [v.text for v in av]
            except Exception:
                wfs.constraints[elem.attrib["name"]] = None
    t = None


def build_content_meta(obj, elem):
    """Build the content metadata."""
    elem.attrib["name"]
    # Links in the Operation content meta
    obj.request_methods = {}
    for e in elem.findall(element_key(OWS_NAMESPACE, "DCP/HTTP/*")):
        key = e.tag.replace(f"{{{OWS_NAMESPACE}}}", "")
        obj.request_methods.update(
            {key.upper(): e.attrib[element_key(XLI_NAMESPACE, "href")]}
        )
    # Parameters in the Operation content meta
    for e in elem.findall(element_key(OWS_NAMESPACE, "Parameter")):
        key = e.attrib["name"]
        setattr(
            obj,
            key,
            tuple(
                [
                    item.text
                    for item in e.findall(
                        element_key(OWS_NAMESPACE, "AllowedValues/Value")
                    )
                ],
            ),
        )


def build_response_meta(reader, r, keyword):
    """Build the metadata of geospatial data request."""
    t = etree.fromstring(r.content)
    # Generate Local NameSpace
    get_localns(t.nsmap)
    # Some identifiers
    reader.gml = r.content
    # Get the requested feature xml's
    reader.features = []
    for elem in t.iter(element_key(LOC_NAMESPACE, keyword)):
        reader.features.append(Feature(elem))
    # Get the Layer meta data
    reader.layer_meta = LayerMeta(t, keyword)
    t = None


def get_localns(nsmap):
    """Local Namespace of the GetCapabilities and GetFeature Response."""
    global LOC_NAMESPACE
    nb = ["w3.org", "opengis.net"]
    b_list = [
        all([item not in master for item in nb]) for master in list(nsmap.values())
    ]
    try:
        LOC_NAMESPACE = list(nsmap.values())[b_list.index(True)]
    except ValueError:
        LOC_NAMESPACE = ""


def element_key(ns, sub):
    """Return key in xml format."""

    def ns_string(ns, s):
        return f"{{{ns}}}{s}"

    subs = sub.split("/")
    return "/".join(tuple(map(ns_string, [ns] * len(subs), subs)))


def is_type(elem):
    """Get the underlying type of the string content."""
    val = elem.text
    try:
        s = eval(val)
    except Exception:
        s = val
    return type(s)


def is_field_type(lst):
    """Get the type for a field."""
    if float in lst:
        type = float
    else:
        type = int
    if str in lst:
        type = str
    return type


class PostElement(etree.ElementBase):
    """lxml.etree.Element to create post request data.

    _extended_summary_

    Parameters
    ----------
    etree : _type_
        _description_
    """

    def __init__(self, ns, sub):
        # Supercharge the ElementBase class
        super(PostElement, self).__init__(nsmap={"ns0": ns})
        self.tag = element_key(ns, sub)
        self.set("service", "WFS")
        self.set("version", "2.0.0")
        self._query = etree.SubElement(self, element_key(GML_NAMESPACE, "Query"))

    def feature_type(self, featuretype):
        """Set the featuretype."""
        self._query.set("typenames", featuretype)

    def bbox_post(self, bbox, crs):
        """Set the bbox for the post request."""
        # Nested part
        f_elem = etree.SubElement(self._query, element_key(FES_NAMESPACE, "Filter"))
        bb_elem = etree.SubElement(f_elem, element_key(FES_NAMESPACE, "BBOX"))
        c_elem = etree.SubElement(bb_elem, element_key(GML_NAMESPACE, "Envelope"))
        # Filling it in
        c_elem.set("srsName", crs.GetURNCode())
        # Setting the bounding box coordinates
        ll = etree.SubElement(c_elem, element_key(GML_NAMESPACE, "LowerCorner"))
        ll.text = f"{bbox[0]} {bbox[1]}"
        ur = etree.SubElement(c_elem, element_key(GML_NAMESPACE, "UpperCorner"))
        ur.text = f"{bbox[2]} {bbox[3]}"

    def start_index(self, si):
        """Set the starting index of the request."""
        self.set("startindex", str(si))

    def to_string(self):
        """Return the data in xml format for the post request."""
        return etree.tostring(self)


class CapabilitiesMeta:
    """_summary_.

    _extended_summary_
    """

    def __init__(self, elem):
        build_content_meta(self, elem)

    def __repr__(self):
        return super().__repr__()


class FeatureMeta:
    """_summary_.

    _extended_summary_
    """

    def __init__(self, elem):
        build_content_meta(self, elem)

    def __repr__(self):
        return super().__repr__()


class FeatureTypeMeta:
    """Create metadata of a featuretype.

    Parameters
    ----------
    elem : lxml.etree._Element
        Data corresponding to the featuretype in xml format
        parsed by lxml.etree

    Returns
    -------
    FeatureType metadata object
    """

    def __init__(self, elem):
        # Identifiers
        self.feature_type = elem.find(element_key(WFS_NAMESPACE, "Name")).text
        self.title = elem.find(element_key(WFS_NAMESPACE, "Title")).text
        self.abstract = elem.find(element_key(WFS_NAMESPACE, "Abstract")).text
        # Bounding Box
        self.bbox84 = None
        bbox = elem.find(element_key(OWS_NAMESPACE, "WGS84BoundingBox"))
        if bbox is not None:
            try:
                ll = bbox.find(element_key(OWS_NAMESPACE, "LowerCorner"))
                ur = bbox.find(element_key(OWS_NAMESPACE, "UpperCorner"))
                self.bbox84 = tuple(
                    [float(d) for d in ll.text.split()]
                    + [float(d) for d in ur.text.split()]
                )
            except Exception:
                self.bbox84 = None
        # CRS
        self.crs = tuple(
            [CRS(elem.find(element_key(WFS_NAMESPACE, "DefaultCRS")).text)]
            + [
                CRS(item.text)
                for item in elem.findall(element_key(WFS_NAMESPACE, "OtherCRS"))
            ]
        )
        # Output Formats
        self.output_formats = tuple(
            [
                item.text
                for item in elem.findall(
                    element_key(WFS_NAMESPACE, "OutputFormats/Format")
                )
            ]
        )
        # Metadata URL
        self.metadata_urls = []
        for url in elem.findall(element_key(WFS_NAMESPACE, "MetadataURL")):
            self.metadata_urls.append(url.attrib["{http://www.w3.org/1999/xlink}href"])


class Feature:
    """Feature object based on xml data.

    Holds data of individual features returned by the request
    for geospatial data

    Parameters
    ----------
    elem: lxml.etree._Element
        Data corresponding to the feature

    Returns
    -------
    Feature
    """

    def __init__(self, elem):
        self.fields = {}
        for e in elem.findall(element_key(LOC_NAMESPACE, "*")):
            if e.text and e.text.strip():
                self.fields[e.tag.replace(f"{{{LOC_NAMESPACE}}}", "")] = e.text
            if e.tag.replace(f"{{{LOC_NAMESPACE}}}", "").lower() in (
                "geom",
                "geometry",
                "geometrie",
                "shape",
            ):
                self.geometry = etree.tostring(e[0])

    def __repr__(self):
        return super().__repr__()


class LayerMeta:
    """Metadata for a vector layer based on gml data.

    Parameters
    ----------
    t: lxml.etree._Element
        gml data parsed by lxml.etree
    keyword: str
        string associated with feature dependent values
    """

    def __init__(self, t, keyword):
        # Headers
        self.field_headers = set(
            (
                item.tag.replace(f"{{{LOC_NAMESPACE}}}", "")
                for item in t.iter(element_key(LOC_NAMESPACE, "*"))
                if item.text and not item.text.strip() == ""
            )
        )
        try:
            self.field_headers.remove(keyword)
        except KeyError:
            pass
        finally:
            # self.field_headers = list(self.field_headers)
            pass
        # Field types
        self.field_types = {}
        for header in self.field_headers:
            type_list = tuple(map(is_type, t.iter(element_key(LOC_NAMESPACE, header))))
            self.field_types[header] = is_field_type(type_list)
        type_list = None
        # Create Header link table (max len 10 for shapefile attribute table headers)
        self.link_table = {}
        count = dict(
            zip(
                [item[0:10] for item in self.field_headers],
                [0] * len(self.field_headers),
            )
        )
        for item in self.field_headers:
            ab = item[0:10]
            if count[ab] >= 1:
                n = ab[:-1] + f"{count[ab]}"
            else:
                n = ab
            self.link_table[item] = n
            count[ab] += 1

    def __repr__(self):
        return super().__repr__()

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return sorted(self.field_headers) == sorted(other.field_headers)
        else:
            return False

    def __or__(self, other):
        if isinstance(self, other.__class__):
            pass
        else:
            raise TypeError(
                f"unsupported operand type(s) for |: \
'{self.__class__}' and '{other.__class__}'"
            )

    def __ior__(self, other):
        if isinstance(self, other.__class__):
            self.field_headers |= other.field_headers
            dd = defaultdict(list)
            for d in (self.field_types, other.field_types):
                for k, v in d.items():
                    dd[k].append(v)
            for k, v in dd.items():
                self.field_types.update({k: is_field_type(v)})
            dd = None
            self.link_table |= other.link_table
            return self
        else:
            raise TypeError(
                f"unsupported operand type(s) for |=: \
'{self.__class__}' and '{other.__class__}'"
            )
