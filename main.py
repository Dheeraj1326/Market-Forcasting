import streamlit as st

from datetime import date

import yfinance as yf
import numpy as np
np.float_ = np.float64

from prophet.forecaster import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objects as go

START = "2015-01-01"
TODAY = date.today().strftime('%Y-%m-%d')

st.title("Market Forcasting")

stocks = ("CIPLA.NS","SHRIRAMFIN.NS","LTIM.NS","ULTRACEMCO.NS","INDUSINDBK.NS","TCS.NS","LT.NS","TITAN.NS","NTPC.NS","TATACONSUM.NS","COALINDIA.NS","ADANIENT.NS","TATASTEEL.NS","NESTLEIND.NS","ONGC.NS","BHARTIARTL.NS","HINDALCO.NS","HDFCLIFE.NS","WIPRO.NS","MARUTI.NS","KOTAKBANK.NS","HEROMOTOCO.NS","APOLLOHOSP.NS","BAJAJ-AUTO.NS","RELIANCE.NS","ITC.NS","BRITANNIA.NS","BAJFINANCE.NS","BAJAJFINSV.NS")

selected_stocks = st.selectbox("Select DataSet For Prediction",stocks)

n_year = st.slider("Year of prediction: ",1,4)
period = n_year * 365
st.write("You Select ",period," day's of prediction")

@st.cache_data
def load_data(ticker):
    data = yf.download(ticker,start=START,end=TODAY)
    data.reset_index(inplace=True)
    return data

data_load_state = st.text("Loding data...")
data = load_data(selected_stocks)
data_load_state.text("Loding data... done!")

# print(data.columns.tolist())

st.subheader("Raw data")
st.write(data.tail())

def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='stock_open'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='stock_close'))
    fig.layout.update(title_text="Time Series Data", xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

plot_raw_data()

#Forecast Data

df_train = data[['Date', 'Close']] 

# Rename columns for Prophet
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

# Create Prophet model
m = Prophet()

# Train the model on historical data
m.fit(df_train)

# Define the forecasting period
future = m.make_future_dataframe(periods=period)

# Generate forecasts
forecast = m.predict(future)

# Display forecast data in Streamlit
st.subheader("Forecast data")
st.write(forecast.tail())

# Display forecast data graph
st.write("Forecast Data")
fig1 = plot_plotly(m,forecast)
st.plotly_chart(fig1)

# Display forecast components
st.write("Forecast Component")
fig2 = m.plot_components(forecast)
st.write(fig2)


