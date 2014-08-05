import os

from portalflask.models.database import db_session

from portalflask.models.shapefile import Shapefile
from portalflask.models.shape import Shape

import shapefile as sf
from beampy import jpy
import numpy as np
from pygeoif import geometry
import pyproj

class ShapefileSupport():


    def __init__(self, db):
        self.db = db
        self.projections = {}


    def get_shape_names(self, shapefile_path):
        shape_names = self.db.get_shape_names(shapefile_path)
        if shape_names is not None:
            print('returning shape names from database')
            return shape_names

        if not os.path.exists(shapefile_path):
            return None
        shapefile = sf.Reader(shapefile_path)
        index = self.get_name_index(shapefile.fields) - 1  # '- 1' because fields count a deletion flag, which is not present in records
        shape_names = []
        for record_number, shape_record in enumerate(shapefile.shapeRecords()):
            shape_name = shape_record.record[index]
            if shape_name in [t[1] for t in shape_names]:
                shape_name = shape_name + '_' + str(record_number)
            shape_names.append((record_number, shape_name))
        return shape_names


    def get_bounding_box(self, shapefile_path, shape_name):
        shape = self.db.get_shape(shape_name, shapefile_path)
        if shape.bounding_box is not None:
            print('returning bounding box from database')
            return shape.bounding_box

        if not os.path.exists(shapefile_path):
            return None
        shapefile = sf.Reader(shapefile_path)
        record = self.get_record(shape.record_number, shapefile)
        result_bbox = ''

        is_point_type = record.shape.shapeType == 1
        if is_point_type:
            epsilon = 0.000001
            point = np.array(record.shape.points)
            point = self.reproject_points(shapefile_path, point)
            point = np.array(point).round(6).tolist()
            result_bbox += str(point[0][0] - epsilon) + ',' + str(point[0][1] - epsilon) + ',' + str(point[0][0] + epsilon) + ',' + str(point[0][1] + epsilon)
        else:
            shape_bbox = []
            for k in range(0, len(record.shape.bbox), 2):
                point = [[record.shape.bbox[k], record.shape.bbox[k + 1]]]
                point = self.reproject_points(shapefile_path, point)
                shape_bbox.append(point[0][0])
                shape_bbox.append(point[0][1])

            for i, component in enumerate(shape_bbox):
                result_bbox += str(component)
                if i < len(shape_bbox) - 1:
                    result_bbox += ','

        shape.bounding_box = result_bbox
        db_session.commit()
        return result_bbox


    def get_shape_geometry(self, shapefile_path, shape_name):
        shape = self.db.get_shape(shape_name, shapefile_path)
        if shape.geometry is not None:
            print('returning geometry from database')
            return shape.geometry

        if not os.path.exists(shapefile_path):
            return None
        shapefile = sf.Reader(shapefile_path)
        shape_record = shapefile.shapeRecords()[shape.record_number]

        points = np.array(shape_record.shape.points)
        points = self.reproject_points(shapefile_path, points)

        is_point_type = shape_record.shape.shapeType == 1
        if is_point_type:
            return geometry.Point([points[0][0], points[0][1]]).wkt

        parts = shape_record.shape.parts
        geom = self.get_geometry(points, parts)
        shape.geometry = geom
        db_session.commit()
        return geom


    def get_geometry(self, points, parts):
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


    def get_name_index(self, fields):
        for index, field in enumerate(fields):
            identifier_index = 0
            if 'name' in field[identifier_index].lower():
                return index
        print('Warning: cannot find name column. Falling back to column \'' + str(fields[1]) + '\'')
        return 1


    def get_record(self, record_number, shapefile):
        return shapefile.shapeRecords()[record_number]


    def get_shape_for_record(self, record):
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

    # points is a 2-dim array, such as [[x1, y1] , [x2, y2]]
    def reproject_points(self, shapefile_path, points):
        if shapefile_path in self.projections:
            in_projection = self.projections[shapefile_path][0]
            out_projection = self.projections[shapefile_path][1]
        else:
            projection_file = str(shapefile_path)[:len(shapefile_path) - 3] + 'prj'
            if os.path.exists(projection_file):
                from osgeo import osr
                with open(projection_file) as proj:
                    projection_text = proj.read()
                spatial_reference = osr.SpatialReference()
                if spatial_reference.ImportFromWkt(projection_text) != 0:
                    return points.tolist()
                in_projection = pyproj.Proj(spatial_reference.ExportToProj4())
                out_projection = pyproj.Proj("+proj=latlong +datum=WGS84")
                self.projections[shapefile_path] = (in_projection, out_projection)
            else:
                return points.tolist()

        lons = np.take(points, [0], 1)
        lats = np.take(points, [1], 1)
        points = pyproj.transform(in_projection, out_projection, lons, lats)
        result = np.zeros((len(points[0]), 2))
        result[:, 0] = points[0].flatten()
        result[:, 1] = points[1].flatten()
        return result.tolist()


class ShapefileDB():

    def get_shape_names(self, shapefile_path):
        shapefiles = Shapefile.query.filter(Shapefile.path == shapefile_path).all()
        if len(shapefiles) > 0:
            shape_names = []
            for shape in shapefiles[0].children:
                shape_names.append(shape.name)
            return shape_names
        return None


    def get_shape(self, shape_name, shapefile_path):
       # select shape.geometry from shape, shapefile where shape.shapefile_id = shapefile.id and shape.name = shape_name
       return Shape.query \
           .join(Shapefile.children) \
           .filter(Shapefile.path == shapefile_path) \
           .filter(Shape.shapefile_id == Shapefile.id) \
           .filter(Shape.name == shape_name) \
           .all()[0]