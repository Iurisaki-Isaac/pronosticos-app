import pandas as pd
from json import dumps

df = pd.read_csv('data_pronosticos.csv', encoding='latin1')

def filt(params):
    print(params)
    temp = df
    if params["fecha_fin"] != '':
        temp = temp[temp['Fecha Semana'] <= params['fecha_fin']]
    if params["fecha_inicio"] != '':
        temp = temp[temp['Fecha Semana'] >= params['fecha_inicio']]
    if len(params["cliente"]) > 0:
        temp= temp[temp['Nombre'].isin(params['cliente'])]
    if len(params["producto"]) > 0:
        temp= temp[temp['Producto'].isin(params['producto'])]
    return temp.to_json(orient= 'records')


def products():
    return dumps(df['Producto'].unique().tolist())

def customers():
    return dumps(df['Nombre'].unique().tolist())
        
    
    

