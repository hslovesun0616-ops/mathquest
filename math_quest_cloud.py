"""Vercel request adapter backed by a private Supabase PostgreSQL schema."""
from contextlib import contextmanager
from pathlib import Path
import json,os,time,secrets
from urllib.parse import quote,urlparse
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parent
class PostgresConnection:
    def __init__(self,connection):self.connection=connection
    def execute(self,sql,params=()):
        if sql.strip().upper()=='BEGIN IMMEDIATE':return self.connection.execute('SELECT pg_advisory_xact_lock(21433,1)')
        return self.connection.execute(sql.replace('?','%s'),params)

class PrivateStorage:
    def __init__(self):
        self.url=os.environ['SUPABASE_URL'].rstrip('/')
        if not self.url.startswith('https://'):raise RuntimeError('HTTPS storage URL required')
        self.key=os.environ['SUPABASE_SECRET_KEY'];self.bucket='mathquest-submissions'
    def call(self,method,path,body=None,content_type='application/json'):
        data=json.dumps(body).encode() if isinstance(body,dict) else body
        request=Request(self.url+'/storage/v1/'+path,data=data,method=method,headers={'apikey':self.key,'Authorization':'Bearer '+self.key,'Content-Type':content_type})
        with urlopen(request,timeout=30) as response:
            value=response.read()
            return json.loads(value) if value else {}
    def object_path(self,path):return quote(self.bucket,safe='')+'/'+quote(path,safe='/')
    def absolute(self,value):
        if value.startswith(self.url+'/storage/v1/'):return value
        if value.startswith('/object/'):return self.url+'/storage/v1'+value
        raise ValueError('Unexpected storage URL')
    def prepare(self,db,uuid,body):
        size=body.get('size');name=str(body.get('name','')).replace('\\','/').rsplit('/',1)[-1][:200]
        if type(size) is not int or not 0<size<=10*1024*1024 or not name:raise ValueError('첨부파일은 10MB 이하로 선택해 주세요.')
        id=secrets.token_urlsafe(24);path=uuid+'/'+id
        result=self.call('POST','object/upload/sign/'+self.object_path(path),{})
        db.execute('INSERT INTO pending_uploads(id,student_uuid,name,mime,storage_path,size,expires) VALUES(?,?,?,?,?,?,?)',(id,uuid,name,str(body.get('type') or 'application/octet-stream'),path,size,time.time()+7200))
        return {'fileId':id,'uploadUrl':self.absolute(result['url'])}
    def complete(self,db,uuid,id):
        upload=db.execute('SELECT * FROM pending_uploads WHERE id=? AND student_uuid=? AND expires>?',(id,uuid,time.time())).fetchone()
        if not upload:raise ValueError('첨부파일 연결이 만료됐습니다. 파일을 다시 선택해 주세요.')
        info=self.call('GET','object/info/'+self.object_path(upload['storage_path']))
        actual=int(info.get('metadata',{}).get('size',info.get('size',-1)))
        if actual!=upload['size'] or actual>10*1024*1024:raise ValueError('업로드가 완료되지 않았습니다. 파일을 다시 선택해 주세요.')
        db.execute('INSERT INTO files(id,student_uuid,name,mime,body,storage_path) VALUES(?,?,?,?,?,?)',(id,uuid,upload['name'],upload['mime'],b'',upload['storage_path']))
        db.execute('DELETE FROM pending_uploads WHERE id=?',(id,))
        return id,upload['name']
    def download(self,row):
        result=self.call('POST','object/sign/'+self.object_path(row['storage_path']),{'expiresIn':60})
        return self.absolute(result['signedURL'])+'&download='+quote(row['name'],safe='')

class CloudApp:
    is_cloud=True
    server_port=443
    html=ROOT/'math_quest_app.updated.html'
    def __init__(self):
        self.database=os.environ['DATABASE_URL']
        self.storage=PrivateStorage()
    def allow_login(self,db,path,student_id,address):
        import hashlib
        key=hashlib.sha256((path+'|'+student_id+'|'+address).encode()).hexdigest();now=time.time()
        db.execute('DELETE FROM auth_attempts WHERE expires<?',(now,))
        prior=db.execute('SELECT attempts FROM auth_attempts WHERE key=?',(key,)).fetchone()
        if prior and prior['attempts']>=10:return None
        db.execute('INSERT INTO auth_attempts(key,attempts,expires) VALUES(?,1,?) ON CONFLICT(key) DO UPDATE SET attempts=auth_attempts.attempts+1',(key,now+600))
        return key
    @contextmanager
    def connect(self):
        import psycopg
        from psycopg.rows import dict_row
        with psycopg.connect(self.database,sslmode='require',connect_timeout=10,prepare_threshold=None,row_factory=dict_row) as connection:
            connection.execute('SET LOCAL search_path TO mathquest,pg_catalog')
            yield PostgresConnection(connection)
