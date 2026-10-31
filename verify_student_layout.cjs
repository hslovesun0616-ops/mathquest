const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const elements=new Map();
function el(id){if(!elements.has(id))elements.set(id,{hidden:false,open:false,textContent:'',attrs:{},classList:{add(){},remove(){}},setAttribute(k,v){this.attrs[k]=v},focus(){}});return elements.get(id);}
const context=vm.createContext({document:{getElementById:el},students:[{uuid:'a'}],currentStudentIndex:0,selectedLearningGrade:1,selectedMiniCatalog:()=>[{}],applyStudentCopy(){},renderGrowthPassport(){},renderStudentTasks(){},renderStudentResearch(){}});
vm.runInContext(fs.readFileSync('math_quest_student_layout.js','utf8'),context);
vm.runInContext('syncStudentLayout()',context);
assert(!el('studentHideoutArea').hidden);assert(el('studentLearningArea').hidden);assert(!el('studentCollection').open);
for(const category of ['tasks','mini','adventure']){
  vm.runInContext(`showLearningCategory('${category}');syncStudentLayout()`,context);
  assert(el('studentHideoutArea').hidden);assert(!el('studentLearningArea').hidden);
  const ids={tasks:'studentTasksPanel',mini:'miniExplorationSection',adventure:'studentAdventurePanel'};
  assert.deepEqual(Object.entries(ids).filter(([,id])=>!el(id).hidden).map(([key])=>key),[category]);
}
vm.runInContext("showStudentArea('hideout');showCollection('stamps')",context);
assert(!el('studentHideoutArea').hidden);assert(el('studentLearningArea').hidden);
assert(el('collectionPanel-big').hidden);assert(el('collectionPanel-mini').hidden);assert(!el('collectionPanel-stamps').hidden);
vm.runInContext("showStudentArea('growth')",context);assert(!el('studentGrowthArea').hidden);assert(el('studentHideoutArea').hidden);assert(el('studentLearningArea').hidden);
context.selectedLearningGrade=2;vm.runInContext('syncStudentLayout()',context);
assert(!el('studentHideoutArea').hidden);assert.equal(el('collectionGradeLabel').textContent,2);
console.log('PASS: two main areas, one learning activity at a time, one collection tab, grade changes reset navigation.');
