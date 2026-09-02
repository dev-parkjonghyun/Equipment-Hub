const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`openPane,togglePalette,switchMode,switchTab,renderSpacePane,renderRigPane,
 renderScenePane,selectRoom,deleteRoom,removeBg,focusBlock,gotoScene,setRigView,
 ensureFloor,finishRoom,attachBlock,acceptSlot,renderCanvas,renderFloor,newScene,
 cur:currentScene,st:()=>state,get pane(){return activePane},get rv(){return rigView},
 get sel(){return selectedIds}`);
const A=H.api;
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i||''))};
const S=()=>A.cur();

console.log('=== 1. 레일 5개 탭 ===');
['equip','sets','rig','scenes'].forEach(p=>{
  A.openPane(p);
  t(`${p} 패널 활성`, A.pane===p && H.store['pane-'+p].classList.contains('on'));
});

console.log('=== 2. 같은 탭 재클릭 = 접기 ===');
A.openPane('equip');
t('열림 상태', !H.store['app'].classList.contains('pal-hidden'));
A.openPane('equip');
t('같은 탭 재클릭 → 접힘', H.store['app'].classList.contains('pal-hidden'));
A.openPane('sets');
t('다른 탭 누르면 다시 펼쳐짐', !H.store['app'].classList.contains('pal-hidden'));
t('탭 화살표 방향', H.store['panel-tab'].textContent==='‹', H.store['panel-tab'].textContent);
A.togglePalette();
t('접으면 화살표 반전', H.store['panel-tab'].textContent==='›');
A.togglePalette();

console.log('=== 3. 하단 모드 도크 ===');
['layout','floor','three'].forEach(m=>{
  A.switchMode(m);
  const id=m==='layout'?'mode-layout':m==='floor'?'mode-floor':'mode-3d';
  t(`${m} 도크 활성`, H.store[id].classList.contains('on'));
  const others=['mode-layout','mode-floor','mode-3d'].filter(x=>x!==id);
  t(`  나머지 비활성`, others.every(x=>!H.store[x].classList.contains('on')));
});
A.switchMode('layout');

console.log('=== 5. 조립 패널 ===');
A.switchMode('layout');
const sc=S(); sc.blocks={};
const mk=e=>{const id='b'+Math.random().toString(36).slice(2,7);sc.blocks[id]={eqId:e,x:50,y:50};return id;};
const cam=mk('CAM-001');
const trp=mk('TRP-001'); A.attachBlock(trp,cam,A.acceptSlot(cam,'TRP'));
const len=mk('LEN-001'); A.attachBlock(len,cam,A.acceptSlot(cam,'LEN'));
const loose=mk('STD-A-001');
A.openPane('rig');
h=H.store['rig-body'].innerHTML;
t('조립체 목록 표시', h.includes('CAM-001'));
t('부품 개수 표시', h.includes('부품 2개'), h.match(/부품 \d+개/)||'');
t('단독 배치 구분', h.includes('단독 배치'));
t('결합 규칙 안내', h.includes('그립헤드·암 세트'));
A.setRigView('link');
A.renderRigPane();
t('표시방식 버튼 활성', H.store['rig-body'].innerHTML.includes('data-v="link" class="primary"'));
A.setRigView('nest');
A.focusBlock(cam);
t('클릭 시 블록 선택', A.sel.has(cam));

console.log('=== 6. 씬 패널 ===');
A.openPane('scenes');
h=H.store['scene-body'].innerHTML;
t('현재 씬 표시', h.includes('plist-item on'));
t('배치/평면 개수', h.includes('배치 4'), h.match(/배치 \d+/)||'');
t('씬 관리 버튼', h.includes('새 씬')&&h.includes('씬 삭제'));
t('저장 위치 안내(JSON 버튼 숨김)', (h.includes('서버에 저장')||h.includes('이 브라우저에만')) && !h.includes('파일로 저장') && !h.includes('파일 불러오기'));

console.log('=== 7. 기존 호환 ===');
A.switchTab('sets');
t('switchTab(sets) → 세트 패널', A.pane==='sets');
A.switchTab('equip');
t('switchTab(equip) → 장비 패널', A.pane==='equip');
t('팔레트 목록 유지', (H.store['palette-list'].innerHTML.match(/eq-card/g)||[]).length===112);
t('상태 저장', A.st().pane==='equip');

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
