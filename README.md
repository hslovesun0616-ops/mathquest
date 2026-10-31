# Math Quest · 나의 수학 성장 앱

Python 표준 라이브러리와 HTML/JavaScript로 구성한 학생·교사 학습 관리 앱입니다.

공개 소스: https://github.com/hslovesun0616-ops/mathquest

온라인 운영: https://mathquest-six-ashen.vercel.app — Vercel + Supabase 구성은 `CLOUD_SETUP.md`를 참고하세요. 온라인과 로컬 DB는 자동 동기화되지 않습니다.

## 실행

`python math_quest_server.py --port 8765`

- 학생: http://127.0.0.1:8765/?view=student
- 교사: http://127.0.0.1:8765/?view=teacher
- 최초 교사 비밀번호는 실행자가 직접 설정합니다. 연구용 검증 척도도 교사가 출처·채점법을 확인해 등록합니다.

## 구성

- 공통 성장 여권: 선택 학년의 교사 과제 통과·작은 탐험·방탈출 요약. 펼침은 이전 학년 기록만 표시합니다.
- 나의 수학 아지트: 캐릭터 의상 12종, 가구와 테마, 배지 전시와 수집함.
- 나의 학습: 교사 과제, 작은 탐험 40개·640문항, 방탈출 10탄·100문항.
- 나의 성장 돌아보기: 정기 설문, 지난 응답, 자유 돌아보기. 설문 보상 없음.
- 교사: 과제 통과·보완 요청, 학생·진급 취소, 문제 편집, 척도와 측정 시점, 연구 조회.

## 빌드·검증

`python build_research_app.py`

`python -m unittest test_math_quest_complete test_math_quest_hideout test_math_quest_adventure test_math_quest_research test_math_quest_server`

현재 UI 검증: `node verify_student_layout.cjs`, `node verify_mini_grades.cjs`, `node verify_adventure_map.cjs`, `node verify_research_analysis.cjs`, `node verify_passport_history.cjs`.

운영 데이터베이스·제출물·비밀번호·세션·실행 로그·화면 캡처·백업은 Git에 포함하지 않습니다. 초기 seed의 학생은 개발용 예시입니다. GitHub 소스와 별개로 Vercel + Supabase 운영 배포를 구성했습니다. 온라인 설정과 주소는 CLOUD_SETUP.md에 정리했습니다.

상세 실행·연구 안내는 `MATH_QUEST_RUN.md`, 외부 AI용 사본은 `python package_math_quest_review.py`로 만듭니다.
