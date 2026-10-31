"""Deploy only an explicit runtime allowlist. Send secrets over stdin, never argv."""
from pathlib import Path
import json,subprocess,shutil

ROOT=Path(__file__).resolve().parent
npm_root=Path(subprocess.check_output(['npm.cmd','root','-g'],text=True).strip())
CLI=['node','-r',str(ROOT/'vercel_cli_compat.cjs'),str(npm_root/'vercel/dist/vc.js')]
def run(args,cwd=ROOT,input=None):
    result=subprocess.run(CLI+args,cwd=cwd,input=input,capture_output=True,text=True,encoding='utf-8',errors='replace')
    if result.returncode:raise RuntimeError('Vercel operation failed: '+args[0]+'; '+result.stderr[-1500:] if input is None else 'Could not set a private Vercel environment variable.')
    return result

if __name__=='__main__':
    user=json.loads(run(['api','/v2/user','--raw']).stdout)['user']
    owner=json.loads((ROOT/'.cloud-owner.json').read_text(encoding='utf-8'))
    if user['email'].lower()!=owner['email'].lower():raise RuntimeError('Vercel account does not match the confirmed owner.')
    values={line.split('=',1)[0]:line.split('=',1)[1] for line in (ROOT/'.env.cloud.local').read_text(encoding='utf-8').splitlines() if line and not line.startswith('#')}
    for key,value in values.items():run(['env','add',key,'production','--sensitive','--force','--yes'],input=value)
    print('Private production environment configured; values not printed.',flush=True)
    stage=ROOT/'.vercel-build-context';stage.mkdir(exist_ok=True)
    names=['vercel.json','requirements.txt','math_quest_server.py','math_quest_cloud.py','math_quest_growth.py','math_quest_research.py','math_quest_adventure.py','math_quest_hideout.py','math_quest_mini_bank.py','math_quest_app.updated.html','math_quest_adventures.json']
    for name in names:shutil.copy2(ROOT/name,stage/name)
    (stage/'api').mkdir(exist_ok=True);shutil.copy2(ROOT/'api/index.py',stage/'api/index.py')
    (stage/'.vercel').mkdir(exist_ok=True);shutil.copy2(ROOT/'.vercel/project.json',stage/'.vercel/project.json')
    (stage/'.vercelignore').write_text('.env*\n__pycache__\n*.sqlite3\nmath_quest_data\n.git\n',encoding='utf-8')
    print('Deploy context contains runtime files only; no classroom database or local secrets.',flush=True)
    result=run(['deploy','--prod','--yes'],cwd=stage)
    url=next((line.strip() for line in reversed(result.stdout.splitlines()) if line.strip().startswith('https://')),None)
    project=json.loads((ROOT/'.vercel/project.json').read_text())
    deployments=json.loads(run(['api',f"/v6/deployments?projectId={project['projectId']}&teamId={project['orgId']}&limit=1",'--raw']).stdout)['deployments']
    detail=json.loads(run(['api',f"/v13/deployments/{deployments[0]['uid']}?teamId={project['orgId']}",'--raw']).stdout)
    aliases=detail.get('alias',[])
    if aliases:url='https://'+aliases[0]
    elif not url:url='https://'+deployments[0]['url']
    (ROOT/'.cloud-deployment.json').write_text(json.dumps({'url':url,'project':'mathquest','supabaseProject':owner['supabaseProject']},indent=2),encoding='utf-8')
    print('Vercel production deployment is READY.');print('Deployment:',url)
