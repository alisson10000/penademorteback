import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não encontrado no .env")

TABLE_NAME = "questions"
ORDER_COL = "order_index"

def open_gap_at_2_only_up_to_37():
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)

    POS_INICIO = 2
    POS_FIM = 37
    OFFSET = 1000

    try:
        with engine.begin() as conn:
            # Antes: diagnóstico rápido
            before = conn.execute(text(f"""
                SELECT
                  SUM({ORDER_COL}=1) AS has1,
                  SUM({ORDER_COL}=2) AS has2,
                  MIN({ORDER_COL}) AS min_idx,
                  MAX({ORDER_COL}) AS max_idx
                FROM {TABLE_NAME}
            """)).fetchone()

            # 1) Joga 2..37 para longe (evita conflito se existir UNIQUE)
            r1 = conn.execute(
                text(f"""
                    UPDATE {TABLE_NAME}
                    SET {ORDER_COL} = {ORDER_COL} + :off
                    WHERE {ORDER_COL} BETWEEN :ini AND :fim
                """),
                {"off": OFFSET, "ini": POS_INICIO, "fim": POS_FIM},
            )

            # 2) Traz de volta como +1 (2..37 vira 3..38)
            r2 = conn.execute(
                text(f"""
                    UPDATE {TABLE_NAME}
                    SET {ORDER_COL} = {ORDER_COL} - (:off - 1)
                    WHERE {ORDER_COL} BETWEEN (:ini + :off) AND (:fim + :off)
                """),
                {"off": OFFSET, "ini": POS_INICIO, "fim": POS_FIM},
            )

            # Depois: valida se a posição 2 ficou vazia
            after = conn.execute(text(f"""
                SELECT
                  SUM({ORDER_COL}=1) AS has1,
                  SUM({ORDER_COL}=2) AS has2,
                  SUM({ORDER_COL}=38) AS has38,
                  MIN({ORDER_COL}) AS min_idx,
                  MAX({ORDER_COL}) AS max_idx
                FROM {TABLE_NAME}
            """)).fetchone()

        print("✅ Shift concluído (2..37 -> 3..38).")
        print(f"Linhas afetadas (passo 1): {r1.rowcount}")
        print(f"Linhas afetadas (passo 2): {r2.rowcount}")
        print(f"ANTES  -> has1={before[0]} has2={before[1]} min={before[2]} max={before[3]}")
        print(f"DEPOIS -> has1={after[0]} has2={after[1]} has38={after[2]} min={after[3]} max={after[4]}")
        print("🔎 O esperado é: has2=0 (posição 2 vazia) e has38=1 (antiga 37 virou 38).")

    except SQLAlchemyError as e:
        print("❌ Erro (rollback automático):", str(e))
        raise

if __name__ == "__main__":
    open_gap_at_2_only_up_to_37()