import pandas as pd
from json import dumps
from math import floor, ceil
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

df = pd.read_csv('data_procesada.csv', encoding='latin1')[['Fecha Semana','Cantidad Total', 'Cliente','Nombre','Producto','Mes','Semana']]

default_params = {
    "fecha_fin": '2023-08-31',
    "fecha_inicio": '2022-11-18',
    "fecha_fin_a": '2022-11-18',
    "fecha_inicio_a": '2021-11-18',
    "producto": ["EI-S4TA"],
    "cliente": ["INDUSTRIAS ACROS WHIRLPOOL S. DE R.L. DE C.V."],
    "modo_pronostico": "temporal_a",
    "sustitucion": '',
    "tasa": 0,
    "desperdicio": 0
    }

def filt(params):
    print(params)
    temp = df
    #filtrado por cliente y producto (tomando en cuenta sustitución si es que la hay)
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
        return "[]","[]"
    
    #tabla de fecha de facturación (análisis)
    temp2 = temp
    if params["fecha_fin_a"] != '':
        temp2 = temp2[temp2['Fecha Semana'] < params['fecha_fin_a']]
    else:
        temp2 = temp2[temp2['Fecha Semana'] < default_params['fecha_fin_a']]
    if params["fecha_inicio_a"] != '':
        temp2 = temp2[temp2['Fecha Semana'] > params['fecha_inicio_a']]
    else:
        temp2 = temp2[temp2['Fecha Semana'] > default_params['fecha_inicio_a']]
    
    #revisar si hay datos de facturacion de fechas seleccionadas
    if temp2.empty:
        return "[]","[]"
    
    #tabla pronostico simple
    if params["modo_pronostico"] == "simple":
        out_df = tablaPromedioSimple(temp2,params)
        
    #tabla pronostico temporal cerrado
    if params["modo_pronostico"] == "temporal_c":
        out_df = tablaTemporalCerrado(temp2,params)
        
    #tabla pronostico temporal abierto
    if params["modo_pronostico"] == "temporal_a":
        out_df = tablaTemporalAbierto(temp,temp2,params)
    
    #nombres de columnas
    if out_df.empty:
        return out_df.to_json(orient= 'records'), out_df.to_json(orient= 'records')
    else:
        out_df.columns = ['Fecha Semana','Nombre','Producto','Cantidad Pronostico']
    
    # TABLA RESUMEN-----------------------#
    resumen_df = []
    for producto in out_df['Producto'].unique():
        total = sum(out_df[out_df['Producto'] == producto]['Cantidad Pronostico'])
        promedio_semana = total / len(weekDates(params['fecha_inicio'],params['fecha_fin']))        
        fi = params['fecha_inicio']
        ff = params['fecha_fin']
        resumen_df.append([producto,fi,ff,ceil(promedio_semana),total])
    resumen_df = pd.DataFrame(resumen_df)
    resumen_df.columns = ['Producto','Fecha inicio','Fecha fin','Promedio semana','Total']
    #-------------------------------------#

    out_df.to_csv('out.csv', index = False, encoding="latin1")
    resumen_df.to_csv('resumen.csv', index = False, encoding="latin1")
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

def weekDates(i_date,e_date):
    return [date for date in pd.date_range(i_date,e_date) if date.day in [1,9,16,24]]

def getMonthAndDay(fecha):
    return fecha[5:7], fecha[8:10]

def promedioSimpleDF(df,params):
    df_ps = []
    for producto in df['Producto'].unique():
        for cliente in df['Nombre'].unique():
            df_pc = df[(df['Nombre'] == cliente) & (df['Producto'] == producto)]
            promedio = sum(df_pc['Cantidad Total']) / len(df_pc)
            fecha_inicio_r = df_pc['Fecha Semana'].unique()[0]
            fecha_fin_r = df_pc['Fecha Semana'].unique()[-1]
            ps = sum(df_pc['Cantidad Total']) / len(weekDates(fecha_inicio_r,fecha_fin_r))
            ps_input_usuario = sum(df_pc['Cantidad Total']) / len(weekDates(params['fecha_inicio_a'],params['fecha_fin_a']))
            df_ps.append([producto,cliente,promedio,ps,ps_input_usuario])
    df_ps = pd.DataFrame(df_ps)
    df_ps.columns = ['Producto','Cliente','Promedio','Promedio Simple','Promedio Simple IU']
    return df_ps

def tablaPromedioSimple(df,params):
    df_ps= promedioSimpleDF(df,params)
    #df_ps.to_csv('out2.csv', index = False, encoding = 'latin1')
    
    out_df = []
    for date in weekDates(params["fecha_inicio"], params["fecha_fin"]):
        for cliente in df_ps["Cliente"].unique():
            for producto in df_ps["Producto"].unique():
                cantidad = df_ps[(df_ps["Producto"] == producto) & (df_ps["Cliente"] == cliente)]["Promedio Simple"].unique()[0]
                out_df.append([date.strftime('%Y-%m-%d'),cliente,producto,ceil(cantidad)])
        
    return pd.DataFrame(out_df)


def tablaTemporalCerrado(df,params):
    results_df = []
    for mes in range(1,13):
        for semana in range(1,5):
            for producto in df['Producto'].unique():
                for cliente in df['Nombre'].unique():
                    df_mspc = df[(df['Producto'] == producto) & (df['Mes'] == mes) & (df['Semana'] == semana) & (df['Nombre'] == cliente)]
                    if len(df_mspc) < 1:
                        results_df.append([cliente,producto,mes,semana,0])
                    else:
                        results_df.append([cliente,producto,mes,semana,sum(df_mspc['Cantidad Total'])/len(df_mspc)])
                    
    results_df = pd.DataFrame(results_df)    
    
    out_df = []
    for date in weekDates(params['fecha_inicio'], params['fecha_fin']):
        for cliente in results_df[0].unique():
            for producto in results_df[1].unique():
                temp3 = results_df[(results_df[2] == date.month) & (results_df[3] == floor(date.day/8)+1)]
                temp3 = temp3[(temp3[0] == cliente) & (temp3[1] == producto)]
                cantidad = temp3[4].unique()[0] if len(temp3) > 0 else 0
                if params["tasa"] != '':
                    cantidad = cantidad * (1+(float(params["tasa"])/100))
                if params["desperdicio"] != '':
                    cantidad = cantidad * (1+(float(params["desperdicio"])/100))
                out_df.append([date.strftime('%Y-%m-%d'),cliente,producto,ceil(cantidad)]) if cantidad>0 else out_df
        
    return pd.DataFrame(out_df)
    
    
def tablaTemporalAbierto(df,df2,params):
    e_year = dt.now()
    i_year = dt.now() - relativedelta(years=1)
    e_year = e_year.strftime("%Y-%m-%d")
    i_year = i_year.strftime("%Y-%m-%d")
    lastyear_df = df[(df['Fecha Semana'] < e_year) & (df['Fecha Semana'] > i_year)]
    total_ventas = sum(lastyear_df["Cantidad Total"])
    week_dates = [fecha.strftime("%Y-%m-%d") for fecha in weekDates(i_year, e_year)]
    
    dist_table = []
    for fecha in week_dates:
        for producto in lastyear_df['Producto'].unique():
            for cliente in lastyear_df['Nombre'].unique():
                if fecha in lastyear_df['Fecha Semana'].unique():            
                    porcentaje = lastyear_df[lastyear_df["Fecha Semana"] == fecha]["Cantidad Total"].unique()[0] / total_ventas            
                else:
                    porcentaje = 0
                mes, dia = getMonthAndDay(fecha)
                dist_table.append([fecha, producto, cliente, porcentaje, mes, dia])
    
    dist_table = pd.DataFrame(dist_table)
    dist_table.columns = ['Fecha Semana','Producto','Cliente','Porcentaje','Mes','Dia']    
    df_ps = promedioSimpleDF(df2,params)    
    
    out_df = []
    for fecha in weekDates(params['fecha_inicio'],params['fecha_fin']):
        for producto in df2['Producto'].unique():
            df2_p = df2[df2['Producto'] == producto]
            for cliente in df2_p['Nombre'].unique():
                #tomo el promedio simple del input del usuario
                mes, dia = getMonthAndDay(fecha.strftime("%Y-%m-%d"))
                promedio = df_ps[(df_ps['Cliente'] == cliente) & (df_ps['Producto'] == producto)]['Promedio Simple IU'].unique()[0]
                total_extrapolado = promedio * 48
                porcentaje = dist_table[(dist_table['Producto'] == producto) & (dist_table['Cliente'] == cliente) & (dist_table['Mes'] == mes) & (dist_table['Dia'] == dia)]['Porcentaje'].unique()[0]                
                pronostico = total_extrapolado * porcentaje
                if pronostico > 0:
                    out_df.append([fecha.strftime("%Y-%m-%d"), cliente, producto, pronostico])
                
    #print(dist_table)
    #print(df_ps)
    return pd.DataFrame(out_df)

