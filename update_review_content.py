"""Apply reviewed stock lessons without replacing teacher edits or student records."""
import argparse
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from math_quest_hideout import upgrade_review_content

ROOT=Path(__file__).resolve().parent

def update(db,backup=None):
    db.execute('BEGIN IMMEDIATE')
    row=db.execute('SELECT body,version FROM state WHERE id=1').fetchone()
    state=json.loads(row['body'])
    changed=upgrade_review_content(state)
    if changed:
        if backup:
            backup.parent.mkdir(parents=True,exist_ok=True)
            backup.write_text(row['body'],encoding='utf-8')
        db.execute('UPDATE state SET body=?,version=version+1 WHERE id=1',
                   (json.dumps(state,ensure_ascii=False),))
    return len(changed)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--cloud',action='store_true')
    parser.add_argument('--database',type=Path,default=ROOT/'math_quest_data/math_quest.sqlite3')
    args=parser.parse_args()
    if args.cloud:
        from math_quest_cloud import CloudApp
        for line in (ROOT/'.env.cloud.local').read_text(encoding='utf-8').splitlines():
            if line and not line.startswith('#'):
                key,value=line.split('=',1);os.environ[key]=value
        backup=ROOT/'math_quest_data'/('before-review-cloud-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.json')
        with CloudApp().connect() as db:count=update(db,backup)
    else:
        if not args.database.is_file():raise SystemExit('Local database not found; specify --database.')
        # SQLite backup API also preserves transactions held in WAL files.
        backup=args.database.with_name('math_quest.before-review-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.sqlite3')
        with sqlite3.connect(args.database) as db:
            with sqlite3.connect(backup) as target:db.backup(target)
            db.row_factory=sqlite3.Row;count=update(db)
    print('Reviewed stock lessons updated:',count)
