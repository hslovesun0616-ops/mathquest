import copy
import unittest
from math_quest_research import empty_research, prepare_teacher_state, score, student_research, submit_response
from test_math_quest_server import ServerTests


def instrument():
    # Synthetic test fixture, not a research instrument or validated questionnaire.
    return {'id':'test-scale-v1','title':'테스트 전용 도구','version':'test-v1','source':'자동화 테스트용 가상 문항',
            'kind':'motivation','min':1,'max':5,'options':['1','2','3','4','5'],'scoringConfirmed':True,
            'items':[{'id':'q1','text':'테스트 문항 A','dimension':'자율적 동기','reverse':False},
                     {'id':'q2','text':'테스트 문항 B','dimension':'자율적 동기','reverse':True},
                     {'id':'q3','text':'테스트 문항 C','dimension':'통제적 동기','reverse':False}]}


class ResearchTests(unittest.TestCase):
    def test_scoring_no_imputation_or_combined_score(self):
        self.assertEqual(score(instrument(),{'q1':4,'q2':2,'q3':1}),{'자율적 동기':4,'통제적 동기':1})
        for answers in ({'q1':4,'q2':2},{'q1':0,'q2':2,'q3':1},{'q1':True,'q2':2,'q3':1}):
            with self.assertRaises(ValueError):score(instrument(),answers)

    def test_wave_immutability_and_privacy(self):
        student={'uuid':'a','grade':1,'classNum':'1-1','gradeRecords':{'1':{'submissions':[]}}}
        old={'students':[student],'assignments':[],'research':empty_research()}
        new=copy.deepcopy(old);new['research']['instruments']=[instrument()]
        new['research']['participation']={'a':{'eligible':True},'b':{'eligible':True}}
        new['research']['waves']=[{'id':'w1','label':'최초 측정','date':'2026-10-30','participantIds':['a'],'instrumentIds':['test-scale-v1'],'status':'open'}]
        prepare_teacher_state(old,new)
        self.assertEqual(new['research']['waves'][0]['participantSnapshot']['a']['grade'],1)
        with self.assertRaises(ValueError):
            changed=copy.deepcopy(new);changed['research']['instruments'][0]['items'][0]['text']='변경';prepare_teacher_state(new,changed)
        bad=copy.deepcopy(old);bad['research']=copy.deepcopy(new['research']);bad['research']['participation']['a']['eligible']=False
        with self.assertRaises(ValueError):prepare_teacher_state(old,bad)
        submit_response(new,'a',{'waveId':'w1','instrumentId':'test-scale-v1','declined':True})
        self.assertEqual(new['research']['responses'][0]['scores'],{})
        with self.assertRaises(ValueError):submit_response(new,'a',{'waveId':'w1','instrumentId':'test-scale-v1','declined':True})
        new['research']['observations']=[{'studentUuid':'a','content':'교사용 관찰'}]
        self.assertEqual(student_research(new['research'],'a')['observations'],[])
        self.assertEqual(student_research(new['research'],'b')['waves'],[])


class ResearchAPI(ServerTests):
    def test_research_response_access_no_rewards_and_fixed_version(self):
        self.request(self.teacher,'/api/teacher/setup',{'password':'temporary-test-password'})
        state_response=self.request(self.teacher,'/api/state')[1]
        state=state_response['state'];uuid=state['students'][0]['uuid'];other_uuid=state['students'][1]['uuid']
        self.assertIsNone(state['students'][0]['selfEfficacy'])
        self.assertEqual(state['research']['responses'],[])
        r=state['research'];r['instruments']=[instrument()];r['participation']={uuid:{'eligible':True}}
        r['waves']=[{'id':'w1','label':'최초 측정','date':'2026-10-30','participantIds':[uuid],'instrumentIds':['test-scale-v1'],'status':'open'}]
        status,result=self.request(self.teacher,'/api/state',{'state':state,'version':state_response['version']})
        self.assertEqual(status,200);self.assertIn('participantSnapshot',result['state']['research']['waves'][0])
        self.request(self.student,'/api/student/login',{'studentId':'10101','name':'검토학생1'})
        self.request(self.other,'/api/student/login',{'studentId':'10102','name':'검토학생2'})
        before=self.request(self.student,'/api/state')[1]['state']['students'][0]
        payload={'waveId':'w1','instrumentId':'test-scale-v1','answers':{'q1':4,'q2':2,'q3':1}}
        self.assertEqual(self.request(self.other,'/api/research/respond',payload)[0],400)
        status,result=self.request(self.student,'/api/research/respond',payload)
        self.assertEqual(status,200)
        self.assertEqual(result['state']['research']['responses'][0]['scores'],{'자율적 동기':4,'통제적 동기':1})
        after=result['state']['students'][0]
        self.assertEqual(before['clearedStages'],after['clearedStages'])
        self.assertEqual(before['submissions'],after['submissions'])
        self.assertEqual(before['gradeRecords']['1'].get('growthStamps'),after['gradeRecords']['1'].get('growthStamps'))
        self.assertEqual(self.request(self.student,'/api/research/respond',payload)[0],400)
        other=self.request(self.other,'/api/state')[1]['state']['research']
        self.assertEqual(other['responses'],[]);self.assertEqual(other['waves'],[])
        current=self.request(self.teacher,'/api/state')[1]
        changed=copy.deepcopy(current['state']);changed['research']['instruments'][0]['items'][0]['text']='変更'
        self.assertEqual(self.request(self.teacher,'/api/state',{'state':changed,'version':current['version']})[0],400)


if __name__=='__main__':unittest.main()
