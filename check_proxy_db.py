import sqlite3

db_path = 'database_container.sqlite'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM proxy_host")
    rows = cursor.fetchall()
    
    if rows:
        for row in rows:
            print(f"Proxy Host: {row}")
    else:
        print("A tabela proxy_host está vazia no SQLite!")
        
    conn.close()
except Exception as e:
    print(f"Erro: {e}")
