from pathlib import Path
from math_quest_student_layout import organise_student_layout
p=Path('math_quest_app.updated.html')
s=Path('math_quest_teacher_base.html').read_text(encoding='utf-8')
s=s.replace('clearedStages: [], submissions: [], preScore: 0, postScore: 0, selfEfficacy: 0, qualitativeNotes:', 'clearedStages: [], submissions: [], preScore: null, postScore: null, selfEfficacy: null, qualitativeNotes:')
# Rebuild the embedded management script from its editable source.
start=s.index('// Account, teacher management, editable student copy')
end=s.rindex('  </script>')
s=s[:start]+Path('math_quest_admin.js').read_text(encoding='utf-8')+'\n'+Path('math_quest_research.js').read_text(encoding='utf-8')+'\n'+Path('math_quest_adventure.js').read_text(encoding='utf-8')+'\n'+Path('math_quest_hideout.js').read_text(encoding='utf-8')+'\n'+Path('math_quest_student_layout.js').read_text(encoding='utf-8')+'\n'+Path('math_quest_finish.js').read_text(encoding='utf-8')+'\n'+s[end:]
start=s.index('    <section id="teacherView"')
end=s.index('    </section>',start)+len('    </section>')
old=s[start:end]
menus=old[old.index('      <details class="bg-white rounded-2xl border p-5" open>'):old.index('      <!-- 교사 상단 컨트롤 바:')]
menus+='''<details class="bg-white border rounded-2xl p-5"><summary class="font-extrabold text-lg cursor-pointer">🧩 내장 방탈출 1~10탄 문제·스토리 관리</summary><p class="text-sm text-slate-500 mt-3">각 탄의 도입·완료 이야기와 10개 장치의 문제·숫자 정답·힌트·해설을 수정할 수 있습니다. 문제를 변경하면 진행 중인 도전은 새 버전으로 시작하며, 이전 기록과 이미 획득한 배지는 보존합니다.</p><label class="block font-bold text-sm mt-4">수정할 탄<select id="adventureEditorStage" onchange="loadAdventureEditor()" class="border rounded-lg p-2 ml-2"></select></label><form id="adventureEditorForm" onsubmit="saveAdventureEditor(event)" class="space-y-4 mt-4"></form></details>'''
menus+='''<details class="bg-white border rounded-2xl p-5"><summary class="font-extrabold text-lg cursor-pointer">🌱 작은 탐험 콘텐츠 관리</summary><p class="text-sm text-slate-500 mt-3">우선 소수와 합성수 작은 탐험을 제공합니다. 단계별 3문제, 5단계 전체 완료 시 배지 1개입니다. 나머지 39개 주제는 추가 예정으로 표시합니다. 아래 원고에서 text(문제), options(선택지), answer(정답), hint(힌트), explanation(해설)을 편집할 수 있습니다. 선택형 정답은 1부터 시작하는 선택지 번호이며, 복수 선택형은 번호 배열입니다. 단계 수·문항 ID·형식은 유지해 주세요.</p><textarea id="miniContentEditor" rows="16" class="block w-full border rounded-xl p-3 mt-4 font-mono text-xs" aria-label="작은 탐험 문항 원고"></textarea><button onclick="saveMiniTeacherEditor()" class="bg-indigo-600 text-white rounded-xl px-4 py-2 font-bold mt-3">작은 탐험 원고 저장</button></details>'''
teacher='''    <section id="teacherView" class="hidden space-y-6">
      <div class="bg-indigo-950 text-white rounded-2xl p-6 flex flex-wrap justify-between gap-4 items-center">
        <div><h1 class="text-2xl font-extrabold">교사 관리실</h1><p class="text-sm text-indigo-200 mt-2">꾸준한 수업 지원과 피드백, 학생의 정의적 태도 변화를 기록합니다.</p></div>
        <div class="flex flex-wrap gap-3 items-center"><span id="teacherSaveStatus" role="status" class="text-xs text-indigo-200">서버 연결됨</span><button onclick="refreshTeacherData()" class="bg-white text-indigo-950 rounded-xl p-3 text-sm font-bold">최신 기록 불러오기</button></div>
      </div>
      <nav class="flex flex-wrap gap-3" aria-label="교사 관리 영역"><button id="teacherArea-lesson" onclick="changeTeacherArea('lesson')" aria-pressed="true">수업 관리</button><button id="teacherArea-research" onclick="changeTeacherArea('research')" aria-pressed="false">연구·변화 분석</button></nav>
      <div id="teacherLessonArea" class="space-y-6">
      <div class="flex flex-wrap gap-4 bg-white border rounded-2xl p-4"><label class="text-sm font-bold">학급 <select id="teacherClassFilter" onchange="renderTeacherDashboard()" class="border rounded-lg p-2"><option value="all">전체 학급</option></select></label><label class="text-sm font-bold">어드벤처 배지 모양 <select id="badgeStyleSelector" onchange="changeBadgeStyle(this.value)" class="border rounded-lg p-2"><option value="math">수학 기호</option><option value="geometry">기하 보석</option><option value="adventure">모험 유물</option></select></label></div>
      <div id="teacherLessonStats" class="grid grid-cols-1 sm:grid-cols-3 gap-4"></div>
'''+menus+'''
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-6"><div class="bg-white border rounded-2xl p-5 overflow-x-auto"><h2 class="text-lg font-extrabold mb-4">학생별 수업 현황</h2><table class="w-full text-sm text-left"><thead><tr class="text-slate-500"><th class="p-3">학생</th><th class="p-3">학급</th><th class="p-3">과제 확인 완료율</th><th class="p-3">관리</th></tr></thead><tbody id="teacherStudentTableBody"></tbody></table></div><div id="teacherStudentResearchPanel" class="bg-white border rounded-2xl p-5"></div></div>
      </div>
      <div id="teacherResearchArea" hidden class="space-y-6">
        <div class="bg-indigo-50 border border-indigo-200 rounded-2xl p-5"><h2 class="text-xl font-extrabold text-indigo-950">자기효능감·학습동기 변화 기록</h2><p class="text-sm text-indigo-900 mt-2">자기효능감은 주된 결과, 학습동기는 보조 결과로 각각 추적합니다. 과제 완료율과 도장 수를 정의적 태도 점수로 대신하지 않습니다.</p><p class="text-sm text-slate-600 mt-2">상승·유지·하락을 그대로 기록합니다. 변화가 관찰되어도 비교 설계 없이 앱의 효과로 단정하지 않습니다. 연구 설문에는 보상을 지급하지 않습니다.</p></div>
        <details class="bg-white border rounded-2xl p-5" open><summary class="font-extrabold cursor-pointer">1. 연구 계획·참여 확인</summary>
          <form onsubmit="saveResearchProject(event)" class="space-y-3 mt-4"><label class="block text-sm font-bold">연구 이름<input id="researchProjectTitle" required maxlength="200" class="block w-full border rounded-lg p-2 mt-1"></label><label class="block text-sm font-bold">연구 질문<textarea id="researchQuestion" required rows="2" class="block w-full border rounded-lg p-2 mt-1"></textarea></label><label class="block text-sm font-bold">앱을 실제로 활용하기 시작한 날짜<input id="researchAppStart" type="date" class="block border rounded-lg p-2 mt-1"></label><p class="text-xs text-slate-500">이미 사용을 시작했다면 최초 설문을 ‘앱 사용 전’으로 소급하지 않습니다. 최초 측정 → 매 학기 말, 중1~중3 추적을 권장 일정으로 사용할 수 있습니다.</p><button class="bg-indigo-600 text-white rounded-lg px-4 py-2 font-bold">연구 계획 저장</button></form>
          <h3 class="font-bold text-sm mt-6">연구 참여 확인</h3><p class="text-xs text-slate-500 mt-2">학생·보호자 동의 등 정한 연구 절차를 확인한 학생만 선택합니다. 참여하지 않아도 수업·과제·보상은 그대로 이용합니다.</p><div id="researchParticipationRows" class="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-3"></div><button onclick="saveResearchParticipation()" class="mt-3 border rounded-lg px-4 py-2 font-bold text-sm">참여 확인 저장</button>
        </details>
        <details class="bg-white border rounded-2xl p-5"><summary class="font-extrabold cursor-pointer">2. 연구 설문·척도 버전 관리</summary>
          <p class="text-sm text-slate-600 mt-3">사용할 척도는 아직 확정하지 않았습니다. 중학생에게 적합한 도구의 출처·사용 조건·채점 지침을 확인하고 등록해 주세요. 현재 자동 채점은 같은 응답 범위 안에서 하위영역별 문항 평균과 역채점을 지원합니다. 원 척도와 채점법이 일치할 때만 배포합니다.</p>
          <div id="researchInstrumentList" class="space-y-3 mt-4"></div>
          <form id="researchInstrumentForm" onsubmit="registerResearchInstrument(event)" class="space-y-3 border-t mt-5 pt-5">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3"><label class="text-sm font-bold">측정 영역<select name="kind" class="block w-full border rounded-lg p-2 mt-1"><option value="selfEfficacy">수학 자기효능감</option><option value="motivation">학습동기</option></select></label><label class="text-sm font-bold">척도 이름<input name="title" required maxlength="200" class="block w-full border rounded-lg p-2 mt-1"></label><label class="text-sm font-bold">버전<input name="version" required placeholder="예: 한국어판 v1" class="block w-full border rounded-lg p-2 mt-1"></label><label class="text-sm font-bold">출처·번안·사용 조건<input name="source" required class="block w-full border rounded-lg p-2 mt-1"></label></div>
            <div class="flex gap-4"><label class="text-sm font-bold">응답 최솟값<input name="min" required type="number" min="0" max="9" value="1" class="block w-24 border rounded-lg p-2 mt-1"></label><label class="text-sm font-bold">응답 최댓값<input name="max" required type="number" min="1" max="10" value="5" class="block w-24 border rounded-lg p-2 mt-1"></label></div>
            <label class="block text-sm font-bold">선택지 설명 — 최솟값부터 한 줄에 하나씩<textarea name="options" required rows="4" placeholder="선택한 원 척도의 응답 선택지를 순서대로 입력" class="block w-full border rounded-lg p-2 mt-1"></textarea></label>
            <label class="block text-sm font-bold">문항 — 한 줄에 ‘하위영역 | 정 또는 역 | 문항 내용’<textarea name="items" required rows="6" placeholder="원 척도의 하위영역, 역채점 여부, 문항을 그대로 등록" class="block w-full border rounded-lg p-2 mt-1"></textarea></label>
            <label class="flex gap-2 items-start text-sm"><input name="scoringConfirmed" type="checkbox" class="mt-1">원 도구의 사용 조건과 채점 지침을 확인했으며, 등록한 응답 범위·역채점·하위영역 평균 방식이 일치합니다.</label><button class="bg-indigo-600 text-white font-bold rounded-lg px-4 py-2">새 척도 버전 등록</button><p class="text-xs text-slate-500">측정에 사용한 버전은 수정하지 않습니다. 문항을 바꾸면 새 버전으로 등록하고 결과를 별도로 표시합니다.</p>
          </form>
        </details>
        <details class="bg-white border rounded-2xl p-5"><summary class="font-extrabold cursor-pointer">3. 측정 시점·배포·마감</summary><div id="researchWaveList" class="space-y-3 mt-4"></div>
          <form onsubmit="openResearchWave(event)" class="space-y-3 border-t mt-5 pt-5"><label class="block text-sm font-bold">측정 이름<input name="label" required placeholder="예: 최초 측정 / 중1 1학기 말" class="block w-full border rounded-lg p-2 mt-1"></label><label class="block text-sm font-bold">측정 기준일<input name="date" type="date" required class="block border rounded-lg p-2 mt-1"></label><fieldset><legend class="font-bold text-sm">사용할 척도</legend><div id="researchWaveInstruments"></div></fieldset><fieldset><legend class="font-bold text-sm mt-3">참여 학생</legend><div id="researchWaveParticipants" class="grid grid-cols-1 sm:grid-cols-2"></div></fieldset><button class="bg-indigo-600 text-white font-bold rounded-lg px-4 py-2">측정 시작·학생에게 배포</button></form>
        </details>
        <section class="bg-white border rounded-2xl p-5"><div class="flex flex-wrap gap-3 items-center justify-between"><h3 class="text-lg font-extrabold">학생별 변화·학습 행동</h3><select id="researchStudentSelect" onchange="renderResearchAnalysis()" class="border rounded-lg p-2 text-sm" aria-label="연구 결과를 볼 학생"></select></div><p class="text-xs text-slate-500 mt-3">같은 척도·버전의 하위영역끼리만 연결합니다. 미응답은 0점으로 처리하지 않으며, 그래프의 빈 시점도 연결하지 않습니다.</p><div id="researchIndividualResults" class="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4"></div><h4 class="font-bold mt-6">학습 행동 — 현재 학년별 기록 기준</h4><p class="text-xs text-slate-500 mt-2">제출률은 전체 과제 중 제출한 비율입니다. 피드백 후 수정률은 현재 남아 있는 피드백을 받은 과제 중 이후 재제출한 비율입니다. 문항 점수나 도장 수와 합산하지 않습니다. 측정 시작 시의 행동 현황도 별도로 저장합니다.</p><div class="overflow-x-auto"><table class="w-full text-sm text-left mt-3"><thead><tr><th class="p-2">학년</th><th class="p-2">제출률</th><th class="p-2">피드백 후 수정률</th><th class="p-2">재제출 과제</th></tr></thead><tbody id="researchBehaviorResults"></tbody></table></div></section>
        <section class="bg-white border rounded-2xl p-5"><div class="flex flex-wrap gap-3 justify-between"><h3 class="text-lg font-extrabold">연구 참여 집단 변화</h3><button onclick="exportResearchCSV()" class="border rounded-lg px-3 py-2 font-bold text-sm">반복 측정 결과 CSV</button></div><p class="text-xs text-slate-500 mt-3">전체 연구 참여 학생 기준입니다. 평균 옆에 완료 응답 인원을 표시합니다. 변화량은 직전 시점과 같은 척도에 모두 응답한 학생만 짝지어 계산합니다. 상승이 곧 앱의 인과적 효과를 뜻하지 않습니다.</p><div class="overflow-x-auto mt-4"><table class="w-full text-sm text-left"><thead><tr><th class="p-2">척도·하위영역</th><th class="p-2">측정 시점</th><th class="p-2">응답/대상</th><th class="p-2">평균</th><th class="p-2">최솟값~최댓값</th><th class="p-2">직전 시점 대비 변화 (짝지은 인원)</th></tr></thead><tbody id="researchClassResults"></tbody></table></div></section>
        <details class="bg-white border rounded-2xl p-5"><summary class="font-extrabold cursor-pointer">학생 경험·교사 관찰 기록</summary><p class="text-sm text-slate-500 mt-3">도움이 된 점, 부담이 된 점, 보상이 없어도 이어가고 싶은지 등을 면담·자유응답으로 기록하세요. 실제 기록만 저장하며 점수로 자동 변환하지 않습니다.</p><form onsubmit="addResearchObservation(event)" class="space-y-3 mt-4"><div class="flex flex-wrap gap-3"><select id="observationStudent" name="studentUuid" class="border rounded-lg p-2" aria-label="면담 기록 대상 학생"></select><select name="kind" class="border rounded-lg p-2" aria-label="기록 종류"><option>학생 면담</option><option>학생 자유응답</option><option>교사 관찰</option></select><input name="date" type="date" required class="border rounded-lg p-2" aria-label="면담·관찰 날짜"></div><textarea name="content" required rows="3" class="block w-full border rounded-lg p-2" placeholder="실제 학생의 말과 교사의 해석을 구분하여 적어 주세요."></textarea><button class="border rounded-lg px-4 py-2 font-bold text-sm">기록 저장</button></form><p class="text-xs text-slate-500 mt-4">아래에는 위 학생별 변화 메뉴에서 선택한 학생의 기록이 표시됩니다.</p><div id="researchObservationList" class="space-y-3 mt-3"></div></details>
      </div>
    </section>'''
teacher=teacher.replace('<button onclick="exportResearchCSV()"', '<button onclick="exportResearchRawCSV()" class="border rounded-lg px-3 py-2 font-bold text-sm">문항별 원응답 CSV</button><button onclick="exportResearchCSV()"')
teacher=teacher.replace('''<tbody id="researchBehaviorResults"></tbody></table></div></section>''', '''<tbody id="researchBehaviorResults"></tbody></table></div><h4 class="font-bold mt-5">측정 시작 시의 행동 기록</h4><p class="text-xs text-slate-500 mt-2">각 시점을 열 때 저장한 현황입니다. 이후 과제가 추가되거나 학생이 진급해도 이 기록은 바뀌지 않습니다.</p><div class="overflow-x-auto"><table class="w-full text-sm text-left mt-3"><thead><tr><th class="p-2">측정 시점</th><th class="p-2">제출/대상 과제</th><th class="p-2">수정/피드백 과제</th><th class="p-2">재제출 과제</th></tr></thead><tbody id="researchBehaviorSnapshots"></tbody></table></div></section>''')
s=s[:start]+teacher+s[end:]
# Add a separate student research area; it is never counted as an assignment.
pos=s.index('          </nav>',s.index('id="tasksCategory"'))
s=s[:pos]+'''            <button onclick="showStudentResearch()" class="w-full text-left border border-indigo-100 bg-indigo-50 rounded-xl p-4"><span class="font-extrabold text-sm">3. 연구 설문</span><span class="block text-xs text-slate-500 mt-2">나의 수학 학습 경험 돌아보기</span></button>
'''+s[pos:]
pos=s.index('          <section id="studentTasksPanel"')
s=s[:pos]+'''          <section id="studentResearchPanel" hidden class="bg-white border rounded-2xl p-5 sm:p-7"><h3 id="studentResearchTitle" tabindex="-1" class="text-xl font-extrabold">나의 수학 학습 경험 · 연구 설문</h3><p class="text-sm text-slate-500 mt-3">정답이 없는 설문이에요. 지금 느끼는 대로 답해 주세요. 참여하지 않아도 과제 성취율·배지·도장에 영향이 없어요.</p><div id="studentResearchList" class="space-y-4 mt-5"></div></section>
'''+s[pos:]
s=s.replace("    function showStudentTasks() {", "    function showStudentTasks() {\n      document.getElementById('studentResearchPanel').hidden=true;")
s=s.replace("      renderStudentTasks();\n    }\n\n    function selectStage", "      renderStudentTasks();\n      renderStudentResearch();\n    }\n\n    function selectStage")
s=s.replace("      document.getElementById('studentTasksPanel').classList.add('hidden');\n      document.getElementById('tasksCategory').setAttribute", "      document.getElementById('studentTasksPanel').classList.add('hidden');\n      document.getElementById('studentResearchPanel').hidden=true;\n      document.getElementById('tasksCategory').setAttribute")
s=s.replace('<section id="teacherView"', '<section id="adventureView" hidden class="space-y-4"></section>\n    <section id="teacherView"',1)
s=s.replace('<a id="adventureCategory" target="_blank" rel="noopener noreferrer"', '<button type="button" id="adventureCategory"')
anchor_start=s.index('<button type="button" id="adventureCategory"')
anchor_end=s.index('</a>',anchor_start)
s=s[:anchor_end]+'</button>'+s[anchor_end+len('</a>'):]
s=s.replace('열린 단계를 누르면 Tally 방탈출로 이동합니다. 앞 단계를 완료하면 다음 단계가 열립니다.', '1~10탄 모두 앱 안에서 도전해요. 앞 단계를 완료하면 다음 탄이 열려요.')
s=s.replace('    .badge-glow {', '''    .game-paper { background:#fff; border:1px solid #e2e8f0; border-radius:24px; padding:clamp(20px,4vw,36px); box-shadow:0 12px 30px #0f172a08; margin-top:20px; }
    .game-primary { background:#4f46e5; color:white; padding:13px 22px; border-radius:12px; font-weight:800; font-size:14px; }
    .game-primary:hover { background:#4338ca; }
    .game-primary:disabled { opacity:.55; cursor:wait; }
    .game-problem { font-size:clamp(17px,2.4vw,21px); line-height:1.95; font-weight:600; color:#334155; letter-spacing:.01em; }
    #adventureView button:focus-visible, #adventureView summary:focus-visible { outline:3px solid #a5b4fc; outline-offset:3px; }
    @media(prefers-reduced-motion:reduce) { #adventureView * { transition:none!important; } }
    .badge-glow {''',1)
# A bright, personal place and a separate mini-expedition collection.
pos=s.index('      <section class="bg-white border border-slate-200 rounded-2xl p-4" aria-label="나의 수학 성장 여권">')
s=s[:pos]+'''      <section id="hideoutSection" class="bg-white border border-slate-200 rounded-3xl p-4 sm:p-6" aria-label="나의 수학 아지트"></section>
'''+s[pos:]
pos=s.index('      <div class="grid grid-cols-1 lg:grid-cols-[300px_1fr]')
s=s[:pos]+'''      <section id="miniExplorationSection" class="bg-white border border-slate-200 rounded-3xl p-5 sm:p-6" aria-label="작은 탐험 지도"><div class="flex flex-wrap justify-between gap-3"><div><p class="text-xs font-black text-sky-700 tracking-widest">LITTLE EXPEDITIONS</p><h2 id="miniMapHeading" class="text-xl font-extrabold mt-2">수업 속 작은 탐험</h2></div><p class="text-sm text-slate-500 max-w-md">작은 탐험 1개 = 5단계 = 완성 배지 1개. 마지막 선택 도전은 배지의 조건이 아니에요.</p></div><div id="miniRegionFilters" class="flex flex-wrap gap-2 mt-5"></div><div id="miniTopicCards" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-5"></div><p id="miniCatalogNotice" class="text-sm text-slate-500 mt-4"></p></section>
      <details id="miniBadgeDetails" class="bg-white border border-slate-200 rounded-2xl p-5"><summary id="miniBadgeTitle" class="font-bold cursor-pointer">작은 탐험 배지 도감</summary><p class="text-sm text-slate-500 mt-3">단계마다 배지를 주지 않아요. 탐험 하나를 마치면 주제가 담긴 배지 하나를 모아요.</p><div id="miniBadgeCollection" class="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-8 gap-3 mt-4"></div></details>
'''+s[pos:]
s=s.replace('<section id="adventureView" hidden', '<section id="miniView" hidden class="space-y-4"></section><section id="adventureView" hidden',1)
s=s.replace("      renderStudentResearch();\n    }\n\n    function selectStage", "      renderStudentResearch();\n      renderMyHideout();\n      renderBadgeGallery();\n      renderMiniCatalog();\n    }\n\n    function selectStage")
s=s.replace('나의 수학 배지 컬렉션','나의 대탐험 배지 컬렉션')
s=s.replace('어드벤처 맵 10단계를 완료하면 단계마다 배지 1개를 얻어요. 과제 제출로는 배지가 지급되지 않아요.', '선택한 학년의 탐험을 마치면 완성 배지를 모을 수 있어요. 작은 탐험의 각 단계에는 진행 표시만 남아요.')
s=s.replace('🎨 나의 프로필 꾸미기','💬 선생님 피드백').replace('중1~중3 성장 도장을 모아 원하는 프로필 테두리를 골라 보세요.','학습 과정에서 받은 피드백을 확인하고 다시 도전해 보세요.')
s=s.replace('id="profileRewardOptions" class=', 'id="profileRewardOptions" hidden class=')
s=s.replace('선택 학년 배지:', '나의 완성 배지:')
s=s.replace(''' / <span id="gradeBadgeTotal">10</span>개''','''<span id="badgeCapacity"> / <span id="gradeBadgeTotal">50</span>개</span>''')
s=s.replace('<body class=', '<body data-mode="student" class=',1)
s=s.replace('record?.clearedStages.length || 0', '(record?.clearedStages.length || 0) + (record?.miniBadges?.length || 0)')
s=s.replace('sum + r.clearedStages.length, 0', 'sum + r.clearedStages.length + (r.miniBadges?.length || 0), 0')
s=s.replace('  </style>', '''
    body { background:#f5f8fb; }
    body:not([data-mode="teacher"]) #studentHeader { background:#fff; color:#334155; border-bottom:1px solid #e2e8f0; box-shadow:0 2px 12px #33415506; }
    body:not([data-mode="teacher"]) #studentHeader .text-amber-400 { color:#435bb4; }
    body:not([data-mode="teacher"]) #studentHeader .bg-indigo-700:not(button) { background:#eef2ff; color:#6474ad; }
    body:not([data-mode="teacher"]) #currentModeText { color:#475569; }
    body:not([data-mode="teacher"]) #currentModeText + button { color:#fff; }
    #studentView .from-indigo-600 { background-image:none; background:#eef6ff; color:#1e3a5f; border:1px solid #dbeafe; box-shadow:none; }
    #studentView .from-indigo-600 .text-indigo-100 { color:#526b86; }
    #personalAchievementBar { background:#78a6d3!important; }
    #personalAchievementProgress { background:#d9e9f6!important; }
    .game-hero { color:#334155!important; border:1px solid #e2e8f0; }
    .game-hero [class*="bg-black"] { background:#ffffff90; }
    .game-hero [role="progressbar"] { background:#ffffffa8!important; }
    .game-hero [role="progressbar"]>div { background:#7c98bb!important; }
    .room-primary { background:#3e6b96; color:white; border-radius:12px; padding:10px 16px; font-size:13px; font-weight:800; }
    .room-primary:hover { background:#315a82; }
    .room-primary:disabled { opacity:.5; }
    .room-stat { padding:14px 16px; border:1px solid #e8edf3; background:#f9fbfd; border-radius:16px; }
    .room-stat span,.room-stat small { display:block; color:#64748b; font-size:11px; }
    .room-stat strong { display:block; margin:5px 0; color:#334155; font-size:21px; font-weight:800; }
    .room-scene { overflow:hidden; border:1px solid #e2e8f0; border-radius:22px; background:var(--room-wall); max-width:920px; margin:auto; }
    .room-wall { height:150px; position:relative; background:linear-gradient(115deg,var(--room-wall),#ffffffaa); border-bottom:7px solid var(--room-trim); }
    .room-window { position:absolute; left:7%; top:20px; width:85px; height:95px; background:linear-gradient(#cfe7f7,#f5fbff); border:7px solid white; border-radius:35px 35px 8px 8px; box-shadow:0 2px 8px #64748b0c; }
    .room-window:before,.room-window:after { content:''; position:absolute; background:white; }
    .room-window:before { width:4px; height:100%; left:50%; }
    .room-window:after { height:4px; width:100%; top:50%; }
    .room-pins { position:absolute; left:35%; right:7%; top:25px; display:flex; gap:14px; justify-content:center; }
    .room-pin { display:flex; justify-content:center; align-items:center; width:82px; height:82px; background:#fffefb; border:5px solid #e1d3bf; border-radius:10px; box-shadow:0 3px 0 #c3b39c22; }
    .room-pin:hover { border-color:#b7cbd9; }
    .room-wall-note { position:absolute; left:35%; right:7%; bottom:6px; text-align:center; color:#7b8792; font-size:10px; }
    .room-floor { min-height:260px; padding:10px 5% 10px; }
    .room-floor-wood { background:repeating-linear-gradient(0deg,#f0e6d8,#f0e6d8 41px,#e3d6c5 42px,#f0e6d8 43px); }
    .room-floor-cream { background:#f6efe1; }
    .room-floor-tiles { background-color:#f1f2ee; background-image:linear-gradient(45deg,#e0e8e3 25%,transparent 25%),linear-gradient(-45deg,#e0e8e3 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#e0e8e3 75%),linear-gradient(-45deg,transparent 75%,#e0e8e3 75%); background-size:60px 60px; background-position:0 0,0 30px,30px -30px,-30px 0; }
    .room-floor-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); grid-template-rows:repeat(3,82px); max-width:740px; margin:auto; gap:0 10px; }
    .room-cell { position:relative; display:flex; align-items:center; justify-content:center; min-width:0; border-radius:14px; border:1px solid transparent; }
    .room-edit-cell { border:1px dashed #abafa780; background:#ffffff30; }
    .room-edit-cell:hover { background:#ffffffb0; border-color:#6a9dbd; }
    .room-furniture { width:100%; height:105px; max-width:150px; overflow:visible; }
    .student-character { flex-shrink:0; max-width:100%; overflow:visible; }
    .room-cell .student-character { pointer-events:none; }
    .character-card { border:1px solid #e2e8f0; border-radius:18px; padding:16px; background:#f8fbff; }
    .character-hats { display:grid; grid-template-columns:repeat(auto-fit,minmax(95px,1fr)); gap:8px; }
    .character-hat { display:flex; flex-direction:column; align-items:center; justify-content:center; background:white; border:1px solid #dce6ed; border-radius:14px; padding:10px 6px; }
    .character-hat span { font-size:11px; color:#475569; font-weight:700; margin-top:7px; }
    .character-hat small { font-size:9px; color:#64748b; margin-top:4px; }
    .character-hat:disabled { opacity:.5; }
    .room-item { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:8px 5px; border:1px solid #e2e8f0; border-radius:14px; background:#fff; min-height:125px; }
    .room-item .room-furniture { height:63px; width:85px; }
    .room-item span { font-size:11px; font-weight:700; color:#475569; }
    .room-item small { font-size:9px; color:#94a3b8; margin-top:4px; }
    .room-item-selected { border-color:#7cabc7; box-shadow:0 0 0 2px #cfe6f3; }
    .topic-badge { display:flex; flex-direction:column; align-items:center; justify-content:flex-start; min-width:0; text-align:center; border-radius:16px; padding:7px 3px; }
    .topic-badge svg { max-width:100%; }
    .topic-badge span { display:block; font-size:10px; font-weight:800; color:#475569; margin-top:5px; line-height:1.4; }
    .topic-badge small { font-size:9px; color:#94a3b8; margin-top:3px; }
    .badge-locked { opacity:.65; }
    .mini-topic-card { padding:20px; border-radius:20px; border:1px solid #e2e8f0; background:linear-gradient(135deg,#fff,#f7fbff); }
    .mini-topic-card:disabled { background:#fafbfc; }
    .mini-topic-card:not(:disabled):hover { border-color:#93bdd4; box-shadow:0 5px 20px #64748b09; }
    #miniExplorationSection { scroll-margin-top:85px; }
    @media(max-width:520px) { .room-wall { height:120px; } .room-window { width:57px; height:76px; left:5%; top:15px; } .room-pins { left:28%; right:4%; gap:6px; top:21px; } .room-pin { width:58px; height:65px; border-width:4px; } .room-pin svg { width:44px; height:49px; } .room-wall-note { left:28%; font-size:8px; } .room-floor-grid { grid-template-rows:repeat(3,70px); gap:0 3px; } .room-floor { min-height:225px; padding:5px 3%; } .room-furniture { height:78px; } }
  </style>''',1)
s=s.replace('  </style>', '''
    .student-main-nav { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }
    .student-main-nav button { display:flex; align-items:center; justify-content:center; gap:10px; padding:18px 12px; border-radius:18px; border:1px solid #dfe8f0; background:white; color:#607184; font-size:18px; font-weight:800; }
    .student-main-nav button span { font-size:11px; color:#97a9b9; }
    .student-main-nav button[aria-pressed="true"] { color:#285778; background:#edf6fd; border-color:#a7cce6; box-shadow:inset 0 -3px 0 #a7cce6; }
    #hideoutSection { margin-top:0; }
    #hideoutSection .room-scene { margin-top:20px; }
    .student-collection { background:white; border:1px solid #e2e8f0; border-radius:22px; padding:20px; }
    .student-collection summary { cursor:pointer; font-size:17px; font-weight:800; color:#334155; }
    .student-collection summary small { font-size:12px; font-weight:400; color:#7b8c9c; margin-left:12px; }
    .collection-tabs { display:flex; flex-wrap:wrap; gap:8px; margin:20px 0; padding-bottom:18px; border-bottom:1px solid #edf1f5; }
    .collection-tabs button { padding:10px 15px; border:1px solid #e2e8f0; border-radius:12px; font-size:13px; font-weight:700; color:#64748b; }
    .collection-tabs button[aria-pressed="true"] { background:#edf6fd; border-color:#b8d7eb; color:#285778; }
    #miniBadgeDetails { padding:0; border:0; }
    .learning-categories { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; }
    .learning-category { display:flex; align-items:flex-start; gap:10px; text-align:left; padding:19px 16px; border:1px solid #e2e8f0; border-radius:18px; background:white; color:#334155; }
    .category-number { display:none; }
    .learning-category strong { display:block; font-size:14px; line-height:1.6; }
    .learning-category small { display:block; font-size:11px; line-height:1.7; margin-top:8px; color:#7c8a99; }
    .learning-category[aria-pressed="true"] { border-color:#8db8d7; background:#eff7fc; box-shadow:inset 0 3px 0 #8db8d7; }
    .category-count { margin-left:auto; border-radius:8px; padding:2px 7px; background:#e6eef8; color:#4c7296; font-size:11px; font-weight:800; }
    .learning-paper { background:white; border:1px solid #e2e8f0; border-radius:24px; padding:24px; }
    #studentTasksPanel,#studentResearchPanel,#miniExplorationSection { border-radius:24px; }
    #studentTasksPanel #personalAchievementProgress { background:#dceaf5; }
    #studentTasksPanel #personalAchievementBar { background:#709dbd; }
    #studentTasksPanel .from-indigo-600 { margin:20px 0; }
    #missionMapGrid button { min-height:116px; padding:20px; border-radius:18px; font-size:13px; line-height:1.7; }
    #missionMapGrid button:not(:disabled):hover { border-color:#91b8d6; box-shadow:0 4px 15px #64748b10; }
    @media(max-width:760px) { .learning-categories { grid-template-columns:repeat(2,minmax(0,1fr)); gap:9px; } .student-main-nav button { font-size:15px; padding:15px 7px; } .learning-category { padding:14px 12px; } .student-collection summary small { display:block; margin:7px 0 0 19px; } }
  </style>''',1)
import re
s=re.sub(r'<textarea id="miniContentEditor".*?</button>', '<div id="miniContentManager"></div>',s,count=1,flags=re.S)
s=s.replace('우선 소수와 합성수 작은 탐험을 제공합니다.', '중1 작은 탐험 40개, 기본 600문항과 선택 도전 40문항을 관리합니다.')
s=s.replace('나머지 39개 주제는 추가 예정으로 표시합니다.', '모든 주제를 앱 안에서 풀 수 있습니다.')
s=s.replace('아래 원고에서 text(문제), options(선택지), answer(정답), hint(힌트), explanation(해설)을 편집할 수 있습니다. 선택형 정답은 1부터 시작하는 선택지 번호이며, 복수 선택형은 번호 배열입니다. 단계 수·문항 ID·형식은 유지해 주세요.', '탐험과 문항을 선택하여 문제·정답·선택지·힌트·해설을 수정하세요.')
s=s.replace('<div id="teacherLessonArea" class="space-y-6">','<div id="teacherLessonArea" class="space-y-6"><section id="teacherStudentPolicy" class="learning-paper"></section>')
s=s.replace('<div id="researchObservationList" class="space-y-3 mt-3"></div>', '<div id="researchObservationList" class="space-y-3 mt-3"></div><div id="teacherReflectionList" class="mt-5"></div>')
s=s.replace('확인 완료','과제 통과').replace('확인 대기','검토 대기').replace('선생님이 확인하면','선생님이 통과 처리하면')
s=s.replace('과제 과제 통과','과제 통과').replace('과제 통과 과제','통과한 과제')
s=s.replace('<label class="text-sm font-bold">어드벤처 배지 모양', '<label hidden class="text-sm font-bold">어드벤처 배지 모양')
s=s.replace('배우고 도전하며 모으는 나의 수학 배지', '배우고 도전하며 나의 성장을 돌아봐요')
s=s.replace('  </style>', Path('math_quest_growth.css').read_text(encoding='utf-8')+'\n  </style>',1)
s=organise_student_layout(s)
s=s.replace('      renderMiniCatalog();\n    }\n\n    function selectStage','      renderMiniCatalog();\n      syncStudentLayout();\n    }\n\n    function selectStage')
p.write_text(s,encoding='utf-8')
print('Built teaching and affective-research workspaces')
