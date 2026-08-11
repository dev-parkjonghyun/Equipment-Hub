const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`switchMode,addBlockAt,attachBlock,detachBlock,acceptSlot,deleteSelectedBlocks,
 syncFromLayout,afterLayoutChange,reflowFromLayout,addFloorItem,deleteFloorMulti,removeLayoutBlockFor,
 rigParts,supportOf,specOf,clearScene,rootBlocks,build3D,renderFloor,renderCanvas,selToLayout,
 toggleSel,armKitOf,hRange,
 F:F,T:()=>THREE,cur:currentScene,EQ:()=>EQUIPMENT,setR3:v=>{R3=v},getR3:()=>R3,
 sel:()=>selectedIds,fm:()=>fMulti,setSel3:v=>{three3Sel=v},getSel3:()=>three3Sel`,{runTimers:true});
const A=H.api, THREE=A.T();
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const html=require('fs').readFileSync(APP,'utf-8');
function add(id,x,y){return A.addBlockAt(id,x||100,y||100);}
function link(cid,pid){const b=A.cur().blocks[cid];const eq=A.EQ().find(e=>e.id===b.eqId);
  const r=A.acceptSlot(pid,eq.cat);if(r)A.attachBlock(cid,pid,r);return r;}
const items=()=>Object.values(A.F().items);
const ids=()=>items().map(i=>i.eqId).sort();
H.ctx.confirm=()=>true;

console.log('=== 1. 배치도에 올리면 평면도·3D에 바로 생긴다 ===');
A.clearScene(); A.switchMode('layout');
t('처음엔 비어 있음', items().length===0);
const cam=add('CAM-003');
t('블록 올리자마자 평면도에 생김', ids().join()==='CAM-003', ids().join());
add('LIT-001');
t('두 번째도 자동 반영', ids().join()==='CAM-003,LIT-001', ids().join());
t('겹치지 않게 배치', (()=>{const p=items().map(i=>i.x+','+i.y);return new Set(p).size===p.length;})());
t('방 밖으로 안 나감', items().every(i=>i.x>=0&&i.x<=40&&i.y>=0&&i.y<=30));
t('높이 기본값 설정', items().every(i=>i.h3!==undefined), JSON.stringify(items().map(i=>i.h3)));

console.log('=== 2. 조립하면 부품도 따라간다 ===');
const trp=add('TRP-001',300,100); link(trp,cam);
const len=add('LEN-002',400,100); link(len,cam);
const ci=items().find(i=>i.eqId==='CAM-003');
t('부품 2개 전달', A.rigParts(ci).length===2, A.rigParts(ci).map(p=>p.slot).join(','));
t('삼각대 인식', A.supportOf(ci)==='TRP-001');
t('삼각대 높이 범위 적용', A.hRange(ci)[1]===1.73, A.hRange(ci).join('~'));
t('렌즈 스펙 반영', ci.focalMin===70&&ci.fstop===2.8, `${ci.focalMin}mm F${ci.fstop}`);
t('삼각대는 따로 안 놓임', !ids().includes('TRP-001'), ids().join());
// 렌즈 교체
const len2=add('LEN-005',500,100); link(len2,cam);
t('부품 교체가 바로 반영', A.rigParts(items().find(i=>i.eqId==='CAM-003')).some(p=>p.eqId==='LEN-005'));

console.log('=== 3. 분리하면 독립 장비가 된다 ===');
const before=ids().length;
A.detachBlock(trp,null);
t('분리한 삼각대가 평면도에 등장', ids().includes('TRP-001'), ids().join());
t('개수 증가', ids().length===before+1);
const ci2=items().find(i=>i.eqId==='CAM-003');
t('카메라 부품에서 빠짐', !A.rigParts(ci2).some(p=>p.eqId==='TRP-001'));
t('높이 범위도 되돌아감', A.hRange(ci2)[1]!==1.73, A.hRange(ci2).join('~'));

console.log('=== 4. 배치도에서 지우면 평면도·3D에서도 내려간다 ===');
const litBid=Object.entries(A.cur().blocks).find(([,b])=>b.eqId==='LIT-001')[0];
A.sel().clear(); A.sel().add(litBid);
A.deleteSelectedBlocks();
t('평면도에서 사라짐', !ids().includes('LIT-001'), ids().join());
t('나머지는 유지', ids().includes('CAM-003'));
t('삭제 안내에 반영', html.includes('평면도·3D에서도 ${sy.removed}개 내림'));

console.log('=== 5. 위치는 건드리지 않는다 ===');
const it=items().find(i=>i.eqId==='CAM-003');
it.x=7.5; it.y=4.25; it.h3=1.55;
A.syncFromLayout(false);
const it2=items().find(i=>i.eqId==='CAM-003');
t('직접 옮긴 위치 유지', it2.x===7.5&&it2.y===4.25, `${it2.x},${it2.y}`);
t('직접 맞춘 높이 유지', it2.h3===1.55, it2.h3);
// 새 장비를 추가해도 기존 위치는 그대로
add('AUD-003',600,300);
t('새 장비 추가해도 기존 위치 유지', items().find(i=>i.eqId==='CAM-003').x===7.5);
t('새 장비는 빈 자리에', items().find(i=>i.eqId==='AUD-003').x!==7.5);

console.log('=== 6. 재정렬은 수동일 때만 ===');
A.reflowFromLayout();
t('재정렬하면 위치 다시 깔림', items().find(i=>i.eqId==='CAM-003').x!==7.5,
  items().find(i=>i.eqId==='CAM-003').x);
t('재정렬 버튼 존재', html.includes('reflowFromLayout()')&&html.includes('배치도 기준 재정렬'));
t('확인 후 실행', html.includes('직접 옮겨둔 위치는 사라집니다'));
t('옛 가져오기 버튼 제거', !html.includes('배치도에서 가져오기'));

console.log('=== 7. 평면도에서 놓아도 배치도에 생긴다 ===');
A.clearScene(); A.switchMode('floor');
A.addFloorItem('MON-001',3,3);
t('평면도에 생김', ids().includes('MON-001'));
t('배치도에도 블록 생김', Object.values(A.cur().blocks).some(b=>b.eqId==='MON-001'));
t('놓은 자리 유지', items().find(i=>i.eqId==='MON-001').x===3);
// 동기화해도 사라지지 않음
A.syncFromLayout(false);
t('동기화 후에도 살아있음', ids().includes('MON-001'));
t('자리도 그대로', items().find(i=>i.eqId==='MON-001').x===3);

console.log('=== 8. 평면도에서 지우면 배치도에서도 ===');
const fid=Object.entries(A.F().items).find(([,i])=>i.eqId==='MON-001')[0];
A.fm().clear(); A.fm().add(fid);
A.deleteFloorMulti();
t('평면도에서 삭제', !ids().includes('MON-001'));
t('배치도에서도 삭제', !Object.values(A.cur().blocks).some(b=>b.eqId==='MON-001'));
t('다시 동기화해도 안 돌아옴', (()=>{A.syncFromLayout(false);return !ids().includes('MON-001');})());
// 조립 부품은 살아남는다
A.clearScene(); A.switchMode('layout');
const c2=add('CAM-001'); const t2=add('TRP-002',300,100); link(t2,c2);
t('조립 상태', A.rigParts(items().find(i=>i.eqId==='CAM-001')).length===1);
const fid2=Object.entries(A.F().items).find(([,i])=>i.eqId==='CAM-001')[0];
A.fm().clear(); A.fm().add(fid2); A.deleteFloorMulti();
t('부모만 내려감', !Object.values(A.cur().blocks).some(b=>b.eqId==='CAM-001'));
t('부품(삼각대)은 배치도에 남음', Object.values(A.cur().blocks).some(b=>b.eqId==='TRP-002'));
A.syncFromLayout(false);
t('남은 삼각대가 단독 장비로', ids().includes('TRP-002'), ids().join());

console.log('=== 9. 선택 상태 정리 ===');
A.clearScene(); A.switchMode('layout');
const b1=add('LIT-005');
A.syncFromLayout(false);
const f1=Object.entries(A.F().items).find(([,i])=>i.eqId==='LIT-005')[0];
A.setSel3(f1);
A.sel().clear(); A.sel().add(Object.entries(A.cur().blocks).find(([,b])=>b.eqId==='LIT-005')[0]);
A.deleteSelectedBlocks();
t('지운 장비의 3D 선택 해제', A.getSel3()===null, A.getSel3());
t('평면도 다중선택도 정리', A.fm().size===0);

console.log('=== 10. 화면 전환 시 항상 최신 ===');
t('평면도·3D 진입 시 동기화', html.includes("if (m === 'floor' || m === 'three') syncFromLayout(false);"));
t('결합 후 즉시 반영', html.includes('renderCanvas(); afterLayoutChange();'));
t('분리 후 즉시 반영', /detachBlock[\s\S]{0,600}afterLayoutChange\(\)/.test(html));
t('드롭 후 즉시 반영', html.includes('if (bid) { saveState(); renderPalette(); renderCanvas(); afterLayoutChange(); }'));
A.clearScene(); A.switchMode('layout');
add('LIT-009'); add('STD-A-001',300,100);
A.switchMode('three');
t('3D 진입 시 반영됨', ids().length===2, ids().join());
A.switchMode('floor');
t('평면도도 동일', ids().length===2);

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
