import pandas as pd
from json import dumps
from math import floor, ceil, log10
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import numpy as np

pd.options.mode.chained_assignment = None

df = pd.read_csv('data_procesada.csv', encoding='latin1')[['Fecha Semana','Cantidad Total', 'Cliente','Nombre','Producto','Mes','Semana']]

default_params = {
    "fecha_fin": '2023-07-31',
    "fecha_inicio": '2022-12-07',
    "fecha_fin_a": '2022-12-06',
    "fecha_inicio_a": '2021-12-06',
    "producto": ["EI-S4TA","BUJIA849"],
    "cliente": [],    
    "sustitucion": '',
    "tasa": 0,
    "desperdicio": 0
    }

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
    return int(fecha[5:7]), int(fecha[8:10])

def promedioSimpleDF(df,params):
    df_ps = []
    for producto in df['Producto'].unique():
        for cliente in df[df['Producto'] == producto]['Nombre'].unique():
            df_pc = df[(df['Nombre'] == cliente) & (df['Producto'] == producto)]
            promedio = sum(df_pc['Cantidad Total']) / len(df_pc) if len(df_pc) > 0 else 0
            fecha_inicio_r = df_pc['Fecha Semana'].unique()[0]
            fecha_fin_r = df_pc['Fecha Semana'].unique()[-1]
            ps = sum(df_pc['Cantidad Total']) / len(weekDates(fecha_inicio_r,fecha_fin_r))
            ps_input_usuario = sum(df_pc['Cantidad Total']) / len(weekDates(params['fecha_inicio_a'],params['fecha_fin_a']))
            df_ps.append([producto,cliente,promedio,ps,ps_input_usuario])
    df_ps = pd.DataFrame(df_ps)
    df_ps.columns = ['Producto','Cliente','Promedio','Promedio Simple','Promedio Simple IU']
    return df_ps

def noSemanaYAno(fechas):
    semanas = []
    anos = []
    for fecha in fechas:
        if fecha[-2:] == '01':
            semana = 1 + ((int(fecha[5:7])*4)-4)
            semanas.append(semana)
        if fecha[-2:] == '09':
            semana = 2 + ((int(fecha[5:7])*4)-4)
            semanas.append(semana)
        if fecha[-2:] == '16':
            semana = 3 + ((int(fecha[5:7])*4)-4)
            semanas.append(semana)
        if fecha[-2:] == '24':
            semana = 4 + ((int(fecha[5:7])*4)-4)
            semanas.append(semana)
        anos.append(int(fecha[0:4]))
    return semanas, anos

def getDia(v,mes):
    x = (mes-1)*4
    y = (v-x)
    if y == 1:
        return 1
    if y == 2:
        return 9
    if y == 3:
        return 16
    if y == 4:
        return 24


def distAC(params):
    df2 = pd.read_csv('data_procesada2.csv',encoding='latin1')
    df2["Semana"], df2["Año"] = noSemanaYAno(df2['Fecha Semana'].values)
    if len(params["cliente"]) > 0:
        df2= df2[df2['Nombre'].isin(params['cliente'])]
    df2 = df2[df2["Producto"].isin(params['producto'])]
    e_year = dt.now()
    i_year = dt.now() - relativedelta(years=1)
    e_year = e_year.strftime("%Y-%m-%d")
    i_year = i_year.strftime("%Y-%m-%d")   
    lastyear_df = df2[(df2['Fecha Semana'] <= e_year) & (df2['Fecha Semana'] >= i_year)]        
    dist_table = []
    
    for producto in params["producto"]:
        for cliente in lastyear_df[lastyear_df["Producto"] == producto]['Nombre'].unique():
            temp = lastyear_df[(lastyear_df["Producto"] == producto) & (lastyear_df["Nombre"] == cliente)]
            for s in range(1,49):
                mes = ceil(s/4)
                dia = getDia(s, mes)
                if s in temp["Semana"].values:
                    cantidad = temp[temp["Semana"] == s]['Cantidad Total'].values[0]
                    porcentaje = cantidad / sum(temp['Cantidad Total'])
                else:
                    porcentaje = 0
                dist_table.append([producto, cliente, porcentaje, mes, dia ])
    
    dist_table = pd.DataFrame(dist_table)
    dist_table.columns = ['Producto','Cliente','Porcentaje','Mes','Dia']    
    return dist_table

def distAllYears(params):    
    df2 = pd.read_csv('data_procesada2.csv',encoding='latin1')
    df2["Semana"], df2["Año"] = noSemanaYAno(df2['Fecha Semana'].values)
    if len(params["cliente"]) > 0:
        df2= df2[df2['Nombre'].isin(params['cliente'])]
    df2 = df2[df2["Producto"].isin(params['producto'])]

    dist_table = []
    for producto in params["producto"]:            
        for cliente in df2[df2['Producto'] == producto]['Nombre'].unique():
            temp = df2[(df2['Nombre'] == cliente) & (df2['Producto'] == producto)]                 
            if not temp.empty:                
                #obtenemos importancia
                temp["Importancia"] = [1-log10(1 + abs(a - max(temp["Año"].values))) for a in temp["Año"].values]
            
                #repeticiones R
                temp["R"] = [int(i*10) for i in temp["Importancia"].values]
            
                #obteniendo distribucion anual
                distribucion = []
                for a in temp["Año"].unique():
                    temp_a = temp[temp["Año"] == a]
                    for s in temp_a["Semana"].unique():
                        cantidad = temp_a[temp_a["Semana"] == s]['Cantidad Total'].values[0]
                        if sum(temp_a["Cantidad Total"].values) != 0:
                            dist = (cantidad * 100) / sum(temp_a["Cantidad Total"].values)
                        else:
                            dist = 0
                        distribucion.append(dist)

                temp["Distribucion Anual"] = distribucion
                     
                #obteniendo R*D   
                temp["R*D"] = temp["R"] * temp["Distribucion Anual"]
            
                # distribucion con peso
                dist_p = []
                for s in temp["Semana"].unique():
                    temp_s = temp[temp["Semana"] == s]
                    dist_calc = sum(temp_s["R*D"].values) / sum(temp_s["R"].values)
                    dist_p.append([s,dist_calc])
                    
                dist_p = pd.DataFrame(dist_p)
                dist_p.columns = ["Semana","Distribucion"]
                dist_p = dist_p.sort_values("Semana")                
                dist_p["Porcentaje"] = [v/sum(dist_p["Distribucion"].values) for v in dist_p["Distribucion"].values]                
                
                for s in dist_p["Semana"].values:
                    mes = ceil(s/4)
                    dia = getDia(s,mes)
                    porcentaje = dist_p[dist_p["Semana"] == s]["Porcentaje"].values[0]
                    dist_table.append([producto, cliente, porcentaje, mes, dia])
            
    dist_table = pd.DataFrame(dist_table)
    dist_table.columns = ['Producto','Cliente','Porcentaje','Mes','Dia']
    return dist_table


def tablaPromedioSimple(df,params):
    df_ps= promedioSimpleDF(df,params)    
    
    out_df = []
    for date in weekDates(params["fecha_inicio"], params["fecha_fin"]):
        for cliente in df_ps["Cliente"].unique():
            for producto in df_ps[df_ps["Cliente"] == cliente]["Producto"].unique():
                cantidad = df_ps[(df_ps["Producto"] == producto) & (df_ps["Cliente"] == cliente)]["Promedio Simple"].unique()[0]
                out_df.append([date.strftime('%Y-%m-%d'),cliente,producto,cantidad])
        
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
                out_df.append([date.strftime('%Y-%m-%d'),cliente,producto,cantidad]) if cantidad>0 else out_df
        
    return pd.DataFrame(out_df)
    
    
def tablaTemporalAbierto(df, params, modo_pronostico):    
    if modo_pronostico == "temporal_a":
        dist_table = distAC(params)
    if modo_pronostico == "temporal_a2":
        dist_table = distAllYears(params)
    
    df_ps = promedioSimpleDF(df,params)
    
    out_df = []
    for fecha in weekDates(params['fecha_inicio'],params['fecha_fin']):
        for producto in df['Producto'].unique():
            df_p = df[df['Producto'] == producto]
            for cliente in df_p['Nombre'].unique():                
                #tomo el promedio simple del input del usuario
                mes, dia = getMonthAndDay(fecha.strftime("%Y-%m-%d"))                
                promedio = df_ps[(df_ps['Cliente'] == cliente) & (df_ps['Producto'] == producto)]['Promedio Simple IU'].unique()[0]
                total_extrapolado = promedio * 48
                temp = dist_table[(dist_table['Producto'] == producto) & (dist_table['Cliente'] == cliente) & (dist_table['Mes'] == mes) & (dist_table['Dia'] == dia)]
                porcentaje = temp['Porcentaje'].unique()[0] if not temp.empty else 0
                pronostico = total_extrapolado * porcentaje
                if pronostico > 0:
                    out_df.append([fecha.strftime("%Y-%m-%d"), cliente, producto, pronostico])
                
    return pd.DataFrame(out_df)

def Croston(ts,extra_periods=1,alpha=0.4):
    d = np.array(ts) # Transform the input into a numpy array
    cols = len(d) # Historical period length
    d = np.append(d,[np.nan]*extra_periods) # Append np.nan into the demand array to cover future periods
    
    #level (a), periodicity(p) and forecast (f)
    a,p,f = np.full((3,cols+extra_periods),np.nan)
    q = 1 #periods since last demand observation
    
    # Initialization
    first_occurence = np.argmax(d[:cols]>0)
    a[0] = d[first_occurence]
    p[0] = 1 + first_occurence
    f[0] = a[0]/p[0]
# Create all the t+1 forecasts
    for t in range(0,cols):        
        if d[t] > 0:
            a[t+1] = alpha*d[t] + (1-alpha)*a[t] 
            p[t+1] = alpha*q + (1-alpha)*p[t]
            f[t+1] = a[t+1]/p[t+1]
            q = 1           
        else:
            a[t+1] = a[t]
            p[t+1] = p[t]
            f[t+1] = f[t]
            q += 1
       
    # Future Forecast 
    a[cols+1:cols+extra_periods] = a[cols]
    p[cols+1:cols+extra_periods] = p[cols]
    f[cols+1:cols+extra_periods] = f[cols]
                      
    df = pd.DataFrame.from_dict({"Demand":d,"Forecast":f,"Period":p,"Level":a,"Error":d-f})
    return df

def Croston_TSB(ts,extra_periods=1,alpha=0.4,beta=0.4):
    d = np.array(ts) # Transform the input into a numpy array
    cols = len(d) # Historical period length
    d = np.append(d,[np.nan]*extra_periods) # Append np.nan into the demand array to cover future periods
    
    #level (a), probability(p) and forecast (f)
    a,p,f = np.full((3,cols+extra_periods),np.nan)
# Initialization
    first_occurence = np.argmax(d[:cols]>0)
    a[0] = d[first_occurence]
    p[0] = 1/(1 + first_occurence)
    f[0] = p[0]*a[0]
                 
    # Create all the t+1 forecasts
    for t in range(0,cols): 
        if d[t] > 0:
            a[t+1] = alpha*d[t] + (1-alpha)*a[t] 
            p[t+1] = beta*(1) + (1-beta)*p[t]  
        else:
            a[t+1] = a[t]
            p[t+1] = (1-beta)*p[t]       
        f[t+1] = p[t+1]*a[t+1]
        
    # Future Forecast
    a[cols+1:cols+extra_periods] = a[cols]
    p[cols+1:cols+extra_periods] = p[cols]
    f[cols+1:cols+extra_periods] = f[cols]
                      
    df = pd.DataFrame.from_dict({"Demand":d,"Forecast":f,"Period":p,"Level":a,"Error":d-f})
    return df

def tablaCroston(products_with_data ,params, modo_pronostico):
    df2 = pd.read_csv('data_procesada2.csv',encoding='latin1')
    if len(params["cliente"]) > 0:
        df2= df2[df2['Nombre'].isin(params['cliente'])]
    df2 = df2[df2["Producto"].isin(params['producto'])]
    out_df2 = []
    for producto in products_with_data:    
        temp = df2[df2['Producto'] == producto]
        for cliente in temp['Nombre'].unique():
            temp2 = temp[temp['Nombre'] == cliente]
            temp2 = temp2[(temp2['Fecha Semana'] >= params["fecha_inicio_a"]) & (temp2['Fecha Semana'] <= params['fecha_fin_a'])]            
            ep = len(weekDates(params['fecha_inicio'], params['fecha_fin']))
            if modo_pronostico == 'croston' and len(temp2['Cantidad Total']) > 0:
                r_croston = Croston(temp2['Cantidad Total'], extra_periods=ep)
            elif modo_pronostico == 'croston_tsb' and len(temp2['Cantidad Total']) > 0:
                r_croston = Croston_TSB(temp2['Cantidad Total'], extra_periods=ep)
            pronostico = r_croston['Forecast'].values[-1]
            for fecha in weekDates(params['fecha_inicio'], params['fecha_fin']):
                out_df2.append([fecha.strftime("%Y-%m-%d"), cliente, producto, pronostico])   
    
    return pd.DataFrame(out_df2)

def dataParaGraficar(df, params):
    dic = {}
    values = []    
    for producto in df['Producto'].unique():
        temp = df[df['Producto'] == producto]
        for fecha in weekDates(params['fecha_inicio'], params['fecha_fin']):            
            if fecha.strftime("%Y-%m-%d") in temp['Fecha Semana'].values:                
                v = temp[temp['Fecha Semana'] == fecha.strftime("%Y-%m-%d")]['Cantidad Pronostico'].values[0]
                values.append(float(v))
            else:
                values.append(float(0))
        dic[producto] = values
        values = []
    
    return dic

def filt(params,modo_pronostico):    
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
        return "[]","[]","[]"
    
    #tabla de fecha de facturación (análisis)
    temp2 = temp
    if params["fecha_fin_a"] != '':
        temp2 = temp2[temp2["Fecha Semana"] < params['fecha_fin_a']]
    else:
        temp2 = temp2[temp2["Fecha Semana"] < default_params['fecha_fin_a']]
    if params["fecha_inicio_a"] != '':
        temp2 = temp2[temp2["Fecha Semana"] > params['fecha_inicio_a']]
    else:
        temp2 = temp2[temp2["Fecha Semana"] > default_params['fecha_inicio_a']]
    
    #revisar si hay datos de facturacion de fechas seleccionadas
    if temp2.empty:
        return "[]","[]","[]"
    
    #tabla pronostico simple
    if modo_pronostico == "simple":
        out_df = tablaPromedioSimple(temp2,params)
        
    #tabla pronostico temporal cerrado
    if modo_pronostico == "temporal_c":
        out_df = tablaTemporalCerrado(temp2,params)
        
    #tabla pronostico temporal abierto y temporal abierto con peso
    if modo_pronostico == "temporal_a" or modo_pronostico == "temporal_a2":
        out_df = tablaTemporalAbierto(temp2,params,modo_pronostico)
        
    #tabla pronostico croston y croston tsb
    if modo_pronostico == "croston" or modo_pronostico == "croston_tsb":
        out_df = tablaCroston(temp2['Producto'].unique(), params, modo_pronostico)
    
    #nombres de columnas
    if out_df.empty:        
        return out_df.to_json(orient= 'records'), out_df.to_json(orient= 'records'), out_df.to_json(orient= 'records')
    else:
        out_df.columns = ['Fecha Semana','Nombre','Producto','Cantidad Pronostico']

    #aplicar tasa de crecimiento y desperdicio
    if params["tasa"] != '':
        out_df['Cantidad Pronostico'] = out_df['Cantidad Pronostico'] * (1+(float(params["tasa"])/100))
    if params["desperdicio"] != '':
        out_df['Cantidad Pronostico'] = out_df['Cantidad Pronostico'] * (1+(float(params["desperdicio"])/100))
    
    # TABLA RESUMEN-----------------------#
    if modo_pronostico == "simple":
        tecnica = "Promedio Simple"
    elif modo_pronostico == "temporal_c":
        tecnica = "Temporalidad cerrada"
    elif modo_pronostico == "temporal_a":
        tecnica = "Temporalidad abierta"
    elif modo_pronostico == "temporal_a2":
        tecnica = "Temporalidad abierta con peso"
    elif modo_pronostico == "croston":
        tecnica = "Croston"
    elif modo_pronostico =="croston_tsb":
        tecnica = "Croston TSB"
    
    resumen_df = []
    for producto in out_df['Producto'].unique():
        total = sum(out_df[out_df['Producto'] == producto]['Cantidad Pronostico'])
        promedio_semana = total / len(weekDates(params['fecha_inicio'],params['fecha_fin']))        
        fi = params['fecha_inicio']
        ff = params['fecha_fin']
        resumen_df.append([tecnica, producto, fi, ff, promedio_semana, total])
    resumen_df = pd.DataFrame(resumen_df)
    resumen_df.columns = ['Tecnica','Producto','Fecha inicio','Fecha fin','Promedio semana','Total']
    #-------------------------------------#        
    
    dpg = dataParaGraficar(out_df, params)
    return out_df.to_json(orient= 'records'),resumen_df.to_json(orient = 'records'), dpg


def realPastData(params):
    last_year_i = str(int(params["fecha_inicio"][:4])-1)
    last_year_e = str(int(params["fecha_fin"][:4])-1)
    
    last_date_i = last_year_i + params["fecha_inicio"][4:]
    last_date_e = last_year_e + params["fecha_fin"][4:]
    
    wd = weekDates(last_date_i,last_date_e)
    df2 = pd.read_csv('data_procesada2.csv',encoding='latin1')
    if len(params["cliente"]) > 0:
        df2= df2[df2['Nombre'].isin(params['cliente'])]
    df2 = df2[df2["Producto"].isin(params['producto'])]
    
    dic = {}
    values = []
    for producto in df2["Producto"].unique():
        temp = df2[df2["Producto"] == producto]
        for fecha in wd:
            if fecha.strftime("%Y-%m-%d") in temp["Fecha Semana"].values:
                v = temp[temp["Fecha Semana"] == fecha.strftime("%Y-%m-%d")]['Cantidad Total'].values[0]
            else:
                v = 0
            values.append(float(v))
        dic[producto] = values
        values = []
        
    return dic
    

