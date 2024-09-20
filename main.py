import streamlit as st

from datetime import date

import yfinance as yf
import numpy as np
np.float_ = np.float64

from prophet.forecaster import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objects as go

import hashlib
import mysql.connector

# Initialize session state for the current page
if 'page' not in st.session_state:
    st.session_state.page = 'signin'

# Function to switch to sign-up page
def go_to_signup():
    st.session_state.page = 'signup'

# Function to switch to sign-in page
def go_to_signin():
    st.session_state.page = 'signin'
# Function to Switch to main page

def go_to_main():
    st.session_state.page = 'main'

# Database connection function
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",  
        user="root",  
        password="admin",
        database="marketforcasting"  
    )
    return conn

# Hash function for passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to check if a user exists
def user_exists(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to add a new user
def add_user(username, password):
    hashed_password = hash_password(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
    conn.commit()
    conn.close()

# Function to validate login
def validate_login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user






# Function to handle sign-in
def signin():
    st.write("### Sign In")

    # Input fields for username and password
    username = st.text_input("Username", key="signin_username")
    password = st.text_input("Password", type="password", key="signin_password")

    # Sign-in button
    if st.button("Sign In"):
        # Here you would add authentication logic
        if username and password :
            user = validate_login(username,password)
            if user :  # Example condition
                go_to_main()
            else:
                st.error("Invalid username or password")
        else:
            st.error("Please Enter Username or password")
    # Sign-up redirection link
    st.write("Don't have an account?")
    st.button("Sign Up", on_click=go_to_signup)

# Function to handle sign-up
def signup():
    st.write("### Sign Up")

    # Input fields for new user sign-up
    new_username = st.text_input("New Username", key="signup_username")
    new_password = st.text_input("New Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
   
    # Sign-up button
    if st.button("Sign Up"):
        if new_username and new_password:
            if new_password == confirm_password:
                # Check if user already exists
                old_user = user_exists(new_username)
                if old_user:
                    st.error("User already exists.")
                else:
                    # Add the new user
                    add_user(new_username, new_password)
                    st.success(f"Account created for {new_username}!")
                    st.info("Please sign in.")
                    
            else:
                st.error("Passwords do not match!")
    else:
        st.error("Please enter a username and password")
    st.button("Signin", on_click=go_to_signin)

# Function to handle main

def main():
    START = "2015-01-01"
    TODAY = date.today().strftime('%Y-%m-%d')

    st.title("Market Forcasting")

    stocks = ("","CIPLA.NS","SHRIRAMFIN.NS","LTIM.NS","ULTRACEMCO.NS","INDUSINDBK.NS","TCS.NS","LT.NS","TITAN.NS","NTPC.NS","TATACONSUM.NS","COALINDIA.NS","ADANIENT.NS","TATASTEEL.NS","NESTLEIND.NS","ONGC.NS","BHARTIARTL.NS","HINDALCO.NS","HDFCLIFE.NS","WIPRO.NS","MARUTI.NS","KOTAKBANK.NS","HEROMOTOCO.NS","APOLLOHOSP.NS","BAJAJ-AUTO.NS","RELIANCE.NS","ITC.NS","BRITANNIA.NS","BAJFINANCE.NS","BAJAJFINSV.NS")

    selected_stocks = st.selectbox("Select DataSet For Prediction",stocks)

    n_year = st.slider("Year of prediction: ",1,4)
    period = n_year * 365
    st.write("You Select ",period," day's of prediction")

    if(selected_stocks != ""):
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

        st.button("logout", on_click=go_to_signin)
    else:
        ""

# Display the current page based on session state
if st.session_state.page == 'signin':
    signin()
elif st.session_state.page == 'signup':
    signup()
elif st.session_state.page == 'main':
    main()




