// 2026-11-18 MOD-013 고독스 UL-BOX 90×90 소프트박스
const {makeHarness}=require('./harness.js');
const H=makeHarness(`isUlBox,godoxUlBox,specOf,isTriflector,isRoundReflector,buildItemMesh,T:()=>THREE`,{runTimers:true});
const A=H.api, THREE=A.T();
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const near=(a,b,e)=>Math.abs(a-b)<=e;
const dim=o=>{o.updateMatrixWorld(true);const b=new THREE.Box3().setFromObject(o);return {x:b.max.x-b.min.x,y:b.max.y-b.min.y,z:b.max.z-b.min.z,minZ:b.min.z,maxZ:b.max.z};};

console.log('=== 인식 ===');
t('MOD-013 = UL-BOX', A.isUlBox({id:'MOD-013'}));
t('제품명으로 인식', A.isUlBox({id:'X',product:'Godox UL-BOX 90x90 퀵 릴리스 소프트박스 (보웬스)'}));
t('NANLITE 소프트박스(MOD-001)는 아님', !A.isUlBox({id:'MOD-001',product:'Softbox 60b'}));
t('Triflector 로 오인 안 함', !A.isTriflector({id:'MOD-013',product:'Godox UL-BOX 90x90 퀵 릴리스 소프트박스 (보웬스)'}));

console.log('=== 공식 치수 ===');
{ const s=A.specOf('MOD-013'); t('90×90 · 깊이 38cm', s.w===0.9&&s.h===0.9&&s.d===0.38); }

console.log('=== 형태 ===');
{ const g=A.godoxUlBox(A.specOf('MOD-013')); const d=dim(g);
  t('개구부 약 90cm', near(d.x,0.912,0.02)&&near(d.y,0.912,0.02), JSON.stringify(d));
  t('마운트 면에서 앞으로 38cm', near(d.minZ,0,0.005)&&near(d.maxZ,0.38,0.01), JSON.stringify(d));
  let em=0; g.traverse(o=>{ if(o.userData&&o.userData.emitter) em++; }); t('발광면 1개', em===1); }
{ const g=A.godoxUlBox(Object.assign({},A.specOf('MOD-013'),{grid:true})); const d=dim(g);
  t('그리드 장착 시 5cm 앞으로', near(d.maxZ,0.43,0.01), d.maxZ); }
{ const g=A.godoxUlBox(Object.assign({},A.specOf('MOD-013'),{size:'60x90'})); const d=dim(g);
  t('60×90 사이즈 전환', near(d.x,0.612,0.02)&&near(d.y,0.912,0.02)&&near(d.maxZ,0.495,0.01), JSON.stringify(d)); }

console.log(`결과: ${pass} 통과 / ${fail} 실패`);
process.exit(fail?1:0);
