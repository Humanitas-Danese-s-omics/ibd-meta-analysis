#import packages
import dash
from dash.exceptions import PreventUpdate
from dash import dcc
from dash.dependencies import Input, Output, State
from dash.dash_table.Format import Format, Scheme
import pandas as pd
import numpy as np
import urllib.parse
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
from functools import reduce
from sklearn.preprocessing import scale
#import modules
import functions
from functions import config, label_to_value

def define_callbacks(app):

	##### elements ######

	#add gsea switch
	@app.callback(
		Output("add_gsea_switch_div", "hidden"),
		Output("add_gsea_switch", "value"),
		Input("feature_dataset_dropdown", "value")
	)
	def show_add_gsea_switch(expression_dataset):
		if expression_dataset in ["human", "mouse"]:
			folders = functions.get_content_from_github("data/{}".format(expression_dataset))
			if "gsea" in folders:
				hidden = False	
			else:
				hidden = True
		else:
			hidden = True
		value = []
		
		return hidden, value

	#labels for tabs titles
	@app.callback(
		Output("expression_abundance_profiling", "label"),
		Output("dge_table_tab", "label"),
		Output("go_table_tab", "label"),
		Input("feature_dataset_dropdown", "value")
	)
	def get_tabs_titles(expression_dataset):
		if expression_dataset in ["human", "mouse"]:
			expression_abundance_profiling_label = "Gene expression profiling"
		elif "genes" in expression_dataset:
			expression_abundance_profiling_label = "{} expression profiling".format(expression_dataset.replace("_genes", " gene").capitalize())
		else:
			expression_abundance_profiling_label = expression_dataset.replace("_", " ").capitalize() + " abundance profiling"

		if "lipid" in expression_dataset:
			dge_table_label = "DLE table"
			go_table_label = "LO table"
		else:
			dge_table_label = "DGE table"
			go_table_label = "GO table"
		
		return expression_abundance_profiling_label, dge_table_label, go_table_label

	#placeholder for heatmap_text_area
	@app.callback(
		Output("heatmap_text_area", "placeholder"),
		Input("feature_dataset_dropdown", "value")
	)
	def get_placeholder_heatmap_text_area(expression_dataset):
		if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
			placeholder = "Paste list (plot allowed for max 10 features)"
		else:
			placeholder = "Paste list (plot allowed for max 10 features, one per line)"

		return placeholder

	#search genes for heatmap
	@app.callback(
		Output("feature_heatmap_dropdown", "value"),
		Output("genes_not_found_heatmap_div", "children"),
		Output("genes_not_found_heatmap_div", "hidden"),
		Output("heatmap_text_area", "value"),
		Output("update_heatmap_plot_button", "n_clicks"),
		Input("heatmap_search_button", "n_clicks"),
		Input("go_plot_graph", "clickData"),
		Input("contrast_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		State("heatmap_text_area", "value"),
		State("feature_dataset_dropdown", "value"),
		State("feature_heatmap_dropdown", "value"),
		State("genes_not_found_heatmap_div", "hidden"),
		State("genes_not_found_heatmap_div", "children"),
		State("update_heatmap_plot_button", "n_clicks"),
		State("add_gsea_switch", "value")
	)
	def serach_genes_in_text_area_heatmap(n_clicks_search, go_plot_click, contrast, stringency_info, text, expression_dataset, already_selected_genes_species, log_hidden_status, log_div, n_clicks_update_plot, add_gsea_switch):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		already_selected_genes_species, log_div, log_hidden_status, text = functions.serach_genes_in_textarea(trigger_id, go_plot_click, expression_dataset, stringency_info, contrast, text, already_selected_genes_species, add_gsea_switch, 15)

		return already_selected_genes_species, log_div, log_hidden_status, text, n_clicks_update_plot

	#search genes for multiboxplots
	@app.callback(
		Output("feature_multi_boxplots_dropdown", "value"),
		Output("genes_not_found_multi_boxplots_div", "children"),
		Output("genes_not_found_multi_boxplots_div", "hidden"),
		Output("multi_boxplots_text_area", "value"),
		Output("update_multiboxplot_plot_button", "n_clicks"),
		Input("multi_boxplots_search_button", "n_clicks"),
		Input("go_plot_graph", "clickData"),
		Input("contrast_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		State("feature_dataset_dropdown", "value"),
		State("multi_boxplots_text_area", "value"),
		State("feature_multi_boxplots_dropdown", "value"),
		State("genes_not_found_multi_boxplots_div", "hidden"),
		State("add_gsea_switch", "value"),
		State("update_multiboxplot_plot_button", "n_clicks")
	)
	def serach_genes_in_text_area_multiboxplots(n_clicks_search, go_plot_click, contrast, stringency_info, expression_dataset, text, already_selected_genes_species, log_hidden_status, add_gsea_switch, update_multiboxplot_plot_button):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		already_selected_genes_species, log_div, log_hidden_status, text = functions.serach_genes_in_textarea(trigger_id, go_plot_click, expression_dataset, stringency_info, contrast, text, already_selected_genes_species, add_gsea_switch, 10)
		
		return already_selected_genes_species, log_div, log_hidden_status, text, update_multiboxplot_plot_button

	#target prioritization switch
	@app.callback(
		Output("target_prioritization_switch_div", "hidden"),
		Input("feature_dataset_dropdown", "value")
	)
	def show_target_prioritization_switch(feature_dataset):
		if feature_dataset == "human" and config["opentargets"] is True:
			hidden = False
		else:
			hidden = True
		
		return hidden

	##### dropdowns #####

	#get mds datasets types
	@app.callback(
		Output("mds_type", "options"),
		Input("mds_dataset", "value")
	)
	def get_mds_type_for_dataset(mds_dataset):

		mds_files = functions.get_content_from_github("data/" + mds_dataset + "/mds")
		
		options = []
		for file in mds_files:
			mds_type = file.split(".")[0]
			if mds_type == "tsne":
				label = "t-SNE"
			else:
				label = "UMAP"
			options.append({"label": label, "value": mds_type})

		return options

	#get features dropdown
	@app.callback(
		Output("feature_dropdown", "value"),
		Output("feature_dropdown", "options"),
		Output("feature_label", "children"),
		Output("feature_heatmap_dropdown", "options"),
		Output("feature_multi_boxplots_dropdown", "options"),
		Output("feature_multi_boxplots_dropdown", "placeholder"),
		Output("multi_gene_dge_table_selection_dropdown", "options"),
		Output("multi_gene_dge_table_selection_dropdown", "placeholder"),
		Input("feature_dataset_dropdown", "value"),
		Input("ma_plot_graph", "clickData"),
		Input("dge_table", "active_cell"),
		Input("dge_table_filtered", "active_cell"),
		State("feature_dropdown", "options")
	)
	def get_features(expression_dataset, selected_point_ma_plot, active_cell_full, active_cell_filtered, current_dropdown_options):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#dataset specific variables
		if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
			list = "data/" + expression_dataset + "/counts/genes_list.tsv"
			if expression_dataset in ["human", "mouse"]:
				placeholder = "Type here to search host genes"
				label = "Host gene"
			else:
				placeholder = "Type here to search {}".format(expression_dataset.replace("_", " "))
				label = "{}".format(expression_dataset.replace("genes", "gene"))
		else:
			label = expression_dataset.replace("_", " ")
			if "lipid" in expression_dataset:
				list = "data/" + expression_dataset + "/counts/lipid_list.tsv"
				if expression_dataset == "lipid":
					placeholder = "Type here to search lipids"
				else:
					placeholder = "Type here to search lipid categories"
			else:
				list = "data/" + expression_dataset + "/counts/feature_list.tsv"
				placeholder = "Type here to search {}".format(expression_dataset.replace("_", " ").replace("order", "orders").replace("family", "families"))
				label = expression_dataset.capitalize().replace("_", " by ")

		#if you click a gene, update only the dropdown value and keep the rest as it is
		if trigger_id == "ma_plot_graph.clickData":
			selected_element = selected_point_ma_plot["points"][0]["customdata"][0].replace(" ", "_")
			if selected_element == "NA":
				raise PreventUpdate
			else:
				value = selected_element
				options = current_dropdown_options

		#active cell in dge_table
		elif trigger_id in ["dge_table.active_cell", "dge_table_filtered.active_cell"]:
			#find out which active table to use
			if trigger_id == "dge_table.active_cell":
				active_cell = active_cell_full
			else:
				active_cell = active_cell_filtered
			if active_cell is None:
				raise PreventUpdate
			else:
				#prevent update for click on wrong column or empty gene
				if active_cell["column_id"] != "Gene" or active_cell["column_id"] == "Gene" and active_cell["row_id"] == "":
					raise PreventUpdate
				#return values
				else:
					value = active_cell["row_id"]
					options = current_dropdown_options
		else:
			#load and open input file			
			list = functions.download_from_github(list)
			list = pd.read_csv(list, sep = "\t", header=None, names=["gene_species"])
			list = list["gene_species"].tolist()
			#parse file and get options and value
			options = []
			for feature in list:
				if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
					options.append({"label": feature.replace("€", "/"), "value": feature})
				else:
					options.append({"label": feature.replace("_", " ").replace("[", "").replace("]", ""), "value": feature})
			if expression_dataset not in ["human", "mouse"]:
				if "lipid" in expression_dataset:
					label = expression_dataset.capitalize().replace("_", " ")
					if expression_dataset == "lipid":
						value = "10-HDoHE"
					else:
						value = "DHA"
				else:
					if "genes" in expression_dataset:
						label = expression_dataset.capitalize().replace("_", " ")
					else:
						label = expression_dataset.capitalize().replace("_", " by ")
					value = options[0]["value"]
			else:
				if expression_dataset == "human":
					value = "GAPDH"
				elif expression_dataset == "mouse":
					value = "Gapdh"
				label = "Host gene"

		#populate children
		children = [
			label, 	
			dcc.Dropdown(
				id="feature_dropdown",
				clearable=False,
				value=value,
				options=options
			)
		]

		return value, options, children, options, options, placeholder, options, placeholder

	#contrast dropdown
	@app.callback(
		Output("contrast_dropdown", "options"),
		Output("contrast_dropdown", "value"),
		Input("feature_dataset_dropdown", "value"),
		Input("comparison_filter_input", "value")
	)
	def get_contrasts(expression_dataset, input_value):
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		
		dge_folder = "data/" + expression_dataset + "/dge"
		dge_files = functions.get_content_from_github(dge_folder)
		contrasts = []
		filtered_contrasts = []
		#get dge files for getting all the contrasts
		for dge_file in dge_files:
			contrast = dge_file.split("/")[-1]
			contrast = contrast.split(".")[0]
			contrasts.append(contrast)
			#if the input is the search bar, then try to filter
			if trigger_id == "comparison_filter_input.value":
				#get lower search values
				input_value = input_value.lower()
				search_values = input_value.split(" ")
				#check search values into the contrast
				number_of_values = len(search_values)
				matches = 0
				for search_value in search_values:
					contrast_lower = contrast.lower()
					condition_1 = contrast_lower.split("-vs-")[0]
					condition_2 = contrast_lower.split("-vs-")[1]
					#all keywords must be present in both conditions
					if search_value in condition_1 and search_value in condition_2:
						matches += 1
				#if all the keyword are in both condition, the add this contrast to the filtered contrasts
				if matches == number_of_values:
					filtered_contrasts.append(contrast)

		#if no filtered contrasts are present, use all the contrast
		if len(filtered_contrasts) != 0:
			contrasts = filtered_contrasts
		
		#define options and default value
		options = []
		for contrast in contrasts:
			options.append({"label": contrast.replace("-", " ").replace("_", " "), "value": contrast})
		value = options[0]["value"]

		return options, value

	#stringecy dropdown
	@app.callback(
		Output("stringency_dropdown", "value"),
		Output("stringency_dropdown", "options"),
		Input("feature_dataset_dropdown", "value")
	)
	def get_stringecy_value(expression_dataset):
		if expression_dataset in ["human", "mouse"]:
			folders = functions.get_content_from_github("data/{}".format(expression_dataset))
			options = []
			#get all dge analyisis performed
			for folder in folders:
				if folder not in ["counts", "dge", "mds", "gsea"]:
					#label will be constructed
					label = ""
					#strincecy type
					stringency_type = folder.split("_")[0]
					if stringency_type == "pvalue":
						label += "P-value "
					else:
						label += "FDR "
					#stringency value
					stringency_value = folder.split("_")[1]
					label += stringency_value
					
					#populate options
					options.append({"label": label, "value": folder})
		
			#default value defined in config file
			value = functions.config["stringecy"]
		else:
			options = [{"label": "P-value 0.05", "value": "pvalue_0.05"}]
			value = "pvalue_0.05"

		return value, options

	#expression or abundance y dropdown
	@app.callback(
		Output("y_boxplot_dropdown", "options"),
		Output("y_boxplot_dropdown", "value"),
		Input("feature_dataset_dropdown", "value"),
		State("y_boxplot_dropdown", "options")
	)
	def get_expression_or_abundance_dropdowns(feature_dataset_dropdown, y_boxplots_dropdown):
		if feature_dataset_dropdown in ["human", "mouse"] or "genes" in feature_dataset_dropdown:
			y_boxplots_dropdown[0] = {"label": "Log2 expression", "value": "log2_expression"}
			value = "log2_expression"
		else:
			y_boxplots_dropdown[0] = {"label": "Log2 abundance", "value": "log2_abundance"}
			value = "log2_abundance"

		return y_boxplots_dropdown, value

	#filter x axis boxplots
	@app.callback(
		Output("x_filter_boxplot_dropdown", "options"),
		Output("x_filter_boxplot_dropdown", "value"),
		Input("x_boxplot_dropdown", "value"),
		Input("y_boxplot_dropdown", "value"),
		Input("feature_dataset_dropdown", "value")
	)
	def get_x_values_boxplots(selected_x, selected_y, feature_dataset):
		
		options, x_values = functions.get_x_axis_elements_boxplots(selected_x, selected_y, feature_dataset)

		return options, x_values

	#filter x axis multiboxplots
	@app.callback(
		Output("x_filter_multiboxplots_dropdown", "options"),
		Output("x_filter_multiboxplots_dropdown", "value"),
		Input("x_multiboxplots_dropdown", "value"),
		Input("y_multiboxplots_dropdown", "value"),
		Input("feature_dataset_dropdown", "value")
	)
	def get_x_values_multiboxplots(selected_x, selected_y, feature_dataset):

		options, x_values = functions.get_x_axis_elements_boxplots(selected_x, selected_y, feature_dataset)

		return options, x_values

	### DOWNLOAD CALLBACKS ###

	#download diffexp
	@app.callback(
		Output("download_diffexp", "href"),
		Output("download_diffexp", "download"),
		Input("download_diffexp_button", "n_clicks"),
		Input("feature_dataset_dropdown", "value"),
		Input("contrast_dropdown", "value")
	)
	def downlaod_diffexp_table(button_click, dataset, contrast):

		#download from GitHub
		df = functions.download_from_github("data/" + dataset + "/dge/" + contrast + ".diffexp.tsv")
		#read the downloaded content and make a pandas dataframe
		df = pd.read_csv(df, sep="\t")
		df = df[["Gene", "Geneid", "log2FoldChange", "lfcSE", "pvalue", "padj", "baseMean"]]

		if dataset not in ["human", "mouse"]:
			df["Gene"] = [x.replace("_", " ").replace("[", "").replace("]", "") for x in df["Gene"]]

		#define dataset specific variables
		if dataset in ["human", "mouse"]:
			base_mean_label = "Average expression"
			gene_id = "Gene ID"
			file_name = "DGE_{}_{}.xls".format(dataset, contrast)
		else:
			base_mean_label = "Average abundance"
			if "lipid" in dataset:
				gene_column_name = dataset.replace("_", " ").capitalize()
				gene_id = "Lipid ID"
				file_name = "DLE_{}_{}.xls".format(dataset, contrast)
			else:
				gene_column_name = dataset.split("_")[1].capitalize()
				gene_id = "Meta ID"
				file_name = "DGE_{}_{}.xls".format(dataset, contrast)
			df = df.rename(columns={"Gene": gene_column_name})

		#rename and sort
		df = df.rename(columns={"Geneid": gene_id, "log2FoldChange": "log2 FC", "lfcSE": "log2 FC SE", "pvalue": "P-value", "padj": "FDR", "baseMean": base_mean_label})
		df = df.sort_values(by=["FDR"])

		#remove a geneid in non human dge
		if dataset not in ["human", "mouse", "lipid", "lipid_id"]:
			df = df[[gene_column_name, "log2 FC", "log2 FC SE", "P-value", "FDR", base_mean_label]]

		#create a downloadable tsv file forced to excel by extension
		link = df.to_csv(index=False, encoding="utf-8", sep="\t")
		link = "data:text/tsv;charset=utf-8," + urllib.parse.quote(link)

		return link, file_name

	#download partial diffexp
	@app.callback(
		Output("download_diffexp_partial", "href"),
		Output("download_diffexp_partial", "download"),
		Output("download_diffexp_button_partial", "disabled"),
		Input("download_diffexp_button_partial", "n_clicks"),
		Input("feature_dataset_dropdown", "value"),
		Input("contrast_dropdown", "value"),
		Input("multi_gene_dge_table_selection_dropdown", "value"),
	)
	def downlaod_diffexp_table_partial(button_click, dataset, contrast, dropdown_values):
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		
		if dropdown_values is None or dropdown_values == [] or trigger_id == "feature_dataset_dropdown.value":
			link = ""
			file_name = ""
			disabled_status = True
		else:
			disabled_status = False
			#download from GitHub
			url = "data/" + dataset + "/dge/" + contrast + ".diffexp.tsv"
			#read the downloaded content and make a pandas dataframe
			df = functions.download_from_github(url)
			df = pd.read_csv(df, sep="\t")
			df = df[["Gene", "Geneid", "log2FoldChange", "lfcSE", "pvalue", "padj", "baseMean"]]

			#filter selected genes
			if dataset not in ["human", "mouse"]:
				df["Gene"] = [x.replace("_", " ").replace("[", "").replace("]", "") for x in df["Gene"]]
				dropdown_values = [value.replace("_", " ").replace("[", "").replace("]", "") for value in dropdown_values]
			else:
				dropdown_values = [value.replace("€", "/") for value in dropdown_values]
			df = df[df["Gene"].isin(dropdown_values)]

			#define dataset specific variables
			if dataset in ["human", "mouse"]:
				base_mean_label = "Average expression"
				id_column = "Gene ID"
				file_name = "DGE_{}_{}_filtered.xls".format(dataset, contrast)
			else:
				base_mean_label = "Average abundance"
				if "lipid" in dataset:
					gene_column_name = dataset.replace("_", " ").capitalize()
					id_column = "Lipid ID"
					file_name = "DLE_{}_{}_filtered.xls".format(dataset, contrast)
				else:
					gene_column_name = dataset.split("_")[1].capitalize()
					id_column = "Gene ID"
					file_name = "DGE_{}_{}_filtered.xls".format(dataset, contrast)
				df = df.rename(columns={"Gene": gene_column_name})

			#rename and sort
			df = df.rename(columns={"Geneid": id_column, "log2FoldChange": "log2 FC", "lfcSE": "log2 FC SE", "pvalue": "P-value", "padj": "FDR", "baseMean": base_mean_label})
			df = df.sort_values(by=["FDR"])

			#remove a geneid in non human dge
			if dataset not in ["human", "mouse", "lipid", "lipid_id"]:
				df = df[[gene_column_name, "log2 FC", "log2 FC SE", "P-value", "FDR", base_mean_label]]

			#create a downloadable tsv file forced to excel by extension
			link = df.to_csv(index=False, encoding="utf-8", sep="\t")
			link = "data:text/tsv;charset=utf-8," + urllib.parse.quote(link)

		return link, file_name, disabled_status

	#download go
	@app.callback(
		Output("download_go", "href"),
		Output("download_go", "download"),
		Input("download_go", "n_clicks"),
		Input("stringency_dropdown", "value"),
		Input("contrast_dropdown", "value"),
		Input("feature_dataset_dropdown", "value"),
		Input("add_gsea_switch", "value")
	)
	def download_go_table(button_click, stringency, contrast, expression_dataset, add_gsea_switch):
		if expression_dataset not in ["human", "mouse", "lipid", "lipid_category"]:
			raise PreventUpdate

		#boolean switch
		boolean_add_gsea_switch = functions.boolean_switch(add_gsea_switch)

		#lipid category does not have GO, load the lipid one instead
		if expression_dataset == "lipid_category":
			expression_dataset = "lipid"

		#download from GitHub
		if expression_dataset in ["human", "mouse"]:
			go_df = functions.download_from_github("data/{}/".format(expression_dataset) + stringency + "/" + contrast + ".merged_go.tsv")
		else:
			go_df = functions.download_from_github("data/{}/".format(expression_dataset) + "lo/" + contrast + ".merged_go.tsv")
		go_df = pd.read_csv(go_df, sep="\t")
		go_df = go_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]

		#concatenate gsea results if the switch is true
		if boolean_add_gsea_switch:
			gsea_df = functions.download_from_github("data/{}/".format(expression_dataset) + "gsea/" + contrast + ".merged_go.tsv")
			gsea_df = pd.read_csv(gsea_df, sep = "\t")
			gsea_df = gsea_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
			go_df = pd.concat([go_df, gsea_df])
		
		if expression_dataset in ["human", "mouse"]:
			process_column = "GO biological process"
			feature_columm = "Genes"
			diff_column = "DEGs"
			go_df = go_df.rename(columns={"Process~name": process_column, "num_of_Genes": diff_column, "gene_group": "Dataset genes", "percentage%": "Enrichment"})
			file_name = "GO_{}.xls".format(contrast)
		else:
			go_df["Genes"] = go_df["Genes"].str.replace(";", "; ")
			go_df["Process~name"] = go_df["Process~name"].str.replace("_", " ")
			process_column = "Functional category"
			feature_columm = "Lipids"
			up_or_down_column = "DLE"
			diff_column = "LSEA DELs"
			go_df = go_df.rename(columns={"DGE": up_or_down_column, "Process~name": process_column, "num_of_Genes": diff_column, "gene_group": "Dataset genes", "percentage%": "Enrichment", "Genes": feature_columm})
			file_name = "LO_{}.xls".format(contrast)

		link = go_df.to_csv(index=False, encoding="utf-8", sep="\t")
		link = "data:text/tsv;charset=utf-8," + urllib.parse.quote(link)
		

		return link, file_name

	#download partial go
	@app.callback(
		Output("download_go_partial", "href"),
		Output("download_go_partial", "download"),
		Output("download_go_button_partial", "disabled"),
		Input("download_go_partial", "n_clicks"),
		Input("contrast_dropdown", "value"),
		Input("go_plot_filter_input", "value"),
		Input("feature_dataset_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("add_gsea_switch", "value")
	)
	def download_partial_go_table(n_clicks, contrast, search_value, expression_dataset, stringency, add_gsea_switch):
		if expression_dataset not in ["human", "mouse", "lipid", "lipid_category"]:
			raise PreventUpdate
		
		#boolean switch
		boolean_add_gsea_switch = functions.boolean_switch(add_gsea_switch)

		#lipid category does not have GO, load the lipid one instead
		if expression_dataset == "lipid_category":
			expression_dataset = "lipid"

		#define search query if present
		if search_value is not None and search_value != "":
			if expression_dataset in ["human", "mouse"]:
				go_df = functions.download_from_github("data/{}/".format(expression_dataset) + stringency + "/" + contrast + ".merged_go.tsv")
			else:
				go_df = functions.download_from_github("data/{}/".format(expression_dataset) + "lo/" + contrast + ".merged_go.tsv")
			go_df = pd.read_csv(go_df, sep="\t")
			go_df = go_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
			
			#concatenate gsea results if the switch is true
			if boolean_add_gsea_switch:
				gsea_df = functions.download_from_github("data/{}/".format(expression_dataset) + "gsea/" + contrast + ".merged_go.tsv")
				gsea_df = pd.read_csv(gsea_df, sep = "\t")
				gsea_df = gsea_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
				go_df = pd.concat([go_df, gsea_df])

			processes_to_keep = functions.serach_go(search_value, go_df, expression_dataset, boolean_add_gsea_switch)

			#filtering
			go_df = go_df[go_df["Process~name"].isin(processes_to_keep)]
			#if there are no categories, disable button
			if go_df.empty:
				disabled_status = True
			else:	
				disabled_status = False

			#add links to amigo for main organism or add spaces for lipids
			if expression_dataset in ["human", "mouse"]:
				process_column = "GO biological process"
				feature_columm = "Genes"
				diff_column = "DEGs"
				go_df = go_df.rename(columns={"Process~name": process_column, "num_of_Genes": diff_column, "gene_group": "Dataset genes", "percentage%": "Enrichment"})
				file_name = "GO_{}_filtered.xls".format(contrast)
			else:	
				go_df["Genes"] = go_df["Genes"].str.replace(";", "; ")
				go_df["Process~name"] = go_df["Process~name"].str.replace("_", " ")
				process_column = "Functional category"
				feature_columm = "Lipids"
				up_or_down_column = "DLE"
				diff_column = "LSEA DELs"
				go_df = go_df.rename(columns={"DGE": up_or_down_column, "Process~name": process_column, "num_of_Genes": diff_column, "gene_group": "Dataset genes", "percentage%": "Enrichment", "Genes": feature_columm})
				file_name = "LO_{}_filtered.xls".format(contrast)

			link = go_df.to_csv(index=False, encoding="utf-8", sep="\t")
			link = "data:text/tsv;charset=utf-8," + urllib.parse.quote(link)
		else:
			link = ""
			file_name = ""
			disabled_status = True

		return link, file_name, disabled_status

	### TABLES ###

	#dge table filtered by multidropdown
	@app.callback(
		Output("dge_table_filtered", "columns"),
		Output("dge_table_filtered", "data"),
		Output("dge_table_filtered", "style_data_conditional"),
		Output("filtered_dge_table_div", "hidden"),
		Input("multi_gene_dge_table_selection_dropdown", "value"),
		Input("contrast_dropdown", "value"),
		Input("feature_dataset_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("target_prioritization_switch", "value")
	)
	def display_filtered_dge_table(dropdown_values, contrast, dataset, fdr, target_prioritization):
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		boolean_target_prioritization = functions.boolean_switch(target_prioritization)
		
		if dropdown_values is None or dropdown_values == [] or trigger_id == "feature_dataset_dropdown.value":
			hidden_div = True
			columns = []
			data = [{}]
			style_data_conditional = []
		else:
			hidden_div = False
			#open tsv
			table = functions.download_from_github("data/" + dataset + "/dge/" + contrast + ".diffexp.tsv")
			table = pd.read_csv(table, sep = "\t")

			#filter selected genes
			if dataset not in ["human", "mouse"]:
				table["Gene"] = [x.replace("_", " ").replace("[", "").replace("]", "") for x in table["Gene"]]
				dropdown_values = [value.replace("_", " ").replace("[", "").replace("]", "") for value in dropdown_values]
			else:
				dropdown_values = [value.replace("€", "/")for value in dropdown_values]
			table = table[table["Gene"].isin(dropdown_values)]

			columns, data, style_data_conditional = functions.dge_table_operations(table, dataset, fdr, boolean_target_prioritization)

		return columns, data, style_data_conditional, hidden_div

	#dge table full
	@app.callback(
		Output("dge_table", "columns"),
		Output("dge_table", "data"),
		Output("dge_table", "style_data_conditional"),
		Input("contrast_dropdown", "value"),
		Input("feature_dataset_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("target_prioritization_switch", "value")
	)
	def display_dge_table(contrast, dataset, strincency, target_prioritization):
		#open tsv
		table = functions.download_from_github("data/" + dataset + "/dge/" + contrast + ".diffexp.tsv")
		table = pd.read_csv(table, sep = "\t")
		
		boolean_target_prioritization = functions.boolean_switch(target_prioritization)
		
		columns, data, style_data_conditional = functions.dge_table_operations(table, dataset, strincency, boolean_target_prioritization)

		return columns, data, style_data_conditional

	#go table
	@app.callback(
		Output("go_table", "columns"),
		Output("go_table", "data"),
		Input("contrast_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("go_plot_filter_input", "value"),
		Input("feature_dataset_dropdown", "value"),
		Input("add_gsea_switch", "value")
	)
	def display_go_table(contrast, stringency, search_value, expression_dataset, add_gsea_switch):
		if expression_dataset not in ["human", "mouse", "lipid", "lipid_category"]:
			raise PreventUpdate
		
		#boolean switch
		boolean_add_gsea_switch = functions.boolean_switch(add_gsea_switch)

		#lipid category does not have GO, load the lipid one instead
		if expression_dataset == "lipid_category":
			expression_dataset = "lipid"
		
		if expression_dataset in ["human", "mouse"]:
			go_df = functions.download_from_github("data/{}/".format(expression_dataset) + stringency + "/" + contrast + ".merged_go.tsv")
		else:
			go_df = functions.download_from_github("data/{}/".format(expression_dataset) + "lo/" + contrast + ".merged_go.tsv")
		go_df = pd.read_csv(go_df, sep="\t")
		go_df = go_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
		#concatenate gsea results if the switch is true
		if boolean_add_gsea_switch:
			gsea_df = functions.download_from_github("data/{}/".format(expression_dataset) + "gsea/" + contrast + ".merged_go.tsv")
			gsea_df = pd.read_csv(gsea_df, sep = "\t")
			gsea_df = gsea_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
			gsea_df["Genes"] = gsea_df["Genes"].str.replace(";", "; ")
			go_df = pd.concat([go_df, gsea_df])

		#define search query if present
		if search_value is not None and search_value != "":
			processes_to_keep = functions.serach_go(search_value, go_df, expression_dataset, boolean_add_gsea_switch)
			#filtering
			go_df = go_df[go_df["Process~name"].isin(processes_to_keep)]

		#add links to amigo for main organism or add spaces for lipids
		if expression_dataset in ["human", "mouse"]:
			go_df["Process~name"] = ["[{}](".format(process) + str("http://amigo.geneontology.org/amigo/term/") + process.split("~")[0] + ")" for process in go_df["Process~name"]]
			process_column = "GO biological process"
			feature_columm = "Genes"
			up_or_down_column = "DGE"
			diff_column = "DEGs"
			go_df = go_df.rename(columns={"Process~name": process_column, "num_of_Genes": diff_column, "gene_group": "Dataset genes", "percentage%": "Enrichment"})
		else:	
			go_df["Genes"] = go_df["Genes"].str.replace(";", "; ")
			go_df["Process~name"] = go_df["Process~name"].str.replace("_", " ")
			process_column = "Functional category"
			feature_columm = "Lipids"
			up_or_down_column = "DLE"
			diff_column = "LSEA DELs"
			go_df = go_df.rename(columns={"DGE": up_or_down_column, "Process~name": process_column, "num_of_Genes": diff_column, "gene_group": "Dataset genes", "percentage%": "Enrichment", "Genes": feature_columm})

		columns = [
			{"name": up_or_down_column, "id": up_or_down_column}, 
			{"name": feature_columm, "id": feature_columm},
			{"name": process_column, "id": process_column, "type": "text", "presentation": "markdown"},
			{"name": diff_column, "id": diff_column},
			{"name": "Dataset genes", "id":"Dataset genes"},
			{"name": "Enrichment", "id":"Enrichment", "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed)},
			{"name": "P-value", "id":"P-value", "type": "numeric", "format": Format(precision=2, scheme=Scheme.decimal_or_exponent)}
			]
		data = go_df.to_dict("records")

		return columns, data

	##### plots #####

	#mds metadata
	@app.callback(
		Output("mds_metadata", "figure"),
		Output("mds_metadata", "config"),
		Output("mds_metadata_div", "style"),
		Input("mds_dataset", "value"),
		Input("mds_type", "value"),
		Input("metadata_dropdown", "value"),
		Input("mds_expression", "relayoutData"),
		Input("comparison_only_mds_metadata_switch", "value"),
		Input("hide_unselected_mds_metadata_switch", "value"),
		Input("contrast_dropdown", "value"),
		Input("mds_metadata", "relayoutData"),
		Input("mds_metadata", "restyleData"),
		State("mds_metadata", "figure"),
		State("mds_expression", "figure"),
	)
	def plot_mds_metadata(mds_dataset, mds_type, metadata_to_plot, zoom_mds_expression, comparison_only_switch, hide_unselected_switch, contrast, legend_mds_metadata_click, zoom_mds_metadata, mds_metadata_fig, mds_expression_fig):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		height = 400

		#boolean switches
		boolean_comparison_only_switch = functions.boolean_switch(comparison_only_switch)
		boolean_hide_unselected_switch = functions.boolean_switch(hide_unselected_switch)
		
		#do not update the plot for change in contrast if the switch is off
		if trigger_id == "contrast_dropdown.value" and boolean_comparison_only_switch is False:
			raise PreventUpdate

		#open metadata
		metadata_df = functions.download_from_github("metadata.tsv")
		metadata_df = pd.read_csv(metadata_df, sep = "\t")

		#change dataset or metadata: create a new figure from tsv
		if trigger_id in ["mds_type.value", "mds_dataset.value", "metadata_dropdown.value", "comparison_only_mds_metadata_switch.value", "contrast_dropdown.value"] or mds_metadata_fig is None:
			
			#preserve old zoom
			keep_old_zoom = False
			if mds_metadata_fig is not None and trigger_id not in ["mds_type.value", "mds_dataset.value", "comparison_only_mds_metadata_switch.value", "contrast_dropdown.value"]:
				xaxis_range = mds_metadata_fig["layout"]["xaxis"]["range"]
				yaxis_range = mds_metadata_fig["layout"]["yaxis"]["range"]
				keep_old_zoom = True

			#create figure from tsv
			mds_metadata_fig = go.Figure()
			if str(metadata_df.dtypes[metadata_to_plot]) == "object":
				mds_metadata_fig = functions.plot_mds_discrete(mds_type, mds_dataset, metadata_to_plot, mds_metadata_fig, height, label_to_value, boolean_comparison_only_switch, contrast)
			else:
				variable_to_plot = [metadata_to_plot]
				#get msd df
				mds_df = functions.download_from_github("data/" + mds_dataset + "/mds/" + mds_type + ".tsv")
				mds_df = pd.read_csv(mds_df, sep = "\t")
				#comparison only will filter the samples
				if boolean_comparison_only_switch:
					mds_df = mds_df[mds_df["condition"].isin(contrast.split("-vs-"))]
				color = functions.get_color(metadata_to_plot, "continuous")
				mds_metadata_fig = functions.plot_mds_continuous(mds_df, mds_type, variable_to_plot, color, mds_metadata_fig, height, label_to_value)

			#apply old zoom if present
			if keep_old_zoom:
				mds_metadata_fig["layout"]["xaxis"]["range"] = xaxis_range
				mds_metadata_fig["layout"]["yaxis"]["range"] = yaxis_range
				mds_metadata_fig["layout"]["xaxis"]["autorange"] = False
				mds_metadata_fig["layout"]["yaxis"]["autorange"] = False
		
		#change umap expression means just to update the zoom
		elif trigger_id == "mds_expression.relayoutData" and mds_expression_fig is not None:
			mds_metadata_fig = functions.synchronize_zoom(mds_metadata_fig, mds_expression_fig)
		
		#get number of displayed samples
		n_samples_mds_metadata = functions.get_displayed_samples(mds_metadata_fig)

		#labels for graph title
		if "lipid" in mds_dataset:
			omics = "lipidome"
			subdirs = functions.get_content_from_github("data")
			if "human" in subdirs:
				mds_title = "human"
			elif "mouse" in subdirs:
				mds_title = "mouse"
		else:
			omics = "transcriptome"
		if mds_dataset in ["human", "mouse"]:
			mds_title = mds_dataset
		elif "archaea" in mds_dataset:
			mds_title = "archaeal " + mds_dataset.split("_")[1]
		elif "bacteria" in mds_dataset:
			mds_title = "bacterial " + mds_dataset.split("_")[1]
		elif "eukaryota" in mds_dataset:
			mds_title = "eukaryota " + mds_dataset.split("_")[1]
		elif "viruses" in mds_dataset:
			mds_title = "viral " + mds_dataset.split("_")[1]

		#apply title
		mds_metadata_fig["layout"]["title"]["text"] = "Sample dispersion within<br>the " + mds_title + " " + omics + " MDS<br>colored by " + metadata_to_plot.replace("_", " ") + " metadata n=" + str(n_samples_mds_metadata)


		#hide unselected legend items
		if boolean_hide_unselected_switch:
			mds_metadata_fig["layout"]["legend"]["itemclick"] = False
			mds_metadata_fig["layout"]["legend"]["itemdoubleclick"] = False
			for trace in mds_metadata_fig["data"]:
				if trace["visible"] == "legendonly":
					trace["visible"] = False
		else:
			mds_metadata_fig["layout"]["legend"]["itemclick"] = "toggle"
			mds_metadata_fig["layout"]["legend"]["itemdoubleclick"] = "toggleothers"
			for trace in mds_metadata_fig["data"]:
				if trace["visible"] is False :
					trace["visible"] = "legendonly"

		#div style
		if str(metadata_df.dtypes[metadata_to_plot]) == "object":
			mds_metadata_div_style = {"width": "45%", "display": "inline-block"}
		else:
			mds_metadata_div_style = {"width": "33.5%", "display": "inline-block"}

		##### CONFIG OPTIONS ####
		config_mds_metadata = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5, "filename": "mds_{mds_metadata}_colored_by_{metadata}".format(mds_metadata = mds_dataset, metadata = metadata_to_plot)}}

		return mds_metadata_fig, config_mds_metadata, mds_metadata_div_style

	#mds feature
	@app.callback(
		Output("mds_expression", "figure"),
		Output("mds_expression", "config"),
		Output("mds_expression_div", "style"),
		Input("mds_dataset", "value"),
		Input("mds_type", "value"),
		Input("feature_dataset_dropdown", "value"),
		Input("feature_dropdown", "value"),
		Input("mds_metadata", "relayoutData"),
		Input("mds_metadata", "restyleData"),
		Input("mds_metadata", "figure"),
		State("mds_expression", "figure"),
		prevent_initial_call=True
	)
	def plot_mds_feature(mds_dataset, mds_type, expression_dataset, feature, zoom_mds_metadata, legend_click, mds_metadata_fig, mds_expression_fig):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		height = 400

		#change umap dataset, expression dataset or gene/species: create a new figure from tsv
		if trigger_id in ["mds_type.value", "mds_dataset.value", "feature_dataset_dropdown.value", "feature_dropdown.value", "mds_metadata.figure", "mds_metadata.restyleData"] or mds_expression_fig is None:

			#get samples to keep
			samples_to_keep = []
			#parse metadata figure data 
			for trace in mds_metadata_fig["data"]:
				if trace["visible"] is True:
					for dot in trace["customdata"]:
						#stores samples to keep after filtering
						samples_to_keep.append(dot[0])
			variable_to_plot = [expression_dataset, feature, samples_to_keep]
			#create figure
			mds_expression_fig = go.Figure()
			#get msd df
			mds_df = functions.download_from_github("data/" + mds_dataset + "/mds/" + mds_type + ".tsv")
			mds_df = pd.read_csv(mds_df, sep = "\t")
			color = functions.get_color("Log2 expression", "continuous")
			mds_expression_fig = functions.plot_mds_continuous(mds_df, mds_type, variable_to_plot, color, mds_expression_fig, height, label_to_value)

		#update zoom
		mds_metadata_fig = functions.synchronize_zoom(mds_expression_fig, mds_metadata_fig)

		#get number of displayed samples
		n_samples_mds_expression = functions.get_displayed_samples(mds_metadata_fig)

		#labels for graph title
		if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
			expression_or_abundance = " expression"
		else:
			expression_or_abundance = " abundance"

		#labels for graph title
		if "lipid" in mds_dataset:
			omics = "lipidome"
			subdirs = functions.get_content_from_github("data")
			if "human" in subdirs:
				mds_title = "human"
			elif "mouse" in subdirs:
				mds_title = "mouse"
		else:
			omics = "transcriptome"
		if mds_dataset in ["human", "mouse"]:
			mds_title = mds_dataset
		elif "archaea" in mds_dataset:
			mds_title = "archaeal " + mds_dataset.split("_")[1]
		elif "bacteria" in mds_dataset:
			mds_title = "bacterial " + mds_dataset.split("_")[1]
		elif "eukaryota" in mds_dataset:
			mds_title = "eukaryota " + mds_dataset.split("_")[1]
		elif "viruses" in mds_dataset:
			mds_title = "viral " + mds_dataset.split("_")[1]

		#apply title
		mds_expression_fig["layout"]["title"]["text"] = "Sample dispersion within<br>the " + mds_title + " " + omics + " MDS<br>colored by " + feature.replace("_", " ").replace("[", "").replace("]", "").replace("€", "/") + expression_or_abundance + " n=" + str(n_samples_mds_expression)

		##### CONFIG OPTIONS ####
		config_mds_expression = {"doubleClick": "autosize", "modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5, "filename": "mds_{mds_metadata}_colored_by_{gene_species}_{expression_abundance}".format(mds_metadata = mds_dataset, gene_species = feature, expression_abundance = expression_or_abundance)}}
		mds_expression_div_style = {"width": "34.5%", "display": "inline-block"}

		return mds_expression_fig, config_mds_expression, mds_expression_div_style

	#boxplots
	@app.callback(
		Output("boxplots_graph", "figure"),
		Output("boxplots_graph", "config"),
		Output("x_filter_dropdown_div", "hidden"),
		Output("hide_unselected_boxplot_switch", "value"),
		Output("boxplots_width_slider", "value"),
		Output("boxplots_height_slider", "value"),
		Input("feature_dataset_dropdown", "value"),
		Input("feature_dropdown", "value"),
		Input("x_boxplot_dropdown", "value"),
		Input("x_filter_boxplot_dropdown", "value"),
		Input("group_by_boxplot_dropdown", "value"),
		Input("y_boxplot_dropdown", "value"),
		Input("comparison_only_boxplots_switch", "value"),
		Input("contrast_dropdown", "value"),
		Input("hide_unselected_boxplot_switch", "value"),
		Input("show_as_boxplot_switch", "value"),
		Input("boxplots_width_slider", "value"),
		Input("boxplots_height_slider", "value"),
		State("boxplots_graph", "figure"),
		State("x_filter_dropdown_div", "hidden"),
	)
	def plot_boxplots(expression_dataset, feature, x_metadata, selected_x_values, group_by_metadata, y_metadata, comparison_only_switch, contrast, hide_unselected_switch, show_as_boxplot, width, height, box_fig, hidden):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#boolean switch
		boolean_comparison_only_switch = functions.boolean_switch(comparison_only_switch)
		boolean_hide_unselected_switch = functions.boolean_switch(hide_unselected_switch)
		boolean_show_as_boxplot = functions.boolean_switch(show_as_boxplot)

		#do not update the plot for change in contrast if the switch is off
		if trigger_id == "contrast_dropdown.value" and boolean_comparison_only_switch is False and box_fig is not None:
			raise PreventUpdate

		#labels
		if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
			expression_or_abundance = "expression"
			log2_expression_or_abundance = "Log2 expression"
		else:
			expression_or_abundance = "abundance"
			log2_expression_or_abundance = "Log2 abundance"

		#slider resize
		if trigger_id in ["boxplots_height_slider.value", "boxplots_width_slider.value"]:
			box_fig["layout"]["height"] = height
			box_fig["layout"]["width"] = width
			if width < 600:
				if "abundance" in box_fig["layout"]["title"]["text"]:
					box_fig["layout"]["title"]["text"] = box_fig["layout"]["title"]["text"].replace(" abundance", "<br>abundance")
				else:
					box_fig["layout"]["title"]["text"] = box_fig["layout"]["title"]["text"].replace("profile ", "profile<br>")
		#new plot
		else:
			if trigger_id != "hide_unselected_boxplot_switch.value":
				#open metadata
				metadata_df = functions.download_from_github("metadata.tsv")
				metadata_df = pd.read_csv(metadata_df, sep = "\t")

				#clean metadata
				metadata_df = metadata_df.fillna("NA")
				metadata_df = metadata_df.replace("_", " ", regex=True)

				#filter samples for comparison
				if boolean_comparison_only_switch:
					contrast = contrast.replace("_", " ")
					metadata_df = metadata_df[metadata_df["condition"].isin(contrast.split("-vs-"))]

				#counts as y need external file with count values
				if y_metadata in ["log2_expression", "log2_abundance"]:
					counts = functions.download_from_github("data/" + expression_dataset + "/counts/" + feature + ".tsv")
					counts = pd.read_csv(counts, sep = "\t")
					counts = counts.replace("_", " ", regex=True)
					#merge and compute log2 and replace inf with 0
					metadata_df = metadata_df.merge(counts, how="inner", on="sample")
					metadata_df[log2_expression_or_abundance] = np.log2(metadata_df["counts"])
					metadata_df[log2_expression_or_abundance].replace(to_replace = -np.inf, value = 0, inplace=True)

				#get trace names
				if x_metadata == group_by_metadata:
					column_for_filtering = x_metadata
					#user defined list of condition
					if x_metadata == "condition" and config["sorted_conditions"]:
						metadata_fields_ordered = config["condition_list"]
						metadata_fields_ordered = [condition.replace("_", " ") for condition in metadata_fields_ordered]
					else:
						metadata_fields_ordered = metadata_df[x_metadata].unique().tolist()
						metadata_fields_ordered.sort()
				else:
					column_for_filtering = group_by_metadata
					metadata_fields_ordered = metadata_df[group_by_metadata].unique().tolist()
					metadata_fields_ordered.sort()

				#changing the gene does not reset the figure
				if trigger_id == "feature_dropdown.value":
					visible = {}
					for trace in box_fig["data"]:
						visible[trace["name"]] = trace["visible"]
				#if there is a change in the plot beside the gene, reset the figure 
				else:
					hide_unselected_switch = []
					boolean_hide_unselected_switch = False
					if trigger_id != "comparison_only_boxplots_switch.value":
						width = 900
						height = 375
					visible = {}
					for metadata in metadata_fields_ordered:
						visible[metadata] = True

				#grouped or not boxplot setup
				boxmode = "overlay"
				hidden = True
				#get values that will be on the x axis
				all_x_values = metadata_df[x_metadata].unique().tolist()
				for x_value in all_x_values:
					if boxmode != "group":
						#filter df for x_value and get his traces
						filtered_metadata = metadata_df[metadata_df[x_metadata] == x_value]
						values_column_for_filtering = filtered_metadata[column_for_filtering].unique().tolist()
						#if, for the same x, there is more than one trace, then should be grouped
						if len(set(values_column_for_filtering)) > 1:
							boxmode = "group"
							hidden = False
							#keep only selected x_values
							selected_x_values = [x_value.replace("_", " ") for x_value in selected_x_values]
							metadata_df = metadata_df[metadata_df[x_metadata].isin(selected_x_values)]
				
				#create figure
				box_fig = go.Figure()
				for metadata in metadata_fields_ordered:
					#slice metadata
					filtered_metadata = metadata_df[metadata_df[column_for_filtering] == metadata]
					#only 2 decimals
					filtered_metadata = filtered_metadata.round(2)
					#get x and y
					if y_metadata in ["log2_expression", "log2_abundance"]:
						y_values = filtered_metadata[log2_expression_or_abundance]
						y_axis_title = "Log2 {}".format(expression_or_abundance)
						title_text = feature.replace("_", " ").replace("[", "").replace("]", "").replace("€", "/") + " {} profile per ".format(expression_or_abundance) + x_metadata.replace("_", " ").capitalize()
					else:
						y_values = filtered_metadata[y_metadata]
						y_axis_title = y_metadata
						title_text = "{y_metadata} profile per {x_metadata}".format(y_metadata=y_metadata, x_metadata=x_metadata.replace("_", " ").capitalize())
					x_values = filtered_metadata[x_metadata]

					#create hovertext
					filtered_metadata["hovertext"] = ""
					for column in filtered_metadata.columns:
						if column not in ["control", "counts", "hovertext", "fq1", "fq2", "raw_counts", "kraken2", "immune_profiling_vdj"]:
							filtered_metadata["hovertext"] = filtered_metadata["hovertext"] + column.replace("_", " ").capitalize() + ": " + filtered_metadata[column].astype(str) + "<br>"
					hovertext = filtered_metadata["hovertext"].tolist()

					#create traces
					marker_color = functions.get_color(column_for_filtering, metadata)
					
					if boolean_show_as_boxplot: 
						box_fig.add_trace(go.Box(y=y_values, x=x_values, name=metadata, marker_color=marker_color, boxpoints="all", hovertext=hovertext, hoverinfo="text", marker_size=3, line_width=4, visible=visible[metadata]))
					else:
						box_fig.add_trace(go.Violin(y=y_values, x=x_values, name=metadata, marker_color=marker_color, hovertext=hovertext, hoverinfo="text", marker_size=3, line_width=4, visible=visible[metadata], points="all"))

				#figure layout
				if width < 600:
					if "abundance" in box_fig["layout"]["title"]["text"]:
						box_fig["layout"]["title"]["text"] = box_fig["layout"]["title"]["text"].replace(" abundance", "<br>abundance")
					else:
						box_fig["layout"]["title"]["text"] = box_fig["layout"]["title"]["text"].replace("profile ", "profile<br>")
				if boolean_show_as_boxplot:
					box_fig.update_layout(title = {"text": title_text, "x": 0.5, "xanchor": "center", "xref": "paper", "font_size": 14, "y": 0.95}, legend_title_text=group_by_metadata.capitalize(), legend_yanchor="top", legend_y=1.2, yaxis_title=y_axis_title, xaxis_automargin=True, xaxis_tickangle=-90, yaxis_automargin=True, font_family="Arial", width=width, height=height, margin=dict(t=45, b=50, l=5, r=10), boxmode=boxmode, showlegend=True)
				else:
					box_fig.update_layout(title = {"text": title_text, "x": 0.5, "xanchor": "center", "xref": "paper", "font_size": 14, "y": 0.95}, legend_title_text=group_by_metadata.capitalize(), legend_yanchor="top", legend_y=1.2, yaxis_title=y_axis_title, xaxis_automargin=True, xaxis_tickangle=-90, yaxis_automargin=True, font_family="Arial", width=width, height=height, margin=dict(t=45, b=50, l=5, r=10), violinmode=boxmode, showlegend=True)
			else:
				box_fig = go.Figure(box_fig)

			#when the switch is true, the legend is no longer interactive
			if boolean_hide_unselected_switch:
				box_fig.update_layout(legend_itemclick=False, legend_itemdoubleclick=False)
				for trace in box_fig["data"]:
					if trace["visible"] == "legendonly":
						trace["visible"] = False
			else:
				box_fig.update_layout(legend_itemclick="toggle", legend_itemdoubleclick="toggleothers")
				for trace in box_fig["data"]:
					if trace["visible"] is False:
						trace["visible"] = "legendonly"

		#general config for boxplots
		config_boxplots = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5, "filename": "boxplots_with_{feature}_{expression_or_abundance}_colored_by_{metadata}".format(feature=feature.replace("€", "_"), expression_or_abundance=expression_or_abundance, metadata=x_metadata)}}

		#box_fig["layout"]["paper_bgcolor"] = "#BCBDDC"

		return box_fig, config_boxplots, hidden, hide_unselected_switch, width, height

	#MA-plot
	@app.callback(
		Output("ma_plot_graph", "figure"),
		Output("ma_plot_graph", "config"),
		Input("feature_dataset_dropdown", "value"),
		Input("contrast_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("feature_dropdown", "value"),
		State("ma_plot_graph", "figure")
	)
	def plot_MA_plot(expression_dataset, contrast, stringecy_info, gene, old_ma_plot_figure):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#stingency specs
		pvalue_type = stringecy_info.split("_")[0]
		pvalue_value = stringecy_info.split("_")[1]

		#labels
		if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
			gene = gene.replace("€", "/")
			gene_or_species = "Gene"
			expression_or_abundance = "gene expression"
			xaxis_title = "Log2 average expression"
		else:
			gene = gene.replace("_", " ").replace("[", "").replace("]", "")
			xaxis_title = "Log2 average abundance"
			if "lipid" in expression_dataset:
				gene_or_species = expression_dataset.replace("_", " ")
			else:
				gene_or_species = expression_dataset.split("_")[1]
			expression_or_abundance = gene_or_species + " abundance"
			gene_or_species = gene_or_species

		#read tsv if change in dataset or contrast
		if trigger_id in ["feature_dataset_dropdown.value", "contrast_dropdown.value"] or old_ma_plot_figure is None:
			table = functions.download_from_github("data/" + expression_dataset + "/dge/" + contrast + ".diffexp.tsv")
			table = pd.read_csv(table, sep = "\t")
			table["Gene"] = table["Gene"].fillna("NA")
			#log2 base mean
			table["log2_baseMean"] = np.log2(table["baseMean"])
			#clean gene/species name
			if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
				table["Gene"] = [i for i in table["Gene"]]
			else:
				table["Gene"] = [i.replace("_", " ").replace("[", "").replace("]", "") for i in table["Gene"]]

		#parse existing figure for change in stringency or gene
		elif trigger_id in ["stringency_dropdown.value", "feature_dropdown.value"] and old_ma_plot_figure is not None:
			figure_data = {}
			figure_data["Gene"] = []
			figure_data[pvalue_type] = []
			figure_data["log2_baseMean"] = []
			figure_data["log2FoldChange"] = []

			for trace in range(0, len(old_ma_plot_figure["data"])):
				figure_data["log2_baseMean"].extend(old_ma_plot_figure["data"][trace]["x"])
				figure_data["log2FoldChange"].extend(old_ma_plot_figure["data"][trace]["y"])
				for dot in old_ma_plot_figure["data"][trace]["customdata"]:
					figure_data["Gene"].append(dot[0])
					if dot[1] == "NA":
						dot[1] = np.nan
					figure_data[pvalue_type].append(dot[1])
			
			table = pd.DataFrame(figure_data)

		#find DEGs and selected gene
		table.loc[(table[pvalue_type] <= float(pvalue_value)) & (table["log2FoldChange"] > 0) & (table["Gene"] != gene), "DEG"] = "Up"
		table.loc[(table[pvalue_type] <= float(pvalue_value)) & (table["log2FoldChange"] < 0) & (table["Gene"] != gene), "DEG"] = "Down"
		table.loc[(table[pvalue_type] <= float(pvalue_value)) & (table["log2FoldChange"] > 0) & (table["Gene"] == gene), "DEG"] = "selected_Up"
		table.loc[(table[pvalue_type] <= float(pvalue_value)) & (table["log2FoldChange"] < 0) & (table["Gene"] == gene), "DEG"] = "selected_Down"
		table.loc[(table["DEG"].isnull()) & (table["Gene"] != gene), "DEG"] = "no_DEG"
		table.loc[(table["DEG"].isnull()) & (table["Gene"] == gene), "DEG"] = "selected_no_DEG"

		#replace nan values with NA
		table = table.fillna(value={pvalue_type: "NA"})

		#count DEGs
		up = table[table["DEG"] == "Up"]
		up = len(up["Gene"])
		up_selected = table[table["DEG"] == "selected_Up"]
		up += len(up_selected["Gene"])
		down = table[table["DEG"] == "Down"]
		down = len(down["Gene"])
		down_selected = table[table["DEG"] == "selected_Down"]
		down += len(down_selected["Gene"])

		#find out if the selected gene have more than 1 gene ID
		filtered_table = table[table["Gene"] == gene]
		number_of_geneids_for_gene = len(filtered_table["Gene"])

		#if there are more gene ID for the same gene, a warning should appear on the ceneter of the plot
		if number_of_geneids_for_gene > 1:
			max_x = table["log2_baseMean"].max()
			min_x = table["log2_baseMean"].min()
			mid_x = (max_x + min_x)/2 
			max_y = table["log2FoldChange"].max()
			min_y = table["log2FoldChange"].min()
			mid_y = (max_y + min_y)/2

		#colors for plot traces (gray, red, blue)
		colors_ma_plot = ["#636363", "#D7301F", "#045A8D", "#636363", "#D7301F", "#045A8D"]
		colors_ma_plot = {"no_deg": "#636363", "down": "#045A8D", "up": "#D7301F", "selected": "#D9D9D9"}
		#rename column if not human
		if expression_dataset not in ["human", "mouse"]:
			table = table.rename(columns={"Gene": gene_or_species})

		#plot
		ma_plot_fig = go.Figure()
		for deg_status in ["no_DEG", "Up", "Down", "selected_no_DEG", "selected_Up", "selected_Down"]:
			#params for trace
			if "selected" in deg_status:
				marker_size = 9
				marker_line = {"color": "#525252", "width": 2}
				color = colors_ma_plot["selected"]
			else:	
				marker_size = 5
				marker_line = {"color": None, "width": None}
				if "up" in deg_status.lower():
					color = colors_ma_plot["up"]
				elif "down" in deg_status.lower():
					color = colors_ma_plot["down"]
				else:
					color = colors_ma_plot["no_deg"]
			filtered_table = table[table["DEG"] == deg_status]
			#custom data and hover template
			custom_data = filtered_table[[gene_or_species, pvalue_type, "log2_baseMean", "log2FoldChange"]]
			custom_data = custom_data.fillna("NA")
			if pvalue_type == "padj":
				pvalue_type_for_labels = "FDR"
			else:
				pvalue_type_for_labels = "P-value"
			hover_template = gene_or_species.capitalize() + ": %{{customdata[0]}}<br>{pvalue_type}: %{{customdata[1]:.2e}}<br>{expression_or_abundance}: %{{x:.2e}}<br>Log2 fold change: %{{y:.2e}}<extra></extra>".format(expression_or_abundance=xaxis_title, pvalue_type=pvalue_type_for_labels)
			
			#add trace
			ma_plot_fig.add_trace(go.Scattergl(x=filtered_table["log2_baseMean"], y=filtered_table["log2FoldChange"], marker_opacity=1, marker_color=color, marker_symbol=2, marker_size=marker_size, marker_line=marker_line, customdata=custom_data, mode="markers", hovertemplate = hover_template))

		#update layout
		title_text = "Differential {expression_or_abundance} {pvalue_type} < ".format(expression_or_abundance=expression_or_abundance, pvalue_type=pvalue_type_for_labels) + str(float(pvalue_value)) + "<br>" + contrast.replace("_", " ").replace("-", " ").replace("Control", "Control")
		
		ma_plot_fig.update_layout(title={"text": title_text, "xref": "paper", "x": 0.5, "font_size": 13}, xaxis_automargin=True, xaxis_title=xaxis_title, yaxis_zeroline=True, yaxis_automargin=True, yaxis_title="Log2 fold change", yaxis_domain=[0.25, 1], font_family="Arial", height=415, margin=dict(t=50, b=5, l=5, r=5), showlegend=False)

		#annotations
		up_genes_annotation = [dict(text = str(up) + " higher in<br>" + contrast.split("-vs-")[0].replace("_", " "), align="right", xref="paper", yref="paper", x=0.98, y=0.98, showarrow=False, font=dict(size=14, color="#DE2D26", family="Arial"))]
		down_genes_annotation = [dict(text = str(down) + " higher in<br>" + contrast.split("-vs-")[1].replace("_", " "), align="right", xref="paper", yref="paper", x=0.98, y=0.25, showarrow=False, font=dict(size=14, color="#045A8D", family="Arial"))]
		annotaton_title = [dict(text = "Show annotations", align="center", xref="paper", yref="paper", x=0, y=0, showarrow=False, font_size=12)]
		if number_of_geneids_for_gene == 1:
			for i in [3, 4, 5]:
				if len(ma_plot_fig["data"][i]["x"]) == 1:
					feature_name = ma_plot_fig["data"][i]["customdata"][0][0]
					feature_fdr = ma_plot_fig["data"][i]["customdata"][0][1]
					if feature_fdr != "NA":
						feature_fdr = "{:.1e}".format(feature_fdr)
					feature_log2_base_mean = ma_plot_fig["data"][i]["customdata"][0][2]
					feature_log2fc = ma_plot_fig["data"][i]["customdata"][0][3]
					x = ma_plot_fig["data"][i]["x"][0]
					y = ma_plot_fig["data"][i]["y"][0]
					selected_gene_annotation = [dict(x=x, y=y, xref="x", yref="y", text=feature_name + "<br>Log2 avg expr: " +  str(round(feature_log2_base_mean, 1)) + "<br>Log2 FC: " +  str(round(feature_log2fc, 1)) + "<br>{pvalue_type}: ".format(pvalue_type=pvalue_type_for_labels) + feature_fdr, showarrow=True, font=dict(family="Arial", size=12, color="#252525"), align="center", arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#525252", ax=50, ay=50, bordercolor="#525252", borderwidth=2, borderpad=4, bgcolor="#D9D9D9", opacity=0.9)]
		else:
			selected_gene_annotation = [dict(x=mid_x, y=mid_y, text="Multiple transcripts with the same gene name.", showarrow=False, font=dict(family="Arial", size=12, color="#252525"), align="center", bordercolor="#525252", borderwidth=2, borderpad=4, bgcolor="#D9D9D9", opacity=0.9)]

		#add default annotations
		ma_plot_fig["layout"]["annotations"] = annotaton_title + up_genes_annotation + down_genes_annotation + selected_gene_annotation

		#buttons
		ma_plot_fig.update_layout(updatemenus=[dict(
			pad=dict(r=5),
			active=0,
			xanchor = "left",
			direction = "up",
			x=0,
			y=0,
			buttons=[
				dict(label="All",
					method="update",
					args=[
						{"marker": [{"color": colors_ma_plot["no_deg"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["up"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["down"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["selected"], "size": 9, "symbol": 2, "line": {"color": "#525252", "width": 2}},
									{"color": colors_ma_plot["selected"], "size": 9, "symbol": 2, "line": {"color": "#525252", "width": 2}},
									{"color": colors_ma_plot["selected"], "size": 9, "symbol": 2, "line": {"color": "#525252", "width": 2}}]
						},
						{"annotations": annotaton_title + up_genes_annotation + down_genes_annotation + selected_gene_annotation}]
				),
				dict(label="Differential analysis",
					method="update",
					args=[
						{"marker": [{"color": colors_ma_plot["no_deg"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["up"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["down"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["no_deg"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}},
									{"color": colors_ma_plot["up"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}},
									{"color": colors_ma_plot["down"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}]
						},
						{"annotations": annotaton_title + up_genes_annotation + down_genes_annotation}]
				),
				dict(label="Selected {gene_or_species}".format(gene_or_species = gene_or_species.lower()),
					method="update",
					args=[
						{"marker": [{"color": colors_ma_plot["no_deg"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["up"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["down"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["selected"], "size": 9, "symbol": 2, "line": {"color": "#525252", "width": 2}},
									{"color": colors_ma_plot["selected"], "size": 9, "symbol": 2, "line": {"color": "#525252", "width": 2}},
									{"color": colors_ma_plot["selected"], "size": 9, "symbol": 2, "line": {"color": "#525252", "width": 2}}]
						},
						{"annotations": annotaton_title + selected_gene_annotation}]
				),
				dict(label="None",
					method="update",
					args=[
						{"marker": [{"color": colors_ma_plot["no_deg"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["up"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["down"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["no_deg"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}},
									{"color": colors_ma_plot["up"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}},
									{"color": colors_ma_plot["down"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}]
						},
						{"annotations": annotaton_title}]
				)
			])
		])

		config_ma_plot = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5}}
		config_ma_plot["toImageButtonOptions"]["filename"] = "MA-plot_with_{contrast}_stringency_{pvalue_type}_{pvalue}".format(contrast = contrast, pvalue_type = pvalue_type.replace("padj", "FDR"), pvalue = pvalue_value)

		#ma_plot_fig["layout"]["paper_bgcolor"] = "#E0F3DB"
		
		return ma_plot_fig, config_ma_plot
	
	#GO-plot
	@app.callback(
		Output("go_plot_graph", "figure"),
		Output("go_plot_graph", "config"),
		Input("contrast_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("go_plot_filter_input", "value"),
		Input("add_gsea_switch", "value"),
		State("feature_dataset_dropdown", "value")
	)
	def plot_go_plot(contrast, stringecy, search_value, add_gsea_switch, expression_dataset):
		#metatranscriptomics does not have go
		if expression_dataset not in ["human", "mouse", "lipid", "lipid_category"]:
			raise PreventUpdate
		
		#boolean switch
		boolean_add_gsea_switch = functions.boolean_switch(add_gsea_switch)

		#lipid category does not have GO, load the lipid one instead
		if expression_dataset == "lipid_category":
			expression_dataset = "lipid"

		#get pvalue type and value
		pvalue_type = stringecy.split("_")[0]
		pvalue_type = pvalue_type.replace("padj", "FDR").replace("pvalue", "P-value")
		pvalue_threshold = stringecy.split("_")[1]

		#omics type
		if "lipid" in expression_dataset:
			omics = "lipidome"
		else:
			omics = "transcriptome"

		#open df
		if expression_dataset in ["human", "mouse"]:
			go_df = functions.download_from_github("data/{}/".format(expression_dataset) + stringecy + "/" + contrast + ".merged_go.tsv")
		else:
			go_df = functions.download_from_github("data/{}/".format(expression_dataset) + "lo/" + contrast + ".merged_go.tsv")
		go_df = pd.read_csv(go_df, sep = "\t")
		go_df = go_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
		
		#concatenate gsea results if the switch is true
		if boolean_add_gsea_switch:
			gsea_df = functions.download_from_github("data/{}/".format(expression_dataset) + "gsea/" + contrast + ".merged_go.tsv")
			gsea_df = pd.read_csv(gsea_df, sep = "\t")
			gsea_df["Genes"] = [gene.replace(";", "; ") for gene in gsea_df["Genes"]]
			gsea_df = gsea_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
			go_df = pd.concat([go_df, gsea_df])

		hide_go_axis = False
		#empty gene ontology file
		if go_df.empty:
			go_df = go_df.rename(columns={"Process~name": "Process", "percentage%": "Enrichment", "P-value": "GO p-value"})
			go_df["Enrichment"] = 1
			go_df_up = go_df
			go_df_down = go_df
			all_enrichments = [33, 66, 99]
			sizeref = 2. * max(all_enrichments)/(5.5 ** 2)
			computed_height = 460
			hide_go_axis = True
		#gene ontology is not empty
		else:
			#filter out useless columns
			go_df = go_df[["DGE", "Process~name", "P-value", "percentage%"]]
			#remove duplicate GO categories for up and down
			#go_df.drop_duplicates(subset ="Process~name", keep = False, inplace = True)

			#define search query if present
			if search_value is not None and search_value != "":
				processes_to_keep = functions.serach_go(search_value, go_df, expression_dataset, boolean_add_gsea_switch)
				#filtering
				go_df = go_df[go_df["Process~name"].isin(processes_to_keep)]
				if go_df.empty:
					hide_go_axis = True

			#rename columns
			go_df = go_df.rename(columns={"Process~name": "Process", "percentage%": "Enrichment", "P-value": "GO p-value"})
			#crop too long process name
			processes = []
			for process in go_df["Process"]:
				if len(process) > 80:
					process = process[0:79] + " ..."
				processes.append(process.replace("_", " "))
			go_df["Process"] = processes

			#divide up and down GO categories
			go_df_up = go_df[go_df["DGE"] == "up"]
			go_df_down = go_df[go_df["DGE"] == "down"]
			
			#function to select GO categories
			def select_go_categories(df):
				#sort by pvalue
				df = df.sort_values(by=["GO p-value"])
				#take top 15
				df = df.head(15)
				#take go categories
				go_categories = df["Process"].tolist()

				return go_categories

			#take most important GO up and down
			go_up_categories = select_go_categories(go_df_up)
			go_down_categories = select_go_categories(go_df_down)
			
			#unique list of go categories
			all_go_categories = list(set(go_up_categories + go_down_categories))

			#find if there are double go categories (up + down)
			unique_go_categories = []
			double_go_categories = []
			for go_category in all_go_categories:
				filtered_go_df = go_df[go_df["Process"] == go_category]
				dge_values = filtered_go_df["DGE"].tolist()
				if len(dge_values) == 2:
					double_go_categories.append(go_category)
				else:
					unique_go_categories.append(go_category)

			#filter df by important unique categories
			filtered_go_df = go_df[go_df["Process"].isin(unique_go_categories)]
			
			#divide up and down GO categories and sort by enrichment
			go_df_up = filtered_go_df[filtered_go_df["DGE"] == "up"]
			go_df_up = go_df_up.sort_values(by=["Enrichment", "GO p-value"])
			go_df_down = filtered_go_df[filtered_go_df["DGE"] == "down"]
			go_df_down = go_df_down.sort_values(by=["Enrichment", "GO p-value"])

			#if there are double categories, these should not influence the sorting of the unique one
			if len(double_go_categories) > 0:
				filtered_go_df = go_df[go_df["Process"].isin(double_go_categories)]
				go_df_up = pd.concat([go_df_up, filtered_go_df[filtered_go_df["DGE"] == "up"].sort_values(by=["Enrichment", "GO p-value"])])
				go_df_down = pd.concat([go_df_down, filtered_go_df[filtered_go_df["DGE"] == "down"].sort_values(by=["Enrichment", "GO p-value"])])

			#find out max enrichment for this dataset
			all_enrichments = go_df_down["Enrichment"].tolist() + go_df_up["Enrichment"].tolist()
			if len(all_enrichments) > 0:
				sizeref = 2. * max(all_enrichments)/(5.5 ** 2)
			else:
				sizeref = None

			#compute figure height
			pixels_per_go_category = 20
			computed_height = len(all_enrichments) * pixels_per_go_category

			#min and max height
			if computed_height < 480:
				computed_height = 480
			elif computed_height > 600:
				computed_height = 600

		#create figure
		go_plot_fig = go.Figure()
		#create subplots
		go_plot_fig = make_subplots(rows=7, cols=4, specs=[[{"rowspan": 7}, None, None, None], [None, None, {"rowspan": 2}, None], [None, None, None, None], [None, None, None, None], [None, None, {"rowspan": 2}, None], [None, None, None, None], [None, None, None, None]], column_widths=[0.5, 0.1, 0.3, 0.1], subplot_titles=(None, "GO p-value", "Enrichment"))

		#function for hover text
		def create_hover_text(df):
			hover_text = []
			for index, row in df.iterrows():
				hover_text.append(("DGE: {dge}<br>" + "Process: {process}<br>" + "Enrichment: {enrichment:.2f}<br>" + "GO p-value: {pvalue:.2f}").format(dge=row["DGE"], process=row["Process"], enrichment=row["Enrichment"], pvalue=row["GO p-value"]))

			return hover_text

		#up trace
		hover_text = create_hover_text(go_df_up)
		go_plot_fig.add_trace(go.Scatter(x=go_df_up["DGE"], y=go_df_up["Process"], marker_size=go_df_up["Enrichment"], marker_opacity=1, marker_color=go_df_up["GO p-value"], marker_colorscale=["#D7301F", "#FCBBA1"], marker_showscale=False, marker_sizeref=sizeref, marker_cmax=0.05, marker_cmin=0, mode="markers", hovertext=hover_text, hoverinfo="text"), row=1, col=1)
		#down trace
		hover_text = create_hover_text(go_df_down)
		go_plot_fig.add_trace(go.Scatter(x=go_df_down["DGE"], y=go_df_down["Process"], marker_size=go_df_down["Enrichment"], marker_opacity=1, marker_color=go_df_down["GO p-value"], marker_colorscale=["#045A8D", "#C6DBEF"], marker_showscale=False, marker_sizeref=sizeref, marker_cmax=0.05, marker_cmin=0, mode="markers", hovertext=hover_text, hoverinfo="text"), row=1, col=1)

		#legend colorbar trace
		go_plot_fig.add_trace(go.Scatter(x=[None], y=[None], marker_showscale=True, marker_color = [0], marker_colorscale=["#737373", "#D9D9D9"], marker_cmax=0.05, marker_cmin=0, marker_colorbar = dict(thicknessmode="pixels", thickness=20, lenmode="pixels", len=(computed_height/5), y=0.68, x=0.8, xpad=0, ypad=0, xanchor="center", yanchor="middle")), row=2, col=3)

		#size legend trace
		if len(all_enrichments) > 0:
			legend_sizes = [min(all_enrichments), np.average([max(all_enrichments), min(all_enrichments)]), max(all_enrichments)]
			legend_sizes_text = [round(min(all_enrichments)), round(np.average([max(all_enrichments), min(all_enrichments)])), round(max(all_enrichments))]
		else:
			legend_sizes = [33, 66, 99]
			legend_sizes_text = [33, 66, 99]
			all_enrichments = [33, 66, 99]
			sizeref = 2. * max(all_enrichments)/(5.5 ** 2)
		go_plot_fig.add_trace(go.Scatter(x = [1, 1, 1], y = [8, 43, 78], marker_size = legend_sizes, marker_sizeref = sizeref, marker_color = "#737373", mode="markers+text", text=["min", "mid", "max"], hoverinfo="text", hovertext=legend_sizes_text, textposition="top center"), row = 5, col = 3)

		#figure layout
		if expression_dataset in ["human", "mouse"]:
			title_text = "Gene ontology enrichment plot<br>{host} {omics} DGE {pvalue_type} < {pvalue_threshold}<br>".format(host=expression_dataset.capitalize(), omics=omics, pvalue_type=pvalue_type, pvalue_threshold=pvalue_threshold) + contrast.replace("_", " ").replace("-", " ")
		else:
			title_text = "Lipid ontology enrichment plot<br>".format(host=expression_dataset.capitalize(), omics=omics, pvalue_type=pvalue_type, pvalue_threshold=pvalue_threshold) + contrast.replace("_", " ").replace("-", " ")
		go_plot_fig.update_layout(title={"text": title_text , "x": 0.75, "xanchor": "center", "font_size": 14}, 
									font_family="Arial",
									height=computed_height,
									showlegend=False,
									autosize=False,
									margin=dict(t=60, b=5, l=410, r=5),
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

		#hide xaxis and yaxis for empty GO
		if hide_go_axis:
			go_plot_fig.update_layout(xaxis_visible=False, yaxis_visible=False)

		#go_plot_fig["layout"]["paper_bgcolor"] = "#FDE0DD"

		config_go_plot = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5}, "responsive": True}
		config_go_plot["toImageButtonOptions"]["filename"] = "GO-plot_with_{contrast}".format(contrast = contrast)

		return go_plot_fig, config_go_plot

	#heatmap
	@app.callback(
		Output("heatmap_graph", "figure"),
		Output("heatmap_graph", "config"),
		Output("hetamap_height_slider", "value"),
		Output("hetamap_height_slider", "max"),
		Output("hetamap_width_slider", "value"),
		Output("hetamap_width_slider", "disabled"),
		Output("hetamap_height_slider", "disabled"),
		Output("comparison_only_heatmap_switch", "value"),
		Input("update_heatmap_plot_button", "n_clicks"),
		Input("clustered_heatmap_switch", "value"),
		Input("comparison_only_heatmap_switch", "value"),
		Input("hide_unselected_heatmap_switch", "value"),
		Input("hetamap_height_slider", "value"),
		Input("hetamap_width_slider", "value"),
		State("feature_heatmap_dropdown", "value"),
		State("annotation_dropdown", "value"),
		State("feature_dataset_dropdown", "value"),
		State("heatmap_graph", "figure"),
		State("contrast_dropdown", "value"),
		#resize
		State("hetamap_height_slider", "max"),
		State("hetamap_width_slider", "max"),
	)
	def plot_heatmap(n_clicks, clustered_switch, comparison_only_switch, hide_unselected_switch, height, width, features, annotations, expression_dataset, old_figure, contrast, max_height, width_max):
		# jak1 jak2 jak3 stat3 stat4 stat5a stat5b

		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#transform switch to boolean switch
		boolean_clustering_switch = functions.boolean_switch(clustered_switch)
		boolean_comparison_only_switch = functions.boolean_switch(comparison_only_switch)
		boolean_hide_unselected_switch = functions.boolean_switch(hide_unselected_switch)

		#do not update the plot for change in contrast if the switch is off
		if trigger_id == "contrast_dropdown.value" and boolean_comparison_only_switch is False:
			raise PreventUpdate

		#resize
		if trigger_id in ["hetamap_height_slider.value", "hetamap_width_slider.value"]:
			if height <= max_height and height >= 200 and width <= width_max and width >= 200:
				old_figure["layout"]["height"] = height
				old_figure["layout"]["width"] = width
				height_fig = height
				width_fig = width
				if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
					colorbar_title = "gene expression"
				else:
					colorbar_title = expression_dataset.replace("_", " ") + " abundance"
				if functions.boolean_switch(clustered_switch):
					clustered_or_sorted = ", hierarchically clustered"
				else:
					clustered_or_sorted = ", sorted by condition"
				
				config_filename_title = colorbar_title + " heatmap" + clustered_or_sorted
				fig = old_figure
				disabled = False
			else:
				raise PreventUpdate
		#plot
		else:
			if trigger_id == "update_heatmap_plot_button.n_clicks":
				comparison_only_switch = []

			#coerce features to list
			if features is None:
				features = []
			#annotations will have always condition by default and these will be at the top of the other annotations
			if annotations == None or annotations == []:
				annotations = ["condition"]
			else:
				annotations.insert(0, "condition")

			#plot only if at least one feature is present
			if len(features) >= 2:
				#get counts dfs
				counts_df_list = []
				for feature in features:
					df = functions.download_from_github("data/" + expression_dataset + "/counts/" + feature + ".tsv")
					df = pd.read_csv(df, sep = "\t")
					feature = feature.replace("€", "/")
					df = df.rename(columns={"counts": feature})
					df = df[["sample", feature]]
					counts_df_list.append(df)
				
				#merge all counts
				counts = reduce(lambda x, y: pd.merge(x, y, on = "sample"), counts_df_list)
				counts = counts.replace("_", " ", regex=True)
				counts = counts.set_index("sample")
				#log 2 and row scaling
				counts = np.log2(counts)
				counts = counts.replace(to_replace = -np.inf, value = 0)
				counts = pd.DataFrame(scale(counts), index=counts.index, columns=counts.columns)

				#open metadata
				metadata = functions.download_from_github("metadata.tsv")
				metadata = pd.read_csv(metadata, sep="\t")
				metadata = metadata.replace("_", " ", regex=True)
				#remove samples for which we don't have counts
				metadata = metadata[metadata["sample"].isin(counts.index)]
				metadata = metadata.set_index("sample")
				metadata_with_NA = metadata.fillna("NA")
				
				#by default all conditions are visible
				if config["sorted_conditions"]:
					sorted_conditions = config["condition_list"]
					conditions = [condition.replace("_", " ") for condition in sorted_conditions]
				else:
					conditions = metadata["condition"].unique().tolist()
					conditions.sort()

				#parse old figure if present to get conditions to plot
				if old_figure is None or len(old_figure["data"]) == 0:
					conditions_to_keep = conditions
				else:
					#filter samples according to legend status
					conditions_to_keep = []
					#only comparison conditions are visible
					if boolean_comparison_only_switch:
						contrast = contrast.replace("_", " ")
						conditions_to_keep = contrast.split("-vs-")
					else:
						#find out if some conditions have to be removed
						for trace in old_figure["data"]:
							#clicking on the switch to false will turn all traces to true
							if trigger_id == "comparison_only_heatmap_switch.value":
								conditions_to_keep = conditions
							#get the previous legend selection
							else:
								#only traces with a name are legend traces
								if "name" in trace.keys():
									if trace["visible"] is True:
										conditions_to_keep.append(trace["name"])

					#filter metadata and get remaining samples
					metadata = metadata[metadata["condition"].isin(conditions_to_keep)]
					samples_to_keep = metadata.index.tolist()
					#filter counts for these samples
					counts = counts[counts.index.isin(samples_to_keep)]

				#create df with features as columns
				feature_df = counts
				#create df with samples as columns
				sample_df = counts.T

				#get a list of features and samples
				features = list(sample_df.index)
				samples = list(sample_df.columns)

				#dendrogram colors
				blacks = ["#676969", "#676969", "#676969", "#676969", "#676969", "#676969", "#676969", "#676969"]

				#the number of yaxis will be the number of annotations + 2 (main heatmap and dendrogram), keep track of the number of annotations
				number_of_annotations = len(annotations)

				#setup figure
				fig = go.Figure()

				#top dendrogram (samples) only if switch is true
				if boolean_clustering_switch:
					dendro_top = ff.create_dendrogram(feature_df, orientation="bottom", labels=samples, colorscale=blacks)
					#set as the last yaxis
					dendro_top.update_traces(yaxis="y" + str(number_of_annotations + 2), showlegend=False)
					
					#save top dendro yaxis
					top_dendro_yaxis = "yaxis" + str(number_of_annotations + 2)
					
					#add top dendrogram traces to figure
					for trace in dendro_top["data"]:
						fig.add_trace(trace)
					
					#get clustered samples
					clustered_samples = dendro_top["layout"]["xaxis"]["ticktext"]
				#sort samples by condition
				else:
					#custom sorting
					if config["sorted_conditions"]:
						df_slices = []
						for condition in conditions:
							df_slice = metadata[metadata["condition"] == condition]
							df_slices.append(df_slice)
						metadata = pd.concat(df_slices)
					#alphabetical sort
					else:
						metadata = metadata.sort_values(by=["condition"])
					clustered_samples = metadata.index.tolist()

				#right dengrogram (features)
				dendro_side = ff.create_dendrogram(sample_df.values, orientation="left", labels=features, colorscale=blacks)
				#set as xaxis2
				dendro_side.update_traces(xaxis="x2", showlegend=False)
				#add right dendrogram data to figure
				for data in dendro_side["data"]:
					fig.add_trace(data)

				#add annotations
				y_axis_number = 2
				all_annotations_yaxis = []
				for annotation in annotations:
					
					#y axis for condition annotation
					if annotation == "condition":
						#condition must be the annotation closer to the dendrogram
						current_y_axis_number = number_of_annotations + 1
						
						#save the yaxis for condition annotation
						condition_annotation_yaxis = "yaxis" + str(current_y_axis_number)

						#get elements with clustered order
						clustered_features = dendro_side["layout"]["yaxis"]["ticktext"]
					#y axis for any other annotation
					else:
						current_y_axis_number = y_axis_number
						#save all additional annotation yaxis in a list
						all_annotations_yaxis.append("yaxis" + str(current_y_axis_number))

					#get clustered annotation
					clustered_annotations = []
					for sample in clustered_samples:
						clustered_annotations.append(metadata_with_NA.loc[sample, annotation])
					
					#discrete annotation
					if str(metadata.dtypes[annotation]) == "object":
						hovertemplate = "{annotation}: ".format(annotation=annotation.capitalize()) + "%{customdata}<Br>Sample: %{x}<extra></extra>"
						if annotation == "condition" and config["sorted_conditions"]:
							values_for_discrete_color_mapping = conditions
						else:
							values_for_discrete_color_mapping = metadata_with_NA[annotation].unique().tolist()
							values_for_discrete_color_mapping.sort()

						#color mapping
						annotation_colors = []
						#link between condition and number for discrete color mapping
						annotation_number_mapping = {}
						i = 0
						for value in values_for_discrete_color_mapping:
							#give a number to the condition
							annotation_number_mapping[value] = i
							#map a color to this number
							annotation_colors.append(functions.get_color(annotation, value))
							#increase incrementals
							i += 1

						#translate clustered conditions in numbers
						z = []
						for value in clustered_annotations:
							z.append(annotation_number_mapping[value])
						zmin = 0
						zmax = i-1
						if zmax == 0:
							zmax = 1
							annotation_colors = annotation_colors + annotation_colors
					#continuous annotation
					else:
						hovertemplate = "{annotation}: ".format(annotation=annotation.capitalize()) + "%{z}<Br>Sample: %{x}<extra></extra>"
						annotation_colors = ["#FFFFFF", functions.get_color(annotation, "continuous")]
						z = []
						for sample in clustered_samples:
							z.append(metadata.loc[sample, annotation])
						zmin = min(z)
						zmax = max(z)

					#create annotation heatmap
					annotation_heatmap = go.Heatmap(z=[z], x=clustered_samples, y=[label_to_value[annotation]], colorscale=annotation_colors, customdata=[clustered_annotations], showscale=False, hovertemplate=hovertemplate, hoverlabel_bgcolor="lightgrey", zmin=zmin, zmax=zmax)
					if boolean_clustering_switch:
						annotation_heatmap["x"] = dendro_top["layout"]["xaxis"]["tickvals"]
						
					annotation_heatmap["yaxis"] = "y" + str(current_y_axis_number)
					fig.add_trace(annotation_heatmap)

					# increase count only when not condition
					if annotation != "condition":
						y_axis_number += 1
				
				#reorder sample df with clustered items
				heat_data = sample_df
				heat_data = heat_data.reindex(columns=clustered_samples)
				heat_data = heat_data.reindex(index=clustered_features)

				#dataset specific variables
				if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
					feature = "Gene"
					colorbar_title = "gene expression"
					space_for_legend = 80
				else:
					feature = expression_dataset.replace("_", " ").capitalize()
					colorbar_title = expression_dataset.replace("_", " ") + " abundance"
					space_for_legend = 200

				#create main heatmap
				heatmap = go.Heatmap(x=clustered_samples, y=clustered_features, z=heat_data, colorscale="Reds", hovertemplate="Sample: %{{x}}<br>{feature}:%{{y}}<extra></extra>".format(feature=feature), hoverlabel_bgcolor="lightgrey", colorbar_title="Row scaled " + colorbar_title, colorbar_title_side="right", colorbar_title_font_family="Arial", colorbar_thicknessmode="pixels", colorbar_thickness=20, colorbar_lenmode="pixels", colorbar_len=100)
				if boolean_clustering_switch:
					heatmap["x"] = dendro_top["layout"]["xaxis"]["tickvals"]
				heatmap["y"] = dendro_side["layout"]["yaxis"]["tickvals"]
				heatmap["yaxis"] = "y"
				fig.add_trace(heatmap)

				##update layout
				if boolean_clustering_switch:
					dendro_top_height = 75
				else:
					dendro_top_height = 0

				#the height and the width will be adaptive to features and samples
				heigth_multiplier = 30
				width_multiplier = 30
				height_fig = heigth_multiplier*len(clustered_features) + heigth_multiplier*number_of_annotations + dendro_top_height + 50
				if height_fig < 245:
					height_fig = 245
				width_fig = width_multiplier*len(clustered_samples) + 75 + space_for_legend

				#max height
				max_height = dendro_top_height + 30*30 + heigth_multiplier*number_of_annotations + 50
				if height_fig > max_height:
					height_fig = max_height
					max_height_flag = True
				else:
					max_height_flag = False
				#max width
				if width_fig > 885:
					width_fig = 885

				### xaxis ###
				dendro_x_left_domain = 0.95 - (75/width_fig)
				#xaxis (x heatmap)
				fig.update_layout(xaxis={"domain": [0, dendro_x_left_domain], "mirror": False, "showgrid": False, "showline": False, "zeroline": False, "ticks":""})
				#xaxis2 (x dendrogram side)
				fig.update_layout(xaxis2={"domain": [dendro_x_left_domain, 0.95], "mirror": False, "showgrid": False, "showline": False, "zeroline": False, "showticklabels": False, "ticks":""})

				### yaxis ###

				#the last yaxis is the dendrogram
				if boolean_clustering_switch:
					bottom_dendro_domain = 0.95-(dendro_top_height/height_fig)
					fig["layout"][top_dendro_yaxis] = {"domain":[bottom_dendro_domain, 0.95], "mirror": False, "showgrid": False, "showline": False, "zeroline": False, "showticklabels": False, "ticks":""}
					top_condition_annotation_domain = bottom_dendro_domain
					bot_condition_annotation_domain = 0.95-((dendro_top_height + heigth_multiplier)/height_fig)
				#the last yaxis is the condition annotation
				else:
					top_condition_annotation_domain = 0.95
					bot_condition_annotation_domain = 0.95-(heigth_multiplier/height_fig)
				#update domain for condition annotation yaxis
				fig["layout"][condition_annotation_yaxis] = {"domain":[bot_condition_annotation_domain, top_condition_annotation_domain], "mirror": False, "showgrid": False, "showline": False, "zeroline": False, "showticklabels": True, "ticks":""}

				#additional annotations
				if len(all_annotations_yaxis) > 0:
					additional_annotation_area = heigth_multiplier/height_fig
					#start from the top annotation
					all_annotations_yaxis.reverse()
					#at the beginning use condition annotation domain as starting point
					annotation_top_domain = bot_condition_annotation_domain
					annotation_bot_domain = bot_condition_annotation_domain - additional_annotation_area
					#add additional annotations
					for annotation_yaxis in all_annotations_yaxis:
						fig["layout"][annotation_yaxis] = {"domain":[annotation_bot_domain, annotation_top_domain], "mirror": False, "showgrid": False, "showline": False, "zeroline": False, "showticklabels": True, "ticks":""}
						#reassign domain for next yaxis
						annotation_top_domain = annotation_bot_domain
						annotation_bot_domain = annotation_bot_domain - additional_annotation_area
					annotation_bot_domain += additional_annotation_area
				#start heatmap from condition annotation domain
				else:
					annotation_bot_domain = bot_condition_annotation_domain

				#main heatmap yaxis
				fig.update_layout(yaxis={"domain": [0, annotation_bot_domain], "mirror": False, "showgrid": False, "showline": False, "zeroline": False, "showticklabels": True, "ticks": ""})
				
				if max_height_flag:
					fig["layout"]["yaxis"]["showticklabels"] = False
				#add feature labels
				fig["layout"]["yaxis"]["tickvals"] = dendro_side["layout"]["yaxis"]["tickvals"]
				fig["layout"]["yaxis"]["ticktext"] = [clustered_feature.replace("_", " ").replace("[", "").replace("]", "") for clustered_feature in clustered_features]
				#add sample labels and define title
				if boolean_clustering_switch:
					fig["layout"]["xaxis"]["tickvals"] = dendro_top["layout"]["xaxis"]["tickvals"]
					clustered_or_sorted = ", hierarchically clustered"
				else:
					clustered_or_sorted = ", sorted by condition"
				fig["layout"]["xaxis"]["ticktext"] = clustered_samples
				fig["layout"]["xaxis"]["showticklabels"] = False

				#legend click behaviour
				if boolean_hide_unselected_switch:
					legend_itemclick = False
					legend_itemdoubleclick = False
				else:
					legend_itemclick = "toggle"
					legend_itemdoubleclick = "toggleothers"
				#add traces for legend
				for condition in conditions:
					if condition in conditions_to_keep:
						visible = True
					else:
						if boolean_hide_unselected_switch:
							visible = False
						else:
							visible = "legendonly"
					fig.add_trace(go.Scatter(x=[None], y=[None], marker_color=functions.get_color("condition", condition), marker_size=8, mode="markers", showlegend=True, name=condition, visible=visible))

				#update layout
				fig.update_layout(title_text=colorbar_title.capitalize() + " heatmap" + clustered_or_sorted, title_font_family="arial", title_font_size=14, title_x=0.5, title_y = 0.98, plot_bgcolor="rgba(0,0,0,0)", legend_title="Condition", legend_title_side="top", legend_orientation="h", legend_tracegroupgap=0.05, margin_t=30, margin_b=0, margin_l=0, margin_r=0, legend_x=0, legend_y=0, legend_yanchor="top", legend_xanchor="left", legend_itemclick=legend_itemclick, legend_itemdoubleclick=legend_itemdoubleclick, width=width_fig, height=height_fig)
				
				config_filename_title = colorbar_title + " heatmap" + clustered_or_sorted
				disabled = False
				max_height = height_fig + 200
				#fig["layout"]["paper_bgcolor"] = "#FDE0DD"
			else:
				fig = go.Figure()
				fig.add_annotation(text="Please select at least two features to plot the heatmap.", showarrow=False)
				width_fig = 885
				height_fig = 450
				max_height = height_fig
				config_filename_title = "empty_heatmap"
				fig.update_layout(xaxis_linecolor="rgb(255,255,255)", yaxis_linecolor="rgb(255,255,255)", xaxis_showticklabels=False, yaxis_showticklabels=False, xaxis_fixedrange=True, yaxis_fixedrange=True, xaxis_ticks="", yaxis_ticks="")
				disabled = True

		config_fig = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "width": width_fig, "height": height_fig, "scale": 5, "filename": config_filename_title}}

		return fig, config_fig, height_fig, max_height, width_fig, disabled, disabled, comparison_only_switch

	#heatmap annotation legend
	@app.callback(
		Output("heatmap_legend_div", "children"),
		Output("heatmap_legend_div", "hidden"),
		Input("heatmap_graph", "figure"),
		State("annotation_dropdown", "value")	
	)
	def plot_heatmap_annotation_legend(heatmap_fig, annotations):
		#setup empty children
		children = []

		#no annotations
		if len(annotations) == 0:
			hidden = True
		#any number of annotation
		else:
			hidden = False
			#open metadata
			metadata = functions.download_from_github("metadata.tsv")
			metadata = pd.read_csv(metadata, sep="\t")
			metadata = metadata.replace("_", " ", regex=True)
			metadata_with_NA = metadata.fillna("NA")

			#filter metadata for selected conditions in the heatmap condition legend
			if len(heatmap_fig["data"]) > 0:
				conditions_to_keep = []
				for trace in heatmap_fig["data"]:
					#find out if there is the legend in the trace
					if "name" in trace:
						if trace["visible"] is True:
							conditions_to_keep.append(trace["name"])
				#filter
				metadata = metadata[metadata["condition"].isin(conditions_to_keep)]

			#setup subplots
			legends_to_plot = len(annotations)
			rows = int(np.ceil(legends_to_plot/6))
			specs = []
			specs_done = 0
			for row in range(1, rows+1):
				#last row means that some of these plots can be None
				if row == rows:
					number_of_missing_elements = legends_to_plot - specs_done
					last_row = []
					for i in range(1, 6):
						if i <= number_of_missing_elements:
							last_row.append({})
						else:
							last_row.append(None)
					specs.append(last_row)
				#any non-last row will be filled by plots
				else:
					specs.append([{}, {}, {}, {}, {}])
					specs_done += 5
			
			#find out how many categories will have each annotation and use the one with the most categories as a reference
			max_categories = 0
			discrete_annotation_count = 1
			#order names for subplots: first discrete, then continue
			discrete_annotations = []
			continuous_annotations = []
			for annotation in annotations:
				if str(metadata.dtypes[annotation]) == "object":
					discrete_annotations.append(annotation.capitalize())
					categories = metadata[annotation].unique().tolist()
					number_of_categories = len(categories)
					#the continue annotations will be after the discrete, 
					#so count the number of discrete annotations to see where will be the first continue x and y axes
					discrete_annotation_count += 1
				else:
					continuous_annotations.append(annotation)
					number_of_categories = 5
				
				#update the number of max categories
				if number_of_categories > max_categories:
					max_categories = number_of_categories

			#make subplot
			fig = make_subplots(rows=rows, cols=5, specs=specs, subplot_titles=discrete_annotations + continuous_annotations, shared_yaxes=True, horizontal_spacing=0)

			#setup loop
			discrete_legends = []
			continue_legends = []
			#loop over annotations
			for annotation in annotations:		
				#discrete annotation
				if str(metadata.dtypes[annotation]) == "object":
					#get unique categories for legend creation
					categories_for_legend = metadata_with_NA[annotation].unique().tolist()
					categories_for_legend.sort()

					#the starting point depends on the number of categories related to the legend with more categories
					y = 1
					if len(categories_for_legend) < max_categories:
						y += max_categories - len(categories_for_legend)
					#add traces to legend
					discrete_legend = []
					for category in categories_for_legend:
						trace = go.Scatter(x=[1], y=[y], marker_color=functions.get_color(annotation, category), marker_size=8, mode="markers+text", name=category, text= "   " + category, textposition="middle right", hoverinfo="none")
						discrete_legend.append(trace)
						y += 1
					#transparent trace to move the colored markes on the left of the area
					trace = go.Scatter(x=[3], y=[1, max_categories], marker_color="rgb(255,255,255)", hoverinfo="none")
					discrete_legend.append(trace)
					discrete_legends.append(discrete_legend)
				
				#continuous annotation
				else:
					#get current xaxis and yaxis
					if discrete_annotation_count == 1:
						annotation_xaxis = "xaxis"
						annotation_yaxis = "yaxis"
					else:
						annotation_xaxis = "xaxis" + str(discrete_annotation_count)
						annotation_yaxis = "yaxis" + str(discrete_annotation_count)
					#get coordinates for colorbar in between of domain values
					colorbar_x = np.mean(fig["layout"][annotation_xaxis]["domain"])
					colorbar_y = np.mean(fig["layout"][annotation_yaxis]["domain"])

					continue_legend = []
					trace = go.Scatter(x = [None], y = [None], marker_showscale=True, marker_color=metadata[annotation], marker_colorscale=["#FFFFFF", functions.get_color(annotation, "continuous")], marker_colorbar=dict(thicknessmode="pixels", thickness=20, lenmode="pixels", len=80, x=colorbar_x, y=colorbar_y, xanchor="right"))
					continue_legend.append(trace)

					#add legends to legends list
					continue_legends.append(continue_legend)
					#increase discrete annotation number count
					discrete_annotation_count += 1

			#add discrete legends to plot
			working_col = 1
			working_row = 1
			#loop over legends
			for legend_type in [discrete_legends, continue_legends]:
				for legend in legend_type:
					#loop over traces in legends
					for trace in legend:
						fig.add_trace(trace, row=working_row, col=working_col)
					#update position on the subplot
					working_col += 1
					if working_col == 6:
						working_col = 1
						working_row += 1

			#update axes
			fig.update_xaxes(linecolor="rgb(255,255,255)", showticklabels=False, fixedrange=True, ticks="")
			fig.update_yaxes(linecolor="rgb(255,255,255)", showticklabels=False, fixedrange=True, ticks="")
			fig.update_annotations(font_size=12, xanchor="left")
			#move legend titles to the left so that they line up with markers
			for annotation in fig["layout"]["annotations"]:
				current_x = annotation["x"]
				annotation["x"] = current_x - 0.102
				current_y = annotation["y"]
				annotation["y"] = current_y
			#compute height
			category_height = 20
			subplot_title_height = 30
			row_height = (category_height*max_categories) + subplot_title_height
			height = (row_height*rows)
			#update layout
			fig.update_layout(width=900, height=height, showlegend=False, margin=dict(t=30, b=10, l=0, r=0, autoexpand=False))

			#add figure to children
			children.append(dcc.Graph(figure=fig, config={"modeBarButtonsToRemove": ["zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "hoverClosestGl2d", "hoverClosestPie", "toggleHover", "sendDataToCloud", "toggleSpikelines", "resetViewMapbox", "hoverClosestCartesian", "hoverCompareCartesian"], "toImageButtonOptions": {"format": "png", "width": 885, "height": height, "scale": 5, "filename": "heatmap_legend_for_" + "_".join(annotations)}}))

			#fig["layout"]["paper_bgcolor"] = "#FDE0DD"
			
		return children, hidden

	#multiboxplots callback
	@app.callback(
		Output("multi_boxplots_graph", "figure"),
		Output("multi_boxplots_graph", "config"),
		Output("multi_boxplots_div", "hidden"),
		Output("popover_plot_multiboxplots", "is_open"),
		Output("multiboxplot_div", "style"),
		Output("x_filter_dropdown_multiboxplots_div", "hidden"),
		Output("hide_unselected_multiboxplots_switch", "value"),
		Output("multiboxplots_height_slider", "value"),
		Output("multiboxplots_width_slider", "value"),
		Input("update_multiboxplot_plot_button", "n_clicks"),
		Input("x_multiboxplots_dropdown", "value"),
		Input("group_by_multiboxplots_dropdown", "value"),
		Input("y_multiboxplots_dropdown", "value"),
		Input("comparison_only_multiboxplots_switch", "value"),
		Input("hide_unselected_multiboxplots_switch", "value"),
		Input("show_as_multiboxplot_switch", "value"),
		Input("x_filter_multiboxplots_dropdown", "value"),
		Input("plot_per_row_multiboxplots_dropdown", "value"),
		Input("multiboxplots_height_slider", "value"),
		Input("multiboxplots_width_slider", "value"),
		State("contrast_dropdown", "value"),
		State("feature_multi_boxplots_dropdown", "value"),
		State("feature_dataset_dropdown", "value"),
		State("multi_boxplots_graph", "figure"),
		State("multi_boxplots_div", "hidden"),
		State("x_filter_dropdown_multiboxplots_div", "hidden")
	)
	def plot_multiboxplots(n_clicks_multiboxplots, x_metadata, group_by_metadata, y_metadata, comparison_only_switch, hide_unselected_switch, show_as_boxplot_switch, selected_x_values, plot_per_row, height, width, contrast, selected_features, expression_dataset, box_fig, hidden_status, x_filter_div_hidden):
		# MEN1; CIT; NDC80; AURKA; PPP1R12A; XRCC2; ENSA; AKAP8; BUB1B; TADA3; DCTN3; JTB; RECQL5; YEATS4; CDK11B; RRM1; CDC25B; CLIP1; NUP214; CETN2
		
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#boolean swithces
		boolean_comparison_only_switch = functions.boolean_switch(comparison_only_switch)
		boolean_hide_unselected_switch = functions.boolean_switch(hide_unselected_switch)
		boolean_show_as_boxplot_switch = functions.boolean_switch(show_as_boxplot_switch)

		#do not update the plot for change in contrast if the switch is off
		if trigger_id == "contrast_dropdown.value" and boolean_comparison_only_switch is False:
			raise PreventUpdate

		#title text
		if expression_dataset in ["human", "mouse"]:
			title_text = "{host} gene expression profiles per ".format(host=expression_dataset.capitalize()) + x_metadata.replace("_", " ").capitalize()
		elif "genes" in expression_dataset:
			title_text = "{} expression profiles per".format(expression_dataset.replace("_genes", " gene").capitalize())
		else:
			title_text = "{} abundance profiles per ".format(expression_dataset.replace("_", " ").replace("viruses", "viral").replace("archaea", "archaeal").replace("bacteria", "bacterial").capitalize()) + x_metadata.replace("_", " ").capitalize()

		#open metadata
		metadata_df_full = functions.download_from_github("metadata.tsv")
		metadata_df_full = pd.read_csv(metadata_df_full, sep = "\t")

		#clean metadata
		metadata_df_full = metadata_df_full.fillna("NA")
		metadata_df_full = metadata_df_full.replace("_", " ", regex=True)
		
		#empty dropdown
		if selected_features is None or selected_features == []:
			hidden_status = True
			popover_status = False
			x_filter_div_hidden = True
		#filled dropdown
		else:
			#up to X elements to plot
			if len(selected_features) <= 20:

				if trigger_id not in ["hide_unselected_multiboxplots_switch.value", "multiboxplots_height_slider.value", "multiboxplots_height_slider.value"]:

					#if there is a change in the plot, hide unselected must be false
					hide_unselected_switch = []
					boolean_hide_unselected_switch = False

					#filter samples for comparison
					if boolean_comparison_only_switch:
						contrast = contrast.replace("_", " ")
						metadata_df_full = metadata_df_full[metadata_df_full["condition"].isin(contrast.split("-vs-"))]

					#create figure
					box_fig = go.Figure()
					
					#define number of rows
					if (len(selected_features) % plot_per_row) == 0:
						n_rows = len(selected_features)/plot_per_row
					else:
						n_rows = int(len(selected_features)/plot_per_row) + 1
					n_rows = int(n_rows)

					#define specs for subplot starting from the space for the legend
					specs = []

					#define specs for each plot row
					for i in range(0, n_rows):
						specs.append([])
						for y in range(0, plot_per_row):
							specs[i].append({})
					
					#in case of odd number of selected elements, some plots in the grid are None
					if (len(selected_features) % plot_per_row) != 0:
						odd_elements_to_plot = len(selected_features) - plot_per_row * (n_rows - 1)
						for i in range(1, ((plot_per_row + 1) - odd_elements_to_plot)):
							specs[-1][-i] = None
					
					#compute height
					height = 250 + n_rows*220
					row_height = 1/n_rows
					row_heights = []
					for i in range(0, n_rows):
						row_heights.append(row_height)

					#labels
					if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
						expression_or_abundance = "expression"
						log2_expression_or_abundance = "Log2 expression"
					else:
						expression_or_abundance = "abundance"
						log2_expression_or_abundance = "Log2 abundance"

					if y_metadata in ["log2_expression", "log2_abundance"]:
						y_axis_title = "Log2 {}".format(expression_or_abundance)
					else:
						y_axis_title = y_metadata

					#make subplots
					box_fig = make_subplots(rows=n_rows, cols=plot_per_row, specs=specs, subplot_titles=[feature.replace("[", "").replace("]", "").replace("_", " ").replace("€", "/") for feature in selected_features], shared_xaxes=True, vertical_spacing=(0.25/(n_rows)), y_title=y_axis_title, row_heights=row_heights)

					#loop 1 plot per gene
					working_row = 1
					working_col = 1
					showlegend = True
					for feature in selected_features:
						#counts as y need external file with count values
						if y_metadata in ["log2_expression", "log2_abundance"]:
							counts = functions.download_from_github("data/" + expression_dataset + "/counts/" + feature + ".tsv")
							counts = pd.read_csv(counts, sep = "\t")
							counts = counts.replace("_", " ", regex=True)
							#merge and compute log2 and replace inf with 0
							metadata_df = metadata_df_full.merge(counts, how="inner", on="sample")
							metadata_df[log2_expression_or_abundance] = np.log2(metadata_df["counts"])
							metadata_df[log2_expression_or_abundance].replace(to_replace = -np.inf, value = 0, inplace=True)
						else:
							metadata_df = metadata_df_full.copy()

						#setup traces
						if x_metadata == group_by_metadata:
							column_for_filtering = x_metadata
							#user defined list of traces
							if x_metadata == "condition" and config["sorted_conditions"]:
								metadata_fields_ordered = config["condition_list"]
								metadata_fields_ordered = [condition.replace("_", " ") for condition in metadata_fields_ordered]
							else:
								metadata_fields_ordered = metadata_df[x_metadata].unique().tolist()
								metadata_fields_ordered.sort()
						else:
							column_for_filtering = group_by_metadata
							metadata_fields_ordered = metadata_df[group_by_metadata].unique().tolist()
							metadata_fields_ordered.sort()

						#grouped or not boxplot setup
						boxmode = "overlay"
						x_filter_div_hidden = True
						#get values that will be on the x axis
						all_x_values = metadata_df[x_metadata].unique().tolist()
						for x_value in all_x_values:
							if boxmode != "group":
								#filter df for x_value and get his traces
								filtered_metadata = metadata_df[metadata_df[x_metadata] == x_value]
								values_column_for_filtering = filtered_metadata[column_for_filtering].unique().tolist()
								#if, for the same x, there is more than one trace, then should be grouped
								if len(set(values_column_for_filtering)) > 1:
									boxmode = "group"
									x_filter_div_hidden = False
									#keep only selected x_values
									selected_x_values = [x_value.replace("_", " ") for x_value in selected_x_values]
									metadata_df = metadata_df[metadata_df[x_metadata].isin(selected_x_values)]

						#plot
						for metadata in metadata_fields_ordered:
							#slice metadata
							filtered_metadata = metadata_df[metadata_df[column_for_filtering] == metadata]
							#only 2 decimals
							filtered_metadata = filtered_metadata.round(2)
							#get x and y
							if y_metadata in ["log2_expression", "log2_abundance"]:
								y_values = filtered_metadata[log2_expression_or_abundance]
							else:
								y_values = filtered_metadata[y_metadata]
							x_values = filtered_metadata[x_metadata]

							#create hovertext
							filtered_metadata["hovertext"] = ""
							for column in filtered_metadata.columns:
								if column not in ["control", "counts", "hovertext", "fq1", "fq2"]:
									filtered_metadata["hovertext"] = filtered_metadata["hovertext"] + column.replace("_", " ").capitalize() + ": " + filtered_metadata[column].astype(str) + "<br>"
							hovertext = filtered_metadata["hovertext"].tolist()

							#create traces
							marker_color = functions.get_color(column_for_filtering, metadata)
							if boolean_show_as_boxplot_switch:
								box_fig.add_trace(go.Box(x=x_values, y=y_values, name=metadata, marker_color=marker_color, boxpoints="all", hovertext=hovertext, hoverinfo="text", legendgroup=metadata, showlegend=showlegend, offsetgroup=metadata, marker_size=3, line_width=4), row=working_row, col=working_col)
							else:
								box_fig.add_trace(go.Violin(x=x_values, y=y_values, name=metadata, marker_color=marker_color, points="all", hovertext=hovertext, hoverinfo="text", legendgroup=metadata, showlegend=showlegend, offsetgroup=metadata, marker_size=3, line_width=4), row=working_row, col=working_col)

						#just one legend for trece showed is enough
						if showlegend is True:
							showlegend = False

						#row and column count
						working_col += 1
						#reset count
						if working_col > plot_per_row:
							working_col = 1
							working_row += 1
					
					#update layout
					box_fig.update_xaxes(tickangle=-90)
					if boolean_show_as_boxplot_switch:
						box_fig.update_layout(height=height, width=width, title={"text": title_text, "x": 0.5, "y": 0.99, "yanchor": "top"}, font_size=14, font_family="Arial", boxmode=boxmode, legend_y=1, legend_tracegroupgap=5, showlegend=True)
					else:
						box_fig.update_layout(height=height, width=width, title={"text": title_text, "x": 0.5, "y": 0.99, "yanchor": "top"}, font_size=14, font_family="Arial", violinmode=boxmode, legend_y=1, legend_tracegroupgap=5, showlegend=True)
				else:
					box_fig = go.Figure(box_fig)
					if trigger_id in ["multiboxplots_height_slider.value", "multiboxplots_height_slider.value"]:
						box_fig.update_layout(height=height, width=width)
				
				#when the switch is true, the legend is no longer interactive
				if boolean_hide_unselected_switch:
					box_fig.update_layout(legend_itemclick=False, legend_itemdoubleclick=False)
					for trace in box_fig["data"]:
						if trace["visible"] == "legendonly":
							trace["visible"] = False
				else:
					box_fig.update_layout(legend_itemclick="toggle", legend_itemdoubleclick="toggleothers")
					for trace in box_fig["data"]:
						if trace["visible"] is False :
							trace["visible"] = "legendonly"

				#popover and div status
				popover_status = False
				hidden_status = False

			#more then 20 elements to plot
			else:
				#default values used when the figure is hidden
				height = 450
				hidden_status = True
				popover_status = True
				x_filter_div_hidden = True

		config_multi_boxplots = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5, "filename": "multiboxplots_{title_text}".format(title_text = title_text.replace(" ", "_") + x_metadata)}}

		multiboxplot_div_style = {"height": height, "width": "100%", "display":"inline-block"}

		return box_fig, config_multi_boxplots, hidden_status, popover_status, multiboxplot_div_style, x_filter_div_hidden, hide_unselected_switch, height, width
