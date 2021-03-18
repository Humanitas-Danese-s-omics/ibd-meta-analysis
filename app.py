import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
import dash_daq as daq
import dash_auth
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import re

pio.templates.default = "simple_white"

colors = ["#A6CEE3", "#1F78B4", "#B2DF8A", "#33A02C", "#FB9A99", "#E31A1C", "#FDBF6F", "#FF7F00", "#CAB2D6", "#6A3D9A", "#B15928", "#8DD3C7", "#BEBADA", 
		"#FB8072", "#80B1D3", "#FDB462", "#B3DE69", "#FCCDE5", "#D9D9D9", "#BC80BD", "#CCEBC5", "#FFED6F", "#A6CEE3", "#1F78B4", "#B2DF8A", "#33A02C", "#FB9A99", "#E31A1C", 
		"#FDBF6F", "#FF7F00", "#CAB2D6", "#6A3D9A", "#B15928", "#8DD3C7", "#BEBADA","#FB8072", "#80B1D3", "#FDB462", "#B3DE69", "#FCCDE5", "#D9D9D9", 
		"#BC80BD", "#CCEBC5", "#FFED6F"]

#dropdown options
datasets_options = [{"label": "Human", "value": "human"},
					{"label": "Archaea", "value": "archaea"},
					{"label": "Bacteria", "value": "bacteria"},
					{"label": "Eukaryota", "value": "eukaryota"},
					{"label": "Viruses", "value": "viruses"}]

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

dataset_stats = pd.read_csv("http://www.lucamassimino.com/ibd/stats.tsv", sep = "\t")
labels = pd.read_csv("http://www.lucamassimino.com/ibd/labels_list.tsv", sep = "\t", header=None, names=["labels"])
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
		value =  dataset_stats["n"]
	)
)])
snakey_fig.update_layout(margin=dict(l=0, r=0, t=20, b=20))

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

VALID_USERNAME_PASSWORD_PAIRS = {
    "danese": "steam"
}

#layout
app = dash.Dash(__name__, title="IBD meta-analisys Danese omics")
server = app.server
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
app.layout = html.Div([
				html.Div([
					#header
					html.Div([
						#logo
						html.Img(src="assets/logo.png", alt="logo", style={"width": "70%", "height": "70%"}, title="Tamma means talking drum in West Africa, where it’s also known as dundun. It is a small drum, played with a curved stick and having a membrane stretched over one end or both ends of a narrow-waisted wooden frame by cords whose tension can be manually altered to vary the drum's tonality as it is played."),
					], style={"width": "100%", "display": "inline-block"}),
					
					#graphical abstract
					html.Div([html.Img(src="assets/menu.png", alt="menu", style={"width": "100%", "height": "100%"})
					], style = {"width": "100%", "display": "inline-block"}),

					#general options dropdowns
					html.Div([
						#umap dataset dropdown
						html.Div([ 
							html.Label("UMAP dataset:"),
							dcc.Dropdown(
								id="umap_dataset_dropdown",
								options=datasets_options,
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
								value="tissue",
								clearable=False
							)
						], style={"width": "10%", "display": "inline-block"}),
						
						#expression dataset dropdown
						html.Div([
							html.Label(children = "Expression dataset:"),
							dcc.Dropdown(
								id="expression_dataset_dropdown",
								clearable=False,
								options=datasets_options,
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

					#summary info
					html.Div(id="summary", children=[html.Br(), ""], style={"width": "100%", "textAlign": "center", "font-size": "14px"}),

					#UMAP
					html.Div([
						dcc.Loading(
							id = "loading_umap_metadata",
							children = dcc.Graph(id="umap_metadata", config={"doubleClick": "autosize", "showEditInChartStudio": True, "plotlyServerURL": "https://chart-studio.plotly.com"}),
							type = "dot",
							color = "#ADDD8E"
						)
					], style={"width": "55%", "height": 425, "display": "inline-block"} 
					),

					html.Div([
						dcc.Loading(
							id = "loading_umap_expression",
							children = dcc.Graph(id="umap_expression", config={"doubleClick": "autosize", "showEditInChartStudio": True, "plotlyServerURL": "https://chart-studio.plotly.com"}),
							type = "dot",
							color = "#ADDD8E"
						)
					], style={"width": "45%", "height": 425, "display": "inline-block"}
					),
					
					#switches + MA-plot + boxplots
					html.Div([
						html.Div([
							#switches
							html.Div([
								html.Br(), html.Br(), html.Br(), html.Br(),
								daq.BooleanSwitch(id = "contrast_only_switch", on = False, color = "#ADDD8E", label = "Comparison only"),
								html.Br(),
								daq.BooleanSwitch(id = "gene_stats_switch", on = True, color = "#ADDD8E", label = "Show gene stats"),
								html.Br(),
								dcc.Loading(
									id = "loading_statistics",
									children = html.Div(id = "selected_gene_ma_plot_statistics", children = [], hidden = False, style = {"font-size": "12px"}),
									type = "dot",
									color = "#ADDD8E"
								)
							], style={"width": "22%", "height": "100%", "display": "inline-block", "vertical-align": "top"}),

							#MA-plot
							html.Div([
								dcc.Loading(
									id = "loading_ma_plot",
									children = dcc.Graph(id="ma_plot_graph", config = {"showEditInChartStudio": True, "plotlyServerURL": "https://chart-studio.plotly.com"}),
									type = "dot",
									color = "#ADDD8E"
								)
							], style={"width": "78%", "height": "100%", "display": "inline-block"}),
						
						], style={"width": "100%", "height": "50%", "display": "inline-block"}),
						
						#boxplots 
						html.Div([
							dcc.Loading(
								id = "loading_boxplots",
								children = dcc.Graph(id="boxplots_graph", config = {"showEditInChartStudio": True, "plotlyServerURL": "https://chart-studio.plotly.com"}),
								type = "dot",
								color = "#ADDD8E"
							)
						], style={"width": "100%", "height": "50%", "display": "inline-block"})
					
					], style={"width": "40%", "height": 800, "display": "inline-block"}),

					#go plot
					html.Div([
						html.Div([
							#search bar
							html.Div([
							], style={"width": "50%", "display": "inline-block"}),
						
							html.Div([
								html.Br(),
								dcc.Input(id="go_plot_filter_input", type="search", placeholder="Type here to filter GO gene sets", size="30", debounce=True),
							], style={"width": "50%", "display": "inline-block", "font-size": "12px"}),
						
						], style={"width": "100%", "height": "8%", "display": "inline-block"}),
						
						#go plot
						html.Div([
							dcc.Loading(
								id = "loading_go_plot",
								children = dcc.Graph(id="go_plot_graph", config = {"showEditInChartStudio": True, "plotlyServerURL": "https://chart-studio.plotly.com"}),
								type = "dot",
								color = "#ADDD8E"
							)
						],style={"width": "95%", "height": "92%", "display": "inline-block"}),
					
					], style={"width": "60%", "height": 800, "display": "inline-block"}),

					#graphical abstract
					html.Div([html.Hr(), html.Img(src="assets/workflow.png", alt="graphical_abstract", style={"width": "100%", "height": "100%"}, title="FASTQ reads from 3,853 RNA-Seq data from different tissues, namely ileum, colon, rectum, mesenteric adipose tissue, peripheral blood, and stools, were mined from NCBI GEO/SRA and passed the initial quality filter. All files were mapped to the human reference genome and initial gene quantification was performed. Since these data came from 26 different studies made in different laboratories, we counteract the presumptive bias through a batch correction in accordance with source and tissue of origin. Once the gene counts were adjusted, samples were divided into groups in accordance with the tissue of origin and patient condition prior to differential expression analysis and gene ontology functional enrichment. Finally, the reads failing to map to the human genome were subjected to metatranscriptomics profiling by taxonomic classification using exact k-mer matching either archaeal, bacterial, eukaryotic, or viral genes.")
					], style={"width": "100%", "display": "inline-block"}),

					#statistics
					html.Div([
						dcc.Graph(id="snakey", figure=snakey_fig)
					], style={"width": "100%", "display": "inline-block"})

				], style={"width": 1200}),

			], style={"width": "100%", "justify-content":"center", "display":"flex", "textAlign": "center"})

#gene/species dropdown
@app.callback(
	#gene species dropdown
	Output("gene_species_label", "children"),
	Output("gene_species_dropdown", "options"),
	Output("gene_species_dropdown", "value"),
	#stringency
	Output("stringency_dropdown", "value"),
	#switch
	Output("gene_stats_switch", "on"),
	
	#inputs
	Input("expression_dataset_dropdown", "value"),
	Input("ma_plot_graph", "clickData"),
	State("gene_species_dropdown", "options"),
	State("gene_stats_switch", "on"),
)
def find_genes_or_species(dataset, selected_point_ma_plot, current_dropdown_options, switch_state):
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
		label = "Species:"
		stringency = 0.1

	#if you click a gene, update only the dropdown value and keep the rest as it is
	if trigger_id == "ma_plot_graph":
		value = selected_point_ma_plot["points"][0]["customdata"][0].replace(" ", "_")
		options = current_dropdown_options
		if not switch_state:
			switch_state = True
	#if you change the datast, load it and change options and values
	elif trigger_id == "expression_dataset_dropdown":
		if dataset == "human":
			genes = pd.read_csv("http://www.lucamassimino.com/ibd/genes_list.tsv", sep = "\t", header=None, names=["genes"])
			genes = genes["genes"].dropna().tolist()
			options=[{"label": i, "value": i} for i in genes]
			value="IFNG"
		else:
			species = pd.read_csv("http://www.lucamassimino.com/ibd/{}_list.tsv".format(dataset), sep = "\t", header=None, names=["species"])
			species = species["species"].dropna().tolist()
			options = [{"label": i.replace("_", " ").replace("[", "").replace("]", ""), "value": i} for i in species]
			value = species[0]

	return label, options, value, stringency, switch_state

#tissue filter callback
@app.callback(
	Output("tissue_filter_dropdown", "options"),
	Output("tissue_filter_dropdown", "value"),
	Input("expression_dataset_dropdown", "value")
)
def get_tissues_with_2_or_more_conditions(dataset):
	#get all contrasts for dataset
	contrasts = pd.read_csv("http://www.lucamassimino.com/ibd/dge_list_{}.tsv".format(dataset), sep = "\t", header=None, names=["contrast"])
	contrasts = contrasts["contrast"].tolist()
	#get all tissues for dataset
	tissues = pd.read_csv("http://www.lucamassimino.com/ibd/umap_{}.tsv".format(dataset), sep = "\t")
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
	default_value_tissue = "Ileum"
	tissues_options = [{"label": i.replace("_", " "), "value": i} for i in filtered_tissues]

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
	contrasts = pd.read_csv("http://www.lucamassimino.com/ibd/dge_list_{}.tsv".format(dataset), sep = "\t", header=None, names=["contrast"])
	contrasts = contrasts["contrast"].dropna().tolist()

	filtered_contrasts = []
	for contrast in contrasts:
		#define the two tiessues in the contrast
		re_result = re.search(r"(\w+)_\w+-vs-(\w+)_\w+", contrast)
		tissue_1 = re_result.group(1)
		tissue_2 = re_result.group(2)
		#check if they are the same
		if tissue == tissue_1 and tissue == tissue_2:
			filtered_contrasts.append(contrast)
	default_contrast_value = filtered_contrasts[0]
	contrasts = [{"label": i.replace("_", " ").replace("-", " "), "value": i} for i in filtered_contrasts]

	return contrasts, default_contrast_value 

#plot umap callback
@app.callback(
	#umaps
	Output("umap_metadata", "figure"),
	Output("umap_expression", "figure"),
	#contrast only
	Output("metadata_dropdown", "value"),
	Output("contrast_only_switch", "on"),
	
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
	Input("contrast_only_switch", "on"),
	Input("umap_metadata", "restyleData"),
	#states
	State("umap_metadata", "figure"),
	State("umap_expression", "figure")
)
def plot_umaps(umap_dataset, metadata, expression_dataset, gene_species, contrast, zoom_metadata, zoom_expression, contrast_switch, metadata_legend_click, umap_metadata_fig, umap_expression_fig):
	#define contexts
	ctx = dash.callback_context
	trigger_id = ctx.triggered[0]["prop_id"]

	#changing metadata with something else then "condition" will switch off the switch; clicking umap metadata legend will have the same result
	if trigger_id == "metadata_dropdown.value" and contrast_switch is True and metadata != "condition" or trigger_id == "umap_metadata.restyleData":
		contrast_switch = False

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
		umap_df = pd.read_csv("http://www.lucamassimino.com/ibd/umap_{}.tsv".format(dataset), sep = "\t")
		
		#prepare df
		umap_df = umap_df.sort_values(by=[selected_metadata])
		umap_df[selected_metadata] = [i.replace("_", " ") for i in umap_df[selected_metadata]]
		label_to_value = {"sample": "Sample", "group": "Group", "tissue": "Tissue", "source": "Source", "library_strategy": "Library strategy", "condition": "Condition"}
		umap_df = umap_df.rename(columns=label_to_value)

		#plot
		umap_metadata_fig = px.scatter(umap_df, x="UMAP1", y="UMAP2", color = label_to_value[selected_metadata], hover_data={"UMAP1": False, "UMAP2": False, "Sample": True, "Group": True, "Tissue": True, "Source": True, "Library strategy": True}, color_discrete_sequence = colors)
		hover_template = "Sample: %{customdata[0]}<br>Group: %{customdata[1]}<br>Tissue: %{customdata[2]}<br>Source: %{customdata[3]}<br>Library strategy: %{customdata[4]}<extra></extra>"
		#update traces
		umap_metadata_fig.update_traces(marker_size=4, hovertemplate = hover_template)
		
		return umap_metadata_fig, umap_df

	#function to create a dataframe from umap_metadata_fig
	def parse_old_metadata_fig_to_get_its_df(umap_metadata_fig):
		#parse umap metadata data
		metadata_data = {}
		metadata_data["Sample"] = []
		metadata_data["Group"] = []
		metadata_data["Tissue"] = []
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
				metadata_data["Tissue"].append(dot[2])
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

	#click on contrast_only_switch. True = On, False = Off
	elif trigger_id == "contrast_only_switch.on":
		#true means to select only sample in contrast
		if contrast_switch is True:
			#if metadfata is not "condition", umap_metadata_fig must be created from tsv by selecting condition as metadata
			if metadata != "condition":
				metadata = "condition"
				umap_metadata_fig, umap_df = plot_umap_metadata(umap_dataset, metadata)
			#if metadata is "condition" then just parse the figure to recreate the df
			else:
				umap_df = parse_old_metadata_fig_to_get_its_df(umap_metadata_fig)

			#find condition and filter visibility in umap metadata legend
			condition_1 = contrast.split("-vs-")[0].replace("_", " ")
			condition_2 = contrast.split("-vs-")[1].replace("_", " ")
			#setup "visible" only for the two conditions in contrast
			for trace in umap_metadata_fig["data"]:
				if trace["name"] in [condition_1, condition_2]:
					trace["visible"] = True
				else:
					trace["visible"] = "legendonly"

		#false means do not change anything
		elif contrast_switch is False:
			raise PreventUpdate

	#if you don't have to change umap_metadata_fig, just parse the old fig to get its dataframe
	else:
		umap_df = parse_old_metadata_fig_to_get_its_df(umap_metadata_fig)

	##### UMAP EXPRESSION #####

	#function for creating umap_expression_fig from tsv file
	def plot_umap_expression(dataset, gene_species, samples_to_keep, umap_df, selected_metadata, umap_metadata_fig):
		#label for graph title
		if dataset == "human":
			expression_or_abundance = " expression"
		else:
			expression_or_abundance = " abundance"
		
		counts = pd.read_csv("http://www.lucamassimino.com/ibd/counts/{}/{}.tsv".format(dataset, gene_species), sep = "\t")
		counts = counts.rename(columns={"sample": "Sample"})

		#add counts to umap df
		umap_df = umap_df.merge(counts, how="left", on="Sample")
		umap_df = umap_df.dropna(subset=["counts"])
		
		#filter samples that are not visible
		umap_df = umap_df[umap_df["Sample"].isin(samples_to_keep)]
		
		#add log2 counts column to df
		umap_df["Log2 average expression"] = np.log2(umap_df["counts"])
		umap_df["Log2 average expression"].replace(to_replace = -np.inf, value = 0, inplace=True)

		#count samples
		n_samples = len(umap_df["Sample"])
		
		#plot
		umap_expression_fig = px.scatter(umap_df, x="UMAP1", y="UMAP2", color = "Log2 average expression", hover_data={"UMAP1": False, "UMAP2": False, "Sample": True, "Group": True, "Tissue": True, "Source": True, "Library strategy": True}, color_continuous_scale="reds")
		umap_expression_fig.update_layout(title = {"text": gene_species.replace("_", " ").replace("[", "").replace("]", "") + expression_or_abundance + " n=" + str(n_samples), "xanchor": "center", "x": 0.5, "y": 0.9, "font_size": 14}, margin=dict(l=0, r=20, t=80, b=80), coloraxis_colorbar_title_side = "right", coloraxis_colorbar_thickness=20, font_family="Arial", hoverlabel_bgcolor = "lightgrey")
		hover_template = "Sample: %{customdata[0]}<br>Group: %{customdata[1]}<br>Tissue: %{customdata[2]}<br>Source: %{customdata[3]}<br>Library strategy: %{customdata[4]}<br>Log2 average expression: %{marker.color}<extra></extra>"
		umap_expression_fig.update_traces(marker_size=4, hovertemplate = hover_template)

		#update layout umap metadata
		umap_metadata_fig["layout"]["title"]["text"] = selected_metadata.capitalize() + " n=" + str(n_samples)
		umap_metadata_fig["layout"]["title"]["xanchor"] = "center"
		umap_metadata_fig["layout"]["title"]["x"] = 0.7
		umap_metadata_fig["layout"]["title"]["y"] = 0.9
		umap_metadata_fig["layout"]["title"]["font"]["size"] = 14
		umap_metadata_fig["layout"]["legend"]["title"]["text"] = selected_metadata.capitalize().replace("_", " ")
		umap_metadata_fig["layout"]["legend"]["yanchor"] = "top"
		umap_metadata_fig["layout"]["legend"]["y"] = 1.1
		umap_metadata_fig["layout"]["legend"]["xanchor"] = "left"
		umap_metadata_fig["layout"]["legend"]["x"] = -0.65
		umap_metadata_fig["layout"]["legend"]["itemsizing"] = "constant"
		umap_metadata_fig["layout"]["margin"] = dict(l=0, r=0, t=70, b=80)
		umap_metadata_fig["layout"]["font"]["family"] = "Arial"

		return umap_expression_fig, umap_metadata_fig

	#function to get samples to keep from visibility status in umap_metadata_fig
	def get_samples_to_keep(umap_metadata_fig):
		samples_to_keep = []
		#parse metadata figure data 
		for trace in umap_metadata_fig["data"]:
			if trace["visible"] != "legendonly":
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

		samples_to_keep = get_samples_to_keep(umap_metadata_fig)
		#create figure
		umap_expression_fig, umap_metadata_fig = plot_umap_expression(expression_dataset, gene_species, samples_to_keep, umap_df, metadata, umap_metadata_fig)

		#apply old zoom if present
		if keep_old_zoom:
			umap_expression_fig["layout"]["xaxis"]["range"] = xaxis_range
			umap_expression_fig["layout"]["yaxis"]["range"] = yaxis_range
			umap_expression_fig["layout"]["xaxis"]["autorange"] = False
			umap_expression_fig["layout"]["yaxis"]["autorange"] = False
	
	#changes in umap metadata zoom and its legend
	elif trigger_id in ["umap_metadata.relayoutData", "umap_metadata.restyleData", "contrast_only_switch.on"]:
		
		#select samples to filter
		if trigger_id in ["umap_metadata.restyleData", "contrast_only_switch.on"]:
			samples_to_keep = get_samples_to_keep(umap_metadata_fig)
			#get new filtered umap_expression_fig
			umap_expression_fig, umap_metadata_fig = plot_umap_expression(expression_dataset, gene_species, samples_to_keep, umap_df, metadata, umap_metadata_fig)
		
		#update zoom from metadata
		umap_expression_fig = synchronize_zoom(umap_expression_fig, umap_metadata_fig)

	return umap_metadata_fig, umap_expression_fig, metadata, contrast_switch

#plot boxplots callback
@app.callback(
	Output("boxplots_graph", "figure"),
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
		counts = pd.read_csv("http://www.lucamassimino.com/ibd/counts/{}/{}.tsv".format(expression_dataset, gene), sep = "\t")
		#open metadata and select only the desired column
		metadata_df = pd.read_csv("http://www.lucamassimino.com/ibd/umap_{}.tsv".format(expression_dataset), sep = "\t")
		#merge and compute log2 and replace inf with 0
		metadata_df = metadata_df.merge(counts, how="left", on="sample")
		metadata_df["Log2 counts"] = np.log2(metadata_df["counts"])
		metadata_df["Log2 counts"].replace(to_replace = -np.inf, value = 0, inplace=True)
		#sort by metadata and clean it
		metadata = metadata_df.sort_values(by=[metadata_field])
		metadata_df[metadata_field] = [i.replace("_", " ") for i in metadata_df[metadata_field]]

		#label for dropdown
		metadata_field_label = metadata_field.replace("_", " ")
		metadata_field_label = metadata_field_label.capitalize()

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
		box_fig.update_layout(title = {"text": gene.replace("_", " ").replace("[", "").replace("]", "") + " / " + metadata_field_label, "xanchor": "center", "x": 0.5, "y": 0.9, "font_size": 14}, legend_title_text = metadata_field_label, yaxis_title = "Log2 normalized counts", margin=dict(l=57, r=20, t=80, b=0), font_family="Arial", height = 400)
	
	#syncronyze legend status with umap metadata
	for trace in range(0, len(umap_metadata_figure["data"])):
		box_fig["data"][trace]["visible"] = umap_metadata_figure["data"][trace]["visible"]

	return box_fig

#plot MA-plot
@app.callback(
	Output("ma_plot_graph", "figure"),
	Input("expression_dataset_dropdown", "value"),
	Input("contrast_dropdown", "value"),
	Input("stringency_dropdown", "value"),
	Input("gene_species_dropdown", "value"),
	Input("gene_stats_switch", "on"),
	State("ma_plot_graph", "figure")
)
def plot_MA_plot(dataset, contrast, fdr, gene, show_gene, old_ma_plot_figure):
	
	#define contexts
	ctx = dash.callback_context
	trigger_id = ctx.triggered[0]["prop_id"]

	if dataset == "human":
		gene_or_species = "Gene"
	else:
		gene_or_species = "Species"
	gene = gene.replace("_", " ").replace("[", "").replace("]", "")

	#read tsv if change in dataset or contrast
	if trigger_id in ["expression_dataset_dropdown.value", "contrast_dropdown.value"] or old_ma_plot_figure is None:
		table = pd.read_csv("http://www.lucamassimino.com/ibd/dge/{}/{}.diffexp.tsv".format(dataset, contrast), sep = "\t")
		table = table.dropna(subset=["Gene"])
		#log2 base mean
		table["log2_baseMean"] = np.log2(table["baseMean"])
		#clean gene/species name
		table["Gene"] = [i.replace("_", " ").replace("[", "").replace("]", "") for i in table["Gene"]]
	
	#parse existing figure for change in stringency or gene
	elif trigger_id in ["stringency_dropdown.value", "gene_species_dropdown.value", "gene_stats_switch.on"] and old_ma_plot_figure is not None:
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
				figure_data["padj"].append(dot[1])
		
		table = pd.DataFrame(figure_data)

	#find DEGs
	table.loc[(table["padj"] < fdr) & (table["log2FoldChange"] > 0), "DEG"] = "Up"
	table.loc[(table["padj"] < fdr) & (table["log2FoldChange"] < 0), "DEG"] = "Down"
	table.loc[table["DEG"].isnull(), "DEG"] = "no_DEG"

	#count DEGs
	up = table[table["DEG"] == "Up"]
	up = len(up["Gene"])
	down = table[table["DEG"] == "Down"]
	down = len(down["Gene"])

	#find selected gene
	if show_gene is True:
		table.loc[table["Gene"] == gene, "DEG"] = "selected_gene"
		table["selected_gene"] = ""
		table.loc[table["Gene"] == gene, "selected_gene"] = gene
	else:
		table["selected_gene"] = ""

	colors = ["#636363", "#D7301F", "#045A8D", "#ADDD8E"]
	
	if dataset != "human":
		table = table.rename(columns={"Gene": "Species"})

	#plot
	ma_plot_fig = px.scatter(table, x="log2_baseMean", y="log2FoldChange", hover_data={gene_or_species: True, "log2_baseMean": True, "log2FoldChange": True, "padj": True, "DEG": False, "selected_gene": False}, color="DEG", color_discrete_sequence=colors, category_orders = {"DEG": ["no_DEG", "Up", "Down", "selected_gene"]}, text = "selected_gene", labels={"log2FoldChange": "Log2 fold change", "log2_baseMean": "Log2 average expression"}, height = 400)

	#label of selected genes and hover template
	hover_template = "Log2 average expression: %{x}<br>Log2 fold change: %{y}<br>Gene: %{customdata[0]}<br>Padj: %{customdata[1]}<extra></extra>"
	ma_plot_fig.update_traces(textposition="top center", textfont_size=14, textfont_color = "#ADDD8E", marker_size=5, marker_symbol = 2, hovertemplate = hover_template)
	#marker selected gene have increased size
	ma_plot_fig["data"][3]["marker"]["size"] = 8
	#title and no legend
	ma_plot_fig.update_layout(showlegend=False, title={"text": contrast.replace("_", " ").replace("-", " ").replace("Control", "Ctrl") + " / FDR " + "{:.0e}".format(fdr), "xanchor": "center", "x": 0.5, "y": 0.9, "font_size": 14}, margin=dict(l=20, r=20, t=80, b=0), font_family="Arial")
	#line at y=0
	ma_plot_fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=0, line=dict(color="black", width=3), xref="paper", layer="below")
	#add annotation with number of up and down degs
	ma_plot_fig.add_annotation(text = "⇧" + str(up), xref="paper", yref="paper", x=0.95, y=0.9, showarrow=False, font_size=14, font_color="#DE2D26")
	ma_plot_fig.add_annotation(text = "⇩" + str(down), xref="paper", yref="paper", x=0.95, y=0.1, showarrow=False, font_size=14, font_color="#045A8D")

	return ma_plot_fig

#selected gene statistics on MA-plot
@app.callback(
	Output("selected_gene_ma_plot_statistics", "children"),
	Output("selected_gene_ma_plot_statistics", "hidden"),
	Input("gene_stats_switch", "on"),
	Input("ma_plot_graph", "figure"),
	State("expression_dataset_dropdown", "value")
)
def show_gene_statistics(switch_info, ma_plot_data, expression_dataset):
	if expression_dataset == "human":
		gene_or_species_label = "Gene: "
	else:
		gene_or_species_label = "Species: "
	
	children = []
	if switch_info:
		hidden_status = False
		gene_or_species = ma_plot_data["data"][3]["customdata"][0][0]
		average_expression = ma_plot_data["data"][3]["x"][0]
		log2_fold_change = ma_plot_data["data"][3]["y"][0]
		padj = ma_plot_data["data"][3]["customdata"][0][1]
		children.append(html.Div([gene_or_species_label, gene_or_species]))
		children.append(html.Div(["Log2 avg expr: ", str(round(average_expression, 1))]))
		children.append(html.Div(["Log2 FC: ", str(round(log2_fold_change, 1))]))
		if padj is not None:
			children.append(html.Div(["FDR: ", "{:.1e}".format(padj)]))
		else:
			children.append(html.Div(["FDR: NA"]))
	else:
		hidden_status = True

	return children, hidden_status

#summary callback
@app.callback(
	Output("summary", "children"),
	Input("umap_dataset_dropdown", "value"),
	Input("gene_species_dropdown", "value"),
	Input("contrast_dropdown", "value"),
	Input("tissue_filter_dropdown", "value"),
	Input("expression_dataset_dropdown", "value"),
	Input("contrast_only_switch", "on"),
	State("summary", "children")
)
def print_summary(umap_dataset, gene_species, contrast, tissue, expression_dataset, contrast_switch, summary_children):
	#expression dataset check
	if expression_dataset == "human":
		expression_enrichment = "expression"		
	else:
		expression_enrichment = "enrichment"

	#umap dataset check
	if umap_dataset == "human":
		transcriptome_metatranscriptome = "transcriptome"
	else:
		transcriptome_metatranscriptome = "metatranscriptome"

	#contrast_switch check
	if contrast_switch:
		tissue_comparison = contrast.replace("_", " ").replace("-", " ")
	else:
		tissue_comparison = tissue.replace("_", " ")

	#compone string
	summary_string = "You are now watching at {gene_species} {expression_enrichment} in {tissue_comparison}, within the {umap_dataset} {transcriptome_metatranscriptome} multidimensional scaling (UMAP)".format(gene_species = gene_species.replace("_", " ").replace("[", "").replace("]", ""), expression_enrichment = expression_enrichment, tissue_comparison = tissue_comparison, umap_dataset = umap_dataset.capitalize(), transcriptome_metatranscriptome = transcriptome_metatranscriptome)

	#add to children
	summary_children[1] = summary_string

	return summary_children

#go_plot callback
@app.callback(
	Output("go_plot_graph", "figure"),
	Input("contrast_dropdown", "value"),
	Input("go_plot_filter_input", "value")
)
def plot_go_plot(contrast, search_value):
	#open df
	go_df = pd.read_csv("http://www.lucamassimino.com/ibd/go/{}.merged_go.tsv".format(contrast), sep = "\t")
	#filter out useless columns and rename the one to keep
	go_df = go_df[["DGE", "Process~name", "P-value", "percentage%"]]
	go_df = go_df.rename(columns={"Process~name": "Process", "percentage%": "Enrichment", "P-value": "GO p-value"})
	#remove duplicate GO categories for up and down
	go_df.drop_duplicates(subset ="Process", keep = False, inplace = True)
	
	#define search query if present
	if search_value is not None:
		if search_value.endswith(" "):
			search_value = search_value.rstrip()
		search_query = re.split(r"[\s\-/,_]+", search_value)
		search_query = [x.lower() for x in search_query]

	#filter df by keyword
	processes_to_keep = []
	for process in go_df["Process"]:
		#got some keywords
		if search_value is not None or search_value == "":
			#force lowecase
			process_lower = process.lower()
			#check each quesy
			for x in search_query:
				if x in process_lower:
					processes_to_keep.append(process)
					break
		#no keyword
		else:
			processes_to_keep = go_df["Process"]
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
	go_df_up["DGE"] = [x.capitalize() for x in go_df_up["DGE"]]
	go_df_down = go_df[go_df["DGE"] == "down"]
	go_df_down["DGE"] = [x.capitalize() for x in go_df_down["DGE"]]
	
	#function to select GO categories
	def select_go_categories(df):
		#sort by pvalue
		df = df.sort_values(by=["GO p-value"])
		#take top ten
		df = df.head(12)
		#sort by enrichment
		df = df.sort_values(by=["Enrichment"])

		return df

	#apply function
	go_df_up = select_go_categories(go_df_up)
	go_df_down = select_go_categories(go_df_down)

	#create figure
	go_plot_fig = go.Figure()

	#function for hover text
	def create_hover_text(df):
		hover_text = []
		for index, row in df.iterrows():
			hover_text.append(('DGE: {dge}<br>' + 'Process: {process}<br>' + 'Enrichment: {enrichment}<br>' + 'GO p-value: {pvalue}').format(dge=row["DGE"], process=row['Process'], enrichment=row['Enrichment'], pvalue=row['GO p-value']))

		return hover_text

	#find out max enrichment for this dataset	
	all_enrichments = go_df_up["Enrichment"].append(go_df_down["Enrichment"], ignore_index=True)
	sizeref = 2. * max(all_enrichments)/(7 ** 2)

	#create subplots
	go_plot_fig = make_subplots(rows=2, cols=2, specs=[[{"rowspan": 2}, {}], [None, {}]], column_widths=[0.8, 0.2], subplot_titles=(None, "GO p-value", "Enrichment"))

	#up trace
	hover_text = create_hover_text(go_df_up)
	go_plot_fig.add_trace(go.Scatter(x=go_df_up["DGE"], y=go_df_up["Process"], marker_size=go_df_up["Enrichment"], marker_opacity = 1, marker_color = go_df_up["GO p-value"], marker_colorscale=["#D7301F", "#FCBBA1"], marker_showscale=False, marker_sizeref = sizeref, marker_cmax=0.05, marker_cmin=0, mode="markers", hovertext = hover_text, hoverinfo = "text"), row = 1, col = 1)
	#down trace
	hover_text = create_hover_text(go_df_down)
	go_plot_fig.add_trace(go.Scatter(x=go_df_down["DGE"], y=go_df_down["Process"], marker_size=go_df_down["Enrichment"], marker_opacity = 1, marker_color = go_df_down["GO p-value"], marker_colorscale=["#045A8D", "#C6DBEF"], marker_showscale=False, marker_sizeref = sizeref, marker_cmax=0.05, marker_cmin=0, mode="markers", hovertext = hover_text, hoverinfo = "text"), row = 1, col = 1)

	#colorbar trace
	go_plot_fig.add_trace(go.Scatter(x = [None], y = [None], marker_showscale=True, marker_color = [0], marker_colorscale=["#737373", "#D9D9D9"], marker_cmax=0.05, marker_cmin=0, marker_colorbar = dict(thicknessmode="pixels", thickness=20, lenmode="pixels", len=200, yanchor="top", y=1, x=0.8)), row = 1, col = 2)

	#size_legend_trace
	legend_sizes = [round(min(all_enrichments)), round(np.average([max(all_enrichments), min(all_enrichments)])), round(max(all_enrichments))]
	go_plot_fig.add_trace(go.Scatter(x = [1, 1, 1], y = [10, 40, 70], marker_size = legend_sizes, marker_sizeref = sizeref, marker_color = "#737373", mode="markers+text", text=["min", "mid", "max"], hoverinfo="text", hovertext=legend_sizes, textposition="top center"), row = 2, col = 2)

	#figure layout
	go_plot_fig.update_layout(title={"text": contrast.replace("_", " ").replace("-", " ").replace("Control", "Ctrl") + " / DGE FDR 1e-10", "xanchor": "center", "x": 0.775, "y": 0.95, "font_size": 14}, font_family="Arial", height = 720, xaxis_title = None, yaxis_title = None, showlegend=False, xaxis_fixedrange=True, yaxis_fixedrange=True, xaxis2_visible=False, yaxis2_visible=False, xaxis2_fixedrange=True, yaxis2_fixedrange=True, xaxis3_visible=False, yaxis3_visible=False, xaxis3_fixedrange=True, yaxis3_fixedrange=True, yaxis3_range=[0, 100], margin=dict(l=0, r=0, t=80, b=0), yaxis_autorange=True, yaxis2_autorange=True, yaxis3_autorange=False, xaxis_linecolor='rgb(255,255,255)', yaxis_linecolor='rgb(255,255,255)')

	#legend title dimension and position
	go_plot_fig["layout"]["annotations"][0]["font"]["size"] = 12
	go_plot_fig["layout"]["annotations"][1]["font"]["size"] = 12
	go_plot_fig["layout"]["annotations"][1]["y"] = 0.33

	return go_plot_fig

if __name__ == "__main__":
	app.run_server()
