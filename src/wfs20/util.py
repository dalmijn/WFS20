"""Utility."""

WFS_NAMESPACE = "http://www.opengis.net/wfs/2.0"
OWS_NAMESPACE = "http://www.opengis.net/ows/1.1"
OGC_NAMESPACE = "http://www.opengis.net/ogc"
GML_NAMESPACE = "http://www.opengis.net/gml/3.2"
FES_NAMESPACE = "http://www.opengis.net/fes/2.0"
XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
XLI_NAMESPACE = "http://www.w3.org/1999/xlink"
LOC_NAMESPACE = ""


def execute_read_query(conn, query):
    """Execute a reading query."""
    cur = conn.cursor()
    r = None
    try:
        cur.execute(query)
        r = cur.fetchall()
        return r
    except Exception as e:
        print(f"The error '{e}' occurred")
    cur.close()


def get_localns(nsmap):
    """Local Namespace of the GetCapabilities and GetFeature Response."""
    nb = ["w3.org", "opengis.net"]
    b_list = [
        all([item not in master for item in nb]) for master in list(nsmap.values())
    ]
    try:
        loc_namespace = list(nsmap.values())[b_list.index(True)]
    except ValueError:
        loc_namespace = ""
    finally:
        return loc_namespace


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
