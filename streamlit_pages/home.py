import streamlit as st
from PIL import Image


def app():
    st.write("Welcome to SurfScanner, the perfect platform for surfers to plan their next surf trip!")
    imagen = Image.open("images/tauro4.jpeg")
    st.image(imagen, use_column_width=True)
    st.write("This platform lets choose from the 10 best surfing spots worldwide depending on the conditions at the moment of your trip! Don´t miss out on the opportunity of finding the best waves!")