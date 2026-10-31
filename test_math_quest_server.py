import base64
import copy
import http.cookiejar
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from math_quest_server import AppServer, ROOT


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        seed = json.loads((ROOT/'math_quest_seed.json').read_text(encoding='utf-8'))
        self.server = AppServer(('127.0.0.1', 0), ROOT/'math_quest_app.updated.html', self.temp.name, seed)
        self.base = 'http://127.0.0.1:' + str(self.server.server_port)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.teacher = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.student = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.other = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.temp.cleanup()

    def request(self, opener, path, data=None):
        request = urllib.request.Request(self.base+path, data=json.dumps(data).encode() if data is not None else None,
                                         headers={'Origin': self.base, 'Content-Type': 'application/json'})
        try:
            with opener.open(request) as response:
                body = response.read()
                return response.status, json.loads(body) if response.headers.get_content_type() == 'application/json' else body
        except urllib.error.HTTPError as error:
            try:
                return error.code, json.loads(error.read())
            finally:
                error.close()

    def test_accounts_files_roles_and_persistence(self):
        self.assertEqual(self.request(self.student,'/api/state')[0],401)
        public = self.request(self.student,'/')[1].decode()
        self.assertNotIn("name: '검토학생1'", public)
        self.assertNotIn('첨부 파일명 기록', public)
        # An already-empty seed must not consume subsequent functions/arrays.
        self.assertIn('function achievement(record, grade)',public)
        self.assertIn('function showGradeSelection()',public)
        self.assertEqual(self.request(self.teacher,'/api/teacher/setup',{'password':'temporary-test-password'})[0],200)
        self.assertEqual(self.request(self.other,'/api/teacher/setup',{'password':'temporary-test-password'})[0],409)
        self.assertEqual(self.request(self.student,'/api/student/login',{'studentId':'10101','name':'검토학생1'})[0],200)
        student_state = self.request(self.student,'/api/state')[1]
        self.assertEqual(len(student_state['state']['students']),1)
        self.assertEqual(student_state['state']['students'][0]['qualitativeNotes'],'')
        self.assertEqual(self.request(self.student,'/api/state',{'version':1,'state':student_state['state']})[0],403)
        data=b'Actual uploaded attachment bytes\x00\x01'
        status, uploaded=self.request(self.student,'/api/submit',{'assignmentId':'stage-1','content':'학생 풀이','file':{'name':'풀이.txt','type':'text/plain','data':base64.b64encode(data).decode()}})
        self.assertEqual(status,200)
        sub=uploaded['state']['students'][0]['submissions'][0]
        self.assertEqual(sub['reviewStatus'],'pending')
        file_id=sub['fileId']
        self.assertEqual(self.request(self.teacher,'/api/files/'+file_id)[1],data)
        self.request(self.other,'/api/student/login',{'studentId':'10102','name':'검토학생2'})
        self.assertEqual(self.request(self.other,'/api/files/'+file_id)[0],404)
        teacher_state=self.request(self.teacher,'/api/state')[1]
        outdated=copy.deepcopy(teacher_state)
        state=teacher_state['state']
        state['copyOverrides']={'나의 과제':'오늘의 수학 활동'}
        state['students'][0]['submissions'][0]['reviewStatus']='approved'
        state['students'][0]['gradeRecords']['1']['submissions'][0]['reviewStatus']='approved'
        self.assertEqual(self.request(self.teacher,'/api/state',{'version':teacher_state['version'],'state':state})[0],200)
        self.assertEqual(self.request(self.teacher,'/api/state',{'version':outdated['version'],'state':outdated['state']})[0],409)
        updated=self.request(self.student,'/api/state')[1]
        self.assertEqual(updated['state']['copyOverrides']['나의 과제'],'오늘의 수학 활동')
        self.assertEqual(updated['state']['students'][0]['submissions'][0]['reviewStatus'],'approved')
        status,resubmit=self.request(self.student,'/api/submit',{'assignmentId':'stage-1','content':'수정 풀이','file':None})
        self.assertEqual(status,200)
        sub=resubmit['state']['students'][0]['submissions'][0]
        self.assertEqual(sub['reviewStatus'],'pending')
        self.assertEqual(sub['fileId'],file_id)
        self.assertEqual(self.request(self.teacher,'/api/files/'+file_id)[1],data)
        self.assertEqual(self.request(self.student,'/api/profile',{'reward':'space'})[0],400)
        self.request(self.student,'/api/logout',{})
        self.assertEqual(self.request(self.student,'/api/files/'+file_id)[0],401)
        # The file bytes and copy changes are persisted in the database, not browser memory.
        with self.server.connect() as db:
            self.assertEqual(db.execute('SELECT body FROM files WHERE id=?',(file_id,)).fetchone()['body'],data)
        cross_origin=urllib.request.Request(self.base+'/api/student/login',data=b'{}',headers={'Origin':'http://elsewhere.invalid'})
        with self.assertRaises(urllib.error.HTTPError) as rejected:
            self.student.open(cross_origin)
        self.assertEqual(rejected.exception.code,403)
        rejected.exception.close()


if __name__=='__main__':
    unittest.main()
