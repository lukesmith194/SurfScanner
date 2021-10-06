import streamlit as st
from PIL import Image


def app():
    st.write("""
    ## Top 10 spots
    """)
    st.write("""
    ### Nazaré / Praia do Norte
    """)

    imagen = Image.open("images/nazare.jpg")
    imagen2 = Image.open("images/praia.jpg")
    
    st.image(imagen, use_column_width=True)
    st.image(imagen2, use_column_width=True)
    
    st.write("Nazaré explaination")

    st.write("""
    ### Pipeline / Backdoor
    """)
    imagen3 = Image.open("images/pipe.jpg")
    
    st.image(imagen3, use_column_width=True)

    st.write("Nazaré explaination")

    st.write("""
    ### El Fronton
    """)
    imagen4 = Image.open("images/fronton.jpeg")
    st.image(imagen4, use_column_width=True)
    st.write("Nazaré explaination")

    st.write("""
    ### Puerto Escondido
    """)
    imagen5 = Image.open("images/puerto.jpg")
    st.image(imagen5, use_column_width=True)
    st.write("Nazaré explaination")

    st.write("""
    ### The Box
    """)

    imagen6 = Image.open("images/box.jpg")
    st.image(imagen6, use_column_width=True)
    st.write("Nazaré explaination")

    st.write("""
    ### Itacoatiara
    """)

    imagen7 = Image.open("images/ita.jpg")
    st.image(imagen7, use_column_width=True)
    
    st.write("Nazaré explaination")

    st.write("""
    ## Padang-Padang
    """)

    imagen8 = Image.open("images/pp.jpg")
    st.image(imagen8, use_column_width=True)

    st.write("Nazaré explaination")


    st.write("""
    ### Mosca Point
    """)
    imagen9 = Image.open("images/mosca.jpg")
    st.image(imagen9, use_column_width=True)
    st.write("Nazaré explaination")

    st.write("""
    ### Tauro
    """)

    imagen10 = Image.open("images/tauro.jpeg")
    st.image(imagen10, use_column_width=True)
    st.write("Nazaré explaination")

    st.write("""
    ### Mundaka
    """)
    imagen11 = Image.open("images/mundaka.jpg")
    st.image(imagen11, use_column_width=True)
    st.write("Nazaré explaination")
    

