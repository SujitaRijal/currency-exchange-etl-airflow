from include.load.database import get_connection

def test_postgres_connection():
    conn = get_connection()
    assert conn is not None

    cursor = conn.cursor()
    cursor.execute("SELECT 1;")
    result = cursor.fetchone()

    assert result[0] == 1

    cursor.close()
    conn.close()