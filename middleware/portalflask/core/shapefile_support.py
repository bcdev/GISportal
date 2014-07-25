import os

from portalflask.models.database import db_session

from portalflask.models.shapefile import Shapefile
from portalflask.models.shape import Shape

import shapefile as sf
from beampy import jpy
import numpy as np
from flask import current_app, g
from pygeoif import geometry


def get_shape_names(shapefile_name):
    shapefile_path = get_shape_path() + shapefile_name
    shape_names = get_shape_names_from_db(shapefile_path)
    if shape_names is not None:
        print('returning shape names from database')
        return shape_names

    if not os.path.exists(shapefile_path):
        return None
    shapefile = sf.Reader(shapefile_path)
    index = get_name_index(shapefile.fields) - 1  # '- 1' because fields count a deletion flag, which is not present in records
    shape_names = []
    for shape_record in shapefile.shapeRecords():
        shape_names.append(shape_record.record[index])
    return shape_names


def get_bounding_box(shapefile_name, shape_name):
    shapefile_path = get_shape_path() + shapefile_name
    shape = get_shape_from_db(shape_name, shapefile_path)
    if shape.bounding_box is not None:
        print('returning bounding box from database')
        return shape.bounding_box

    if not os.path.exists(shapefile_path):
        return None
    shapefile = sf.Reader(shapefile_path)
    record = get_record(shape_name, shapefile)
    shape_bbox = record.shape.bbox
    result_bbox = ''
    for i, component in enumerate(shape_bbox):
        result_bbox += str(component)
        if i < len(shape_bbox) - 1:
            result_bbox += ','

    shape.bounding_box = result_bbox
    db_session.commit()
    return result_bbox


def get_shape_geometry(shapefile_name, shape_name):
    shapefile_path = get_shape_path() + shapefile_name

    shape_from_db = get_shape_from_db(shape_name, shapefile_path)
    if shape_from_db.geometry is not None:
        print('returning geometry from database')
        return shape_from_db.geometry

    if not os.path.exists(shapefile_path):
        return None
    shapefile = sf.Reader(shapefile_path)
    name_index = get_name_index(shapefile.fields) - 1

    for index, shape_record in enumerate(shapefile.shapeRecords()):
        if shape_record.record[name_index] == shape_name:
            break

    points = np.array(shape_record.shape.points).tolist()
    parts = shape_record.shape.parts

    geometry = get_geometry(points, parts)

    shape_from_db.geometry = geometry
    db_session.commit()
    return geometry


def get_geometry(points, parts):
    start_index = 0
    polygons = []
    for index, part in enumerate(parts):
        sub_geometry = []
        end_index = len(points) if index == len(parts) - 1 else parts[index + 1]

        for x in range(start_index, end_index):
            sub_geometry.append(points[x])

        p = geometry.Polygon(sub_geometry)
        if len(parts) == 1:
            return p.wkt
        else:
            polygons.append(p)

        polygons.append(sub_geometry)
        start_index = end_index
    wkt = geometry.MultiPolygon([(p, None) for p in polygons]).wkt
    return wkt.replace('))((', ')),((')


def get_name_index(fields):
    for index, field in enumerate(fields):
        identifier_index = 0
        if field[identifier_index].lower() == 'name':  # indexing is correct, don't worry
            return index
    print('Warning: cannot find name column. Falling back to column \'' + str(fields[1]) + '\'')
    return 1


def get_record(shape_name, shapefile):
    index = get_name_index(shapefile.fields) - 1  # '- 1' because fields count a deletion flag, which is not present in records
    records = shapefile.shapeRecords()
    for rec in records:
        if rec.record[index] == shape_name:
            return rec
    raise ValueError('Cannot find record with name \'' + shape_name + '\'')


def get_shape_for_record(record):
    GeometryCollectionShape = jpy.get_type('com.vividsolutions.jts.awt.GeometryCollectionShape')
    GeneralPath = jpy.get_type('java.awt.geom.GeneralPath')
    shape = GeometryCollectionShape()
    start_index = 1
    for point_count in record.shape.parts[1:]:
        end_index = start_index + point_count
        path = GeneralPath()
        start_point = record.shape.points[0]
        path.moveTo(start_point[0], start_point[1])
        for point in record.shape.points[start_index:end_index]:
            # lon lat
            path.lineTo(point[0], point[1])
        path.closePath()
        shape.add(path)
        start_index = end_index

    return shape


def get_shape_path():
    return str(current_app.config.get('SHAPEFILE_PATH')) + str(g.user.username) + "/"


def get_shape_names_from_db(shapefile_path):
    shapefiles = Shapefile.query.filter(Shapefile.path == shapefile_path).all()
    if len(shapefiles) > 0:
        shape_names = []
        for shape in shapefiles[0].children:
            shape_names.append(shape.name)
        return shape_names
    return None


def get_shape_from_db(shape_name, shapefile_path):
    # select shape.geometry from shape, shapefile where shape.shapefile_id = shapefile.id and shape.name = shape_name

    return Shape.query \
        .join(Shapefile.children) \
        .filter(Shapefile.path == shapefile_path) \
        .filter(Shape.shapefile_id == Shapefile.id) \
        .filter(Shape.name == shape_name) \
        .all()[0]