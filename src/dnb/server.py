from multiprocessing import Condition

import dash_leaflet as dl
import geopandas as gpd

import setproctitle
from dash import dash, html
import numpy as np
from dnb.domino import terminate_when_parent_process_dies


def start_dash(host: str, port: int, server_is_started: Condition):
    # Set the process title.
    setproctitle.setproctitle('dnb-dash')
    # When the parent dies, follow along.
    terminate_when_parent_process_dies()

    # The following is the minimal sample code from dash itself:
    # https://dash.plotly.com/minimal-app

    
    map=gpd.read_file("src/dnb/municipiosjair.shp")
    print(map)

    geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": feature["geometry"],
                    "properties": {
                        **feature["properties"],
                        "tooltip": f"Municipio: {feature['properties'].get('NOM_MUN','N/A')} "

                    }
                }
                for idx, feature in enumerate(map.__geo_interface__["features"])
            ]
        }
    app = dash.Dash()

    app.layout = html.Div([
        dl.Map(center=[21, -98], zoom=8, children=[
            dl.TileLayer(),
            dl.GeoJSON(data=geojson_data, id="geojson", 
                options=dict(interactive=False,
                            style=dict(color="gray", weight=1, fillOpacity=0.5,
                                        fillColor="white")),
                
            ),
        ], style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"})
    ])
    with server_is_started:
        server_is_started.notify()

# debug cannot be True right now with nuitka: https://github.com/Nuitka/Nuitka/issues/2953
    app.run(debug=False, host=host, port=port)
