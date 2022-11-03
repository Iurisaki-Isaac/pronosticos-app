import pandas as pd
from json import dumps

df = pd.read_csv('data_procesada.csv', encoding='latin1')

def filt(params):
    temp = df
    if "fecha_fin" in params.keys():
        temp = temp[temp['Fecha Semana'] <= params['fecha_fin']]
    if "fecha_inicio" in params.keys():
        temp = temp[temp['Fecha Semana'] >= params['fecha_inicio']]
    if "cliente" in params.keys():
        temp= temp[temp['Cliente'].isin(params['cliente'])]
    if "producto" in params.keys():
        temp= temp[temp['Producto'].isin(params['producto'])]
    return temp.to_json(orient= 'records')


def products():
    return dumps(df['Producto'].unique().tolist())

def customers():
    return dumps(df['Cliente'].unique().tolist())
        
    
    

