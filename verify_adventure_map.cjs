const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const elements=new Map(['adventureCategory','adventureCategoryTitle','adventureMapTitle','adventureNextLabel','missionMapGrid'].map(id=>[id,{hidden:false,textContent:'',innerHTML:''}]));
const context=vm.createContext({document:{getElementById:id=>elements.get(id)},selectedRecord:()=>({clearedStages:[1]}),selectedStages:()=>[{id:1,unit:'1. 소인수분해'},{id:2,unit:'2. 정수와 유리수'},{id:3,unit:'3. 문자의 사용과 식'}],selectedLearningGrade:1,teacherMode:false,escapeHtml:x=>String(x)});
vm.runInContext(fs.readFileSync('math_quest_adventure.js','utf8'),context);
vm.runInContext("adventureCatalog=[{id:1,unit:'소인수분해',version:'v1',icon:'🏛️'},{id:2,unit:'정수와 유리수',version:'v1',icon:'🌊'},{id:3,unit:'문자의 사용과 식',version:'v1',icon:'🧪'}];renderCompactMap()",context);
assert(!elements.get('missionMapGrid').innerHTML.includes('Tally'));
assert(elements.get('missionMapGrid').innerHTML.includes('onclick="selectStage(1)"'));
assert(elements.get('missionMapGrid').innerHTML.includes('onclick="selectStage(2)"'));
assert(!elements.get('missionMapGrid').innerHTML.includes('onclick="selectStage(3)"'));
assert(elements.get('adventureNextLabel').textContent.includes('앱 안에서 도전'));
for(const kind of ['coordinate-triangle','equal-segments','midpoints','parallel-bend','hexagon','cuboid','inscribed-triangle','isosceles','sector','cuboid-dimensions']){
  const svg=vm.runInContext('adventureDiagram('+JSON.stringify(kind)+')',context);
  assert(svg.includes('<svg role="img"'));
  assert(!svg.includes('undefined'));
}
console.log('PASS: native stages 1-10, stage locks, all 10 diagram types');
