import pandas as pd
from json import dumps
from math import floor, ceil

df = pd.read_csv('data_procesada.csv', encoding='latin1')[['Fecha Semana','Cantidad Total', 'Cliente','Nombre','Producto','Mes','Semana']]

default_params = {
    "fecha_fin": '2023-04-01',
    "fecha_inicio": '2022-11-01',
    "fecha_fin_a": '2021-12-31',
    "fecha_inicio_a": '2018-01-01',
    "producto": ["BUJIA849","EI-S4TA"],
    "cliente": ["INDUSTRIAS ACROS WHIRLPOOL S. DE R.L. DE C.V."],
    "tasa_crecimiento": 0,
    "desperdicio": 0
    }

def filt(params):
    print(params)
    temp = df    
    if len(params["cliente"]) > 0:
        temp= temp[temp['Nombre'].isin(params['cliente'])]
    if len(params["producto"]) > 0:
        if params["sustitucion"] != '' and len(params["producto"]) == 1:
            temp = temp[temp['Producto'].isin([params["producto"][0],params["sustitucion"]])]
            new_col = [params["producto"][0] for i in range(len(temp))]
            temp['Producto'] = new_col
        else:
            temp= temp[temp['Producto'].isin(params["producto"])]
    else:
        return
    
    #obtener promedios de semana para las fechas de analisis
    temp2 = temp
    if params["fecha_fin_a"] != '':
        temp2 = temp2[temp2['Fecha Semana'] < params['fecha_fin_a']]
    else:
        temp2 = temp2[temp2['Fecha Semana'] < default_params['fecha_fin_a']]
    if params["fecha_inicio_a"] != '':
        temp2 = temp2[temp2['Fecha Semana'] > params['fecha_inicio_a']]
    else:
        temp2 = temp2[temp2['Fecha Semana'] > default_params['fecha_inicio_a']]
    
    #print("DATAFRAME",temp2[(temp2['Fecha Semana'] < params['fecha_fin']) & (temp2['Fecha Semana'] > params['fecha_inicio'])])
    results_df = []
    for mes in range(1,13):
        for semana in range(1,5):
            for producto in temp2['Producto'].unique():
                for cliente in temp2['Nombre'].unique():
                    temp2_mspc = temp2[(temp2['Producto'] == producto) & (temp2['Mes'] == mes) & (temp2['Semana'] == semana) & (temp2['Nombre'] == cliente)]
                    if len(temp2_mspc) < 1:
                        results_df.append([cliente,producto,mes,semana,0])
                    else:
                        results_df.append([cliente,producto,mes,semana,sum(temp2_mspc['Cantidad Total'])/len(temp2_mspc)])
                    
    results_df = pd.DataFrame(results_df)
    
    out_df = []
    for date in futureWeekDates(params['fecha_inicio'], params['fecha_fin']):
        for cliente in results_df[0].unique():
            for producto in results_df[1].unique():
                temp3 = results_df[(results_df[2] == date.month) & (results_df[3] == floor(date.day/8)+1)]
                cantidad = temp3[4].unique()[0] if len(temp3) > 0 else 0
                if params["tasa"] != '':
                    cantidad = cantidad * (1+(float(params["tasa"])/100))
                if params["desperdicio"] != '':
                    cantidad = cantidad * (1+(float(params["desperdicio"])/100))
                out_df.append([date.strftime('%Y-%m-%d'),cliente,producto,ceil(cantidad)]) if cantidad>0 else out_df
        
    out_df = pd.DataFrame(out_df)
    if out_df.empty:
        return out_df.to_json(orient= 'records'), out_df.to_json(orient= 'records')
    else:
        out_df.columns = ['Fecha Semana','Nombre','Producto','Cantidad Pronostico']
    
    # TABLA RESUMEN-----------------------#
    resumen_df = []
    for producto in out_df['Producto'].unique():
        total = sum(out_df[out_df['Producto'] == producto]['Cantidad Pronostico'])
        promedio_semana = total / len(pd.date_range(params['fecha_inicio'],params['fecha_fin']))
        fi = params['fecha_inicio']
        ff = params['fecha_fin']
        resumen_df.append([producto,fi,ff,ceil(promedio_semana),total])
    resumen_df = pd.DataFrame(resumen_df)
    resumen_df.columns = ['Producto','Fecha inicio','Fecha fin','Promedio semana','Total']
    #-------------------------------------#

    return out_df.to_json(orient= 'records'),resumen_df.to_json(orient = 'records')


def products(data):
    if 'cliente' in data:
        if len(data['cliente']) > 0:
            return dumps(df[df['Nombre'].isin(data["cliente"])]['Producto'].unique().tolist())
        else:
            return dumps(df['Producto'].unique().tolist())    
    else:
        return dumps(df['Producto'].unique().tolist())

def customers(data):
    if 'producto' in data:
        if len(data['producto']) > 0:
            return dumps(df[df['Producto'].isin(data["producto"])]['Nombre'].unique().tolist()) 
        else:
            return dumps(df['Nombre'].unique().tolist())    
    else:
        return dumps(df['Nombre'].unique().tolist())

def futureWeekDates(i_date,e_date):
    return [date for date in pd.date_range(i_date,e_date) if date.day in [1,9,16,24]]
    
    

