"""Build metadata functions."""

from lxml import etree

import wfs20.util as util
from wfs20.struct import (
    Feature,
    FeatureTypeMeta,
    LayerMeta,
)
from wfs20.util import (
    OWS_NAMESPACE,
    WFS_NAMESPACE,
    XLI_NAMESPACE,
    element_key,
    get_localns,
)


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
            key.lower(),
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
    tree = etree.fromstring(r.content)
    # Generate Local NameSpace
    loc_namespace = get_localns(tree.nsmap)
    # Set the global variable
    util.LOC_NAMESPACE = loc_namespace
    # Some identifiers
    reader.gml = r.content
    # Get the requested feature xml's
    reader.features = []
    for elem in tree.iter(element_key(loc_namespace, keyword)):
        reader.features.append(Feature(elem))
    # Get the Layer meta data
    reader.layer_meta = LayerMeta(tree, keyword)
    tree = None


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
