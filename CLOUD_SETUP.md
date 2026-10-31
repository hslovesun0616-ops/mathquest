# Vercel + Supabase 운영

운영 주소: https://mathquest-six-ashen.vercel.app

- 학생: https://mathquest-six-ashen.vercel.app/?view=student
- 교사: https://mathquest-six-ashen.vercel.app/?view=teacher

Vercel은 HTML과 Python API를 실행하고, Supabase는 `mathquest` 비공개 PostgreSQL 스키마와 `mathquest-submissions` 비공개 Storage 버킷을 제공합니다. 브라우저는 DB 비밀번호나 서버용 키를 받지 않습니다. 첨부파일은 인증된 요청에서 발급한 서명 URL로 최대 10MB까지 전송하고, 권한 확인 후 60초 다운로드 URL을 발급합니다.

## 운영 원칙

- 기존 로컬 기록과 교사 계정을 백업 후 이전했습니다. 활성 로컬 세션은 복사하지 않았습니다.
- 이후 운영 기록은 위 온라인 주소에서 저장합니다. 로컬 SQLite는 보존된 별도 백업이며, 양방향 자동 동기화되지 않습니다.
- 공개 방문자가 교사 계정을 먼저 생성할 수 없도록 클라우드 교사 가입은 차단합니다. 기존 교사 비밀번호로 로그인합니다.
- 로그인은 반복 시도를 제한하고 HTTPS의 Secure·HttpOnly·SameSite 쿠키를 사용합니다.
- 학생·연구·첨부 원자료는 Git과 배포 소스에 넣지 않습니다. Preview 환경에 운영 DB 키를 자동 배포하지 않습니다.

## 주요 파일

- `api/index.py`: Vercel 요청을 기존 역할 검증 API로 연결
- `math_quest_cloud.py`: PostgreSQL 연결·동시 쓰기 잠금·서명 업로드와 다운로드
- `supabase/mathquest_schema.sql`: 공개 Data API에 노출되지 않는 스키마
- `provision_cloud.py`: 확인된 계정 프로젝트에 최소 권한 앱 역할과 비공개 버킷을 최초 구성
- `migrate_to_supabase.py`: 기존 DB를 백업하고 상태·교사 설정·첨부물을 대조해 이전. 다른 클라우드 기록을 덮어쓰지 않음
- `deploy_vercel.py`: 허용된 실행 파일만 별도 배포 폴더에 복사하고 민감 환경변수는 stdin으로 전달
- `verify_cloud_live.py`: 실제 배포의 로그인·권한·5MB 가상 첨부를 검사하고 테스트 데이터 정리

## 로컬 연결 설정

`python -m pip install -r requirements.txt`

계정 확인용 `.cloud-owner.json`은 `email`, `supabaseProject` 필드를 가진 비공개 로컬 설정입니다. 실제 값이나 인증키를 Git에 넣지 않습니다. Supabase CLI는 앱 전용 `mathquest` 프로필로 연결하며, Vercel CLI는 연결한 사용자 계정을 검증합니다.

`.env.cloud.local`에는 `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SECRET_KEY`가 있습니다. Vercel Production에 민감 환경변수로 등록합니다. `NEXT_PUBLIC` 같은 공개 접두사를 쓰지 않습니다. `.env.local`의 Vercel OIDC 토큰, `.vercel` 설정, `supabase/.temp`, 배포 작업 폴더도 Git에서 제외됩니다.

스키마나 권한을 변경할 때에는 확인한 프로젝트에만 적용하고 운영 기록은 백업합니다. 계정 변경·프로젝트 변경 때 기존 연결값을 무작정 덮어쓰지 않습니다.

## 검증

로컬 단위·회귀 검사: `python -m unittest test_math_quest_cloud test_math_quest_complete test_math_quest_hideout test_math_quest_adventure test_math_quest_research test_math_quest_server`

실서비스 검사: 운영자가 비공개 연결 환경을 준비한 후 `python verify_cloud_live.py`. 학습과 연구 기록은 수정하지 않으며, 5MB 테스트 파일과 짧은 검증용 세션은 정리합니다. 서명 URL·쿠키·연결키·학생 내용은 로그로 출력하지 않습니다.
