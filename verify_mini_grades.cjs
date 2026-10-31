const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const elements=new Map();
const element=id=>{if(!elements.has(id))elements.set(id,{hidden:false,innerHTML:'',textContent:''});return elements.get(id);};
const context=vm.createContext({document:{getElementById:element},adventureThemes:{},selectedLearningGrade:1,
  STAGES:[{id:1,unit:'1. 소인수분해'}],selectedRecord:()=>({miniBadges:[],miniAdventures:{}}),escapeHtml:String});
vm.runInContext(fs.readFileSync('math_quest_hideout.js','utf8'),context);
vm.runInContext("miniCatalog=[{id:'1-1',grade:1,unit:1,title:'소수와 합성수',story:'분류 연구소',ready:true}];renderMiniCatalog()",context);
assert(element('miniTopicCards').innerHTML.includes('소수와 합성수'));
assert(element('miniRegionFilters').innerHTML.includes('소인수분해'));
assert(!element('miniBadgeDetails').hidden);
for(const grade of [2,3]){
  context.selectedLearningGrade=grade;vm.runInContext('renderMiniCatalog()',context);
  assert.equal(element('miniRegionFilters').innerHTML,'');
  assert.equal(element('miniTopicCards').innerHTML,'');
  assert(element('miniCatalogNotice').textContent.includes(`중${grade} 작은 탐험은 아직 준비 중`));
  assert(element('miniBadgeDetails').hidden);
}
// A promoted student can still select the middle-1 record and see its catalog.
context.selectedLearningGrade=1;vm.runInContext('renderMiniCatalog()',context);
assert(element('miniTopicCards').innerHTML.includes("openMiniExploration('1-1')"));
assert(!element('miniBadgeDetails').hidden);
console.log('PASS: grade-specific catalog, no middle-1 topics on grades 2/3, previous-grade access restored.');
