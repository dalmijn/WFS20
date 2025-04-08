# wfs20: Small library for requesting geospatial data (WFS)

## What is it?
wfs20 is a small library with the sole purpose of making it easy
on the user to request geospatial data from a WebFeatureService.
wfs20 only caters to the 2.0.0 version of the WebFeatureService
for now. wfs20 will be expanded in the future to also contain the
1.0.0 and 1.1.0 version of the WebFeatureService.

## Where to get it?
Source code is available at this repository on Github:
https://github.com/B-Dalmijn/WFS20

The package can be installed from:

```sh
# PyPI
pip install wfs20
```

## What can it do?
Some of its functionality is listed below:

  - Get the capabilities and metadata of/from the service

  ```sh
  # service
  from wfs20 import WebFeatureService
  wfs = WebFeatureService(url)

  # metadata
  wfs.Constraints
  wfs.FeatureTypes
  wfs.FeatureTypeMeta
  wfs.GetCapabilitiesMeta
  wfs.GetFeatureMeta
  wfs.Keywords
  ```

  - Request geospatial data from the service

  ```sh
  reader = wfs.RequestData("<layer>",(x1,y1,x2,y2),proj_code)
  # proj_code is the projection code corresponding with the geospatial data
  # to be requested and the given bbox (x1,y1,x2,y2)
  ```

    The returned reader object holds the geospatial data and
    subsequent metadata

  - Export the requested data to the harddrive, as long as there is
    data in the reader object

  ```sh
  # to gml
  wfs.ToFile("<folder>",format="gml")
  ```

  ```sh
  # to ESRI ShapeFile
  wfs.ToFile("<folder>",format="shp")
  ```

  - It is completely modular, so if you know the capabilities of the service,
    you don't really need to use the WebFeatureService class

    E.g.

  ```sh
  from wfs20.crs import CRS
  from wfs20.reader import DataReader
  from wfs20.request import CreateGetRequest

  crs = CRS.from_epsg(epsg)

  url = CreateGetRequest(
    service_url,
    version,
    featuretype,
    bbox,
    crs
    )

  reader = DataReader(url,keyword)
  ```
    keyword is in general the Title of the featuretype, e.g. 'bag:pand' -> keyword is 'pand'
    Where again you have a reader object holding the geospatial data

  - Both GET and POST requests are supported, though wfs20.RequestData only supports GET request
    url and POST request data can however be implemented in the DataReader

  ```sh
  from wfs20.request import CreatePostRequest

  url,data = CreatePostRequest(
    url,
    version,
    featuretype,
    bbox,
    crs
    )

  reader = DataReader(url,keyword,method="POST",data=data)
  ```

  Again one would have a reader object holding the acquired geospatial data.

## Dependencies
  - [requests:    HTTP library]
  - [lxml:        XML parsing library]

## Additional packages
These packages improve the functionality wfs20 package
  - [GDAL:        Geospatial Data Abstraction Library]

GDAL can either be installed from the conda repository via:

```sh
conda install gdal
```

Or from a wheel (.whl) file. Wheel files for GDAL are very kindly made by
Christoph Gohlke and are in the releases of this [repository on github](https://github.com/cgohlke/geospatial.whl/).
The newest GDAL wheel file of Gohlke will always be in the newest release of wfs20 on github.

Simply install the wheel file with pip:

```sh
# GDAL 3.6.2 for python 3.10
pip install GDAL-3.6.2-cp310-cp310-win_amd64.whl
```

## License
[BSD 3](https://github.com/B-Dalmijn/WFS20/blob/master/LICENSE)

## Questions/ suggestions/ requests/ bugs?
Send an email to brencodeert@outlook.com
