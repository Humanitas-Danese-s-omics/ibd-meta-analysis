#import packages
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash import dash_table
from functions import config, organism, expression_datasets_options, mds_dataset_options, metadata_options, discrete_metadata_options, continuous_metadata_options, metadata_link, metadata_table_data, metadata_table_columns, heatmap_annotation_options, deconvolution_fig

#styles for tabs and selected tabs
tab_style = {
	"padding": 6, 
	"backgroundColor": "#FAFAFA"
}

tab_selected_style = {
    "padding": 6,
	"border-top": "3px solid #597ea2"
}

#header type
if config["header"]["logo"] == "NA":
	header_content = html.Div(config["header"]["text"], style={"width": "100%", "font-size": 50, "text-align": "center"})
else:
	header_content = html.Img(src=config["header"]["logo"], alt="logo", style={"width": "70%", "height": "70%"}, title=config["header"]["text"])

#app layout
layout = html.Div([
	html.Div([
		html.Br(),
		#title
		html.Div(header_content),

		#common options dropdown
		html.Div([
			
			#expression dataset dropdown
			html.Div([
				html.Label(["Expression", 
					dcc.Dropdown(
						id="feature_dataset_dropdown",
						clearable=False,
						options=expression_datasets_options,
						value=organism
				)], style={"width": "100%"}, className="dropdown-luigi"),
			], style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),

			#feature dropdown
			html.Div([
				html.Label(id = "feature_label", children = ["Loading...",
					dcc.Dropdown(
						id="feature_dropdown",
						clearable=False
				)], style={"width": "100%"}, className="dropdown-luigi"),
			], style={"width": "30%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),

			#info comparison filter
			html.Div([
				html.Img(src="assets/info.png", alt="info", id="info_comparison_filter", style={"width": 20, "height": 20}),
				dbc.Tooltip(
					children=[dcc.Markdown(
						"""
						To filter ___Comparison___ drodown, write here any number of keywords. All comparsons which have ___all___ keywords in ___both___ conditions (e.g. before and after the "vs") will be kept. In case any comparison is left, all comparisons will be visualized.
						""")
					],
					target="info_comparison_filter",
					style={"font-family": "arial", "font-size": 14}
				),
			], style={"width": "5%", "display": "inline-block", "vertical-align": "middle"}),
			
			#comparison filter
			html.Label(["Filter comparison by",
				dbc.Input(id="comparison_filter_input", type="search", placeholder="Type here to filter comparisons", debounce=True, style={"font-family": "Arial", "font-size": 12, "height": 36}),
			], style={"width": "17%", "display": "inline-block", "margin-left": "auto", "margin-right": "auto", "vertical-align": "middle", "textAlign": "left"}),
			
			#contrast dropdown
			html.Label(["Comparison", 
				dcc.Dropdown(
					id="contrast_dropdown",
					clearable=False
			)], className="dropdown-luigi", style={"width": "19%", "display": "inline-block", "margin-left": "auto", "margin-right": "auto", "vertical-align": "middle", "textAlign": "left"}),

			#stringecy dropdown
			html.Label(["Stringency", 
				dcc.Dropdown(
					id="stringency_dropdown",
					clearable=False
			)], className="dropdown-luigi", style={"width": "9%", "display": "inline-block", "margin-left": "auto", "margin-right": "auto", "vertical-align": "middle", "textAlign": "left"})

		], style={"width": "100%", "font-size": "12px"}),
		
		html.Br(),

		#mds
		html.Div([
			#mds options and info
			html.Div([
				#info mds
				html.Div([
					html.Img(src="assets/info.png", alt="info", id="info_mds_metadata", style={"width": 20, "height": 20}),
					dbc.Tooltip(
						children=[dcc.Markdown(
							"""
							Low-dimensional embedding of high-dimensional data (e.g., 55k genes in the human transcriptome) by Uniform Manifold Approximation and Projection (UMAP).  
							
							Click the ___legend___ to choose which group you want to display.  
							Click the ___MDS dataset___ dropdown to change multidimensional scaling.  
							Click the ___Color by___ dropdown to change sample colors.  
							Click the ___Comparison only___ button to display only the samples from the two comparisons.

							Click the ___Show legend___ button to display the legend under the plot as well.
							""")
						],
						target="info_mds_metadata",
						style={"font-family": "arial", "font-size": 14}
					),
				], style={"width": "5%", "display": "inline-block", "vertical-align": "middle"}),
				
				#mds dataset dropdown
				html.Div([
					html.Label(["MDS dataset", 
						dcc.Dropdown(
							id="mds_dataset",
							clearable=False,
							options=mds_dataset_options,
							value=organism
					)], style={"width": "100%", "textAlign": "left"}),
				], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto"}),

				#mds type dropdown
				html.Div([
					html.Label(["MDS type", 
						dcc.Dropdown(
							id="mds_type",
							clearable=False,
							value="umap"
					)], style={"width": "100%", "textAlign": "left"}),
				], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto"}),

				#metadata dropdown
				html.Div([
					html.Label(["Color by", 
						dcc.Dropdown(
							id="metadata_dropdown",
							clearable=False,
							options=metadata_options,
							value="condition"
					)], style={"width": "100%", "textAlign": "left"}),
				], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto"}),

				#comparison_only switch
				html.Div([
					html.Label(["Comparison only",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[],
							id="comparison_only_mds_metadata_switch",
							switch=True
						)
					], style={"textAlign": "center"}),
				], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),

				#hide unselected switch
				html.Div([
					html.Label(["Hide unselected",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[],
							id="hide_unselected_mds_metadata_switch",
							switch=True
						)
					], style={"textAlign": "center"}),
				], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"})
			], style={"width": "100%", "font-size": "12px", "display": "inline-block"}),

			#mds metadata
			html.Div(id="mds_metadata_div", children=[
				dcc.Loading(
					id = "loading_mds_metadata",
					children = dcc.Graph(id="mds_metadata"),
					type = "dot",
					color = "#33A02C"
				)
			], style={"width": "48%", "display": "inline-block"}),

			#mds expression
			html.Div(id="mds_expression_div", children=[
				dcc.Loading(
					id = "loading_mds_expression",
					children = dcc.Graph(id="mds_expression"),
					type = "dot",
					color = "#33A02C"
				)
			], style={"width": "35%", "display": "inline-block"}),
		], style={"width": "100%", "display": "inline-block"}),
		
		html.Br(),

		#boxplots
		html.Br(),
		html.Div([
			#boxplots options
			html.Div([
				#info boxplots
				html.Div([
					html.Img(src="assets/info.png", alt="info", id="info_boxplots", style={"width": 20, "height": 20}),
					dbc.Tooltip(
						children=[dcc.Markdown(
							"""
							Box plots showing gene/species/family/order expression/abundance in the different groups.
							
							Click the ___Color by___ dropdown to choose in which way you want to color the samples.
							Click the ___legend___ to choose which group(s) you want to display.
							Click the ___Comparison only___ switch to display only the samples from the two conditions in comparison.
							""")
						],
						target="info_boxplots",
						style={"font-family": "arial", "font-size": 14}
					),
				], style={"width": "5%", "display": "inline-block", "vertical-align": "middle"}),
				#x dropdown
				html.Label(["x",
					dcc.Dropdown(
					id="x_boxplot_dropdown",
					clearable=False,
					options=discrete_metadata_options,
					value="condition"
				)], className="dropdown-luigi", style={"width": "10%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
				#group by dropdown
				html.Label(["Group by", 
							dcc.Dropdown(
								id="group_by_boxplot_dropdown",
								clearable=False,
								value="condition",
								options=discrete_metadata_options
				)], className="dropdown-luigi", style={"width": "10%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
				#y dropdown
				html.Label(["y", 
							dcc.Dropdown(
								id="y_boxplot_dropdown",
								clearable=False,
								value="log2_expression",
								options=continuous_metadata_options
				)], className="dropdown-luigi", style={"width": "10%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
				#comparison only switch
				html.Div([
					html.Label(["Comparison only",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[],
							id="comparison_only_boxplots_switch",
							switch=True
						)
					], style={"textAlign": "center"}),
				], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),
				#hide unselected switch
				html.Div([
					html.Label(["Hide unselected",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[],
							id="hide_unselected_boxplot_switch",
							switch=True
						)
					], style={"textAlign": "center"}),
				], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),
				#show as boxplot switch
				html.Div([
					html.Label(["Show as boxplots",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[],
							id="show_as_boxplot_switch",
							switch=True
						)
					], style={"textAlign": "center"}),
				], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),
				#height slider
				html.Div([
					html.Label(["Height",
						dcc.Slider(id="boxplots_height_slider", min=200, max=400, step=1)
					], style={"width": "100%", "height": "30px", "display": "inline-block"})
				], style={"width": "15%", "display": "inline-block", "vertical-align": "middle"}),
				#width slider
				html.Div([
					html.Label(["Width",
						dcc.Slider(id="boxplots_width_slider", min=200, max=1000, step=1)
					], style={"width": "100%", "height": "30px", "display": "inline-block"})
				], style={"width": "15%", "display": "inline-block", "vertical-align": "middle"}),
			], style={"width": "100%", "font-size": "12px", "display": "inline-block"}),
			
			#x filter dropdown
			html.Div(id="x_filter_dropdown_div", hidden=True, children=[
				html.Label(["x filter", 
					dcc.Dropdown(
						id="x_filter_boxplot_dropdown",
						multi=True
				)], className="dropdown-luigi", style={"width": "100%", "textAlign": "left"}),
			], style={"width": "80%", "display": "inline-block", "vertical-align": "middle", "font-size": "12px"}),

			#plot
			html.Div([
				dcc.Loading(
					id = "loading_boxplots",
					children = dcc.Graph(id="boxplots_graph"),
					type = "dot",
					color = "#33A02C"
				),
			], style={"width": "80%", "display": "inline-block"})
		], style={"width": "100%", "display": "inline-block"}),

		html.Br(),
		html.Br(),

		#MA-plot + go plot
		html.Div([
			#MA-plot + deconvolution
			html.Div([
				#info MA-plot
				html.Div([
					html.Img(src="assets/info.png", alt="info", id="info_ma_plot", style={"width": 20, "height": 20}),
					dbc.Tooltip(
						children=[dcc.Markdown(
							"""
							Differential expression/abundance visualization by MA plot, with gene/species/family/order dispersion in accordance with the fold change between conditions and their average expression/abundance.
							
							Click on the ___Strincency___ dropdown to select the differential gene expression stringency.
							Click on the ___Show gene stats___ button to display its statistics.
							Click a dot inside the plot to change the gene/species/family/order of interest.
							""")
						],
						target="info_ma_plot",
						style={"font-family": "arial", "font-size": 14}
					),
				], style={"width": "100%", "display": "inline-block"}),
				#MA-plot
				html.Div([
					dcc.Loading(
						id = "loading_ma_plot",
						children = dcc.Graph(id="ma_plot_graph"),
						type = "dot",
						color = "#33A02C"
					)
				], style={"width": "100%", "display": "inline-block"}),

				#info deconvolution
				html.Div([
					html.Img(src="assets/info.png", alt="info", id="info_deconvolution", style={"width": 20, "height": 20}),
					dbc.Tooltip(
						children=[dcc.Markdown(
							"""
							TODO
							""")
						],
						target="info_ma_plot",
						style={"font-family": "arial", "font-size": 14}
					),
				], style={"width": "100%", "display": "inline-block"}),
				#deconvolution plot
				html.Div([
					dcc.Loading(
						id = "loading_deconvolution",
						children = dcc.Graph(id="deconvolution_graph", figure = deconvolution_fig),
						type = "dot",
						color = "#33A02C"
					)
				], style={"width": "100%", "display": "inline-block"}),
			], style={"width": "32%", "display": "inline-block"}),

			#go plot
			html.Div([
				#info and search bar
				html.Div([
					#info
					html.Div([
						html.Img(src="assets/info.png", alt="info", id="info_go_plot", style={"width": 20, "height": 20}),
						dbc.Tooltip(
							children=[dcc.Markdown(
								"""
								Balloon plot showing top 15 up and top 15 down differentially enriched gene ontology (GO) biological processes between the two conditions in the selected comparison, unless filtered otherwise by keyword.

								Click on the ___Comparison___ dropdown to change the results.
								Click on the ___Strincency___ dropdown to select the differential gene expression stringency used to find the enriched GO processes.
								""")
							],
							target="info_go_plot",
							style={"font-family": "arial", "font-size": 14}
						),
					], style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "textAlign": "right"}),
					
					#spacer
					html.Div([], style={"width": "1%", "display": "inline-block"}),

					#add gsea switch
					html.Div(id="add_gsea_switch_div", children=[
						html.Label(["Add GSEA",
							dbc.Checklist(
								options=[
									{"label": "", "value": 1},
								],
								value=[],
								id="add_gsea_switch",
								switch=True
							)
						], style={"width": "100%", "display": "inline-block", "vertical-align": "middle", "text-align": "center"})
					], style={"width": "15%", "display": "inline-block", "font-size": "12px"}),

					#spacer
					html.Div([], style={"width": "1%", "display": "inline-block"}),

					#search bar
					html.Div([
						dbc.Input(id="go_plot_filter_input", type="search", placeholder="Type here to filter GO gene sets", size="30", debounce=True, style={"font-family": "Arial", "font-size": 12}),
					], style={"width": "35%", "display": "inline-block", "vertical-align": "middle"})
				], style={"width": "100%", "display": "inline-block", "vertical-align": "middle", "text-align": "right"}),
				#plot
				html.Div([
					dcc.Loading(
						id = "loading_go_plot",
						children = [html.Br(), dcc.Graph(id="go_plot_graph")],
						type = "dot",
						color = "#33A02C", 
					),
				], style={"width": "100%", "display": "inline-block"})
			], style={"width": "68%", "display": "inline-block", "vertical-align": "top"})
		], style = {"width": "80%", "height": 800, "display": "inline-block"}),

		#tabs
		html.Div(children=[
			dcc.Tabs(id="site_tabs", value="metadata_tab", children=[
				#metadata tab
				dcc.Tab(label="Metadata", value="metadata_tab", children=[

					html.Br(),

					#info metadata table
					html.Div([
						html.Img(src="assets/info.png", alt="info", id="info_metadata_table", style={"width": 20, "height": 20}),
						dbc.Tooltip(
							children=[dcc.Markdown(
								"""
								Sample metadata table showing all variables used in web app.
								
								Click on headers/subheaders to reorder/filter the table, respectively.
								""")
							],
							target="info_metadata_table",
							style={"font-family": "arial", "font-size": 14}
						),
					], style={"width": "12%", "display": "inline-block", "vertical-align": "middle", "textAlign": "center"}),

					#download button
					html.Div([
						dcc.Loading(
							type = "circle",
							color = "#33A02C",
							children=[html.A(
								id="download_metadata",
								href=metadata_link,
								download="metadata.xls",
								target="_blank",
								children = [dbc.Button("Download full table", id="download_metadata_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"})],
								)
							]
						)
					], style={"width": "20%", "display": "inline-block", "textAlign": "left", "vertical-align": "middle", 'color': 'black'}),
					
					#table
					html.Div([
						html.Br(),
						dcc.Loading(
							type="dot",
							color="#33A02C",
							children=dash_table.DataTable(
								id="metadata_table",
								filter_action="native",
								style_filter={
									"text-align": "left"
								},
								style_table={
									"text-align": "left"
								},
								style_cell={
									"whiteSpace": "normal",
									"height": "auto",
									"fontSize": 12, 
									"font-family": "arial",
									"text-align": "left"
								},
								style_data_conditional=[                
									{
										"if": {"state": "selected"},
										"backgroundColor": "rgba(44, 62, 80, 0.2)",
										"border": "1px solid #597ea2",
									},
								],
								page_size=25,
								sort_action="native",
								style_header={
									"text-align": "left"
								},
								style_as_list_view=True,
								data = metadata_table_data,
								columns = metadata_table_columns
							)
						)
					], className="luigi-dash-table", style={"width": "100%", "font-family": "arial"}),
					html.Br(),
					html.Br()
				], style=tab_style, selected_style=tab_selected_style),
				#expression/abundance profiling
				dcc.Tab(id="expression_abundance_profiling", value="expression_abundance", children=[
					dcc.Tabs(id="expression_abundance_profiling_tabs", value="heatmap", children=[
						#heatmap
						dcc.Tab(disabled = False, label="Heatmap", value="heatmap", children=[
							html.Div([
								html.Br(),
								
								#heatmap input
								html.Div([
									
									#info + update plot button
									html.Div([
										
										#info
										html.Div([
											html.Img(src="assets/info.png", alt="info", id="info_heatmap", style={"width": 20, "height": 20}),
											dbc.Tooltip(
												children=[dcc.Markdown(
													"""
													Heatmap showing gene/species/family/order expression/abundance in the different conditions. Expression/abundance data is log2 row scaled. By default, are showed the top 15 up and down genes which are statistically differentially expressed in the selected comparison and that shows the higher log2 fold change. 
													
													To select features to plot is possible to search them manualy using the ___Features___ dropdown and the relative search area or in alternative by clicking on any GO plot dot. 
													Switches allow the user to have the control over sample clustering and condition selection/hiding in the legend. 
													Annotations can be added to the heatmap using the ___Annotations___ dropdown.
													""")
												],
												target="info_heatmap",
												style={"font-family": "arial", "font-size": 14}
											),
										], style={"width": "20%", "display": "inline-block", "vertical-align": "middle"}),

										#update plot button
										html.Div([
											dbc.Button("Update plot", id="update_heatmap_plot_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"}),
											#warning popup
											dbc.Popover(
												children=[
													dbc.PopoverHeader(children=["Warning!"], tag="div", style={"font-family": "arial", "font-size": 14}),
													dbc.PopoverBody(children=["Plotting more than 10 features is not allowed."], style={"font-family": "arial", "font-size": 12})
												],
												id="popover_plot_heatmap",
												target="update_heatmap_plot_button",
												is_open=False,
												style={"font-family": "arial"}
											),
										], style={"width": "40%", "display": "inline-block", "vertical-align": "middle"}),
									]),
									
									html.Br(),

									#cluster heatmap switch
									html.Div([
										html.Label(["Clustered samples",
											dbc.Checklist(
												options=[
													{"label": "", "value": 1},
												],
												value=[1],
												id="clustered_heatmap_switch",
												switch=True
											)
										], style={"width": "100%", "display": "inline-block", "vertical-align": "middle"}),
									], style={"width": "34%", "display": "inline-block", "vertical-align": "middle", "font-size": "12px"}),

									#comparison only heatmap switch
									html.Div([
										html.Label(["Comparison only",
											dbc.Checklist(
												options=[
													{"label": "", "value": 1},
												],
												value=[],
												id="comparison_only_heatmap_switch",
												switch=True
											)
										], style={"width": "100%", "display": "inline-block", "vertical-align": "middle"}),
									], style={"width": "33%", "display": "inline-block", "vertical-align": "middle", "font-size": "12px"}),

									#hide unselected legend heatmap switch
									html.Div([
										html.Label(["Hide unselected",
											dbc.Checklist(
												options=[
													{"label": "", "value": 1},
												],
												value=[],
												id="hide_unselected_heatmap_switch",
												switch=True
											)
										], style={"width": "100%", "display": "inline-block", "vertical-align": "middle"}),
									], style={"width": "33%", "display": "inline-block", "vertical-align": "middle", "font-size": "12px"}),

									#dropdowns
									html.Label(["Annotations", 
										dcc.Dropdown(id="annotation_dropdown", 
											multi=True, 
											options=heatmap_annotation_options, 
											value=[], 
											style={"textAlign": "left", "font-size": "12px"})
									], className="dropdown-luigi", style={"width": "100%", "display": "inline-block", "textAlign": "left", "font-size": "12px"}),

									html.Br(),

									html.Label(["Features",
										dcc.Dropdown(id="feature_heatmap_dropdown", 
											multi=True, 
											placeholder="Select features", 
											style={"textAlign": "left", "font-size": "12px"})
									], className="dropdown-luigi", style={"width": "100%", "display": "inline-block", "textAlign": "left", "font-size": "12px"}),

									html.Br(),

									#text area
									dbc.Textarea(id="heatmap_text_area", style={"height": 300, "resize": "none", "font-size": "12px"}),

									html.Br(),

									#search button
									dbc.Button("Search", id="heatmap_search_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"}),

									html.Br(),

									#genes not found area
									html.Div(id="genes_not_found_heatmap_div", children=[], hidden=True, style={"font-size": "12px", "text-align": "center"}), 

									html.Br()
								], style={"width": "25%", "display": "inline-block", "vertical-align": "top"}),

								#spacer
								html.Div([], style={"width": "1%", "display": "inline-block"}),

								#heatmap graph and legend
								html.Div(children=[
									
									#custom hetmap dimension
									html.Div([
										#height slider
										html.Label(["Height",
											dcc.Slider(id="hetamap_height_slider", min=200, step=1)
										], style={"width": "30%", "display": "inline-block"}),
										#spacer
										html.Div([], style={"width": "3%", "display": "inline-block"}),
										#width slider
										html.Label(["Width",
											dcc.Slider(id="hetamap_width_slider", min=200, max=885, step=1)
										], style={"width": "30%", "display": "inline-block"})
									], style={"width": "100%", "display": "inline-block", "vertical-align": "middle"}),

									#graph
									dcc.Loading(
										children = [dcc.Graph(id="heatmap_graph")],
										type = "dot",
										color = "#33A02C"
									),
									#legend
									html.Div(id="heatmap_legend_div", hidden=True)
								], style = {"width": "74%", "display": "inline-block"})
							], style = {"width": "100%", "height": 800, "display": "inline-block"})
						], style=tab_style, selected_style=tab_selected_style, disabled_style={"padding": 6, "color": "#d6d6d6"}),
						#multiboxplots
						dcc.Tab(label="Boxplots", value="boxplots", children=[
							html.Div(id="multiboxplot_div", children=[
								
								html.Br(),
								
								#input section
								html.Div([
									
									#info + update plot button
									html.Div([
										
										#info
										html.Div([
											html.Img(src="assets/info.png", alt="info", id="info_multiboxplots", style={"width": 20, "height": 20}),
											dbc.Tooltip(
												children=[dcc.Markdown(
													"""
													Box plots showing host gene/species/family/order expression/abundance in the different groups.
													
													Click the ___legend___ on the top of the page to choose which group you want to display.  
													Click the ___Comparison only___ button to display only the samples from the two comparisons.
													Is not possible to plot more than 10 elements.
													""")
												],
												target="info_multiboxplots",
												style={"font-family": "arial", "font-size": 14}
											),
										], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),

										#update plot button
										html.Div([
											dbc.Button("Update plot", id="update_multiboxplot_plot_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"}),
											#warning popup
											dbc.Popover(
												children=[
													dbc.PopoverHeader(children=["Warning!"], tag="div", style={"font-family": "arial", "font-size": 14}),
													dbc.PopoverBody(children=["Plotting more than 20 features is not allowed."], style={"font-family": "arial", "font-size": 12})
												],
												id="popover_plot_multiboxplots",
												target="update_multiboxplot_plot_button",
												is_open=False,
												style={"font-family": "arial"}
											),
										], style={"width": "30%", "display": "inline-block", "vertical-align": "middle"}),
									]),
									
									html.Br(),

									#dropdown
									html.Div([
										dcc.Dropdown(id="feature_multi_boxplots_dropdown", 
											multi=True, 
											placeholder="", 
											style={"textAlign": "left", "font-size": "12px"}
										),
									], className="dropdown-luigi"),

									html.Br(),

									#text area
									dbc.Textarea(id="multi_boxplots_text_area", style={"width": "100%", "height": 300, "resize": "none", "font-size": "12px"}),

									html.Br(),

									#search button
									dbc.Button("Search", id="multi_boxplots_search_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"}),

									html.Br(),

									#genes not found area
									html.Div(id="genes_not_found_multi_boxplots_div", children=[], hidden=True, style={"font-size": "12px", "text-align": "center"}), 

									html.Br()
								], style={"width": "25%", "display": "inline-block", "vertical-align": "top"}),

								#multiboxplots options and graph
								html.Div([
									#x dropdown
									html.Label(["x",
										dcc.Dropdown(
										id="x_multiboxplots_dropdown",
										clearable=False,
										options=discrete_metadata_options,
										value="condition"
									)], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
									#group by dropdown
									html.Label(["Group by", 
										dcc.Dropdown(
											id="group_by_multiboxplots_dropdown",
											clearable=False,
											value="condition",
											options=discrete_metadata_options
									)], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
									#y dropdown
									html.Label(["y", 
										dcc.Dropdown(
											id="y_multiboxplots_dropdown",
											clearable=False,
											value="log2_expression",
											options=continuous_metadata_options, 
											className="dropdown-luigi"
									)], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
									#plot per row
									#y dropdown
									html.Label(["Plot per row", 
										dcc.Dropdown(
											id="plot_per_row_multiboxplots_dropdown",
											clearable=False,
											value=3,
											options=[{"label": n, "value": n} for n in [1, 2, 3]]
									)], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
									#comparison_only switch
									html.Div([
										html.Label(["Comparison only",
											dbc.Checklist(
												options=[
													{"label": "", "value": 1},
												],
												value=[],
												id="comparison_only_multiboxplots_switch",
												switch=True
											)
										], style={"textAlign": "center"}),
									], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),
									#hide unselected switch
									html.Div([
										html.Label(["Hide unselected",
											dbc.Checklist(
												options=[
													{"label": "", "value": 1},
												],
												value=[],
												id="hide_unselected_multiboxplots_switch",
												switch=True
											)
										], style={"textAlign": "center"}),
									], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),
									#show as boxplot switch
									html.Div([
										html.Label(["Show as boxplots",
											dbc.Checklist(
												options=[
													{"label": "", "value": 1},
												],
												value=[],
												id="show_as_multiboxplot_switch",
												switch=True
											)
										], style={"textAlign": "center"}),
									], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),
									#custom hetmap dimension
									html.Div([
										#height slider
										html.Label(["Height",
											dcc.Slider(id="multiboxplots_height_slider", min=200, step=1, max = 2000)
										], style={"width": "30%", "display": "inline-block"}),
										#spacer
										html.Div([], style={"width": "3%", "display": "inline-block"}),
										#width slider
										html.Label(["Width",
											dcc.Slider(id="multiboxplots_width_slider", min=200, max=900, value=900, step=1)
										], style={"width": "30%", "display": "inline-block"})
									], style={"width": "100%", "display": "inline-block", "vertical-align": "middle"}),
									#x filter dropdown
									html.Div(id="x_filter_dropdown_multiboxplots_div", hidden=True, children=[
										html.Label(["x filter", 
											dcc.Dropdown(
												id="x_filter_multiboxplots_dropdown",
												multi=True, 
												className="dropdown-luigi"
										)], style={"width": "100%", "textAlign": "left"}),
									], style={"width": "90%", "display": "inline-block", "textAlign": "left", "font-size": "12px"}),

									#graph
									html.Div(id="multiboxplot_graph_div", children=[
										dcc.Loading(type = "dot", color = "#33A02C", children=[
											html.Div(
												id="multi_boxplots_div",
												children=[dcc.Loading(
													children = [dcc.Graph(id="multi_boxplots_graph", figure={})],
													type = "dot",
													color = "#33A02C")
											], hidden=True)
										])
									], style={"height": 800, "width": "100%", "display": "inline-block", "vertical-align": "top"})
								], style={"width": "75%", "font-size": "12px", "display": "inline-block"}),
							], style={"width": "100%", "height": 800, "display": "inline-block"})
						], style=tab_style, selected_style=tab_selected_style),
					], style= {"height": 40})
				], style=tab_style, selected_style=tab_selected_style),
				#differential analysis tab
				dcc.Tab(label="Differential analysis", value="differential_analysis", children=[
					dcc.Tabs(id="differential_analysis_tabs", value="dge_tab", children=[
						#dge table tab
						dcc.Tab(id="dge_table_tab", label="DGE table", value="dge_tab", children=[
							
							html.Br(),
							#title dge table
							html.Div(id="dge_table_title", children=[], style={"width": "100%", "display": "inline-block", "textAlign": "center", "font-size": "14px"}),
							html.Br(),
							html.Br(),

							#info dge table
							html.Div([
								html.Img(src="assets/info.png", alt="info", id="info_dge_table", style={"width": 20, "height": 20}),
								dbc.Tooltip(
									children=[dcc.Markdown(
										"""
										Table showing the differential gene/species/family/order expression/abundance between the two conditions, unless filtered otherwise.

										Click on headers to reorder the table.

										Click on a cell with the gene/species/family/order will highlight the feature in the MA plot.
										Click on an icon in the last column to open external resources.
										""")
									],
									target="info_dge_table",
									style={"font-family": "arial", "font-size": 14}
								),
							], style={"width": "10%", "display": "inline-block", "vertical-align": "middle", "textAlign": "center"}),

							#download full table button diffexp
							html.Div([
								dcc.Loading(
									id = "loading_download_diffexp",
									type = "circle",
									color = "#33A02C",
									children=[html.A(
										id="download_diffexp",
										href="",
										target="_blank",
										children = [dbc.Button("Download full table", id="download_diffexp_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", 'color': 'black'})],
										)
									]
								)
							], style={"width": "15%", "display": "inline-block", "vertical-align": "middle", 'color': 'black'}),

							#download partial button diffexp
							html.Div([
								dcc.Loading(
									type = "circle",
									color = "#33A02C",
									children=[html.A(
										id="download_diffexp_partial",
										href="",
										target="_blank",
										children = [dbc.Button("Download filtered table", id="download_diffexp_button_partial", disabled=True, style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", 'color': 'black'})],
										)
									]
								)
							], style={"width": "25%", "display": "inline-block", "vertical-align": "middle", 'color': 'black'}),

							#dropdown
							html.Div([
								dcc.Dropdown(id="multi_gene_dge_table_selection_dropdown", 
									multi=True, 
									placeholder="", 
									style={"textAlign": "left", "font-size": "12px"})
							], className="dropdown-luigi", style={"width": "25%", "display": "inline-block", "font-size": "12px", "vertical-align": "middle"}),

							#target priorization switch
							html.Div(id = "target_prioritization_switch_div", hidden = True, children = [
								html.Label(["Target prioritization",
									dbc.Checklist(
										options=[
											{"label": "", "value": 1},
										],
										value=[],
										id="target_prioritization_switch",
										switch=True
									)
								], style={"textAlign": "center"})
							], style={"width": "16%", "display": "inline-block", "vertical-align": "middle"}),

							#filtered dge table
							html.Div(id="filtered_dge_table_div", children=[
								html.Br(),
								dcc.Loading(
									id="loading_dge_table_filtered",
									type="dot",
									color="#33A02C",
									children=dash_table.DataTable(
										id="dge_table_filtered",
										style_cell={
											"whiteSpace": "normal",
											"height": "auto",
											"fontSize": 12, 
											"font-family": "arial",
											"textAlign": "center"
										},
										page_size=25,
										sort_action="native",
										style_header={
											"textAlign": "center"
										},
										style_cell_conditional=[
											{
												"if": {"column_id": "External resources"},
												"width": "12%"
											}
										],
										style_data_conditional=[],
										style_as_list_view=True
									)
								)
							], className="luigi-dash-table", style={"width": "100%", "font-family": "arial"}, hidden=True),

							#full dge table
							html.Div([
								html.Br(),
								dcc.Loading(
									id="loading_dge_table",
									type="dot",
									color="#33A02C",
									children=dash_table.DataTable(
										id="dge_table",
										style_cell={
											"whiteSpace": "normal",
											"height": "auto",
											"fontSize": 12, 
											"font-family": "arial",
											"textAlign": "center"
										},
										page_size=25,
										sort_action="native",
										style_header={
											"textAlign": "center"
										},
										style_cell_conditional=[
											{
												"if": {"column_id": "External resources"},
												"width": "12%"
											}
										],
										style_data_conditional=[],
										style_as_list_view=True
									)
								)
							], className="luigi-dash-table", style={"width": "100%", "font-family": "arial"}),
							html.Br()
						], style=tab_style, selected_style=tab_selected_style),
						#go table tab
						dcc.Tab(id="go_table_tab", label="GO table", value="go_table_tab", children=[
							
							html.Br(),
							#title go table
							html.Div(id="go_table_title", children=[], style={"width": "100%", "display": "inline-block", "textAlign": "center", "font-size": "14px"}),
							html.Br(),
							html.Br(),

							#info go table
							html.Div([
								html.Img(src="assets/info.png", alt="info", id="info_go_table", style={"width": 20, "height": 20}),
								dbc.Tooltip(
									children=[dcc.Markdown(
										"""
										Table showing the differentially enriched gene ontology biological processes between the two conditions, unless filtered otherwise.

										Use the ___search bar___ above the GO plot to filter the processes.

										Click on headers to reorder the table.
										Click on a GO dataset name to see its specifics in AmiGO 2 (___Ashburner et al. 2000, PMID 10802651___).
										""")
									],
									target="info_go_table",
									style={"font-family": "arial", "font-size": 14}
								),
							], style={"width": "12%", "display": "inline-block", "vertical-align": "middle", "textAlign": "center"}),

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
										children = [dbc.Button("Download full table", id="download_go_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", 'color': 'black'})],
										)
									]
								)
							], style={"width": "20%", "display": "inline-block", "textAlign": "left", "vertical-align": "middle", 'color': 'black'}),

							#download button partial
							html.Div([
								dcc.Loading(
									type = "circle",
									color = "#33A02C",
									children=[html.A(
										id="download_go_partial",
										href="",
										target="_blank",
										children = [dbc.Button("Download shown table", id="download_go_button_partial", disabled=True, style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", 'color': 'black'})],
										)
									]
								)
							], style={"width": "20%", "display": "inline-block", "textAlign": "left", "vertical-align": "middle", 'color': 'black'}),

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
												"if": {"column_id": "Lipids"},
												"textAlign": "left",
												"width": "50%"
											},
											{
												"if": {"column_id": "GO biological process"},
												"textAlign": "left",
												"width": "15%"
											},
											{
												"if": {"column_id": "Functional category"},
												"textAlign": "left",
												"width": "15%"
											}
										],
										style_data_conditional=[
											{
												"if": {"filter_query": "{{DGE}} = {}".format("up")},
												"backgroundColor": "#FFE6E6"
											},
											{
												"if": {"filter_query": "{{DGE}} = {}".format("down")},
												"backgroundColor": "#E6F0FF"
											},
											{
												"if": {	"filter_query": "{{DLE}} = {}".format("up")},
												"backgroundColor": "#FFE6E6"
											},
											{
												"if": {"filter_query": "{{DLE}} = {}".format("down")},
												"backgroundColor": "#E6F0FF"
											},
											{
												"if": {"state": "selected"},
												"backgroundColor": "rgba(44, 62, 80, 0.2)",
												"border": "1px solid #597ea2",
											}
										],
										style_as_list_view=True
									)
								)
							], className="luigi-dash-table", style={"width": "100%", "font-family": "arial"}),
							html.Br()
						], style=tab_style, selected_style=tab_selected_style)
					], style= {"height": 40})
				], style=tab_style, selected_style=tab_selected_style)
			], style= {"height": 40}),
		], style = {"width": "100%", "display": "inline-block"})
	], style={"width": 1200, "font-family": "Arial"})
], style={"width": "100%", "justify-content":"center", "display":"flex", "textAlign": "center"})
