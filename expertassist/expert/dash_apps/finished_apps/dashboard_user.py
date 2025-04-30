import os
import pandas as pd
from dash import dcc, html, Input, Output
from django_plotly_dash import DjangoDash
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from pathlib import Path
import dash_bootstrap_components as dbc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def create_dash_app_dashboard(user, user_id):
    
    app = DjangoDash('UserDashboard', external_stylesheets=external_stylesheets)

    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
    DATABASE_PATH = BASE_DIR / 'db.sqlite3'

    def get_engine():
        try:
            return create_engine(f'sqlite:///{DATABASE_PATH}', echo=False).connect()
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None

    def load_data(engine, table_name):
        try:
            return pd.read_sql_table(table_name, engine)
        except Exception as e:
            print(f"Error loading data from {table_name}: {e}")
            return pd.DataFrame()

    def style_fig(fig):
        fig.update_layout(
            margin=dict(t=0, l=0, r=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
        )
        return fig

    def create_timeline_fig(data):
        fig = px.scatter_3d()
        fig.add_annotation(text="Bienvenido " + str(user), showarrow=False, font={"size":20})
        fig.update_layout(
            font=dict(size=12, color='white'),
        )
        return style_fig(fig)

    def create_timeline_fig_2(data):
        
        fig = go.Figure()

        fig.add_trace(go.Indicator(
                mode = "number",
                title = {"text": "<span style='font-size:1em;'>TOTAL<br>DATAFRAMES</span>", 'font_color':'white'},
                value = len(data.data_file.to_list()),
                domain = {'x': [0, 0.5], 'y': [0, 0.5]},
                number = {'font_color':'white'}
            )
        )

        return style_fig(fig)        

    def create_tasks_fig(data):
        discrete_colors = {"A": "#000000"}

        data["id_2"] = data["id"]
        data["data_file"] = data["data_file"].str.replace("uploads/","")

        fig = px.treemap(
            data,
            path=[px.Constant('DATAFRAMES'), 'area', 'id_2'],
            hover_data={
                'title': True,
                'description': True,
                'data_file': True,
            },
            color_discrete_map=discrete_colors,
        )
        fig.data[0]['textfont']['color'] = "white"
        fig.update_traces(
            textinfo="label+value",
            texttemplate="%{label}<br><br>Título: %{customdata[0]}<br>Descripción: %{customdata[1]}<br>Archivo: %{customdata[2]}",
            marker=dict(cornerradius=5),
        )
        fig.update_layout(
            margin=dict(t=0, l=0, r=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12,color="black"),
            title='Tareas'
        )
        return style_fig(fig)

    def get_figures(user_id):
        engine = get_engine()
        if engine:
            login_data = load_data(engine, 'auth_user')
            tasks_data = load_data(engine, 'expert_task')

            if user_id:
                filtered_logins = login_data[login_data['id'] == user_id]
                filtered_tasks = tasks_data[tasks_data['user_id'] == user_id]

                login_fig = create_timeline_fig(filtered_logins) if not filtered_logins.empty else style_fig(px.scatter_3d())
                tasks_fig = create_tasks_fig(filtered_tasks) if not filtered_tasks.empty else style_fig(px.scatter_3d())
                tasks_fig_2 = create_timeline_fig_2(filtered_tasks) if not filtered_tasks.empty else style_fig(px.scatter_3d())

                return login_fig, tasks_fig, tasks_fig_2

        return go.Figure(), go.Figure(), go.Figure()

    app.layout = dbc.Container(
        [
            dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0),  # Update every minute
            html.Div([
                dcc.Graph(id='login-timeline',style={'width': '50%', 'height': '25vh', 'overflowY': "show"}),
                dcc.Graph(id='tasks-bar-2',style={'width': '50%', 'height': '25vh', 'overflowY': "show"}),
                dcc.Graph(id='tasks-bar',style={'width': '100%', 'height': '25vh', 'overflowY': "show"}),
            ], style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'space-between', 'width': '100%', 'height': '25vh', 'overflowX': "show",'overflowY': "show"})
        ],
        style={'margin': '0px', 'padding': '0px'},fluid=True,
    )

    @app.callback(
        [Output('login-timeline', 'figure'),
         Output('tasks-bar', 'figure'),
         Output('tasks-bar-2', 'figure')],
        [Input('interval-component', 'n_intervals')]
    )
    def update_graphs(n):
        login_fig, tasks_fig, tasks_fig_2 = get_figures(user_id)
        return login_fig, tasks_fig, tasks_fig_2

    return app

