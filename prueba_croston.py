# -*- coding: utf-8 -*-
"""
Created on Fri Dec  9 14:52:38 2022

@author: isaac
"""

import processing as pro
import pandas as pd
import json

df = pd.read_csv('data_procesada2.csv', encoding = 'latin1')

def productosCandidatos(df,params):
    candidatos = []
    for producto in df['Producto'].unique():
        for cliente in df[df['Producto'] == producto]['Nombre'].unique():
            temp = df[(df['Producto'] == producto) & (df['Nombre'] == cliente)]
            temp_p1 = temp[(temp['Fecha Semana'] >= params['fecha_inicio_a']) & (temp['Fecha Semana'] <= params['fecha_fin_a'])]
            temp_p2 = temp[(temp['Fecha Semana'] >= params['fecha_inicio']) & (temp['Fecha Semana'] <= params['fecha_fin'])]
            b = sum(temp_p1['Cantidad Total']) > 0 and sum(temp_p2['Cantidad Total']) > 0
            candidatos.append({"producto" : [producto], "cliente" : [cliente]}) if b else candidatos
    return candidatos
        

params = {
    "fecha_inicio_a" : '2020-01-01',
    "fecha_fin_a"    : '2020-12-31',
    "fecha_inicio"   : '2021-01-01',
    "fecha_fin"      : '2021-12-21',
    "sustitucion"    : ''
    }

pc = productosCandidatos(df,params)

diferencias = []
diferencias_tsb = []
for v in pc:
    new_params = {**params, **v}
    c_result , c_summary = pro.filt(new_params, 'croston')
    ct_result , ct_summary = pro.filt(new_params, 'croston_tsb')
    c_summary = json.loads(c_summary)
    ct_summary = json.loads(ct_summary)
    temp = df[(df['Producto'].isin(new_params["producto"])) & (df['Nombre'].isin(new_params["cliente"]))]
    temp = temp[(temp['Fecha Semana'] >= params['fecha_inicio']) & (temp['Fecha Semana'] <= params['fecha_fin'])]
    minimo = min(temp['Cantidad Total'])
    maximo = max(temp['Cantidad Total'])
    valores_norm = [(v - minimo) / (maximo - minimo) for v in temp['Cantidad Total'].values]
    cantidad_real = sum(temp['Cantidad Total'])
    cantidad_real_norm = sum(valores_norm)
    cantidad_pronosticada = c_summary[0]["Total"]
    cantidad_pronosticada_tsb = ct_summary[0]["Total"]    
    if maximo != minimo:
        cantidad_pronosticada_norm = (cantidad_pronosticada - minimo) / (maximo - minimo)
        cantidad_pronosticada_norm_tsb  = (cantidad_pronosticada_tsb - minimo) / (maximo - minimo)
        dif = cantidad_real - cantidad_pronosticada
        dif_tsb = cantidad_real - cantidad_pronosticada_tsb
        dif_norm = cantidad_real_norm - cantidad_pronosticada_norm
        dif_norm_tsb = cantidad_real_norm - cantidad_pronosticada_norm_tsb
        diferencias.append([v["producto"][0], v["cliente"][0], cantidad_real, cantidad_real_norm, cantidad_pronosticada, cantidad_pronosticada_norm, dif, dif_norm])
        diferencias_tsb.append([v["producto"][0], v["cliente"][0], cantidad_real, cantidad_real_norm, cantidad_pronosticada_tsb, cantidad_pronosticada_norm_tsb, dif_tsb, dif_norm_tsb])
    
diferencias = pd.DataFrame(diferencias)
diferencias_tsb = pd.DataFrame(diferencias_tsb)

diferencias.columns = ["Producto", "Cliente", "Cantidad Real", "Cantidad Real N", "Cantidad Pronosticada", "Cantidad Pronosticada N", "Diferencia", "Diferencia Norm"]
diferencias_tsb.columns = ["Producto", "Cliente", "Cantidad Real", "Cantidad Real N", "Cantidad Pronosticada", "Cantidad Pronosticada N", "Diferencia", "Diferencia Norm"]