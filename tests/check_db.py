import sqlite3, os
from app.config import get_settings
s = get_settings()
uri = s.SQLALCHEMY_DATABASE_URI
print('DB URI:', uri)
if uri.startswith('sqlite:///'):
    path = uri.replace('sqlite:///', '')
    print('DB path:', path, os.path.exists(path))
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()
    print('Tables:', tables)
    for t in ['users', 'projects', 'skills', 'allocations', 'notifications']:
        try:
            cur.execute(f"SELECT count(*) FROM {t}")
            print(t, cur.fetchone()[0])
        except Exception as e:
            print(t, 'error', e)
    conn.close()
else:
    print('Not sqlite')
