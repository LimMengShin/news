import sqlite3
from datetime import datetime, timedelta

def get_start_end_date():
    connection = sqlite3.connect("news.db")
    cursor = connection.cursor()

    select_query = """
    SELECT MAX(date) FROM news_articles;
    """

    cursor.execute(select_query)

    datetime_str = cursor.fetchone()[0]

    connection.commit()
    connection.close()

    start_date = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ").date()
    start_date += timedelta(days=1)
    end_date = datetime.now().date() - timedelta(days=1)
    return start_date, end_date