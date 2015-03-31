#!/usr/bin/python
import fiona
from shapely import geometry
from pyproj import Proj, transform
import shapefile
from rtree import index

SHP_FILE = './garda-sub-districts/Census2011_Garda_SubDistricts_Nov2013/Census2011_Garda_Subdistricts_Nov2013.shp'
#FIELD_INDEX = 6
FIELD_INDEX = 8

#SHP_FILE = './garda-sub-districts/dublin_parishes/Census2011_Dublin_Parishes_generalised.shp'
#FIELD_INDEX = 3

with fiona.open(SHP_FILE) as fc:
    CRS = fc.crs


def add_fields(data, field_index=FIELD_INDEX, field_name='garda_subdistrict'):
    points = data[['lat', 'lng']].values
    label_values = find_polygons(points, field_index)
    
    data[field_name] = label_values
    return data

# http://stackoverflow.com/questions/20297977/looking-for-a-fast-way-to-find-the-polygon-a-point-belongs-to-using-shapely
def find_polygons(points, field_index):
    shp_file = shapefile.Reader(SHP_FILE)
    print 'READ FILE'
    shapes = shp_file.shapes()

    print 'CREATE INDEX'
    index = create_index(shapes)

    print 'CREATE POLYGONS'
    polygons = [geometry.Polygon(shape.points) for shape in shapes]

    res = []

    print 'FIND SUB_DISTS'
    for (i, p) in enumerate(points):
        lat, lng = p
        point = project_point(lng, lat)
        polygon_index = find_polygon(lng, lat, index, polygons)
        res.append(shp_file.records()[polygon_index][field_index])
        #if polygon_index:
            #res.append(shp_file.records()[polygon_index][field_index])
        #else:
            #res.append(None)

        if i%100==0:
            print '{} DONE'.format(i)

    return res

def create_index(shapes):
    idx = index.Index()
    count = -1
    for s in shapes:
        count +=1
        idx.insert(count, s.bbox)
    return idx


def find_polygon(lng, lat, index, polygons):
    point = project_point(lng, lat)

    for j in index.intersection([point.x, point.y]):
        if(point.within(polygons[j])):
            return j

    return None

def label_all(data):
    with fiona.open(SHP_FILE) as records:
        data['garda_subdistrict'] = data[['lat', 'lng']].apply(lambda x: check(x[1], x[0], records), axis=1)


def check(lng, lat, records):
    point = project_point(lng, lat, fc.crs)

    for record in records:
        print 'create shape for {}'.format(record['properties']['SUB_DIST'])
        shape = geometry.asShape(record['geometry'])
        if shape.contains(point):
            return record['properties']['SUB_DIST']


def project_point(lng, lat):
    origin = Proj(init='EPSG:4326', preserve_units=True)
    dest = Proj(CRS, preserve_units=True)
    projected_point = transform(origin, dest, lng, lat)
    return geometry.Point(projected_point)
