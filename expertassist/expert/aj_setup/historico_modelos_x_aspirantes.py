import pandas as pd
import os
from pathlib import Path

def process_aspirante_x_historico(filename):

    data = pd.ExcelFile(filename)
    data = pd.read_excel(data)
    data = data.drop_duplicates(subset=['Numero_de_Documento'])

    data = data.reset_index(drop=True)

    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    file_path = os.path.join(base_dir, 'static/HISTORICO MODELOS SATELITES VINCULADAS.xlsx')

    historic_data = pd.ExcelFile(file_path)
    historic_data = pd.read_excel(historic_data,'Worksheet')

    historic_data_activos = historic_data.loc[ historic_data["Estado"]=="Activo" ]
    historic_data_activos = historic_data_activos.drop_duplicates(subset=['Numero documento'])
    historic_data_activos = historic_data_activos.reset_index()

    historic_data_inactivos = historic_data.loc[ historic_data["Estado"]=="Inactivo" ]
    historic_data_inactivos = historic_data_inactivos.drop_duplicates(subset=['Numero documento'])
    historic_data_inactivos = historic_data_inactivos.reset_index()

    data["Paso_convocatoria"] = ""
    for index, row in data.iterrows():
        if  data.at[index,'Numero_de_Documento'] in historic_data.drop_duplicates(subset=['Numero documento'])["Numero documento"].to_list():
            data.at[index,'Paso_convocatoria'] = "Si"
        else:
            data.at[index,'Paso_convocatoria'] = "No"

    data["Estado"] = ""
    for index, row in data.iterrows():
        if data.at[index,'Numero_de_Documento'] in historic_data_activos["Numero documento"].to_list():
            data.at[index,"Estado"] = "Activo"
        elif data.at[index,'Numero_de_Documento'] in historic_data_inactivos["Numero documento"].to_list():
            data.at[index,"Estado"] = "Inactivo"
        else:
            data.at[index,"Estado"] = "No paso convocatoria"

    return data

