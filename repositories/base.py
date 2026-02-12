from db import get_conn, release_conn


class BaseRepository:
    def execute(self, sql, params=None, fetchone=False, fetchall=False):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                if fetchone:
                    return cur.fetchone()
                if fetchall:
                    return cur.fetchall()
                conn.commit()
        finally:
            release_conn(conn)
