#import python packages
import dash
import dash_bootstrap_components as dbc
import dash_auth
import plotly.io as pio
from functions import config

#default template
pio.templates.default = "simple_white"

#assign objects to app
app = dash.Dash(__name__, title=config["header"]["text"], external_stylesheets=[dbc.themes.FLATLY])
server = app.server

#layout
from layout import layout
app.layout = layout

#callbacks
from callbacks import define_callbacks
define_callbacks(app)

if __name__ == "__main__":

	#run app
	import os.path
	if os.path.isfile(".vscode/settings.json"):
		app.run_server(debug=True, host = "10.39.173.120", port = "8052")
	else:
		app.run_server()
