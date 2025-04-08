import psycopg2
import pandas as pd
# import sqlalchemy as sa
from warnings import filterwarnings

filterwarnings("ignore", category=UserWarning, message=".*pandas only supports SQLAlchemy connectable.*")

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


def dump_data():
    excel_file = "../data/stations.csv"

    stations = pd.read_csv(excel_file)

    stations.head()

    print(stations.head())

    conn1 = get_conn()
    conn1.autocommit = True
    cur1 = conn1.cursor()


    # for index, row in stations.iterrows():
    #     print(row['name'])

    for row in stations.itertuples():
        print(getattr(row, 'name'))
        print(getattr(row, 'longname'))
        print(getattr(row, 'alpha'))
        print(getattr(row, 'code'))
        print(getattr(row, 'longcode'))
        print("--" * 5)

        name = getattr(row, 'name')
        longname = getattr(row, 'longname')
        alpha = getattr(row, 'alpha')
        code = getattr(row, 'code')
        longcode = getattr(row, 'longcode')

        try:
            insert_sql = "INSERT INTO station (name, longname, alpha, code, code_two) VALUES ('{}', '{}',  '{}', '{}', '{}' )".format(name, longname, alpha, code, longcode)

            cur1.execute(insert_sql)
            print(cur1.statusmessage)

        except Exception as e:
            print(e)


    conn1.close()

try:
    conn = get_conn()
    conn.autocommit = True
    cur = conn.cursor()

    try:
        cur.execute(search_path)

        cur.execute("DROP TABLE IF EXISTS station")

        sql = '''create table station ( 
               id serial not null primary key,
               name varchar(100) not null,
               longname varchar(255) not null, 
               alpha varchar(255) not null, 
               code varchar(3) not null, 
               code_two varchar(20) not null, 
               my_train_code varchar(50),
               anglia_code varchar(50),
               national_rail_code varchar(50) 
               )'''

        cur.execute(sql)
        print(cur.statusmessage)
        cur.close()

        dump_data()
    except psycopg2.Error as e:
        print(e)

except Exception as e:
    print(e)


