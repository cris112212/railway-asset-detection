import arcpy
import os

image_directory = r"path/to/images"
bbox_directory = r"path/to/image_bbox"


def get_transformation_params(tfw_path):
    with open(tfw_path, 'r') as f:
        params = [float(line.strip()) for line in f.readlines()]
    return params


def bbox_to_polygon(cx, cy, w, h, params):
    a, d, b, e, c, f = params
    half_width = w / 2.0
    half_height = h / 2.0
    geo_cx = a * cx + b * cy + c
    geo_cy = d * cx + e * cy + f
    geo_half_width = a * half_width
    geo_half_height = e * half_height
    return [
        arcpy.Point(geo_cx - geo_half_width, geo_cy + geo_half_height),
        arcpy.Point(geo_cx + geo_half_width, geo_cy + geo_half_height),
        arcpy.Point(geo_cx + geo_half_width, geo_cy - geo_half_height),
        arcpy.Point(geo_cx - geo_half_width, geo_cy - geo_half_height),
    ]


for image_filename in os.listdir(image_directory):
    if not image_filename.endswith(".tif"):
        continue

    base_name = os.path.splitext(image_filename)[0]
    output_shapefile = os.path.join(image_directory, f"{base_name}_BoundingBoxes.shp")
    bbox_file_path = os.path.join(bbox_directory, base_name + ".txt")
    tfw_file_path = os.path.join(image_directory, base_name + ".tfw")
    prj_file_path = os.path.join(image_directory, base_name + ".prj")

    if not all(os.path.exists(p) for p in [bbox_file_path, tfw_file_path, prj_file_path]):
        continue

    spatial_ref = arcpy.SpatialReference(prj_file_path)
    params = get_transformation_params(tfw_file_path)

    arcpy.CreateFeatureclass_management(
        out_path=os.path.dirname(output_shapefile),
        out_name=os.path.basename(output_shapefile),
        geometry_type="POLYGON",
        spatial_reference=spatial_ref
    )
    arcpy.AddField_management(output_shapefile, "Label", "TEXT")

    with open(bbox_file_path, 'r') as bbox_file:
        with arcpy.da.InsertCursor(output_shapefile, ['SHAPE@', 'Label']) as cursor:
            for line in bbox_file:
                parts = line.strip().split()
                if len(parts) == 5:
                    label, cx, cy, w, h = parts
                    cx, cy, w, h = map(float, [cx, cy, w, h])
                    polygon = arcpy.Polygon(arcpy.Array(bbox_to_polygon(cx, cy, w, h, params)), spatial_ref)
                    cursor.insertRow([polygon, label])
                else:
                    print(f"Invalid bbox format in file {bbox_file_path}")

print("Finished creating individual bounding box shapefiles for each image.")
