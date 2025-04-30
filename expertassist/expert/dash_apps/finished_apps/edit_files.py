import dash_ag_grid as dag
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from django_plotly_dash import DjangoDash
import os
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


def create_dash_app_edit_file(file_path):
    app = DjangoDash('Edit_File', external_stylesheets=external_stylesheets)

    short_name, extension = os.path.splitext(os.path.basename(file_path))
    extension = extension.lower()[1:]

    if extension == 'csv':
        df = pd.read_csv(file_path)
    elif extension in ['xls', 'xlsx']:
        df = pd.read_excel(file_path, engine='openpyxl')
    else:
        raise ValueError("Unsupported file type")

    df['id'] = df.index

    table = dag.AgGrid(
        id="portfolio-table",
        columnDefs=[{"field": i, "resizable": True} for i in df.columns],
        rowData=df.to_dict("records"),
        columnSize="autoSize",
        defaultColDef={"editable": True, "resizable": True},
        dashGridOptions={"rowSelection": "multiple", "undoRedoCellEditing": True, "rowDragManaged": True},
    )

    app.layout = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        table,
                                        html.Div(
                                            [
                                                html.Button('Agregar fila', id='add-row-btn', n_clicks=0),
                                                html.Button('Eliminar fila', id='delete-row-btn', n_clicks=0),
                                                html.Button('Descargar Datos', id='download-data-btn', n_clicks=0),
                                                html.Button('Guardar Datos', id='save-changes-btn', n_clicks=0),
                                                dcc.Download(id="download-data"),
                                            ],
                                            className="d-flex justify-content-between mt-3",
                                        ),
                                    ]
                                ),
                                style={'height': '100%'},
                            )
                        ],
                        width=12,
                        style={'height': '100vh'},
                    ),
                ],
                className="py-4",
                style={'height': '100%'},
            ),
        ],
        fluid=True,
        style={'height': '100vh'},
    )

    @app.callback(
        Output("portfolio-table", "rowData"),
        [Input("delete-row-btn", "n_clicks"),
         Input("add-row-btn", "n_clicks")],
        [State("portfolio-table", "selectedRows"),
         State("portfolio-table", "rowData")],
        prevent_initial_call=True,
    )
    def update_dash_table(n_dlt, n_add, selected, data):
        df = pd.DataFrame(data)

        if n_add and n_add > n_dlt:
            new_row = {col: '' for col in df.columns}
            new_row['id'] = df['id'].max() + 1 if not df.empty else 0
            new_row_df = pd.DataFrame([new_row])
            df = pd.concat([new_row_df, df], ignore_index=True)
        elif n_dlt and n_dlt > n_add and selected:
            selected_ids = {row['id'] for row in selected}
            df = df[~df['id'].isin(selected_ids)]

        return df.to_dict("records")

    @app.callback(
        Output("download-data", "data"),
        Input("download-data-btn", "n_clicks"),
        State("portfolio-table", "rowData"),
        prevent_initial_call=True
    )
    def download_data(n_clicks, data):
        df = pd.DataFrame(data)
        return dcc.send_data_frame(df.to_excel, str(short_name) + "_edited.xlsx", index=False)

    @app.callback(
        Output("save-changes-btn", "children"),
        Input("save-changes-btn", "n_clicks"),
        State("portfolio-table", "rowData"),
        prevent_initial_call=True
    )
    def save_data(n_clicks, data):
        if n_clicks and n_clicks > 0:
            try:
                if n_clicks:
                    df = pd.DataFrame(data)
                    if extension == 'csv':
                        df.to_csv(file_path, index=False)
                    elif extension in ['xls', 'xlsx']:
                        df.to_excel(file_path, index=False)
                    return html.Div('¡Cambios guardados correctamente!', style={'color': 'green'})
            except Exception as e:
                return html.Div(f'Error al guardar cambios: {e}', style={'color': 'red'})
        return ''

    return app
