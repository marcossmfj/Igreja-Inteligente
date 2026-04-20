import sqlite3

db_path = 'nginx_data/database.sqlite'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Atualiza o proxy host para usar 'app' em vez de 'church_api'
    cursor.execute("UPDATE proxy_host SET forward_host = 'app' WHERE forward_host = 'church_api'")
    conn.commit()
    
    if cursor.rowcount > 0:
        print("✅ Banco de dados do Proxy atualizado com sucesso! (Destino alterado para 'app')")
    else:
        print("⚠️ Nenhuma entrada 'church_api' encontrada no banco. (Já deve estar corrigido)")
        
    conn.close()
except Exception as e:
    print(f"❌ Erro ao atualizar o banco de dados: {e}")
