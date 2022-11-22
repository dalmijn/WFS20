# wfs20: Small library for requesting geospatial data (WFS)

## What is it?
wfs20 is a small library with the sole purpose of making it easy
on the user to request geospatial data from a WebFeatureService.
wfs20 only caters to the 2.0.0 version of the WebFeatureService 
for now. wfs20 will be expanded in the future to also contain the
1.0.0 and 1.1.0 version of the WebFeatureService.

## What can it do?
Some of its functionality is listed below:

  - Get the capabilities and metadata of/from the service

    ```sh
    from wfs20 import WebFeatureService
    wfs = WebFeatureService(<url>)
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

    crs = CRS.from_epsg(<epsg>)

    url = CreateGetRequest(
      service_url,
      version
      featuretype
      bbox,
      crs
      )

    reader = DataReader(<url>)
    ```

    Where again you have a reader object holding the geospatial data

## Where to get it?
Source code is available at this repository on Github:
https://github.com/B-Dalmijn/WFS20

The package can be installed from:

```sh
# PyPI
pip install wfs20
```

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