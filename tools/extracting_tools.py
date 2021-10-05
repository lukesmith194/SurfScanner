import config.config as config 
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


def login():
    """
    ARGS:
    RETURNS:

    
    
    """
    driver = webdriver.Chrome("./chromedriver.exe")
    driver.get("https://magicseaweed.com/account/login/?dest=%2F")
    sleep(2)
    driver.find_element_by_css_selector("#msw-js-user-login-tab > form > div:nth-child(2) > input").send_keys("lukesmith194@hotmail.com")
    driver.find_element_by_css_selector("#msw-js-user-login-tab > form > div:nth-child(3) > input").send_keys("Versus.123")
    sleep(1)
    driver.find_element_by_css_selector("#msw-js-login").click()
    sleep(2)

    return driver

driver = login()


def get_arrow_value(fila):

    """
    ARGS:
    RETURNS:

    
    
    """
    col = fila.find_element_by_class_name("text-center.msw-js-tooltip.background-gray-lighter").get_attribute("data-original-title")
    direction, angle = col.split(" - ")
    
    angle = int(angle[:-1])
    
    return direction, angle


def get_wind_value(fila):

    """
    ARGS:
    RETURNS:

    
    
    """
    try:
        col = fila.find_element_by_class_name("text-center.last.msw-js-tooltip.td-square.background-success").get_attribute("data-original-title")
    except:
        try:
            col = fila.find_element_by_class_name("text-center.last.msw-js-tooltip.td-square.background-warning").get_attribute("data-original-title")
        except:
            try:
                col = fila.find_element_by_class_name("text-center.last.msw-js-tooltip.td-square.background-danger").get_attribute("data-original-title")
            except:
                return "null", "null", np.nan
        
    
    text, angle = col.split(" - ")

    angle = int(angle[:-1])
    _, text = text.split(", ")

    text, direction = text.split()

    return text, direction, angle


    def get_hora(fila):
        """
    ARGS:
    RETURNS:

    
    
    """
        elems = fila.text.split("\n")
    elems = elems[0].split() + elems[1:]
    
    arrow = get_arrow_value(fila)
    wind = get_wind_value(fila)
    
    elems = elems + list(arrow) + list(wind)
    
    return elems


def get_dia(tabla):
    """
    ARGS:
    RETURNS:

    
    
    """
    filas = tabla.find_elements_by_tag_name("tr")
    dia = filas[0].text.split()[1]
    
    # 6am 12pm 6pm son filas 4, 6, 8
    filas = filas[3:8:2]
    
    dias = [[dia] + get_hora(f) for f in filas]
    
    return dias

def get_range_dates(d, driver, dic_spots):

    """
    ARGS:
    RETURNS:
    todo:

    
    
    """
    # d is a tuple of 2 elements (start_date, end_date)
    # access webpage
        
    driver.get(f"https://magicseaweed.com/Tauro-Surf-Report/1878/Historic/?start={d[0]}&end={d[1]}")
    sleep(2)
    # extract 31 days' data
    table = driver.find_element_by_css_selector("#msw-js-fc > div.table-responsive-xs > table")

    tablitas = table.find_elements_by_tag_name("tbody")
    tablitas = tablitas[::3]

    mega_tabla = []

    for t in tablitas:
        dia = get_dia(t)
        mega_tabla.extend(dia)
        
    return mega_tabla


def date_range_iterator(ranges,dic_spots):
    """
    ARGS:
    RETURNS:
    todo:

    
    
    """
    tabla_anio = []

    for r in ranges:
        print(f"Rango {r}...")
        driver.get(f"https://magicseaweed.com/Tauro-Surf-Report/1878/Historic/?start={r[0]}&end={r[1]}")
        
        tabla_mes = get_range_dates(r, driver)
        
        tabla_anio.extend(tabla_mes)



