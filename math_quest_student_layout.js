let studentArea='hideout',learningCategory='tasks',collectionCategory='big',studentLayoutIdentity='';
function syncStudentLayout(){
  const st=students[currentStudentIndex];if(!st)return;
  const identity=st.uuid+':'+selectedLearningGrade;
  if(studentLayoutIdentity!==identity){studentLayoutIdentity=identity;studentArea='hideout';learningCategory='tasks';collectionCategory='big';document.getElementById('studentCollection').open=false;}
  document.getElementById('studentHideoutArea').hidden=studentArea!=='hideout';
  document.getElementById('studentLearningArea').hidden=studentArea!=='learning';
  document.getElementById('studentGrowthArea').hidden=studentArea!=='growth';
  document.getElementById('studentResearchPanel').hidden=false;
  ['hideout','learning','growth'].forEach(area=>document.getElementById('studentArea-'+area).setAttribute('aria-pressed',String(studentArea===area)));
  const panels={tasks:'studentTasksPanel',mini:'miniExplorationSection',adventure:'studentAdventurePanel'};
  Object.entries(panels).forEach(([key,id])=>{const panel=document.getElementById(id);panel.hidden=key!==learningCategory;panel.classList.remove('hidden');document.getElementById(key==='tasks'?'tasksCategory':key==='mini'?'miniCategory':key==='adventure'?'adventureCategory':'researchCategory').setAttribute('aria-pressed',String(key===learningCategory));});
  document.getElementById('studentWelcome').classList.add('hidden');
  document.getElementById('collectionGradeLabel').textContent=selectedLearningGrade;
  document.getElementById('miniCollectionEmpty').hidden=selectedMiniCatalog().length>0;
  document.getElementById('miniCollectionEmpty').textContent=`중${selectedLearningGrade} 작은 탐험 배지는 콘텐츠와 함께 준비 중이에요.`;
  ['big','mini','stamps'].forEach(key=>{document.getElementById('collection-'+key).setAttribute('aria-pressed',String(key===collectionCategory));document.getElementById('collectionPanel-'+key).hidden=key!==collectionCategory;});
  renderGrowthPassport();
}
function showStudentArea(area){studentArea=area;syncStudentLayout();applyStudentCopy();}
function showLearningCategory(category){studentArea='learning';learningCategory=category;syncStudentLayout();applyStudentCopy();}
function showCollection(category){collectionCategory=category;syncStudentLayout();applyStudentCopy();}
function showStudentTasks(){showLearningCategory('tasks');renderStudentTasks();document.getElementById('studentTasksTitle').focus();}
async function showStudentResearch(){
  if(SERVER_MODE&&!teacherMode){try{applyRemote(await api('/api/state'));}catch(error){alert(error.message);return;}}
  showStudentArea('growth');renderStudentResearch();document.getElementById('studentResearchTitle').focus();
}
