"""Local Math Quest server. Run: python math_quest_server.py"""
import argparse
import base64
import hashlib
import hmac
import json
import secrets
import sqlite3
import time
from contextlib import contextmanager
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, quote, parse_qs
from math_quest_adventure import initialise_adventures, catalog, prepare_adventure_state, payload as adventure_payload, answer as adventure_answer, confirm_tally
from math_quest_hideout import initialise_hideout, mini_catalog, mini_payload, mini_answer, room_catalog, save_room, protect_student_rewards, character_catalog
from math_quest_research import empty_research, prepare_teacher_state, submit_response, student_research
from math_quest_growth import change_grade, add_reflection
from math_quest_hideout import outfit_catalog

ROOT = Path(__file__).resolve().parent
MAX_FILE = 10 * 1024 * 1024


class AppServer(ThreadingHTTPServer):
    def __init__(self, address, html, data_dir, seed):
        super().__init__(address, Handler)
        self.html = Path(html)
        data_dir = Path(data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        self.database = data_dir / 'math_quest.sqlite3'
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY, body TEXT NOT NULL, version INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, role TEXT NOT NULL, student_uuid TEXT, expires REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS files (id TEXT PRIMARY KEY, student_uuid TEXT NOT NULL, name TEXT NOT NULL, mime TEXT NOT NULL, body BLOB NOT NULL);
            ''')
            db.execute('INSERT OR IGNORE INTO state VALUES (1,?,1)', (json.dumps(seed, ensure_ascii=False),))
            row = db.execute('SELECT body,version FROM state WHERE id=1').fetchone()
            state = json.loads(row['body'])
            if not state.get('affectiveResearchVersion'):
                state.setdefault('research', empty_research())
                for student in state['students']:
                    for record in student.get('gradeRecords', {}).values():
                        record['legacyAssessment'] = {k: record.get(k) for k in ('preScore', 'postScore', 'selfEfficacy')}
                        for key in ('preScore', 'postScore', 'selfEfficacy'):
                            record[key] = None
                    for key in ('preScore', 'postScore', 'selfEfficacy'):
                        student[key] = None
                state['affectiveResearchVersion'] = 1
                db.execute('UPDATE state SET body=?,version=? WHERE id=1', (json.dumps(state, ensure_ascii=False), row['version']+1))
            before_adventures=json.dumps(state.get('adventureContent'),ensure_ascii=False,sort_keys=True)
            initialise_adventures(state)
            if before_adventures!=json.dumps(state['adventureContent'],ensure_ascii=False,sort_keys=True):
                db.execute('UPDATE state SET body=?,version=version+1 WHERE id=1',(json.dumps(state,ensure_ascii=False),))
            before_minis=json.dumps(state.get('miniContent'),ensure_ascii=False,sort_keys=True)
            initialise_hideout(state)
            if before_minis!=json.dumps(state['miniContent'],ensure_ascii=False,sort_keys=True):
                db.execute('UPDATE state SET body=?,version=version+1 WHERE id=1',(json.dumps(state,ensure_ascii=False),))

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.database, timeout=15)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Do not log student identifiers or authentication requests.

    def reply(self, status, body, extra=None):
        payload = json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(payload)

    def session(self, db):
        jar = cookies.SimpleCookie()
        try:
            jar.load(self.headers.get('Cookie', ''))
            token = jar['mq_session_' + str(self.server.server_port)].value
        except (KeyError, cookies.CookieError):
            return None
        return db.execute('SELECT * FROM sessions WHERE token=? AND expires>?',
                          (hashlib.sha256(token.encode()).hexdigest(), time.time())).fetchone()

    def login_cookie(self, db, role, student_uuid=None):
        token = secrets.token_urlsafe(32)
        db.execute('DELETE FROM sessions WHERE expires<?', (time.time(),))
        db.execute('INSERT INTO sessions VALUES (?,?,?,?)',
                   (hashlib.sha256(token.encode()).hexdigest(), role, student_uuid, time.time() + 14400))
        return {'Set-Cookie': f'mq_session_{self.server.server_port}={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=14400'}

    @staticmethod
    def state(db):
        row = db.execute('SELECT body, version FROM state WHERE id=1').fetchone()
        return json.loads(row['body']), row['version']

    @staticmethod
    def write_state(db, state, version):
        db.execute('UPDATE state SET body=?,version=? WHERE id=1',
                   (json.dumps(state, ensure_ascii=False), version + 1))
        return version + 1

    @staticmethod
    def view(state, version, session):
        result = dict(state)
        result['adventureCatalog']=catalog(state)
        result['miniCatalog']=mini_catalog(state)
        if session['role'] != 'teacher':
            result.pop('adventureContent',None)
            result.pop('miniContent',None)
            result['research'] = student_research(state.get('research'), session['student_uuid'])
            result['students'] = [s for s in state['students'] if s['uuid'] == session['student_uuid']]
            # Research observations are teacher-only.
            for original in result['students']:
                original['qualitativeNotes'] = ''
                for record in original.get('gradeRecords', {}).values():
                    record['qualitativeNotes'] = ''
        result['roomCatalog']={student['uuid']:room_catalog(student) for student in result['students']}
        result['characterCatalog']={student['uuid']:character_catalog(student) for student in result['students']}
        result['outfitCatalog']={student['uuid']:outfit_catalog(student) for student in result['students']}
        return {'state': result, 'version': version, 'role': session['role']}

    def do_GET(self):
        path = urlparse(self.path).path
        with self.server.connect() as db:
            if path == '/':
                import re
                html = self.server.html.read_text(encoding='utf-8')
                # Student profiles and teacher research are served only after authentication.
                html = re.sub(r'    let students = \[\s*\n.*?\n    \];', '    let students = [];', html, count=1, flags=re.S)
                payload = html.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(payload)))
                self.send_header('Cache-Control', 'no-store')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.end_headers()
                self.wfile.write(payload)
                return
            state, version = self.state(db)
            if path == '/api/public':
                configured = bool(db.execute("SELECT 1 FROM config WHERE key='teacher'").fetchone())
                return self.reply(200, {'teacherConfigured': configured, 'copyOverrides': state.get('copyOverrides', {}), 'copyCatalog': state.get('copyCatalog', {})})
            session = self.session(db)
            if not session:
                return self.reply(401, {'error': '로그인이 필요합니다.'})
            if path == '/api/state':
                return self.reply(200, self.view(state, version, session))
            if path.startswith('/api/adventure/'):
                try:
                    stage=int(path.rsplit('/',1)[-1])
                    query=parse_qs(urlparse(self.path).query)
                    return self.reply(200,adventure_payload(state,session,stage,query.get('student',[None])[0]))
                except ValueError as error:
                    return self.reply(400,{'error':str(error)})
            if path.startswith('/api/mini/'):
                try:
                    query=parse_qs(urlparse(self.path).query)
                    uuid=session['student_uuid'] if session['role']=='student' else query.get('student',[None])[0]
                    student=next((s for s in state['students'] if s['uuid']==uuid),None)
                    if student is None:raise ValueError('학생을 찾을 수 없습니다.')
                    return self.reply(200,mini_payload(state,student,path.rsplit('/',1)[-1],session['role']=='teacher'))
                except ValueError as error:return self.reply(400,{'error':str(error)})
            if path.startswith('/api/files/'):
                row = db.execute('SELECT * FROM files WHERE id=?', (path.rsplit('/', 1)[-1],)).fetchone()
                if not row or (session['role'] != 'teacher' and row['student_uuid'] != session['student_uuid']):
                    return self.reply(404, {'error': '첨부파일을 찾을 수 없습니다.'})
                self.send_response(200)
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Disposition', "attachment; filename*=UTF-8''" + quote(row['name'], safe=''))
                self.send_header('Content-Length', str(len(row['body'])))
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                self.wfile.write(row['body'])
                return
        self.reply(404, {'error': '찾을 수 없는 주소입니다.'})

    def do_POST(self):
        # All mutations require same-origin requests. This also rejects file:// writes.
        origin = self.headers.get('Origin', '')
        if origin != 'http://' + self.headers.get('Host', ''):
            return self.reply(403, {'error': '앱을 연 주소에서 다시 시도해 주세요.'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length <= 0 or length > 16 * 1024 * 1024:
                return self.reply(413, {'error': '첨부파일은 10MB까지 제출할 수 있습니다.'})
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError()
        except (ValueError, json.JSONDecodeError):
            return self.reply(400, {'error': '요청 내용을 확인해 주세요.'})
        path = urlparse(self.path).path
        try:
            with self.server.connect() as db:
                db.execute('BEGIN IMMEDIATE')
                state, version = self.state(db)
                if path in ['/api/teacher/setup', '/api/teacher/login']:
                    existing = db.execute("SELECT value FROM config WHERE key='teacher'").fetchone()
                    password = str(body.get('password', ''))
                    if path.endswith('/setup'):
                        if existing:
                            return self.reply(409, {'error': '교사 계정이 이미 설정되어 있습니다. 로그인해 주세요.'})
                        if len(password) < 8:
                            return self.reply(400, {'error': '비밀번호는 8자 이상 입력해 주세요.'})
                        salt = secrets.token_hex(16)
                        digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
                        db.execute('INSERT INTO config VALUES (?,?)', ('teacher', json.dumps({'salt': salt, 'hash': digest})))
                    else:
                        if not existing:
                            return self.reply(400, {'error': '먼저 교사 비밀번호를 설정해 주세요.'})
                        stored = json.loads(existing['value'])
                        digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(stored['salt']), n=16384, r=8, p=1).hex()
                        if not hmac.compare_digest(digest, stored['hash']):
                            return self.reply(401, {'error': '교사 비밀번호가 일치하지 않습니다.'})
                    headers = self.login_cookie(db, 'teacher')
                    return self.reply(200, {'ok': True}, headers)
                if path == '/api/student/login':
                    student = next((s for s in state['students'] if s['studentId'] == str(body.get('studentId', '')).strip() and s['name'] == str(body.get('name', '')).strip()), None)
                    if not student:
                        return self.reply(401, {'error': '학번 또는 이름이 일치하지 않습니다.'})
                    return self.reply(200, {'ok': True}, self.login_cookie(db, 'student', student['uuid']))
                session = self.session(db)
                if not session:
                    return self.reply(401, {'error': '로그인이 필요합니다.'})
                if path == '/api/logout':
                    db.execute('DELETE FROM sessions WHERE token=?', (session['token'],))
                    return self.reply(200, {'ok': True}, {'Set-Cookie': f'mq_session_{self.server.server_port}=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0'})
                if path=='/api/teacher/grade':
                    if session['role']!='teacher':return self.reply(403,{'error':'교사만 변경할 수 있습니다.'})
                    if body.get('version')!=version:return self.reply(409,{'error':'최신 기록을 불러온 뒤 다시 시도해 주세요.'})
                    result=change_grade(state,body.get('studentUuid'),body.get('direction'))
                    version=self.write_state(db,state,version)
                    return self.reply(200,{'result':result,**self.view(state,version,session)})
                if path=='/api/research/reflect':
                    if session['role']!='student':return self.reply(403,{'error':'학생 계정에서 기록해 주세요.'})
                    add_reflection(state,session['student_uuid'],body)
                    version=self.write_state(db,state,version)
                    return self.reply(200,self.view(state,version,session))
                if path == '/api/state':
                    if session['role'] != 'teacher':
                        return self.reply(403, {'error': '교사만 수정할 수 있습니다.'})
                    if body.get('version') != version:
                        return self.reply(409, {'error': '다른 화면에서 변경된 내용이 있습니다. 새로고침 후 다시 저장해 주세요.'})
                    candidate = body.get('state')
                    if not isinstance(candidate, dict) or not isinstance(candidate.get('students'), list) or not isinstance(candidate.get('assignments'), list):
                        return self.reply(400, {'error': '저장할 내용을 확인해 주세요.'})
                    try:
                        prepare_teacher_state(state, candidate)
                        prepare_adventure_state(state,candidate)
                        protect_student_rewards(state,candidate)
                    except ValueError as error:
                        return self.reply(400, {'error': str(error)})
                    version = self.write_state(db, candidate, version)
                    return self.reply(200, self.view(candidate, version, session))
                if path == '/api/adventure/answer':
                    try:
                        result=adventure_answer(state,session,body)
                    except ValueError as error:
                        return self.reply(400,{'error':str(error)})
                    version=self.write_state(db,state,version)
                    return self.reply(200,{'result':result,**self.view(state,version,session)})
                if path in ('/api/mini/answer','/api/hideout'):
                    if session['role']!='student':return self.reply(403,{'error':'학생 계정에서 이용해 주세요.'})
                    student=next(s for s in state['students'] if s['uuid']==session['student_uuid'])
                    try:
                        if path=='/api/mini/answer':result=mini_answer(state,student,body)
                        else:save_room(student,body.get('room'));result={'saved':True}
                    except ValueError as error:return self.reply(400,{'error':str(error)})
                    version=self.write_state(db,state,version)
                    return self.reply(200,{'result':result,**self.view(state,version,session)})
                if path == '/api/adventure/confirm-tally':
                    try:
                        confirm_tally(state,session,body.get('studentUuid'))
                    except ValueError as error:
                        return self.reply(400,{'error':str(error)})
                    version=self.write_state(db,state,version)
                    return self.reply(200,self.view(state,version,session))
                if path == '/api/research/respond':
                    if session['role'] != 'student':
                        return self.reply(403, {'error': '학생 계정에서 응답해 주세요.'})
                    try:
                        submit_response(state, session['student_uuid'], body)
                    except ValueError as error:
                        return self.reply(400, {'error': str(error)})
                    version = self.write_state(db, state, version)
                    return self.reply(200, self.view(state, version, session))
                if path == '/api/submit':
                    if session['role'] != 'student':
                        return self.reply(403, {'error': '학생 계정에서 제출해 주세요.'})
                    student = next(s for s in state['students'] if s['uuid'] == session['student_uuid'])
                    task = next((t for t in state['assignments'] if t['id'] == body.get('assignmentId') and t['grade'] == student['grade']), None)
                    if not task:
                        return self.reply(400, {'error': '현재 학년의 과제만 제출할 수 있습니다.'})
                    record = student['gradeRecords'][str(student['grade'])]
                    previous = next((sub for sub in record['submissions'] if sub.get('assignmentId', 'stage-' + str(sub.get('stageId'))) == task['id']), None)
                    content = str(body.get('content', '')).strip()
                    if len(content) > 50000:
                        return self.reply(400, {'error': '과제 내용은 5만 자 이내로 입력해 주세요.'})
                    attachment = body.get('file')
                    file_id = previous.get('fileId') if previous else None
                    file_name = previous.get('fileName', '첨부 없음') if previous else '첨부 없음'
                    if attachment:
                        data = base64.b64decode(attachment.get('data', ''), validate=True)
                        if len(data) > MAX_FILE:
                            return self.reply(413, {'error': '첨부파일은 10MB까지 제출할 수 있습니다.'})
                        file_name = str(attachment.get('name', '첨부파일')).replace('\\', '/').rsplit('/', 1)[-1][:200]
                        file_id = secrets.token_urlsafe(24)
                        db.execute('INSERT INTO files VALUES (?,?,?,?,?)', (file_id, student['uuid'], file_name, str(attachment.get('type', 'application/octet-stream')), data))
                    if not content and not file_id:
                        return self.reply(400, {'error': '과제 내용이나 첨부파일을 추가해 주세요.'})
                    prev = previous or {}
                    sub = {**prev, 'assignmentId': task['id'], 'stageId': task['stageId'], 'grade': student['grade'], 'type': task.get('type', ''),
                           'content': content, 'fileId': file_id, 'fileName': file_name, 'reviewStatus': 'pending', 'reviewedAt': None,
                           'revision': prev.get('revision', 0) + 1, 'date': time.strftime('%Y-%m-%d')}
                    if previous:
                        record['submissions'][record['submissions'].index(previous)] = sub
                    else:
                        record['submissions'].append(sub)
                    student['submissions'] = record['submissions']
                    version = self.write_state(db, state, version)
                    return self.reply(200, self.view(state, version, session))
                if path == '/api/profile':
                    if session['role'] != 'student':
                        return self.reply(403, {'error': '학생 계정이 필요합니다.'})
                    student = next(s for s in state['students'] if s['uuid'] == session['student_uuid'])
                    required = {'basic': 0, 'sprout': 3, 'star': 5, 'space': 10}
                    reward = body.get('reward')
                    stamps = sum(len(r.get('growthStamps', [])) for r in student['gradeRecords'].values())
                    if reward not in required or stamps < required[reward]:
                        return self.reply(400, {'error': '아직 선택할 수 없는 꾸미기입니다.'})
                    student['profileReward'] = reward
                    version = self.write_state(db, state, version)
                    return self.reply(200, self.view(state, version, session))
        except (ValueError, KeyError, TypeError, StopIteration):
            return self.reply(400, {'error': '요청 내용을 확인해 주세요.'})
        self.reply(404, {'error': '찾을 수 없는 주소입니다.'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--html', default=str(ROOT / 'math_quest_app.updated.html'))
    parser.add_argument('--data-dir', default=str(ROOT / 'math_quest_data'))
    args = parser.parse_args()
    seed = json.loads((ROOT / 'math_quest_seed.json').read_text(encoding='utf-8'))
    server = AppServer(('127.0.0.1', args.port), args.html, args.data_dir, seed)
    print(f'Math Quest: http://127.0.0.1:{args.port}', flush=True)
    server.serve_forever()
