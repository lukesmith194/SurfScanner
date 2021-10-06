import pandas as pd
import streamlit as st
import plotly.express as px

def import_map():
    df = pd.read_csv (r'CSV/DF_lat_long.csv')
    return df


def import_linegraph():
    df = pd.read_csv (r'CSV/DF_lat_long.csv')
    return df

def plot_map():
    data_lat_long = import_map()
    fig = px.scatter_geo(data_lat_long,
                        lat=data_lat_long.Latitude,
                        lon=data_lat_long.Longitud,
                        hover_name="Spot",
                        color = "Conditions",
                        opacity = 0.5, 
                        size = "height_ft",
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


