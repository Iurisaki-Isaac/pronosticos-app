# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 14:00:42 2022

@author: isaac
"""

from os import chdir
from statistics import mean
from math import ceil
import pandas as pd
import datetime as dt
import time

inicio = time.time()

chdir('./')

def weekDates(i_date,e_date):
    return [date for date in pd.date_range(i_date,e_date) if date.day in [1,9,16,24]]

df = pd.read_html('./Reportes/Ventas 2017-2022.htm')[0]
df = df.drop(columns = ['Clase','Peso','Linea','Zona'])

mapping_dict = {'Ene':'JAN',
'Feb':'FEB',
'Mar':'MAR',
'Abr':'APR',
'May':'MAY',
'Jun':'JUN',
'Jul':'JUL',
'Ago':'AUG',
'Sep':'SEP',
'Oct':'OCT',
'Nov':'NOV',
'Dic':'DEC'}

df['Fecha'] = df["Fecha"].apply(lambda x: dt.datetime.strptime(x.replace(x.split('-')[1],mapping_dict[x.split('-')[1]].capitalize()), "%d-%b-%Y"))
df_ncred = df[df['Tipo'] == 'N/CRED.']
df = df[df['Tipo'] != 'N/CRED.']


dia_semana = []
no_semana = []
fecha_semana = []
year = []
for fecha in df['Fecha']:
    dia_semana.append(pd.Timestamp(fecha).dayofweek)
    year.append(fecha.year)
    if fecha.day <= 8:
        semana = 1
        fecha_s = fecha.replace(day = 1)
    elif fecha.day > 8 and fecha.day < 16:
        semana = 2
        fecha_s = fecha.replace(day = 9)
    elif fecha.day >= 16 and fecha.day < 24:
        semana = 3
        fecha_s = fecha.replace(day = 16)
    elif fecha.day >= 24:
        semana = 4
        fecha_s = fecha.replace(day = 24)
    no_semana.append(semana)
    fecha_semana.append(fecha_s)
    

df['Dia Semana'] = dia_semana
df['Semana'] = no_semana
df['Fecha Semana'] = fecha_semana
df['Año'] = year


new_df = []
for cliente in df['Cliente'].unique():
    df_c = df[df['Cliente'] == cliente]
    nombre = df_c['Nombre'].unique()[0]
    for producto in df_c['Producto'].unique():
        df_cp = df_c[df_c['Producto'] == producto]
        for year in df_cp['Año'].unique():
            df_cpa = df_cp[df_cp['Año'] == year]
            cantidad_total_year = sum(df_cpa['Cantidad'])
            for mes in df_cpa['Mes'].unique():
                df_cpam = df_cpa[df_cpa['Mes'] == mes]
                for semana in df_cpam['Semana'].unique():
                    df_cpams = df_cpam[df_cpam['Semana'] == semana]
                    f_semana = df_cpams['Fecha Semana'].unique()[0]
                    no_ventas = len(df_cpams)
                    cantidad_Total = sum(df_cpams['Cantidad'])
                    importe_Total = sum(df_cpams['Importe'])
                    new_df.append([f_semana,cantidad_Total,cantidad_total_year,importe_Total,cliente,nombre,producto,year,mes,semana,no_ventas])

df2 = pd.DataFrame(new_df)
df2.columns = ['Fecha Semana','Cantidad Total','Cantidad Total Año','Importe Total','Cliente','Nombre','Producto','Año','Mes','Semana','No. ventas']


extra_df = []
for cliente in df2['Cliente'].unique():
    df2_c = df2[df2['Cliente'] == cliente]
    nombre = df2_c['Nombre'].unique()[0]
    for producto in df2_c['Producto'].unique():
        df2_cp = df2_c[df2_c['Producto'] == producto]
        promedio = mean(df2_cp['Cantidad Total'])
        for mes in df2_cp['Mes'].unique():
            df2_cpm = df2_cp[df2_cp['Mes'] == mes]
            promedio_mes = mean(df2_cpm['Cantidad Total'])
            for semana in df2_cpm['Semana'].unique():
                df2_cpms = df2_cpm[df2_cpm['Semana'] == semana]
                promedio_semana = mean(df2_cpms['Cantidad Total'])
                extra_df.append([cliente,nombre,producto,mes,promedio,promedio_mes,semana,promedio_semana])

extra_df = pd.DataFrame(extra_df)
extra_df.columns = ['Cliente','Nombre','Producto','Mes','Promedio','P. Mes','Semana','P. Semana']
df3 = pd.merge(df2, extra_df, how = 'left', left_on = ['Cliente','Nombre','Producto','Mes','Semana'], right_on = ['Cliente','Nombre','Producto','Mes','Semana'])

df3['Bimestre'] = df3['Mes'].apply(lambda x: ceil(x/2))
df3['Trimestre'] = df3['Mes'].apply(lambda x: ceil(x/3))
df3['Cuatrimestre'] = df3['Mes'].apply(lambda x: ceil(x/4))
df3['Semestre'] = df3['Mes'].apply(lambda x: ceil(x/6))
df3['Fecha Semana'] = pd.to_datetime(df3['Fecha Semana'],format = '%Y-%m-%d')


df3.to_csv('data_procesada.csv', index = False, encoding = 'latin1')

# Generación de procesados con ceros
df4 = []
for producto in df3['Producto'].unique():    
    for cliente in df3['Nombre'].unique():    
        df3_pc = df3[(df3['Producto'] == producto) & (df3['Nombre'] == cliente)]
        if not df3_pc.empty:
            semanas = weekDates(min(df3_pc['Fecha Semana']), max(df3_pc['Fecha Semana']))
            for fecha in semanas:
                codigo_cliente = df3_pc['Cliente'].values[0]
                if fecha in df3_pc["Fecha Semana"].values:                
                    cantidad = df3_pc[df3_pc['Fecha Semana'] == fecha]['Cantidad Total'].values[0]
                else:
                    cantidad = 0
                df4.append([fecha, cantidad, codigo_cliente, cliente, producto])
        
df4 = pd.DataFrame(df4)
df4.columns = ["Fecha Semana","Cantidad Total","Cliente","Nombre", "Producto"]

df4.to_csv("data_procesada2.csv", index = False, encoding = 'latin1')

fin = time.time() - inicio
print("Tiempo de ejecución: ",fin)

#Subida de datos a sheets
#df2sheets(df3, '1fbU0WsoiVhnZDbhYJwzCqA77vkVTKTotaAAyox7c8sc')