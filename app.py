import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_bootstrap_components as dbc
import dash_auth
import dash_table
from dash_table.Format import Format, Scheme
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import re
import urllib.parse
import requests
from io import StringIO

#GitHub username
username = "maximinio"
#Personal Access Token (PAO)
token = "3b2bc6c745bd96682a139e46ee27922df7e1dcd6"
#creates a re-usable session object with your creds in-built
github_session = requests.Session()
github_session.auth = (username, token)

#function for downloading and importing in pandas df
def download_from_github(file_url):
	file_url = "https://raw.githubusercontent.com/Humanitas-Danese-s-omics/ibd-meta-analysis-data/main/data/" + file_url
	download = github_session.get(file_url).content
	#read the downloaded content and make a pandas dataframe
	df_downloaded_data = StringIO(download.decode('utf-8'))

	return df_downloaded_data

#default template
pio.templates.default = "simple_white"

colors = ["#A6CEE3", "#1F78B4", "#B2DF8A", "#33A02C", "#FB9A99", "#E31A1C", "#FDBF6F", "#FF7F00", "#CAB2D6", "#6A3D9A", "#B15928", "#8DD3C7", "#BEBADA", 
		"#FB8072", "#80B1D3", "#FDB462", "#B3DE69", "#FCCDE5", "#D9D9D9", "#BC80BD", "#CCEBC5", "#FFED6F", "#A6CEE3", "#1F78B4", "#B2DF8A", "#33A02C", "#FB9A99", "#E31A1C", 
		"#FDBF6F", "#FF7F00", "#CAB2D6", "#6A3D9A", "#B15928", "#8DD3C7", "#BEBADA","#FB8072", "#80B1D3", "#FDB462", "#B3DE69", "#FCCDE5", "#D9D9D9", 
		"#BC80BD", "#CCEBC5", "#FFED6F"]

#dropdown options
umap_datasets_options = [{"label": "Human", "value": "human"},
					{"label": "Archaea", "value": "archaea"},
					{"label": "Bacteria", "value": "bacteria"},
					{"label": "Eukaryota", "value": "eukaryota"},
					{"label": "Viruses", "value": "viruses"}]

#dropdown options
expression_datasets_options = [{"label": "Human", "value": "human"},
					{"label": "Archaea by order", "value": "archaea_order"},
					{"label": "Archaea by family", "value": "archaea_family"},
					{"label": "Archaea by species", "value": "archaea_species"},
					{"label": "Bacteria by order", "value": "bacteria_order"},
					{"label": "Bacteria by family", "value": "bacteria_family"},
					{"label": "Bacteria by species", "value": "bacteria_species"},
					{"label": "Eukaryota by order", "value": "eukaryota_order"},
					{"label": "Eukaryota by family", "value": "eukaryota_family"},
					{"label": "Eukaryota by species", "value": "eukaryota_species"},
					{"label": "Viruses by order", "value": "viruses_order"},
					{"label": "Viruses by family", "value": "viruses_family"},
					{"label": "Viruses by species", "value": "viruses_species"}]

metadata_umap_options = [{"label": "Condition", "value": "condition"},
						{"label": "Group", "value": "group"},
						{"label": "Tissue", "value": "tissue"},
						{"label": "Source", "value": "source"},
						{"label": "Library strategy", "value": "library_strategy"}]

padj_options = [{"label": "0.1", "value": 0.1},
				{"label": "0.01", "value": 0.01},
				{"label": "1e-03", "value": 0.001},
				{"label": "1e-04", "value": 0.0001},
				{"label": "1e-05", "value": 0.00001},
				{"label": "1e-06", "value": 0.000001},
				{"label": "1e-07", "value": 0.0000001},
				{"label": "1e-08", "value": 0.00000001},
				{"label": "1e-09", "value": 0.000000001},
				{"label": "1e-10", "value": 0.0000000001}]

dataset_stats = download_from_github("stats.tsv")
dataset_stats = pd.read_csv(dataset_stats, sep="\t")
labels = download_from_github("labels_list.tsv")
labels = pd.read_csv(labels, sep = "\t", header=None, names=["labels"])
labels = labels["labels"].dropna().tolist()
labels = [label.replace("_", " ") for label in labels]

snakey_fig = go.Figure(data=[go.Sankey(
	node = dict(
		pad = 15,
		thickness = 20,
		line = dict(color = "black", width = 0.5),
		label = labels,
		color = colors,
		hoverinfo = "none"
	),
	link = dict(
		source = dataset_stats["source"],
		target = dataset_stats["target"],
		value = dataset_stats["n"]
	)
)])
snakey_fig.update_layout(margin=dict(l=0, r=0, t=20, b=20))

#external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

VALID_USERNAME_PASSWORD_PAIRS = {
	"danese": "steam"
}

#layout
app = dash.Dash(__name__, title="IBD TaMMA", external_stylesheets=[dbc.themes.MINTY])
server = app.server
auth = dash_auth.BasicAuth(
	app,
	VALID_USERNAME_PASSWORD_PAIRS
)

#styles for tabs and selected tabs
tab_style = {
	"padding": 6, 
	"backgroundColor": "#FAFAFA"
}

tab_selected_style = {
    "padding": 6
}

#google analytics tag
app.index_string = '''
	<!DOCTYPE html>
	<html>
		<head>
			<!-- Global site tag (gtag.js) - Google Analytics -->
			<script async src="https://www.googletagmanager.com/gtag/js?id=G-HL81GG80X2"></script>
			<script>
				window.dataLayer = window.dataLayer || [];
				function gtag(){dataLayer.push(arguments);}
				gtag('js', new Date());

				gtag('config', 'G-HL81GG80X2');
			</script>
			{%metas%}
			<title>{%title%}</title>
			{%favicon%}
			{%css%}
		</head>
		<body>
			<div></div>
			{%app_entry%}
			<footer>
				{%config%}
				{%scripts%}
				{%renderer%}
			</footer>
			<div></div>
		</body>
	</html>
'''

app.layout = html.Div([
				
				html.Div([
					#logo
					html.Div([
						html.Img(src="assets/logo.png", alt="logo", style={"width": "70%", "height": "70%"}, title="Tamma means talking drum in West Africa, where it’s also known as dundun. It is a small drum, played with a curved stick and having a membrane stretched over one end or both ends of a narrow-waisted wooden frame by cords whose tension can be manually altered to vary the drum's tonality as it is played. This image has been designed using resources from Flaticon.com."
						),
					]),

					#main content
					html.Div([
						#menù
						html.Div([html.Img(src="assets/menu.png", alt="menu", style={"width": "100%", "height": "100%"})
						], style = {"width": "100%", "display": "inline-block"}),

						#general options dropdowns
						html.Div([
							#umap dataset dropdown
							html.Div([ 
								html.Label("UMAP dataset:"),
								dcc.Dropdown(
									id="umap_dataset_dropdown",
									options=umap_datasets_options,
									value="human",
									clearable=False
								) 
							], style={"width": "10%", "display": "inline-block"}),
							
							#metadata dropdown
							html.Div([
								html.Label("Metadata:"),
								dcc.Dropdown(
									id="metadata_dropdown",
									options=metadata_umap_options,
									value="condition",
									clearable=False
								)
							], style={"width": "10%", "display": "inline-block"}),
							
							#expression dataset dropdown
							html.Div([
								html.Label(children = "Expression dataset:"),
								dcc.Dropdown(
									id="expression_dataset_dropdown",
									clearable=False,
									options=expression_datasets_options,
									value="human"
								)
							], style={"width": "10%", "display": "inline-block"}),

							#gene/specie dropdown
							html.Div([
								html.Label(id = "gene_species_label", children = "Loading..."),
								dcc.Dropdown(
									id="gene_species_dropdown",
									clearable=False
								)
							], style={"width": "20%", "display": "inline-block"}),
							
							#tissue filter for contrast dropdown
							html.Div([
								html.Label("Tissue filter:"),
								dcc.Dropdown(
									id="tissue_filter_dropdown",
									clearable=False
								)
							], style={"width": "10%", "display": "inline-block"}),

							#contrast dropdown
							html.Div([
								html.Label("Comparison:"),
								dcc.Dropdown(
									id="contrast_dropdown",
									clearable=False
								)
							], style={"width": "30%", "display": "inline-block"}),

							#stringecy dropdown
							html.Div([
								html.Label("FDR:"),
								dcc.Dropdown(
									id="stringency_dropdown",
									options=padj_options,
									clearable=False
									)
							], style={"width": "8%", "display": "inline-block"}),
						], style={"width": "100%", "textAlign": "center", "font-size": "12px"}
						),

						#UMAP switches and info
						html.Div([
							html.Br(),
							html.Div([
								#info umap metadata
								html.Div([
									html.Img(src="assets/info.png", alt="info", id="info_umap_metadata", style={"width": "15%", "height": "15%"}),
									dbc.Tooltip(
										children=[dcc.Markdown(
											"""
											Low-dimensional embedding of high-dimensional data (e.g., 55k genes in the human transcriptome)  
											by Uniform Manifold Approximation and Projection (UMAP).  
											
											Click the ___legend___ to choose which group you want to display.  
											Click the ___UMAP dataset___ dropdown to change multidimensional scaling.  
											Click the ___Metadata___ dropdown to change sample colors.  
											Click the ___Comparison only___ button to display only the samples from the two comparisons.
											""")
										],
										target="info_umap_metadata",
										style={"font-family": "arial", "font-size": 14}
									),
								], style={"width": "20%", "display": "inline-block", "vertical-align": "middle"}),
								#contrast only switch
								html.Div([
									daq.BooleanSwitch(id = "contrast_only_umap_metadata_switch", on = False, color = "#33A02C", label = "Comparison only")
								], style={"width": "20%", "display": "inline-block", "vertical-align": "middle"}),
								#hide unselected metadata switch
								html.Div([
									daq.BooleanSwitch(id = "hide_unselected_metadata_switch", on = False, color = "#33A02C", label = "Hide unselected")
								], style={"width": "20%", "display": "inline-block", "vertical-align": "middle"})
							], style={"width": "50%", "display": "inline-block"}),
							
							#info umap expression
							html.Div([
								html.Img(src="assets/info.png", alt="info", id="info_umap_expression", style={"width": "3%", "height": "3%"}),
								dbc.Tooltip(
									children=[dcc.Markdown(
										"""
										Low-dimensional embedding of high-dimensional data (e.g., 55k genes in the human transcriptome)  
										by Uniform Manifold Approximation and Projection (UMAP).  
										
										Click the ___Host gene___ / ___Species___ / ___Family___ / ___Order___ dropdown to change the expression/abundance profile.
										""")
									],
									target="info_umap_expression",
									style={"font-family": "arial", "font-size": 14}
								),
							], style={"width": "50%", "display": "inline-block", "vertical-align": "middle"}),
						], style={"width":"100%"}),

						#UMAP metadata plot 
						html.Div([
							dcc.Loading(
								id = "loading_umap_metadata",
								children = dcc.Graph(id="umap_metadata", style={"height": 600}),
								type = "dot",
								color = "#33A02C"
							)
						], style={"width": "47%", "height": 600, "display": "inline-block"}),

						#UMAP expression plot
						html.Div([
							dcc.Loading(
								id = "loading_umap_expression",
								children = dcc.Graph(id="umap_expression", style={"height": 535}),
								type = "dot",
								color = "#33A02C"
							)
						], style={"width": "53%", "height": 600, "display": "inline-block"}),

						#boxplots + MA-plot + go plot
						html.Div([
							#boxplots + MA-plot
							html.Div([
								#control switch and info boxplots
								html.Div([

									#info boxplots
									html.Div([
										html.Img(src="assets/info.png", alt="info", id="info_boxplots", style={"width": "12%", "height": "12%"}),
										dbc.Tooltip(
											children=[dcc.Markdown(
												"""
												Box plots showing host gene/species/family/order expression/abundance in the different groups.
												
												Click the ___UMAP legend___ to choose which group you want to display.  
												Click the ___Comparison only___ button to display only the samples from the two comparisons.
												""")
											],
											target="info_boxplots",
											style={"font-family": "arial", "font-size": 14}
										),
									], style={"width": "30%", "display": "inline-block", "vertical-align": "middle"}),

									html.Div([
										daq.BooleanSwitch(id = "contrast_only_boxplots_switch", on = False, color = "#33A02C", label = "Comparison only"),
									], style={"width": "30%", "display": "inline-block", "textAlign": "left", "vertical-align": "middle"})
								], style={"width": "100%", "display": "inline-block", "text-align":"center"}),

								#boxplots 
								html.Div([
									html.Br(),
									dcc.Loading(
										id = "loading_boxplots",
										children = dcc.Graph(id="boxplots_graph", style={"height": 400}),
										type = "dot",
										color = "#33A02C"
									),
									html.Br()
								], style={"width": "100%", "display": "inline-block"}),

								#info and download button MA-plot
								html.Div([
									#info
									html.Div([
										html.Img(src="assets/info.png", alt="info", id="info_ma_plot", style={"width": "12%", "height": "12%"}),
										dbc.Tooltip(
											children=[dcc.Markdown(
												"""
												Differential expression/abundance visualization by MA plot,  
												with gene/species/family/order dispersion in accordance with the fold changes  
												between conditions and their average expression/abundance.
												
												Click on the ___Show gene stats___ to display its statistics.  
												Click inside the plot to change statistics of interest.
												""")
											],
											target="info_ma_plot",
											style={"font-family": "arial", "font-size": 14}
										),
									], style={"width": "30%", "display": "inline-block", "vertical-align": "middle"}),
									
									#download button
									html.Div([
										dcc.Loading(
											id = "loading_download_diffexp",
											type = "circle",
											color = "#33A02C",
											children=[html.A(
												id="download_diffexp",
												href="",
												target="_blank",
												children = [html.Button("Download full table", id="download_diffexp_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)"})],
												)
											]
										)
									], style={"width": "30%", "display": "inline-block", "textAlign": "center", "vertical-align": "middle", 'color': 'black'}),
								], style={"width": "100%", "display": "inline-block", "text-align":"center"}),

								#MA-plot
								html.Div([
									dcc.Loading(
										id = "loading_ma_plot",
										children = dcc.Graph(id="ma_plot_graph", style={"height": 359}),
										type = "dot",
										color = "#33A02C"
									)
								], style={"width": "100%", "display": "inline-block"}),
							], style={"width": "40%", "display": "inline-block"}),

							#go plot
							html.Div([
								
								#info and search bar
								html.Div([
									#info
									html.Div([
										html.Img(src="assets/info.png", alt="info", id="info_go_plot", style={"width": "16%", "height": "16%"}),
										dbc.Tooltip(
											children=[dcc.Markdown(
												"""
												Balloon plot showing the top 15 up and top 15 down differentially enriched gene ontology biological processes 
												between the two conditions (differential gene expression FDR<1e-10), unless filtered otherwise.

												Click on the ___Comparison___ dropdown to change the results.
												""")
											],
											target="info_go_plot",
											style={"font-family": "arial", "font-size": 14}
										),
									], style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "textAlign": "right",}),
									
									#search bar
									html.Div([
										dcc.Input(id="go_plot_filter_input", type="search", placeholder="Type here to filter GO gene sets", size="30", debounce=True),
									], style={"width": "35%", "display": "inline-block", "font-size": "12px", "vertical-align": "middle"})
								], style={"width": "100%", "display": "inline-block", "vertical-align": "middle", "text-align": "right"}),

								#plot
								dcc.Loading(
									id = "loading_go_plot",
									children = dcc.Graph(id="go_plot_graph", style={"height": 900}),
									type = "dot",
									color = "#33A02C", 
								),
							], style={"width": "60%", "display": "inline-block", "vertical-align": "top"}),
						], style = {"width": "100%", "height": 1000, "display": "inline-block"}),
					]),

					#content
					dcc.Tabs(id="site_tabs", value="boxplots_tab", children=[
						#summary tab
						dcc.Tab(label="Summary", value="summary_tab", children =[
								html.Br(),
								#graphical abstract
								html.Div([html.Img(src="assets/workflow.png", alt="graphical_abstract", style={"width": "40%", "height": "40%"}, title="FASTQ reads from 3,853 RNA-Seq data from different tissues, namely ileum, colon, rectum, mesenteric adipose tissue, peripheral blood, and stools, were mined from NCBI GEO/SRA and passed the initial quality filter. All files were mapped to the human reference genome and initial gene quantification was performed. Since these data came from 26 different studies made in different laboratories, we counteract the presumptive bias through a batch correction in accordance with source and tissue of origin. Once the gene counts were adjusted, samples were divided into groups in accordance with the tissue of origin and patient condition prior to differential expression analysis and gene ontology functional enrichment. Finally, the reads failing to map to the human genome were subjected to metatranscriptomics profiling by taxonomic classification using exact k-mer matching either archaeal, bacterial, eukaryotic, or viral genes. This image has been designed using resources from https://streamlineicons.com")
								], style={"width": "100%", "display": "inline-block"}),

								#statistics
								html.Div([
									dcc.Graph(id="snakey", figure=snakey_fig, config={"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "width": 1000, "height": 400, "scale": 20, "filename": "easter_egg_TBD"}})
								], style={"width": "100%", "display": "inline-block"})
						], style=tab_style, selected_style=tab_selected_style),
						#go table tab
						dcc.Tab(label="GO table", value="go_table_tab", children=[
								html.Br(),
								
								#info go table
								html.Div([
									html.Img(src="assets/info.png", alt="info", id="info_go_table", style={"width": "3%", "height": "3%"}),
									dbc.Tooltip(
										children=[dcc.Markdown(
											"""
											Table showing the complete list of the differentially enriched gene ontology biological processes between the two conditions, unless filtered otherwise.  
												
											Click on headers to reorder the table.  
											Click on a GO dataset name to see its specifics in the AmiGO 2 web resource (___Ashburner et al. 2000, PMID 10802651___)
											""")
										],
										target="info_go_table",
										style={"font-family": "arial", "font-size": 14}
									),
								], style={"width": "50%", "display": "inline-block", "vertical-align": "middle", "textAlign": "center"}),

								#download button
								html.Div([
									dcc.Loading(
										id = "loading_download_go",
										type = "circle",
										color = "#33A02C",
										children=[html.A(
											id="download_go",
											href="",
											target="_blank",
											children = [html.Button("Download full table", id="download_go_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)"})],
											)
										]
									)
								], style={"width": "25%", "display": "inline-block", "textAlign": "left", "vertical-align": "middle", 'color': 'black'}),

								#go table
								html.Div([
									html.Br(),
									dcc.Loading(
										id="loading_go_table",
										type="dot",
										color="#33A02C",
										children=dash_table.DataTable(
											id="go_table",
											style_cell={
												"whiteSpace": "normal",
												"height": "auto",
												"fontSize": 12, 
												"font-family": "arial",
												"textAlign": "center"
											},
											page_size=10,
											sort_action="native",
											style_header={
												"textAlign": "center"
											},
											style_cell_conditional=[
												{
													"if": {"column_id": "Genes"},
													"textAlign": "left",
													"width": "50%"
												},
												{
													"if": {"column_id": "GO biological process"},
													"textAlign": "left",
													"width": "15%"
												}
											],
											style_data_conditional=[
												{
													"if": {
														"column_id": "DGE",
														"filter_query": "{{DGE}} = {}".format("up")
													},
													"backgroundColor": "#FCBBA1"
												},
												{
													"if": {
														"column_id": "DGE",
														"filter_query": "{{DGE}} = {}".format("down")
													},
													"backgroundColor": "#D0D1E6"
												},
											],
											style_as_list_view=True
										)
									)
								], style={"width": "100%", "font-family": "arial"}),
						], style=tab_style, selected_style=tab_selected_style),
						#custom boxplots
						dcc.Tab(label="Box plots", value="boxplots_tab", children=[
							html.Br(),
							html.Div([
								#input section
								html.Div([
									
									#info + update plot button
									html.Div([
										
										#info
										html.Div([
											html.Img(src="assets/info.png", alt="info", id="info_multiboxplots", style={"width": "10%", "height": "10%"}),
											dbc.Tooltip(
												children=[dcc.Markdown(
													"""
													Box plots showing host gene/species/family/order expression/abundance in the different groups.
													
													Click the ___UMAP legend___ to choose which group you want to display.  
													Click the ___Comparison only___ button to display only the samples from the two comparisons.
													""")
												],
												target="info_multiboxplots",
												style={"font-family": "arial", "font-size": 14}
											),
										], style={"width": "50%", "display": "inline-block", "vertical-align": "middle"}),
										
										#update plot button
										html.Div([
											html.Button("Update plot", id="update_multixoplot_plot_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)"}),
											#warning popup
											dbc.Popover(
												children=[
													dbc.PopoverHeader(children=["Warning!"], tag="div", style={"font-family": "arial", "font-size": 14}),
													dbc.PopoverBody(children=["Plotting more than 10 elements is not allowed."], style={"font-family": "arial", "font-size": 12})
												],
												id="popover_plot_multiboxplots",
												target="update_multixoplot_plot_button",
												is_open=False,
												style={"font-family": "arial"}
											),
										], style={"width": "50%", "display": "inline-block", "vertical-align": "middle"}),
									]),
									
									html.Br(),

									#dropdown
									dcc.Dropdown(id="gene_species_multi_boxplots_dropdown", multi=True, placeholder="Select genes", style={"textAlign": "left", "font-size": "12px"}),

									html.Br(),

									#text area
									dcc.Textarea(id="multi_boxplots_text_area", placeholder="Paste gene list (plot allowed for max 10 genes)", style={"width": "100%", "height": 300, "resize": "none", "font-size": "12px"}),

									html.Br(),

									#search button
									html.Button("Search genes", id="multi_boxplots_search_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)"}),

									html.Br(),

									#genes not found area
									html.Div(id="genes_not_found_multi_boxplots_div", children=[], hidden=True, style={"font-size": "12px", "text-align": "center"})
								], style={"width": "30%", "display": "inline-block", "vertical-align": "top"}),

								#graph
								html.Div(children=[
									dcc.Loading(
										id="multi_boxplots_graph_div", 
										children = [],
										type = "dot",
										color = "#33A02C"
								)], style={"height": 600, "width": "70%", "display": "inline-block"})
							], style={"height": 600})

						], style=tab_style, selected_style=tab_selected_style),
					], style= {"height": 40}),

				], style={"width": 1200}),

			], style={"width": "100%", "justify-content":"center", "display":"flex", "textAlign": "center"})

### DOWNLOAD CALLBACKS ###

#download diffexp
@app.callback(
	Output("download_diffexp", "href"),
	Output("download_diffexp", "download"),
	Input("download_diffexp_button", "n_clicks"),
	Input("expression_dataset_dropdown", "value"),
	Input("contrast_dropdown", "value")
)
def downlaod_diffexp_table(button_click, dataset, contrast):

	#download from GitHub
	url = "dge/{}/{}.diffexp.tsv".format(dataset, contrast)
	#read the downloaded content and make a pandas dataframe
	df = download_from_github(url)
	df = pd.read_csv(df, sep="\t")
	#create a downloadable tsv file forced to excel by extension
	link = df.to_csv(index=False, encoding="utf-8", sep="\t")
	link = "data:text/tsv;charset=utf-8," + urllib.parse.quote(link)
	file_name = "DGE_{}_{}.xls".format(dataset, contrast)

	return link, file_name

#download go
@app.callback(
	Output("download_go", "href"),
	Output("download_go", "download"),
	Input("download_go", "n_clicks"),
	Input("contrast_dropdown", "value")
)
def download_go_table(button_click, contrast):

	#download from GitHub
	url = "go/{}.merged_go.tsv".format(contrast)
	df = download_from_github(url)
	df = pd.read_csv(df, sep="\t")
	link = df.to_csv(index=False, encoding="utf-8", sep="\t")
	link = "data:text/tsv;charset=utf-8," + urllib.parse.quote(link)
	file_name = "GO_human_{}.xls".format(contrast)

	return link, file_name

### ELEMENTS CALLBACKS ###

#gene/species dropdowns
@app.callback(
	#gene species dropdown
	Output("gene_species_label", "children"),
	Output("gene_species_dropdown", "options"),
	Output("gene_species_dropdown", "value"),
	Output("gene_species_multi_boxplots_dropdown", "options"),
	#stringency
	Output("stringency_dropdown", "value"),
	#inputs
	Input("expression_dataset_dropdown", "value"),
	Input("ma_plot_graph", "clickData"),
	State("gene_species_dropdown", "options"),
)
def find_genes_or_species(dataset, selected_point_ma_plot, current_dropdown_options):
	#define contexts
	ctx = dash.callback_context
	trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

	#initial run: load all dataset
	if trigger_id == "":
		trigger_id = "expression_dataset_dropdown"

	#dropdown label depends on selected dataset
	if dataset == "human":
		label = "Host gene:"
		stringency = 0.0000000001
	elif dataset != "human":
		label = dataset.split("_")[1]
		label = label.capitalize() + ":"
		stringency = 0.1

	#if you click a gene, update only the dropdown value and keep the rest as it is
	if trigger_id == "ma_plot_graph":
		value = selected_point_ma_plot["points"][0]["customdata"][0].replace(" ", "_")
		options = current_dropdown_options
	#if you change the datast, load it and change options and values
	elif trigger_id == "expression_dataset_dropdown":
		if dataset == "human":
			genes = download_from_github("genes_list.tsv")
			genes = pd.read_csv(genes, sep = "\t", header=None, names=["genes"])
			genes = genes["genes"].dropna().tolist()
			options=[{"label": i, "value": i} for i in genes]
			value="TNF"
		else:
			species = download_from_github("{}_list.tsv".format(dataset))
			species = pd.read_csv(species, sep = "\t", header=None, names=["species"])
			species = species["species"].dropna().tolist()
			options = [{"label": i.replace("_", " ").replace("[", "").replace("]", ""), "value": i} for i in species]
			value = species[0]

	return label, options, value, options, stringency

#tissue filter callback
@app.callback(
	Output("tissue_filter_dropdown", "options"),
	Output("tissue_filter_dropdown", "value"),
	Input("expression_dataset_dropdown", "value")
)
def get_tissues_with_2_or_more_conditions(dataset):
	#get all contrasts for dataset
	contrasts = download_from_github("dge_list_{}.tsv".format(dataset))
	contrasts = pd.read_csv(contrasts, sep = "\t", header=None, names=["contrast"])
	contrasts = contrasts["contrast"].tolist()
	#get all tissues for dataset
	tissues = download_from_github("umap_{}.tsv".format(dataset.split("_")[0]))
	tissues = pd.read_csv(tissues, sep = "\t")
	tissues = tissues["tissue"].unique().tolist()

	#loop over tissues and contrasts
	filtered_tissues = []
	for contrast in contrasts:
		#define the two tiessues in the contrast
		re_result = re.search(r"(\w+)_\w+-vs-(\w+)_\w+", contrast)
		tissue_1 = re_result.group(1)
		tissue_2 = re_result.group(2)
		for tissue in tissues:
			#check if they are the same
			if tissue == tissue_1 and tissue == tissue_2:
				if tissue not in filtered_tissues:
					filtered_tissues.append(tissue)

	#define default value and options
	default_value_tissue = "All"
	tissues_options = [{"label": i.replace("_", " "), "value": i} for i in ["All"] + filtered_tissues]

	return tissues_options, default_value_tissue

#contrast callback
@app.callback(
	Output("contrast_dropdown", "options"),
	Output("contrast_dropdown", "value"),
	Input("expression_dataset_dropdown", "value"),
	Input("tissue_filter_dropdown", "value")
)
def filter_contrasts(dataset, tissue):
	#get all contrasts for selected dataset
	contrasts = download_from_github("dge_list_{}.tsv".format(dataset))
	contrasts = pd.read_csv(contrasts, sep = "\t", header=None, names=["contrast"])
	contrasts = contrasts["contrast"].dropna().tolist()

	#if all, then do not filter
	if tissue == "All":
		filtered_contrasts = contrasts
	else:
		filtered_contrasts = []
		for contrast in contrasts:
			#define the two tiessues in the contrast
			re_result = re.search(r"(\w+)_\w+-vs-(\w+)_\w+", contrast)
			tissue_1 = re_result.group(1)
			tissue_2 = re_result.group(2)
			#check if they are the same
			if tissue == tissue_1 and tissue == tissue_2:
				filtered_contrasts.append(contrast)
		
	if "Ileum_CD-vs-Ileum_Control" in filtered_contrasts:
		default_contrast_value = "Ileum_CD-vs-Ileum_Control"
	else:
		default_contrast_value = filtered_contrasts[0]
	contrasts = [{"label": i.replace("_", " ").replace("-", " "), "value": i} for i in filtered_contrasts]

	return contrasts, default_contrast_value 

#go_table
@app.callback(
	Output("go_table", "columns"),
	Output("go_table", "data"),
	Input("contrast_dropdown", "value"),
	Input("go_plot_filter_input", "value")
)
def display_go_table(contrast, search_value):
	go_df = download_from_github("go/{}.merged_go.tsv".format(contrast))
	go_df = pd.read_csv(go_df, sep="\t")
	go_df = go_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]

	#define search query if present
	if search_value is not None and search_value != "":
		if search_value.endswith(" "):
			search_value = search_value.rstrip()
		search_query = re.split(r"[\s\-/,_]+", search_value)
		search_query = [x.lower() for x in search_query]

		#search keyword in processes
		processes_to_keep = []
		for process in go_df["Process~name"]:
			#force lowecase
			process_lower = process.lower()
			#check each keyword
			for x in search_query:
				#if it is a GO id, search for GO id
				if x.startswith("go:"):
					go_id = process_lower.split("~")[0]
					if x == go_id:
						if process not in processes_to_keep:
							processes_to_keep.append(process)
				#else, just search in the name og the GO category
				else:
					if x in process_lower.split("~")[1]:
						processes_to_keep.append(process)
						if process not in processes_to_keep:
							processes_to_keep.append(process)

		#filtering
		go_df = go_df[go_df["Process~name"].isin(processes_to_keep)]

	go_df["Process~name"] = ["[{}](".format(process) + str("http://amigo.geneontology.org/amigo/term/") + process.split("~")[0] + ")" for process in go_df["Process~name"]]
	go_df = go_df.rename(columns={"Process~name": "GO biological process", "num_of_Genes": "DEGs", "gene_group": "Dataset genes", "percentage%": "Enrichment"})
	columns = [
		{"name": "DGE", "id":"DGE"}, 
		{"name": "Genes", "id":"Genes"},
		{"name": "GO biological process", "id":"GO biological process", "type": "text", "presentation": "markdown"},
		{"name": "DEGs", "id":"DEGs"},
		{"name": "Dataset genes", "id":"Dataset genes"},
		{"name": "Enrichment", "id":"Enrichment", "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed)},
		{"name": "P-value", "id":"P-value", "type": "numeric", "format": Format(precision=1, scheme=Scheme.exponent)}
		]
	data = go_df.to_dict("records")

	return (columns, data)

#search genes for multi boxplots
@app.callback(
	Output("gene_species_multi_boxplots_dropdown", "value"),
	Output("genes_not_found_multi_boxplots_div", "children"),
	Output("genes_not_found_multi_boxplots_div", "hidden"),
	Input("multi_boxplots_search_button", "n_clicks"),
	State("multi_boxplots_text_area", "value"),
	State("gene_species_multi_boxplots_dropdown", "value"),
	State("expression_dataset_dropdown", "value"),
	State("genes_not_found_multi_boxplots_div", "hidden"),
	prevent_initial_call=True
)
def serach_genes_in_text_area(n_clicks, text, already_selected_genes_species, expression_dataset, log_hidden_status):
	#text is none, do almost anything
	if text is None:
		log_div = [html.Br(), "No genes in the search area!"]
		log_hidden_status = False
	else:
		genes_species_not_found = []
		#human dataset
		if expression_dataset == "human":
			#get all genes
			all_genes = download_from_github("genes_list.tsv")
			all_genes = pd.read_csv(all_genes, sep = "\t", header=None, names=["genes"])
			all_genes = all_genes["genes"].dropna().tolist()
			#search genes in text
			genes_species_in_text_area = re.split(r"[\s,;]+", text)
			#remove last gene if empty
			if genes_species_in_text_area[-1] == "":
				genes_species_in_text_area = genes_species_in_text_area[0:-1]
			
			#parse gene
			for gene in genes_species_in_text_area:
				gene = gene.upper()
				#gene existing but not in selected: add it to selected
				if gene in all_genes:
					if already_selected_genes_species is None:
						already_selected_genes_species = [gene]
					elif gene not in already_selected_genes_species:
						already_selected_genes_species.append(gene)
				#gene not existing
				elif gene not in all_genes:
					genes_species_not_found.append(gene)
	
		#log for genes not found
		if len(genes_species_not_found) > 0:
			log_div_string = ", ".join(genes_species_not_found)
			log_div = [html.Br(), "Can't find the following genes:", html.Br(), log_div_string]
			log_hidden_status = False
		#hide div if all genes has been found
		else:
			log_div = []
			log_hidden_status = True

	return already_selected_genes_species, log_div, log_hidden_status

### PLOTS ###

#plot umap callback
@app.callback(
	#umaps
	Output("umap_metadata", "figure"),
	Output("umap_expression", "figure"),
	#contrast only
	Output("metadata_dropdown", "value"),
	Output("contrast_only_umap_metadata_switch", "on"),
	Output("contrast_only_boxplots_switch", "on"),
	#config
	Output("umap_metadata", "config"),
	Output("umap_expression", "config"),
	#dropdowns
	Input("umap_dataset_dropdown", "value"),
	Input("metadata_dropdown", "value"),
	Input("expression_dataset_dropdown", "value"),
	Input("gene_species_dropdown", "value"),
	Input("contrast_dropdown", "value"),
	#zoom
	Input("umap_metadata", "relayoutData"),
	Input("umap_expression", "relayoutData"),
	#contrast only and legend click
	Input("contrast_only_umap_metadata_switch", "on"),
	Input("contrast_only_boxplots_switch", "on"),
	Input("hide_unselected_metadata_switch", "on"),
	Input("umap_metadata", "restyleData"),
	#states
	State("umap_metadata", "figure"),
	State("umap_expression", "figure")
)
def plot_umaps(umap_dataset, metadata, expression_dataset, gene_species, contrast, zoom_metadata, zoom_expression, contrast_switch_umap, contrast_switch_boxplot, hide_unselected_switch, metadata_legend_click, umap_metadata_fig, umap_expression_fig):
	#define contexts
	ctx = dash.callback_context
	trigger_id = ctx.triggered[0]["prop_id"]

	#if one switch is changed, then update the other
	if trigger_id == "contrast_only_umap_metadata_switch.on":
		contrast_switch = contrast_switch_umap
		contrast_switch_boxplot = contrast_switch_umap
	elif trigger_id == "contrast_only_boxplots_switch.on":
		contrast_switch = contrast_switch_boxplot
		contrast_switch_umap = contrast_switch_boxplot
	#else just take its value form one of the two
	else:
		contrast_switch = contrast_switch_umap

	#changing metadata with something else then "condition" will switch off the switch; clicking umap metadata legend will have the same result
	if trigger_id == "metadata_dropdown.value" and contrast_switch is True and metadata != "condition" or trigger_id == "umap_metadata.restyleData":
		contrast_switch = False
		contrast_switch_umap = False
		contrast_switch_boxplot = False

	#function for zoom synchronization
	def synchronize_zoom(umap_to_update, reference_umap):
		umap_to_update["layout"]["xaxis"]["range"] = reference_umap["layout"]["xaxis"]["range"]
		umap_to_update["layout"]["yaxis"]["range"] = reference_umap["layout"]["yaxis"]["range"]
		umap_to_update["layout"]["xaxis"]["autorange"] = reference_umap["layout"]["xaxis"]["autorange"]
		umap_to_update["layout"]["yaxis"]["autorange"] = reference_umap["layout"]["yaxis"]["autorange"]

		return umap_to_update

	##### UMAP METADATA #####

	#function for creating umap_metadata_fig from tsv file
	def plot_umap_metadata(dataset, selected_metadata):
		#open tsv
		umap_df = download_from_github("umap_{}.tsv".format(dataset.split("_")[0]))
		umap_df = pd.read_csv(umap_df, sep = "\t")

		#prepare df
		umap_df = umap_df.sort_values(by=[selected_metadata])
		umap_df[selected_metadata] = [i.replace("_", " ") for i in umap_df[selected_metadata]]
		label_to_value = {"sample": "Sample", "group": "Group", "tissue": "Tissue", "source": "Source", "library_strategy": "Library strategy", "condition": "Condition"}
		umap_df = umap_df.rename(columns=label_to_value)

		#create figure
		umap_metadata_fig = go.Figure()
		i = 0
		metadata_fields_ordered = umap_df[label_to_value[selected_metadata]].unique().tolist()
		metadata_fields_ordered.sort()
		hover_template = "Sample: %{customdata[0]}<br>Group: %{customdata[1]}<br>Tissue: %{customdata[2]}<br>Source: %{customdata[3]}<br>Library strategy: %{customdata[4]}<extra></extra>"
		for metadata in metadata_fields_ordered:
			filtered_umap_df = umap_df[umap_df[label_to_value[selected_metadata]] == metadata]
			custom_data = filtered_umap_df[["Sample", "Group", label_to_value[selected_metadata], "Source", "Library strategy"]]
			umap_metadata_fig.add_trace(go.Scatter(x=filtered_umap_df["UMAP1"], y=filtered_umap_df["UMAP2"], marker_opacity = 1, marker_color = colors[i], marker_size = 4, customdata = custom_data, mode="markers", legendgroup = metadata, showlegend = True, hovertemplate = hover_template, name=metadata))
			i += 1

		#add titles to axis
		umap_metadata_fig.update_layout(xaxis_title_text = "UMAP1", yaxis_title_text = "UMAP2")

		return umap_metadata_fig, umap_df

	#function to create a dataframe from umap_metadata_fig
	def parse_old_metadata_fig_to_get_its_df(umap_metadata_fig, metadata):
		label_to_value = {"sample": "Sample", "group": "Group", "tissue": "Tissue", "source": "Source", "library_strategy": "Library strategy", "condition": "Condition"}
		metadata = label_to_value[metadata]
		#parse umap metadata data
		metadata_data = {}
		metadata_data["Sample"] = []
		metadata_data["Group"] = []
		metadata_data[metadata] = []
		metadata_data["Source"] = []
		metadata_data["Library strategy"] = []
		metadata_data["UMAP1"] = []
		metadata_data["UMAP2"] = []
		#parse metadata figure data 
		for trace in umap_metadata_fig["data"]:
			for dot in trace["customdata"]:				
				#populate data
				metadata_data["Sample"].append(dot[0])
				metadata_data["Group"].append(dot[1])
				metadata_data[metadata].append(dot[2])
				metadata_data["Source"].append(dot[3])
				metadata_data["Library strategy"].append(dot[4])
			#data outside "customdata"
			metadata_data["UMAP1"].extend(trace["x"])
			metadata_data["UMAP2"].extend(trace["y"])

		#create a df from parsed data
		umap_df = pd.DataFrame(metadata_data)

		return umap_df

	#change dataset or metadata: create a new figure from tsv
	if trigger_id in ["umap_dataset_dropdown.value", "metadata_dropdown.value"] or umap_metadata_fig is None:

		#preserve old zoom
		keep_old_zoom = False
		if umap_metadata_fig is not None:
			xaxis_range = umap_metadata_fig["layout"]["xaxis"]["range"]
			yaxis_range = umap_metadata_fig["layout"]["yaxis"]["range"]
			keep_old_zoom = True
		if trigger_id in ["umap_dataset_dropdown.value", "metadata_dropdown.value"]:
			keep_old_zoom = False
			umap_metadata_fig["layout"]["xaxis"]["autorange"] = True
			umap_metadata_fig["layout"]["yaxis"]["autorange"] = True
		if trigger_id == "umap_dataset_dropdown.value":
			contrast_switch_umap = False
			contrast_switch_boxplot = False

		#create figure from tsv
		umap_metadata_fig, umap_df = plot_umap_metadata(umap_dataset, metadata)

		#add "visible" key to all the traces if not present; these will be used by umap expression and boxplots
		for trace in umap_metadata_fig["data"]:
			if trace["visible"] is None:
				trace["visible"] = True

		#apply old zoom if present
		if keep_old_zoom:
			umap_metadata_fig["layout"]["xaxis"]["range"] = xaxis_range
			umap_metadata_fig["layout"]["yaxis"]["range"] = yaxis_range
			umap_metadata_fig["layout"]["xaxis"]["autorange"] = False
			umap_metadata_fig["layout"]["yaxis"]["autorange"] = False
	
	#change umap expression means just to update the zoom
	elif trigger_id == "umap_expression.relayoutData":
		umap_metadata_fig = synchronize_zoom(umap_metadata_fig, umap_expression_fig)

	#click on contrast_only_switch. True = On, False = Off or change in contrast
	elif trigger_id in ["contrast_only_umap_metadata_switch.on", "contrast_only_boxplots_switch.on", "contrast_dropdown.value"]:
		#true means to select only sample in contrast
		if contrast_switch is True:
			#if metadfata is not "condition", umap_metadata_fig must be created from tsv by selecting condition as metadata
			if metadata != "condition":
				metadata = "condition"
				umap_metadata_fig, umap_df = plot_umap_metadata(umap_dataset, metadata)
			#if metadata is "condition" then just parse the figure to recreate the df
			else:
				umap_df = parse_old_metadata_fig_to_get_its_df(umap_metadata_fig, metadata)

			#find condition and filter visibility in umap metadata legend
			condition_1 = contrast.split("-vs-")[0].replace("_", " ")
			condition_2 = contrast.split("-vs-")[1].replace("_", " ")
			#setup "visible" only for the two conditions in contrast
			for trace in umap_metadata_fig["data"]:
				if trace["name"] in [condition_1, condition_2]:
					trace["visible"] = True
				else:
					trace["visible"] = "legendonly"

			umap_metadata_fig["layout"]["xaxis"]["autorange"] = True
			umap_metadata_fig["layout"]["yaxis"]["autorange"] = True
		else:
			umap_metadata_fig, umap_df = plot_umap_metadata(umap_dataset, metadata)
			for trace in umap_metadata_fig["data"]:
				if trace["visible"] is None:
					trace["visible"] = True

	#if you don't have to change umap_metadata_fig, just parse the old fig to get its dataframe
	else:
		umap_df = parse_old_metadata_fig_to_get_its_df(umap_metadata_fig, metadata)

	##### UMAP EXPRESSION #####

	#function for creating umap_expression_fig from tsv file
	def plot_umap_expression(umap_dataset, expression_dataset, gene_species, samples_to_keep, umap_df, selected_metadata, umap_metadata_fig):
		#labels for graph title
		if expression_dataset == "human":
			expression_or_abundance = " expression"
		else:
			expression_or_abundance = " abundance"

		if umap_dataset == "human":
			transcriptome_title = "human"
		elif umap_dataset == "archaea":
			transcriptome_title = "archaeal"
		elif umap_dataset == "bacteria":
			transcriptome_title = "bacterial"
		elif umap_dataset == "eukaryota":
			transcriptome_title = "eukaryota"
		elif umap_dataset == "viruses":
			transcriptome_title = "viral"
		
		counts = download_from_github("counts/{}/{}.tsv".format(expression_dataset.split("_")[0], gene_species))
		counts = pd.read_csv(counts, sep = "\t")
		counts = counts.rename(columns={"sample": "Sample"})

		#create custom data for hover data
		label_to_value = {"sample": "Sample", "group": "Group", "tissue": "Tissue", "source": "Source", "library_strategy": "Library strategy", "condition": "Condition"}
		custom_data = umap_df[["Sample", "Group", label_to_value[selected_metadata], "Source", "Library strategy"]]

		#add counts to umap df
		umap_df = umap_df.merge(counts, how="left", on="Sample")
		umap_df = umap_df.dropna(subset=["counts"])

		#filter samples that are not visible
		umap_df = umap_df[umap_df["Sample"].isin(samples_to_keep)]

		#add log2 counts column to df
		umap_df["Log2 expression"] = np.log2(umap_df["counts"])
		umap_df["Log2 expression"].replace(to_replace = -np.inf, value = 0, inplace=True)

		#count samples
		n_samples = len(umap_df["Sample"])

		#plot
		hover_template = "Sample: %{customdata[0]}<br>Group: %{customdata[1]}<br>Tissue: %{customdata[2]}<br>Source: %{customdata[3]}<br>Library strategy: %{customdata[4]}<br>Log2 expression: %{marker.color}<extra></extra>"
		
		umap_expression_fig = go.Figure(data=go.Scatter(x=umap_df["UMAP1"], y=umap_df["UMAP2"], marker_color=umap_df["Log2 expression"], marker_colorscale="reds", marker_showscale=True, marker_opacity=1, marker_size=4, marker_colorbar_title="Log2 {}".format(expression_or_abundance), marker_colorbar_title_side="right", marker_colorbar_title_font_size=14, mode="markers", customdata = custom_data, hovertemplate = hover_template, showlegend = False))
		
		umap_expression_fig.update_layout(title = {"text": "Sample dispersion within the " + transcriptome_title + " transcriptome multidimensional scaling<br>colored by " + gene_species.replace("_", " ").replace("[", "").replace("]", "") + expression_or_abundance + " n=" + str(n_samples), "x": 0.5, "font_size": 14}, coloraxis_colorbar_thickness=20, font_family="Arial", hoverlabel_bgcolor = "lightgrey", xaxis_automargin=True, yaxis_automargin=True, height = 535, margin=dict(t=60, b=0, l=10, r=60), xaxis_title_text="UMAP1", yaxis_title_text="UMAP2")

		#update layout umap metadata
		umap_metadata_fig["layout"]["height"] = 600
		umap_metadata_fig["layout"]["title"]["text"] = "Sample dispersion within the " + transcriptome_title + " transcriptome multidimensional scaling<br>colored by " + selected_metadata + " metadata n=" + str(n_samples)
		umap_metadata_fig["layout"]["title"]["x"] = 0.5
		umap_metadata_fig["layout"]["title"]["font"]["size"] = 14
		umap_metadata_fig["layout"]["legend"]["title"]["text"] = selected_metadata.capitalize().replace("_", " ")
		umap_metadata_fig["layout"]["legend"]["orientation"] = "h"
		umap_metadata_fig["layout"]["legend"]["xanchor"] = "center"
		umap_metadata_fig["layout"]["legend"]["x"] = 0.5
		umap_metadata_fig["layout"]["legend"]["yanchor"] = "top"
		umap_metadata_fig["layout"]["legend"]["y"] = -0.15
		umap_metadata_fig["layout"]["legend"]["itemsizing"] = "constant"
		umap_metadata_fig["layout"]["xaxis"]["automargin"] = True
		umap_metadata_fig["layout"]["yaxis"]["automargin"] = True
		umap_metadata_fig["layout"]["font"]["family"] = "Arial"
		umap_metadata_fig["layout"]["margin"] = dict(t=60, b=0, l=10, r=10)

		#umap_metadata_fig["layout"]["paper_bgcolor"]="LightSteelBlue"
		#umap_expression_fig["layout"]["paper_bgcolor"]="#E5F5F9"

		return umap_expression_fig, umap_metadata_fig

	#function to get samples to keep from visibility status in umap_metadata_fig
	def get_samples_to_keep(umap_metadata_fig):
		samples_to_keep = []
		#parse metadata figure data 
		for trace in umap_metadata_fig["data"]:
			if trace["visible"] is True:
				for dot in trace["customdata"]:
					#stores samples to keep after filtering
					samples_to_keep.append(dot[0])
		return samples_to_keep
	
	#change umap dataset, expression dataset or gene/species: create a new figure from tsv
	if trigger_id in ["umap_dataset_dropdown.value", "expression_dataset_dropdown.value", "gene_species_dropdown.value", "metadata_dropdown.value"] or umap_expression_fig is None:

		#preserve old zoom
		keep_old_zoom = False
		if umap_expression_fig is not None:
			xaxis_range = umap_expression_fig["layout"]["xaxis"]["range"]
			yaxis_range = umap_expression_fig["layout"]["yaxis"]["range"]
			keep_old_zoom = True
		if trigger_id in ["umap_dataset_dropdown.value", "metadata_dropdown.value"]:
			keep_old_zoom = False
			umap_metadata_fig["layout"]["xaxis"]["autorange"] = True
			umap_metadata_fig["layout"]["yaxis"]["autorange"] = True

		samples_to_keep = get_samples_to_keep(umap_metadata_fig)
		#create figure
		umap_expression_fig, umap_metadata_fig = plot_umap_expression(umap_dataset, expression_dataset, gene_species, samples_to_keep, umap_df, metadata, umap_metadata_fig)

		#apply old zoom if present
		if keep_old_zoom:
			umap_expression_fig["layout"]["xaxis"]["range"] = xaxis_range
			umap_expression_fig["layout"]["yaxis"]["range"] = yaxis_range
			umap_expression_fig["layout"]["xaxis"]["autorange"] = False
			umap_expression_fig["layout"]["yaxis"]["autorange"] = False
	
	#changes in umap metadata zoom and its legend
	elif trigger_id in ["umap_metadata.relayoutData", "umap_metadata.restyleData", "contrast_only_umap_metadata_switch.on", "contrast_only_boxplots_switch.on", "contrast_dropdown.value", "hide_unselected_metadata_switch.on"]:

		#select samples to filter
		if trigger_id in ["umap_metadata.restyleData", "contrast_only_umap_metadata_switch.on", "contrast_only_boxplots_switch.on", "contrast_dropdown.value", "hide_unselected_metadata_switch.on"]:
			samples_to_keep = get_samples_to_keep(umap_metadata_fig)
			#get new filtered umap_expression_fig
			umap_expression_fig, umap_metadata_fig = plot_umap_expression(umap_dataset, expression_dataset, gene_species, samples_to_keep, umap_df, metadata, umap_metadata_fig)
			
			#selected traces only if switch is true
			if hide_unselected_switch is True:
				#if legend is clicked while the hide_unselected_switch is on, then the clicked item should be hidden too
				if trigger_id == "umap_metadata.restyleData":
					trace_to_modify = metadata_legend_click[1][0]
					umap_metadata_fig["data"][trace_to_modify]["visible"] = False
				#change visibility of traces in case of click on both switches
				elif trigger_id in ["hide_unselected_metadata_switch.on", "contrast_only_umap_metadata_switch.on", "contrast_only_boxplots_switch.on", "contrast_dropdown.value"]:
					for trace in umap_metadata_fig["data"]:
						if trace["visible"] == "legendonly":
							trace["visible"] = False
			#if is false, show all traces again
			elif hide_unselected_switch is False:
				for trace in umap_metadata_fig["data"]:
					if trace["visible"] is False:
						trace["visible"] = "legendonly"

		#update zoom from metadata
		umap_expression_fig = synchronize_zoom(umap_expression_fig, umap_metadata_fig)

	##### CONFIG OPTIONS ####
	config_umap_metadata = {"doubleClick": "autosize", "modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "width": 500, "height": 500, "scale": 5}}
	config_umap_expression = {"doubleClick": "autosize", "modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "width": 520, "height": 500, "scale": 5}}

	config_umap_metadata["toImageButtonOptions"]["filename"] = "TaMMA_umap_{umap_metadata}_colored_by_{metadata}".format(umap_metadata = umap_dataset, metadata = metadata)
	config_umap_expression["toImageButtonOptions"]["filename"] = "TaMMA_umap_{umap_metadata}_colored_by_{gene_species}_{expression_abundance}".format(umap_metadata = umap_dataset, gene_species = gene_species, expression_abundance = "expression" if expression_dataset == "human" else "abundance")

	return umap_metadata_fig, umap_expression_fig, metadata, contrast_switch_umap, contrast_switch_boxplot, config_umap_metadata, config_umap_expression

#plot boxplots callback
@app.callback(
	Output("boxplots_graph", "figure"),
	Output("boxplots_graph", "config"),
	Input("expression_dataset_dropdown", "value"),
	Input("gene_species_dropdown", "value"),
	Input("metadata_dropdown", "value"),
	Input("umap_metadata", "restyleData"),
	State("boxplots_graph", "figure"),
	State("umap_metadata", "figure")
)
def plot_boxplots(expression_dataset, gene, metadata_field, umap_legend_click, boxplots_figure, umap_metadata_figure):
	#define contexts
	ctx = dash.callback_context
	trigger_id = ctx.triggered[0]["prop_id"]

	#get counts for a specific gene
	if trigger_id == "umap_metadata.restyleData":
		number_of_changes = len(umap_legend_click[1])
		traces_to_change = umap_legend_click[1]
		settings_to_apply = umap_legend_click[0]["visible"]
		for n in range(0, number_of_changes):
			boxplots_figure["data"][traces_to_change[n]]["visible"] = settings_to_apply[n]
		box_fig = boxplots_figure
	elif trigger_id in ["expression_dataset_dropdown.value", "gene_species_dropdown.value", "metadata_dropdown.value"]:
		counts = download_from_github("counts/{}/{}.tsv".format(expression_dataset.split("_")[0], gene))
		counts = pd.read_csv(counts, sep = "\t")
		#open metadata and select only the desired column
		if expression_dataset != "human":
			expression_dataset = expression_dataset.split("_")[0]
		metadata_df = download_from_github("umap_{}.tsv".format(expression_dataset))
		metadata_df = pd.read_csv(metadata_df, sep = "\t")
		#merge and compute log2 and replace inf with 0
		metadata_df = metadata_df.merge(counts, how="left", on="sample")
		metadata_df["Log2 counts"] = np.log2(metadata_df["counts"])
		metadata_df["Log2 counts"].replace(to_replace = -np.inf, value = 0, inplace=True)
		#sort by metadata and clean it
		metadata = metadata_df.sort_values(by=[metadata_field])
		metadata_df[metadata_field] = [i.replace("_", " ") for i in metadata_df[metadata_field]]

		#label for dropdown
		metadata_field_label = metadata_field.replace("_", " ")

		#create figure
		box_fig = go.Figure()
		i = 0
		metadata_fields_ordered = metadata_df[metadata_field].unique().tolist()
		metadata_fields_ordered.sort()
		for metadata in metadata_fields_ordered:
			filtered_metadata = metadata_df[metadata_df[metadata_field] == metadata]
			hovertext_labels = "Sample: " + filtered_metadata["sample"] + "<br>Group: " + filtered_metadata["group"] + "<br>Tissue: " + filtered_metadata["tissue"] + "<br>Source: " + filtered_metadata["source"] + "<br>Library strategy: " + filtered_metadata["library_strategy"]
			box_fig.add_trace(go.Box(y=filtered_metadata["Log2 counts"], name = metadata, marker_color = colors[i], boxpoints = "all", hovertext = hovertext_labels, hoverinfo = "y+text"))
			i += 1
		box_fig.update_traces(marker_size=4, showlegend=False)
		box_fig.update_layout(title = {"text": gene.replace("_", " ").replace("[", "").replace("]", "") + " expression profiles per " + metadata_field_label, "x": 0.5, "font_size": 14}, legend_title_text = metadata_field_label, yaxis_title = "Log2 expression", xaxis_automargin=True, yaxis_automargin=True, font_family="Arial", height=400, margin=dict(t=30, b=30, l=5, r=10))

	#syncronyze legend status with umap metadata
	for trace in range(0, len(umap_metadata_figure["data"])):
		box_fig["data"][trace]["visible"] = umap_metadata_figure["data"][trace]["visible"]

	#box_fig["layout"]["paper_bgcolor"] = "#BCBDDC"

	config_boxplots = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "width": 450, "height": 400, "scale": 5}}
	config_boxplots["toImageButtonOptions"]["filename"] = "TaMMA_boxplots_with_{gene_species}_expression_colored_by_{metadata}".format(gene_species = gene, metadata = metadata_field)

	return box_fig, config_boxplots

#plot MA-plot callback
@app.callback(
	Output("ma_plot_graph", "figure"),
	Output("ma_plot_graph", "config"),
	Input("expression_dataset_dropdown", "value"),
	Input("contrast_dropdown", "value"),
	Input("stringency_dropdown", "value"),
	Input("gene_species_dropdown", "value"),
	State("ma_plot_graph", "figure")
)
def plot_MA_plot(dataset, contrast, fdr, gene, old_ma_plot_figure):

	#define contexts
	ctx = dash.callback_context
	trigger_id = ctx.triggered[0]["prop_id"]

	if dataset == "human":
		gene_or_species = "Gene"
		expression_or_abundance = "gene expression"
		xaxis_title = "Log2 average expression"
	else:
		xaxis_title = "Log2 average abundance"
		gene_or_species = dataset.split("_")[1]
		expression_or_abundance = gene_or_species + " abundance"
		gene_or_species = gene_or_species.capitalize()

	gene = gene.replace("_", " ").replace("[", "").replace("]", "")

	#read tsv if change in dataset or contrast
	if trigger_id in ["expression_dataset_dropdown.value", "contrast_dropdown.value"] or old_ma_plot_figure is None:
		table = download_from_github("dge/{}/{}.diffexp.tsv".format(dataset, contrast))
		table = pd.read_csv(table, sep = "\t")
		table = table.dropna(subset=["Gene"])
		#log2 base mean
		table["log2_baseMean"] = np.log2(table["baseMean"])
		#clean gene/species name
		table["Gene"] = [i.replace("_", " ").replace("[", "").replace("]", "") for i in table["Gene"]]

	#parse existing figure for change in stringency or gene
	elif trigger_id in ["stringency_dropdown.value", "gene_species_dropdown.value"] and old_ma_plot_figure is not None:
		figure_data = {}
		figure_data["Gene"] = []
		figure_data["padj"] = []
		figure_data["log2_baseMean"] = []
		figure_data["log2FoldChange"] = []

		for trace in range(0, len(old_ma_plot_figure["data"])):
			figure_data["log2_baseMean"].extend(old_ma_plot_figure["data"][trace]["x"])
			figure_data["log2FoldChange"].extend(old_ma_plot_figure["data"][trace]["y"])
			for dot in old_ma_plot_figure["data"][trace]["customdata"]:
				figure_data["Gene"].append(dot[0])
				if dot[1] == "NA":
					dot[1] = np.nan
				figure_data["padj"].append(dot[1])
		
		table = pd.DataFrame(figure_data)

	#find DEGs
	table.loc[(table["padj"] <= fdr) & (table["log2FoldChange"] > 0), "DEG"] = "Up"
	table.loc[(table["padj"] <= fdr) & (table["log2FoldChange"] < 0), "DEG"] = "Down"
	table.loc[table["DEG"].isnull(), "DEG"] = "no_DEG"

	#replace nan values with NA
	table = table.fillna(value={"padj": "NA"})

	#count DEGs
	up = table[table["DEG"] == "Up"]
	up = len(up["Gene"])
	down = table[table["DEG"] == "Down"]
	down = len(down["Gene"])

	#find selected gene
	table.loc[table["Gene"] == gene, "DEG"] = "selected_gene"
	table["selected_gene"] = ""
	table.loc[table["Gene"] == gene, "selected_gene"] = gene

	#assign color for the selected gene
	table = table.set_index("Gene")
	selected_gene_log2fc = table.loc[gene, "log2FoldChange"]
	selected_gene_fdr = table.loc[gene, "padj"]
	selected_gene_log2_base_mean = table.loc[gene, "log2_baseMean"]
	table = table.reset_index()
	
	#assign color for marker to the selected gene
	if selected_gene_fdr != "NA":
		if selected_gene_fdr <= fdr:
			#red
			if selected_gene_log2fc > 0:
				selected_gene_marker_color = "#D7301F"
			#blue
			elif selected_gene_log2fc < 0:
				selected_gene_marker_color = "#045A8D"
		#grey
		elif selected_gene_fdr > fdr:
			selected_gene_marker_color = "#636363"
		
		#round it for annotation
		selected_gene_fdr = "{:.1e}".format(selected_gene_fdr)
	#grey
	elif selected_gene_fdr == "NA":
		selected_gene_marker_color = "#636363"

	#colors for discrete sequence
	colors = ["#636363", "#D7301F", "#045A8D", selected_gene_marker_color]
	#rename column if not human
	if dataset != "human":
		table = table.rename(columns={"Gene": gene_or_species})

	#plot
	ma_plot_fig = go.Figure()
	i = 0
	for deg_status in ["no_DEG", "Up", "Down", "selected_gene"]:
		filtered_table = table[table["DEG"] == deg_status]
		custom_data = filtered_table[[gene_or_species, "padj"]]
		hover_template = "Log2 average expression: %{x}<br>Log2 fold change: %{y}<br>" + gene_or_species + ": %{customdata[0]}<br>Padj: %{customdata[1]}<extra></extra>"
		ma_plot_fig.add_trace(go.Scattergl(x=filtered_table["log2_baseMean"], y=filtered_table["log2FoldChange"], marker_opacity = 1, marker_color = colors[i], marker_symbol = 2, marker_size = 5, customdata = custom_data, mode="markers", hovertemplate = hover_template))
		i += 1

	#title and no legend
	ma_plot_fig.update_layout(title={"text": "Differential {} FDR<".format(expression_or_abundance) + "{:.0e}".format(fdr) + "<br>" + contrast.replace("_", " ").replace("-", " ").replace("Control", "Control"), "xref": "paper", "x": 0.5, "font_size": 14}, xaxis_automargin=True, xaxis_title=xaxis_title, yaxis_automargin=True, yaxis_title="Log2 fold change", font_family="Arial", height=359, margin=dict(t=50, b=0, l=5, r=130), showlegend = False)
	#line at y=0
	ma_plot_fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=0, line=dict(color="black", width=3), xref="paper", layer="below")
	#add annotation with number of up and down degs and show selected gene text
	ma_plot_fig.add_annotation(text = str(up) + " higher in<br>" + contrast.split("-vs-")[0].replace("_", " "), align="right", xref="paper", yref="paper", x=0.98, y=0.98, showarrow=False, font_size=14, font_color="#DE2D26", font_family="Arial")
	ma_plot_fig.add_annotation(text = str(down) + " higher in<br>" + contrast.split("-vs-")[1].replace("_", " "), align="right", xref="paper", yref="paper", x=0.98, y=0.02, showarrow=False, font_size=14, font_color="#045A8D", font_family="Arial")
	ma_plot_fig.add_annotation(text = "Show gene stats", align="center", xref="paper", yref="paper", x=1.4, y=1, showarrow=False, font_size=12, font_family="Arial")

	#save annotations for button
	up_genes_annotation = [dict(text = str(up) + " higher in<br>" + contrast.split("-vs-")[0].replace("_", " "), align="right", xref="paper", yref="paper", x=0.98, y=0.98, showarrow=False, font=dict(size=14, color="#DE2D26", family="Arial"))]
	down_genes_annotation = [dict(text = str(down) + " higher in<br>" + contrast.split("-vs-")[1].replace("_", " "), align="right", xref="paper", yref="paper", x=0.98, y=0.02, showarrow=False, font=dict(size=14, color="#045A8D", family="Arial"))]
	show_gene_annotaton = [dict(text = "Show gene stats", align="center", xref="paper", yref="paper", x=1.4, y=1, showarrow=False, font_size=12)]
	selected_gene_annotation = [dict(x=ma_plot_fig["data"][3]["x"][0], y=ma_plot_fig["data"][3]["y"][0], xref="x", yref="y", text=ma_plot_fig["data"][3]["customdata"][0][0] + "<br>Log2 avg expr: " +  str(round(selected_gene_log2_base_mean, 1)) + "<br>Log2 FC: " +  str(round(selected_gene_log2fc, 1)) + "<br>FDR: " + selected_gene_fdr, showarrow=True, font=dict(family="Arial", size=12, color="#252525"), align="center", arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#525252", ax=-50, ay=-50, bordercolor="#525252", borderwidth=2, borderpad=4, bgcolor="#D9D9D9", opacity=0.7)]

	#buttons
	ma_plot_fig.update_layout(updatemenus=[
		dict(
			type="buttons",
            direction="right",
            active=1,
            x=1.42,
            y=0.9,
            buttons=list([
                dict(label="True",
                    method="update",
                    args=[
						{"marker": [{"color": colors[0], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors[1], "size": 5 , "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors[2], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": "#D9D9D9", "size": 9, "symbol": 2, "line": {"color": "#525252", "width": 2}}]},
						{"annotations": up_genes_annotation + down_genes_annotation + show_gene_annotaton + selected_gene_annotation}]
				),
				dict(label="False",
                    method="update",
                    args=[
						{"marker": [{"color": colors[0], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors[1], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors[2], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": selected_gene_marker_color, "size": 5, "symbol": 2, "line": {"color": None, "width": None}}]},
						{"annotations": up_genes_annotation + down_genes_annotation + show_gene_annotaton}]
				)
			])
		)]
	)

	config_ma_plot = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "width": 450, "height": 350, "scale": 5}, "plotGlPixelRatio": 5000}
	config_ma_plot["toImageButtonOptions"]["filename"] = "TaMMA_maplot_with_{contrast}".format(contrast = contrast)

	#ma_plot_fig["layout"]["paper_bgcolor"] = "#E0F3DB"
	
	return ma_plot_fig, config_ma_plot

#plot go plot callback
@app.callback(
	Output("go_plot_graph", "figure"),
	Output("go_plot_graph", "config"),
	Input("contrast_dropdown", "value"),
	Input("go_plot_filter_input", "value")
)
def plot_go_plot(contrast, search_value):
	#open df
	go_df = download_from_github("go/{}.merged_go.tsv".format(contrast))
	go_df = pd.read_csv(go_df, sep = "\t")
	#filter out useless columns and rename the one to keep
	go_df = go_df[["DGE", "Process~name", "P-value", "percentage%"]]
	go_df = go_df.rename(columns={"Process~name": "Process", "percentage%": "Enrichment", "P-value": "GO p-value"})
	#remove duplicate GO categories for up and down
	go_df.drop_duplicates(subset ="Process", keep = False, inplace = True)

	#define search query if present
	if search_value is not None and search_value != "":
		if search_value.endswith(" "):
			search_value = search_value.rstrip()
		search_query = re.split(r"[\s\-/,_]+", search_value)
		search_query = [x.lower() for x in search_query]

		#search keyword in processes
		processes_to_keep = []
		for process in go_df["Process"]:
			#force lowecase
			process_lower = process.lower()
			#check each keyword
			for x in search_query:
				#if it is a GO id, search for GO id
				if x.startswith("go:"):
					go_id = process_lower.split("~")[0]
					if x == go_id:
						if process not in processes_to_keep:
							processes_to_keep.append(process)
				#else, just search in the name og the GO category
				else:
					if x in process_lower.split("~")[1]:
						processes_to_keep.append(process)
						if process not in processes_to_keep:
							processes_to_keep.append(process)

		#filtering
		go_df = go_df[go_df["Process"].isin(processes_to_keep)]

	#crop too long process name
	processes = []
	for process in go_df["Process"]:
		if len(process) > 80:
			process = process[0:79] + " ..."
		processes.append(process)
	go_df["Process"] = processes

	#divide up and down GO categories
	go_df_up = go_df[go_df["DGE"] == "up"]
	go_df_down = go_df[go_df["DGE"] == "down"]

	#function to select GO categories
	def select_go_categories(df):
		#sort by pvalue
		df = df.sort_values(by=["GO p-value"])
		#take top ten
		df = df.head(15)
		#sort by enrichment
		df = df.sort_values(by=["Enrichment"])

		return df

	#apply function
	go_df_up = select_go_categories(go_df_up)
	go_df_down = select_go_categories(go_df_down)

	#function for hover text
	def create_hover_text(df):
		hover_text = []
		for index, row in df.iterrows():
			hover_text.append(('DGE: {dge}<br>' + 'Process: {process}<br>' + 'Enrichment: {enrichment}<br>' + 'GO p-value: {pvalue}').format(dge=row["DGE"], process=row['Process'], enrichment=row['Enrichment'], pvalue=row['GO p-value']))

		return hover_text

	#find out max enrichment for this dataset
	all_enrichments = go_df_up["Enrichment"].append(go_df_down["Enrichment"], ignore_index=True)
	if len(all_enrichments) > 0:
		sizeref = 2. * max(all_enrichments)/(7 ** 2)
	else:
		sizeref = None

	#compute figure height
	pixels_per_go_category = 30
	computed_height = len(all_enrichments) * pixels_per_go_category

	#min and max height
	if computed_height < 500:
		computed_height = 500
	elif computed_height > 900:
		computed_height = 900

	#relative size of colorbar to the main plot
	if computed_height < 600:
		row_span_colorbar = 3
	else:
		row_span_colorbar = 2

	#create figure
	go_plot_fig = go.Figure()
	#create subplots
	go_plot_fig = make_subplots(rows=7, cols=2, specs=[[{"rowspan": 7}, {"rowspan": 2}], [None, None], [None, None], [None, {"rowspan": row_span_colorbar}], [None, None], [None, None], [None, None]], column_widths=[0.78, 0.2], subplot_titles=(None, "GO p-value", "Enrichment"))

	#up trace
	hover_text = create_hover_text(go_df_up)
	go_plot_fig.add_trace(go.Scatter(x=go_df_up["DGE"], y=go_df_up["Process"], marker_size=go_df_up["Enrichment"], marker_opacity = 1, marker_color = go_df_up["GO p-value"], marker_colorscale=["#D7301F", "#FCBBA1"], marker_showscale=False, marker_sizeref = sizeref, marker_cmax=0.05, marker_cmin=0, mode="markers", hovertext = hover_text, hoverinfo = "text"), row = 1, col = 1)
	#down trace
	hover_text = create_hover_text(go_df_down)
	go_plot_fig.add_trace(go.Scatter(x=go_df_down["DGE"], y=go_df_down["Process"], marker_size=go_df_down["Enrichment"], marker_opacity = 1, marker_color = go_df_down["GO p-value"], marker_colorscale=["#045A8D", "#C6DBEF"], marker_showscale=False, marker_sizeref = sizeref, marker_cmax=0.05, marker_cmin=0, mode="markers", hovertext = hover_text, hoverinfo = "text"), row = 1, col = 1)

	#colorbar trace
	go_plot_fig.add_trace(go.Scatter(x = [None], y = [None], marker_showscale=True, marker_color = [0], marker_colorscale=["#737373", "#D9D9D9"], marker_cmax=0.05, marker_cmin=0, marker_colorbar = dict(thicknessmode="pixels", thickness=20, lenmode="pixels", len=(computed_height/4), y=0.86, x=0.8)), row = 1, col = 2)

	#size_legend_trace
	if len(all_enrichments) > 0:
		legend_sizes = [round(min(all_enrichments)), round(np.average([max(all_enrichments), min(all_enrichments)])), round(max(all_enrichments))]
	else:
		legend_sizes = [11, 22, 33]
	go_plot_fig.add_trace(go.Scatter(x = [1, 1, 1], y = [10, 45, 80], marker_size = legend_sizes, marker_sizeref = sizeref, marker_color = "#737373", mode="markers+text", text=["min", "mid", "max"], hoverinfo="text", hovertext=legend_sizes, textposition="top center"), row = 4, col = 2)

	#figure layout
	go_plot_fig.update_layout(title={"text": "Gene ontology enrichment plot<br>Human transcriptome DGE FDR<1e-10<br>" + contrast.replace("_", " ").replace("-", " ").replace("Control", "Control"), 
									"x": 0.5, 
									"font_size": 14}, 
								font_family="Arial",
								height=computed_height,
								showlegend=False,
								autosize=False,
								margin=dict(t=50, b=0, l=470, r=0),
								#titles
								xaxis_title = None, 
								yaxis_title = None, 
								#linecolors
								xaxis_linecolor="rgb(255,255,255)",
								yaxis_linecolor="rgb(255,255,255)",
								#fixed range for enrichment legend
								yaxis3_range=[0, 100],
								#no zoom
								xaxis_fixedrange=True, 
								xaxis2_fixedrange=True, 
								xaxis3_fixedrange=True,
								yaxis_fixedrange=True,
								yaxis2_fixedrange=True, 
								yaxis3_fixedrange=True,
								#hide axis of legends
								xaxis2_visible=False,
								xaxis3_visible=False,
								yaxis2_visible=False, 
								yaxis3_visible=False)

	#legend title dimension and position
	go_plot_fig["layout"]["annotations"][0]["font"]["size"] = 12
	go_plot_fig["layout"]["annotations"][1]["font"]["size"] = 12

	#go_plot_fig["layout"]["paper_bgcolor"] = "#FDE0DD"

	config_go_plot = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "width": 700, "height": computed_height, "scale": 5}, "responsive": True}
	config_go_plot["toImageButtonOptions"]["filename"] = "TaMMA_goplot_with_{contrast}".format(contrast = contrast)

	return go_plot_fig, config_go_plot

#multiboxplots callback
@app.callback(
	Output("multi_boxplots_graph_div", "children"),
	Output("popover_plot_multiboxplots", "is_open"),
	Input("update_multixoplot_plot_button", "n_clicks"),
	Input("metadata_dropdown", "value"),
	Input("umap_metadata", "restyleData"),
	State("gene_species_multi_boxplots_dropdown", "value"),
	State("expression_dataset_dropdown", "value"),
	State("umap_metadata", "figure")
)
def plot_multiboxplots(n_clicks, metadata_field, umap_metadata_legend_click, selected_genes_species, expression_dataset, metadata_fig):
	#define contexts
	ctx = dash.callback_context
	trigger_id = ctx.triggered[0]["prop_id"]

	#empty dropdown
	if selected_genes_species is None or selected_genes_species == []:
		div_content = []
		popover_status = False
	#filled dropdown
	else:
		#up to 10 elements to plot
		if len(selected_genes_species) < 11:

			#create figure
			box_fig = go.Figure()
			
			#define number of rows
			if (len(selected_genes_species) % 2) == 0:
				n_rows = len(selected_genes_species)/2
			else:
				n_rows = int(len(selected_genes_species)/2) + 1
			n_rows = int(n_rows)

			#vertical spacing
			if n_rows > 3:
				vertical_spacing = 0.04
			elif n_rows == 3:
				vertical_spacing = 0.07
			elif n_rows < 3:
				vertical_spacing = 0.1
			
			#define specs for subplot
			specs = []
			for i in range(0, n_rows):
				specs.append([{}, {}])
			#in case of odd number of selected elements, the last plot in grid is None
			if (len(selected_genes_species) % 2) != 0:
				specs[-1][-1] = None

			#make subplots
			box_fig = make_subplots(rows=n_rows, cols=2, specs=specs, subplot_titles=[gene for gene in selected_genes_species], shared_xaxes=True, vertical_spacing=vertical_spacing, y_title="Log2 expression")

			working_row = 1
			working_col = 1
			for gene in selected_genes_species:
				counts = download_from_github("counts/{}/{}.tsv".format(expression_dataset, gene))
				counts = pd.read_csv(counts, sep = "\t")
				#open metadata and select only the desired column
				metadata_df = download_from_github("umap_{}.tsv".format(expression_dataset))
				metadata_df = pd.read_csv(metadata_df, sep = "\t")
				#merge and compute log2 and replace inf with 0
				metadata_df = metadata_df.merge(counts, how="left", on="sample")
				metadata_df["Log2 counts"] = np.log2(metadata_df["counts"])
				metadata_df["Log2 counts"].replace(to_replace = -np.inf, value = 0, inplace=True)
				#sort by metadata and clean it
				metadata = metadata_df.sort_values(by=[metadata_field])
				metadata_df[metadata_field] = [i.replace("_", " ") for i in metadata_df[metadata_field]]

				#label for dropdown
				metadata_field_label = metadata_field.replace("_", " ")

				#find out visible traces
				if trigger_id == "umap_metadata.restyleData":
					#get all traces
					all_traces = []
					colors_dict = {}
					i += 0
					for trace in metadata_fig["data"]:
						all_traces.append(trace["name"])
						colors_dict[trace["name"]] = colors[i]
						i += 1

					#identify traces to remove
					traces_to_remove = []
					#parse legend click data to get changes 
					for i in range(0, len(umap_metadata_legend_click[1])):
						status = umap_metadata_legend_click[0]["visible"][i]
						trace = umap_metadata_legend_click[1][i]
						if status is not True:
							traces_to_remove.append(all_traces[trace])
					#remove from all traces the traces to remove
					visible_traces = []
					for trace in all_traces:
						if trace not in traces_to_remove:
							visible_traces.append(trace)
				#visible traces in umap metadata legend are the one to plot
				else:
					visible_traces = []
					colors_dict = {}
					i = 0
					for trace in metadata_fig["data"]:
						if trace["visible"] is True:
							visible_traces.append(trace["name"])
						colors_dict[trace["name"]] = colors[i]
						i += 1

				#plot
				for metadata in visible_traces:
					filtered_metadata = metadata_df[metadata_df[metadata_field] == metadata]
					hovertext_labels = "Sample: " + filtered_metadata["sample"] + "<br>Group: " + filtered_metadata["group"] + "<br>Tissue: " + filtered_metadata["tissue"] + "<br>Source: " + filtered_metadata["source"] + "<br>Library strategy: " + filtered_metadata["library_strategy"]
					box_fig.add_trace(go.Box(y=filtered_metadata["Log2 counts"], name = metadata, marker_color = colors_dict[metadata], boxpoints = "all", hovertext = hovertext_labels, hoverinfo = "y+text"), row = int(working_row), col = working_col)

				#row and column count
				working_row += 0.5
				if working_col == 1:
					working_col = 2
				elif working_col == 2:
					working_col = 1

			# CIT; NDC80; AURKA; PPP1R12A; XRCC2; RGS14; ENSA; AKAP8; BUB1B; TADA3
			#update all traces markers and remove legend
			box_fig.update_traces(marker_size=4, showlegend=False)
			#compute height
			if n_rows == 1:
				height_fig = 450
			else:
				height_fig = n_rows*300
			#add title and set height
			box_fig.update_layout(height=height_fig, title = {"text": "Gene expression profiles per " + metadata_field_label, "x": 0.5, "font_size": 14}, font_family="Arial")

			#embed in html
			div_content = [
				dcc.Loading(
					children = dcc.Graph(figure=box_fig),
					type = "dot",
					color = "#33A02C"
				)
			]

			popover_status = False
		#more then 10 elements to plot
		else:
			div_content = []
			popover_status = True

	return div_content, popover_status


if __name__ == "__main__":
	import os.path

	if os.path.isfile(".vscode/settings.json"):
		app.run_server(debug=True, host = "10.39.173.120", port = "8050")
	else:
		app.run_server()
