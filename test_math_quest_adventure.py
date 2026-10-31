import copy
import json
import unittest
from pathlib import Path
from math_quest_adventure import initialise_adventures, payload, answer, number, prepare_adventure_state, confirm_tally
from test_math_quest_server import ServerTests


class AdventureTests(unittest.TestCase):
    def setUp(self):
        record={'clearedStages':[],'submissions':[]}
        self.state={'students':[{'uuid':'a','grade':1,'clearedStages':record['clearedStages'],'gradeRecords':{'1':record}}]}
        initialise_adventures(self.state)
        self.student={'role':'student','student_uuid':'a'}
        self.teacher={'role':'teacher','student_uuid':None}

    def test_all_hundred_questions_completion_and_resume(self):
        self.assertEqual(sum(len(g['questions']) for g in self.state['adventureContent']),100)
        with self.assertRaises(ValueError):payload(self.state,self.student,3)
        for game in self.state['adventureContent']:
            stage=game['id']
            initial=payload(self.state,self.student,stage)
            self.assertNotIn('answer',initial['game']['questions'][0])
            self.assertNotIn('explanation',initial['game']['questions'][0])
            self.assertNotIn('ending',initial['game'])
            for index,q in enumerate(game['questions']):
                body={'stageId':stage,'version':game['version'],'questionId':q['id'],'answer':q['answer']}
                if index==0:
                    wrong=answer(self.state,self.student,{**body,'answer':'999999'})
                    self.assertFalse(wrong['correct'])
                    self.assertEqual(len(wrong['progress']['solved']),0)
                    with self.assertRaises(ValueError):answer(self.state,self.student,{**body,'questionId':game['questions'][1]['id']})
                result=answer(self.state,self.student,body)
                self.assertTrue(result['correct'])
                self.assertEqual(len(result['progress']['solved']),index+1)
                self.assertEqual(result['badgeAwarded'],index==9)
                reloaded=json.loads(json.dumps(self.state))
                self.assertEqual(len(payload(reloaded,self.student,stage)['progress']['solved']),index+1)
            self.assertIn(stage,self.state['students'][0]['clearedStages'])
            self.assertTrue(result['completed'])
            self.assertIn('ending',result['game'])
            retry=answer(self.state,self.student,body)
            self.assertTrue(retry['alreadyComplete'])
        self.assertEqual(self.state['students'][0]['clearedStages'],list(range(1,11)))

    def test_numeric_validation_versions_and_preview(self):
        self.state['students'][0]['gradeRecords']['1']['clearedStages'].append(1)
        self.assertEqual(number(' −３５０.０ '),-350)
        for invalid in ['1+1','NaN','Infinity','1e2','<script>','2cm','2,000','']:
            with self.assertRaises(ValueError):number(invalid)
        preview=payload(self.state,self.teacher,10,'a')
        self.assertIn('answer',preview['game']['questions'][0])
        with self.assertRaises(ValueError):answer(self.state,self.teacher,{})
        game=next(g for g in self.state['adventureContent'] if g['id']==2)
        answer(self.state,self.student,{'stageId':2,'version':game['version'],'questionId':'2-1','answer':'-350'})
        changed=copy.deepcopy(self.state);changed['adventureContent'][1]['questions'][0]['prompt']+=' 수정'
        prepare_adventure_state(self.state,changed)
        self.assertNotEqual(changed['adventureContent'][1]['version'],game['version'])
        self.assertTrue(payload(changed,self.student,2)['contentChanged'])
        with self.assertRaises(ValueError):answer(changed,self.student,{'stageId':2,'version':game['version'],'questionId':'2-1','answer':'-350'})
        answer(changed,self.student,{'stageId':2,'version':changed['adventureContent'][1]['version'],'questionId':'2-1','answer':'-350'})
        self.assertEqual(len(changed['students'][0]['gradeRecords']['1']['adventures']['2']['history']),1)
        attempted=copy.deepcopy(self.state);attempted['students'][0]['gradeRecords']['1']['clearedStages']=[1,2,10]
        prepare_adventure_state(self.state,attempted)
        self.assertEqual(attempted['students'][0]['gradeRecords']['1']['clearedStages'],[1])

    def test_stage_one_upgrade_preserves_existing_edits_and_badges(self):
        self.state['adventureContent']=[g for g in self.state['adventureContent'] if g['id']!=1]
        self.state['adventureContent'][0]['title']='기존 교사 편집본'
        self.state['students'][0]['clearedStages'].append(1)
        initialise_adventures(self.state)
        self.assertEqual(len(self.state['adventureContent']),10)
        self.assertEqual(self.state['adventureContent'][1]['title'],'기존 교사 편집본')
        self.assertEqual(self.state['students'][0]['clearedStages'],[1])
        self.assertEqual(len(payload(self.state,self.student,1)['game']['questions']),10)


class AdventureAPI(ServerTests):
    def test_authenticated_game_play_and_editor(self):
        self.request(self.teacher,'/api/teacher/setup',{'password':'temporary-test-password'})
        self.request(self.student,'/api/student/login',{'studentId':'10102','name':'검토학생2'})
        bootstrap=self.request(self.student,'/api/state')[1]
        self.assertNotIn('adventureContent',bootstrap['state'])
        self.assertEqual(len(bootstrap['state']['adventureCatalog']),10)
        game=self.request(self.student,'/api/adventure/3')[1]['game']
        self.assertNotIn('answer',game['questions'][0])
        hidden=self.request(self.student,'/api/adventure/3?student=DEMO-STUDENT-001')[1]
        self.assertEqual(hidden['progress']['solved'],[])
        result=self.request(self.student,'/api/adventure/answer',{'stageId':3,'version':game['version'],'questionId':'3-1','answer':'-4'})
        self.assertEqual(result[0],200)
        self.assertEqual(result[1]['result']['progress']['solved'],['3-1'])
        self.assertNotIn('adventureContent',result[1]['state'])
        self.assertEqual(self.request(self.student,'/api/adventure/confirm-tally',{'studentUuid':'DEMO-STUDENT-001'})[0],400)
        self.assertEqual(self.request(self.teacher,'/api/adventure/confirm-tally',{'studentUuid':'DEMO-STUDENT-004'})[0],400)
        current=self.request(self.teacher,'/api/state')[1]
        state=current['state'];q=state['adventureContent'][0]['questions'][0];q['prompt']+=' 교사 수정'
        status,updated=self.request(self.teacher,'/api/state',{'version':current['version'],'state':state})
        self.assertEqual(status,200)
        self.assertIn('교사 수정',updated['state']['adventureContent'][0]['questions'][0]['prompt'])


if __name__=='__main__':unittest.main()
