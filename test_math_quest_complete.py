import copy,json,unittest
from math_quest_hideout import initialise_hideout,mini_answer,mini_payload,save_room,default_room,outfit_catalog,room_catalog
from math_quest_growth import change_grade,add_reflection
from test_math_quest_server import ServerTests

class CompleteContent(unittest.TestCase):
    def test_every_mini_can_finish_with_exactly_one_badge_and_optional_extension(self):
        st={'uuid':'a','grade':1,'studentId':'10101','classNum':'1-1','clearedStages':[],'submissions':[],'gradeRecords':{'1':{'clearedStages':[],'submissions':[]}}}
        state={'students':[st]};initialise_hideout(state)
        self.assertEqual(len(state['miniContent']),40);self.assertEqual(sum(len(m['questions']) for m in state['miniContent']),640)
        for m in state['miniContent']:
            self.assertEqual([sum(q['level']==l for q in m['questions']) for l in range(1,7)],[3,3,3,3,3,1])
            for i,q in enumerate(m['questions']):
                result=mini_answer(state,st,dict(miniId=m['id'],version=m['version'],questionId=q['id'],answer=q['answer']))
                self.assertTrue(result['correct']);self.assertEqual(result['badgeAwarded'],i==14)
            self.assertNotIn('answer',mini_payload(state,st,m['id'])['mini']['questions'][0])
        self.assertEqual(len(st['gradeRecords']['1']['miniBadges']),40)
        # Independent mathematical oracles for generated arithmetic / geometry.
        for id,expected in [('1-2',3),('1-3',12),('2-4',10),('4-2',4),('7-2',5),('8-5',12),('9-3',12),('9-4',56),('10-5',5)]:
            m=next(m for m in state['miniContent'] if m['id']==id)
            # Last basic skill, first example (n=2).
            self.assertEqual(next(q for q in m['questions'] if q['level']==5)['answer'],expected,id)

    def test_grade_undo_retains_records_and_rewards(self):
        st={'uuid':'a','grade':1,'studentId':'10101','classNum':'1-1','clearedStages':[1],'submissions':[], 'hideout':{'name':'keep'},'gradeRecords':{'1':{'clearedStages':[1],'submissions':[],'miniBadges':['1-1']}}}
        state={'students':[st]};change_grade(state,'a',1)
        st['gradeRecords']['2']['miniNote']='keep future record'
        change_grade(state,'a',-1)
        self.assertEqual((st['grade'],st['studentId']),(1,'10101'))
        self.assertEqual(st['gradeRecords']['1']['miniBadges'],['1-1'])
        self.assertEqual(st['gradeRecords']['2']['miniNote'],'keep future record')
        self.assertEqual(st['hideout'],{'name':'keep'})
        with self.assertRaises(ValueError):change_grade(state,'a',-1)

    def test_outfits_stamp_unlocks_and_free_reflection_no_rewards(self):
        st={'uuid':'a','grade':1,'gradeRecords':{'1':{'clearedStages':[],'growthStamps':[]}}};state={'students':[st],'research':{}}
        self.assertEqual(sum(o['unlocked'] for o in outfit_catalog(st)),5)
        r=default_room();r['character']['outfit']='space'
        with self.assertRaises(ValueError):save_room(st,r)
        st['gradeRecords']['1']['growthStamps']=[{'assignmentId':str(i),'kind':'growth'} for i in range(3)]
        self.assertTrue(next(i for i in room_catalog(st) if i['id']=='lamp')['unlocked'])
        r['character']['outfit']='labcoat';save_room(st,r)
        previous=copy.deepcopy(st);add_reflection(state,'a',{'grade':1,'content':'도전이 어려웠지만 다시 해 보고 싶다.'})
        self.assertEqual(st,previous)

class CompleteAPI(ServerTests):
    def test_grade_teacher_only_and_reflection_private(self):
        self.request(self.teacher,'/api/teacher/setup',{'password':'temporary-test-password'})
        self.request(self.student,'/api/student/login',{'studentId':'10101','name':'검토학생1'})
        state=self.request(self.teacher,'/api/state')[1];uuid=state['state']['students'][0]['uuid']
        self.assertEqual(self.request(self.student,'/api/teacher/grade',{'studentUuid':uuid,'direction':1,'version':state['version']})[0],403)
        status,promoted=self.request(self.teacher,'/api/teacher/grade',{'studentUuid':uuid,'direction':1,'version':state['version']})
        self.assertEqual(status,200)
        status,undone=self.request(self.teacher,'/api/teacher/grade',{'studentUuid':uuid,'direction':-1,'version':promoted['version']})
        self.assertEqual(status,200);self.assertEqual(undone['state']['students'][0]['grade'],1)
        self.assertEqual(self.request(self.student,'/api/research/reflect',{'grade':1,'content':'my private reflection'})[0],200)
        self.request(self.other,'/api/student/login',{'studentId':'10102','name':'검토학생2'})
        self.assertEqual(self.request(self.other,'/api/state')[1]['state']['research']['reflections'],[])

if __name__=='__main__':unittest.main()
