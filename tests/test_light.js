// 조명·모디파이어 전용 3D 모델(제품별 형태) 검증.
const {APP}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`cobHeadMesh,isForza500,lanternMesh,isLanternSoftbox,projectionMesh,isProjection,
 isForza60B,isAD300Pro,isFresnelMod,isAStandPro,isCStandPro,isTerisTripod,geoBatch,
 fs60bHead,ad300ProIIHead,pjFmmBody,fl11Fresnel,valensPro403a,valensPro40t,terisTsn6cfTripod,
 isPavoSlim,isMixPanel,isV1Flash,isNanlink,pavoSlim240bPanel,mixPanel150,godoxV1,nanlinkBoxWsTb1,
 buildItemMesh,specOf,defaultHeight,isTriflector,T:()=>THREE,EQ:()=>EQUIPMENT`,{runTimers:true});
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
t('Forza 500 조명이 일반 조명(LIT-004)보다 디테일 많음', nodes(build('LIT-001'))>nodes(build('LIT-004')),
  `${nodes(build('LIT-001'))} vs ${nodes(build('LIT-004'))}`);
t('MOD-003은 랜턴(구형) 형태', (()=>{const d=dim(build('MOD-003'));return Math.abs(d.x-d.z)<Math.max(d.x,d.z)*0.4;})());
t('MOD-004는 배럴 형태', nodes(build('MOD-004'))>=12, nodes(build('MOD-004')));

console.log('=== 6. 사용자 제작 모델 통합 (Downloads/3d) ===');
// 인식
t('60B 인식(LIT-005/006)', A.isForza60B({id:'LIT-005'}) && A.isForza60B({id:'LIT-006'}));
t('AD300Pro 인식(LIT-009)', A.isAD300Pro({id:'LIT-009'}));
t('프레넬 인식(MOD-005)', A.isFresnelMod({id:'MOD-005'}));
t('A스탠드 계열 인식(A·작은A·T)', A.isAStandPro({id:'STD-A-001'}) && A.isAStandPro({id:'STD-AS-001'}) && A.isAStandPro({id:'STD-T-001'}));
t('C스탠드 인식(STD-C)', A.isCStandPro({id:'STD-C-001'}) && !A.isAStandPro({id:'STD-C-001'}));
t('Teris 삼각대 인식(TRP-003)', A.isTerisTripod({id:'TRP-003'}));
// SPECS 공식 치수 반영
t('60B 공식 치수(247×134×87mm)', (()=>{const s=A.specOf('LIT-005');return s.d===0.247&&s.w===0.134&&s.h===0.087&&s.src==='spec';})());
t('AD300 공식 치수', (()=>{const s=A.specOf('LIT-009');return s.d===0.1869&&s.src==='spec';})());
// geoBatch 동작
t('geoBatch가 지오메트리를 합침', (()=>{const g=A.geoBatch([{geo:new THREE.BoxGeometry(1,1,1)},{geo:new THREE.BoxGeometry(1,1,1),pos:[2,0,0]}]);return g.attributes.position.count===72;})());
// 빌더가 실제 dispatch 에서 쓰임 (일반보다 디테일 많음)
t('60B 헤드가 일반 조명보다 디테일', nodes(build('LIT-005'))>nodes(build('LIT-004')), `${nodes(build('LIT-005'))} vs ${nodes(build('LIT-004'))}`);
t('AD300 헤드가 일반 조명보다 디테일', nodes(build('LIT-009'))>nodes(build('LIT-004')));
t('프레넬(MOD-005) 배럴 형태', (()=>{const d=dim(build('MOD-005'));return d.z>0.05;})());
t('A스탠드 디테일(STD-A)', nodes(build('STD-A-001'))>=6, nodes(build('STD-A-001')));
t('작은 A스탠드도 A모델', nodes(build('STD-AS-001'))>=6, nodes(build('STD-AS-001')));
t('T스탠드도 A모델', nodes(build('STD-T-001'))>=6, nodes(build('STD-T-001')));
t('C스탠드 전용 모델(PRO-40T)', nodes(build('STD-C-001'))>=6, nodes(build('STD-C-001')));
t('Teris 삼각대 디테일(카본 트윈튜브+헤드)', nodes(build('TRP-003'))>=6, nodes(build('TRP-003')));
{ const d=dim(build('TRP-003')); t('삼각대 다리 펼침(약 1m)', d.x>0.8, JSON.stringify(d)); }

console.log('=== 7. 리그 결합 (지지대 있을 때만 스탠드, 최신 모델) ===');
const rig=(id,parts,h3)=>A.buildItemMesh(A.EQ().find(e=>e.id===id),{eqId:id,x:0,y:0,h3:h3||1.5,rot:0,parts:parts||[]});
// 카메라 단독 = 삼각대 없음 → 카메라+삼각대보다 훨씬 적은 메시, 낮은 바운딩박스
const camAlone=rig('CAM-003',[]), camTrp=rig('CAM-003',[{eqId:'TRP-003',slot:'support'}],1.3);
t('카메라 단독 = 삼각대 없음(결합보다 메시 적음)', nodes(camAlone)<nodes(camTrp), `${nodes(camAlone)} vs ${nodes(camTrp)}`);
// 카메라 단독은 카메라 몸체가 h3 높이에 떠 있고, 바닥엔 위치 디스크만(다리 없음)
t('카메라 단독 바닥~머리 사이가 비어있음(다리 없음)', (()=>{
  // 다리가 있으면 y=0.3~1.2 구간에 메시가 많다. 단독이면 그 구간 메시가 거의 없다.
  let midMeshes=0; camAlone.updateMatrixWorld(true);
  camAlone.traverse(m=>{if(m.isMesh){const b=new THREE.Box3().setFromObject(m);const cy=(b.min.y+b.max.y)/2;if(cy>0.3&&cy<1.1)midMeshes++;}});
  return midMeshes===0;})(), 'mid');
// 조명+스탠드는 최신 모델 사용(옛 폴백보다 메시 많음)
t('조명+A스탠드 = 최신 모델', nodes(rig('LIT-001',[{eqId:'STD-A-001',slot:'support'}],2.0))>=8);
t('조명+C스탠드 = 최신 모델', nodes(rig('LIT-005',[{eqId:'STD-C-001',slot:'support'}],2.0))>=8);
t('카메라+삼각대 = 최신 Teris', nodes(camTrp)>=8, nodes(camTrp));
// Triflector MkII 키트 = 스탠드 항상 포함 + 기본 높이 150cm
const trif=rig('MOD-010',[],1.5), trifMid=(()=>{let n=0;trif.updateMatrixWorld(true);trif.traverse(m=>{if(m.isMesh){const b=new THREE.Box3().setFromObject(m);const cy=(b.min.y+b.max.y)/2;if(cy>0.3&&cy<1.1)n++;}});return n;})();
t('Triflector는 지지대 없어도 스탠드 있음', trifMid>0, trifMid);
t('Triflector 기본 높이 150cm', A.defaultHeight(A.EQ().find(e=>e.id==='MOD-010'))===1.50);

console.log('=== 8. 2차 추가 모델 (PavoSlim·MixPanel·V1·NANLINK) ===');
t('PavoSlim 인식(LIT-003)', A.isPavoSlim({id:'LIT-003'}) && A.isPavoSlim({product:'NANLITE PavoSlim240B'}));
t('MixPanel 인식(LIT-004)', A.isMixPanel({id:'LIT-004'}) && A.isMixPanel({product:'MixPanel 150'}));
t('V1 인식(LIT-010)', A.isV1Flash({id:'LIT-010'}) && A.isV1Flash({product:'고독스 V1'}));
t('NANLINK 인식(MOD-006)', A.isNanlink({id:'MOD-006'}) && A.isNanlink({product:'NANLINK BOX'}));
t('PavoSlim 공식 치수', (()=>{const s=A.specOf('LIT-003');return s.w===0.6087&&s.src==='spec';})());
t('MixPanel 실측 치수(426×370×82mm, 긴 변 가로)', (()=>{const s=A.specOf('LIT-004');return s.w===0.426&&s.h===0.370&&s.d===0.082&&s.w>s.h&&s.src==='spec';})());
t('빌더가 메시 생성', nodes(A.pavoSlim240bPanel(A.specOf('LIT-003')))>=1 && nodes(A.mixPanel150(A.specOf('LIT-004')))>=1
  && nodes(A.godoxV1(A.specOf('LIT-010')))>=1 && nodes(A.nanlinkBoxWsTb1(A.specOf('MOD-006')))>=1);
t('패널은 가로로 넓음(PavoSlim)', (()=>{const d=dim(A.pavoSlim240bPanel(A.specOf('LIT-003')));return d.x>0.4&&d.y>0.4;})());
t('V1은 작음(플래시)', (()=>{const d=dim(A.godoxV1(A.specOf('LIT-010')));return d.y<0.3;})());
// dispatch: 4종이 일반형 대신 전용 모델을 씀
t('LIT-003/004/010 dispatch에 전용 모델 연결', nodes(build('LIT-003'))>=1 && nodes(build('LIT-004'))>=1 && nodes(build('LIT-010'))>=1);
t('MOD-006 dispatch 연결', nodes(build('MOD-006'))>=1);

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
