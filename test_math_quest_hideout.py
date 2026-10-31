import copy
import json
import unittest
from math_quest_hideout import (initialise_hideout, mini_catalog, mini_payload, mini_answer,
    earned_badges, room_catalog, default_room, save_room, protect_student_rewards,character_catalog)
from test_math_quest_server import ServerTests


class HideoutTests(unittest.TestCase):
    def setUp(self):
        self.student={'uuid':'a','grade':1,'gradeRecords':{'1':{'clearedStages':[]}}}
        self.state={'students':[self.student]}
        initialise_hideout(self.state)

    def answer(self,q,answer=None):
        m=self.state['miniContent'][0]
        return mini_answer(self.state,self.student,{'miniId':m['id'],'version':m['version'],
            'questionId':q['id'],'answer':q['answer'] if answer is None else answer})

    def test_character_unlocks_persistence_and_old_room_compatibility(self):
        room=default_room()
        self.assertEqual(sum(h['unlocked'] for h in character_catalog(self.student)),3)
        room['character'].update(expression='happy',shirt='mint',hair='curly',skin='deep',hat='bow',cell=8)
        save_room(self.student,room)
        reloaded=json.loads(json.dumps(self.student))
        self.assertEqual(reloaded['hideout']['character'],room['character'])
        room['character']['hat']='wizard'
        with self.assertRaises(ValueError):save_room(self.student,room)
        self.student['gradeRecords']['1']['clearedStages']=[3]
        save_room(self.student,room)
        self.assertEqual(self.student['gradeRecords']['1']['clearedStages'],[3])
        room['character']['cell']=7
        with self.assertRaises(ValueError):save_room(self.student,room)
        room['character']['cell']=8
        room['character']['shirt']='unknown'
        with self.assertRaises(ValueError):save_room(self.student,room)
        old_room=default_room();old_room.pop('character')
        self.student.pop('hideout')
        old_room['cells']['5']='crystal'
        save_room(self.student,old_room)
        self.assertNotIn(str(self.student['hideout']['character']['cell']),old_room['cells'])
        self.student['grade']=2
        self.assertTrue(next(h for h in character_catalog(self.student) if h['id']=='wizard')['unlocked'])

    def test_one_badge_after_fifteen_questions_and_optional_bonus(self):
        catalog=mini_catalog(self.state)
        self.assertEqual(len(catalog),40)
        self.assertEqual({m['grade'] for m in catalog},{1})
        self.assertEqual(sum(m['ready'] for m in catalog),40)
        initial=mini_payload(self.state,self.student,'1-1')
        self.assertNotIn('answer',initial['mini']['questions'][0])
        self.assertNotIn('explanation',initial['mini']['questions'][0])
        qs=self.state['miniContent'][0]['questions']
        with self.assertRaises(ValueError):self.answer(qs[1])
        with self.assertRaises(ValueError):self.answer(qs[-1])
        wrong=self.answer(qs[0],999)
        self.assertFalse(wrong['correct'])
        for i,q in enumerate(qs[:15]):
            result=self.answer(q)
            self.assertTrue(result['correct'])
            self.assertEqual(result['badgeAwarded'],i==14)
            self.assertEqual(len(earned_badges(self.student)),int(i==14))
            loaded=json.loads(json.dumps(self.state))
            self.assertEqual(len(mini_payload(loaded,loaded['students'][0],'1-1')['progress']['solved']),i+1)
        self.assertFalse(result['progress']['bonusSolved'])
        self.assertTrue(next(i for i in room_catalog(self.student) if i['id']=='cabinet')['unlocked'])
        self.assertTrue(self.answer(qs[-1])['correct'])
        self.assertEqual(earned_badges(self.student),['mini:1:1-1'])
        self.assertFalse(self.answer(qs[-1])['badgeAwarded'])

    def test_room_validation_and_rewards_not_spent(self):
        room=default_room()
        self.assertEqual(sum(i['unlocked'] for i in room_catalog(self.student)),4)
        save_room(self.student,room)
        locked=copy.deepcopy(room);locked['cells']['0']='aquarium'
        with self.assertRaises(ValueError):save_room(self.student,locked)
        room['pins']=['big:1:1']
        with self.assertRaises(ValueError):save_room(self.student,room)
        self.student['gradeRecords']['1']['clearedStages']=[1,2]
        room['cells']['0']='aquarium';room['pins']=[None,'big:1:2','big:1:1']
        save_room(self.student,room)
        self.assertEqual(self.student['hideout']['pins'],room['pins'])
        self.assertEqual(len(earned_badges(self.student)),2)
        duplicate=copy.deepcopy(room);duplicate['cells']['1']='aquarium'
        with self.assertRaises(ValueError):save_room(self.student,duplicate)
        candidate=copy.deepcopy(self.state)
        candidate['students'][0]['hideout']['name']='교사 덮어쓰기'
        candidate['students'][0]['gradeRecords']['1']['miniBadges']=['1-1']
        protect_student_rewards(self.state,candidate)
        self.assertEqual(candidate['students'][0]['hideout'],self.student['hideout'])
        self.assertEqual(candidate['students'][0]['gradeRecords']['1']['miniBadges'],[])


class HideoutAPI(ServerTests):
    def test_room_and_mini_routes_preserve_privacy(self):
        self.assertEqual(self.request(self.student,'/api/mini/1-1')[0],401)
        self.request(self.teacher,'/api/teacher/setup',{'password':'temporary-test-password'})
        self.request(self.student,'/api/student/login',{'studentId':'10101','name':'검토학생1'})
        self.request(self.other,'/api/student/login',{'studentId':'10102','name':'검토학생2'})
        current=self.request(self.student,'/api/state')[1]
        self.assertNotIn('miniContent',current['state'])
        self.assertEqual(len(current['state']['roomCatalog']),1)
        mini=self.request(self.student,'/api/mini/1-1')[1]
        self.assertNotIn('answer',mini['mini']['questions'][0])
        room=default_room();room['name']='나만의 밝은 아지트';room['theme']='mint'
        saved=self.request(self.student,'/api/hideout',{'room':room})
        self.assertEqual(saved[0],200)
        self.assertEqual(saved[1]['state']['students'][0]['hideout']['name'],room['name'])
        self.assertNotIn('hideout',self.request(self.other,'/api/state')[1]['state']['students'][0])
        self.assertEqual(self.request(self.teacher,'/api/hideout',{'room':room})[0],403)
        self.assertEqual(self.request(self.teacher,'/api/mini/answer',{})[0],403)
        q=mini['mini']['questions'][0]
        answer=self.request(self.student,'/api/mini/answer',{'miniId':'1-1','version':mini['mini']['version'],'questionId':q['id'],'answer':2})
        self.assertEqual(answer[0],200)
        self.assertFalse(answer[1]['result']['badgeAwarded'])
        self.assertEqual(answer[1]['result']['progress']['solved'],['p1'])
        self.assertEqual(self.request(self.other,'/api/mini/1-1?student='+current['state']['students'][0]['uuid'])[1]['progress']['solved'],[])


if __name__=='__main__':unittest.main()
