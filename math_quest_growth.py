"""Account grade changes and student-authored reflections; no survey rewards."""
from datetime import datetime, timezone
from uuid import uuid4
import copy

def change_grade(state,uuid,direction):
    student=next((s for s in state['students'] if s['uuid']==uuid),None)
    if student is None or type(direction) is not int or direction not in (-1,1):raise ValueError('학생과 진급 방향을 확인해 주세요.')
    old=student['grade'];target=old+direction
    if not 1<=target<=3:raise ValueError('중1부터 중3까지만 변경할 수 있습니다.')
    records=student.setdefault('gradeRecords',{})
    if direction==-1 and str(target) not in records:raise ValueError('돌아갈 이전 학년 기록이 없습니다.')
    current=records.setdefault(str(old),{})
    for key in ('studentId','classNum','clearedStages','submissions','preScore','postScore','selfEfficacy','qualitativeNotes'):
        if key in student:current[key]=copy.deepcopy(student[key])
    record=records.get(str(target)) or {'clearedStages':[],'submissions':[],'growthStamps':[],'preScore':None,'postScore':None,'selfEfficacy':None,'qualitativeNotes':''}
    id=record.get('studentId') or str(target)+str(student['studentId'])[1:]
    if any(s['uuid']!=uuid and s['studentId']==id for s in state['students']):raise ValueError('돌아갈 학번이 다른 학생과 중복됩니다.')
    class_num=record.get('classNum') or f"{target}-{student['classNum'].split('-')[-1]}"
    record.update(studentId=id,classNum=class_num);records[str(target)]=record
    student.update(grade=target,studentId=id,classNum=class_num)
    for key in ('clearedStages','submissions','preScore','postScore','selfEfficacy','qualitativeNotes'):student[key]=copy.deepcopy(record.get(key,[] if key in ('clearedStages','submissions') else None))
    event={'from':old,'to':target,'at':datetime.now(timezone.utc).isoformat(),'kind':'promote' if direction==1 else 'undo'}
    student.setdefault('gradeEvents',[]).append(event)
    student['history']=student.get('history','')+f" ➔ {'진급 취소' if direction==-1 else '진급'} 중{target}({id})"
    return event

def add_reflection(state,uuid,body):
    student=next(s for s in state['students'] if s['uuid']==uuid)
    grade=body.get('grade');content=body.get('content','')
    if type(grade) is not int or not 1<=grade<=student['grade'] or not isinstance(content,str) or not 1<=len(content.strip())<=2000:raise ValueError('선택 학년과 1~2000자의 돌아보기 내용을 확인해 주세요.')
    state['research'].setdefault('reflections',[]).append({'id':str(uuid4()),'studentUuid':uuid,'grade':grade,'content':content.strip(),'at':datetime.now(timezone.utc).isoformat()})
