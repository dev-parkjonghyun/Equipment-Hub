// 2026-11-18 신규 3D 모델 3종 (STD-005 사이드킥, MOD-011 원형 반사판, MOD-007 프레임 디퓨저)
const {makeHarness}=require('./harness.js');
const H=makeHarness(`isSidekickStand,isRoundReflector,isFrameDiffuser,isTriflector,valensPro2003sk,
 auroraLd60Reflector,auroraFfFrameDiffuser,buildItemMesh,specOf,defaultHeight,T:()=>THREE`,{runTimers:true});
const A=H.api, THREE=A.T();
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const dim=o=>{o.updateMatrixWorld(true);const b=new THREE.Box3().setFromObject(o);
  return {x:b.max.x-b.min.x,y:b.max.y-b.min.y,z:b.max.z-b.min.z,minY:b.min.y,maxY:b.max.y};};
const near=(a,b,e)=>Math.abs(a-b)<=e;

console.log('=== 인식 ===');
t('STD-005 = 사이드킥', A.isSidekickStand({id:'STD-005'}));
t('제품명 PRO-2003SK 인식', A.isSidekickStand({id:'X',product:'발렌스 PRO-2003SK 사이드킥 조명 스탠드'}));
t('MOD-011 = 원형 반사판', A.isRoundReflector({id:'MOD-011',product:'반사판 55cm'}));
t('MOD-011 은 Triflector 아님', !A.isTriflector({id:'MOD-011',product:'반사판 55cm'}));
t('MOD-010 은 여전히 Triflector', A.isTriflector({id:'MOD-010',product:'Triflector MkII Kit 반사판 스탠드 키트'}));
t('MOD-007 = 프레임 디퓨저', A.isFrameDiffuser({id:'MOD-007'}));
t('MOD-009 플랙은 프레임 디퓨저 아님', !A.isFrameDiffuser({id:'MOD-009',product:'모듈형 프레임 원단 디퓨저 꼬리 플랙'}));

console.log('=== 공식 치수 ===');
{ const s=A.specOf('STD-005'); t('사이드킥 기둥 103.5/220cm', s.poleShort===1.035&&s.poleLong===2.20);
  t('다리 직경 110cm', s.spreadD===1.10&&s.w===1.10); t('튜브 Ø35mm', s.tube===0.035); }
{ const s=A.specOf('MOD-011'); t('반사판 지름 60cm', s.w===0.60&&s.h===0.60); }
{ const s=A.specOf('MOD-007'); t('디퓨저 750×900 · 지지대 20cm', s.w===0.75&&s.h===0.90&&s.stemL===0.20); }

console.log('=== 형태 ===');
{ const g=A.valensPro2003sk(Object.assign({},A.specOf('STD-005'),{slideY:1.6})); const d=dim(g);
  t('높게 쓰면 연결봉 장착 → 220cm', near(d.maxY,2.212,0.02), d.maxY);
  let rMax=0; g.updateMatrixWorld(true); g.traverse(o=>{ if(!o.isMesh) return; const pa=o.geometry.attributes.position, v=new THREE.Vector3();
    for(let i=0;i<pa.count;i++){ v.fromBufferAttribute(pa,i).applyMatrix4(o.matrixWorld); if(v.y<0.2) rMax=Math.max(rMax,Math.hypot(v.x,v.z)); } });
  t('다리 펼침 지름 약 1.1m', rMax*2>1.05&&rMax*2<1.15, rMax*2);
  t('스피곳 자리 = 암 끝·설정 높이', g.userData.mount[0]===0.26&&near(g.userData.mount[1],1.6,1e-6)); }
{ const g=A.valensPro2003sk(Object.assign({},A.specOf('STD-005'),{slideY:0.7})); const d=dim(g);
  t('낮게 쓰면 연결봉 없이 103.5cm', near(d.maxY,1.047,0.02), d.maxY); }
{ const g=A.auroraLd60Reflector(A.specOf('MOD-011')); const d=dim(g);
  t('원판 60cm (얇음)', near(d.x,0.611,0.02)&&d.z<0.03, JSON.stringify(d)); }
{ const g=A.auroraFfFrameDiffuser(A.specOf('MOD-007')); const d=dim(g);
  t('프레임 75cm 폭', near(d.x,0.763,0.02), d.x);
  t('핀 끝(원점)부터 프레임 위까지 1.1m', near(d.minY,0,0.01)&&near(d.maxY,1.106,0.02), JSON.stringify(d)); }

console.log('=== 조립 ===');
const lit={id:'LIT-005',cat:'LIT',product:'NANLITE Forza 60B'};
{ const m=A.buildItemMesh(lit,{eqId:'LIT-005',x:0,y:0,h3:1.7,rot:0,parts:[{eqId:'STD-005',slot:'support'}]});
  const st=m.children.find(c=>c.userData&&c.userData.mount);
  t('사이드킥 위 조명 — 스탠드가 암 길이만큼 비켜 섬', st&&near(st.position.x,-0.26,1e-6)&&dim(m).maxY>2.1, st&&st.position.x); }
{ const m=A.buildItemMesh(lit,{eqId:'LIT-005',x:0,y:0,h3:1.5,rot:0,parts:[{eqId:'MOD-011',slot:'mod'}]});
  let found=false; m.traverse(o=>{ if(o.isMesh&&o.geometry&&o.geometry.type==='TorusGeometry') found=true; });
  t('조명 앞 원형 반사판(테두리 토러스)', found); }
t('반사판·디퓨저 기본 높이 1m', A.defaultHeight({id:'MOD-011',cat:'MOD'})===1&&A.defaultHeight({id:'MOD-007',cat:'MOD'})===1);

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
