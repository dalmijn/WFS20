def execute_query(conn, query):
    cur = conn.cursor()
    try:
        cur.execute(query)
        conn.commit()
    except Exception as e:
        print(f"The error '{e}' occurred")
    cur.close()

def execute_read_query(conn, query):
    cur = conn.cursor()
    r = None
    try:
        cur.execute(query)
        r = cur.fetchall()
        return r
    except Exception as e:
        print(f"The error '{e}' occurred")
    cur.close()