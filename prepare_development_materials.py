"""Assemble a complete, private-data-free desktop handoff directory."""
from pathlib import Path
import csv,hashlib,json,os,shutil,subprocess,sys,zipfile

root=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(root/'package_math_quest_review.py')],cwd=root,check=True)
target=Path.home()/'Desktop'/'개발자료'
target.mkdir(exist_ok=True)
src=target/'01_전체소스';src.mkdir(exist_ok=True)
questions=target/'02_문항자료';questions.mkdir(exist_ok=True)
docs=target/'03_설계와검증';docs.mkdir(exist_ok=True)
pictures=target/'04_화면미리보기';pictures.mkdir(exist_ok=True)
for cache in src.rglob('__pycache__'):
    if not cache.resolve().is_relative_to(target.resolve()):raise RuntimeError('Unexpected cache location')
    for file in cache.glob('*.pyc'):file.unlink()
    if not any(cache.iterdir()):cache.rmdir()
seed=json.loads((root/'math_quest_seed.json').read_text(encoding='utf-8'))
mapping={student['name']:f'검토학생{i}' for i,student in enumerate(seed['students'],1)}
for file in (root/'math_quest_review').rglob('*'):
    if not file.is_file():continue
    if file.suffix=='.csv' or file.name=='math_quest_minis.json':shutil.copy2(file,questions/file.name)
    else:
        destination=src/file.relative_to(root/'math_quest_review');destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,destination)
extras=['README.md','MATH_QUEST_RUN.md','make_adventure_content.py','.gitignore','test_math_quest_server.py','test_math_quest_research.py','test_math_quest_adventure.py','test_math_quest_hideout.py','test_math_quest_complete.py','test_math_quest_cloud.py','verify_student_layout.cjs','verify_mini_grades.cjs','verify_adventure_map.cjs','verify_research_analysis.cjs','verify_passport_history.cjs']
for name in extras:
    text=(root/name).read_text(encoding='utf-8')
    for old,new in mapping.items():text=text.replace(old,new)
    (src/name).write_text(text,encoding='utf-8')
shutil.copy2(root/'math_quest_adventures.json',questions/'방탈출_10탄_100문항.json')
for name in ['student-final-preview.png','teacher-final-preview.png','online-deployment-preview.png']:
    if (root/name).exists():shutil.copy2(root/name,pictures/name)
(target/'00_먼저읽기.md').write_text('''# AI 검토용 개발자료

**다른 AI에는 이 폴더의 `AI검토용_전체개발자료.zip` 하나를 첨부하면 됩니다.** ZIP 첨부가 어려우면 `03_설계와검증/AI_검토요청서.md`를 먼저 전달하고 소스와 문항 파일을 나누어 첨부하세요.

- 01_전체소스: 실행 가능한 앱과 빌더, 서버, 현재 자동화 테스트, 가상 초기 학생 데이터
- 02_문항자료: 작은 탐험 40개·640문항 CSV/JSON, 기존 방탈출 10탄·100문항 JSON
- 03_설계와검증: 기능·데이터·보상·연구 설계, 검토 요청과 검증 결과
- 04_화면미리보기: 학생·교사 화면 예시
- 파일목록_SHA256.csv: 빠진 파일이나 파일 변경을 확인할 목록과 해시

운영용 학생 데이터베이스, 제출 파일, 실제 설문 응답, 교사 비밀번호, 인증 토큰, 로그인 세션, 실행 로그와 운영 백업은 포함하지 않았습니다. 전체 소스의 seed와 테스트 학생 이름은 검토용 가명입니다.

실행: 01_전체소스 폴더에서 `python math_quest_server.py --port 8877 --data-dir review_data` 또는 `검토용_실행.cmd`를 실행하세요. 학생은 10101 / 검토학생1로 로그인합니다. 교사 비밀번호는 검토자가 처음에 직접 설정합니다. Python 표준 라이브러리를 사용하며 UI 스타일과 아이콘에는 인터넷 CDN 연결이 필요합니다.

학생: http://127.0.0.1:8877/?view=student / 교사: http://127.0.0.1:8877/?view=teacher
실제 온라인 주소는 https://mathquest-six-ashen.vercel.app 입니다. 검토용 위 localhost 주소는 이 사본을 실행한 컴퓨터에서만 열립니다. 외부 AI가 주소만으로 접속할 수는 없습니다. GitHub 연결도 앱의 인터넷 배포와는 다릅니다.
''',encoding='utf-8')
(docs/'AI_검토요청서.md').write_text('''# 검토 요청

이 앱은 중학생의 수학 학습 지속과 정의적 태도 변화를 기록하기 위한 앱입니다. 단순한 보상 수집보다 학습·재도전·성찰을 중심으로 검토해 주세요.

1. 학생 화면: 공통 성장 여권 + 01 아지트 / 02 학습 / 03 성장 돌아보기. 중복 정보와 접근성, 모바일 화면을 검토합니다. 여권 요약은 선택 학년, 펼침은 이전 학년만 표시하며 이전 학년이 없으면 숨깁니다.
2. 교사 과제: 제출은 검토 대기입니다. 교사의 과제 통과만 성취율·기본 성장 도장에 반영합니다. 보완 요청과 피드백 후 재도전을 지원합니다. 탐험·설문을 과제 성취율에 합산하지 않습니다.
3. 문항: 40개 작은 탐험의 기본 15문항+선택 1문항=640문항, 대탐험 10탄×10문항=100문항을 수학적으로 대조해 주세요. 정답/선택지 순서/해설/조건의 충분성/난이도/학년 적합성/문항 표현을 검토합니다. 정답이 있는 CSV·JSON은 교사 검토 자료이며 학생 API에는 미해결 정답을 보내지 않습니다.
4. 보상: 작은 탐험은 5단계 전체 완료 시 배지 1개, 대탐험은 한 탄 완료 시 1개입니다. 선택 도전은 배지 조건이 아닙니다. 도장·배지는 차감하지 않고 의상/가구/테마를 엽니다. 반복 승인·재제출로 보상을 부풀릴 수 없는지 확인합니다.
5. 연구: 자기효능감과 학습동기는 서로 다른 영역으로 추적합니다. 검증 척도는 임의로 만들어 넣지 않았습니다. 교사가 출처·사용 조건·역채점·하위영역을 확인해 등록하고 측정 시점을 열어 배포합니다. 미응답은 0점이 아니며 설문 참여와 긍정 응답에 보상을 주지 않습니다. 자유 돌아보기는 설문 점수와 분리합니다.
6. 누적 기록: 고유 학생 ID와 학년별 기록, 진급·진급 취소, 과제 첨부물과 꾸미기 보존을 확인합니다. 중1 콘텐츠가 중2·중3 화면에 섞이지 않아야 합니다. 현재 작은 탐험·방탈출 콘텐츠는 중1용이며 중2·중3는 준비 안내입니다.
7. 교사 관리: 학생 관리, 진급 취소, 과제 통과/보완, 640문항 편집·CSV, 연구 척도·시점·참여 관리, 학생 돌아보기 조회를 검토합니다.
8. 보안: 역할별 데이터 노출, 제출 파일 권한, 학생 원자료 비공개, 낙관적 동시 저장, 버전 변경 시 이전 기록 보존을 확인합니다.

결과는 우선순위/재현 방법/원인/수정할 파일과 제안/회귀 검증으로 구체적으로 제시해 주세요. 가상 seed를 실제 연구 결과로 해석하지 마세요. 자동화 테스트 통과가 모든 문항의 학술적 검증이나 연구 척도 타당성을 뜻하지 않습니다.
''',encoding='utf-8')
(docs/'앱_설계와_파일구조.md').write_text('''# 설계와 주요 파일

Python ThreadingHTTPServer + SQLite, HTML/JavaScript입니다. 별도 DB 서버나 Python 외부 패키지가 필요하지 않습니다. 실제 배포에는 별도 인증·HTTPS·접속 구조 설계가 필요합니다.

- math_quest_server.py: 인증·세션·파일·API·서버 측 역할 검증
- math_quest_growth.py: 진급/취소와 자유 돌아보기
- math_quest_research.py/js: 연구 척도 버전·측정 시점·응답·분석
- math_quest_hideout.py/js: 작은 탐험 진행, 배지, 가구·캐릭터 보상과 저장
- math_quest_mini_bank.py: 39개 작은 탐험 원고와 변형 생성; 기존 소수와 합성수 원고는 hideout.py
- math_quest_adventure.py/js + adventures.json: 기존 10탄 게임과 100문항
- math_quest_admin.js: 교사 관리·문구·제출 API 연결
- math_quest_student_layout.py/js: 세 영역의 구조와 화면 전환
- math_quest_finish.js: 성장 여권·의상·편집기·교사 추가 기능
- math_quest_growth.css: 성장 여권·아지트·세 영역 스타일
- build_research_app.py: teacher_base.html과 편집 가능한 모듈에서 최종 HTML 생성

운영 DB는 state/body/version, config, sessions, files 테이블로 구성됩니다. students.uuid는 계속 유지하며 gradeRecords에 학년별 기록을 보관합니다. 진급 취소는 이전 학번·반을 복구하되 다음 학년 기록을 삭제하지 않습니다. 교사 전체 저장은 version으로 충돌을 차단합니다.

학생 API는 본인 데이터만, 교사는 관리 범위 데이터를 받습니다. 연구 관찰은 교사 전용입니다. 설문 버전과 시작한 측정의 대상·문항은 고정됩니다. 작은 탐험 문항 버전이 바뀌면 새 진행으로 시작하고 과거 시도와 획득 배지를 보존합니다.

이 사본은 운영 데이터가 없는 검토용입니다. 실제 교실 기록을 공유하거나 Git에 커밋하지 마세요.
''',encoding='utf-8')
(docs/'최근_변경사항.md').write_text('''# 최근 반영

- 학생 주요 영역을 아지트·학습·성장 돌아보기로 분리
- 성장 여권에 교사 과제/작은 탐험/방탈출을 각기 표시
- 현재 학년 숫자를 다시 보여주던 펼침을 제거하고 이전 학년 기록만 표시
- 작은 탐험 40개·640문항 완성, 교사 편집과 CSV 제공
- 의상 12종과 테마, 과제 도장에 따른 생활 소품, 지역 배지에 따른 장식
- 과제 통과·보완 요청, 설문·자유 돌아보기에 보상 없음
- 기록을 삭제하지 않는 진급 취소
- 외부 AI 검토용 가상 데이터 사본과 Git의 운영 데이터 제외 규칙
''',encoding='utf-8')
commands=[['python','-m','unittest','test_math_quest_cloud','test_math_quest_complete','test_math_quest_hideout','test_math_quest_adventure','test_math_quest_research','test_math_quest_server']]+[['node',name] for name in ['verify_student_layout.cjs','verify_mini_grades.cjs','verify_adventure_map.cjs','verify_research_analysis.cjs','verify_passport_history.cjs']]
results=[]
for command in commands:
    run=subprocess.run(command,cwd=src,capture_output=True,text=True,encoding='utf-8',errors='replace',env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    results.append('$ '+' '.join(command)+'\n'+run.stdout+run.stderr+f'\nexit={run.returncode}\n')
    if run.returncode:raise RuntimeError('Review-copy check failed: '+' '.join(command)+'\n'+run.stdout+run.stderr)
(docs/'검증결과.txt').write_text('\n'.join(results),encoding='utf-8')
(docs/'GitHub_저장소.md').write_text('''# 공개 소스 저장소

https://github.com/hslovesun0616-ops/mathquest

사용자가 공개 업로드를 승인한 소스입니다. 운영 DB·제출물·설문 응답·비밀번호·로그인 세션은 포함하지 않습니다. seed·HTML·테스트의 학생 이름과 ID는 가상 개발 데이터로 정리했습니다. 이 폴더에는 AI 검토에 바로 쓸 수 있도록 실행용 소스, 문항 CSV/JSON, 테스트, 설계 문서와 화면 예시를 함께 제공합니다.

GitHub 주소는 소스를 보는 주소입니다. Python·SQLite 서버가 자동 배포된 앱 실행 주소는 아닙니다.
''',encoding='utf-8')
manifest=target/'파일목록_SHA256.csv'
files=sorted(p for p in target.rglob('*') if p.is_file() and p.name!='AI검토용_전체개발자료.zip' and p!=manifest)
with manifest.open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.writer(f);writer.writerow(['파일','바이트','SHA256'])
    for file in files:writer.writerow([file.relative_to(target).as_posix(),file.stat().st_size,hashlib.sha256(file.read_bytes()).hexdigest()])
with zipfile.ZipFile(target/'AI검토용_전체개발자료.zip','w',zipfile.ZIP_DEFLATED) as z:
    for file in files+[manifest]:z.write(file,'개발자료/'+file.relative_to(target).as_posix())
print(f'Prepared {len(files)+1} files and one complete handoff ZIP in {target}')
