// 조명·모디파이어 전용 3D 모델(제품별 형태) 검증.
const {APP}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`cobHeadMesh,isForza500,lanternMesh,isLanternSoftbox,projectionMesh,isProjection,
 buildItemMesh,specOf,T:()=>THREE,EQ:()=>EQUIPMENT`,{runTimers:true});
const A=H.api, THREE=A.T();
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const nodes=o=>{let n=0;o.traverse(m=>{if(m.isMesh)n++;});return n;};
const dim=o=>{o.updateMatrixWorld(true);const b=new THREE.Box3().setFromObject(o);
  return {x:b.max.x-b.min.x, y:b.max.y-b.min.y, z:b.max.z-b.min.z};};
const build=id=>A.buildItemMesh(A.EQ().find(e=>e.id===id),{eqId:id,x:0,y:0,h3:1.6,rot:0});

console.log('=== 1. 인식(제품 매칭) ===');
t('Forza 500 인식(LIT-001)', A.isForza500({id:'LIT-001'}));
t('제품명으로도(Forza 500)', A.isForza500({product:'NANLITE Forza 500B II'}));
t('60B는 Forza500 아님', !A.isForza500({id:'LIT-005',product:'Forza 60B'}));
t('랜턴 소프트박스(MOD-003)', A.isLanternSoftbox({id:'MOD-003'}));
t('JEMBALL 이름 매칭', A.isLanternSoftbox({product:'Forza 500 JEMBALL'}));
t('프로젝션(MOD-004)', A.isProjection({id:'MOD-004'}));
t('PJ-FZ60 이름 매칭', A.isProjection({product:'NANLITE PJ-FZ60'}));
t('일반 소프트박스는 프로젝션 아님', !A.isProjection({id:'MOD-001',product:'Softbox 60b'}));

console.log('=== 2. COB 헤드(Forza 500) ===');
const cob=A.cobHeadMesh(A.specOf('LIT-001'));
t('메시 다수(디테일)', nodes(cob)>=35, nodes(cob));
{ const d=dim(cob); t('앞뒤(배럴) 길이가 있음', d.z>0.15, JSON.stringify(d)); }

console.log('=== 3. 랜턴 소프트박스 ===');
const lan=A.lanternMesh(A.specOf('MOD-003'));
t('구형(가로≈세로)', (()=>{const d=dim(lan);return Math.abs(d.x-d.y)<d.x*0.25;})(), JSON.stringify(dim(lan)));
t('구성 요소 있음', nodes(lan)>=4, nodes(lan));

console.log('=== 4. 프로젝션 스누트 ===');
const prj=A.projectionMesh(A.specOf('MOD-004'));
t('배럴(앞뒤로 긺)', (()=>{const d=dim(prj);return d.z>=d.x*0.7;})(), JSON.stringify(dim(prj)));
t('메시 다수', nodes(prj)>=10, nodes(prj));

console.log('=== 5. dispatch 연결(전용 형태가 실제로 쓰임) ===');
t('Forza 500 조명이 일반 조명보다 디테일 많음', nodes(build('LIT-001'))>nodes(build('LIT-005')),
  `${nodes(build('LIT-001'))} vs ${nodes(build('LIT-005'))}`);
t('MOD-003은 랜턴(구형) 형태', (()=>{const d=dim(build('MOD-003'));return Math.abs(d.x-d.z)<Math.max(d.x,d.z)*0.4;})());
t('MOD-004는 배럴 형태', nodes(build('MOD-004'))>=12, nodes(build('MOD-004')));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
