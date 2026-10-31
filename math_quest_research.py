"""Research data rules; no default questionnaire or invented scale scores."""
import copy
from datetime import date, datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


def empty_research():
    return {'project': {'title': '수학 학습 앱 활용과 정의적 태도 변화',
                        'question': '개인 성장 기록·피드백·보상을 활용하는 수학 수업에서 자기효능감과 학습동기는 어떻게 변화하는가?',
                        'appStartedOn': ''},
            'instruments': [], 'waves': [], 'responses': [], 'observations': [], 'participation': {}}


def validate_instrument(instrument):
    if instrument.get('kind') not in ('selfEfficacy', 'motivation'):
        raise ValueError('측정 영역을 확인해 주세요.')
    if not all(str(instrument.get(k, '')).strip() for k in ('id', 'title', 'version', 'source')):
        raise ValueError('척도 이름·버전·출처를 입력해 주세요.')
    lo, hi = instrument.get('min'), instrument.get('max')
    if type(lo) is not int or type(hi) is not int or lo < 0 or hi > 10 or hi <= lo:
        raise ValueError('응답 범위는 0~10 사이의 정수로 지정해 주세요.')
    if len(instrument.get('options', [])) != hi - lo + 1:
        raise ValueError('응답 범위에 맞는 선택지 설명을 입력해 주세요.')
    items = instrument.get('items', [])
    if not items or len(items) > 100 or len({q.get('id') for q in items}) != len(items):
        raise ValueError('문항은 중복 없이 1~100개 등록해 주세요.')
    if any(not q.get('text') or not q.get('dimension') or type(q.get('reverse')) is not bool for q in items):
        raise ValueError('문항·하위영역·역채점 여부를 확인해 주세요.')


def score(instrument, answers):
    validate_instrument(instrument)
    if not isinstance(answers, dict) or set(answers) != {q['id'] for q in instrument['items']}:
        raise ValueError('모든 문항에 응답하거나 이번 측정 참여 안 함을 선택해 주세요.')
    dimensions = {}
    for item in instrument['items']:
        value = answers[item['id']]
        if type(value) is not int or not instrument['min'] <= value <= instrument['max']:
            raise ValueError('문항 응답 범위를 확인해 주세요.')
        if item['reverse']:
            value = instrument['min'] + instrument['max'] - value
        dimensions.setdefault(item['dimension'], []).append(value)
    return {key: sum(values) / len(values) for key, values in dimensions.items()}


def behavior(student, assignments):
    record = student['gradeRecords'][str(student['grade'])]
    tasks = [t for t in assignments if t['grade'] == student['grade']]
    ids = {t['id'] for t in tasks}
    subs = [s for s in record['submissions'] if s.get('assignmentId', 'stage-' + str(s.get('stageId'))) in ids]
    submitted = {s.get('assignmentId', 'stage-' + str(s.get('stageId'))) for s in subs}
    feedback = [s for s in subs if s.get('teacherFeedback')]
    revised = [s for s in feedback if s.get('revision', 0) > s.get('feedbackRevision', 0)]
    return {'assigned': len(ids), 'submitted': len(submitted), 'feedbackReceived': len(feedback),
            'feedbackRevised': len(revised), 'resubmitted': sum(1 for s in subs if s.get('revision', 0) > 1)}


def prepare_teacher_state(old_state, new_state):
    old = old_state.get('research') or empty_research()
    new = new_state.setdefault('research', empty_research())
    # Student responses and scores can only be created by the authenticated response endpoint.
    new['responses'] = copy.deepcopy(old['responses'])
    new['reflections']=copy.deepcopy(old.get('reflections',[]))
    old_instruments = {i['id']: i for i in old['instruments']}
    used = {i for w in old['waves'] for i in w['instrumentIds']}
    new_ids = {i['id'] for i in new['instruments']}
    if not used <= new_ids:
        raise ValueError('실시한 측정의 척도는 삭제할 수 없습니다.')
    for instrument in new['instruments']:
        validate_instrument(instrument)
        if instrument['id'] in used and instrument != old_instruments[instrument['id']]:
            raise ValueError('실시한 척도는 고정됩니다. 변경하려면 새 버전으로 등록해 주세요.')
    if len(new_ids) != len(new['instruments']):
        raise ValueError('척도 ID가 중복되었습니다.')
    instruments = {i['id']: i for i in new['instruments']}
    old_waves = {w['id']: w for w in old['waves']}
    if len({w['id'] for w in new['waves']}) != len(new['waves']):
        raise ValueError('측정 시점 ID가 중복되었습니다.')
    if not set(old_waves) <= {w['id'] for w in new['waves']}:
        raise ValueError('실시한 측정 시점은 삭제할 수 없습니다.')
    students = {s['uuid']: s for s in new_state['students']}
    for wave in new['waves']:
        if wave['id'] in old_waves:
            previous = old_waves[wave['id']]
            comparable = {k: v for k, v in wave.items() if k != 'status'}
            baseline = {k: v for k, v in previous.items() if k != 'status'}
            if comparable != baseline or wave.get('status') not in ('open', 'closed') or (previous['status'] == 'closed' and wave['status'] != 'closed'):
                raise ValueError('시작한 측정의 문항·대상·시점은 고정됩니다. 마감만 변경할 수 있습니다.')
            continue
        if not wave.get('label') or not wave.get('date') or not wave.get('participantIds') or not wave.get('instrumentIds'):
            raise ValueError('측정 이름·날짜·척도·참여 학생을 설정해 주세요.')
        date.fromisoformat(wave['date'])
        if len(set(wave['participantIds'])) != len(wave['participantIds']):
            raise ValueError('측정 대상 학생이 중복되었습니다.')
        if len(set(wave['instrumentIds'])) != len(wave['instrumentIds']) or any(i not in instruments for i in wave['instrumentIds']):
            raise ValueError('등록한 척도를 선택해 주세요.')
        if any(not instruments[i].get('scoringConfirmed') for i in wave['instrumentIds']):
            raise ValueError('원 척도의 사용·채점 지침을 확인한 후 측정을 열어 주세요.')
        if any(uuid not in students or not new['participation'].get(uuid, {}).get('eligible') for uuid in wave['participantIds']):
            raise ValueError('참여 확인된 학생만 측정 대상으로 선택할 수 있습니다.')
        wave['status'] = 'open'
        wave['openedAt'] = now()
        wave['participantSnapshot'] = {uuid: {'grade': students[uuid]['grade'], 'classNum': students[uuid]['classNum'],
                                               'behavior': behavior(students[uuid], new_state['assignments'])}
                                       for uuid in wave['participantIds']}
    return new_state


def submit_response(state, student_uuid, body):
    research = state.setdefault('research', empty_research())
    wave = next((w for w in research['waves'] if w['id'] == body.get('waveId')), None)
    if not wave or wave['status'] != 'open' or student_uuid not in wave['participantIds'] or not research['participation'].get(student_uuid, {}).get('eligible'):
        raise ValueError('현재 참여할 수 있는 연구 설문이 아닙니다.')
    if body.get('instrumentId') not in wave['instrumentIds']:
        raise ValueError('이 측정에 등록된 설문을 선택해 주세요.')
    if any(r['studentUuid'] == student_uuid and r['waveId'] == wave['id'] and r['instrumentId'] == body['instrumentId'] for r in research['responses']):
        raise ValueError('이미 응답을 마쳤습니다. 같은 시점의 응답은 변경하지 않습니다.')
    instrument = next(i for i in research['instruments'] if i['id'] == body['instrumentId'])
    declined = body.get('declined') is True
    answers = {} if declined else body.get('answers')
    scores = {} if declined else score(instrument, answers)
    research['responses'].append({'studentUuid': student_uuid, 'waveId': wave['id'], 'instrumentId': instrument['id'],
                                  'grade': wave['participantSnapshot'][student_uuid]['grade'], 'status': 'declined' if declined else 'completed',
                                  'answers': answers, 'scores': scores, 'submittedAt': now()})


def student_research(research, uuid):
    research = research or empty_research()
    waves = [copy.deepcopy(w) for w in research['waves'] if uuid in w['participantIds']]
    for wave in waves:
        wave['participantIds'] = [uuid]
        wave['participantSnapshot'] = {uuid: wave.get('participantSnapshot', {}).get(uuid, {})}
    ids = {i for w in waves for i in w['instrumentIds']}
    return {'project': {'title': research['project'].get('title', '')},
            'instruments': [i for i in research['instruments'] if i['id'] in ids], 'waves': waves,
            'responses': [r for r in research['responses'] if r['studentUuid'] == uuid],
            'participation': {uuid: research['participation'].get(uuid, {})}, 'observations': [],'reflections':[r for r in research.get('reflections',[]) if r['studentUuid']==uuid]}
