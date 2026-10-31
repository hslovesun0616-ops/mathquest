let researchState=emptyResearchState();
let teacherArea='lesson';
function emptyResearchState(){return {project:{title:'수학 학습 앱 활용과 정의적 태도 변화',question:'개인 성장 기록·피드백·보상을 활용하는 수학 수업에서 자기효능감과 학습동기는 어떻게 변화하는가?',appStartedOn:''},instruments:[],waves:[],responses:[],observations:[],participation:{}};}
const researchKind={selfEfficacy:'수학 자기효능감',motivation:'학습동기'};
function changeTeacherArea(area){
  teacherArea=area;
  document.getElementById('teacherLessonArea').hidden=area!=='lesson';
  document.getElementById('teacherResearchArea').hidden=area!=='research';
  ['lesson','research'].forEach(key=>{const button=document.getElementById('teacherArea-'+key);button.setAttribute('aria-pressed',key===area);button.className='rounded-xl px-5 py-3 font-bold text-sm '+(key===area?'bg-indigo-700 text-white':'bg-white text-slate-600 border');});
  if(area==='research')renderResearchWorkspace();
}
function renderTeacherDashboard(){
  if(!students.length)return;
  const filter=document.getElementById('teacherClassFilter').value;
  const visible=students.filter(st=>filter==='all'||st.classNum===filter);
  document.getElementById('teacherLessonStats').innerHTML=[['학생',visible.length+'명'],['확인 대기 과제',visible.reduce((sum,st)=>sum+st.submissions.filter(sub=>sub.reviewStatus!=='approved').length,0)+'건'],['확인 완료 과제',visible.reduce((sum,st)=>sum+approvedCount(st),0)+'건']].map(([label,value])=>`<div class="bg-white border rounded-2xl p-5"><p class="text-sm text-slate-500">${label}</p><strong class="text-2xl text-indigo-700 block mt-2">${value}</strong></div>`).join('');
  document.getElementById('teacherStudentTableBody').innerHTML=visible.map(st=>{
    const idx=students.findIndex(s=>s.uuid===st.uuid),p=achievement(st,st.grade);
    return `<tr class="border-b"><td class="p-3 font-bold">${escapeHtml(st.studentId)} ${escapeHtml(st.name)}</td><td class="p-3">중${st.grade} · ${escapeHtml(st.classNum)}</td><td class="p-3">${p.total?p.percent+'%':'과제 준비 중'} <span class="text-xs text-slate-500">(${p.approved}/${p.total})</span></td><td class="p-3"><button onclick="selectTeacherStudent(${idx})" class="text-indigo-700 font-bold">제출·피드백 보기</button></td></tr>`;
  }).join('');
  renderTeacherResearchPanel();
  if(teacherArea==='research')renderResearchWorkspace();
}
function renderTeacherResearchPanel(){
  if(!students.length)return;
  const {st,grade,record}=teacherRecord(),p=achievement(record,grade);
  document.getElementById('teacherStudentResearchPanel').innerHTML=`<div class="flex flex-wrap gap-3 justify-between"><h3 class="font-extrabold">${escapeHtml(st.studentId)} ${escapeHtml(st.name)} · 제출·피드백</h3><label class="text-sm">조회 학년 <select onchange="teacherRecordGrade=Number(this.value);renderTeacherResearchPanel()" class="border rounded-lg p-2">${[1,2,3].filter(g=>g<=st.grade).map(g=>`<option value="${g}" ${grade===g?'selected':''}>중${g}${g===st.grade?' (현재)':' 기록'}</option>`).join('')}</select></label></div><p class="text-sm text-indigo-700 mt-3">과제 확인 완료율 ${p.total?p.percent+'%':'측정 대상 과제 없음'} · ${p.approved}/${p.total}개</p><p class="text-xs text-slate-500 mt-2">과제 완료율은 학습 관리 지표입니다. 수학 성취도나 자기효능감 점수로 사용하지 않습니다.</p><div class="space-y-4 mt-5">${record.submissions.map((sub,index)=>`<div class="border rounded-xl p-4"><p class="font-bold text-sm">${escapeHtml(assignments.find(t=>t.id===(sub.assignmentId||'stage-'+sub.stageId))?.title||'제출 과제')}</p><p class="text-xs text-slate-500 mt-1">${escapeHtml(sub.date)} · ${submissionStatus(sub)}</p><p class="text-sm whitespace-pre-wrap mt-3">${escapeHtml(sub.content)}</p>${attachmentLink(sub)}<label class="block mt-3 text-sm font-bold">학생에게 전할 피드백<textarea id="submissionFeedback-${index}" rows="2" class="block w-full border rounded-lg p-2 mt-2 font-normal">${escapeHtml(sub.teacherFeedback||'')}</textarea></label><div class="flex gap-2 mt-3"><button onclick="saveSubmissionFeedback(${selectedTeacherStudentIndex},${index})" class="bg-indigo-100 text-indigo-800 font-bold rounded-lg px-3 py-2 text-sm">피드백 저장</button><button onclick="reviewSubmission(${selectedTeacherStudentIndex},${index},${sub.reviewStatus!=='approved'})" class="bg-emerald-600 text-white font-bold rounded-lg px-3 py-2 text-sm">${sub.reviewStatus==='approved'?'확인 취소':'확인 완료'}</button></div></div>`).join('')||'<p class="text-sm text-slate-500">이 학년의 제출 기록이 없습니다.</p>'}</div>`;
  if(grade===1)document.getElementById('teacherStudentResearchPanel').insertAdjacentHTML('beforeend',`<div class="border-t pt-4 mt-5"><h4 class="font-bold text-sm">어드벤처 진행 기록</h4><p class="text-sm text-slate-500 mt-2">배지 ${record.clearedStages.length}/10개 · 내장 방탈출 1~10탄은 모든 문제를 해결하면 자동으로 배지를 받습니다.</p><div class="space-y-1 mt-3 text-xs">${Object.entries(record.adventures||{}).map(([id,progress])=>`<p>${id}탄 · ${progress.solved.length}/10 장치 복구 · 시도 ${Object.values(progress.attempts||{}).reduce((sum,a)=>sum+a.count,0)}회${progress.completedAt?' · 완료':''}</p>`).join('')}</div></div>`);
}
function researchOptions(){return students.map(st=>`<option value="${escapeHtml(st.uuid)}">${escapeHtml(st.studentId)} ${escapeHtml(st.name)}</option>`).join('');}
function renderResearchWorkspace(){
  if(!requireTeacher())return;
  const r=researchState;
  document.getElementById('researchProjectTitle').value=r.project.title||'';
  document.getElementById('researchQuestion').value=r.project.question||'';
  document.getElementById('researchAppStart').value=r.project.appStartedOn||'';
  document.getElementById('researchParticipationRows').innerHTML=students.map(st=>`<label class="flex items-center gap-2 border rounded-lg p-3 text-sm"><input type="checkbox" data-research-participant="${escapeHtml(st.uuid)}" ${r.participation[st.uuid]?.eligible?'checked':''}>${escapeHtml(st.studentId)} ${escapeHtml(st.name)} · 연구 참여 확인</label>`).join('');
  document.getElementById('researchInstrumentList').innerHTML=r.instruments.map(i=>`<div class="border rounded-xl p-4"><strong class="text-sm">${escapeHtml(i.title)} · ${escapeHtml(i.version)}</strong><p class="text-xs text-slate-500 mt-2">${researchKind[i.kind]} · ${i.items.length}문항 · ${i.min}~${i.max} · 하위영역별 평균(역채점 반영)</p><p class="text-xs mt-2 whitespace-pre-wrap">출처: ${escapeHtml(i.source)}</p><p class="text-xs mt-2">${i.scoringConfirmed?'사용·채점 지침 교사 확인됨':'지침 확인 전 · 배포 불가'}</p></div>`).join('')||'<p class="text-sm text-slate-500">등록된 척도가 없습니다. 임의의 설문 문항이나 시연 점수는 생성하지 않습니다.</p>';
  document.getElementById('researchWaveInstruments').innerHTML=r.instruments.map(i=>`<label class="block text-sm mt-2"><input type="checkbox" name="instrumentIds" value="${escapeHtml(i.id)}" ${i.scoringConfirmed?'':'disabled'}> ${escapeHtml(i.title)} (${escapeHtml(i.version)})</label>`).join('')||'<p class="text-sm text-slate-500">먼저 사용할 척도를 등록해 주세요.</p>';
  document.getElementById('researchWaveParticipants').innerHTML=students.filter(st=>r.participation[st.uuid]?.eligible).map(st=>`<label class="block text-sm mt-2"><input type="checkbox" name="participantIds" value="${escapeHtml(st.uuid)}" checked> ${escapeHtml(st.studentId)} ${escapeHtml(st.name)}</label>`).join('')||'<p class="text-sm text-slate-500">연구 참여 확인을 저장한 학생이 없습니다.</p>';
  document.getElementById('researchWaveList').innerHTML=r.waves.map(w=>{
    const expected=w.participantIds.length*w.instrumentIds.length,completed=r.responses.filter(x=>x.waveId===w.id&&x.status==='completed').length,declined=r.responses.filter(x=>x.waveId===w.id&&x.status==='declined').length;
    return `<div class="border rounded-xl p-4"><p class="font-bold">${escapeHtml(w.label)} · ${escapeHtml(w.date)} <span class="text-xs text-indigo-700">${w.status==='open'?'응답 중':'마감'}</span></p><p class="text-sm text-slate-500 mt-2">학생 ${w.participantIds.length}명 · 설문 응답 ${completed}/${expected}건 · 미참여 ${declined}건 · 미응답 ${expected-completed-declined}건</p>${w.status==='open'?`<button onclick="closeResearchWave('${w.id}')" class="text-sm font-bold text-indigo-700 mt-3">측정 마감</button>`:''}</div>`;
  }).join('')||'<p class="text-sm text-slate-500">측정 전입니다. 최초 측정부터 학기별로 시점을 추가하세요.</p>';
  const selector=document.getElementById('researchStudentSelect'),current=selector.value;selector.innerHTML=researchOptions();if(students.some(st=>st.uuid===current))selector.value=current;
  const observer=document.getElementById('observationStudent'),selected=observer.value;observer.innerHTML=researchOptions();if(students.some(st=>st.uuid===selected))observer.value=selected;
  renderResearchAnalysis();
}
async function saveResearchProject(event){
  event.preventDefault();if(!requireTeacher())return;
  researchState.project={title:document.getElementById('researchProjectTitle').value.trim(),question:document.getElementById('researchQuestion').value.trim(),appStartedOn:document.getElementById('researchAppStart').value};
  if(await persistLearning())alert('연구 계획을 저장했습니다.');
}
async function saveResearchParticipation(){
  if(!requireTeacher())return;
  document.querySelectorAll('[data-research-participant]').forEach(el=>researchState.participation[el.dataset.researchParticipant]={eligible:el.checked,recordedAt:new Date().toISOString()});
  if(await persistLearning()){renderResearchWorkspace();alert('참여 확인을 저장했습니다. 연구 참여 여부는 과제나 보상에 영향을 주지 않습니다.');}
}
async function registerResearchInstrument(event){
  event.preventDefault();if(!requireTeacher())return;const form=event.target;
  const lines=form.elements.items.value.trim().split('\n').filter(line=>line.trim());
  const items=[];
  for(const [index,line]of lines.entries()){
    const parts=line.split('|').map(s=>s.trim());
    if(parts.length!==3||!parts[0]||!parts[2]||!['정','역'].includes(parts[1])){alert('문항은 한 줄에 하위영역 | 정 또는 역 | 문항 내용 형식으로 입력해 주세요.');return;}
    items.push({id:'q'+(index+1),dimension:parts[0],reverse:parts[1]==='역',text:parts[2]});
  }
  const instrument={id:crypto.randomUUID(),kind:form.elements.kind.value,title:form.elements.title.value.trim(),version:form.elements.version.value.trim(),source:form.elements.source.value.trim(),min:Number(form.elements.min.value),max:Number(form.elements.max.value),options:form.elements.options.value.trim().split('\n').map(s=>s.trim()),items,scoringConfirmed:form.elements.scoringConfirmed.checked};
  if(instrument.options.length!==instrument.max-instrument.min+1){alert('최솟값부터 최댓값까지 순서대로 선택지 설명을 한 줄에 하나씩 입력해 주세요.');return;}
  researchState.instruments.push(instrument);
  if(await persistLearning()){form.reset();renderResearchWorkspace();alert('새 척도 버전을 등록했습니다. 측정 시작 후에는 문항과 채점 기준이 고정됩니다.');}else researchState.instruments=researchState.instruments.filter(i=>i.id!==instrument.id);
}
async function openResearchWave(event){
  event.preventDefault();if(!requireTeacher())return;const form=event.target;
  const checked=name=>[...form.querySelectorAll(`input[name="${name}"]:checked`)].map(el=>el.value);
  const wave={id:crypto.randomUUID(),label:form.elements.label.value.trim(),date:form.elements.date.value,instrumentIds:checked('instrumentIds'),participantIds:checked('participantIds'),status:'open'};
  if(!wave.instrumentIds.length||!wave.participantIds.length){alert('척도와 참여 학생을 선택해 주세요.');return;}
  researchState.waves.push(wave);
  if(await persistLearning()){form.reset();renderResearchWorkspace();alert('연구 설문을 열었습니다. 학생 화면의 연구 설문에서 응답할 수 있습니다.');}else researchState.waves=researchState.waves.filter(w=>w.id!==wave.id);
}
async function closeResearchWave(id){if(!requireTeacher())return;researchState.waves.find(w=>w.id===id).status='closed';if(await persistLearning())renderResearchWorkspace();}
function researchSeries(uuid){
  const series=[];
  for(const i of researchState.instruments){
    const dimensions=[...new Set(i.items.map(q=>q.dimension))];
    for(const dimension of dimensions){
      const points=researchState.waves.filter(w=>w.instrumentIds.includes(i.id)).sort((a,b)=>a.date.localeCompare(b.date)).map(w=>{
        const response=researchState.responses.find(r=>r.waveId===w.id&&r.instrumentId===i.id&&r.studentUuid===uuid&&r.status==='completed');
        return {label:w.label,date:w.date,value:response?.scores[dimension]??null};
      });
      series.push({instrument:i,dimension,points});
    }
  }
  return series;
}
function researchChart(series){
  const {points,instrument:i}=series;
  const x=index=>35+(points.length>1?index/(points.length-1)*510:255),y=value=>135-(value-i.min)/(i.max-i.min)*110;
  let lines='',previous=null;
  points.forEach((point,index)=>{if(point.value===null){previous=null;return;}const position={x:x(index),y:y(point.value)};if(previous)lines+=`<line x1="${previous.x}" y1="${previous.y}" x2="${position.x}" y2="${position.y}" stroke="#4f46e5" stroke-width="3"/>`;lines+=`<circle cx="${position.x}" cy="${position.y}" r="4" fill="#4f46e5"/>`;previous=position;});
  return `<svg role="img" aria-label="${escapeHtml(series.dimension)} 변화 그래프. 아래 표에 시점별 수치가 있습니다." viewBox="0 0 580 165" class="w-full max-w-2xl"><line x1="35" y1="135" x2="545" y2="135" stroke="#cbd5e1"/><text x="5" y="30" font-size="12">${i.max}</text><text x="5" y="138" font-size="12">${i.min}</text>${lines}</svg>`;
}
function renderResearchAnalysis(){
  const uuid=document.getElementById('researchStudentSelect').value,st=students.find(s=>s.uuid===uuid);if(!st)return;
  const series=researchSeries(uuid);
  document.getElementById('researchIndividualResults').innerHTML=series.map(s=>`<div class="border rounded-xl p-4"><h4 class="font-bold">${researchKind[s.instrument.kind]} · ${escapeHtml(s.dimension)}</h4><p class="text-xs text-slate-500 mt-1">${escapeHtml(s.instrument.title)} (${escapeHtml(s.instrument.version)}) · 범위 ${s.instrument.min}~${s.instrument.max}</p>${s.points.some(p=>p.value!==null)?researchChart(s):'<p class="text-sm text-slate-500 py-5">측정 전 · 완료된 응답이 없습니다.</p>'}<table class="w-full text-sm"><thead><tr class="text-left text-slate-500"><th>시점</th><th>날짜</th><th>점수</th></tr></thead><tbody>${s.points.map(p=>`<tr class="border-t"><td class="py-2">${escapeHtml(p.label)}</td><td>${escapeHtml(p.date)}</td><td>${p.value===null?'미응답·미참여':p.value.toFixed(2)}</td></tr>`).join('')||'<tr><td class="py-2" colspan="3">측정 시점이 없습니다.</td></tr>'}</tbody></table></div>`).join('')||'<p class="text-sm text-slate-500">측정 전입니다. 척도와 측정 시점을 등록하면 자기효능감·동기를 따로 표시합니다.</p>';
  const rows=[];
  for(const i of researchState.instruments){
    const waves=researchState.waves.filter(w=>w.instrumentIds.includes(i.id)).sort((a,b)=>a.date.localeCompare(b.date));
    for(const dimension of [...new Set(i.items.map(q=>q.dimension))]){
      waves.forEach((w,index)=>{
        const complete=researchState.responses.filter(r=>r.waveId===w.id&&r.instrumentId===i.id&&r.status==='completed');
        const values=complete.map(r=>r.scores[dimension]).filter(Number.isFinite);
        const previous=waves[index-1];const pairs=previous?complete.map(r=>({current:r.scores[dimension],past:researchState.responses.find(p=>p.studentUuid===r.studentUuid&&p.waveId===previous.id&&p.instrumentId===i.id&&p.status==='completed')?.scores[dimension]})).filter(p=>Number.isFinite(p.current)&&Number.isFinite(p.past)):[];
        const mean=values.length?values.reduce((a,b)=>a+b,0)/values.length:null;
        const delta=pairs.length?pairs.reduce((sum,p)=>sum+p.current-p.past,0)/pairs.length:null;
        rows.push(`<tr class="border-t"><td class="p-2">${escapeHtml(i.title)} · ${escapeHtml(i.version)}<br>${escapeHtml(dimension)}</td><td class="p-2">${escapeHtml(w.label)}</td><td class="p-2">${values.length}/${w.participantIds.length}명</td><td class="p-2">${mean===null?'측정 전':mean.toFixed(2)}</td><td class="p-2">${values.length?Math.min(...values).toFixed(2)+'~'+Math.max(...values).toFixed(2):'—'}</td><td class="p-2">${delta===null?'비교 자료 없음':(delta>0?'+':'')+delta.toFixed(2)+' ('+pairs.length+'명)'}</td></tr>`);
      });
    }
  }
  document.getElementById('researchClassResults').innerHTML=rows.join('')||'<tr><td colspan="6" class="p-4 text-slate-500">측정 전 · 학급 결과가 없습니다.</td></tr>';
  document.getElementById('researchBehaviorResults').innerHTML=Object.entries(st.gradeRecords).map(([grade,record])=>{
    const tasks=assignments.filter(t=>t.grade===Number(grade)),subs=tasks.map(t=>taskSubmission(record,t)).filter(Boolean),feedback=subs.filter(s=>s.teacherFeedback),revised=feedback.filter(s=>(s.revision||0)>(s.feedbackRevision||0));
    return `<tr class="border-t"><td class="p-2">중${grade}</td><td class="p-2">${tasks.length?subs.length+'/'+tasks.length+' ('+Math.round(subs.length/tasks.length*100)+'%)':'대상 과제 없음'}</td><td class="p-2">${feedback.length?revised.length+'/'+feedback.length+' ('+Math.round(revised.length/feedback.length*100)+'%)':'피드백 자료 없음'}</td><td class="p-2">${subs.filter(s=>(s.revision||0)>1).length}개 과제</td></tr>`;
  }).join('');
  document.getElementById('researchBehaviorSnapshots').innerHTML=researchState.waves.filter(w=>w.participantSnapshot?.[uuid]).sort((a,b)=>a.date.localeCompare(b.date)).map(w=>{
    const snapshot=w.participantSnapshot[uuid],b=snapshot.behavior;
    return `<tr class="border-t"><td class="p-2">${escapeHtml(w.label)}<br><span class="text-xs text-slate-500">${escapeHtml(w.date)} · 중${snapshot.grade}</span></td><td class="p-2">${b.submitted}/${b.assigned}</td><td class="p-2">${b.feedbackRevised}/${b.feedbackReceived}</td><td class="p-2">${b.resubmitted}개</td></tr>`;
  }).join('')||'<tr><td colspan="4" class="p-3 text-slate-500">측정 시작 시 저장된 행동 기록이 없습니다.</td></tr>';
  document.getElementById('researchObservationList').innerHTML=researchState.observations.filter(o=>o.studentUuid===uuid).sort((a,b)=>b.date.localeCompare(a.date)).map(o=>`<div class="border rounded-xl p-4"><p class="text-xs text-slate-500">${escapeHtml(o.date)} · ${escapeHtml(o.kind)} · 중${o.grade}</p><p class="text-sm whitespace-pre-wrap mt-2">${escapeHtml(o.content)}</p></div>`).join('')||'<p class="text-sm text-slate-500">등록한 면담·관찰 기록이 없습니다.</p>';
}
async function addResearchObservation(event){
  event.preventDefault();if(!requireTeacher())return;const form=event.target,st=students.find(s=>s.uuid===form.elements.studentUuid.value);
  researchState.observations.push({id:crypto.randomUUID(),studentUuid:st.uuid,grade:st.grade,date:form.elements.date.value,kind:form.elements.kind.value,content:form.elements.content.value.trim()});
  if(await persistLearning()){form.elements.content.value='';renderResearchAnalysis();alert('교사용 연구 기록을 저장했습니다.');}
}
function exportResearchCSV(){
  if(!requireTeacher())return;
  const rows=[['학생고유ID','측정시점','측정일','학년','척도','버전','상태','하위영역','점수']];
  researchState.responses.forEach(r=>{
    const wave=researchState.waves.find(w=>w.id===r.waveId),instrument=researchState.instruments.find(i=>i.id===r.instrumentId);
    const scores=Object.entries(r.scores);if(!scores.length)scores.push(['','']);
    scores.forEach(([dimension,value])=>rows.push([r.studentUuid,wave?.label||'',wave?.date||'',r.grade,instrument?.title||'',instrument?.version||'',r.status,dimension,value]));
  });
  const escape=value=>'"'+String(value??'').replace(/^[=+@-]/,"'$&").replace(/"/g,'""')+'"';
  const blob=new Blob(['\uFEFF'+rows.map(row=>row.map(escape).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='수학앱_자기효능감_동기_반복측정.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function exportResearchRawCSV(){
  if(!requireTeacher())return;
  const rows=[['학생고유ID','측정시점','실제응답시각','학년','척도','버전','상태','문항ID','하위영역','역채점','원응답']];
  researchState.responses.forEach(r=>{
    const w=researchState.waves.find(w=>w.id===r.waveId),i=researchState.instruments.find(i=>i.id===r.instrumentId);
    if(r.status!=='completed'){rows.push([r.studentUuid,w?.label,r.submittedAt,r.grade,i?.title,i?.version,r.status,'','','','']);return;}
    i.items.forEach(q=>rows.push([r.studentUuid,w?.label,r.submittedAt,r.grade,i.title,i.version,r.status,q.id,q.dimension,q.reverse?'역':'정',r.answers[q.id]]));
  });
  const escape=value=>'"'+String(value??'').replace(/^[=+@-]/,"'$&").replace(/"/g,'""')+'"';
  const blob=new Blob(['\uFEFF'+rows.map(row=>row.map(escape).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='수학앱_문항별_원응답.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
async function showStudentResearch(){
  if(SERVER_MODE&&!teacherMode){try{applyRemote(await api('/api/state'));}catch(error){alert(error.message);return;}}
  document.getElementById('studentWelcome').classList.add('hidden');document.getElementById('studentTasksPanel').classList.add('hidden');document.getElementById('studentResearchPanel').hidden=false;renderStudentResearch();document.getElementById('studentResearchTitle').focus();
}
function renderStudentResearch(){
  if(!students[currentStudentIndex])return;
  const st=students[currentStudentIndex],r=researchState;
  const waves=r.waves.filter(w=>w.participantIds.includes(st.uuid)&&w.participantSnapshot?.[st.uuid]?.grade===selectedLearningGrade);
  const entries=waves.flatMap(w=>w.instrumentIds.map(id=>({wave:w,instrument:r.instruments.find(i=>i.id===id)}))).filter(e=>e.instrument);
  document.getElementById('studentResearchList').innerHTML=entries.map(({wave:w,instrument:i})=>{
    const response=r.responses.find(x=>x.studentUuid===st.uuid&&x.waveId===w.id&&x.instrumentId===i.id),available=w.status==='open'&&!response&&r.participation[st.uuid]?.eligible;
    return `<div class="border rounded-xl p-4"><h4 class="font-bold">${escapeHtml(w.label)} · ${escapeHtml(i.title)}</h4><p class="text-xs text-slate-500 mt-2">${escapeHtml(w.date)} · ${response?(response.status==='completed'?'응답 완료':'이번 측정 참여 안 함'):w.status==='closed'?'마감 · 미응답':available?'응답 가능':'참여 확인 해제됨'}</p>${available?`<form onsubmit="submitResearchSurvey(event,this)" data-wave-id="${w.id}" data-instrument-id="${i.id}" class="space-y-5 mt-4">${i.items.map((q,index)=>`<fieldset><legend class="text-sm font-bold" data-copy-exclude>${index+1}. ${escapeHtml(q.text)}</legend><div class="flex flex-wrap gap-2 mt-2">${i.options.map((label,k)=>`<label class="border rounded-lg px-3 py-2 text-sm"><input type="radio" name="${q.id}" value="${i.min+k}" required> <span data-copy-exclude>${escapeHtml(label)}</span></label>`).join('')}</div></fieldset>`).join('')}<button ${teacherMode?'disabled':''} class="bg-indigo-600 text-white rounded-xl p-3 font-bold">설문 응답 제출</button><button type="button" ${teacherMode?'disabled':''} onclick="declineResearchSurvey('${w.id}','${i.id}')" class="text-sm text-slate-500 ml-3">이번 측정 참여하지 않기</button></form>`:''}</div>`;
  }).join('')||'<p class="text-sm text-slate-500">이 학년에 참여할 연구 설문이 없습니다.</p>';
}
async function submitResearchSurvey(event,form){
  event.preventDefault();if(!studentLoggedIn||teacherMode)return;const answers={};new FormData(form).forEach((value,key)=>answers[key]=Number(value));
  const button=form.querySelector('button');button.disabled=true;
  try{applyRemote(await api('/api/research/respond',{waveId:form.dataset.waveId,instrumentId:form.dataset.instrumentId,answers}));renderStudentResearch();alert('응답을 저장했습니다. 설문 응답은 과제 성취율이나 보상에 반영되지 않습니다.');}catch(error){alert(error.message);button.disabled=false;}
}
async function declineResearchSurvey(waveId,instrumentId){if(!studentLoggedIn||teacherMode)return;try{applyRemote(await api('/api/research/respond',{waveId,instrumentId,declined:true}));renderStudentResearch();}catch(error){alert(error.message);}}
