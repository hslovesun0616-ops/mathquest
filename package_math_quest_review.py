"""Create a runnable review copy containing synthetic data and no classroom database."""
from pathlib import Path
import csv,json,re,zipfile
from math_quest_hideout import initialise_hideout

root=Path(__file__).resolve().parent
folder=root/'math_quest_review';folder.mkdir(exist_ok=True)
files=['math_quest_server.py','math_quest_growth.py','math_quest_research.py','math_quest_adventure.py','math_quest_hideout.py','math_quest_mini_bank.py','math_quest_adventures.json','math_quest_admin.js','math_quest_research.js','math_quest_adventure.js','math_quest_hideout.js','math_quest_finish.js','math_quest_student_layout.py','math_quest_student_layout.js','math_quest_growth.css','build_research_app.py','math_quest_teacher_base.html','math_quest_app.updated.html','math_quest_cloud.py','api/index.py','supabase/mathquest_schema.sql','vercel.json','requirements.txt','CLOUD_SETUP.md','provision_cloud.py','migrate_to_supabase.py','deploy_vercel.py','vercel_cli_compat.cjs','verify_cloud_live.py']
for name in files:
    text=(root/name).read_text(encoding='utf-8')
    if name.endswith('.html'):text=re.sub(r'    let students = \[\s*\n.*?\n    \];','    let students = [];',text,count=1,flags=re.S)
    destination=folder/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(text,encoding='utf-8')
seed=json.loads((root/'math_quest_seed.json').read_text(encoding='utf-8'))
for i,student in enumerate(seed['students'],1):
    student['name']=f'검토학생{i}';student['teacher']='검토용 교사';student['history']='가상 검토용 학생 기록';student['qualitativeNotes']=''
    for record in student.get('gradeRecords',{}).values():
        record['qualitativeNotes']='';record['submissions']=[]
    student['submissions']=[];student.pop('hideout',None)
seed.pop('research',None)
(folder/'math_quest_seed.json').write_text(json.dumps(seed,ensure_ascii=False,indent=2),encoding='utf-8')
library={};initialise_hideout(library)
(folder/'math_quest_minis.json').write_text(json.dumps(library['miniContent'],ensure_ascii=False,indent=2),encoding='utf-8')
csv_path=root/'작은탐험_40개_640문항.csv'
with csv_path.open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.writer(f);writer.writerow(['탐험','주제','단계','문항ID','유형','문제','선택지','정답','힌트','해설'])
    for m in library['miniContent']:
        for q in m['questions']:writer.writerow([m['id'],m['title'],q['level'],q['id'],q['type'],q['text'],' / '.join(q['options']),json.dumps(q['answer']),q['hint'],q['explanation']])
(folder/csv_path.name).write_bytes(csv_path.read_bytes())
(folder/'검토용_실행.cmd').write_text('@echo off\ncd /d "%~dp0"\npython math_quest_server.py --port 8877 --data-dir review_data\npause\n',encoding='utf-8')
(folder/'검토_안내.md').write_text('''# Math Quest 검토용 사본

실제 수업 데이터베이스, 제출 파일, 설문 응답, 비밀번호, 세션 토큰은 포함하지 않았습니다. 초기 데이터는 가상 검토 학생입니다. 실제 운영 파일을 덮어쓰지 말고 별도 폴더에서 실행하세요.

Python 3에서 `python math_quest_server.py --port 8877 --data-dir review_data`로 실행한 뒤 학생 주소 http://127.0.0.1:8877/?view=student 또는 교사 주소 http://127.0.0.1:8877/?view=teacher 를 엽니다. 첫 교사 비밀번호는 검토자가 직접 설정합니다. 학생은 10101 / 검토학생1입니다. 화면 스타일과 아이콘은 기존 앱처럼 CDN 연결을 사용합니다.

## 검토 요청

- 성장 여권과 아지트·학습·성장 돌아보기 3영역의 정보 구조와 접근성
- 교사 과제 통과만 성취율·성장 도장에 반영되는지, 탐험과 설문이 섞이지 않는지
- 작은 탐험 40개 × 기본 15문항 + 선택 1문항 = 640문항의 수학적 정확성, 난이도, 문항 표현
- `math_quest_minis.json` 및 CSV의 문제·선택지·정답·해설을 대조해 검토
- 12종 의상, 과제 도장에 따른 생활 소품, 지역 배지에 따른 의상·가구·공간 테마
- 진급 취소 때 고유 ID, 이전 기록, 꾸미기, 제출물과 연구 기록이 보존되는지
- 교사 편집기·파일 제출·설문 배포·응답 비공개·낙관적 동시 저장·서버 검증

## 연구 설문

검증된 척도를 임의로 만들어 넣지 않았습니다. 교사가 사용할 척도의 출처·사용 조건·역채점·하위영역을 확인하고 등록한 뒤 측정 시점과 대상을 지정해 배포합니다. 설문 응답과 자유 돌아보기는 보상에 사용하지 않습니다. 이 사본의 설문 응답도 초기에는 비어 있습니다.

## 주소의 범위

127.0.0.1은 실행한 컴퓨터에서만 열립니다. 외부 AI에게는 이 ZIP이나 소스·CSV를 첨부해야 합니다. 실제 운영 앱을 외부에서 쓰려면 별도 인증·HTTPS·서버 배포가 필요합니다. 온라인 운영 주소는 CLOUD_SETUP.md에 있습니다. 이 검토용 사본은 온라인 원자료와 분리한 가상 데이터로 실행합니다.
''',encoding='utf-8')
archive=root/'MathQuest_수정보완_검토용.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for file in folder.rglob('*'):
        if file.is_file() and '__pycache__' not in file.parts:z.write(file,'MathQuest_검토용/'+file.relative_to(folder).as_posix())
print('Review ZIP and 640-question CSV created without classroom database or credentials.')
