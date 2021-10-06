import streamlit as st
import pandas as pd
from PIL import Image
from multipage import MultiPage
from streamlit_pages import spot_info
from streamlit_pages import predictions
from streamlit_pages import home
from streamlit_pages import historical




app = MultiPage()

# Title of the main page
st.title("SurfScanner")

# Add all your applications (pages) here
app.add_page("Home", home.app)
app.add_page("Spot info!", spot_info.app)
app.add_page("Historical", historical.app)
app.add_page("Predictions", predictions.app)


app.run()