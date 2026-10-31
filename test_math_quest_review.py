import copy
import unittest
from math_quest_hideout import TOPICS, initialise_hideout, upgrade_review_content, earned_badges, default_room, save_room
from math_quest_mini_bank import authored_minis
from math_quest_adventure import version


class ReviewChanges(unittest.TestCase):
    def legacy_state(self):
        # These two lessons changed hints only; reconstruct their original stock text.
        minis=authored_minis(TOPICS)[:2]
        for mini in minis:
            for q in mini['questions']:
                if q['level']<=5:q['hint']=f"{mini['title']}의 뜻과 조건을 먼저 확인하고, 필요한 식을 한 줄씩 써 보세요."
            mini['version']=version(mini)
        return {'miniContent':minis,'students':[]}

    def test_upgrade_keeps_progress_badges_teacher_edits_and_is_idempotent(self):
        state=self.legacy_state()
        original=state['miniContent'][0]
        progress={'version':original['version'],'solved':[original['questions'][0]['id']],
                  'attempts':{original['questions'][0]['id']:2},'bonusSolved':False}
        state['students']=[{'gradeRecords':{'1':{'miniAdventures':{original['id']:progress},'miniBadges':['1-1']}}}]
        edited=state['miniContent'][1];edited['questions'][0]['hint']='교사가 직접 고친 힌트'
        before_edited=copy.deepcopy(edited)
        changed=upgrade_review_content(state)
        self.assertIn(original['id'],changed);self.assertNotIn(edited['id'],changed)
        self.assertEqual(edited,before_edited)
        self.assertEqual(progress['solved'],[original['questions'][0]['id']])
        self.assertEqual(progress['attempts'],{original['questions'][0]['id']:2})
        self.assertEqual(progress['history'][0]['version'],original['version'])
        self.assertNotEqual(progress['version'],original['version'])
        self.assertEqual(state['students'][0]['gradeRecords']['1']['miniBadges'],['1-1'])
        snapshot=copy.deepcopy(state);self.assertEqual(upgrade_review_content(state),[])
        self.assertEqual(state,snapshot)

    def test_existing_multigrade_badges_remain_displayable(self):
        student={'gradeRecords':{'1':{'clearedStages':[1]},'2':{'clearedStages':[2],'miniBadges':['1-1']},'4':{'clearedStages':[9]}}}
        self.assertEqual(earned_badges(student),['big:1:1','big:2:2','mini:2:1-1'])
        room=default_room();room['pins']=['big:2:2'];save_room(student,room)
        self.assertEqual(student['hideout']['pins'],['big:2:2'])

    def test_reviewed_content_geometry_and_equivalent_choice(self):
        library={m['id']:m for m in authored_minis(TOPICS)}
        q=next(q for q in library['9-2']['questions'] if q['id']=='9-2-4-2')
        self.assertEqual(q['type'],'choice');self.assertEqual(q['options'][q['answer']-1],'모선')
        self.assertIn('원기둥·원뿔·구',q['hint'])
        state={};initialise_hideout(state)
        self.assertEqual(sum(len(m['questions']) for m in state['miniContent']),640)

if __name__=='__main__':unittest.main()
