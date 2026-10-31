"""Organise existing student widgets without duplicating their IDs or records."""
import re


def element(source, marker):
    hit=re.search(r'<([a-z][\w-]*)\b[^>]*'+marker+r'[^>]*>',source)
    if not hit:raise ValueError('Missing student widget: '+marker)
    tag=hit.group(1);depth=0
    for token in re.finditer(r'</?'+tag+r'\b[^>]*>',source[hit.start():]):
        depth+=-1 if token.group().startswith('</') else 1
        if depth==0:return source[hit.start():hit.start()+token.end()]
    raise ValueError('Unclosed student widget: '+marker)


def organise_student_layout(source):
    student=element(source,r'id="studentView"')
    header=student[:student.index('<!-- 학생 간편')]+'''<section class="growth-passport" aria-label="나의 수학 성장 여권"><div class="passport-heading"><div id="stProfileSymbol" class="passport-character"></div><div><p class="passport-eyebrow">MY MATH GROWTH</p><h1 class="text-2xl font-extrabold text-slate-800">나의 수학 성장 여권</h1><p class="text-sm text-slate-600 mt-2">배우고 도전하며 나의 변화를 돌아봐요.</p><div class="flex flex-wrap items-center gap-2 mt-3"><span id="stGradeBadge" class="text-xs font-bold text-sky-700"></span><h2 id="stNameDisplay" data-copy-exclude class="font-extrabold"></h2><span id="stClassDisplay" data-copy-exclude class="text-xs text-slate-500"></span></div></div><div class="passport-math" aria-hidden="true">＋<br>π × √</div></div><div id="passportMetrics" class="passport-metrics"></div><details id="passportPreviousGrades" hidden class="mt-4"><summary class="text-sm font-bold text-sky-800 cursor-pointer">이전 학년 기록 보기</summary><div id="passportHistory" class="mt-3 space-y-3"></div></details><span hidden id="stBadgeCount"></span><span hidden id="badgeCapacity"><span id="gradeBadgeTotal"></span></span></section>'''
    room=element(student,r'id="hideoutSection"')
    achievement=element(student,r'class="bg-gradient-to-br from-indigo-600[^\"]*"')
    tasks=element(student,r'id="studentTasksPanel"')
    tasks=tasks.replace('<div id="studentTaskList"',achievement+'<div class="rounded-xl bg-slate-50 p-4 my-4"><h3 class="text-sm font-bold">선생님 피드백</h3><p id="studentFeedbackMessage" data-copy-exclude class="text-sm text-slate-600 mt-2 whitespace-pre-wrap"></p></div><div id="studentTaskList"')
    mini=element(student,r'id="miniExplorationSection"')
    mini_badges=element(student,r'id="miniBadgeDetails"').replace('<details','<section',1).replace('<summary','<h3',1).replace('</summary>','</h3>').replace('</details>','</section>')+'<p id="miniCollectionEmpty" hidden class="text-sm text-slate-500"></p>'
    badges=element(student,r'id="studentBadgeRow"')
    research=element(student,r'id="studentResearchPanel"')
    research=research.replace('나의 수학 학습 경험 · 연구 설문','이번 성장 설문')
    growth_intro='''<div class="growth-purpose"><p class="passport-eyebrow">REFLECT & GROW</p><h2 class="text-2xl font-extrabold mt-2">나의 성장 돌아보기</h2><p class="text-sm leading-7 text-slate-600 mt-3">수학을 배우는 나의 마음은 어떻게 달라지고 있을까요? 자신감·흥미·어려움을 솔직하게 돌아봐요. 좋아진 점도, 그대로인 점도, 어려워진 점도 모두 소중한 기록이에요.</p><p class="text-xs text-slate-500 mt-3">정답은 없어요. 참여와 응답 내용은 성적·과제 성취율·배지·도장에 영향을 주지 않아요. 내 응답은 나와 담당 교사가 볼 수 있으며, 교사는 연구 참여 안내와 확인 절차에 따라 연구에 활용합니다.</p></div>'''
    reflections='''<section class="learning-paper"><h3 class="font-extrabold text-lg">나의 한마디</h3><p class="text-sm text-slate-500 mt-2">도움이 된 점, 부담스러웠던 점, 다음에 해 보고 싶은 것을 남겨요. 연구 설문 점수와 별도로 보관합니다.</p><form onsubmit="saveMyReflection(event,this)" class="mt-4"><textarea name="content" required maxlength="2000" rows="3" class="w-full border rounded-xl p-3" aria-label="나의 돌아보기 내용"></textarea><button class="room-primary mt-3">돌아보기 기록 저장</button></form><div id="myReflectionHistory" class="space-y-3 mt-4"></div></section>'''
    collection=f'''<details id="studentCollection" class="student-collection"><summary><span>나의 수집함</span><small>배지와 성장 도장을 한곳에서 보기</small></summary><div class="collection-tabs" role="group" aria-label="수집함 종류"><button id="collection-big" onclick="showCollection('big')">대탐험 배지</button><button id="collection-mini" onclick="showCollection('mini')">작은 탐험 배지</button><button id="collection-stamps" onclick="showCollection('stamps')">성장 도장</button></div><div id="collectionPanel-big"><h3 class="font-extrabold">중<span id="collectionGradeLabel"></span> · 대탐험 배지</h3>{badges}</div><div id="collectionPanel-mini" hidden>{mini_badges}</div><div id="collectionPanel-stamps" hidden><h3 class="font-extrabold">나의 성장 도장</h3><p id="growthStampSummary" class="text-sm text-emerald-800 mt-2"></p><div id="growthStampList" class="flex flex-wrap gap-2 mt-3"></div><p class="text-xs text-slate-500 mt-4">과제의 첫 확인 완료와 피드백을 반영한 재도전을 기록해요. 도장은 학년이 바뀌어도 남아요.</p></div><div id="profileRewardOptions" hidden></div></details>'''
    nav=''.join(f'''<button id="{id}" onclick="showLearningCategory('{key}')" class="learning-category" aria-controls="{panel}" aria-pressed="false"><span class="category-number">{number:02}</span><span><strong id="{title_id}">{number}. {title}</strong><small>{description}</small></span>{extra}</button>''' for number,key,id,panel,title_id,title,description,extra in [
        (1,'tasks','tasksCategory','studentTasksPanel','tasksCategoryTitle','나의 과제','확인하고 제출하기','<span id="taskCount" class="category-count"></span>'),
        (2,'mini','miniCategory','miniExplorationSection','miniCategoryTitle','수업 속 작은 탐험','수업 주제로 가볍게 도전하기',''),
        (3,'adventure','adventureCategory','studentAdventurePanel','adventureCategoryTitle','수학 방탈출 어드벤처','이야기 속 수학 문제 해결하기','<span id="adventureNextLabel" hidden></span>')])
    nav=nav.replace("showLearningCategory('research')",'showStudentResearch()')
    adventure='''<section id="studentAdventurePanel" hidden class="learning-paper" aria-labelledby="adventureMapTitle"><div class="learning-heading"><p class="text-xs font-black tracking-widest text-sky-700">MATH ESCAPE ADVENTURE</p><h2 id="adventureMapTitle" tabindex="-1" class="text-xl font-extrabold mt-2">수학 방탈출 어드벤처</h2><p class="text-sm text-slate-500 mt-3">이야기 속 10개의 장치를 해결하며 탐험해요. 한 탄을 완성하면 배지 하나를 받아요.</p></div><div id="missionMapGrid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-6"></div></section>'''
    layout=header+f'''<nav class="student-main-nav" aria-label="학생 화면 주요 영역"><button id="studentArea-hideout" onclick="showStudentArea('hideout')" aria-pressed="true"><span>01</span> 나의 수학 아지트</button><button id="studentArea-learning" onclick="showStudentArea('learning')" aria-pressed="false"><span>02</span> 나의 학습</button><button id="studentArea-growth" onclick="showStudentResearch()" aria-pressed="false"><span>03</span> 나의 성장 돌아보기</button></nav><div id="studentHideoutArea" class="space-y-5">{room}{collection}</div><section id="studentLearningArea" hidden class="space-y-5" aria-label="나의 학습"><div><p class="text-xs font-black text-sky-700 tracking-widest">MY LEARNING</p><h2 class="text-2xl font-extrabold mt-2">나의 학습</h2><p class="text-sm text-slate-500 mt-2">내 속도로 배우고 도전하고 다시 해결해요.</p></div><nav class="learning-categories" aria-label="학습 카테고리">{nav}</nav>{tasks}{mini}{adventure}<div id="studentWelcome" hidden></div></section><section id="studentGrowthArea" hidden class="space-y-5" aria-label="나의 성장 돌아보기">{growth_intro}{research}{reflections}</section></section>'''
    return source.replace(student,layout,1)
