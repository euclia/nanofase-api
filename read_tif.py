import rasterio
from rasterio.plot import show
import rasterio.features
import rasterio.warp


# lyrFile = arcpy.mp.LayerFile(r"C:\Projects\YosemiteNP\Yosemite.lyrx")
# for lyr in lyrFile.listLayers():
#     if lyr.supports("datasource"):
#         if lyr.isBroken:
#             print(lyr.name)

fp = r'/Users/pantelispanka/Downloads/LUISA_basemap_020321_50m.tif'
# img = rasterio.open(fp)
# show(img)

with rasterio.open(fp) as src:
    print(src.tags())
    array = src.read()
    print(array.shape)
    print(src.indexes)
    print(src.dtypes)
    print(src.nodatavals)

    print(src.meta)

    for i, dtype, nodataval in zip(src.indexes, src.dtypes, src.nodatavals):
        print(i, dtype, nodataval)

    # Read the dataset's valid data mask as a ndarray.
    mask = src.dataset_mask()

    i = 0

    # fs = rasterio.features.dataset_features(src)

    dataset_shape = list(rasterio.features.dataset_features(
        src, bidx=1, band=False, as_mask=True, geographic=True
    ))

    print(len(dataset_shape))

    # for s in dataset_shape:
        # print(s)
    # convex_hull = MultiPolygon([shape(s['geometry']) for s in dataset_shape]).convex_hull


    # for s in fs:
    #     print(s)
    # Extract feature shapes and values from the array.
    for geom, val in rasterio.features.shapes(
            mask, transform=src.transform):


        # Transform shapes from the dataset's own coordinate
        # reference system to CRS84 (EPSG:4326).
        # geom = rasterio.warp.transform_geom(
        #     dataset.crs, 'EPSG:4326', geom, precision=6)
        # Print GeoJSON shapes to stdout.


        print(i)
        i += 1

        # for k in geom:
        #     print(i)
        #     print(geom['type'])
        #     print(k)
        #     i += 1
            # print(geom['properties'])
