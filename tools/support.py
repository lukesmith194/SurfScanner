import pandas as pd
import streamlit as st
import plotly.express as px
import pandas as pd
from pylab import rcParams
import statsmodels.api as sm
import matplotlib.pyplot as plt
from prophet import Prophet
from datetime import datetime
px.set_mapbox_access_token('pk.eyJ1IjoibHVrZXNtaXRoMTk0IiwiYSI6ImNrdWg1dGw5ejA5b3gyb296dndqenp5bGsifQ.ihBrXx2dmoBImgH9Chs47w')


def import_map():
    data_lat_long = df = pd.read_csv('/Users/lukesmith/projects/SurfScanner/csv/DF_lat_long.csv')
    return data_lat_long


def import_linegraph():
    df = pd.read_csv (r'CSV//DF_lat_long.csv')
    return df

def plot_map():
    data_lat_long = import_map()
    fig = px.scatter_mapbox(data_lat_long,
                        lat=data_lat_long.Latitude,
                        lon=data_lat_long.Longitud,
                        hover_name="Spot",
                        color = "Conditions",
                        opacity = 0.5, 
                        size = "height_ft",
                        mapbox_style = "satellite-streets",
                        zoom = 0,
                        animation_frame=data_lat_long["date"]
                        )
    fig.update_layout(height=600,margin={"r":0,"t":30,"l":0,"b":0},title="Spot conditions throughout the year")
    return fig

def plot_line():
    Full_clean_df = import_linegraph()

    fig = px.line(Full_clean_df,x="date", y="height_ft", color="Spot",title="Wave height")
    fig.update_xaxes(nticks=12)
    fig.update_yaxes(nticks=25)
    return fig

### Applies

def apply_condi_naz(string):
    if (string[3:5]) in ([10,11,3]) :
        return "Epic"
    elif (string[3:5]) in([9,12,1,2]):
        return "Good"
    elif (string[3:5]) in ([4]):
        return "Mediocre"
    else:
        return "Not recommended"

def apply_condi_pip(string):
    if (string[5:7]) in ([11,12,1,2]) :
        return "Epic"
    elif (string[5:7]) in([10,3]):
        return "Good"
    elif (string[5:7]) in ([9]):
        return "Mediocre"
    else:
        return "Not recommended"

def apply_condi_mun(string):
    if (string[5:7]) in ([12,1]) :
        return "Epic"
    elif (string[5:7]) in([10,11,2,3]):
        return "Good"
    elif (string[5:7]) in ([9]):
        return "Mediocre"
    else:
        return "Not recommended"

def apply_condi_fron(string):
    if (string[5:7]) in ([10,11,12,1]) :
        return "Epic"
    elif (string[5:7]) in([2,3]):
        return "Good"
    elif (string[5:7]) in ([9]):
        return "Mediocre"
    else:
        return "Not recommended"

def apply_condi_box(string):
    if (string[5:7]) in ([6,7,8,9]) :
        return "Epic"
    elif (string[5:7]) in([1,2,3,4,5,10,11,12]):
        return "Good"

def apply_condi_pe(string):
    if (string[5:7]) in ([4,5,6]) :
        return "Epic"
    elif (string[5:7]) in([7,8,9]):
        return "Good"
    elif (string[5:7]) in ([2,3,10]):
        return "Mediocre"
    else:
        return "Not recommended"

def apply_condi_ita(string):
    if (string[5:7]) in ([6,7]) :
        return "Epic"
    elif (string[5:7]) in([5,8,9]):
        return "Good"
    elif (string[5:7]) in ([4]):
        return "Mediocre"
    else:
        return "Not recommended"

def apply_condi_pp(string):
    if (string[5:7]) in ([6,7,8]) :
        return "Epic"
    elif (string[5:7]) in([5,10,9]):
        return "Good"
    elif (string[5:7]) in ([1,2,3,4,11,12]):
        return "Mediocre"

def apply_condi_mosca(string):
    if (string[5:7]) in ([11,12,1,2]) :
        return "Epic"
    elif (string[5:7]) in([3,9,10]):
        return "Good"
    elif (string[5:7]) in([6,7,8]):
        return "Choppy"
    else:
        return "Not recommended"

def apply_condi_tauro(string):
    if int(string[5:7]) in ([11,12,1,2]) :
        return "Epic"
    elif int(string[5:7]) in([3,9,10]):
        return "Good"
    else:
        return "Not recommended"

### CSVS

nazare_wave = pd.read_csv (r'CSV/nazare_wave.csv')
nazare_wind = pd.read_csv (r'CSV/nazare_wind.csv')
pipe_wave = pd.read_csv (r'CSV/pipe_wave.csv')
pipe_wind = pd.read_csv (r'CSV/pipe_wind.csv')
fronton_wave = pd.read_csv (r'CSV/fronton_wave.csv')
fronton_wind = pd.read_csv (r'CSV/fronton_wind.csv')
box_wave = pd.read_csv (r'CSV/box_wave.csv')
box_wind = pd.read_csv (r'CSV/box_wind.csv')
pe_wave = pd.read_csv (r'CSV/pe_wave.csv')
pe_wind = pd.read_csv (r'CSV/pe_wind.csv')
ita_wave = pd.read_csv (r'CSV/ita_wave.csv')
ita_wind = pd.read_csv (r'CSV/ita_wind.csv')
pp_wave = pd.read_csv (r'CSV/pp_wave.csv')
pp_wind = pd.read_csv (r'CSV/pp_wind.csv')
mosca_wave = pd.read_csv (r'CSV/mosca_wave.csv')
mosca_wind = pd.read_csv (r'CSV/mosca_wind.csv')
tauro_wave = pd.read_csv (r'CSV/tauro_wave.csv')
tauro_wind = pd.read_csv (r'CSV/tauro_wind.csv')
mundaka_wave = pd.read_csv (r'CSV/mundaka_wave.csv')
mundaka_wind = pd.read_csv (r'CSV/mundaka_wind.csv')

def prophet_(df_waves, df_wind, spot, start_date,end_date):
    
    #model waves
    model_waves = Prophet(daily_seasonality=True)
    model_waves.fit(df_waves)
    future_waves = model_waves.make_future_dataframe(periods=730, freq='D')
    forecast_waves = model_waves.predict(future_waves)
    forecast_waves = forecast_waves[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    fig1_waves = model_waves.plot(forecast_waves, uncertainty = True)
    forecast_waves.drop(["yhat_lower","yhat_upper"],axis= 1, inplace= True)
    forecast_waves.columns = ["date", "waves_pred"]
    
    # model wind
    model_wind = Prophet(daily_seasonality=True)
    model_wind.fit(df_wind)
    future_wind = model_wind.make_future_dataframe(periods=730, freq='D')
    forecast_wind = model_wind.predict(future_wind)
    forecast_wind = forecast_wind[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    fig1_wind = model_wind.plot(forecast_wind, uncertainty = True)
    forecast_wind.drop(["yhat_lower","yhat_upper"],axis= 1, inplace= True)
    forecast_wind.columns = ["date2", "wind_pred"]
    
    #join
    forecast = pd.concat([forecast_waves,forecast_wind],axis = 1, join =  "inner")
    forecast.drop(["date2"],axis= 1, inplace = True)
    forecast.date = forecast.date.dt.strftime('%Y/%m/%d')
    forecast.date = forecast.date.astype(str)
    forecast["Spot"] = f'{spot}'
    
    if spot == "Nazare":
        forecast["Conditions"] = forecast.date.apply(apply_condi_naz)
    elif spot == "Pipeline":
         forecast["Conditions"] = forecast.date.apply(apply_condi_pip)
    elif spot == "Fronton":
         forecast["Conditions"] = forecast.date.apply(apply_condi_fron)
    elif spot == "The Box":
         forecast["Conditions"] = forecast.date.apply(apply_condi_box)
    elif spot == "Puerto Escondido":
         forecast["Conditions"] = forecast.date.apply(apply_condi_pe)
    elif spot == "Itacoatiara":
        forecast["Conditions"] = forecast.date.apply(apply_condi_ita)
    elif spot == "Padang-Padang":
        forecast["Conditions"] = forecast.date.apply(apply_condi_pp)
    elif spot == "Mosca Point":
        forecast["Conditions"] = forecast.date.apply(apply_condi_mosca)
    elif spot == "Tauro":
        forecast["Conditions"] = forecast.date.apply(apply_condi_tauro)
    else:
        forecast["Conditions"] = forecast.date.apply(apply_condi_mun)
        
    
    forecast.date = pd.to_datetime(forecast.date)
    
    start_date = datetime.strptime(start_date,'%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    mask = (forecast["date"] > start_date) & (forecast["date"] <= end_date)
    forecast = forecast.loc[mask]
    forecast= forecast[(forecast["Conditions"] == "Good") | (forecast["Conditions"] == "Epic")]
    
    
    return forecast, fig1_waves,fig1_wind

df_wave_list = [nazare_wave,pipe_wave,fronton_wave,box_wave,pe_wave,ita_wave,pp_wave,mosca_wave,tauro_wave,mundaka_wave]
df_wind_list = [nazare_wind,pipe_wind,fronton_wind,box_wind,pe_wind,ita_wind,pp_wind,mosca_wind,tauro_wind,mundaka_wind]
spot_list = ["Nazare","Pipeline","Fronton","The Box","Puerto Escondido","Itacoatiara","Padang-Padang","Mosca Point","Tauro","Mundaka"]


def find_empties(df_wave_list,df_wind_list,spot_list,start_date,end_date):
    prueba = []
    for i,j,k in zip(df_wave_list,df_wind_list,spot_list):
        spot_num,wave_fig,wind_fig = prophet_(i,j,k,start_date,end_date)
        if spot_num.empty:
            print("empty")
        else:
            #final = pd.DataFrame(spot_num)
            prueba.append(spot_num)#,wave_fig,wind_fig])
    #finall = pd.concat(prueba)
    
    #for i in len(prueba): 
        #return prueba[i][0]
    return prueba





