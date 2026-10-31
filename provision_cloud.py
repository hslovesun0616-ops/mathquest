"""Provision the linked, owner-confirmed project. Never print connection secrets."""
import json,secrets,subprocess,os
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def cli(args):
    result=subprocess.run(['supabase.cmd',*args,'--profile','mathquest','--output','json'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if result.returncode:raise RuntimeError('Supabase CLI operation failed; no secrets printed.')
    return json.loads(result.stdout)

if __name__=='__main__':
    ref=(ROOT/'supabase/.temp/project-ref').read_text().strip()
    owner=json.loads((ROOT/'.cloud-owner.json').read_text(encoding='utf-8'))
    if ref!=owner['supabaseProject']:raise RuntimeError('Project must match the owner-confirmed mathquest account.')
    environment=ROOT/'.env.cloud.local'
    if environment.exists():raise RuntimeError('Cloud environment already exists; do not rotate credentials automatically.')
    password=secrets.token_urlsafe(36)
    sql=(ROOT/'supabase/mathquest_schema.sql').read_text(encoding='utf-8')
    sql+=f"\nCREATE ROLE mathquest_app LOGIN PASSWORD '{password}';\nGRANT USAGE ON SCHEMA mathquest TO mathquest_app;\nGRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA mathquest TO mathquest_app;\n"
    temp=ROOT/'.cloud-bootstrap.sql'
    try:
        temp.write_text(sql,encoding='utf-8');cli(['db','query','--linked','--file',str(temp)])
    finally:
        if temp.exists():temp.unlink()
    keys=cli(['projects','api-keys','--project-ref',ref,'--reveal'])
    if isinstance(keys,dict):keys=keys.get('keys',keys.get('api_keys',[]))
    secret=next((k.get('api_key') or k.get('key') for k in keys if k.get('name')=='service_role'),None)
    if not secret:secret=next((k.get('api_key') or k.get('key') for k in keys if k.get('type')=='secret'),None)
    if not secret:raise RuntimeError('No server secret key returned; no credentials printed.')
    pooler=(ROOT/'supabase/.temp/pooler-url').read_text().strip()
    from urllib.parse import urlparse
    host=urlparse(pooler).hostname
    if not host or not host.endswith('.pooler.supabase.com'):raise RuntimeError('Unexpected pooler host')
    values={'DATABASE_URL':f'postgresql://mathquest_app.{ref}:{password}@{host}:6543/postgres','SUPABASE_URL':f'https://{ref}.supabase.co','SUPABASE_SECRET_KEY':secret}
    environment.write_text('\n'.join(f'{k}={v}' for k,v in values.items())+'\n',encoding='utf-8')
    # Storage is private, with an enforced 10MB object limit.
    os.environ.update(values)
    from math_quest_cloud import PrivateStorage,CloudApp
    storage=PrivateStorage();storage.call('POST','bucket',{'id':storage.bucket,'name':storage.bucket,'public':False,'file_size_limit':10*1024*1024})
    with CloudApp().connect() as db:db.execute('SELECT count(*) FROM state').fetchone()
    print('Owner-confirmed private schema, limited application role, pooler connection and private storage configured. Secrets stored only in ignored local environment.')
