let adventureContent=[];
let adventureCatalog=[];
let activeAdventure=null;
function adventureMeta(id){return adventureCatalog.find(g=>g.id===id);}
function renderCompactMap(){
  const record=selectedRecord(),stages=selectedStages(),next=stages.find(s=>!record.clearedStages.includes(s.id)&&(s.id===1||record.clearedStages.includes(s.id-1)))||stages[0];
  const category=document.getElementById('adventureCategory');category.hidden=false;
  document.getElementById('adventureCategoryTitle').textContent='3. 수학 방탈출 어드벤처';
  document.getElementById('adventureMapTitle').textContent=`중${selectedLearningGrade} · 수학 방탈출 어드벤처`;
  category.onclick=()=>showLearningCategory('adventure');
  document.getElementById('adventureNextLabel').textContent=next?`${next.unit} · 앱 안에서 도전`:'';
  document.getElementById('missionMapGrid').innerHTML=stages.map(stage=>{
    const done=record.clearedStages.includes(stage.id),unlocked=teacherMode||done||stage.id===1||record.clearedStages.includes(stage.id-1),meta=adventureMeta(stage.id),saved=record.adventures?.[stage.id];
    const solved=saved&&meta&&saved.version===meta.version?saved.solved.length:0;
    return `<button type="button" ${unlocked?`onclick="selectStage(${stage.id})"`:'disabled'} class="text-left rounded-xl border p-3 text-xs ${done?'bg-emerald-50 border-emerald-200 text-emerald-900':unlocked?'bg-indigo-50 border-indigo-200 text-indigo-900':'bg-slate-50 border-slate-100 text-slate-400'}"><span class="block font-extrabold">${done?'✓':unlocked?(meta?.icon||'↗'):'🔒'} ${stage.id}. ${escapeHtml(meta?.unit||stage.unit.replace(/^\d+\.\s*/,''))}</span><span class="block mt-2">${!unlocked?'이전 단계 완료 후':done?'배지 보유 · 다시 도전':solved?`${solved}/10 장치 복구 · 이어하기`:'10개 장치에 도전'}</span></button>`;
  }).join('')||'<p class="col-span-2 text-sm text-slate-500">이 학년의 방탈출 활동은 아직 등록되지 않았습니다.</p>';
}
function selectStage(id){
  if(!studentLoggedIn&&!teacherMode)return;
  if(selectedLearningGrade!==1){alert('중1 어드벤처 맵에서 도전할 수 있어요.');return;}
  openNativeAdventure(id);
}
async function openNativeAdventure(id,fromTeacher=false){
  if(!SERVER_MODE){alert('수업 앱 주소에서 로그인한 뒤 도전해 주세요.');return;}
  try{
    const uuid=students[fromTeacher?selectedTeacherStudentIndex:currentStudentIndex]?.uuid;
    const data=await api(`/api/adventure/${id}${teacherMode?'?student='+encodeURIComponent(uuid):''}`);
    if(data.preview)data.progress={version:data.game.version,solved:[],attempts:{}};
    activeAdventure={...data,index:0,screen:'intro',busy:false,lastInput:'',feedback:null,fromTeacher};
    hideAppViews();document.getElementById('adventureView').hidden=false;
    if(teacherMode)document.getElementById('teacherPreviewBar').hidden=false;
    renderAdventure();
  }catch(error){alert(error.message);}
}
function closeAdventure(){
  const fromTeacher=activeAdventure?.fromTeacher;activeAdventure=null;document.getElementById('adventureView').hidden=true;
  if(teacherMode&&fromTeacher){showTeacherDashboard();return;}
  document.getElementById('studentView').hidden=false;renderStudentView();document.getElementById('stNameDisplay').focus();
}
function startAdventure(){
  if(!activeAdventure)return;
  activeAdventure.screen=activeAdventure.progress.solved.length===10?'complete':'question';
  activeAdventure.index=Math.min(activeAdventure.progress.solved.length,9);renderAdventure();
}
function jumpAdventure(index){if(!activeAdventure||index>activeAdventure.progress.solved.length)return;activeAdventure.index=index;activeAdventure.screen='question';activeAdventure.feedback=null;activeAdventure.lastInput='';renderAdventure();}
function nextAdventureQuestion(){
  const a=activeAdventure;if(!a)return;
  if(a.index===9&&a.progress.solved.length===10){a.screen='complete';renderAdventure();return;}
  a.index=Math.min(a.index+1,a.progress.solved.length,9);a.feedback=null;a.lastInput='';renderAdventure();
}
const adventureThemes={ocean:['#073b56','#087f8c','#38d9e6'],magic:['#36115e','#7c3aed','#e0aaff'],detective:['#292524','#92400e','#fbbf24'],space:['#171044','#4338ca','#a5b4fc'],laser:['#350b28','#a21caf','#fb7185'],garden:['#143a2b','#047857','#a7f3d0'],clock:['#35280a','#a16207','#fde047'],chocolate:['#40261e','#9a3412','#fdba74'],data:['#062b2a','#0f766e','#5eead4']};
adventureThemes.museum=['#3a2416','#98652b','#fde68a'];
function renderAdventure(){
  const a=activeAdventure;if(!a)return;const g=a.game,q=g.questions[a.index],count=a.progress.solved.length,colors=adventureThemes[g.theme]||adventureThemes.ocean;
  const done=q&&a.progress.solved.includes(q.id);
  const top=`<div class="flex flex-wrap justify-between gap-3 items-center"><button onclick="closeAdventure()" class="rounded-xl border border-white/30 px-4 py-2 text-sm font-bold hover:bg-white/10">← 어드벤처 맵으로</button><span class="text-xs font-bold bg-black/20 px-3 py-2 rounded-full">${a.preview?'교사 미리보기 · 기록·배지에 반영 안 됨':a.practiceOnly?'지난 학년 복습 · 새 배지 지급 없음':'MATH QUEST · 나만의 탐험'}</span></div><div class="mt-8 sm:flex gap-5 items-center"><span class="text-6xl" aria-hidden="true">${escapeHtml(g.icon)}</span><div><p class="text-sm font-bold opacity-80 mt-4 sm:mt-0">EPISODE ${g.id} · ${escapeHtml(g.unit)}</p><h1 id="adventureHeading" tabindex="-1" data-copy-exclude class="text-2xl sm:text-3xl font-black leading-snug mt-2">${escapeHtml(g.title)}</h1></div></div><div class="flex justify-between gap-2 text-sm font-bold mt-8"><span>장치 복구 현황</span><span>${count} / 10</span></div><div role="progressbar" aria-label="장치 복구 현황" aria-valuemin="0" aria-valuemax="10" aria-valuenow="${count}" class="h-3 bg-black/20 rounded-full mt-3 overflow-hidden"><div class="h-full bg-white rounded-full transition-all duration-500" style="width:${count*10}%"></div></div>`;
  let body='';
  if(a.screen==='intro')body=`<div class="game-paper text-center"><p class="text-xs font-black tracking-widest text-indigo-600">MISSION BRIEFING</p><h2 class="text-2xl font-extrabold mt-3">새로운 탐험이 기다려요</h2><p data-copy-exclude class="whitespace-pre-wrap text-slate-600 leading-8 text-left sm:text-center max-w-2xl mx-auto mt-5">${escapeHtml(g.intro)}</p>${a.contentChanged?'<p class="bg-amber-50 text-amber-900 rounded-xl p-3 mt-5 text-sm">문제가 새 버전으로 바뀌었어요. 새 도전으로 시작하며 이전 배지는 유지돼요.</p>':''}<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-7 text-sm"><p class="rounded-xl bg-slate-50 p-4">🧩 장치 10개</p><p class="rounded-xl bg-slate-50 p-4">💡 힌트와 다시 도전</p><p class="rounded-xl bg-slate-50 p-4">${a.preview?'🔎 수업 전 미리 확인':'💾 자동으로 진행 저장'}</p></div><button onclick="startAdventure()" class="game-primary mt-7">${count===10?'완료한 탐험 보기':count?'이어서 도전하기 →':'탐험 시작하기 →'}</button><p class="text-xs text-slate-500 mt-4">${a.preview?'미리보기에서는 정답 확인과 진행을 자유롭게 시험할 수 있습니다.':'틀려도 괜찮아요. 시간 제한 없이 내 속도로 풀어 보세요.'}</p></div>`;
  else if(a.screen==='complete')body=`<div class="game-paper text-center"><div class="text-7xl" aria-hidden="true">🏅</div><p class="text-indigo-600 text-xs font-black tracking-widest mt-4">MISSION COMPLETE</p><h2 class="text-3xl font-black mt-3">${g.id}탄 탈출 성공!</h2><p data-copy-exclude class="whitespace-pre-wrap text-slate-600 leading-8 max-w-2xl mx-auto mt-5">${escapeHtml(g.ending)}</p><div class="rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 p-5 mt-6"><p class="text-4xl">${BADGE_THEMES[currentBadgeTheme][g.id-1]}</p><p class="font-bold mt-3">${a.preview?'교사 미리보기 완료 · 실제 배지 지급 없음':a.practiceOnly?'이전 학년 복습 완료':a.newBadge?'새 어드벤처 배지를 얻었어요!':'이 탄의 배지는 이미 보유하고 있어요.'}</p><p class="text-sm mt-2">10개 장치를 모두 해결했어요. 과제 도장과는 별도의 어드벤처 기록이에요.</p></div><div class="flex flex-wrap justify-center gap-3 mt-6"><button onclick="closeAdventure()" class="game-primary">어드벤처 맵으로</button>${g.id<10?`<button onclick="openNativeAdventure(${g.id+1},${a.fromTeacher})" class="border border-indigo-200 text-indigo-700 rounded-xl px-5 py-3 font-bold">다음 탄으로 →</button>`:''}<button onclick="restartAdventure()" class="border rounded-xl px-5 py-3 font-bold text-slate-600">한 번 더 도전</button></div></div>`;
  else body=`<div class="game-paper"><nav class="grid grid-cols-5 sm:grid-cols-10 gap-2 mb-7" aria-label="장치 선택">${g.questions.map((item,index)=>`<button onclick="jumpAdventure(${index})" ${index>count?'disabled':''} aria-current="${index===a.index?'step':'false'}" aria-label="${index+1}번 장치 ${a.progress.solved.includes(item.id)?'복구 완료':index===count?'도전 가능':'잠김'}" class="rounded-xl p-3 text-sm font-black ${index===a.index?'bg-indigo-600 text-white':a.progress.solved.includes(item.id)?'bg-emerald-100 text-emerald-800':'bg-slate-100 text-slate-400'}">${a.progress.solved.includes(item.id)?'✓':index+1}</button>`).join('')}</nav><div class="flex flex-wrap justify-between gap-3"><p class="text-xs font-extrabold text-indigo-600">DEVICE ${String(a.index+1).padStart(2,'0')} / 10</p><p data-copy-exclude class="text-xs font-bold text-slate-500">${escapeHtml(q.skill)}</p></div><h2 data-copy-exclude class="text-2xl font-extrabold mt-3">${escapeHtml(q.title)}</h2><p data-copy-exclude class="game-problem whitespace-pre-wrap mt-5">${escapeHtml(q.prompt)}</p>${adventureDiagram(q.diagram)}${done?`<div class="bg-emerald-50 border border-emerald-200 rounded-2xl p-5 mt-6" role="status"><p class="font-extrabold text-emerald-800">✓ 장치를 복구했어요!</p><p data-copy-exclude class="text-emerald-900 leading-7 whitespace-pre-wrap mt-2">${escapeHtml(q.explanation||a.feedback?.message||'')}</p></div><button onclick="nextAdventureQuestion()" class="game-primary mt-5">${a.index===9?'탈출 결과 보기 →':'다음 장치로 →'}</button>`:`<form onsubmit="submitAdventureAnswer(event,this)" class="mt-6"><label for="adventureAnswer" class="block font-bold text-sm">장치를 여는 숫자 코드</label><div class="flex flex-wrap gap-3 mt-2"><input id="adventureAnswer" name="answer" type="text" autocomplete="off" maxlength="80" required value="${escapeHtml(a.lastInput)}" aria-describedby="adventureAnswerHelp adventureFeedback" class="flex-1 min-w-[160px] border-2 border-slate-200 rounded-xl px-4 py-3 text-xl font-bold focus:outline-none focus:border-indigo-500" placeholder="숫자를 입력하세요"><button class="game-primary" ${a.busy?'disabled':''}>${a.busy?'확인 중…':'코드 확인'}</button></div><p id="adventureAnswerHelp" class="text-xs text-slate-500 mt-2">단위 없이 숫자만 입력하세요. 음수는 - 기호를 함께 입력해요.</p></form><p id="adventureFeedback" role="status" class="text-sm font-bold text-amber-800 mt-4">${escapeHtml(a.feedback?.message||'')}</p><details class="border border-slate-200 bg-slate-50 rounded-xl p-4 mt-5"><summary class="font-bold text-sm cursor-pointer">💡 생각의 실마리 보기</summary><p data-copy-exclude class="text-sm leading-7 text-slate-600 mt-3">${escapeHtml(q.hint)}</p></details>${a.preview?`<details class="border rounded-xl p-4 mt-3"><summary class="font-bold text-sm cursor-pointer">교사용 정답·해설</summary><p data-copy-exclude class="text-sm mt-2">정답: ${escapeHtml(q.answer)}<br>${escapeHtml(q.explanation)}</p></details>`:''}`}</div>`;
  document.getElementById('adventureView').innerHTML=`<div class="game-hero rounded-3xl text-white p-5 sm:p-8" style="background:radial-gradient(circle at 85% 10%,${colors[1]},transparent 45%),linear-gradient(135deg,${colors[0]},${colors[1]})">${top}</div><div class="max-w-4xl mx-auto -mt-1 relative px-0 sm:px-3 pb-8">${body}</div>`;
  applyStudentCopy();
  if(a.screen==='question'&&!done)document.getElementById('adventureAnswer').focus();else document.getElementById('adventureHeading').focus();
}
async function submitAdventureAnswer(event,form){
  event.preventDefault();const a=activeAdventure;if(!a||a.busy)return;
  a.lastInput=form.elements.answer.value.trim();if(!a.lastInput)return;
  const q=a.game.questions[a.index];
  if(a.preview){
    const correct=Number(a.lastInput.replace('−','-'))===Number(q.answer)&&/^[+\-−]?\d+(\.\d*)?$/.test(a.lastInput);
    if(correct&&!a.progress.solved.includes(q.id))a.progress.solved.push(q.id);
    a.feedback={correct,message:correct?q.explanation:'다시 계산해 보세요. 미리보기에서도 정답일 때 다음 장치가 열립니다.'};renderAdventure();return;
  }
  a.busy=true;form.querySelector('button').disabled=true;
  try{
    const response=await api('/api/adventure/answer',{stageId:a.game.id,version:a.game.version,questionId:q.id,answer:a.lastInput});
    applyRemote(response);if(activeAdventure!==a)return;
    const result=response.result;a.game=result.game;a.progress=result.progress;a.newBadge=a.newBadge||result.badgeAwarded;a.badgeEarned=result.badgeEarned;a.feedback={correct:result.correct,message:result.feedback};
  }catch(error){if(activeAdventure===a)a.feedback={correct:false,message:error.message};}
  finally{a.busy=false;if(activeAdventure===a)renderAdventure();}
}
async function restartAdventure(){
  const a=activeAdventure;if(!a||a.busy)return;
  if(a.preview){a.progress={version:a.game.version,solved:[],attempts:{}};a.screen='intro';a.feedback=null;renderAdventure();return;}
  a.busy=true;
  try{const response=await api('/api/adventure/answer',{stageId:a.game.id,version:a.game.version,action:'restart'});applyRemote(response);if(activeAdventure!==a)return;Object.assign(a,response.result,{screen:'intro',index:0,feedback:null,lastInput:'',newBadge:false});renderAdventure();}catch(error){alert(error.message);}finally{a.busy=false;}
}
function adventureDiagram(kind){
  if(!kind)return '';
  const line=(x1,y1,x2,y2,color='#4f46e5',dash='')=>`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="3" ${dash?'stroke-dasharray="'+dash+'"':''}/>`;
  const text=(x,y,label)=>`<text x="${x}" y="${y}" fill="#334155" font-size="16" text-anchor="middle">${label}</text>`;
  let svg='',label='問題の条件を示す図';
  if(['equal-segments','midpoints'].includes(kind)){
    label=kind==='equal-segments'?'A B C Dの順に並ぶ三等分された線分':'A M N Bの順に並ぶ線分';
    const points=kind==='equal-segments'?[[65,'A'],[195,'B'],[325,'C'],[455,'D']]:[[65,'A'],[260,'M'],[357.5,'N'],[455,'B']];
    svg=line(65,100,455,100)+points.map(([x,name])=>line(x,92,x,108)+text(x,135,name)).join('')+text(260,60,kind==='equal-segments'?'AD = 18 cm · AB = BC = CD':'AB = 24 cm · AM = MB · MN = NB');
  }else if(kind==='parallel-bend'){
    label='平行な二直線の間の折れ線。上の角35度、下の角45度、中央の左側の角がx。';
    svg=line(50,45,470,45,'#94a3b8')+line(50,215,470,215,'#94a3b8')+line(50,130,470,130,'#94a3b8','6 6')+line(138.6,45,260,130)+line(175,215,260,130)+text(190,68,'35°')+text(210,202,'45°')+text(222,138,'x')+text(433,36,'ℓ')+text(433,206,'m');
  }else if(kind==='hexagon'){
    label='정육각형 ABCDEF';const pts=[[190,43.8,'A'],[330,43.8,'B'],[400,165,'C'],[330,286.2,'D'],[190,286.2,'E'],[120,165,'F']];
    svg=`<polygon points="${pts.map(p=>p.slice(0,2).join(',')).join(' ')}" fill="#eef2ff" stroke="#4f46e5" stroke-width="3"/>`+pts.map(([x,y,n])=>text(x+(x<200?-16:16),y+(y<100?-10:22),n)).join('');
  }else if(['cuboid','cuboid-dimensions'].includes(kind)){
    label='直方体。上面ABCD、下面EFGH。対応する縦の辺はAE BF CG DH。';
    const p={A:[110,75],B:[330,75],C:[410,30],D:[190,30],E:[110,240],F:[330,240],G:[410,195],H:[190,195]};
    svg=['AB','BC','CD','DA','AE','BF','CG','DH','EF','FG','GH','HE'].map(pair=>line(...p[pair[0]],...p[pair[1]],'#4f46e5',['DH','GH','HE'].includes(pair)?'6 5':'')).join('');
    if(kind==='cuboid')svg+=Object.entries(p).map(([n,[x,y]])=>text(x-12,y+(n==='E'||n==='F'?22:-10),n)).join('');
    else svg+=text(220,265,'3 cm')+text(390,237,'4 cm')+text(75,165,'5 cm');
  }else if(kind==='coordinate-triangle'){
    label='A(0,4)、B(-3,0)、C(5,0)からなる三角形。';svg=line(55,220,475,220,'#94a3b8')+line(210,260,210,30,'#94a3b8')+`<polygon points="210,55 90,220 410,220" fill="#e0e7ff" stroke="#4f46e5" stroke-width="3"/>`+text(240,45,'A(0,4)')+text(85,248,'B(−3,0)')+text(430,248,'C(5,0)')+text(197,240,'O')+line(210,55,210,220,'#818cf8','5 5');
  }else if(kind==='inscribed-triangle'){
    label='正三角形ABCの各辺上にAD=BE=CFとなるD E Fを置いた図。';
    svg=`<polygon points="260,25 120,267.5 400,267.5" fill="#f0fdf4" stroke="#047857" stroke-width="3"/><polygon points="213.3,105.8 213.3,267.5 353.3,186.7" fill="#d1fae5" stroke="#4f46e5" stroke-width="3"/>`+[[260,18,'A'],[105,290,'B'],[415,290,'C'],[195,100,'D'],[213,290,'E'],[375,185,'F']].map(p=>text(...p)).join('');
  }else if(kind==='isosceles'){
    label='頂角30度、二つの底角が等しい二等辺三角形。';svg=`<polygon points="260,30 205,235.3 315,235.3" fill="#e0e7ff" stroke="#4f46e5" stroke-width="3"/>`+text(260,100,'30°')+text(225,220,'x')+text(295,220,'x');
  }else if(kind==='sector'){
    label='半径6cm、中心角60度の扇形。';svg=`<path d="M170 230 L370 230 A200 200 0 0 0 270 56.8 Z" fill="#fef3c7" stroke="#a16207" stroke-width="3"/>`+text(240,207,'60°')+text(290,255,'6 cm');
  }
  const koreanLabels={'equal-segments':'세 구간이 같은 선분 ABCD','midpoints':'중점 M, N을 표시한 선분 AB','parallel-bend':'평행선 사이의 꺾인 선분과 35°, 45°, 미지각 x','hexagon':'정육각형 ABCDEF','cuboid':'윗면 ABCD, 밑면 EFGH인 직육면체','cuboid-dimensions':'가로 3cm, 세로 4cm, 높이 5cm인 직육면체','coordinate-triangle':'좌표평면 위 삼각형 ABC','inscribed-triangle':'정삼각형 ABC 안의 삼각형 DEF','isosceles':'꼭지각 30도인 이등변삼각형','sector':'반지름 6cm, 중심각 60도인 부채꼴'};
  return svg?`<figure class="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-3"><svg role="img" aria-label="${koreanLabels[kind]}" viewBox="0 0 520 320" class="w-full max-w-xl mx-auto" style="max-height:280px">${svg}</svg><figcaption class="text-center text-xs text-slate-500">${koreanLabels[kind]} · 그림은 조건을 설명하기 위한 것이며 직접 재어 풀지 않아요.</figcaption></figure>`:'';
}
function renderTeacherManagement(){
  baseTeacherManagement();if(!requireTeacher())return;
  document.getElementById('teacherStageManager').closest('details').hidden=true;
  renderAdventureEditor();
  renderMiniTeacherEditor();
}
function renderAdventureEditor(){
  const selector=document.getElementById('adventureEditorStage'),previous=selector.value;
  selector.innerHTML=adventureContent.map(g=>`<option value="${g.id}">${g.id}탄 · ${escapeHtml(g.unit)}</option>`).join('');selector.value=adventureContent.some(g=>String(g.id)===previous)?previous:'1';loadAdventureEditor();
}
function loadAdventureEditor(){
  const g=adventureContent.find(g=>g.id===Number(document.getElementById('adventureEditorStage').value));if(!g)return;
  const field=(name,label,value,rows=2)=>`<label class="block text-sm font-bold">${label}<textarea name="${name}" required rows="${rows}" class="block w-full border rounded-lg p-2 mt-1 font-normal">${escapeHtml(value)}</textarea></label>`;
  document.getElementById('adventureEditorForm').innerHTML=`<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">${field('unit','단원 이름',g.unit,1)}${field('title','탐험 제목',g.title,1)}</div>${field('intro','도입 스토리',g.intro,3)}${field('ending','완료 스토리',g.ending,3)}<div class="space-y-3">${g.questions.map((q,index)=>`<details class="border rounded-xl p-4"><summary class="font-bold text-sm cursor-pointer">${index+1}. ${escapeHtml(q.title)}</summary><div class="space-y-3 mt-4">${field('skill-'+index,'학습 주제',q.skill,1)}${field('title-'+index,'장치 이름',q.title,1)}${field('prompt-'+index,'문제',q.prompt,3)}${field('answer-'+index,'숫자 정답',q.answer,1)}${field('hint-'+index,'힌트',q.hint)}${field('explanation-'+index,'해설',q.explanation)}<label class="block text-sm font-bold">도형<select name="diagram-${index}" class="border rounded-lg p-2 ml-2">${['','coordinate-triangle','equal-segments','midpoints','parallel-bend','hexagon','cuboid','inscribed-triangle','isosceles','sector','cuboid-dimensions'].map(d=>`<option value="${d}" ${q.diagram===d?'selected':''}>${d||'없음'}</option>`).join('')}</select></label></div></details>`).join('')}</div><div class="flex flex-wrap gap-3"><button class="bg-indigo-600 text-white font-bold rounded-xl px-4 py-3">이 탄의 변경 저장</button><button type="button" onclick="openNativeAdventure(${g.id},true)" class="border rounded-xl px-4 py-3 font-bold">이 탄 미리보기</button></div>`;
}
async function saveAdventureEditor(event){
  event.preventDefault();if(!requireTeacher())return;
  const form=event.target,id=Number(document.getElementById('adventureEditorStage').value),original=adventureContent.find(g=>g.id===id),g=JSON.parse(JSON.stringify(original));
  ['unit','title','intro','ending'].forEach(k=>g[k]=form.elements[k].value.trim());
  g.questions.forEach((q,index)=>['skill','title','prompt','answer','hint','explanation','diagram'].forEach(key=>q[key]=form.elements[key+'-'+index].value.trim()));
  adventureContent=adventureContent.map(item=>item.id===id?g:item);
  if(await persistLearning()){renderAdventureEditor();alert('방탈출 내용을 저장했습니다. 기존 배지는 유지되며 변경된 문제는 새 도전으로 시작합니다.');}else adventureContent=adventureContent.map(item=>item.id===id?original:item);
}
function loadStageLink(){
  const stage=STAGES.find(s=>s.id===Number(document.getElementById('modalStageSelect').value));
  if(!stage)return;
  const input=document.getElementById('modalTallyUrl');input.value=stage.tallyUrl;
  input.closest('label').hidden=true;
}
