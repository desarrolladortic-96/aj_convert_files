from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from django_plotly_dash import DjangoDash
import dash_ag_grid as dag
import pandas as pd
import io
import plotly.express as px

import plotly.graph_objects as go
import plotly.figure_factory as ff

import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def create_dash_app_combined_conciliacion(file_path):

    def generate_plots(column_name):
        
        if column_name:

            if df.dtypes[str(column_name)] in ["float64", "int64"]:

                hist_data = [df[str(column_name)].dropna().to_list()]
                group_labels = ['distplot']
                colors = ['#1b60a7']
                bar_fig = ff.create_distplot(hist_data, group_labels, colors=colors, show_rug=False)
                bar_fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', autosize=True, showlegend=False)
                bar_fig.update_xaxes(title_text=str(column_name))
                bar_fig.update_yaxes(title_text="Frecuencia(%)")

                y = df[str(column_name)].dropna().values.tolist()
                trace = go.Box(y=y, name=str(column_name), jitter=0.3, marker=dict(color='#1b60a7'))
                layout = go.Layout(showlegend=False, margin=dict(t=0, l=0, r=0, b=0), autosize=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(zeroline=False))
                data_aux = [trace]
                pie_fig = go.Figure(data=data_aux, layout=layout)

                df_ = df[str(column_name)].describe().astype(float).reset_index()
                df_.columns = ['Parámetro', 'Valor']
                df_.drop([4, 5, 6], axis=0, inplace=True)
                cv_row = np.array(["cv", (df_.Valor.loc[2] / df_.Valor.loc[1]) * 100])
                df_.loc[len(df_)] = cv_row
                df_["Valor"] = pd.to_numeric(df_["Valor"], errors='coerce')
                df_ = df_.round(2)

                table_fig = go.Figure(data=[go.Table(
                    header=dict(values=list(df_.columns), fill_color='#1b60a7', font=dict(color='white', size=12), align='left'),
                    cells=dict(values=[df_[str(i)] for i in df_.columns], fill_color='white', align='left'))
                ])
                
                table_fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', autosize=True, showlegend=False)

                return bar_fig, table_fig, pie_fig

            elif df.dtypes[str(column_name)] == "object":
                
                frequencies = df[column_name].value_counts().sort_values(ascending=False)
                if len(frequencies.index) < 10:
                    bar_fig = px.bar(frequencies, x=frequencies.index, y=frequencies.values, labels={'x': column_name, 'y': 'Frecuencia'}, range_x=[-0.5, len(frequencies.index) - 0.5], color_discrete_sequence=["#086aad"])
                else:
                    bar_fig = px.bar(frequencies, x=frequencies.index, y=frequencies.values, labels={'x': column_name, 'y': 'Frecuencia'}, range_x=[-0.5, 9.5], color_discrete_sequence=["#086aad"])
                
                bar_fig.update_xaxes(title_text=str(column_name), type='category')
                bar_fig.update_yaxes(title_text="")
                bar_fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', autosize=True, showlegend=False)

                top_categories = frequencies.head(10)
                total_values = frequencies.sum()
                percentages = (top_categories / total_values) * 100
                percentages = np.round(percentages, 1)

                pie_fig = go.Figure(data=[go.Pie(labels=top_categories.index, values=percentages)])
                pie_fig.update_traces(textposition='inside', textinfo='label+percent+value', hovertemplate="Categoría:%{label}: <br>Global: %{value} </br> Top 10: %{percent}", hoverinfo='label+value+percent')
                pie_fig.update_layout(margin=dict(t=25, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', autosize=True, showlegend=True, title="Top 10 Categorías Más Relevantes")

                table_fig = go.Figure(data=[go.Table(
                    header=dict(values=[f'{column_name}', 'Frecuencia'], fill_color="#086aad", font=dict(color='white', size=12), align='left'),
                    cells=dict(values=[frequencies.index, frequencies.values], fill_color='white', align='left'))
                ])

                table_fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', autosize=True, showlegend=False)
                
                return bar_fig, table_fig, pie_fig

    app = DjangoDash('Combined_App', external_stylesheets=external_stylesheets)

    df = file_path

    app.layout = html.Div([
            dag.AgGrid(
                id="editing-grid2",
                columnDefs=[{"field": i, "resizable": True} for i in df.columns],
                rowData=df.to_dict("records"),
                columnSize="autoSize",
                defaultColDef={"editable": False, "resizable": True},
                dashGridOptions={"animateRows": False}
            ),
            html.Div([
                html.Button('Descargar Datos', id='download-data-btn', n_clicks=0),
                dcc.Download(id="download-data")
            ]),
            html.Div(id="editing-grid-output2"),
            html.Br(),
            html.Div([
                dcc.Download(id="download-data"),
                dcc.Dropdown(
                    id='column-dropdown',
                    options=[{'label': col, 'value': col} for col in df.columns],
                    placeholder='Selecciona una columna'
                ),
                html.Button('Generar gráficos', id='generate-plots-btn', n_clicks=0),
            ]),
            html.Div(id="graph-output"),
            html.Br(),
        ],
        style={'margin': '0px', 'height': '1000px'},
    )

    @app.callback(
        Output('graph-output', 'children'),
        [Input('generate-plots-btn', 'n_clicks')],
        [State('column-dropdown', 'value')],
    )
    def generate_plots_output(n_clicks, column_name):
        if n_clicks and column_name:
            bar_fig, pie_fig, table_fig = generate_plots(column_name)
            return [
                dcc.Graph(figure=bar_fig,className="four columns"),
                dcc.Graph(figure=table_fig,className="four columns"),                
                dcc.Graph(figure=pie_fig,className="four columns"),
            ]

    @app.callback(
        Output('download-data', 'data'),
        [Input('download-data-btn', 'n_clicks')],
        [State('editing-grid2', 'rowData')]
    )
    def download_data(n_clicks, grid_data):
        if n_clicks and n_clicks > 0:
            edited_df = pd.DataFrame(grid_data)
            buffer = io.BytesIO()
            edited_df.to_excel(buffer, sheet_name='master', index=False, engine='openpyxl')
            buffer.seek(0)
            return dcc.send_bytes(buffer.getvalue(), "download_.xlsx")
    
    return app
