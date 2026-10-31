"""One-time, resumable private import. No passwords or student records are printed."""
import hashlib,json,os,sqlite3
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError
from math_quest_cloud import CloudApp

ROOT=Path(__file__).resolve().parent
def load_cloud_environment():
    for line in (ROOT/'.env.cloud.local').read_text(encoding='utf-8').splitlines():
        if line and not line.startswith('#'):
            key,value=line.split('=',1);os.environ[key]=value

if __name__=='__main__':
    load_cloud_environment();app=CloudApp()
    local=ROOT/'math_quest_data/math_quest.sqlite3'
    backup=local.with_name('math_quest.before-supabase-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.sqlite3')
    with sqlite3.connect(local) as source,sqlite3.connect(backup) as target:source.backup(target)
    with sqlite3.connect(backup) as source:
        source.row_factory=sqlite3.Row
        state=source.execute('SELECT body,version FROM state WHERE id=1').fetchone()
        configs=source.execute('SELECT * FROM config').fetchall()
        files=source.execute('SELECT * FROM files').fetchall()
    if not any(row['key']=='teacher' for row in configs):raise RuntimeError('Set up the local teacher account before deploying.')
    with app.connect() as db:
        db.execute('BEGIN IMMEDIATE')
        prior=db.execute('SELECT body,version FROM state WHERE id=1').fetchone()
        if prior and prior['body']!=state['body']:raise RuntimeError('Cloud data already exists and differs. Refusing to overwrite it.')
        for file in files:
            path=file['student_uuid']+'/'+file['id']
            try:
                info=app.storage.call('GET','object/info/'+app.storage.object_path(path))
                if int(info.get('metadata',{}).get('size',-1))!=len(file['body']):raise RuntimeError('Existing storage object does not match the source.')
            except HTTPError as error:
                if error.code not in (400,404):raise
                app.storage.call('POST','object/'+app.storage.object_path(path),file['body'],file['mime'])
            db.execute('INSERT INTO files(id,student_uuid,name,mime,body,storage_path) VALUES(?,?,?,?,?,?) ON CONFLICT (id) DO NOTHING',(file['id'],file['student_uuid'],file['name'],file['mime'],b'',path))
        for config in configs:
            current=db.execute('SELECT value FROM config WHERE key=?',(config['key'],)).fetchone()
            if current and current['value']!=config['value']:raise RuntimeError('Cloud teacher configuration differs. Refusing to overwrite it.')
            db.execute('INSERT INTO config(key,value) VALUES(?,?) ON CONFLICT (key) DO NOTHING',(config['key'],config['value']))
        db.execute('INSERT INTO state(id,body,version) VALUES(1,?,?) ON CONFLICT (id) DO NOTHING',(state['body'],state['version']))
        imported=db.execute('SELECT body FROM state WHERE id=1').fetchone()
        assert hashlib.sha256(imported['body'].encode()).digest()==hashlib.sha256(state['body'].encode()).digest()
    print('Private migration verified: classroom state, teacher configuration and attachments preserved; active local sessions not copied. Local backup retained.')
