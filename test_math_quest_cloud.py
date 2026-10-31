import unittest
from unittest.mock import Mock
from math_quest_cloud import PostgresConnection,PrivateStorage,CloudApp
from math_quest_server import Handler

class CloudTests(unittest.TestCase):
    def test_write_serialization_and_parameter_binding(self):
        raw=Mock();db=PostgresConnection(raw)
        db.execute('BEGIN IMMEDIATE');self.assertIn('pg_advisory_xact_lock',raw.execute.call_args.args[0])
        db.execute('SELECT body FROM state WHERE id=?',(1,));raw.execute.assert_called_with('SELECT body FROM state WHERE id=%s',(1,))
    def test_cloud_cookie_is_secure_and_http_only(self):
        handler=object.__new__(Handler);handler.server=Mock(server_port=443,is_cloud=True);db=Mock()
        value=handler.login_cookie(db,'student','synthetic')['Set-Cookie']
        self.assertIn('Secure',value);self.assertIn('HttpOnly',value);self.assertIn('SameSite=Strict',value)
    def test_upload_rejects_oversize_before_storage_access(self):
        storage=object.__new__(PrivateStorage);storage.call=Mock()
        for size in [0,-1,True,10*1024*1024+1]:
            with self.assertRaises(ValueError):storage.prepare(Mock(),'synthetic',{'size':size,'name':'test.txt'})
        storage.call.assert_not_called()
    def test_pending_upload_cannot_be_claimed_by_another_student(self):
        storage=object.__new__(PrivateStorage);storage.call=Mock();db=Mock();db.execute.return_value.fetchone.return_value=None
        with self.assertRaises(ValueError):storage.complete(db,'other-student','file-id')
        self.assertEqual(db.execute.call_args.args[1][:2],('file-id','other-student'));storage.call.assert_not_called()
    def test_signed_urls_are_restricted_to_the_configured_project(self):
        storage=object.__new__(PrivateStorage);storage.url='https://synthetic.supabase.co'
        self.assertTrue(storage.absolute('/object/sign/test').startswith(storage.url))
        with self.assertRaises(ValueError):storage.absolute('https://unrelated.example/private')
    def test_too_many_login_attempts_are_rejected(self):
        app=object.__new__(CloudApp);db=Mock();db.execute.return_value.fetchone.return_value={'attempts':10}
        self.assertIsNone(app.allow_login(db,'/api/student/login','synthetic','127.0.0.1'))

if __name__=='__main__':unittest.main()
