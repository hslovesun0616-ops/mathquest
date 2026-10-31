"""Mini-expedition badges and a personal, noncompetitive hideout."""
import copy
from math_quest_adventure import number, now, version

TOPICS=[
 ['소수와 합성수','소인수분해','최대공약수와 최소공배수'],
 ['정수와 유리수','대소 관계','덧셈','뺄셈','곱셈','나눗셈'],
 ['문자식과 식의 값','일차식과 수의 곱셈·나눗셈','일차식의 덧셈·뺄셈'],
 ['등식과 방정식','일차방정식의 풀이·활용'],
 ['순서쌍과 좌표','그래프','정비례','반비례'],
 ['점·선·면','각','위치 관계','평행선의 성질'],
 ['간단한 도형의 작도','삼각형의 작도','삼각형의 합동 조건'],
 ['다각형','삼각형의 내각·외각','다각형의 내각·외각의 합','원과 부채꼴','부채꼴의 호·넓이'],
 ['다면체','회전체','기둥·뿔의 부피','기둥·뿔의 겉넓이','구의 부피·겉넓이'],
 ['대푯값','줄기와 잎 그림','도수분포표·히스토그램','상대도수·그래프','통계적 문제해결']]

def prime_pilot():
    def q(id,level,kind,text,answer,hint,explanation,options=None):
        return dict(id=id,level=level,type=kind,text=text,answer=answer,hint=hint,explanation=explanation,options=options or [])
    questions=[
      q('p1',1,'number','7의 양의 약수는 모두 몇 개인가요?',2,'1과 자기 자신 말고도 나누어떨어지는 수가 있는지 살펴보세요.','7의 약수는 1과 7, 두 개입니다.'),
      q('p2',1,'choice','소수의 설명으로 알맞은 것은?',1,'소수의 약수 개수를 생각해 보세요.','1보다 크고 약수가 1과 자기 자신뿐인 자연수가 소수입니다.',['1보다 크고 약수가 정확히 두 개인 자연수','1을 포함한 모든 홀수','약수가 세 개 이상인 자연수']),
      q('p3',1,'number','가장 작은 소수를 입력하세요.',2,'1은 소수가 아니에요.','가장 작은 소수는 2입니다.'),
      q('p4',2,'multi','소수 카드를 모두 고르세요.',[2,3,5,7],'각 수의 약수를 확인해 보세요.','2, 3, 5, 7이 소수입니다. 1은 소수도 합성수도 아니에요.',['1','2','3','4','5','6','7','9']),
      q('p5',2,'choice','9는 어떤 수인가요?',2,'9=3×3으로 나타낼 수 있어요.','9의 약수는 1, 3, 9이므로 합성수입니다.',['소수','합성수','소수도 합성수도 아님']),
      q('p6',2,'number','4, 6, 7, 11, 15 중 합성수는 몇 개인가요?',3,'1과 자기 자신 외에 다른 약수가 있는 수를 세어요.','4, 6, 15가 합성수이므로 3개입니다.'),
      q('p7',3,'choice','“짝수는 모두 합성수다.” 이 설명은 맞을까요?',2,'가장 작은 소수를 떠올려 보세요.','2는 짝수이면서 소수이므로 틀린 설명입니다.',['맞다','틀리다']),
      q('p8',3,'choice','1에 대한 설명으로 알맞은 것은?',3,'소수는 약수가 두 개, 합성수는 약수가 세 개 이상이어야 해요.','1의 약수는 1 하나뿐입니다. 소수도 합성수도 아닙니다.',['소수이다','합성수이다','소수도 합성수도 아니다']),
      q('p9',3,'choice','“홀수 9는 소수다.”의 잘못을 찾은 설명은?',1,'홀수인지와 약수가 몇 개인지는 다른 기준이에요.','9는 3으로도 나누어떨어지므로 소수가 아닙니다.',['9는 3을 약수로 가진다','홀수는 모두 소수가 아니다','9는 1로 나누어지지 않는다']),
      q('p10',4,'choice','15가 합성수임을 설명하는 식은?',2,'1이 아닌 두 자연수의 곱을 찾아요.','15=3×5이므로 1과 15 외에 3과 5도 약수로 가집니다.',['15=1×15','15=3×5','15=10+5']),
      q('p11',4,'number','“21의 약수는 1과 21뿐이다.”라는 설명에 빠진 약수 중 작은 수를 입력하세요.',3,'21=3×7이에요.','빠진 약수는 3과 7입니다. 그중 작은 수는 3입니다.'),
      q('p12',4,'choice','두 수가 모두 소수인 짝을 고르세요.',2,'나누어떨어지는 작은 수가 있는지 확인해요.','11과 13은 약수가 각각 두 개이므로 모두 소수입니다.',['9와 11','11과 13','13과 15']),
      q('p13',5,'number','10보다 크고 20보다 작은 소수는 모두 몇 개인가요?',4,'11부터 19까지 2, 3, 5 등으로 나누어지는지 살펴보세요.','11, 13, 17, 19의 네 개입니다.'),
      q('p14',5,'number','서로 다른 세 소수 2, 3, 5를 모두 더하면 얼마인가요?',10,'소수의 뜻을 확인하면서 천천히 더해 보세요.','2+3+5=10입니다.'),
      q('p15',5,'number','가장 작은 합성수를 입력하세요.',4,'2와 3은 소수예요. 그다음 자연수를 확인해 보세요.','4의 약수는 1, 2, 4입니다. 가장 작은 합성수는 4입니다.'),
      q('bonus',6,'number','선택 도전: 2 이상 20 이하인 자연수 n 중 n과 n+2가 모두 소수가 되는 n은 몇 개인가요?',4,'(3,5), (5,7)처럼 차이가 2인 소수의 짝을 찾아보세요.','n=3, 5, 11, 17이면 됩니다. (3,5), (5,7), (11,13), (17,19)이므로 4개입니다.')]
    # Choice and multi-select answers both use 1-based option indices.
    return dict(id='1-1',unit=1,title='소수와 합성수',story='수학 생태공원의 분류 연구소',intro='연구소의 숫자 카드가 뒤섞였어요. 관찰하고 분류하고 잘못된 설명을 고쳐 5개의 방을 복구해 주세요. 마지막 방까지 마치면 소수 탐정 배지 하나를 받아요.',levels=['관찰실','분류실','함정의 방','수리 작업장','연구소 복구'],questions=questions)

def initialise_hideout(state):
    state.setdefault('miniContent',[prime_pilot()])
    if not state.get('miniLibraryVersion'):
        from math_quest_mini_bank import authored_minis
        existing={m['id'] for m in state['miniContent']}
        state['miniContent'].extend(m for m in authored_minis(TOPICS) if m['id'] not in existing)
        state['miniLibraryVersion']=1
    validate_minis(state['miniContent'])

def validate_minis(content):
    if not isinstance(content,list) or any(not isinstance(m,dict) for m in content) or len({m.get('id') for m in content})!=len(content):raise ValueError('작은 탐험 ID를 확인해 주세요.')
    allowed={f'{u}-{i}' for u,topics in enumerate(TOPICS,1) for i in range(1,len(topics)+1)}
    for mini in content:
        if mini.get('id') not in allowed or len(mini.get('levels',[]))!=5:raise ValueError('작은 탐험은 등록된 주제의 5단계로 구성합니다.')
        if any(not isinstance(mini.get(key),str) or not mini[key].strip() for key in ('title','story','intro')):raise ValueError('탐험 제목과 이야기를 입력해 주세요.')
        qs=mini.get('questions',[])
        if any(q.get('level') not in range(1,7) for q in qs) or [sum(q.get('level')==level for q in qs) for level in range(1,6)]!=[3]*5 or sum(q.get('level')==6 for q in qs)>1:raise ValueError('단계별 기본 3문항과 선택 도전 최대 1문항을 등록해 주세요.')
        if len({q.get('id') for q in qs})!=len(qs):raise ValueError('문항 ID가 중복되었습니다.')
        for q in qs:
            if q.get('type') not in ('choice','multi','number') or any(not str(q.get(k,'')).strip() for k in ('id','text','hint','explanation')):raise ValueError('문항 형식과 내용을 확인해 주세요.')
            if q['type']=='number':number(q['answer'])
            elif not q.get('options'):raise ValueError('선택지를 입력해 주세요.')
            elif q['type']=='choice' and (type(q['answer']) is not int or not 1<=q['answer']<=len(q['options'])):raise ValueError('정답 선택지 번호를 확인해 주세요.')
            elif q['type']=='multi' and (not isinstance(q['answer'],list) or not q['answer'] or any(type(a) is not int or not 1<=a<=len(q['options']) for a in q['answer']) or len(set(q['answer']))!=len(q['answer'])):raise ValueError('복수 선택 정답 번호를 확인해 주세요.')
        mini['version']=version(mini)

def mini_catalog(state):
    active={m['id']:m for m in state['miniContent']}
    return [{'id':f'{u}-{i}','grade':1,'unit':u,'title':active.get(f'{u}-{i}',{}).get('title',title),'story':active.get(f'{u}-{i}',{}).get('story','다음 탐험 준비 중'),'ready':f'{u}-{i}' in active}
            for u,topics in enumerate(TOPICS,1) for i,title in enumerate(topics,1)]

def earned_badges(student):
    badges=[]
    for grade,record in student.get('gradeRecords',{}).items():
        if str(grade)!='1':continue
        badges += [f'big:{grade}:{id}' for id in record.get('clearedStages',[]) if type(id) is int and 1<=id<=10]
        badges += [f'mini:{grade}:{id}' for id in record.get('miniBadges',[]) if id in {f'{u}-{i}' for u,topics in enumerate(TOPICS,1) for i in range(1,len(topics)+1)}]
    return sorted(set(badges))

ITEMS=[
 {'id':'desk','title':'나무 책상','kind':'desk','unit':0}, {'id':'chair','title':'편안한 의자','kind':'chair','unit':0},
 {'id':'plant','title':'작은 화분','kind':'plant','unit':0}, {'id':'books','title':'나의 책 더미','kind':'books','unit':0},
 {'id':'cabinet','title':'황금 박물관 진열장','kind':'cabinet','unit':1}, {'id':'aquarium','title':'네모호 수족관','kind':'aquarium','unit':2},
 {'id':'crystal','title':'마법 수정 조명','kind':'crystal','unit':3}, {'id':'magnifier','title':'탐정의 지도 보드','kind':'board','unit':4},
 {'id':'telescope','title':'우주 관측 망원경','kind':'telescope','unit':5}, {'id':'gallery','title':'미술관 액자','kind':'gallery','unit':6},
 {'id':'garden','title':'공중정원 화단','kind':'garden','unit':7}, {'id':'clock','title':'마을 시계탑','kind':'clock','unit':8},
 {'id':'cocoa','title':'초콜릿 티 테이블','kind':'cocoa','unit':9}, {'id':'computer','title':'데이터 연구 컴퓨터','kind':'computer','unit':10}]
ITEMS += [{'id':'lamp','title':'독서 스탠드','kind':'lamp','unit':0,'stamps':3},{'id':'cushion','title':'숫자 쿠션','kind':'cushion','unit':0,'stamps':5},{'id':'shelf','title':'나의 책장','kind':'shelf','unit':0,'stamps':8},{'id':'globe','title':'탐험 지구본','kind':'globe','unit':0,'stamps':10}]

def stamp_count(student):return len({(g,s.get('assignmentId')) for g,r in student.get('gradeRecords',{}).items() for s in r.get('growthStamps',[]) if s.get('kind')=='growth'})
def room_catalog(student):
    owned=earned_badges(student)
    units={int(b.split(':')[2].split('-')[0]) for b in owned}
    return [{**item,'unlocked':(item['unit']==0 or item['unit'] in units) and stamp_count(student)>=item.get('stamps',0)} for item in ITEMS]

OUTFITS=[('casual','기본 티셔츠',0,0),('hoodie','포근한 후드티',0,0),('overalls','멜빵옷',0,0),('tracksuit','활동적인 운동복',0,0),('cardigan','독서 카디건',0,0),('labcoat','나의 연구 가운',0,3),('diving','해저 탐험복',2,0),('robe','마법사 로브',3,0),('coat','탐정 코트',4,0),('space','우주 탐험복',5,0),('gardener','정원사 작업복',7,0),('apron','초콜릿 공방 앞치마',9,0)]
def outfit_catalog(student):
    units={int(b.split(':')[2].split('-')[0]) for b in earned_badges(student)}
    return [dict(id=id,title=title,unit=unit,stamps=stamps,unlocked=(unit==0 or unit in units) and stamp_count(student)>=stamps) for id,title,unit,stamps in OUTFITS]

CHARACTER_HATS=[('none','모자 없이',0),('cap','산책 모자',0),('bow','리본',0),
    ('laurel','박물관 탐험가 월계관',1),('diver','네모호 잠수 헬멧',2),('wizard','마법사 모자',3),
    ('detective','탐정 모자',4),('astronaut','우주 탐험 헬멧',5),('beret','미술관 베레모',6),
    ('flower','공중정원 꽃관',7),('goggles','시계탑 정비 고글',8),('chef','초콜릿 요리사 모자',9),('headphones','데이터 연구 헤드폰',10)]

def default_character(cells=None):
    return {'expression':'smile','shirt':'sky','hair':'short','skin':'warm','hat':'none','outfit':'casual',
            'cell':next((i for i in [5]+list(range(12)) if str(i) not in (cells or {})),None)}

def character_catalog(student):
    units={int(b.split(':')[2].split('-')[0]) for b in earned_badges(student)}
    return [{'id':id,'title':title,'unit':unit,'unlocked':unit==0 or unit in units} for id,title,unit in CHARACTER_HATS]

def default_room():return {'name':'나의 수학 아지트','theme':'sky','floor':'wood','cells':{'4':'plant','7':'desk','10':'chair','11':'books'},'pins':[],'character':default_character()}
def save_room(student,room):
    if not isinstance(room,dict):raise ValueError('아지트 설정을 확인해 주세요.')
    if room.get('theme') not in ('sky','mint','peach') or room.get('floor') not in ('wood','cream','tiles'):raise ValueError('배경과 바닥을 확인해 주세요.')
    name=str(room.get('name','')).strip()
    if not name or len(name)>30:raise ValueError('아지트 이름은 1~30자로 입력해 주세요.')
    allowed={i['id'] for i in room_catalog(student) if i['unlocked']}
    cells=room.get('cells',{})
    if not isinstance(cells,dict) or any(k not in {str(i) for i in range(12)} or v not in allowed for k,v in cells.items()) or len(set(cells.values()))!=len(cells):raise ValueError('열린 가구를 한 자리씩 배치해 주세요.')
    pins=room.get('pins',[])
    if not isinstance(pins,list) or len(pins)>3 or any(pin is not None and not isinstance(pin,str) for pin in pins) or len(set(p for p in pins if p))!=len([p for p in pins if p]) or any(pin and pin not in earned_badges(student) for pin in pins):raise ValueError('내가 받은 배지를 최대 3개 전시할 수 있습니다.')
    character=room.get('character',student.get('hideout',{}).get('character',default_character(cells)))
    character=copy.deepcopy(character)
    if not isinstance(character,dict):raise ValueError('캐릭터를 확인해 주세요.')
    character.setdefault('outfit','casual')
    if character['outfit'] not in {o['id'] for o in outfit_catalog(student) if o['unlocked']}:raise ValueError('아직 열리지 않은 의상입니다.')
    style=room.get('style','library')
    style_unit={'library':0,'ocean':2,'magic':3}
    units={int(b.split(':')[2].split('-')[0]) for b in earned_badges(student)}
    if style not in style_unit or style_unit[style] and style_unit[style] not in units:raise ValueError('아직 열리지 않은 아지트 테마입니다.')
    if not isinstance(character,dict) or any(character.get(key) not in values for key,values in {
        'expression':('smile','happy','calm'),'shirt':('sky','mint','peach','lavender','yellow'),
        'hair':('short','bob','curly'),'skin':('light','warm','deep')}.items()):raise ValueError('캐릭터 꾸미기 항목을 확인해 주세요.')
    if character.get('hat') not in {h['id'] for h in character_catalog(student) if h['unlocked']}:raise ValueError('아직 열리지 않은 캐릭터 소품입니다.')
    cell=character.get('cell')
    if cell is not None and (type(cell) is not int or not 0<=cell<12 or str(cell) in cells):raise ValueError('캐릭터는 가구가 없는 자리에 놓아 주세요.')
    student['hideout']={'name':name,'theme':room['theme'],'floor':room['floor'],'cells':copy.deepcopy(cells),'pins':pins,'character':copy.deepcopy(character),'style':style,'savedAt':now()}

def mini_payload(state,student,id,teacher=False):
    m=next((m for m in state['miniContent'] if m['id']==id),None)
    if not m:raise ValueError('아직 준비 중인 작은 탐험입니다.')
    record=student.get('gradeRecords',{}).get('1')
    if record is None:raise ValueError('중1 기록에서 이용할 수 있습니다.')
    saved=record.get('miniAdventures',{}).get(id)
    progress=copy.deepcopy(saved) if saved and saved['version']==m['version'] else {'version':m['version'],'solved':[],'attempts':{},'bonusSolved':False}
    visible=copy.deepcopy(m)
    for q in visible['questions']:
        if not teacher:q.pop('answer',None)
        if not teacher and q['id'] not in progress['solved'] and not(q['level']==6 and progress['bonusSolved']):q.pop('explanation',None)
    return {'mini':visible,'progress':progress,'preview':teacher,'badgeEarned':id in record.get('miniBadges',[]),'practiceOnly':student['grade']!=1}

def mini_answer(state,student,body):
    id=body.get('miniId');payload=mini_payload(state,student,id);m=next(m for m in state['miniContent'] if m['id']==id)
    if body.get('version')!=m['version']:raise ValueError('문제가 변경되었습니다. 작은 탐험을 다시 열어 주세요.')
    record=student['gradeRecords']['1'];progress=record.setdefault('miniAdventures',{}).get(id)
    if not progress or progress['version']!=m['version']:
        previous=progress
        progress=payload['progress'];progress['history']=(previous.get('history',[])+[{k:v for k,v in previous.items() if k!='history'}]) if previous else []
        record['miniAdventures'][id]=progress
    basic=[q for q in m['questions'] if q['level']<=5]
    q=next((q for q in m['questions'] if q['id']==body.get('questionId')),None)
    if not q:raise ValueError('문항을 확인해 주세요.')
    if q['level']<=5 and (len(progress['solved'])==15 or q['id']!=basic[len(progress['solved'])]['id']):raise ValueError('순서대로 해결해 주세요.')
    if q['level']==6 and len(progress['solved'])!=15:raise ValueError('기본 탐험을 먼저 완료해 주세요.')
    value=body.get('answer')
    if q['type']=='number':correct=number(value)==number(q['answer'])
    elif q['type']=='choice':correct=type(value) is int and value==q['answer']
    else:correct=isinstance(value,list) and all(type(v) is int for v in value) and len(value)==len(set(value)) and sorted(value)==sorted(q['answer'])
    progress['attempts'][q['id']]=progress['attempts'].get(q['id'],0)+1
    if correct:
        if q['level']==6:progress['bonusSolved']=True
        else:progress['solved'].append(q['id'])
    badge_awarded=False
    if len(progress['solved'])==15 and student['grade']==1 and id not in record.setdefault('miniBadges',[]):
        record['miniBadges'].append(id);progress['completedAt']=now();badge_awarded=True
    return {**mini_payload(state,student,id),'correct':correct,'badgeAwarded':badge_awarded,'feedback':q['explanation'] if correct else '아직 해결되지 않았어요. 실마리를 살펴보고 다시 해 보세요.'}

def protect_student_rewards(old,new):
    new['miniLibraryVersion']=old.get('miniLibraryVersion',1)
    validate_minis(new.get('miniContent',old['miniContent']))
    new.setdefault('miniContent',copy.deepcopy(old['miniContent']))
    originals={s['uuid']:s for s in old['students']}
    for student in new['students']:
        prior=originals.get(student['uuid'])
        if not prior:continue
        if 'hideout' in prior:student['hideout']=copy.deepcopy(prior['hideout'])
        else:student.pop('hideout',None)
        for grade,record in student.get('gradeRecords',{}).items():
            prev=prior.get('gradeRecords',{}).get(grade,{})
            for key,default in [('miniBadges',[]),('miniAdventures',{})]:record[key]=copy.deepcopy(prev.get(key,default))
