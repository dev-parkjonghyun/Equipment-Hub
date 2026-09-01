// 차량 적재 체크리스트: 열거·카테고리 그룹·부품 포함·토글·진행률·초기화·저장.
const {makeHarness}=require('./harness.js');
const H=makeHarness(`checklistItems,checklistProgress,renderChecklist,openChecklist,closeChecklist,
 toggleCheck,resetChecklist,addBlockAt,attachBlock,acceptSlot,clearScene,switchMode,
 cur:currentScene,EQ:()=>EQUIPMENT`,{runTimers:true});
const A=H.api;
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
H.ctx.__confirm=true;

function add(id,x,y){const b=A.addBlockAt(id,x,y);if(!b)throw new Error('추가실패 '+id);return b;}
function link(cid,pid){const b=A.cur().blocks[cid];const eq=A.EQ().find(e=>e.id===b.eqId);
  const r=A.acceptSlot(pid,eq.cat);if(!r)throw new Error('슬롯거부 '+b.eqId);A.attachBlock(cid,pid,r);return r.slot;}

// 카메라 + 렌즈·배터리·메모리 + 조명 하나 배치
A.clearScene(); A.switchMode('layout');
const cam=add('CAM-003',100,100);
link(add('LEN-002',300,100),cam);
link(add('BAT-FZ-001',400,100),cam);
link(add('STO-001',500,100),cam);
add('LIT-001',700,100);

console.log('=== 1. 열거 · 카테고리 그룹 · 부품 포함 ===');
const groups=A.checklistItems();
const catOf=c=>groups.find(g=>g.cat===c);
t('카메라 그룹 존재', !!catOf('CAM'));
t('렌즈 그룹 존재(부품도 별도 항목)', !!catOf('LEN'));
t('배터리 그룹 존재', !!catOf('BAT'));
t('저장매체 그룹 존재', !!catOf('STO'));
t('조명 그룹 존재', !!catOf('LIT'));
t('카메라 순서가 조명보다 앞(CAT_ORDER)', groups.findIndex(g=>g.cat==='CAM')<groups.findIndex(g=>g.cat==='LIT'));
const total=groups.reduce((s,g)=>s+g.items.length,0);
t('전체 5개(카메라1+렌즈1+배터리1+메모리1+조명1)', total===5, total);
// 부품 슬롯 이름
const lenItem=catOf('LEN').items[0];
t('렌즈 항목이 부품으로 표시', lenItem.isPart===true);
t('부품 슬롯 이름(렌즈)', lenItem.slotName==='렌즈', lenItem.slotName);
t('항목에 자산번호(id) 포함', /^CAM-003$/.test(catOf('CAM').items[0].id));
t('항목 표시명 존재', typeof catOf('CAM').items[0].name==='string' && catOf('CAM').items[0].name.length>0);

console.log('=== 2. 진행률 · 토글 ===');
let p=A.checklistProgress();
t('처음엔 0/5', p.done===0 && p.total===5, `${p.done}/${p.total}`);
const camBid=Object.keys(A.cur().blocks).find(k=>A.cur().blocks[k].eqId==='CAM-003');
A.toggleCheck(camBid);
p=A.checklistProgress();
t('카메라 체크 후 1/5', p.done===1 && p.total===5, `${p.done}/${p.total}`);
t('scene.checked 에 기록', A.cur().checked[camBid]===true);
A.toggleCheck(camBid);
p=A.checklistProgress();
t('다시 누르면 해제 0/5', p.done===0, p.done);
t('scene.checked 에서 제거', !A.cur().checked[camBid]);

console.log('=== 3. 저장(localStorage) 반영 ===');
A.toggleCheck(camBid);
const saved=JSON.parse(H.ctx.localStorage.getItem('eh_layout_v1'));
const savedScene=saved.scenes[saved.currentScene];
t('저장된 씬에 checked 포함', !!(savedScene.checked && savedScene.checked[camBid]));

console.log('=== 4. 렌더 HTML ===');
A.openChecklist();
const html=H.store['cl-body']._html || '';
t('체크박스 행 렌더', html.includes('cl-row') && html.includes('cl-box'));
t('자산번호 렌더', html.includes('CAM-003'));
t('부품 슬롯 태그 렌더', html.includes('cl-part-tag'));
t('체크된 행은 done 표시', html.includes('cl-row done'));
t('진행률 텍스트 갱신', (H.store['cl-prog']._html||'').includes('실음'));
t('열면 화면 표시(flex)', H.store['checklist-view'].style.display==='flex');
// '안 실은 것만' 필터
H.store['cl-only'].checked=true;
A.renderChecklist();
const html2=H.store['cl-body']._html || '';
t('안 실은 것만: 체크된 카메라 행 숨김', !html2.includes('>CAM-003<') && html2.includes('cl-row'), 'filtered');
H.store['cl-only'].checked=false;

console.log('=== 5. 전체 해제 · 닫기 ===');
A.toggleCheck(Object.keys(A.cur().blocks).find(k=>A.cur().blocks[k].eqId==='LEN-002'));
t('해제 전 2개 체크', A.checklistProgress().done===2, A.checklistProgress().done);
A.resetChecklist();
t('전체 해제 후 0개', A.checklistProgress().done===0);
t('checked 비워짐', Object.keys(A.cur().checked).length===0);
A.closeChecklist();
t('닫으면 숨김(none)', H.store['checklist-view'].style.display==='none');

console.log('=== 6. 빈 씬 안전 처리 ===');
A.clearScene();
const empty=A.checklistItems();
t('빈 씬은 그룹 없음', empty.length===0, empty.length);
A.renderChecklist();
t('빈 씬 안내문 렌더', (H.store['cl-body']._html||'').includes('배치된 장비가 없습니다'));
t('빈 씬 진행률 0/0 안내', (H.store['cl-prog']._html||'').includes('장비가 없습니다'));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
