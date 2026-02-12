import psycopg2
from psycopg2.pool import SimpleConnectionPool

POOL = SimpleConnectionPool(
    minconn=1,
    maxconn=5,
    host="localhost",
    database="idx",
    user="psql",
    password="psql",
    port=5432
)


def get_conn():
    return POOL.getconn()


def release_conn(conn):
    POOL.putconn(conn)
