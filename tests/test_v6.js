const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`togglePalette,setBgWidth,nudgeBg,toggleBgMove,syncBgUI,
 renderFloor,renderCanvas,build3D,switchMode,syncFromLayout,attachBlock,acceptSlot,
 ensureFloor,ensure3D,finishRoom,addRoomByNumbers,startRectResize,
 rigParts,partIn,supportOf,rigFootprint,rigHeight,rigRange,itemSize,setItemPos,showSel,
 buildItemMesh,specOf,footprintOf,roomArea,cur:currentScene,
 get sel3(){return three3Sel},set sel3(v){three3Sel=v},
 get bgMove(){return bgMove},EQ:EQUIPMENT,THREE:THREE`,{runTimers:true});
const A=H.api;
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i||''))};
const near=(a,b,e=0.01)=>Math.abs(a-b)<e;
const S=()=>A.cur();

console.log('=== 1. 팔레트 접기 ===');
A.togglePalette();
t('팔레트 숨김 클래스', H.store['app'].classList.contains('pal-hidden'));
A.togglePalette();
t('다시 보이기', !H.store['app'].classList.contains('pal-hidden'));

console.log('=== 2. 배경 도면 크기 조절 ===');
A.switchMode('floor');
const f=A.ensureFloor(S()); f.items={}; f.rooms=[]; f.subjects=[];
f.bg={data:'x',x:1,y:1,w:10,h:8,opacity:.55};
A.setBgWidth(5);
t('폭 10→5m', near(f.bg.w,5), f.bg.w);
t('높이 비율 유지 8→4m', near(f.bg.h,4), f.bg.h);
A.nudgeBg(1.1);
t('＋ 10% 확대', near(f.bg.w,5.5), f.bg.w);
A.nudgeBg(0.9);
t('－ 축소', near(f.bg.w,4.95,0.01), f.bg.w);
A.toggleBgMove();
t('도면 이동 모드 ON', A.bgMove===true);
A.toggleBgMove();
A.syncBgUI();
t('폭 입력칸 동기화', H.store['bg-w'].value==='4.95', H.store['bg-w'].value);

console.log('=== 3. 방 치수 정확 표기 ===');
f.rooms=[];
A.finishRoom(0,0,6.37,4.23);
const r=f.rooms[0];
t('저장은 소수 2자리', r.w===6.37 && r.h===4.23, `${r.w}x${r.h}`);
A.renderFloor();
const svg=H.store['floor-svg'].innerHTML;
t('가로 6.37m 표기', svg.includes('6.37m'), '표시안됨');
t('세로 4.23m 표기', svg.includes('4.23m'));
const area=(6.37*4.23).toFixed(2);
t(`면적 ${area}㎡ 표기 (곱과 일치)`, svg.includes(area+'㎡'), area);
// 다각형
f.rooms.push({id:'p1',name:'L',type:'poly',x:0,y:0,
  pts:[{x:0,y:0},{x:6,y:0},{x:6,y:2},{x:4,y:2},{x:4,y:4},{x:0,y:4}]});
A.renderFloor();
const svg2=H.store['floor-svg'].innerHTML;
t('다각형 면적 20.00㎡', svg2.includes('20.00㎡'));
{ const L=svg2.split('flabels')[1]||'';
  const lens=(L.match(/>[\d.]+m</g)||[]).length;
  t('다각형 변 길이 표시(6변)', lens>=6, lens+'개'); }

console.log('=== 4. 모듈 조립체 → 평면도 ===');
const sc=S(); sc.blocks={}; f.items={}; f.rooms=[];
A.finishRoom(0,0,8,6);
const mk=(e)=>{const id='b'+Math.random().toString(36).slice(2,7);sc.blocks[id]={eqId:e,x:100,y:100};return id;};
const cam=mk('CAM-001');
const trp=mk('TRP-001'); A.attachBlock(trp,cam,A.acceptSlot(cam,'TRP'));
const len=mk('LEN-002'); A.attachBlock(len,cam,A.acceptSlot(cam,'LEN'));
const sto=mk('STO-001'); A.attachBlock(sto,cam,A.acceptSlot(cam,'STO'));
const lit=mk('LIT-001');
const std=mk('STD-A-001'); A.attachBlock(std,lit,A.acceptSlot(lit,'STD'));
const mod=mk('MOD-002'); A.attachBlock(mod,lit,A.acceptSlot(lit,'MOD'));
A.syncFromLayout();
const items=Object.values(f.items);
t('조립체 2개만 가져옴 (부품 제외)', items.length===2, items.length);
const ci=items.find(i=>i.eqId==='CAM-001'), li=items.find(i=>i.eqId==='LIT-001');
t('카메라 부품 3개 동봉', A.rigParts(ci).length===3, A.rigParts(ci).length);
t('조명 부품 2개 동봉', A.rigParts(li).length===2);
t('지지대 인식 (삼각대)', A.supportOf(ci)==='TRP-001');
t('지지대 인식 (스탠드)', A.supportOf(li)==='STD-A-001');
t('렌즈 슬롯 조회', A.partIn(ci,'lens')==='LEN-002');

console.log('=== 5. 조립체 기준 발자국/높이 ===');
const fpCam=A.rigFootprint(ci);
t('카메라 발자국 = 삼각대 1.05m (0.3m 아님)', near(fpCam.w,1.05), fpCam.w);
t('조명 발자국 = A스탠드 0.9m', near(A.rigFootprint(li).w,0.9), A.rigFootprint(li).w);
t('카메라 높이 = 504X 기본 1.30m', near(ci.h3,1.30), ci.h3);
t('조명 높이 = LS-288 기본 2.00m', near(li.h3,2.00), li.h3);
const rg=A.rigRange(ci);
t('높이 범위 = 삼각대 0.435~1.73m', rg && near(rg.min,0.435) && near(rg.max,1.73), JSON.stringify(rg));
t('범위 출처 표기', rg.src==='TRP-001');
const rgL=A.rigRange(li);
t('조명 범위 = 스탠드 1.08~2.88m', near(rgL.min,1.08)&&near(rgL.max,2.88));

console.log('=== 6. 3D 조립 메시 ===');
A.switchMode('three');
A.ensure3D(S());
A.build3D();
const camMesh=A.buildItemMesh(A.EQ.find(e=>e.id==='CAM-001'),ci);
let n=0; camMesh.traverse(o=>{if(o.isMesh)n++;});
t('조립 카메라 메시 다수 (렌즈 포함)', n>=30, 'n='+n);
// 지지대 없는 단독 카메라와 비교
const solo={eqId:'CAM-001',x:0,y:0,h3:1.45,parts:[]};
const soloMesh=A.buildItemMesh(A.EQ.find(e=>e.id==='CAM-001'),solo);
let n2=0; soloMesh.traverse(o=>{if(o.isMesh)n2++;});
t('조립체가 단독보다 부품 많음', n>n2, `조립 ${n} vs 단독 ${n2}`);
// 조명+소프트박스
const litMesh=A.buildItemMesh(A.EQ.find(e=>e.id==='LIT-001'),li);
let n3=0; litMesh.traverse(o=>{if(o.isMesh)n3++;});
t('조명 조립체 메시', n3>=30, 'n='+n3);
// 바운딩: 소프트박스가 조명 앞으로 튀어나옴
litMesh.updateMatrixWorld(true);
const bb=new A.THREE.Box3().setFromObject(litMesh);
t('소프트박스로 깊이 확장', (bb.max.z-bb.min.z)>0.9, 'd='+(bb.max.z-bb.min.z).toFixed(2));

console.log('=== 7. X/Y/Z 위치 입력 ===');
const fid=Object.keys(f.items).find(k=>f.items[k].eqId==='CAM-001');
A.sel3=fid; A.showSel();
t('위치 패널 표시', H.store['item-panel'].style.display==='block');
t('X 입력값 채움', H.store['ip-x'].value===ci.x.toFixed(2), H.store['ip-x'].value);
A.setItemPos('x',3.5); t('X 이동', near(f.items[fid].x,3.5));
A.setItemPos('y',2.25); t('Z 이동', near(f.items[fid].y,2.25));
A.setItemPos('rot',90); t('회전', f.items[fid].rot===90);
A.setItemPos('h3',9);
t('높이는 삼각대 최대 1.73m로 제한', near(f.items[fid].h3,1.73), f.items[fid].h3);
A.setItemPos('h3',0.05);
t('최소 0.435m로 제한', near(f.items[fid].h3,0.435), f.items[fid].h3);
A.setItemPos('x',999);
t('월드 범위 클램프', f.items[fid].x<=40);
A.showSel();
t('패널에 부품 목록', H.store['ip-info'].innerHTML.includes('TRP-001'));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
