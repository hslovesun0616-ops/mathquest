"""Server-authoritative arithmetic adventures. Answers are never sent before solving."""
import copy
import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

DIAGRAMS={'','coordinate-triangle','equal-segments','midpoints','parallel-bend','hexagon','cuboid','inscribed-triangle','isosceles','sector','cuboid-dimensions'}
def now():return datetime.now(timezone.utc).isoformat()
def number(value):
    text=unicodedata.normalize('NFKC',str(value)).strip().replace('−','-').replace('﹣','-')
    if len(text)>80 or not re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)',text):
        raise ValueError('숫자만 입력해 주세요. 음수는 - 기호를 함께 입력하세요.')
    try:
        result=Decimal(text)
        if not result.is_finite():raise ValueError('유한한 숫자를 입력해 주세요.')
        return result
    except InvalidOperation:
        raise ValueError('숫자 형식을 확인해 주세요.')

def version(game):
    raw={k:v for k,v in game.items() if k!='version'}
    return hashlib.sha256(json.dumps(raw,ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:16]

def validate_games(games):
    if not isinstance(games,list) or sorted(g.get('id') for g in games)!=list(range(1,11)):
        raise ValueError('1탄부터 10탄까지의 콘텐츠가 필요합니다.')
    for game in games:
        if any(not isinstance(game.get(key),str) or not game[key].strip() for key in ('unit','title','intro','ending','icon','theme')):
            raise ValueError('단원·제목·도입·완료 이야기를 입력해 주세요.')
        questions=game.get('questions',[])
        if len(questions)!=10 or len({q.get('id') for q in questions})!=10:
            raise ValueError('각 탄은 ID가 중복되지 않는 10개 문항으로 구성합니다.')
        for q in questions:
            if any(not isinstance(q.get(k),str) or not q[k].strip() for k in ('id','skill','title','prompt','answer','explanation','hint')):
                raise ValueError('문항의 주제·제목·문제·정답·해설·힌트를 모두 입력해 주세요.')
            number(q['answer'])
            if q.get('diagram','') not in DIAGRAMS:raise ValueError('지원되는 도형을 선택해 주세요.')
        game['version']=version(game)
    return games

def initialise_adventures(state):
    defaults=json.loads(Path(__file__).with_name('math_quest_adventures.json').read_text(encoding='utf-8'))
    if 'adventureContent' not in state:
        state['adventureContent']=defaults
    elif not any(game['id']==1 for game in state['adventureContent']):
        state['adventureContent'].append(next(game for game in defaults if game['id']==1))
        state['adventureContent'].sort(key=lambda game:game['id'])
    validate_games(state['adventureContent'])

def catalog(state):
    return [{k:game[k] for k in ('id','unit','title','icon','theme','version')}|{'questionCount':10} for game in state['adventureContent']]

def prepare_adventure_state(old,new):
    new['adventureContent']=validate_games(new.get('adventureContent',copy.deepcopy(old['adventureContent'])))
    # Game progress and adventure-earned badges can only be changed by game endpoints.
    originals={student['uuid']:student for student in old['students']}
    for student in new['students']:
        previous=originals.get(student['uuid'])
        if not previous:continue
        for grade,record in student.get('gradeRecords',{}).items():
            prior=previous.get('gradeRecords',{}).get(grade)
            if prior is None:continue
            record['adventures']=copy.deepcopy(prior.get('adventures',{}))
            record['clearedStages']=copy.deepcopy(prior.get('clearedStages',[]))
        current=student.get('gradeRecords',{}).get(str(student['grade']))
        if current is not None:student['clearedStages']=current['clearedStages']

def actor(state,session,student_uuid=None):
    uuid=session['student_uuid'] if session['role']=='student' else student_uuid
    student=next((s for s in state['students'] if s['uuid']==uuid),None)
    if student is None:raise ValueError('학생을 찾을 수 없습니다.')
    return student

def game_and_record(state,session,stage,student_uuid=None):
    student=actor(state,session,student_uuid)
    game=next((g for g in state['adventureContent'] if g['id']==stage),None)
    if not game:raise ValueError('앱 안에서 진행하는 1~10탄을 선택해 주세요.')
    record=student.get('gradeRecords',{}).get('1')
    if record is None:raise ValueError('중1 학습 기록이 없는 학생입니다.')
    if session['role']!='teacher' and stage!=1 and stage not in record['clearedStages'] and stage-1 not in record['clearedStages']:
        raise ValueError('앞 단계의 방탈출을 먼저 완료해 주세요.')
    return student,game,record

def fresh_progress(game):return {'version':game['version'],'solved':[],'attempts':{},'startedAt':now(),'completedAt':None,'history':[]}

def payload(state,session,stage,student_uuid=None):
    student,game,record=game_and_record(state,session,stage,student_uuid)
    saved=record.get('adventures',{}).get(str(stage))
    progress=copy.deepcopy(saved) if saved and saved['version']==game['version'] else fresh_progress(game)
    questions=[]
    for q in game['questions']:
        visible={k:v for k,v in q.items() if k not in ('answer','explanation')}
        if q['id'] in progress['solved'] or session['role']=='teacher':visible['explanation']=q['explanation']
        if session['role']=='teacher':visible['answer']=q['answer']
        questions.append(visible)
    return {'game':{**{k:v for k,v in game.items() if k not in ('questions','ending')},'questions':questions,
                    **({'ending':game['ending']} if len(progress['solved'])==10 or session['role']=='teacher' else {})},
            'progress':progress,'badgeEarned':stage in record['clearedStages'],'practiceOnly':student['grade']!=1,
            'contentChanged':bool(saved and saved['version']!=game['version']),'preview':session['role']=='teacher'}

def answer(state,session,body):
    if session['role']!='student':raise ValueError('학생 계정에서 도전해 주세요.')
    stage=body.get('stageId')
    if type(stage) is not int:raise ValueError('단계를 확인해 주세요.')
    student,game,record=game_and_record(state,session,stage)
    if body.get('version')!=game['version']:raise ValueError('문제가 수정되었습니다. 다시 열어 이어서 도전해 주세요.')
    adventures=record.setdefault('adventures',{})
    progress=adventures.get(str(stage))
    if not progress or progress['version']!=game['version']:
        previous=progress
        progress=fresh_progress(game)
        if previous:progress['history']=previous.get('history',[])+[{k:v for k,v in previous.items() if k!='history'}]
        adventures[str(stage)]=progress
    if body.get('action')=='restart':
        replacement=fresh_progress(game)
        replacement['history']=progress.get('history',[])+[{k:v for k,v in progress.items() if k!='history'}]
        adventures[str(stage)]=replacement
        return {'correct':False,'restarted':True,**payload(state,session,stage)}
    if len(progress['solved'])==10:return {'correct':True,'alreadyComplete':True,**payload(state,session,stage)}
    q=game['questions'][len(progress['solved'])]
    if body.get('questionId')!=q['id']:raise ValueError('앞 장치부터 순서대로 해결해 주세요.')
    response=number(body.get('answer',''))
    attempts=progress['attempts'].setdefault(q['id'],{'count':0,'lastAnswer':'','lastAttemptAt':''})
    attempts.update(count=attempts['count']+1,lastAnswer=str(response),lastAttemptAt=now())
    correct=response==number(q['answer'])
    if correct:progress['solved'].append(q['id'])
    completed=len(progress['solved'])==10
    badge_awarded=False
    if completed:
        progress['completedAt']=now()
        if student['grade']==1 and stage not in record['clearedStages']:
            record['clearedStages'].append(stage);record['clearedStages'].sort();student['clearedStages']=record['clearedStages'];badge_awarded=True
    return {'correct':correct,'completed':completed,'badgeAwarded':badge_awarded,
            **({'feedback':q['explanation']} if correct else {'feedback':'아직 장치가 열리지 않았어요. 부호와 계산 순서를 살펴보고 다시 도전해 보세요.'}),
            **payload(state,session,stage)}

def confirm_tally(state,session,student_uuid):
    raise ValueError('1탄은 앱 안에서 10개 장치를 해결하면 자동 완료됩니다.')
