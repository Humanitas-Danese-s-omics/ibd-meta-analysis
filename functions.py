import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import re
import yaml
import urllib.parse
from io import StringIO
from github import Github
from dash.dash_table.Format import Format, Scheme
from dash.exceptions import PreventUpdate
from dash import html

#tmp deconvolution fig
deconvolution_fig = go.Figure()
deconvolution_fig.add_annotation(text="Deconvolution coming soon.", showarrow=False)
deconvolution_fig.update_layout(xaxis_fixedrange=True, yaxis_fixedrange=True, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_linecolor="rgba(0,0,0,0)", yaxis_linecolor="rgba(0,0,0,0)", xaxis_showticklabels=False, yaxis_showticklabels=False, margin=dict(l=0, t=0, r=0, b=0), height=300)
deconvolution_fig.update_xaxes(range=[0, 4])
deconvolution_fig.update_yaxes(range=[0, 4])
deconvolution_fig.add_shape(type="rect", x0=0, y0=0, x1=4, y1=4, line=dict(color="black"))

#color palette
colors = ["#E31A1C", "#FF7F00", "#D9F0A3", "#33A02C", "#3B5DFF", "#6A3D9A", "#F46D43", "#FDAE61", "#E3DF00", "#B2DF8A", "#A6CEE3", "#CAB2D6", "#9E0142", "#FDB462", "#FFED6F", "#008941", "#1F78B4", "#5E4FA2", "#D53E4F", "#CCAA35", "#F4D749", "#B3DE69", "#3288BD", "#BC80BD", "#FB9A99", "#FED976", "#B15928", "#ABDDA4", "#8FB0FF", "#BB8BFF", "#CC002B", "#FB8072", "#CDA727", "#009131", "#0A09AE", "#5D00B9", "#772600", "#F7924C", "#FAD09F", "#006C31", "#5B93FF", "#5C006A", "#FF3944", "#BEAC3B", "#C48700", "#008531", "#4C43ED", "#BC29E1", "#AB2E00", "#DFFB71", "#E69A49", "#00B433", "#0000A6", "#6300A3", "#6B002C", "#CA834E", "#CCEBC5", "#9FA064", "#002DB5", "#9F94F0"]
#NA color
na_color = "#E6E6E6"
#gender colors
gender_colors = {"Female": "#FA9FB5", "Male": "#9ECAE1"}

#read config file
config = open("config.yaml")
config = yaml.load(config, Loader=yaml.FullLoader)

#data
if config["github"]["private_repo"]:
	github_username = config["github"]["username"]
	github_token = config["github"]["token"]
github_repo_name = config["github"]["repo_name"]
github_raw_link = "https://raw.githubusercontent.com/" + github_repo_name + "/master/"

#session for file download
github_session = requests.Session()
if config["github"]["private_repo"]:
	github_session.auth = (github_username, github_token)

#session for content
if config["github"]["private_repo"]:
	session = Github(github_token)
else:
	session = Github(github_token)
repo = session.get_repo(github_repo_name, lazy=False)

#function for downloading files from GitHub
def download_from_github(file_url):
	file_url = github_raw_link + file_url
	download = github_session.get(file_url).content
	#read the downloaded content and make a pandas dataframe
	df_downloaded_data = StringIO(download.decode('utf-8'))

	return df_downloaded_data

#function to list GitHub repo content of a folder
def get_content_from_github(folder_path):
	dirs = []
	if folder_path[-1] == "/":
		folder_path = folder_path.rstrip()
	contents = repo.get_contents(folder_path)
	for folder in contents:
		folder = folder.name
		dirs.append(folder)
	return dirs

#metadata related elements
metadata = download_from_github("metadata.tsv")
metadata = pd.read_csv(metadata, sep = "\t")
metadata = metadata.replace("_", " ", regex=True)
metadata_options = []
heatmap_annotation_options = []
discrete_metadata_options = []
continuous_metadata_options = [{"label": "Log2 expression", "value": "log2_expression"}]
label_to_value = {"sample": "Sample"}
columns_to_keep = []
for column in metadata.columns:
	#color by and heatmap annotation dropdowns
	if column not in ["sample", "fq1", "fq2", "control", "raw_counts", "kraken2", "immune_profiling_vdj"]:
		#dict used for translating colnames
		label_to_value[column] = column.capitalize().replace("_", " ")
		metadata_options.append({"label": column.capitalize().replace("_", " "), "value": column})
		if column != "condition":
			heatmap_annotation_options.append({"label": column.capitalize().replace("_", " "), "value": column})
		#discrete and continuous metadatas
		if str(metadata.dtypes[column]) == "object":
			#condition should always be the first
			if column == "condition":
				discrete_metadata_options.insert(0, {"label": column.capitalize().replace("_", " "), "value": column})
			else:
				discrete_metadata_options.append({"label": column.capitalize().replace("_", " "), "value": column})
		else:
			continuous_metadata_options.append({"label": column.capitalize().replace("_", " "), "value": column})

	#metadata teble columns
	if column not in [ "fq1", "fq2", "control", "raw_counts", "kraken2", "immune_profiling_vdj"]:
		columns_to_keep.append(column)

#color dictionary
i = 0
color_mapping = {}
#discrete color mapping
for dicscrete_option in discrete_metadata_options:
	column = dicscrete_option["value"]
	if column not in color_mapping:
		color_mapping[column] = {}
	metadata[column] = metadata[column].fillna("NA")
	values = metadata[column].unique().tolist()
	values.sort()
	for value in values:
		if value == "NA":
			color_mapping[column][value] = na_color
		elif value == "Male":
			color_mapping[column][value] = gender_colors["Male"]
		elif value == "Female":
			color_mapping[column][value] = gender_colors["Female"]
		else:
			if i == len(colors):
				i = 0
			color_mapping[column][value] = colors[i]
			i += 1
#continuous color mapping
for continuous_option in continuous_metadata_options:
	column = continuous_option["value"]
	if column != "log2_expression":
		if i == len(colors):
			i = 0
		if column not in color_mapping:
			color_mapping[column] = {}
		color_mapping[column]["continuous"] = colors[i]
		i += 1

#shape metadata table
metadata_table = metadata[columns_to_keep]
metadata_table = metadata_table.rename(columns=label_to_value)
metadata_table_columns = []
for column in metadata_table.columns:
	metadata_table_columns.append({"name": column.capitalize().replace("_", " "), "id": column})
metadata_table_data = metadata_table.to_dict("records")
metadata_link = metadata_table.to_csv(index=False, encoding="utf-8", sep="\t")
metadata_link = "data:text/tsv;charset=utf-8," + urllib.parse.quote(metadata_link)

#get all subdir to populate expression dataset
subdirs = get_content_from_github("data")
expression_datasets_options = []
mds_dataset_options = []
for dir in subdirs:
	if dir in ["human", "mouse"]:
		organism = dir
		expression_datasets_options.append({"label": dir.capitalize(), "value": dir})
		mds_dataset_options.append({"label": dir.capitalize(), "value": dir})
	else:
		non_host_content = get_content_from_github("data/" + dir)
		if "lipid" in dir:
			expression_datasets_options.append({"label": dir.capitalize().replace("_", " "), "value": dir})
			if "mds" in non_host_content:
				mds_dataset_options.append({"label": dir.capitalize().replace("_", " "), "value": dir})
		else:
			kingdom = dir.split("_")[0]
			lineage = dir.split("_")[1]
			if lineage == "genes":
				expression_datasets_options.append({"label": kingdom.capitalize() + " " + lineage, "value": dir})
			else:
				expression_datasets_options.append({"label": kingdom.capitalize() + " by " + lineage, "value": dir})
			#check if there is mds for each metatranscriptomics
			if "mds" in non_host_content:
				if lineage == "genes":
					mds_dataset_options.append({"label": kingdom.capitalize() + " " + lineage, "value": dir})
				else:
					mds_dataset_options.append({"label": kingdom.capitalize() + " by " + lineage, "value": dir})

#dbc switch as boolean switch
def boolean_switch(switch_value):
	if len(switch_value) == 1:
		boolean_switch_value = True
	else:
		boolean_switch_value = False
		
	return boolean_switch_value

#function to assign colors
def get_color(metadata_value, variable):
	if metadata_value == "NA":
		color = na_color
	elif metadata_value == "Log2 expression":
		color = "reds"
	else:
		color = color_mapping[metadata_value][variable]
	
	return color

#function for zoom synchronization mds
def synchronize_zoom(mds_to_update, reference_mds):
	mds_to_update["layout"]["xaxis"]["range"] = reference_mds["layout"]["xaxis"]["range"]
	mds_to_update["layout"]["yaxis"]["range"] = reference_mds["layout"]["yaxis"]["range"]
	mds_to_update["layout"]["xaxis"]["autorange"] = reference_mds["layout"]["xaxis"]["autorange"]
	mds_to_update["layout"]["yaxis"]["autorange"] = reference_mds["layout"]["yaxis"]["autorange"]

	return mds_to_update

#function for creating a discrete colored mds from tsv file
def plot_mds_discrete(mds_type, mds_dataset, selected_metadata, mds_discrete_fig, height, label_to_value, boolean_comparison_only_switch, contrast):
	#open tsv
	mds_df = download_from_github("data/" + mds_dataset + "/mds/" + mds_type + ".tsv")
	mds_df = pd.read_csv(mds_df, sep = "\t")
	#comparison only will filter the samples
	if boolean_comparison_only_switch:
		mds_df = mds_df[mds_df["condition"].isin(contrast.split("-vs-"))]
	number_of_samples = len(mds_df["sample"].tolist())
	if number_of_samples > 20:
		marker_size = 6
	else:
		marker_size = 8

	#prepare df
	mds_df = mds_df.sort_values(by=[selected_metadata])
	mds_df[selected_metadata] = mds_df[selected_metadata].fillna("NA")
	mds_df = mds_df.rename(columns=label_to_value)
	mds_df = mds_df.replace("_", " ", regex=True)

	#plot
	i = 0
	if config["sorted_conditions"] and selected_metadata == "condition":
		metadata_fields_ordered = config["condition_list"]
		metadata_fields_ordered = [metadata_field.replace("_", " ") for metadata_field in metadata_fields_ordered]
	else:
		metadata_fields_ordered = mds_df[label_to_value[selected_metadata]].unique().tolist()
		metadata_fields_ordered.sort()

	#get hover template and get columns to keep for customdata
	metadata_columns = []
	i = 0
	general_hover_template = ""
	for key in label_to_value:
		metadata_columns.append(label_to_value[key])
		general_hover_template += "{key}: %{{customdata[{i}]}}<br>".format(key=label_to_value[key], i=i)
		i += 1

	#hover template for this trace
	hover_template = general_hover_template + "<extra></extra>"

	#define x and y
	if mds_type == "tsne":
		x = "x"
		y = "y"
	elif mds_type == "umap":
		x = "UMAP1"
		y = "UMAP2"

	#add traces
	for metadata in metadata_fields_ordered:
		filtered_mds_df = mds_df[mds_df[label_to_value[selected_metadata]] == metadata]
		filtered_mds_df = filtered_mds_df.round(2)
		custom_data = filtered_mds_df[metadata_columns].fillna("NA")
		marker_color = get_color(selected_metadata, metadata)
		mds_discrete_fig.add_trace(go.Scatter(x=filtered_mds_df[x], y=filtered_mds_df[y], marker_opacity=1, marker_color=marker_color, marker_size=marker_size, customdata=custom_data, mode="markers", legendgroup=metadata, showlegend=True, hovertemplate=hover_template, name=metadata, visible=True))

	#update layout
	mds_discrete_fig.update_layout(height = height, xaxis_title_text = x, yaxis_title_text = y, title_xref="paper", title_xanchor="center", title_x=0.72, title_y=0.95,title_font_size=14, legend_title_text=selected_metadata.capitalize().replace("_", " "), legend_orientation="v", legend_xanchor="left", legend_x=0, legend_yanchor="top", legend_y=1.2, legend_itemsizing="constant", legend_tracegroupgap = 0.05, legend_title_side="top", legend_font_size=12, xaxis_automargin=True, yaxis_automargin=True, font_family="Arial", margin=dict(t=70, b=0, l=10, r=10), xaxis_domain=[0.45, 1])
	
	#mds_discrete_fig["layout"]["paper_bgcolor"]="LightSteelBlue"

	return mds_discrete_fig

#function for creating a continuous colored mds from tsv file
def plot_mds_continuous(mds_df, mds_type, variable_to_plot, color, mds_continuous_fig, height, label_to_value):
	#operations on mds_df
	number_of_samples = len(mds_df["sample"].tolist())
	if number_of_samples > 20:
		marker_size = 6
	else:
		marker_size = 8
	mds_df = mds_df.rename(columns=label_to_value)
	mds_df = mds_df.replace("_", " ", regex=True)

	#get hover template and get columns to keep for customdata
	metadata_columns = []
	i = 0
	general_hover_template = ""
	for key in label_to_value:
		metadata_columns.append(label_to_value[key])
		general_hover_template += "{key}: %{{customdata[{i}]}}<br>".format(key=label_to_value[key], i=i)
		i += 1

	#expression continuous umap will have counts
	if len(variable_to_plot) == 3:
		expression_dataset = variable_to_plot[0]
		feature = variable_to_plot[1]
		samples_to_keep = variable_to_plot[2]
		continuous_variable_to_plot = "Log2 expression"

		#download counts
		counts = download_from_github("data/" + expression_dataset + "/counts/" + feature + ".tsv")
		counts = pd.read_csv(counts, sep = "\t")
		counts = counts.rename(columns={"sample": "Sample"})
		counts = counts.replace("_", " ", regex=True)

		#add counts to umap df
		mds_df = mds_df.merge(counts, how="outer", on="Sample")
		#filter samples that are not visible
		mds_df = mds_df[mds_df["Sample"].isin(samples_to_keep)]

		#add log2 counts column to df
		mds_df["Log2 expression"] = np.log2(mds_df["counts"])
		mds_df["Log2 expression"].replace(to_replace = -np.inf, value = 0, inplace=True)
		#labels for graph title
		if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
			expression_or_abundance = " expression"
		else:
			expression_or_abundance = " abundance"
		#plot parameters
		colorbar_title = "Log2 {}".format(expression_or_abundance)
		hover_template = general_hover_template + "Log2{expression_or_abundance}: %{{marker.color}}<br><extra></extra>".format(expression_or_abundance=expression_or_abundance)
	#metadata continuous umap will use the metadata without counts
	else:
		selected_metadata = variable_to_plot[0]
		continuous_variable_to_plot = label_to_value[selected_metadata]
		colorbar_title = label_to_value[selected_metadata]
		hover_template = general_hover_template + "<extra></extra>"
	
	#fill nan with NA
	mds_df = mds_df.fillna("NA")
	mds_df = mds_df.round(2)
	
	#define x and y
	if mds_type == "tsne":
		x = "x"
		y = "y"
	elif mds_type == "umap":
		x = "UMAP1"
		y = "UMAP2"

	#select only NA values
	na_df = mds_df.loc[mds_df[continuous_variable_to_plot] == "NA"]
	custom_data = na_df[metadata_columns]
	#add discrete trace for NA values
	mds_continuous_fig.add_trace(go.Scatter(x=na_df[x], y=na_df[y], marker_color=na_color, marker_size=marker_size, customdata=custom_data, mode="markers", showlegend=False, hovertemplate=hover_template, visible=True))
	#select only not NA
	mds_df = mds_df.loc[mds_df[continuous_variable_to_plot] != "NA"]
	custom_data = mds_df[metadata_columns]
	marker_color = mds_df[continuous_variable_to_plot]
	#add continuous trace
	if color == "reds":
		colorscale = color
	else:
		colorscale = ["#FFFFFF", color]
	mds_continuous_fig.add_trace(go.Scatter(x=mds_df[x], y=mds_df[y], marker_color=marker_color, marker_colorscale=colorscale, marker_showscale=True, marker_opacity=1, marker_size=marker_size, marker_colorbar_title=colorbar_title, marker_colorbar_title_side="right", marker_colorbar_title_font_size=14, marker_colorbar_thicknessmode="pixels", marker_colorbar_thickness=15, marker_colorbar_tickfont={"family": "Arial", "size": 14}, mode="markers", customdata=custom_data, hovertemplate=hover_template, showlegend=False, visible=True))
	
	#update layout
	mds_continuous_fig.update_layout(height=height, title={"x": 0.5, "y": 0.95, "font_size": 14, "xref": "paper", "xanchor": "center"}, font_family="Arial", hoverlabel_bgcolor="lightgrey", xaxis_automargin=True, yaxis_automargin=True, margin=dict(t=70, b=0, l=10, r=60), xaxis_title_text=x, yaxis_title_text=y)
	
	#mds_continuous_fig["layout"]["paper_bgcolor"]="#E5F5F9"

	return mds_continuous_fig

#get number of displayed samples in mds
def get_displayed_samples(figure_data):
	x_range = figure_data["layout"]["xaxis"]["range"]
	y_range = figure_data["layout"]["yaxis"]["range"]
	
	#start of the app: give an artificial big range for axes
	if x_range is None or y_range is None:
		x_range = [-1000000000000000, 1000000000000000]
		y_range = [-1000000000000000, 1000000000000000]
	
	n_samples = 0
	#parse only visible traces
	for trace in figure_data["data"]:
		if trace["visible"] is True:
			#check all points
			for i in range(0, len(trace["x"])):
				x = trace["x"][i]
				y = trace["y"][i]
				if x != "NA" and y != "NA":
					if x > x_range[0] and x < x_range[1] and y > y_range[0] and y < y_range[1]:
						n_samples += 1

	return n_samples

#elements in the x axis in boxplots
def get_x_axis_elements_boxplots(selected_x, selected_y, feature_dataset):
	#open metadata
	metadata_df = download_from_github("metadata.tsv")
	metadata_df = pd.read_csv(metadata_df, sep = "\t")

	#counts as y need external file with count values
	if selected_y in ["log2_expression", "log2_abundance"]:
		#get a feature to filter metadata by selecting only samples which have counts
		if feature_dataset in ["human", "mouse"] or "genes" in feature_dataset:
			list = "data/" + feature_dataset + "/counts/genes_list.tsv"
		else:
			if "lipid" in feature_dataset:
				list = "data/" + feature_dataset + "/counts/lipid_list.tsv"
			else:
				list = "data/" + feature_dataset + "/counts/feature_list.tsv"
		list = download_from_github(list)
		list = pd.read_csv(list, sep = "\t", header=None, names=["gene_species"])
		list = list["gene_species"].tolist()
		feature = list[0]
		counts = download_from_github("data/" + feature_dataset + "/counts/" + feature + ".tsv")
		counts = pd.read_csv(counts, sep = "\t")
		metadata_df = metadata_df.merge(counts, how="inner", on="sample")
	
	#get all x
	x_values = metadata_df[selected_x].unique().tolist()
	
	#setup options
	options = []
	for x_value in x_values:
		options.append({"label": x_value.replace("_", " "), "value": x_value})
	
	return options, x_values

#go search function
def serach_go(search_value, df, expression_dataset, add_gsea_switch):
	#define search query if present
	if search_value.endswith(" "):
		search_value = search_value.rstrip()
	search_query = re.split(r"[\s\-/,_]+", search_value)
	search_query = [x.lower() for x in search_query]

	#search keyword in processes
	processes_to_keep = []
	for process in df["Process~name"]:
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
			#else, just search in the name of the GO category
			else:
				if expression_dataset in ["human", "mouse"] and not add_gsea_switch:
					process_name = process_lower.split("~")[1]
				else:
					process_name = process_lower
				if x in process_name:
					processes_to_keep.append(process)
					if process not in processes_to_keep:
						processes_to_keep.append(process)

	return processes_to_keep

#dge table rendering
def dge_table_operations(table, dataset, stringency, target_prioritization):
	pvalue_type = stringency.split("_")[0]
	pvalue_threshold = stringency.split("_")[1]

	if target_prioritization:
		#keep degs and remove useless columns
		table = table.rename(columns={"log2FoldChange": "log2 FC", "padj": "FDR", "Geneid": "Gene ID"})
		table["id"] = table["Gene"]
		table = table[table["FDR"] < float(pvalue_threshold)]
		table = table[["Gene", "Gene ID", "log2 FC", "FDR", "id"]]

		#build df from data
		opentarget_df = download_from_github("opentargets.tsv")
		opentarget_df = pd.read_csv(opentarget_df, sep="\t")
		table = pd.merge(table, opentarget_df, on="Gene ID")

		#priority for overexpression
		if not table.empty:
			table.loc[table["log2 FC"] >= 1, "DGE"] = 4
			table.loc[(table["log2 FC"] > 0) & (table["log2 FC"] <1), "DGE"] = 3
			table.loc[(table["log2 FC"] < 0) & (table["log2 FC"] >-1), "DGE"] = 2
			table.loc[table["log2 FC"] <= -1, "DGE"] = 1
			#sort values according to these columns
			table = table.sort_values(["DGE", "index"], ascending = (False, False))
			table = table.reset_index(drop=True)
			table = table.drop("DGE", axis=1)
			table = table.drop("index", axis=1)
			all_columns = list(table.columns)
			table["Rank"] = [x + 1 for x in list(table.index)]
			table = table[["Rank"] + all_columns]
		else:
			table["Rank"] = []
		
		#define columns
		columns = [
			{"name": "Rank", "id": "Rank"},
			{"name": "Gene", "id": "Gene"},
			{"name": "Gene ID", "id":"Gene ID"},
			{"name": "log2 FC", "id":"log2 FC", "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed)},
			{"name": "FDR", "id": "FDR", "type": "numeric", "format": Format(precision=2, scheme=Scheme.decimal_or_exponent)},
			{"name": "Drugs", "id": "drug_count", "type": "numeric"},
			{"name": "Drugs", "id": "total_drug_count"},
			{"name": "Drugs", "id": "drugs", "type": "text", "presentation": "markdown"},
			{"name": "IBD drugs", "id": "IBD_drug_count", "type": "numeric"},
			{"name": "IBD drugs", "id": "IBD_drugs", "type": "text", "presentation": "markdown"},
			{"name": "IBD GWAS", "id": "GWAS_count", "type": "numeric"},
			{"name": "IBD GWAS", "id": "GWAS", "type": "text", "presentation": "markdown"},
			{"name": "Tissue eQTL", "id": "QTL_in_tissues_count", "type": "numeric"},
			{"name": "Tissue eQTL", "id": "QTL_in_tissues", "type": "text", "presentation": "markdown"},
			{"name": "Protein expression in cell types", "id": "expression_in_tissue_cell_types_count", "type": "numeric"},
			{"name": "Protein expression in cell types", "id": "expression_in_tissue_cell_types", "type": "text", "presentation": "markdown"},
			{"name": "Protein expression in cell compartments", "id": "protein_expression_in_cell_compartment_count", "type": "numeric"},
			{"name": "Protein expression in cell compartments", "id": "protein_expression_in_cell_compartment", "type": "text", "presentation": "markdown"}
		]
	else:
		#define dataset specific variables and link
		if dataset in ["human", "mouse"]:
			base_mean_label = "Average expression"
			gene_column_name = "Gene"
			table = table.rename(columns={"Geneid": "Gene ID"})
			#store genes and geneID without link formatting
			table["Gene"] = table["Gene"].fillna("")

			#create links which use gene ID
			external_resources_geneid = "[![NCBI](assets/icon_ncbi.png 'NCBI')](https://www.ncbi.nlm.nih.gov/gene/?term=" + table["Gene ID"] + ") " + "[![Ensembl](assets/icon_ensembl.png 'Ensembl')](https://www.ensembl.org/Homo_sapiens/Gene/Summary?g=" + table["Gene ID"] + ") " + "[![GeneCards](assets/icon_genecards.png 'GeneCards')](https://www.genecards.org/cgi-bin/carddisp.pl?gene=" + table["Gene ID"] + ")"

			#create links which use gene ID
			external_resources_gene = " [![GWAS catalog](assets/icon_gwas_catalog.png 'GWAS catalog')](https://www.ebi.ac.uk/gwas/genes/" + table["Gene"] + ") " + "[![GTEx](assets/icon_gtex.png 'GTEx')](https://www.gtexportal.org/home/gene/" + table["Gene"] + ")"

			#additional external resources
			if config["add_external_resources_to_dge_table"]:
				for external_resource in config["external_resources"]:
					column_to_use = config["external_resources"][external_resource]["column_to_use"]
					if column_to_use == "Gene ID":
						external_resources_to_update = external_resources_geneid
					else:
						external_resources_to_update = external_resources_gene
					external_resources_to_update += " [![{name}]({icon} '{name}')]({link_root}".format(name=external_resource, icon=config["external_resources"][external_resource]["icon"], link_root=config["external_resources"][external_resource]["link_root"]) + table[column_to_use] + ")"
			
			#paste all external resources and apply
			external_resources = external_resources_geneid + external_resources_gene
			table["External resources"] = external_resources
			
			#remove external resources where gene is not defined
			table.loc[table["Gene"] == "", "External resources"] = external_resources_geneid
		else:
			base_mean_label = "Average abundance"
			if "lipid" in dataset:
				gene_column_name = dataset.replace("_", " ").capitalize()
				table = table.rename(columns={"Gene": gene_column_name, "Geneid": "Gene ID"})
				table["Gene ID"] = table["Gene ID"].fillna("")
				table["External resources"] = "[![LIPID MAPS](assets/icon_lipid_maps.png 'LIPID MAPS')](https://www.lipidmaps.org/databases/lmsd/" + table["Gene ID"] + ")"
				table.loc[table["Gene ID"] == "", "External resources"] = ""
			else:
				gene_column_name = dataset.split("_")[1].capitalize()
				table = table.rename(columns={"Gene": gene_column_name})
				table["External resources"] = ["[![NCBI](assets/icon_ncbi.png 'NCBI')](https://www.ncbi.nlm.nih.gov/genome/?term=" + x.replace(" ", "+") + ")" for x in table[gene_column_name]]
			table[gene_column_name] = [x.replace("_", " ").replace("[", "").replace("]", "") for x in table[gene_column_name]]

		#data carpentry
		table["id"] = table[gene_column_name]
		table = table.sort_values(by=[pvalue_type])
		table = table.rename(columns={"log2FoldChange": "log2 FC", "lfcSE": "log2 FC SE", "pvalue": "P-value", "padj": "FDR", "baseMean": base_mean_label})
		table["P-value"] = table["P-value"].fillna("NA")
		table["FDR"] = table["FDR"].fillna("NA")

		#define columns
		if dataset == "lipid":
			geneid_label = "Lipid ID"
		else:
			geneid_label = "Gene ID"
		columns = [
			{"name": gene_column_name, "id": gene_column_name}, 
			{"name": geneid_label, "id":"Gene ID"},
			{"name": base_mean_label, "id": base_mean_label, "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed)},
			{"name": "log2 FC", "id":"log2 FC", "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed)},
			{"name": "log2 FC SE", "id":"log2 FC SE", "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed)},
			{"name": "P-value", "id":"P-value", "type": "numeric", "format": Format(precision=2, scheme=Scheme.decimal_or_exponent)},
			{"name": "FDR", "id":"FDR", "type": "numeric", "format": Format(precision=2, scheme=Scheme.decimal_or_exponent)},
			{"name": "External resources", "id":"External resources", "type": "text", "presentation": "markdown"}
			]
		#Gene ID column not useful for metatransciptomics data and lipid category
		if dataset not in ["human", "mouse", "lipid"]:
			del columns[1]
			#lipid categories doesn't have any external resource
			if dataset == "lipid_category":
				del columns[-1]

	#define data
	data = table.to_dict("records")

	if pvalue_type == "padj":
		pvalue_column = "{FDR}"
	else:
		pvalue_column = "{P-value}"

	#color rows by pvalue and up and down log2FC
	style_data_conditional = [
		{
			"if": {
				"filter_query": '{pvalue_column} = "NA"'.format(pvalue_column=pvalue_column)
			},
			"backgroundColor": "white"
		},
		{
			"if": {
				"filter_query": "{pvalue_column} < {threshold}".format(pvalue_column=pvalue_column, threshold=pvalue_threshold) + " && {log2 FC} < 0"
			},
			"backgroundColor": "#E6F0FF"
		},
		{
			"if": {
				"filter_query": "{pvalue_column} < {threshold}".format(pvalue_column=pvalue_column, threshold=pvalue_threshold) + " && {log2 FC} > 0"
			},
			"backgroundColor": "#FFE6E6"
		},
		{
			"if": {"state": "selected"},
			"backgroundColor": "rgba(44, 62, 80, 0.2)",
			"border": "1px solid #597ea2",
		}
	]

	return columns, data, style_data_conditional

#search genes in the textarea
def serach_genes_in_textarea(trigger_id, go_plot_click, expression_dataset, stringency_info, contrast, text, already_selected_genes_species, add_gsea_switch, number_of_features):
	#click on GO-plot
	if trigger_id == "go_plot_graph.clickData":
		if isinstance(go_plot_click["points"][0]["y"], str):
			#reset log div
			log_div = []
			log_hidden_status = True

			#do not add genes to metatranscriptomics elements!
			if expression_dataset not in ["human", "mouse"]:
				raise PreventUpdate

			#read go table
			go_df = download_from_github("data/{}/".format(expression_dataset) + stringency_info + "/" + contrast + ".merged_go.tsv")
			go_df = pd.read_csv(go_df, sep = "\t")
			go_df = go_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
			#concatenate gsea results if the switch is true
			boolean_add_gsea_switch = boolean_switch(add_gsea_switch)
			if boolean_add_gsea_switch:
				gsea_df = download_from_github("data/{}/".format(expression_dataset) + "gsea/" + contrast + ".merged_go.tsv")
				gsea_df = pd.read_csv(gsea_df, sep = "\t")
				gsea_df["Genes"] = [gene.replace(";", "; ") for gene in gsea_df["Genes"]]
				gsea_df = gsea_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
				go_df = pd.concat([go_df, gsea_df])
			go_df = go_df.rename(columns={"Process~name": "Process", "percentage%": "Enrichment", "P-value": "GO p-value"})

			#crop too long process name
			processes = []
			for process in go_df["Process"]:
				if len(process) > 80:
					process = process[0:79] + " ..."
				processes.append(process.replace("_", " "))
			go_df["Process"] = processes

			#search GO ID and get genes
			if go_plot_click["points"][0]["y"].startswith("GO"):
				process_name = go_plot_click["points"][0]["y"]
			else:
				process_name = go_plot_click["points"][0]["y"].replace("_", " ")
			go_df = go_df[go_df["Process"] == process_name]
			genes = go_df["Genes"].tolist()
			if len(genes) == 2:
				genes = genes[0] + " " + genes[1]
			else:
				genes = genes[0]
			#remove last ;
			genes = genes[:-1]
			#add genes to text area
			if len(text) > 0:
				text += "; "
			text += genes
			#create a list of genes and add them to the multidropdown
			genes = genes.split("; ")
			already_selected_genes_species = already_selected_genes_species + genes
		
		#click on the enrichment legend should not trigger anything
		else:
			raise PreventUpdate

	#reset text area if you change the input dropdowns
	elif trigger_id in ["contrast_dropdown.value", "stringency_dropdown.value"]:
		#reset log div
		log_div = []
		log_hidden_status = True
		
		diffexp_df = download_from_github("data/" + expression_dataset + "/dge/" + contrast + ".diffexp.tsv")
		diffexp_df = pd.read_csv(diffexp_df, sep = "\t")
		diffexp_df["Gene"] = diffexp_df["Gene"].fillna("NA")
		diffexp_df = diffexp_df[diffexp_df["Gene"] != "NA"]

		#stingency specs
		pvalue_type = stringency_info.split("_")[0]
		pvalue_value = stringency_info.split("_")[1]

		#find DEGs
		diffexp_df.loc[(diffexp_df[pvalue_type] <= float(pvalue_value)) & (diffexp_df["log2FoldChange"] > 0), "DEG"] = "Up"
		diffexp_df.loc[(diffexp_df[pvalue_type] <= float(pvalue_value)) & (diffexp_df["log2FoldChange"] < 0), "DEG"] = "Down"

		#get top up 15 DEGs by log2FC
		up_genes = diffexp_df[diffexp_df["DEG"] == "Up"]
		#sort by log2FC
		up_genes = up_genes.sort_values(by=["log2FoldChange"], ascending=False)
		#take top n
		up_genes = up_genes.head(number_of_features)
		#get genes
		up_genes = up_genes["Gene"].tolist()
		#get top down 15 DEGs by log2FC
		down_genes = diffexp_df[diffexp_df["DEG"] == "Down"]
		#sort by log2FC
		down_genes = down_genes.sort_values(by=["log2FoldChange"])
		#take top n
		down_genes = down_genes.head(number_of_features)
		#get genes
		down_genes = down_genes["Gene"].tolist()

		#add genes in text area
		if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
			sep = "; "
		else:
			sep = "\n"
		up_genes_string = sep.join(up_genes)
		down_genes_string = sep.join(down_genes)
		if len(up_genes) == 0 and len(down_genes) != 0:
			text = down_genes_string
		elif len(down_genes) == 0 and len(up_genes) != 0:
			text = up_genes_string
		elif len(up_genes) == 0 and len(down_genes) == 0:
			text = ""
		else:
			text = up_genes_string + sep + down_genes_string

		#add genes to dropdown
		already_selected_genes_species = up_genes + down_genes
		already_selected_genes_species = [gene_species.replace(" ", "_").replace("/", "€") for gene_species in already_selected_genes_species]
	
	#button click by the user
	else:
		#text is none, do almost anything
		if text is None or text == "":
			if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
				log_div = [html.Br(), "No genes in the search area!"]
			else:
				if expression_dataset == "lipid":
					element = "lipids"
				else:
					element = expression_dataset.replace("_", " ").replace("viruses", "viral").replace("bacteria", "bacterial").replace("archaea", "archaeal").replace("eukaryota", "eukaryotic").replace("order", "orders").replace("family", "families").replace("category", "categories")
				log_div = [html.Br(), "No " + element + " in the search area!"]
			log_hidden_status = False
		else:
			#list of features
			if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
				list = "data/" + expression_dataset + "/counts/genes_list.tsv"
			else:
				if "lipid" in expression_dataset:
					list = "data/" + expression_dataset + "/counts/lipid_list.tsv"
				else:
					list = "data/" + expression_dataset + "/counts/feature_list.tsv"
			all_genes = download_from_github(list)
			all_genes = pd.read_csv(all_genes, sep = "\t", header=None, names=["genes"])
			all_genes = all_genes["genes"].replace("€", "/").dropna().tolist()

			#upper for case insensitive search
			if expression_dataset not in ["human", "mouse"] or "genes" not in expression_dataset:
				original_names = {}
				for gene in all_genes:
					original_names[gene.upper()] = gene
				all_genes = [x.upper() for x in all_genes]
				already_selected_genes_species = [x.upper() for x in already_selected_genes_species]
			
			#search genes in text
			if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset: 
				genes_species_in_text_area = re.split(r"[\s,;]+", text)
			else:
				genes_species_in_text_area = re.split(r"[\n]+", text)

			#remove last gene if empty
			if genes_species_in_text_area[-1] == "":
				genes_species_in_text_area = genes_species_in_text_area[0:-1]

			#parse gene
			genes_species_not_found = []
			for gene in genes_species_in_text_area:
				if expression_dataset != "mouse":
					gene = gene.upper().replace(" ", "_")
				else:
					gene = gene.capitalize().replace(" ", "_")
				#gene existing but not in selected: add it to selected
				if gene in all_genes:
					if already_selected_genes_species is None:
						already_selected_genes_species = [gene]
					elif gene not in already_selected_genes_species:
						already_selected_genes_species.append(gene)
				#gene not existing
				elif gene not in all_genes:
					if gene not in genes_species_not_found:
						genes_species_not_found.append(gene)

			if expression_dataset not in ["human", "mouse"]  or "genes" not in expression_dataset:
				already_selected_genes_species = [original_names[gene.upper()] for gene in already_selected_genes_species]
				genes_species_not_found = [gene.lower().capitalize() for gene in genes_species_not_found]

			#log for genes not found
			if len(genes_species_not_found) > 0:
				log_div_string = ", ".join(genes_species_not_found)
				log_div = [html.Br(), "Can not find:", html.Br(), log_div_string]
				log_hidden_status = False
			#hide div if all genes has been found
			else:
				log_div = []
				log_hidden_status = True

	return already_selected_genes_species, log_div, log_hidden_status, text
