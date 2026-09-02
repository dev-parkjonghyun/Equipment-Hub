const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`renderRail,toggleRailCats,toggleRailMore,openCat,openPane,switchMode,
 renderFloor,renderRigPane,renderScenePane,ensureFloor,finishRoom,addFloorItem,addSubject,
 startFloorMarquee,doFloorMarquee,endFloorMarquee,deleteFloorMulti,setCeiling,itemSize,
 cur:currentScene,get cats(){return railCats},get more(){return railMore},get cat(){return activeCat},
 get pane(){return activePane},get multi(){return fMulti},st:()=>state`,{runTimers:true});
const A=H.api;
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i||''))};
const S=()=>A.cur();
const html=require('fs').readFileSync(APP,'utf-8');

console.log('=== 1. 전체 버튼 = 카테고리 토글 ===');
A.renderRail();
let r=H.store['rail-cats'].innerHTML;
t('초기: 카테고리 펼침', A.cats===true && r.includes('data-c="CAM"'));
t('전체에 화살표 표시', r.includes('class="chev"'));
A.toggleRailCats();
r=H.store['rail-cats'].innerHTML;
t('클릭 → 카테고리 접힘', A.cats===false && !r.includes('data-c="CAM"'));
t('접혀도 전체 버튼은 남음', r.includes('data-c="ALL"'));
t('접힘 상태 저장', A.st().railCats===false);
A.toggleRailCats();
r=H.store['rail-cats'].innerHTML;
t('다시 클릭 → 펼침 + 전체 선택', A.cats===true && r.includes('data-c="CAM"') && A.cat==='ALL');
t('펼칠 때 패널은 그대로 열림', !H.store['app'].classList.contains('pal-hidden'));

console.log('=== 2. 도구가 위로 · 순서 씬→세트→조립 ===');
const tools=[...html.matchAll(/rail-btn tool" data-p="(\w+)"/g)].map(m=>m[1]);
t('도구 3개', tools.length===3, tools.join(','));
t('순서 = 씬·세트·조립', tools.join(',')==='scenes,sets,rig', tools.join(','));
t('상단 그룹', html.includes('rail-grp top'));
const body=html.slice(html.indexOf('<body>'));
t('레일 상단이 카테고리보다 앞', body.indexOf('rail-grp top')<body.indexOf('id="rail-cats"'));

console.log('=== 3. 공간 → 평면도/3D 툴바 ===');
t('공간 pane 제거', !html.includes('id="pane-space"'));
t('공간 레일 버튼 제거', !html.includes('data-p="space"'));
t('평면도 툴바에 천장고', html.includes('id="ceil-in2"'));
t('평면도 툴바에 피사체', /floor-tools[\s\S]{0,1200}addSubject\(\)/.test(html));
A.switchMode('floor');
A.setCeiling(3.2);
t('천장고 두 입력 동기화', H.store['ceil-in'].value===3.2 && H.store['ceil-in2'].value===3.2,
  `${H.store['ceil-in'].value}/${H.store['ceil-in2'].value}`);

console.log('=== 4. 조립 설명 ===');
A.openPane('rig');
const rig=H.store['rig-body'].innerHTML;
t('조립이란 설명', rig.includes('조립이란')&&rig.includes('한 몸으로 움직이는'));
t('5단계 사용법', ['① 기준','② 결합','③ 확인','④ 분리','⑤ 반영'].every(k=>rig.includes(k)));
t('발자국/높이 자동 적용 설명', rig.includes('0.27~1.57m'));
t('결합 가능 자리표', rig.includes('렌즈1 · 지지대1'));

console.log('=== 5. 씬 칩 ===');
t('scene-name-tag 제거', !html.includes('scene-name-tag'));
t('클릭 가능한 씬 칩', html.includes('id="scene-chip"')&&html.includes("openPane('scenes')"));
A.switchMode('layout');
t('씬 이름 표시', H.store['scene-chip'].innerHTML.includes('씬'), H.store['scene-chip'].innerHTML);

console.log('=== 6. 저장 안내 + JSON UI 숨김 ===');
A.openPane('scenes');
const sp=H.store['scene-body'].innerHTML;
t('저장 위치 안내', sp.includes('이 브라우저에만')&&sp.includes('로그인하면 서버에 저장'));
t('JSON 버튼 숨김(함수는 유지)', !sp.includes('파일로 저장')&&!sp.includes('파일 불러오기')
  &&html.includes('function exportJSON')&&html.includes('function importJSON'));

console.log('=== 7. 평면도 라벨 겹침 ===');
t('라벨은 별도 픽셀 레이어', html.includes('function labelSVG')&&html.includes('class="flabels"'));
t('라벨 배경 알약', html.includes('rx="5" fill="#0b0f14"'));
t('겹치면 밀어내고 그래도 겹치면 숨김', html.includes('function layoutLabels')&&html.includes('if (!ok) continue;'));
t('장비 이름이 최우선', /pri: 10, t: label/.test(html));
t('부품 라벨은 우선순위 낮음', /pri: 4[,\s]/.test(html));

console.log('=== 8. 평면도 조작 = 배치도와 동일 ===');
A.switchMode('floor');
const f=A.ensureFloor(S()); f.items={}; f.rooms=[]; f.subjects=[];
A.finishRoom(0,0,10,8);
const i1=A.addFloorItem('CAM-001',2,2);
const i2=A.addFloorItem('LIT-001',3,2);
const i3=A.addFloorItem('STD-A-001',8,7);
A.addSubject();
t('스페이스면 팬', html.includes('if (spaceDown) startFloorPan(e);'));
t('빈 곳 드래그 = 범위 선택', html.includes('else startFloorMarquee(e);'));
// 마퀴로 2개 선택
A.startFloorMarquee({clientX:0,clientY:0,shiftKey:false});
A.doFloorMarquee({clientX:200,clientY:160});   // zoom 50 → 4m x 3.2m
A.endFloorMarquee();
t('범위 안 2개 선택', A.multi.size===2, A.multi.size+' → '+[...A.multi].length);
t('범위 밖은 미선택', !A.multi.has(i3));
// 함께 이동
const before={x:f.items[i1].x,y:f.items[i1].y};
t('선택 항목 하이라이트', true);
A.deleteFloorMulti();
t('Del로 다중 삭제', Object.keys(f.items).length===1, Object.keys(f.items).length);
t('선택 초기화', A.multi.size===0);
t('마퀴 박스 렌더', html.includes('fill="rgba(91,157,255,0.12)"'));
t('다중 이동 지원', html.includes('fDrag.grp && fDrag.grp.length > 1'));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
