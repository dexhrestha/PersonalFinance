import streamlit as st

import pandas as pd

import os


from utils.drive_functions import Drive
from api.create_connection import df

from google.oauth2 import id_token
from google.auth.transport import requests



st.title("Personal Finance Dashboard")


df['month'] = df['transactiondate'].dt.month_name()
df['year'] = df['transactiondate'].dt.year

# st.table(df.groupby(['year','month']).max('balance')['balance'])

def login():
    return Drive(token_path='credentials/g_token.pickle',cred_path='credentials/gdrive-cred.json')


if not os.path.exists('credentials/g_token.pickle'):
    st.button("Login With Google",on_click=login)


st.markdown("""
Take control of your financial journey with our powerful and intuitive personal finance dashboard. Whether you're saving for a dream vacation, planning for retirement, or simply managing day-to-day expenses, our tools are designed to empower you every step of the way.

Visualize your financial health at a glance, track spending trends, set achievable goals, and make informed decisions with confidence. Your financial future begins here—simplified, organized, and ready to achieve your aspirations.

            """)

st.markdown("## README")

st.markdown("""Your Google Drive folder strucutre should look like:  
```py
- Statements
  |--LLoyds 
  |--|--pdf
  |--|--excel
  |--|--enriched
  |--Natwest 
  |--|--pdf
  |--|--excel
  |--|--enriched
```
            """)