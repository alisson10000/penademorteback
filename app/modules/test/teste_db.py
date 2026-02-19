from sqlalchemy import text
from app.core.database import engine

def test_connection():
    try:
        with engine.connect() as conn:

            # testa conexão básica
            result = conn.execute(text("SELECT 1"))
            print("Resultado SELECT 1:", result.fetchone()[0])

            # mostra banco atual
            result = conn.execute(text("SELECT DATABASE()"))
            print("Banco atual:", result.fetchone()[0])

            # mostra versão MySQL
            result = conn.execute(text("SELECT VERSION()"))
            print("Versão MySQL:", result.fetchone()[0])

            print("\n✅ Conexão com MySQL funcionando perfeitamente!")

    except Exception as e:
        print("\n❌ ERRO ao conectar no banco:")
        print(e)


if __name__ == "__main__":
    test_connection()
