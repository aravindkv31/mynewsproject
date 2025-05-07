#CONNECTING WITH STREAMLIT AND ADDING SENTIMENATL ANALYSIS
import streamlit as st
import psycopg2
import pandas as pd
from textblob import TextBlob

def classify_sentiment(text):
    analysis = TextBlob(str(text))
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        return 'Positive'
    elif polarity < 0:
        return 'Negative'
    else:
        return 'Neutral'


DB_HOST = '####'
DB_PORT = '####'
DB_NAME = '####'
DB_USER = '####'
DB_PASSWORD = '####'

def get_data():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        query = "SELECT article_id, title, description, country, language, link, image_url FROM news_articles;"
        df = pd.read_sql_query(query, conn)
        conn.close()
        df['Sentiment'] = df['title'].apply(classify_sentiment)
        return df
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return pd.DataFrame()

def highlight_sentiment(row):
    if row['Sentiment'] == 'Positive':
        return ['background-color: green' if col == 'Sentiment' else '' for col in row.index]
    elif row['Sentiment'] == 'Negative':
        return ['background-color: red' if col == 'Sentiment' else '' for col in row.index]
    elif row['Sentiment'] == 'Neutral':
        return ['background-color: violet' if col == 'Sentiment' else '' for col in row.index]
    else:
        return ['' for _ in row.index]


st.set_page_config(page_title="News Dashboard", layout="wide")
st.title("My News Articles")

data = get_data()

if not data.empty:
    styled_data = data.style.apply(highlight_sentiment, axis=1)
    st.dataframe(styled_data, use_container_width=True)
else:
    st.warning("No data available or failed to fetch data.")
