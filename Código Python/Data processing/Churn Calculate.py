#!/C:/Users/carlo/AppData/Local/Programs/Python/Python311/python.exe
# coding: latin-1
# Churn Rate.
# Autor: Carlos Espadin Medina**

# VersiÃƒÂ³n 4.0

    #Caso de estudio: Syngenta México CP desea estimar el "Churn", cuyo significado es un término común en marketing que se refiere a la tasa de abandono o cancelación de clientes en un negocio o servicio en un período determinado.

## Librerias Necesarias:

#### Importamos la librerias necesarias:

import pandas as pd
import numpy as np
import missingno as msno
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from datetime import datetime
from qvd import qvd_reader
## Carga de Datos.
df_clientes = qvd_reader.read(r"C:\Users\carlo\Syngenta\Projects for Analysis - General\Data/CustomerSales.qvd")
print(df_clientes)
## Preprocesamiento de los datos.
#### Tratamiento de datos null y cambio de nombre a ciertas columnas.
df_clientes['Devolucion']=df_clientes['Devoluciones']
df_clientes['Devolucion']=  pd.to_numeric(df_clientes['Devolucion'], errors='coerce')
df_clientes['bp_id'] = df_clientes['bp_id'].replace(['-', ' '], np.nan)
df_clientes['LineaNegocioAbrv'] = df_clientes['LineaNegocioAbrv'].replace(['-', ' '], np.nan)
df_clientes['Fecha_Registro'] = df_clientes['Fecha de Registro'].replace(['-', ' '], np.nan)
df_clientes['Estado'] = df_clientes['Estado'].replace(['-', ' '], np.nan)
df_clientes['Fecha de Facturacion'] = df_clientes['Fecha de Facturacion'].replace(['-', ' '], None)
df_clientes['Material.Number'] = df_clientes['Material.Number'].replace([np.nan], 'Sin producto')
df_clientes
msno.matrix(df_clientes);
msno.bar(df_clientes)
### Se agrega el dato de material mas comprado por cliente
## Se agrega el dato de material mas comprado por cliente
modaMaterial = df_clientes.groupby('bp_id')['Material.Number'].apply(lambda x: x.mode().iloc[0]).reset_index()

## Se incorpora al nuevo dataframe.

df_clientes = df_clientes.merge(modaMaterial, on='bp_id', how='left') 
df_clientes.rename(columns={'Material.Number_y': 'Material.Number'}, inplace=True)
#Tratamiento de fechas de registro
# Encontrar la fecha más reciente para cada 'SoldTo'
fecha_mas_reciente = df_clientes.groupby(['bp_id'])['Fecha de Registro'].max().reset_index()
df_clientes = df_clientes.merge(fecha_mas_reciente, on='bp_id', how='left')
# df_clientes.rename(columns={'Fecha de Registro_x': 'FechaRegistro'}, inplace=True)

# df_clientes['FechaRegistro'].drop()

df_clientes['Estado'] = df_clientes.groupby('bp_id')['Estado'].transform('last')
df_clientes['Territorio'] = df_clientes.groupby('bp_id')['TERRITORY_NUM'].transform('last')


df_clientes
### Pre-EDA
df_clientes.shape
df_clientes.info()
df_clientes.columns.values
df_clientes.dtypes
#### Valores Faltantes.
msno.matrix(df_clientes);
### Agregamos el dato de material más comprado:
### Ordenamos los datos por cliente y fecha

### Encontrar la fecha mas reciente para cada 'bp_id' 
### Esto porque puede que un sold to tenga mas de una fecha de registro

fecha_mas_reciente = df_clientes.groupby(['bp_id'])['Fecha_Registro'].max().reset_index()

# Unimos la variable fecha_mas_reciente

df_clientes = df_clientes.merge(fecha_mas_reciente, on='bp_id', how='left')
df_clientes.rename(columns={'Fecha_Registro_y': 'FechaRegistro'}, inplace=True)
df_clientes = df_clientes.sort_values(['Fecha de Facturacion'])
df_clientes
# df_clientes['Fecha']
### Hacemos los siguiente para la variable Estado.

df_clientes['Estado'] = df_clientes.groupby('bp_id')['Estado'].transform('last')
df_clientes['Territorio'] = df_clientes.groupby('bp_id')['TERRITORY_NUM'].transform('last')
msno.matrix(df_clientes)
## Trasformamos el tipo datetime a Fecha de Facturacion
df_clientes['Fecha de Facturacion'] = pd.to_datetime(df_clientes['Fecha de Facturacion'])
df_clientes
df_clientes = df_clientes.sort_values(['bp_id', 'Fecha de Facturacion'])
msno.matrix(df_clientes)
## Data manipulation.

"""
Estas son algunas de las variables categoricas y númericas que estaremos Calculando:

*   Compró ese mes.
*   Media movil de compró
*   Media movil de consumo por SoldTo.
*   Media movil de volumen por SoldTo
*   Diferencia en meses entre la última compra y ahora.
*   Frecuencia de compra.
"""

# Calculamos la frecuencia de compra:
### Armamos la variable Date_Last para calcular la ultima fecha de facturacion.
Date_Last = df_clientes.groupby(['bp_id'])['Fecha de Facturacion'].max().reset_index()
df_clientes = df_clientes.merge(Date_Last, on='bp_id', how='left')
msno.matrix(df_clientes)
df_clientes.rename(columns={'Fecha de Facturacion_y': 'Date_Last'}, inplace=True)
df_clientes
## Se agrega el dato de Temporada.
df_clientes['Temporada_Temp'] = np.where(
    (
        (df_clientes['Fecha de Facturacion_x'].dt.month == 9) |
        (df_clientes['Fecha de Facturacion_x'].dt.month == 10) |
        (df_clientes['Fecha de Facturacion_x'].dt.month == 11) |
        (df_clientes['Fecha de Facturacion_x'].dt.month == 12) |
        (df_clientes['Fecha de Facturacion_x'].dt.month == 1) |
        (df_clientes['Fecha de Facturacion_x'].dt.month == 2) |
        (df_clientes['Fecha de Facturacion_x'].dt.month == 3)
    ),
    'OI',
    'PV'
)

Temporadas = df_clientes.groupby('bp_id')['Temporada_Temp'].apply(lambda x: x.mode().iloc[0]).reset_index()

df_clientes = df_clientes.merge(Temporadas, on = 'bp_id', how='left')
df_clientes.rename(columns={'Temporada_Temp_y': 'Temporada'}, inplace=True)

df_clientes
### Se agrega el dato de Organizacion de ventas
SO_Temp = df_clientes.groupby('bp_id')['SO'].apply(lambda x: x.mode().iloc[0]).reset_index()
df_clientes = df_clientes.merge(SO_Temp, on = 'bp_id', how='left')
df_clientes.rename(columns={'SO_y': 'SO'}, inplace=True)

df_clientes
msno.matrix(df_clientes)
### Se agrega el dato de Linea Negocio
### Agrupa y encuentra la moda, manejando grupos vacíos o múltiples modas
LineaNeg = df_clientes.groupby('bp_id')['LineaNegocioAbrv'].apply(lambda x: x.mode().iloc[0] if not x.mode().empty else None).reset_index()

df_clientes = df_clientes.merge(LineaNeg, on = 'bp_id', how='left')
df_clientes.rename(columns={'SO_y': 'SO'}, inplace=True)
df_clientes.rename(columns={'LineaNegocioAbrv_y': 'Linea_Negocio'}, inplace=True)
df_clientes
### Arreglamos el nombre de los ESTADOS.

df_clientes['Estado'] = np.where(df_clientes['Estado'] == 'BAJA CALIFORNIA S', 'BAJA CALIFORNIA SUR',
                                np.where(df_clientes['Estado'] == 'BAJA CALIFORNIA N', 'BAJA CALIFORNIA',
                                        df_clientes['Estado']))
df_clientes
### Casteamos tipos de datos:

print(df_clientes.columns)
df_clientes['Consumo'] = pd.to_numeric(df_clientes.Consumo, errors='coerce')
df_clientes['Volumen'] = pd.to_numeric(df_clientes.Volumen, errors='coerce')
# df_clientes['bp_id'] = df_clientes['bp_id'].astype('Int64')
# df_clientes['FechaRegistro'] = pd.to_datetime(df_clientes['FechaRegistro'],format='%Y-%m-%d', errors='coerce')
df_clientes['Fecha de Facturacion_x'] = pd.to_datetime(df_clientes['Fecha de Facturacion_x'],format='%Y-%m-%d', errors='coerce')
df_clientes
### Determinamos las ventas por cada periodo
df_clientes['Venta_2020'] = np.where(df_clientes['Fecha de Facturacion_x'].dt.year==2020,df_clientes['Consumo'], 0)
df_clientes['Venta_2021'] = np.where(df_clientes['Fecha de Facturacion_x'].dt.year==2021,df_clientes['Consumo'], 0)
df_clientes['Venta_2022'] = np.where(df_clientes['Fecha de Facturacion_x'].dt.year==2022,df_clientes['Consumo'], 0)
df_clientes['Venta_2023'] = np.where(df_clientes['Fecha de Facturacion_x'].dt.year==2023,df_clientes['Consumo'], 0)
df_clientes
### Calculamos la frecuencia de compra:
df_clientes['Frec'] = np.where(df_clientes['Consumo'] > 0, 1, 0)
df_clientes
df_clientes.dtypes
### Cambiamos las dimensiones por bp_id
new_df = df_clientes.groupby([
                                'bp_id',
                                'Estado',
                                'Territorio',
                                'Fecha de Registro_y',
                                'Material.Number',
                                'Temporada',
                                'SO',
                                'Linea_Negocio',
                                'Date_Last']).agg({
                                                    'Ship_to': 'nunique',  
                                                    'Devolucion': 'sum',
                                                    'Volumen': 'sum', 
                                                    'Consumo': 'sum', 
                                                    'Frec': 'sum',
                                                    'Venta_2020': 'sum',
                                                    'Venta_2021': 'sum',
                                                    'Venta_2022': 'sum',
                                                    'Venta_2023': 'sum'
                                }).reset_index()


print(new_df)

new_df = new_df.sort_values(['Date_Last', 'bp_id'])
new_df['Compro'] = np.where(new_df['Consumo'] > 0, 1, 0)




## Calculamos el crecimiento por periodo anual
new_df['Crecimiento_21vs20'] = np.where(new_df['Venta_2020']!=0,(new_df['Venta_2021']- new_df['Venta_2020'])/new_df['Venta_2020'], 0)
new_df['Crecimiento_22vs21'] = np.where(new_df['Venta_2021']!=0,(new_df['Venta_2022']- new_df['Venta_2021'])/new_df['Venta_2021'], 0)
new_df['Crecimiento_23vs22'] = np.where(new_df['Venta_2022']!=0,(new_df['Venta_2023']- new_df['Venta_2022'])/new_df['Venta_2022'], 0)

# Obtener la fecha del sistema
fecha_sistema = pd.Timestamp(datetime.now().date())


# Se define una funcion months_diff que toma un objeto Timedelta y devuelve la diferencia en meses como un valor entero. 
def months_diff(td):
    return td.days // 30 if td is not pd.NaT else 0

# Agrupar por bp_id y calcular la diferencia entre la ultima fecha de compra:
new_df['Tiempo_ultima_compra'] = new_df.groupby('bp_id')['Date_Last'].transform(lambda x: np.abs((fecha_sistema - x.max()).days))
print(new_df['Tiempo_ultima_compra'])
# Casteamos el tipo de dato y renombramos

new_df.rename(columns={'Fecha de Registro_y': 'FechaRegistro'}, inplace=True)

new_df['FechaRegistro'] = pd.to_datetime(new_df['FechaRegistro'],format='%Y-%m-%d', errors='coerce')

# Obtenemos el aÃƒÂ±o de registro del cliente
new_df['Anio_Registro'] = new_df['FechaRegistro'].dt.year

# Determinamos si un cliente es nuevo:
new_df['Cliente_Nuevo'] = np.where(new_df['FechaRegistro'].dt.year==fecha_sistema.year, True, False)

# Calculamos la antiguedad del cliente
new_df['Antiguedad'] = new_df.groupby('bp_id')['FechaRegistro'].transform(lambda x: (fecha_sistema - x).dt.days)

# percentiles = new_df[new_df['Frec'] >=6]
percentiles = new_df
percentiles = percentiles.groupby('bp_id').agg(percentile_75=('Tiempo_ultima_compra', lambda x: np.percentile(x, 75))).reset_index()
percentiles = percentiles.sort_values('percentile_75')
percentiles['percentile_75'] = np.percentile(new_df['Tiempo_ultima_compra'], 75)
percentile75 = np.percentile(new_df['Tiempo_ultima_compra'], 75)

print(percentile75, '\n')

# Unimos el dato de percentil al dataframe original
new_df = new_df.merge(percentiles, on='bp_id', how='left') 

# Determinamos la bandera de ciompra unica de un cliente:
new_df['Compra_unica'] = np.where(new_df['Frec'] == 1 & new_df['percentile_75'].isnull(), True, False)

new_df['Churn'] = np.where(new_df['Tiempo_ultima_compra'] > new_df['percentile_75'],True, False)


# print(new_df[new_df['Churn']==True], '\n')

if (new_df['bp_id'].duplicated().all() == True):  
    print('si hay duplicado \n')
else:
    print('No hay duplicado \n')

print(fecha_sistema, '\n')
print(new_df['Date_Last'].min(), '\n')
print('\n', len(new_df['bp_id']))
print('\n', new_df['percentile_75'])

# Eliminamos las columnas que ya no ocupamos.
new_df = new_df.drop(['percentile_75'], axis=1)

print('Cantidad de Clientes analizados: ', len(new_df))

# Escribir el DataFrame en un archivo de Excel
new_df.to_excel(r'C:\Users\carlo\Syngenta\Projects for Analysis - General\Data processing\Output\Customer_Churn.xlsx', index=False)