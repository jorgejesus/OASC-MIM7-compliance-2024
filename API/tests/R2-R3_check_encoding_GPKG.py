#!/usr/bin/env python3

# python ./R2-R3_check_encoding_GPKG.py example.gpkg
# The layer "point1" contains geospatial data.
# The identifiers are unique.
# The identifiers are persistent.
# GeoPackage processing completed.

import os
import click
import geopandas as gpd  # Required to read layers from GeoPackage
import pyogrio  # Vectorized spatial vector file format I/O using GDAL/OGR, with async support ???


def check_geopackage(filepath):
    """
    Check the GeoPackage for geospatial data using pyogrio and geopandas.
    """
    # List all layers in the GeoPackage
    try:
        layers_info = pyogrio.list_layers(filepath)
    except Exception as e:
        print(f"Error listing layers: {e}")
        return

    # Iterate over all layers
    for layer_info in layers_info:
        try:
            # The first value in layer_info is the layer name
            layer_name = layer_info[0]

            # Load the layer into a GeoDataFrame using geopandas
            data = gpd.read_file(filepath, layer=layer_name)

            # Check if the layer contains geospatial data
            if "geometry" in data.columns and not data["geometry"].isnull().all():
                # Extract 50 records
                data = data.head(50)

                print(f'The layer "{layer_name}" contains geospatial data.')

                # Check if identifiers are unique
                if data.index.is_unique:
                    print("The identifiers are unique.")
                else:
                    print("The identifiers are not unique.")

                # Check if identifiers are persistent
                if data.index.is_monotonic_increasing:
                    print("The identifiers are persistent.")
                else:
                    print("The identifiers are not persistent.")

                # Stop iterating after finding the first layer with geospatial data
                break

        except Exception as e:
            print(f"Error processing layer {layer_name}: {e}")

    print("GeoPackage processing completed.")


@click.command()
@click.argument("file", type=click.Path(exists=True))
def main(file):
    """
    Command line tool to check GeoPackage for geospatial data.

    FILE: Path to the GeoPackage file (e.g., ./example.gpg)
    """
    # Check if the file exists
    if not os.path.isfile(file):
        print(f"File not found: {file}")
        return

    # Run the GeoPackage check
    check_geopackage(file)


if __name__ == "__main__":
    main()
