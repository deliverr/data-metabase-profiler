import dash
import dash_bootstrap_components as dbc
import os


application = dash.Dash(__name__,
                        external_stylesheets=[dbc.themes.SPACELAB],
                        suppress_callback_exceptions=True,
                        meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}],
                        title='Metabase Profiler'
                        )
server = application.server
server.secret_key = os.environ['MBP_SECRET_KEY']