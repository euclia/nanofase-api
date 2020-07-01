from src.globals.globals import oidc, mongoClient, data_path, model_files, model_vars, model_config, model_path
import json
from convertbng.util import convert_bng, convert_lonlat
import subprocess
import rasterio as rio
import geopandas as gpd
import pandas as pd
import numpy as np
from rasterio.transform import from_bounds
from shapely.geometry import shape
from rasterio.mask import mask
from rasterio.merge import merge
import rasterio
import rasterio.features
import rasterio.warp
import os

from ruamel.yaml import YAML
import yaml
from .compiler_new import Compiler

from functools import partial
import pyproj
import shapely as sh
import shutil
import f90nml
import subprocess


# export PYTHONPATH="/home/pantelispanka/Jaqpot/nanofase-api"


def run_simulation(simulation, task):

    point_emissions = []
    areal_emissions = []
    out_meta = {}

    point_emissions_pristine = []
    point_emissions_matrix = []
    point_emissions_transformed = []
    point_emissions_dissolved = []

    areal_emissions_pristine_water = []
    areal_emissions_matrix_water = []
    areal_emissions_transformed_water = []
    areal_emissions_dissolved_water = []

    areal_emissions_pristine_soil = []
    areal_emissions_matrix_soil = []
    areal_emissions_transformed_soil = []
    areal_emissions_dissolved_soil = []

    for em in simulation['emissions']:
        query = {"_id": em}
        emis = mongoClient['emission'].find_one(query)
        json_file = data_path + "/" + emis["id"] + ".json"

        with open(json_file, 'w') as f:
            if emis['geometry']['type'] == "Point":


                project = partial(
                    pyproj.transform,
                    pyproj.Proj(init='epsg:4326'),  # Source coordinate system (WGS84)
                    pyproj.Proj(init='epsg:27700'))  # Destination coordinate system (British National Grid)
                # Do the transformation

                geom_transformed = sh.ops.transform(project, shape(emis['geometry']))
                # print(geom_transformed)
                # coos = convert_bng(emis['geometry']['coordinates'][0], emis['geometry']['coordinates'][1])
                # emis['geometry']['coordinates'][0] = coos[0][0]
                # emis['geometry']['coordinates'][1] = coos[1][0]
                jt = gpd.GeoSeries([geom_transformed]).to_json()
                jt = json.loads(jt)
                emis['geometry']['coordinates'] = jt['features'][0]['geometry']['coordinates']
                emis["properties"]["emission"] = int(emis["properties"]["emission"])
                point_emissions.append(json_file)
                json.dump(emis, f, ensure_ascii=False, indent=4)
                if emis['properties']['form'] == "Pristine":
                    point_emissions_pristine.append(json_file)
                if emis['properties']['form'] == "Matrix embedded":
                    point_emissions_matrix.append(json_file)
                if emis['properties']['form'] == "Transformed":
                    point_emissions_transformed.append(json_file)
                if emis['properties']['form'] == "Dissolved":
                    point_emissions_dissolved.append(json_file)

            if emis['geometry']['type'] == "Polygon":
                project = partial(
                    pyproj.transform,
                    pyproj.Proj(init='epsg:4326'),  # Source coordinate system (WGS84)
                    pyproj.Proj(init='epsg:27700'))  # Destination coordinate system (British National Grid)
                # Do the transformation
                geom_transformed = sh.ops.transform(project, shape(emis['geometry']))
                # i = 0
                # for j in emis['geometry']['coordinates'][0]:
                #     coos = convert_bng(j[0], j[1])
                #     emis['geometry']['coordinates'][0][i][0] = coos[0][0]
                #     emis['geometry']['coordinates'][0][i][1] = coos[1][0]
                #     i += 1
                jt = gpd.GeoSeries([geom_transformed]).to_json()
                jt = json.loads(jt)
                emis['geometry']['coordinates'] = jt['features'][0]['geometry']['coordinates']
                point_emissions.append(json_file)
                areal_emissions.append(json_file)
                json.dump(emis, f, ensure_ascii=False, indent=4)

    points = []
    po_em_pri = gpd.GeoDataFrame()
    for po in point_emissions_pristine:
        po_em_pri = po_em_pri.append(gpd.read_file(po))
    if po_em_pri.empty is False:
        to_shape = data_path + "/points/" + "water_pristine_" + simulation['_id'] + ".shp"
        po_em_pri.to_file(to_shape)
        points.append(to_shape)
        pewp = to_shape

    po_em_matr = gpd.GeoDataFrame()
    for po in point_emissions_matrix:
        po_em_matr = po_em_matr.append(gpd.read_file(po))
    if po_em_matr.empty is False:
        to_shape = data_path + "/points/" + "water_matrix_" + simulation['_id'] + ".shp"
        po_em_matr.to_file(to_shape)
        points.append(to_shape)
        pewm = to_shape


    po_em_transf = gpd.GeoDataFrame()
    for po in point_emissions_transformed:
        po_em_transf = po_em_transf.append(gpd.read_file(po))
    if po_em_transf.empty is False:
        to_shape = data_path + "/points/" + "water_transf_" + simulation['_id'] + ".shp"
        po_em_transf.to_file(to_shape)
        points.append(to_shape)
        pewt = to_shape


    po_em_dis = gpd.GeoDataFrame()
    for po in point_emissions_dissolved:
        po_em_dis = po_em_dis.append(gpd.read_file(po))
    if po_em_dis.empty is False:
        to_shape = data_path + "/points/" + "water_dis_" + simulation['_id'] + ".shp"
        po_em_dis.to_file(to_shape)
        points.append(to_shape)



    # for po_em in point_emissions:
    #     po_em_a = po_em.split("/")
    #     po_id = po_em_a[len(po_em_a)-1].split(".")[0]
    #     output_shape = data_path + "/points/" + po_id + ".shp"
    #     gdf = gpd.read_file(po_em)
    #     gdf.to_file(output_shape)
    #     points.append(output_shape)

    areals = []
    for ar_em in areal_emissions:
        with open(ar_em) as f:
            area = json.load(f)
            geom = shape(area['geometry'])
            res = 5000

            # Get the bounds of the Shapely polygon, used to set the height/width of raster
            minx, miny, maxx, maxy = geom.bounds
            # Assume we want all pixels (cells) touched by the polygon, so round the min and max coords to encompass these
            minx_rounded = minx - minx % res
            maxx_rounded = maxx + (res - maxx) % res
            miny_rounded = miny - miny % res
            maxy_rounded = maxy + (res - maxy) % res
            _shape = (1, int((maxx_rounded - minx_rounded) / res), int((maxy_rounded - miny_rounded) / res))

            # Create an array with these dimensions and fill with a constant value
            arr = np.full(_shape, fill_value=42.0)

            # Create an affine transformation to use to create raster
            transform = from_bounds(minx_rounded, miny_rounded, maxx_rounded, maxy_rounded, _shape[1], _shape[2])

            # Create out_meta to pass to rasterio when creating the raster
            out_meta = {
                "driver": "GTiff",
                "height": _shape[1],
                "width": _shape[2],
                "transform": transform,
                "count": 1,
                "dtype": arr.dtype,
                "crs": 'EPSG:27700'
            }
            ar_em_a = ar_em.split("/")
            ar_id = ar_em_a[len(ar_em_a)-1].split(".")[0]
            output_tiff = data_path + "/areal/" + ar_id + ".tif"
            with rio.open(output_tiff, 'w', **out_meta) as dest:
                dest.write(arr)
            with rio.open(output_tiff) as src:
                out_ma, out_transform = rio.mask.mask(src, [geom], crop=True, filled=False)
                out_meta = src.meta
            with rio.open(output_tiff, "w", **out_meta) as dest:
                dest.write(out_ma)
            areals.append(output_tiff)
            if area['properties']['form'] == "Pristine" and area['properties']['compartment'] == "Surface water":
                areal_emissions_pristine_water.append(output_tiff)
            if area['properties']['form'] == "Matrix embedded" and area['properties']['compartment'] == "Surface water":
                areal_emissions_matrix_water.append(output_tiff)
            if area['properties']['form'] == "Transformed" and area['properties']['compartment'] == "Surface water":
                areal_emissions_transformed_water.append(output_tiff)
            if area['properties']['form'] == "Dissolved" and area['properties']['compartment'] == "Surface water":
                areal_emissions_dissolved_water.append(output_tiff)
            if area['properties']['form'] == "Pristine" and area['properties']['compartment'] == "Soil":
                areal_emissions_pristine_soil.append(output_tiff)
            if area['properties']['form'] == "Matrix embedded" and area['properties']['compartment'] == "Soil":
                areal_emissions_matrix_soil.append(output_tiff)
            if area['properties']['form'] == "Transformed" and area['properties']['compartment'] == "Soil":
                areal_emissions_transformed_soil.append(output_tiff)
            if area['properties']['form'] == "Dissolved" and area['properties']['compartment'] == "Soil":
                areal_emissions_dissolved_soil.append(output_tiff)

    tiffs_ds = []
    for aeds in areal_emissions_dissolved_soil:
        tif = rasterio.open(aeds)
        tiffs_ds.append(tif)
    if len(tiffs_ds) > 1:
        mosaic, out_trans = rio.merge.merge(tiffs_ds)
        out_meta.update(
            {"driver": "GTiff",
             "height": mosaic.shape[1],
             "width": mosaic.shape[2],
             "transform": out_trans,
             "crs": 'EPSG:27700'})
        out_areal = data_path + "/areal/" + "dissolved_soil_" + simulation['_id'] + ".tif"
        with rasterio.open(out_areal, "w", **out_meta) as dest:
            dest.write(mosaic)
            aedst = out_areal
    elif len(tiffs_ds) == 1:
        _shape, out_trans = rio.open(tiffs_ds[0])
        out_meta = {
            "driver": "GTiff",
            "height": _shape[1],
            "width": _shape[2],
            "transform": transform,
            "count": 1,
            "dtype": arr.dtype,
            "crs": 'EPSG:27700'
        }
        out_areal = data_path + "/areal/" + "dissolved_soil_" + simulation['_id'] + ".tif"
        with rasterio.open(out_areal, "w", **out_meta) as dest:
            dest.write(_shape)
            aedst = out_areal

    tiffs_dw = []
    for aeds in areal_emissions_dissolved_water:
        tif = rasterio.open(aeds)
        tiffs_dw.append(tif)
    if len(tiffs_dw) > 1:
        mosaic, out_trans = rio.merge.merge(tiffs_dw)
        out_meta.update(
            {"driver": "GTiff",
             "height": mosaic.shape[1],
             "width": mosaic.shape[2],
             "transform": out_trans,
             "crs": 'EPSG:27700'})
        out_areal = data_path + "/areal/" + "dissolved_water_" + simulation['_id'] + ".tif"
        with rasterio.open(out_areal, "w", **out_meta) as dest:
            dest.write(mosaic)
            aedwt = out_areal
    elif len(tiffs_dw) == 1:
        fi = tiffs_dw[0]
        out_areal = data_path + "/areal/" + "dissolved_water_" + simulation['_id'] + ".tif"
        srcf = fi.name
        shutil.copy(srcf, out_areal)
        aedwt = out_areal


    tiffs_ms = []
    for aeds in areal_emissions_matrix_soil:
        tif = rasterio.open(aeds)
        tiffs_ms.append(tif)
    if len(tiffs_ms) > 1:
        mosaic, out_trans = rio.merge.merge(tiffs_ms)
        out_meta.update(
            {"driver": "GTiff",
             "height": mosaic.shape[1],
             "width": mosaic.shape[2],
             "transform": out_trans,
             "crs": 'EPSG:27700'})
        out_areal = data_path + "/areal/" + "matrix_soil_" + simulation['_id'] + ".tif"
        with rasterio.open(out_areal, "w", **out_meta) as dest:
            dest.write(mosaic)
            aemst = out_areal
    elif len(tiffs_ms) == 1:
        fi = tiffs_ms[0]
        out_areal = data_path + "/areal/" + "matrix_soil_" + simulation['_id'] + ".tif"
        srcf = fi.name
        shutil.copy(srcf, out_areal)
        aemst = out_areal

    tiffs_mw = []
    for aeds in areal_emissions_matrix_water:
        tif = rasterio.open(aeds)
        tiffs_mw.append(tif)
    if len(tiffs_mw) > 1:
        mosaic, out_trans = rio.merge.merge(tiffs_mw)
        out_meta.update(
            {"driver": "GTiff",
             "height": mosaic.shape[1],
             "width": mosaic.shape[2],
             "transform": out_trans,
             "crs": 'EPSG:27700'})
        out_areal = data_path + "/areal/" + "matrix_water_" + simulation['_id'] + ".tif"
        with rasterio.open(out_areal, "w", **out_meta) as dest:
            dest.write(mosaic)
            aemwt = out_areal
    elif len(tiffs_mw) == 1:
        fi = tiffs_mw[0]
        out_areal = data_path + "/areal/" + "matrix_water_" + simulation['_id'] + ".tif"
        srcf = fi.name
        shutil.copy(srcf, out_areal)
        aemwt = out_areal

    tiffs_ps = []
    for aeds in areal_emissions_pristine_soil:
        tif = rasterio.open(aeds)
        tiffs_ps.append(tif)
    if len(tiffs_ps) > 1:
        mosaic, out_trans = rio.merge.merge(tiffs_ps)
        out_meta.update(
            {"driver": "GTiff",
             "height": mosaic.shape[1],
             "width": mosaic.shape[2],
             "transform": out_trans,
             "crs": 'EPSG:27700'})
        out_areal = data_path + "/areal/" + "pristine_soil_" + simulation['_id'] + ".tif"
        with rasterio.open(out_areal, "w", **out_meta) as dest:
            dest.write(mosaic)
            aepst = out_areal
    elif len(tiffs_ps) == 1:
        fi = tiffs_ps[0]
        out_areal = data_path + "/areal/" + "pristine_soil_" + simulation['_id'] + ".tif"
        srcf = fi.name
        shutil.copy(srcf, out_areal)
        aepst = out_areal


    tiffs_pw = []
    for aeds in areal_emissions_pristine_water:
        tif = rasterio.open(aeds)
        tiffs_pw.append(tif)
    if len(tiffs_pw) > 1:
        out_meta.update(
            {"driver": "GTiff",
             "height": mosaic.shape[1],
             "width": mosaic.shape[2],
             "transform": out_trans,
             "crs": 'EPSG:27700'})
        out_areal = data_path + "/areal/" + "pristine_water_" + simulation['_id'] + ".tif"
        with rasterio.open(out_areal, "w", **out_meta) as dest:
            dest.write(mosaic)
            aepwt = out_areal
    elif len(tiffs_pw) == 1:
        fi = tiffs_pw[0]
        out_areal = data_path + "/areal/" + "pristine_water_" + simulation['_id'] + ".tif"
        srcf = fi.name
        shutil.copy(srcf, out_areal)
        aepwt = out_areal

    tiffs_ts = []
    for aeds in areal_emissions_transformed_soil:
        tif = rasterio.open(aeds)
        tiffs_ts.append(tif)
    if len(tiffs_ts) > 1:
        mosaic, out_trans = rio.merge.merge(tiffs_ts)
        out_meta.update(
            {"driver": "GTiff",
             "height": mosaic.shape[1],
             "width": mosaic.shape[2],
             "transform": out_trans,
             "crs": 'EPSG:27700'})
        out_areal = data_path + "/areal/" + "transformed_soil_" + simulation['_id'] + ".tif"
        with rasterio.open(out_areal, "w", **out_meta) as dest:
            dest.write(mosaic)
            aetst = out_areal
    elif len(tiffs_ts) == 1:
        fi = tiffs_ts[0]
        out_areal = data_path + "/areal/" + "transformed_soil_" + simulation['_id'] + ".tif"
        srcf = fi.name
        shutil.copy(srcf, out_areal)
        aetst = out_areal

    tiffs_tw = []
    for aeds in areal_emissions_transformed_water:
        tif = rasterio.open(aeds)
        tiffs_tw.append(tif)
    if len(tiffs_tw) > 1:
        mosaic, out_trans = rio.merge.merge(tiffs_tw)
        out_meta.update(
            {"driver": "GTiff",
             "height": mosaic.shape[1],
             "width": mosaic.shape[2],
             "transform": out_trans,
             "crs": 'EPSG:27700'})
        out_areal = data_path + "/areal/" + "transformed_water_" + simulation['_id'] + ".tif"
        with rasterio.open(out_areal, "w", **out_meta) as dest:
            dest.write(mosaic)
            aetwt = out_areal
    elif len(tiffs_tw) == 1:
        fi = tiffs_tw[0]
        out_areal = data_path + "/areal/" + "transformed_water_" + simulation['_id'] + ".tif"
        srcf = fi.name
        shutil.copy(srcf, out_areal)
        aetwt = out_areal



    path = data_path + "/" + simulation['_id']

    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)

    # yaml = YAML(typ='safe')
    with open('/home/pantelispanka/Jaqpot/nanofase-api/src/data/example.yaml', 'r') as f:
        yam = yaml.load(f)
        yam['output']['nc_file'] = path + "/data.nc"
        yam['output']['constants_file'] = path + "/constants.nml"
        yam['constants_file'] = model_files + "constants.yaml"
        yam['land_use_config'] = model_files + "land_use.yaml"
        yam['root_dir'] = model_files
        yam['time']['start_date'] = simulation['startDate']
        try:
            yam['emissions_areal_soil_pristine']['path'] = aepst
        except UnboundLocalError:
            del yam['emissions_areal_soil_pristine']['path']

        try:
            yam['emissions_areal_soil_matrixembedded']['path'] = aemst
        except UnboundLocalError:
            del yam['emissions_areal_soil_matrixembedded']

        try:
            yam['emissions_areal_soil_transformed']['path'] = aetst
        except UnboundLocalError:
            del yam['emissions_areal_soil_transformed']

        try:
            yam['emissions_areal_water_pristine']['path'] = aepwt
        except UnboundLocalError:
            del yam['emissions_areal_water_pristine']

        try:
            yam['emissions_areal_water_matrixembedded']['path'] = aemwt
        except UnboundLocalError:
            del yam['emissions_areal_water_matrixembedded']

        try:
            yam['emissions_areal_water_transformed']['path'] = aetwt
        except UnboundLocalError:
            del yam['emissions_areal_water_transformed']

        try:
            yam['emissions_point_water_pristine']['path'] = pewp
        except UnboundLocalError:
            del yam['emissions_point_water_pristine']

        try:
            yam['emissions_point_water_matrixembedded']['path'] = pewm
        except UnboundLocalError:
            del yam['emissions_point_water_matrixembedded']

        try:
            yam['emissions_point_water_transformed']['path'] = pewt
        except UnboundLocalError:
            del yam['emissions_point_water_transformed']

    yf = path + "/" + simulation['_id']+".yaml"
    with open(yf, "w") as f:
        yaml.dump(yam, f)
    comp = Compiler("create", yf, model_vars)
    comp.create()

    model_conf_file = path + "/" + simulation['_id'] + ".nml"
    with open(model_config) as nml_file:
        nml = f90nml.read(nml_file)
        # patch_nml = {'&data': {'input_file': '/data.nc', 'constants_file': path + '/constants.nml'
        #     , 'output_path': path + "/"}}
        # f90nml.patch(nml_file, patch_nml, model_conf_file)
        nml['data']['input_file'] = path + '/data.nc'
        nml['data']['constants_file'] = path + '/constants.nml'
        nml['data']['output_path'] = path + "/"
        nml['run']['log_file_path'] = path + "/"
        nml['run']['start_date'] = simulation['startDate']
        with open(model_conf_file, 'w') as nml_file2:
            nml.write(nml_file2)

    subprocess.call([model_path, model_conf_file])
    print("Hurray!!!!!")

    for ae in areal_emissions:
        if os.path.exists(ae):
            os.remove(ae)

    for pe in point_emissions:
        if os.path.exists(pe):
            os.remove(pe)




    # tiffs = []
    # for ae in areals:
    #     tif = rasterio.open(ae)
    #     tiffs.append(tif)
    # mosaic, out_trans = rio.merge.merge(tiffs)
    # out_meta.update(
    #     {"driver": "GTiff",
    #      "height": mosaic.shape[1],
    #      "width": mosaic.shape[2],
    #       "transform": out_trans,
    #       "crs": 'EPSG:27700'})
    # out_areal = data_path + "/areal/" + simulation['_id'] + ".tif"
    # with rasterio.open(out_areal, "w", **out_meta) as dest:
    #     dest.write(mosaic)




    #
    # for aer in areals:
    #     if os.path.exists(aer):
    #         os.remove(aer)
    #
    # for po in points:
    #     if os.path.exists(po):
    #         os.remove(po)



        # if emis['geometry']['type'] == "Point":
        #     coos = convert_bng(emis['geometry']['coordinates'][0], emis['geometry']['coordinates'][1])
        #     emis['geometry']['coordinates'][0] = coos[0][0]
        #     emis['geometry']['coordinates'][1] = coos[1][0]
        # json.dump(emis, f, ensure_ascii=False, indent=4)
        # output_shape = data_path + "/shapes/" + emis["id"] + ".shp"
        # gdf = gpd.read_file(json_file)
        # gdf.to_file(output_shape)
        # if emis['geometry']['type'] == "Polygon":
        #     i = 0
        #     for j in emis['geometry']['coordinates'][0]:
        #         coos = convert_bng(j[0], j[1])
        #         emis['geometry']['coordinates'][0][i][0] = coos[0][0]
        #         emis['geometry']['coordinates'][0][i][1] = coos[1][0]
        #         i += 1
        #         # json.dump(emis, f, ensure_ascii=False, indent=4)
        #         geom = shape(emis['geometry'])
        #
        #         res = 5000
        #
        #         # Get the bounds of the Shapely polygon, used to set the height/width of raster
        #         minx, miny, maxx, maxy = geom.bounds
        #         # Assume we want all pixels (cells) touched by the polygon, so round the min and max coords to encompass these
        #         minx_rounded = minx - minx % res
        #         maxx_rounded = maxx + (res - maxx) % res
        #         miny_rounded = miny - miny % res
        #         maxy_rounded = maxy + (res - maxy) % res
        #         shape = (1,
        #                  int((maxx_rounded - minx_rounded) / res),
        #                  int((maxy_rounded - miny_rounded) / res))
        #
        #         # Create an array with these dimensions and fill with a constant value
        #         arr = np.full(shape, fill_value=42.0)
        #
        #         # Create an affine transformation to use to create raster
        #         transform = from_bounds(minx_rounded, miny_rounded, maxx_rounded, maxy_rounded, shape[1], shape[2])
        #
        #         # Create out_meta to pass to rasterio when creating the raster
        #         out_meta = {
        #             "driver": "GTiff",
        #             "height": shape[1],
        #             "width": shape[2],
        #             "transform": transform,
        #             "count": 1,
        #             "dtype": arr.dtype,
        #             "crs": 'EPSG:27700'
        #         }
        #         output_tiff = data_path + "/shapes/" + emis["id"] + ".tif"
        #         with rio.open(output_tiff, 'w', **out_meta) as dest:
        #             dest.write(arr)
        #         with rio.open(output_tiff) as src:
        #             out_ma, out_transform = mask(src, [geom], crop=True, filled=False)
        #             out_meta = src.meta
        #         with rio.open(output_tiff, "w", **out_meta) as dest:
        #             dest.write(out_ma)

        # gJ = GeoJ(json_file)
        # output_shape = data_path + "/shapes/" + emis["id"]
        # gJ.toShp(output_shape)
        #
        # if os.path.exists(json_file):
        #     os.remove(json_file)
        # shp1_file = data_path + "/shapes/" + emis["id"] + ".shp"
        # if os.path.exists(shp1_file):
        #     os.remove(shp1_file)
        # shp2_file = data_path + "/shapes/" + emis["id"] + ".dbf"
        # if os.path.exists(shp2_file):
        #     os.remove(shp2_file)
        # shp3_file = data_path + "/shapes/" + emis["id"] + ".shx"
        # if os.path.exists(shp3_file):
        #     os.remove(shp3_file)
        # shp4_file = data_path + "/shapes/" + emis["id"] + ".prj"
        # if os.path.exists(shp4_file):
        #     os.remove(shp4_file)


        # eng_coordinates = convert_bng(-0.7008836583042489, 51.56269530926185)
        # print("English coordinates : ")
        # print(eng_coordinates)
        # print("---------------------------------------")
        # wgs_coordinates = convert_lonlat(490147.702, 185667.622)
        # print("WGS84  coordinates : ")
        # print(wgs_coordinates)
