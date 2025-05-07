newsapi_key = os.environ['apikey']
headers = {'X-Api-Key':newsapi_key}
newsapi_url = 'https://newsdata.io/api/1/news?apikey=pub_805640501d6ee0d1ddb14cb5df95365e57a64&q=tesla '
   
def lambda_handler(event, context):
    request= requests.get(newsapi_url, headers=headers)
    newsapi_data = request.json()
    pprint.pprint(newsapi_data)
    client = boto3.client('s3')
    filename='articles'+str(datetime.now())+'.json'
    client.put_object(Body=json.dumps(newsapi_data), Bucket='mynewssbuck', Key=filename)
    return 'success'