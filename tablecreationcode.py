#TABLE CREATION WITHOUT SENTIMENTAL ANALYSIS
import json
import boto3
import os
import psycopg2
import pandas as pd
# from textblob import TextBlob


def lambda_handler(event, context):
    host = os.environ['DB_HOST']
    database = os.environ['DB_NAME']
    user = os.environ['DB_USER']
    password = os.environ['DB_PASS']
    port = os.environ['DB_PORT']

    bucket_name = 'mynewssbuck'
    key_key = 'articles2025-04-16 08:22:46.062464.json'
    s3 = boto3.client('s3')

    response = s3.get_object(Bucket=bucket_name, Key=key_key)
    data = json.loads(response['Body'].read())
    article = data.get("results", [])

    df = pd.DataFrame(article)

    if df.empty:
        return {'statusCode': 200, 'body': json.dumps('No articles found.')}

    df = df[['article_id', 'title', 'description', 'country', 'language', 'link', 'image_url']]
    df.dropna(inplace=True)
    # df['sentiment'] = df['description'].apply(get_sentiment_label)

    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_articles (
                article_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                country TEXT NOT NULL,
                language TEXT NOT NULL,
                link TEXT NOT NULL,
                image_url TEXT NOT NULL
            );
        """)
        conn.commit()

        for articles in article:
            try:
                article_id = articles.get("article_id")
                title = articles.get("title")
                description = articles.get("description")
                country = articles.get("country")
                language = articles.get("language")
                link = articles.get("link")
                image_url = articles.get("image_url")

                if not all([article_id, title, description, country, language, link, image_url]):
                    print(f"Skipping article with missing data: {article_id}")
                    continue  # Skip articles with missing data

                cursor.execute("""
                    INSERT INTO news_articles (
                        article_id, title, description, country, language, link, image_url
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (article_id) DO NOTHING;
                """, (article_id, title, description, country, language, link, image_url))

            except Exception as e:
                print(f"Error inserting article {article_id}: {e}")
                continue  # Skip the problematic article but continue with the rest

        conn.commit()
        cursor.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': json.dumps('Data inserted successfully')
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Database error: {str(e)}")
