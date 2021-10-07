import streamlit as st
import datetime


def app():

    st.write("Here we will predict the mean wave height and wind speed for your next surfing holiday!")
    st.write("Insert here the dates of your next surf trip!")
    
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    start_date = st.date_input('Start date', today)
    end_date = st.date_input('End date', tomorrow)
    if start_date < end_date:
        st.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
    else:
        st.error('Error: End date must fall after start date.')