"""Verify the deployed private app without changing learning or research records."""
from pathlib import Path
import hashlib,http.cookiejar,json,secrets,sqlite3,time,urllib.request,urllib.error
from migrate_to_supabase import load_cloud_environment
from math_quest_cloud import CloudApp

ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
    load_cloud_environment();cloud=CloudApp();base=json.loads((ROOT/'.cloud-deployment.json').read_text())['url']
    with sqlite3.connect(ROOT/'math_quest_data/math_quest.sqlite3') as db:local=json.loads(db.execute('SELECT body FROM state WHERE id=1').fetchone()[0])
    clients=[urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())) for _ in range(3)]
    def request(client,path,body=None,headers=None):
        req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers={'Origin':base,'Content-Type':'application/json',**(headers or {})})
        try:
            with client.open(req,timeout=60) as response:
                raw=response.read();return response.status,json.loads(raw) if response.headers.get_content_type()=='application/json' else raw,response.headers
        except urllib.error.HTTPError as error:return error.code,None,error.headers
    assert request(clients[2],'/api/state')[0]==401
    status,public,_=request(clients[2],'/api/public');assert status==200 and public['teacherConfigured'] and public['directUpload']
    users=local['students'][:2]
    for client,user in zip(clients,users):
        status,_,headers=request(client,'/api/student/login',{'studentId':user['studentId'],'name':user['name']})
        assert status==200 and 'Secure' in headers.get('Set-Cookie','')
        status,data,_=request(client,'/api/state');assert status==200 and len(data['state']['students'])==1 and data['state']['students'][0]['uuid']==user['uuid']
        assert 'miniContent' not in data['state']
    status,mini,_=request(clients[0],'/api/mini/1-1');assert status==200 and 'answer' not in mini['mini']['questions'][0]
    file_id=None;teacher_hash=None;path=None
    try:
        payload=(b'MathQuest synthetic connection check.\n'*(5*1024*1024//37+1))[:5*1024*1024]
        status,prepared,_=request(clients[0],'/api/files/prepare',{'name':'synthetic-connection-check.bin','type':'application/octet-stream','size':len(payload)})
        assert status==200;file_id=prepared['fileId'];path=users[0]['uuid']+'/'+file_id
        with urllib.request.urlopen(urllib.request.Request(prepared['uploadUrl'],method='PUT',data=payload,headers={'Content-Type':'application/octet-stream'}),timeout=60) as uploaded:assert uploaded.status in (200,201)
        with cloud.connect() as db:cloud.storage.complete(db,users[0]['uuid'],file_id)
        status,download,_=request(clients[0],'/api/files/'+file_id)
        assert status==200 and hashlib.sha256(download).digest()==hashlib.sha256(payload).digest()
        assert request(clients[1],'/api/files/'+file_id)[0]==404
        token=secrets.token_urlsafe(32);teacher_hash=hashlib.sha256(token.encode()).hexdigest()
        with cloud.connect() as db:db.execute('INSERT INTO sessions(token,role,student_uuid,expires) VALUES(?,?,?,?)',(teacher_hash,'teacher',None,time.time()+120))
        status,teacher,_=request(clients[2],'/api/state',headers={'Cookie':'mq_session_443='+token})
        assert status==200 and len(teacher['state']['students'])==len(local['students'])
        with cloud.connect() as db:
            body=db.execute('SELECT body FROM state WHERE id=1').fetchone()['body'];assert json.loads(body)==local
        print('PASS: HTTPS student and teacher sessions; private role projections; hidden answers; 5MB direct upload/download; other-student denial; learning/research records unchanged.')
    finally:
        if file_id:
            with cloud.connect() as db:
                db.execute('DELETE FROM pending_uploads WHERE id=? AND student_uuid=?',(file_id,users[0]['uuid']))
                db.execute('DELETE FROM files WHERE id=? AND student_uuid=?',(file_id,users[0]['uuid']))
            try:cloud.storage.call('DELETE','object/'+cloud.storage.bucket,{'prefixes':[path]})
            except Exception:print('Synthetic storage cleanup requires retry; no classroom attachments were touched.')
        if teacher_hash:
            with cloud.connect() as db:db.execute('DELETE FROM sessions WHERE token=?',(teacher_hash,))
        for client in clients[:2]:request(client,'/api/logout',{})
