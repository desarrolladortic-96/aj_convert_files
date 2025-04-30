from dash import dcc, html
from dash.dependencies import Input, Output, State
from django_plotly_dash import DjangoDash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def create_dash_app_analisis_atributos(file_path):

    app = DjangoDash('Analisis_Atributos', external_stylesheets=external_stylesheets)

    def load_data(file_path):
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path, engine='openpyxl')
        else:
            raise ValueError("Unsupported file type")

    try:
        df = load_data(file_path)
    except Exception as e:
        return html.Div([html.H3(f"Error loading file: {str(e)}")])

    def style_fig(fig):
        fig.update_layout(
            margin=dict(t=0, l=0, r=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            autosize=True,
            showlegend=False,
            font_color="white",
        )
        return fig

    def generate_numeric_plots(column_name):
        
        hist_data = [df[str(column_name)].dropna().to_list()]
        group_labels = ['distplot']
        colors = ['#1b60a7']

        bar_fig = ff.create_distplot(hist_data, group_labels, colors=colors, show_rug=False)
        bar_fig.update_xaxes(title_text=str(column_name))
        bar_fig.update_yaxes(title_text="Frecuencia(%)")
        bar_fig = style_fig(bar_fig)

        y = df[str(column_name)].dropna().values.tolist()
        trace = go.Box(
            y=y,
            name=str(column_name),
            jitter=0.3,
            marker=dict(color='#1b60a7'),
        )
        layout = go.Layout(
            showlegend=False,
            yaxis=dict(zeroline=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                font=dict(
                    color="white"
                ),
            )
        )
        box_fig = style_fig(go.Figure(data=[trace], layout=layout))

        df_ = df[str(column_name)].describe().astype(float).reset_index()
        df_.columns = ['Parámetro', 'Valor']
        df_ = df_.drop([4, 5, 6], axis=0)
        cv_row = np.array(["cv", (df_.Valor.loc[2] / df_.Valor.loc[1]) * 100])
        df_.loc[len(df_)] = cv_row
        df_["Valor"] = pd.to_numeric(df_["Valor"], errors='coerce')
        df_ = df_.round(2)
        
        table_fig = go.Figure(data=[go.Table(
            header=dict(values=list(df_.columns),
                        fill_color='#1b60a7',
                        font=dict(color='white', size=12),
                        align='left'),
            cells=dict(values=[df_[str(i)] for i in df_.columns],
                       fill_color='rgba(0,0,0,0)',
                       font=dict(color='white', size=12),
                       align='left'))
        ])
        table_fig = style_fig(table_fig)

        return bar_fig, box_fig, table_fig

    def generate_categorical_plots(categorical_col, numeric_col=None):

        if numeric_col and numeric_col in df.columns:

            grouped_df = df.groupby(categorical_col)[numeric_col].mean().reset_index()
            grouped_df = grouped_df.sort_values(by=numeric_col, ascending=False)
            grouped_df = grouped_df.round(2)

            bar_fig = px.bar(
                grouped_df,
                x=categorical_col,
                y=numeric_col,
                labels={categorical_col: 'Categoría', numeric_col: 'Promedio'},
                color_discrete_sequence=["#086aad"],
                range_x=[-0.5,9.5],
            )

            bar_fig.update_xaxes(title_text=categorical_col)
            bar_fig.update_yaxes(title_text=numeric_col)
            bar_fig = style_fig(bar_fig)

            layout_pie = go.Layout(
                    showlegend=False,margin = dict(t=0, l=0, r=0, b=0),autosize=True,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    yaxis=dict(
                        zeroline=False
                    ),
                    legend=dict(font=dict(color="white"))
            )

            top_categories = grouped_df.head(10)
            pie_fig = px.pie(
                top_categories,
                names=categorical_col,
                values=numeric_col,
                labels={categorical_col: 'Categoría', numeric_col: 'Promedio'}
            )

            pie_fig.update_traces(textposition='inside',textinfo='label+percent+value', hovertemplate="Categoría: %{label}<br>Promedio: %{value:.2f}<br>Porcentaje: %{percent:.1%}")
            pie_fig.update_layout(showlegend=True, margin = dict(t=0, l=0, r=0, b=0), autosize=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(zeroline=False), title=f"Distribución del {numeric_col} por {categorical_col}", legend=dict(font=dict(color="white")))

            table_fig = go.Figure(data=[go.Table(
                header=dict(values=[categorical_col, numeric_col],
                            fill_color="#086aad",
                            font=dict(color='white', size=12),
                            align='left'),
                cells=dict(values=[grouped_df[categorical_col], grouped_df[numeric_col]],
                           fill_color='rgba(0,0,0,0)',
                           font=dict(color='white', size=12),
                           align='left'))
            ])
            table_fig = style_fig(table_fig)

        else:

            frequencies = df[categorical_col].value_counts().sort_values(ascending=False)
            top_frequencies = frequencies.head(10)

            if len(frequencies.index) < 10:
                bar_fig = px.bar(
                    top_frequencies,
                    x=top_frequencies.index,
                    y=top_frequencies.values,
                    labels={'x': categorical_col, 'y': 'Frecuencia'},
                    color_discrete_sequence=["#086aad"],
                    range_x=[-0.5, len(frequencies.index) - 0.5],
                )
            else:
                bar_fig = px.bar(
                    top_frequencies,
                    x=top_frequencies.index,
                    y=top_frequencies.values,
                    labels={'x': categorical_col, 'y': 'Frecuencia'},
                    color_discrete_sequence=["#086aad"],
                    range_x=[-0.5, 9.5],
                )

            bar_fig.update_xaxes(title_text=categorical_col, type='category')
            bar_fig.update_yaxes(title_text="")
            bar_fig = style_fig(bar_fig)

            pie_fig = px.pie(
                top_frequencies,
                names=top_frequencies.index,
                values=top_frequencies.values,
                labels={categorical_col: 'Categoría', 'values': 'Frecuencia'}
            )
            pie_fig.update_traces(textposition='inside',textinfo='label+percent+value', hovertemplate="Categoría: %{label}<br>Frecuencia: %{value}<br>Porcentaje: %{percent:.1%}")
            pie_fig.update_layout(showlegend=True, margin = dict(t=0, l=0, r=0, b=0), autosize=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(zeroline=False), legend=dict(font=dict(color="white")))

            table_fig = go.Figure(data=[go.Table(
                header=dict(values=[f'{categorical_col}', 'Frecuencia'],
                            fill_color="#086aad",
                            font=dict(color='white', size=12),
                            align='left'),
                cells=dict(values=[top_frequencies.index, top_frequencies.values],
                           fill_color='rgba(0,0,0,0)',
                           font=dict(color='white', size=12),
                           align='left'))
            ])
            table_fig = style_fig(table_fig)

        return bar_fig, pie_fig, table_fig

    app.layout = html.Div(
        [
            html.Div([
                dcc.Dropdown(
                    id='numeric-dropdown',
                    options=[{'label': col, 'value': col} for col in df.select_dtypes(include=['float64', 'int64']).columns],
                    placeholder='Selecciona una columna numérica',
                    style={'width': '48%', 'margin-right': '4%'}
                ),
                dcc.Dropdown(
                    id='categorical-dropdown',
                    options=[{'label': col, 'value': col} for col in df.select_dtypes(include=['object']).columns],
                    placeholder='Selecciona una columna categórica',
                    style={'width': '48%'}
                ),
                dcc.RadioItems(
                    id='plot-type',
                    options=[
                        {'label': 'Frecuencias', 'value': 'frequencies'},
                        {'label': 'Variable numérica', 'value': 'numeric'}
                    ],
                    value='frequencies',
                    style={'margin-top': '10px', 'margin-bottom': '10px', 'color': 'white'}
                ),
                html.Button('Generar gráficos', id='generate-plots-btn', n_clicks=0),
            ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'space-between'}),
            html.Div(id="graph-output", style={'display': 'flex', 'flex-wrap': 'wrap', 'gap': '20px', 'color': 'white'}),
        ],
        style={'margin': '0px', 'height': '1000px'},
    )
    
    @app.callback(
        Output('graph-output', 'children'),
        [Input('generate-plots-btn', 'n_clicks')],
        [State('numeric-dropdown', 'value'),
         State('categorical-dropdown', 'value'),
         State('plot-type', 'value')],
    )
    def generate_plots_output(n_clicks, numeric_col, categorical_col, plot_type):
        if n_clicks:
            figures = []
            if numeric_col and plot_type == 'numeric':
                figures += generate_categorical_plots(categorical_col, numeric_col)
            elif plot_type == 'frequencies':
                figures += generate_categorical_plots(categorical_col)
            elif numeric_col:
                figures += generate_numeric_plots(numeric_col)

            if figures:
                return [dcc.Graph(figure=fig, style={'width': '30%', 'min-width': '300px'}) for fig in figures]
            return html.Div([html.H3("No se pueden generar gráficos con las selecciones actuales.")])
        return html.Div([html.H3("Seleccione una columna y presione 'Generar gráficos'.")], style={'color': 'white'})

    return app
