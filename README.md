# SurfScanner

![Getting Started](images/tauro4.jpeg)

Surf and travel having always been a passion of mine, the idea for this project came about.
The purpose of this project is to predict wave and wind conditions based on historical data, received via webscrapping, through a thorough visual analysis and various ML models, such as ARMA, and FBProphet. 

## Content
- Executable Streamlit page being found in main.py with various pages and different information.
- Notebooks with full ETL including scrapping via Selenium, Visual analysis and launching of predictive models.
- CSV folder containing all the extracted data in various versions.
- Config folder contains connection to SQL database.
- Tools including extraction, cleaning and plotting functions.

## Path
- Firstly, data was extracted through webscrapping with Selenium.
- Next, the data was cleaning and made into dataframes with NumPy and Pandas.
- After the data was clean, a in depth data analysis was carried out and portrayed using Seaborn, Matplotlib and Plotly express for interactive graphical evidence.
- An ARMA model was deployed both wind conditions and wave conditions for the 10 spots i had the historical data available for.
- FbProphet was then used as it was more efficient then the Auto regressive moving average (ARMA) model.
- A streamlit platform was set up to be able to deploy the product and present it.


### Libraries
-	Pandas [Here](https://pandas.pydata.org/docs/)
-	NumPy [Here](https://numpy.org/doc/stable/user/absolute_beginners.html)
-	Selenium [Here](https://selenium-python.readthedocs.io/)
-   Streamlit [Here](https://docs.streamlit.io/en/stable/)
-   Statsmodels(ARMA) [Here](https://www.statsmodels.org/dev/examples/notebooks/generated/tsa_arma_0.html)
-   FBprophet [Here](https://facebook.github.io/prophet/docs/quick_start.html)
-   Seaborn [Here](https://seaborn.pydata.org/)
-   Matplotlib [Here](https://matplotlib.org/stable/contents.html)
-   Plotly Express [Here](https://plotly.com/python-api-reference/plotly.express.html)