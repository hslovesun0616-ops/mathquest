// Growth passport, richer personal spaces, teacher actions, and editable mini lessons.
let outfitCatalog={},miniEditorDraft=null,miniEditorQuestion=0;
function renderGrowthPassport(){
  const st=students[currentStudentIndex];if(!st)return;const r=selectedRecord(),p=achievement(r,selectedLearningGrade),mini=(r.miniBadges||[]).length,big=(r.clearedStages||[]).length;
  document.getElementById('passportMetrics').innerHTML=[['교사 과제 통과',p.total?`${p.approved}/${p.total}개 · ${p.percent}%`:'과제 준비 중','교사가 부여한 과제만 계산해요'],['작은 탐험 완성',selectedMiniCatalog().length?mini+'개':'콘텐츠 준비 중','5단계 전체 완성으로 기록해요'],['방탈출 완성',selectedStages().length?big+'개':'콘텐츠 준비 중','이야기 한 탄의 완성을 기록해요']].map(([label,value,detail])=>`<div><span>${label}</span><strong>${value}</strong><small>${detail}</small></div>`).join('');
  const previous=Object.entries(st.gradeRecords||{}).filter(([g])=>Number(g)<selectedLearningGrade&&Number(g)<=st.grade).sort(([a],[b])=>Number(b)-Number(a));
  document.getElementById('passportPreviousGrades').hidden=!previous.length;
  document.getElementById('passportHistory').innerHTML=previous.map(([g,record])=>{const a=achievement(record,Number(g));return `<div class="passport-history"><strong>중${g}</strong><span>교사 과제 ${a.approved}/${a.total}개 통과 · 작은 탐험 ${(record.miniBadges||[]).length}개 · 방탈출 ${record.clearedStages.length}개 완성</span></div>`;}).join('');
}
async function changeStudentGrade(index,direction){
  if(!requireTeacher())return;
  try{const response=await api('/api/teacher/grade',{studentUuid:students[index].uuid,direction,version:remoteVersion});applyRemote(response);teacherRecordGrade=null;populateTeacherFilters();renderTeacherDashboard();renderTeacherManagement();alert(direction===1?'진급했습니다. 이전 학년 기록은 보존됩니다.':'진급을 취소했습니다. 모든 학년 기록과 꾸미기는 보존됩니다.');}catch(error){alert(error.message);}
}
async function promoteStudent(index){await changeStudentGrade(index,1);}
async function undoPromotion(index){await changeStudentGrade(index,-1);}
function submissionStatus(sub){return !sub?'미제출':sub.reviewStatus==='approved'?'과제 통과 · 성장 도장 기록':sub.reviewStatus==='revision_requested'?'보완 요청 · 피드백을 확인해 주세요':'제출 완료 · 교사 검토 대기';}
async function requestTaskRevision(index){
  if(!requireTeacher())return;const sub=teacherRecord().record.submissions[index];
  sub.teacherFeedback=document.getElementById('submissionFeedback-'+index).value.trim();
  if(!sub.teacherFeedback){alert('학생이 다시 도전할 수 있도록 보완할 내용을 적어 주세요.');return;}
  sub.reviewStatus='revision_requested';sub.reviewedAt=null;sub.feedbackRevision=sub.revision||0;sub.feedbackAt=new Date().toISOString();if(await persistLearning())renderTeacherDashboard();
}
async function saveMyReflection(event,form){
  event.preventDefault();if(!studentLoggedIn||teacherMode)return;
  try{applyRemote(await api('/api/research/reflect',{grade:selectedLearningGrade,content:form.elements.content.value}));form.reset();renderStudentResearch();}catch(error){alert(error.message);}
}
const priorStudentResearch=renderStudentResearch;
renderStudentResearch=function(){
  priorStudentResearch();const st=students[currentStudentIndex];if(!st)return;
  document.getElementById('myReflectionHistory').innerHTML=(researchState.reflections||[]).filter(r=>r.studentUuid===st.uuid&&r.grade===selectedLearningGrade).slice().reverse().map(r=>`<article class="border rounded-xl p-4"><p class="text-xs text-slate-500">${escapeHtml(r.at.slice(0,10))} · 중${r.grade}</p><p data-copy-exclude class="text-sm whitespace-pre-wrap mt-2">${escapeHtml(r.content)}</p></article>`).join('');
  const history=researchState.responses.filter(r=>r.studentUuid===st.uuid&&r.grade===selectedLearningGrade&&r.status==='completed');
  if(history.length)document.getElementById('studentResearchList').insertAdjacentHTML('beforeend','<h3 class="font-extrabold pt-4">지난 나의 응답 돌아보기</h3>'+history.map(r=>{const instrument=researchState.instruments.find(i=>i.id===r.instrumentId),wave=researchState.waves.find(w=>w.id===r.waveId);return `<details class="border rounded-xl p-4"><summary class="font-bold text-sm cursor-pointer">${escapeHtml(wave?.label||'지난 측정')} · ${escapeHtml(instrument?.title||'설문')}</summary><p class="text-xs text-slate-500 mt-3">좋아짐·유지·어려움 모두 기록으로 남겨요. 다른 척도의 점수는 합치지 않아요.</p>${(instrument?.items||[]).map(q=>`<p class="text-sm mt-3" data-copy-exclude>${escapeHtml(q.text)}<strong class="block text-sky-800 mt-1">${escapeHtml(instrument.options[r.answers[q.id]-instrument.min]||'응답 없음')}</strong></p>`).join('')}</details>`;}).join(''));
};
const priorCharacterArt=characterArt;
characterArt=function(c,size=110){
  let svg=priorCharacterArt(c,size);const color={sky:'#8fbddf',mint:'#8fc8ae',peach:'#edb49f',lavender:'#b9a4db',yellow:'#e6ce87'}[c.shirt]||'#8fbddf';
  const line=d=>`<path d="${d}" fill="none" stroke="#6c7d92" stroke-width="2" stroke-linecap="round"/>`;
  const body=(fill,hem=117)=>`<path d="M40 81 53 77H67L80 81 91 109 79 113 75 94 78 ${hem}H42L45 94 40 113 29 109Z" fill="${fill}"/>`;
  let clothes='';const id=c.outfit||'casual';
  if(id==='hoodie')clothes=body(color)+`<path d="M46 81Q60 94 74 81M50 101H70V111H50Z" fill="none" stroke="#f5f9fc" stroke-width="3"/>`+line('M55 85V95M65 85V95');
  if(id==='overalls'||id==='gardener')clothes=body(color)+`<path d="M45 81H51V96H69V81H75V128H43V96H45Z" fill="${id==='gardener'?'#92ae88':'#668eaf'}"/><rect x="52" y="98" width="16" height="14" rx="3" fill="#c3d6de"/>`;
  if(id==='tracksuit')clothes=body(color)+`<path d="M60 82V116M39 89 33 108M81 89 87 108" stroke="white" stroke-width="4"/>`;
  if(id==='cardigan'||id==='coat'||id==='labcoat')clothes=body(id==='coat'?'#b4a289':id==='labcoat'?'#fffdf7':color,id==='cardigan'?117:132)+`<path d="M50 79 60 98 70 79 64 84 60 90 56 84Z" fill="#f9f4df"/>`+line('M60 98V130M45 109H54M66 109H75')+`<circle cx="62" cy="105" r="1.5" fill="#697a8b"/>`;
  if(id==='robe')clothes=body(color,134)+`<path d="M42 134H78L74 103H46Z" fill="${color}"/><path d="m60 104 3 6 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1Z" fill="#f5df9e"/>`;
  if(id==='diving')clothes=body('#6c9fb4',126)+`<path d="M60 81V127M43 120H77" stroke="#e8ce7f" stroke-width="4"/><rect x="49" y="91" width="22" height="15" rx="4" fill="#c2dfe6"/>`;
  if(id==='space')clothes=body('#edf2f3',129)+`<rect x="47" y="91" width="26" height="22" rx="4" fill="#a1bed0"/><circle cx="54" cy="98" r="3" fill="#e1b27e"/><path d="M33 104H42M78 104H88M45 125H56M65 125H78" stroke="#8fa7c0" stroke-width="5"/>`;
  if(id==='apron')clothes=body(color)+`<path d="M51 81H69V94L76 126H44L51 94Z" fill="#f6e8cc"/><path d="M51 102H69V114H51Z" fill="#d6ba92"/>`;
  if(clothes)svg=svg.replace(/<path d="M39 82[^>]+\/>/,clothes);
  return svg;
};
const priorCharacterPanel=renderCharacterPanel;
renderCharacterPanel=function(room){
  let html=priorCharacterPanel(room);if(!characterEditing)return html;
  const outfits=outfitCatalog[students[currentStudentIndex].uuid]||[];
  const extra=`<h4 class="font-extrabold text-sm mt-5">나의 옷장</h4><p class="text-xs text-slate-500 mt-2">기본 옷 5종은 자유롭게, 테마 의상은 배지로, 연구 가운은 과제 통과 도장 3개로 열려요.</p><div class="character-hats mt-3">${outfits.map(o=>`<button ${o.unlocked?'':'disabled'} onclick="changeCharacter('outfit','${o.id}')" aria-pressed="${room.character.outfit===o.id}" class="character-hat ${room.character.outfit===o.id?'room-item-selected':''}">${characterArt({...room.character,outfit:o.id},52)}<span>${escapeHtml(o.title)}</span><small>${o.unlocked?'사용 가능':o.stamps?'과제 통과 도장 '+o.stamps+'개':o.unit+'지역 배지'}</small></button>`).join('')}</div>`;
  return html.slice(0,-6)+extra+'</div>';
};
const priorHideout=renderMyHideout;
const priorFurniture=furnitureArt;
furnitureArt=function(kind){
  const art={lamp:'<path d="M70 104H114M92 104V62L58 33" fill="none" stroke="#a49a86" stroke-width="6"/><path d="M36 28 68 18 86 48 44 62Z" fill="#e2c27f"/><ellipse cx="65" cy="67" rx="29" ry="9" fill="#f8edbd" opacity=".5"/>',cushion:'<rect x="38" y="35" width="88" height="68" rx="22" fill="#c3bbdf"/><path d="M48 45H116V92H48Z" fill="none" stroke="#eee8fb" stroke-dasharray="4 3"/><text x="82" y="81" font-size="32" text-anchor="middle" fill="#fffaf4">π</text>',shelf:'<rect x="28" y="18" width="108" height="94" rx="5" fill="#cfb38e"/><path d="M36 54H128M36 89H128" stroke="#ab8e6d" stroke-width="5"/><path d="M45 25V49M57 23V49M72 26V49M90 23V49M51 63V84M64 61V84M82 64V84M105 60V84" stroke="#89b4bf" stroke-width="9"/>',globe:'<path d="M50 108H112M81 103V86" stroke="#b59877" stroke-width="6"/><circle cx="81" cy="51" r="33" fill="#a9d1df"/><path d="M58 29 77 28 88 42 71 58 63 77M100 44 110 54 96 72" fill="#91b996"/><path d="M51 21Q27 76 92 91" fill="none" stroke="#d5b780" stroke-width="5"/>'}[kind];
  return art?`<svg viewBox="0 0 160 120" aria-hidden="true" class="room-furniture"><ellipse cx="80" cy="112" rx="50" ry="6" fill="#64748b" opacity=".08"/>${art}</svg>`:priorFurniture(kind);
};
renderMyHideout=function(){
  priorHideout();const room=getRoomDraft(),owned=ownedBadges(students[currentStudentIndex]);
  const scene=document.querySelector('#hideoutSection .room-scene');scene.dataset.style=room.style;
  scene.querySelector('.room-wall').insertAdjacentHTML('beforeend','<div class="room-decor-shelf" aria-hidden="true">▰ ▥ ▰<br><span>나의 배움이 자라는 곳</span></div>');
  scene.querySelector('.room-floor').insertAdjacentHTML('afterbegin','<div class="room-rug" aria-hidden="true"></div>');
  if(roomEditing){const choices=[['library','햇살 도서관',0],['ocean','바닷속 연구실',2],['magic','마법 공방',3]];
    document.getElementById('hideoutSection').insertAdjacentHTML('beforeend',`<div class="room-theme-picker"><h3 class="font-extrabold text-sm">공간 테마 선택</h3><div class="flex flex-wrap gap-3 mt-3">${choices.map(([id,label,unit])=>{const unlocked=!unit||owned.some(b=>Number(b.split(':')[2].split('-')[0])===unit);return `<button ${unlocked?'':'disabled'} onclick="changeRoomSetting('style','${id}')" class="border rounded-xl p-3 text-sm ${room.style===id?'bg-sky-100 border-sky-300':'bg-white'}">${label}${unlocked?'':' · '+unit+'지역 배지'}</button>`;}).join('')}</div><p class="text-xs text-slate-500 mt-3">생활 소품은 과제 통과 도장 3·5·8·10개로, 지역 소품과 의상은 탐험 배지로 열려요. 도장과 배지는 차감되지 않아요.</p></div>`);
  }
};
function miniEditorCapture(){
  if(!miniEditorDraft)return;
  const q=miniEditorDraft.questions[miniEditorQuestion],value=document.getElementById('miniAnswer').value.trim();
  q.text=document.getElementById('miniText').value;q.hint=document.getElementById('miniHint').value;q.explanation=document.getElementById('miniExplanation').value;
  q.answer=q.type==='multi'?value.split(',').map(s=>Number(s.trim())):Number(value);
  if(q.type!=='number')q.options=document.getElementById('miniOptions').value.split('\n').map(s=>s.trim()).filter(Boolean);
  miniEditorDraft.title=document.getElementById('miniTitle').value;miniEditorDraft.story=document.getElementById('miniStory').value;miniEditorDraft.intro=document.getElementById('miniIntro').value;
}
function renderMiniTeacherEditor(){
  if(!requireTeacher())return;const root=document.getElementById('miniContentManager');if(!root)return;
  if(!miniEditorDraft)miniEditorDraft=JSON.parse(JSON.stringify(miniContent[0]));
  const m=miniEditorDraft,q=m.questions[miniEditorQuestion];
  root.innerHTML=`<div class="flex flex-wrap gap-3 items-end"><label class="text-sm font-bold">작은 탐험<select aria-label="편집할 작은 탐험" onchange="miniEditorDraft=JSON.parse(JSON.stringify(miniContent.find(m=>m.id===this.value)));miniEditorQuestion=0;renderMiniTeacherEditor()" class="block border rounded-xl p-2 mt-1">${miniContent.map(x=>`<option value="${x.id}" ${x.id===m.id?'selected':''}>${x.id} · ${escapeHtml(x.title)}</option>`).join('')}</select></label><button onclick="exportMiniQuestions()" class="border rounded-xl p-2 text-sm font-bold">전체 640문항 CSV</button><button onclick="previewEditedMini()" class="border rounded-xl p-2 text-sm font-bold">학생 풀이 미리보기</button></div><form onsubmit="saveMiniTeacherEditor(event)" class="space-y-3 mt-4"><label class="block text-sm font-bold">주제 제목<input id="miniTitle" value="${escapeHtml(m.title)}" required class="block border rounded-xl p-2 w-full mt-1"></label><label class="block text-sm font-bold">탐험 이름<input id="miniStory" value="${escapeHtml(m.story)}" required class="block border rounded-xl p-2 w-full mt-1"></label><label class="block text-sm font-bold">도입 이야기<textarea id="miniIntro" required class="block border rounded-xl p-2 w-full mt-1">${escapeHtml(m.intro)}</textarea></label><label class="block text-sm font-bold">문항 선택<select aria-label="편집할 문항" onchange="miniEditorCapture();miniEditorQuestion=Number(this.value);renderMiniTeacherEditor()" class="block border rounded-xl p-2 w-full mt-1">${m.questions.map((x,index)=>`<option value="${index}" ${index===miniEditorQuestion?'selected':''}>${x.level===6?'선택 도전':x.level+'단계'} · ${index+1}번</option>`).join('')}</select></label><label class="block text-sm font-bold">문제<textarea id="miniText" required rows="3" class="block border rounded-xl p-2 w-full mt-1">${escapeHtml(q.text)}</textarea></label>${q.type==='number'?'':`<label class="block text-sm font-bold">선택지 — 한 줄에 하나<textarea id="miniOptions" rows="3" class="block border rounded-xl p-2 w-full mt-1">${escapeHtml(q.options.join('\n'))}</textarea></label>`}<label class="block text-sm font-bold">정답 ${q.type==='number'?'숫자':q.type==='multi'?'선택지 번호 (쉼표 구분)':'선택지 번호 (1부터)'}<input id="miniAnswer" required value="${escapeHtml(Array.isArray(q.answer)?q.answer.join(','):q.answer)}" class="block border rounded-xl p-2 w-full mt-1"></label><label class="block text-sm font-bold">힌트<textarea id="miniHint" required class="block border rounded-xl p-2 w-full mt-1">${escapeHtml(q.hint)}</textarea></label><label class="block text-sm font-bold">해설<textarea id="miniExplanation" required class="block border rounded-xl p-2 w-full mt-1">${escapeHtml(q.explanation)}</textarea></label><p class="text-xs text-slate-500">문제를 저장하면 새 버전으로 시작합니다. 이전 시도 기록과 획득한 배지는 보존합니다. 다른 탐험으로 전환하기 전에 저장하세요.</p><button class="room-primary">이 탐험 수정 저장</button></form>`;
}
async function saveMiniTeacherEditor(event){
  event?.preventDefault();if(!requireTeacher())return;miniEditorCapture();const previous=JSON.parse(JSON.stringify(miniContent));miniContent=miniContent.map(m=>m.id===miniEditorDraft.id?JSON.parse(JSON.stringify(miniEditorDraft)):m);
  if(await persistLearning()){miniEditorDraft=JSON.parse(JSON.stringify(miniContent.find(m=>m.id===miniEditorDraft.id)));renderMiniTeacherEditor();alert('탐험을 저장했습니다.');}else miniContent=previous;
}
function previewEditedMini(){const index=students.findIndex(s=>s.gradeRecords?.[1]);if(index<0){alert('중1 기록이 있는 학생을 먼저 등록해 주세요.');return;}currentStudentIndex=index;selectedLearningGrade=1;openMiniExploration(miniEditorDraft.id);}
function exportMiniQuestions(){const rows=[['탐험','주제','단계','문항ID','형식','문제','선택지','정답','힌트','해설']];miniContent.forEach(m=>m.questions.forEach(q=>rows.push([m.id,m.title,q.level,q.id,q.type,q.text,q.options.join(' / '),JSON.stringify(q.answer),q.hint,q.explanation])));const a=document.createElement('a');a.href=URL.createObjectURL(new Blob(['\uFEFF'+rows.map(r=>r.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'}));a.download='작은탐험_40개_640문항.csv';a.click();URL.revokeObjectURL(a.href);}
const priorTeacherManagement=renderTeacherManagement;
renderTeacherManagement=function(){priorTeacherManagement();if(!requireTeacher())return;document.getElementById('teacherStudentPolicy').innerHTML=`<h2 class="text-xl font-extrabold">학생의 세 공간을 함께 관리해요</h2><div class="teacher-area-cards"><article><strong>01 아지트·보상</strong><p>기본 의상 5종 · 총 의상 12종<br>과제 통과 도장으로 생활 소품<br>탐험 배지로 지역 의상·가구·테마</p></article><article><strong>02 나의 학습</strong><p>교사 과제 통과만 성취율에 반영<br>작은 탐험 ${miniContent.length}개 · ${miniContent.reduce((n,m)=>n+m.questions.length,0)}문항<br>방탈출 10탄 · 100문항</p></article><article><strong>03 성장 돌아보기</strong><p>정기 자기효능감·동기 설문<br>지난 응답과 자유 돌아보기<br>참여·응답 내용에 보상 없음</p></article></div><p class="text-sm text-slate-500 mt-4">과제는 검토 후 ‘과제 통과’로 처리합니다. 보완이 필요하면 피드백과 함께 보완 요청을 남겨 주세요. 학생별 진급 취소는 학생 관리에서 할 수 있습니다.</p>`;};
const priorTeacherPanel=renderTeacherResearchPanel;
renderTeacherResearchPanel=function(){priorTeacherPanel();if(!requireTeacher())return;const {record}=teacherRecord();record.submissions.forEach((sub,index)=>{const feedback=document.getElementById('submissionFeedback-'+index);feedback?.parentElement?.nextElementSibling?.insertAdjacentHTML('beforeend',`<button onclick="requestTaskRevision(${index})" class="border rounded-lg px-3 py-2 font-bold text-sm text-amber-800">보완 요청</button>`);});};
const priorResearchAnalysis=renderResearchAnalysis;
renderResearchAnalysis=function(){priorResearchAnalysis();const target=document.getElementById('teacherReflectionList');if(!target)return;const id=document.getElementById('researchStudentSelect').value;target.innerHTML='<h3 class="font-extrabold">학생의 자유 돌아보기</h3>'+(researchState.reflections||[]).filter(r=>r.studentUuid===id).map(r=>`<div class="border rounded-xl p-3 mt-3"><p class="text-xs text-slate-500">중${r.grade} · ${r.at.slice(0,10)}</p><p class="text-sm whitespace-pre-wrap mt-2">${escapeHtml(r.content)}</p></div>`).join('');};
