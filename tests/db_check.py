import sys
sys.stdout.reconfigure(encoding='utf-8')
from core.database import db

print('Health:', db.health_check())
conn = db._get_conn()

tables = [t['name'] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print('Tables:', tables)

indexes = conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()
print('Indexes:', len(indexes))

for t in ['cache', 'fan_journeys', 'incidents', 'sentiment_log', 'match_events']:
    cnt = conn.execute(f"SELECT COUNT(*) as c FROM {t}").fetchone()['c']
    print(f'  {t}: {cnt} rows')

print('Journal:', conn.execute('PRAGMA journal_mode').fetchone()[0])

db.cache_set('test_key', {'hello': 'world'}, ttl=60)
val = db.cache_get('test_key')
print('Cache set/get:', 'OK' if val == {'hello': 'world'} else 'FAIL')

db.cache_flush()
val2 = db.cache_get('test_key')
print('Cache flush:', 'OK' if val2 is None else 'FAIL')

print('Queries:', db._query_count)
print('DB file size:', round(conn.execute("PRAGMA page_count").fetchone()[0] * conn.execute("PRAGMA page_size").fetchone()[0] / 1024, 1), 'KB')
