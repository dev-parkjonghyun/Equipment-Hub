const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`renderCanvas,renderPalette,setRigView,attachBlock,detachBlock,acceptSlot,
 slotsFor,rootBlocks,childBlocks,descendantBlocks,eqOfBlock,slotUsed,isAncestor,removeBlockTree,
 blockPos,createGroup,selectedBlockIds,snapAll,autoArrangeByCategory,placedEqSet,
 ROOT:ROOT_CATS,SLOTS:SLOTS,cur:currentScene,get sel(){return selectedIds},
 get view(){return rigView},EQ:EQUIPMENT`);
const A=H.api;
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i||''))};
const S=()=>A.cur();
function mk(eqId,x,y){const id='b'+Math.random().toString(36).slice(2,8);
  S().blocks[id]={eqId,x:x||0,y:y||0};return id;}
function reset(){S().blocks={};S().groups={};A.sel.clear();}

console.log('=== 1. 최상위는 카메라·조명 ===');
t('루트 카테고리 = CAM, LIT', A.ROOT.join(',')==='CAM,LIT');
t('카메라 슬롯 6종', A.SLOTS.CAM.length===6, A.SLOTS.CAM.map(s=>s.n).join('/'));
t('조명 슬롯 4종', A.SLOTS.LIT.length===4, A.SLOTS.LIT.map(s=>s.n).join('/'));
t('카메라에 지지대 슬롯', A.SLOTS.CAM.some(s=>s.k==='support'&&s.accept.includes('TRP')));
t('조명에 스탠드 슬롯', A.SLOTS.LIT.some(s=>s.k==='support'&&s.accept.includes('STD')));

console.log('=== 2. 결합 규칙 ===');
reset();
const cam=mk('CAM-001',100,100);
t('카메라에 렌즈 OK', A.acceptSlot(cam,'LEN').ok===true);
t('카메라에 삼각대 = 지지대', A.acceptSlot(cam,'TRP').slot==='support');
t('카메라에 짐벌도 지지대', A.acceptSlot(cam,'GIM').slot==='support');
t('카메라에 메모리', A.acceptSlot(cam,'STO').slot==='card');
t('카메라에 배터리', A.acceptSlot(cam,'BAT').slot==='batt');
t('카메라에 모니터 = 슈', A.acceptSlot(cam,'MON').slot==='shoe');
const lit=mk('LIT-001',400,100);
t('조명에 스탠드', A.acceptSlot(lit,'STD').ok===true);
t('조명에 소프트박스', A.acceptSlot(lit,'MOD').slot==='mod');
t('조명에 조명 = 경고', A.acceptSlot(lit,'LIT').ok===false);

console.log('=== 3. 실제 조립 ===');
const len=mk('LEN-001'), trp=mk('TRP-001'), sto=mk('STO-001'), bat=mk('BAT-FZ-001');
A.attachBlock(len,cam,A.acceptSlot(cam,'LEN'));
A.attachBlock(trp,cam,A.acceptSlot(cam,'TRP'));
A.attachBlock(sto,cam,A.acceptSlot(cam,'STO'));
A.attachBlock(bat,cam,A.acceptSlot(cam,'BAT'));
t('카메라 하위 4개', A.childBlocks(cam).length===4);
t('삼각대가 카메라의 자식', S().blocks[trp].parent===cam && S().blocks[trp].slot==='support');
t('루트는 카메라·조명 2개', A.rootBlocks().length===2, A.rootBlocks().length);
const filt=mk('ACC-010');
A.attachBlock(filt,len,A.acceptSlot(len,'ACC'));
t('렌즈에 필터 (2단계 깊이)', S().blocks[filt].parent===len);
t('카메라 전체 하위 5개', A.descendantBlocks(cam).length===5);

console.log('=== 4. 슬롯 개수 제한 ===');
const len2=mk('LEN-002');
const r=A.acceptSlot(cam,'LEN');
t('렌즈 슬롯 이미 참 → 경고', r.ok===false && r.full===true, JSON.stringify(r));
const sto2=mk('STO-003');
t('메모리는 2개까지 → 정상', A.acceptSlot(cam,'STO').ok===true);
A.attachBlock(sto2,cam,A.acceptSlot(cam,'STO'));
t('메모리 2개 장착됨', A.slotUsed(cam,'card')===2);
t('3번째 메모리는 경고', A.acceptSlot(cam,'STO').ok===false);

console.log('=== 5. C스탠드 그립암 ===');
const cstd=A.EQ.find(e=>e.id==='STD-C-001');
const cs=A.slotsFor(cstd);
t('C스탠드에 그립암 슬롯', cs.some(s=>s.k==='arm'), cs.map(s=>s.n).join('/'));
t('일반 A스탠드엔 그립암 없음',
  !A.slotsFor(A.EQ.find(e=>e.id==='STD-A-001')).some(s=>s.k==='arm'));

console.log('=== 6. 순환 참조 방지 ===');
t('렌즈는 카메라의 하위', A.isAncestor(cam,len)===true);
t('필터도 카메라 하위', A.isAncestor(cam,filt)===true);
t('카메라는 렌즈의 하위 아님', A.isAncestor(len,cam)===false);

console.log('=== 7. 분리 ===');
A.detachBlock(trp,null);
t('삼각대 분리 → 루트로', !S().blocks[trp].parent);
t('루트 4개 (카메라·조명·미장착렌즈·삼각대)', A.rootBlocks().length===4, A.rootBlocks().length);
t('분리된 블록에 좌표 부여', S().blocks[trp].x>0);
t('카메라 하위 5개로 감소 (삼각대 빠짐)', A.descendantBlocks(cam).length===5, A.descendantBlocks(cam).length);

console.log('=== 8. 제거 시 하위 함께 ===');
const before=Object.keys(S().blocks).length;
A.removeBlockTree(cam);
t('카메라+하위 5개 = 6개 제거', Object.keys(S().blocks).length===before-6,
  `${before}→${Object.keys(S().blocks).length}`);

console.log('=== 9. 표시 모드 ===');
reset();
const c2=mk('CAM-003',200,150);
const l2=mk('LEN-002'); A.attachBlock(l2,c2,A.acceptSlot(c2,'LEN'));
const t2=mk('TRP-002'); A.attachBlock(t2,c2,A.acceptSlot(c2,'TRP'));
['nest','link','fold'].forEach(v=>{
  A.setRigView(v);
  t(`${v} 모드 전환`, A.view===v);
});
A.setRigView('link');
const p1=A.blockPos(l2,S()), p2=A.blockPos(t2,S());
t('선연결: 자식이 부모 아래로 수직 배치', p1.y>150 && p2.y>150, JSON.stringify([p1,p2]));
t('선연결: 자식끼리 세로로 벌어짐', p2.y>p1.y, `${p1.y} vs ${p2.y}`);
A.setRigView('nest');

console.log('=== 10. 기존 기능 호환 ===');
reset();
const a=mk('CAM-001',100,100), b=mk('LIT-001',300,100), c=mk('LIT-002',500,100);
const kid=mk('LEN-001'); A.attachBlock(kid,a,A.acceptSlot(a,'LEN'));
t('팔레트 배치 판정에 자식 포함', A.placedEqSet().has('LEN-001'));
A.sel.clear(); [a,b,kid].forEach(i=>A.sel.add(i));
t('선택 목록은 루트만', A.selectedBlockIds().length===2, A.selectedBlockIds().length);
A.sel.clear(); [a,b,c].forEach(i=>A.sel.add(i));
A.createGroup();
t('그룹 생성 (루트 3개)', Object.keys(S().groups).length===1);
S().blocks[a].x=37; S().blocks[a].y=113;
A.snapAll();
t('격자 맞춤이 루트에만 적용', S().blocks[a].x===40 && S().blocks[a].y===120);
t('자식은 좌표 없음(부모 종속)', S().blocks[kid].x===undefined||S().blocks[kid].x===0);

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
