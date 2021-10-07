import streamlit as st
import datetime
from tools import support as sp
import pandas as pd
from pylab import rcParams
import statsmodels.api as sm
import matplotlib.pyplot as plt
from prophet import Prophet




st.write("Here we will predict the mean wave height and wind speed for your next surfing holiday!")
st.write("Insert here the dates of your next surf trip!")
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
start_date = str(st.date_input('Start date', today))
end_date = str(st.date_input('End date', tomorrow))
if start_date < end_date:
    st.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
else:
    st.error('Error: End date must fall after start date.')


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


df_wave_list = [nazare_wave,pipe_wave,fronton_wave,box_wave,pe_wave,ita_wave,pp_wave,mosca_wave,tauro_wave,mundaka_wave]
df_wind_list = [nazare_wind,pipe_wind,fronton_wind,box_wind,pe_wind,ita_wind,pp_wind,mosca_wind,tauro_wind,mundaka_wind]
spot_list = ["Nazare","Pipeline","Fronton","The Box","Puerto Escondido","Itacoatiara","Padang-Padang","Mosca Point","Tauro","Mundaka"]

df, plot1, plot2 = sp.prophet_(nazare_wave, nazare_wind, "Nazare", start_date, end_date)

st.dataframe(df)
return sp.find_empties(df_wave_list,df_wind_list,spot_list,start_date,end_date)



#st.dataframe(df)
#st.text(sp.find_empties(df_wave_list,df_wind_list,spot_list,start_date,end_date))
