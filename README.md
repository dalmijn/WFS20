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
    wfs.Constraints -> dict
    wfs.FeatureTypes -> tuple
    wfs.FeatureTypeMeta -> object
    wfs.GetCapabilitiesMeta -> object
    wfs.GetFeatureMeta -> object
    wfs.Keywords -> tuple
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
  - [lxml: Parse xml-data returned by the service, whether it be the service itself or the requested data]

## Additional packages
These packages improve the functionality and speed of the wfs20 package, but are not required
  - [osgeo (ogr & osr): Geospatial library written in c++]

These are to be installed from:

```sh
# Conda
conda install gdal
```

Or from a wheel file; Found on the now archived database of Christoph Gohlke: 
https://www.lfd.uci.edu/~gohlke/pythonlibs/

```
# .whl
pip install gdal-xxx.whl
```

## License
[BSD 3](LICENSE.txt)

## Questions/ suggestions/ requests/ bugs?
Send an email to brencodeert@outlook.com