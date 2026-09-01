// 배경 리그(ASSY-BGS-001): 작은 A스탠드 2대 + 크로스바 봉(ACC-006) 조립 시각화.
const {makeHarness}=require('./harness.js');
const H=makeHarness(`buildBackdropRig,buildItemMesh,valensVl3000g,backdropRig,specOf,
 addBlockAt,switchMode,syncFromLayout,clearScene,
 F:F,T:()=>THREE,cur:currentScene,EQ:()=>EQUIPMENT`,{runTimers:true});
const A=H.api, THREE=A.T();
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const nodes=o=>{let n=0;o.traverse(m=>{if(m.isMesh)n++;});return n;};
const dim=o=>{o.updateMatrixWorld(true);const b=new THREE.Box3().setFromObject(o);
  return {x:b.max.x-b.min.x,y:b.max.y-b.min.y,z:b.max.z-b.min.z};};
H.ctx.__confirm=true;

console.log('=== 1. 크로스바 봉(ACC-006) ===');
const cb=A.specOf('ACC-006');
t('ACC-006 스펙 등록', cb && cb.len===3.20 && cb.sections===4, JSON.stringify(cb&&{len:cb.len}));
const bar=A.valensVl3000g(cb);
t('봉 메시 생성', nodes(bar)>=1, nodes(bar));
{ const d=dim(bar); t('봉은 가로(X)로 길다', d.x>d.y*5 && d.x>2.5, JSON.stringify(d)); }
// dispatch: ACC-006 단독 = 봉만
const barMesh=A.buildItemMesh(A.EQ().find(e=>e.id==='ACC-006'),{eqId:'ACC-006',x:0,y:0,h3:1.5,rot:0});
t('단독 ACC-006 → 봉 그림', nodes(barMesh)>=1, nodes(barMesh));

console.log('=== 2. backdropRig 조립 ===');
const rig=A.backdropRig({h:2.30,span:2.90,sections:4});
t('스탠드 2대 + 봉 → 메시 다수', nodes(rig)>=13, nodes(rig));
{ const d=dim(rig);
  t('가로로 넓게 벌어짐(스탠드 간격)', d.x>2.5, JSON.stringify(d));
  t('스탠드 높이만큼 섬(약 2.3m)', d.y>2.0, d.y); }

console.log('=== 3. 씬에 3개가 함께 있으면 리그로 대체 ===');
A.clearScene(); A.switchMode('layout');
A.addBlockAt('STD-AS-001',100,300);
A.addBlockAt('STD-AS-002',400,300);
A.addBlockAt('ACC-006',250,300);
A.switchMode('floor'); A.syncFromLayout();
const rr=A.buildBackdropRig(A.F());
t('세 개 모이면 리그 생성', !!rr, rr);
t('세 아이템 모두 개별 렌더에서 제외', rr && rr.skip.size===3, rr&&rr.skip.size);
t('리그 메시가 실제로 있음', rr && nodes(rr.mesh)>=13, rr&&nodes(rr.mesh));

console.log('=== 4. 하나라도 빠지면 리그 아님 ===');
A.clearScene(); A.switchMode('layout');
A.addBlockAt('STD-AS-001',100,300);
A.addBlockAt('ACC-006',250,300);
A.switchMode('floor'); A.syncFromLayout();
t('스탠드 1대 + 봉 = 리그 아님(개별 렌더)', A.buildBackdropRig(A.F())===null);

console.log('=== 5. 리그는 두 스탠드 사이 간격/방향을 따른다 ===');
A.clearScene(); A.switchMode('layout');
A.addBlockAt('STD-AS-001',0,0);
A.addBlockAt('STD-AS-002',300,0);   // 배치도 px → 평면도 m 로 변환됨
A.addBlockAt('ACC-006',150,0);
A.switchMode('floor'); A.syncFromLayout();
const rr2=A.buildBackdropRig(A.F());
t('리그 생성됨', !!rr2);
{ const d=dim(rr2.mesh); t('두 스탠드 간격만큼 벌어짐', d.x>1.0, JSON.stringify(d)); }

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
