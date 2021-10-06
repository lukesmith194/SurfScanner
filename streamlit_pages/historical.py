import streamlit as st
from PIL import Image
from tools import support as sp

def app():
    st.write("""
    ## Historical data
    """)

    st.plotly_chart(sp.plot_map())

    st.write("""
    map explanation
    """)

    st.plotly_chart(sp.plot_line())

    st.write("""
    map explaination
    """)

