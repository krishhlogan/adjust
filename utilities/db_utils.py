import sqlite3


def make_connection():
    try:
        conn = sqlite3.connect('adjust.db')
        return conn,None
    except Exception as e:
        return None


def execute_query(query_string,columns):
    conn,error = make_connection()
    if conn is not None:
        cursor = conn.execute(query_string)
        data = []
        for row in cursor:
            temp_data = {}
            for i,column in enumerate(columns):
                temp_data[column] = row[i]
            data.append(temp_data)
        conn.close()
        return True,data
    else:
        return False,error
