import time

import pandas as pd
import psycopg2
from warnings import filterwarnings
# from "../config/settings" import settings
filterwarnings("ignore", category=UserWarning, message=".*pandas only supports SQLAlchemy connectable.*")
import requests
import threading


url = "https://gql.rocketonrail.co.uk/graphql"

search_path = "Set SEARCH_PATH to 'chatbot-db', public;"

db_user = "postgres"
db_pass = "admin"
db_host = "localhost"
db_port = "5432"
db_name = "chatbot-db"

def get_conn():
    conn_str = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    connection = psycopg2.connect(conn_str)

    return connection

'''
1. import file and loop
2. for each station 
    3. insert the row in the db.
3. call api for response and get the data
4. save the data to db
5. make a query to db and save the data

'''
# search_path = "Set SEARCH_PATH to chatbot_db, public;"

# def get_conn():

excel_file = "../data/stations.csv"

stations = pd.read_csv(excel_file)

# stations.head()

# print(stations.head())

# for index, row in stations.iterrows():
#     print(row['name'])

def insert_station_code(station_code):
    # threading.Timer(5.0, insert_station_code ).start()
    print(station_code)
    # query = "query placeQuery {\n  placeQuery(query: \"{station_code}\", purpose: ORIGIN, sort: RELEVANCE, limit: 30) {\n    id\n    name\n    nlc\n    __typename\n  }\n}"
    body = {
        "operationName": "placeQuery",
        "variables": {},
        "query": "query placeQuery {\n  placeQuery(query: \"" + station_code + "\", purpose: ORIGIN, sort: RELEVANCE, limit: 30) {\n    id\n    name\n    nlc\n    __typename\n  }\n}"
    }
    response = requests.post(url, json=body, headers={"Content-Type": "application/json",
                                                      "Client-id": "893d4edd-94d5-eb11-aaaa-06a9906e23b3"})

    rrr = response.json()
    print('RESPONSE: ', response.json())
    # print(rrr.data.placeQuery[0])
    my_train_code = ''
    for key in rrr:
        print(key, rrr[key])
        for k in rrr[key]:
            print(k, rrr[key][k])
            for p in rrr[key][k]:
                print(p)
                my_train_code = p["id"]
                break

    print('MY TRAIN', station_code, my_train_code)

    try:
        conn = get_conn()
        conn.autocommit = True
        cur = conn.cursor()

        try:
            cur.execute(search_path)

            sql = "UPDATE station \
                   SET my_train_code = '{}' \
                   WHERE code = '{}'".format(my_train_code, station_code)

            cur.execute(sql)
            print(cur.statusmessage)
            cur.close()


        except psycopg2.Error as e:
            print(e)

    except Exception as e:
        print(e)


def read_file():
    for row in stations.itertuples():
        # print(getattr(row, 'name'))
        code = getattr(row, 'code')
        print("--"*5)
        time.sleep(2)
        insert_station_code(code)
        # yield name



read_file()
