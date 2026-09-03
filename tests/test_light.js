// 조명·모디파이어 전용 3D 모델(제품별 형태) 검증.
const {APP}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`cobHeadMesh,isForza500,lanternMesh,isLanternSoftbox,projectionMesh,isProjection,
 isForza60B,isAD300Pro,isFresnelMod,isAStandPro,isCStandPro,isTerisTripod,geoBatch,
 fs60bHead,ad300ProIIHead,pjFmmBody,fl11Fresnel,valensPro403a,valensPro40t,terisTsn6cfTripod,
 isPavoSlim,isMixPanel,isV1Flash,isNanlink,pavoSlim240bPanel,mixPanel150,godoxV1,nanlinkBoxWsTb1,
 isPavoTube,pavoTubeII6c,nanliteFc500c,isInsta360,insta360X3,djiRs4Pro,isPtGrid,ecPtii6c,
 isCableReel,isMarsM1,isMars400,isGripArmSet,seiseX1Reel,hollylandMarsM1,hollylandMars400s,gripArmSet,
 isAClamp,isECubeBat,isBtBgV,isRnrCart,isRoverWagon,valensAClamp,gentreeECubeVMount,nanliteBtBgV,rocknrollerR12rt,vendictRoverWagon,
 isHandTruck,handTruck2in1,
 buildItemMesh,specOf,defaultHeight,isTriflector,T:()=>THREE,EQ:()=>EQUIPMENT`,{runTimers:true});
const A=H.api, THREE=A.T();
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const nodes=o=>{let n=0;o.traverse(m=>{if(m.isMesh)n++;});return n;};
const dim=o=>{o.updateMatrixWorld(true);const b=new THREE.Box3().setFromObject(o);
  return {x:b.max.x-b.min.x, y:b.max.y-b.min.y, z:b.max.z-b.min.z};};
const build=id=>A.buildItemMesh(A.EQ().find(e=>e.id===id),{eqId:id,x:0,y:0,h3:1.6,rot:0});
const near=(a,b,e=0.002)=>Math.abs(a-b)<=e;

console.log('=== 1. 인식(제품 매칭) ===');
t('Forza 500 인식(LIT-001)', A.isForza500({id:'LIT-001'}));
t('제품명으로도(Forza 500)', A.isForza500({product:'NANLITE Forza 500B II'}));
t('60B는 Forza500 아님', !A.isForza500({id:'LIT-005',product:'Forza 60B'}));
t('랜턴 소프트박스(MOD-003)', A.isLanternSoftbox({id:'MOD-003'}));
t('JEMBALL 이름 매칭', A.isLanternSoftbox({product:'Forza 500 JEMBALL'}));
t('프로젝션(MOD-004)', A.isProjection({id:'MOD-004'}));
t('PJ-FZ60 이름 매칭', A.isProjection({product:'NANLITE PJ-FZ60'}));
t('일반 소프트박스는 프로젝션 아님', !A.isProjection({id:'MOD-001',product:'Softbox 60b'}));

console.log('=== 2. Forza 500 = FC-500C COB 헤드 ===');
const cob=A.nanliteFc500c(A.specOf('LIT-001'));
t('메시 다수(디테일)', nodes(cob)>=8, nodes(cob));
{ const d=dim(cob); t('앞뒤(배럴) 길이가 있음', d.z>0.15, JSON.stringify(d)); }
t('요크 포함(세로로도 큼)', (()=>{const d=dim(cob);return d.y>0.30;})(), JSON.stringify(dim(cob)));

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

console.log('=== 9. PavoTube II 6C (LIT-007/008) 전용 튜브 ===');
t('PavoTube 인식(LIT-007/008)', A.isPavoTube({id:'LIT-007'}) && A.isPavoTube({id:'LIT-008'}));
t('PavoSlim 과 구분', !A.isPavoTube({id:'LIT-003'}) && !A.isPavoSlim({id:'LIT-007'}));
t('제품명으로도(PavoTube)', A.isPavoTube({product:'NANLITE PavoTube'}));
t('PavoTube II 6C 실측 SPECS(250×38×38)', (()=>{const s=A.specOf('LIT-007');return s.len===0.250 && s.h===0.038 && s.src==='spec';})());
t('빌더가 메시 생성', nodes(A.pavoTubeII6c(A.specOf('LIT-007')))>=3);
{ const d=dim(A.pavoTubeII6c(A.specOf('LIT-007')));
  t('가로(X)로 길고 얇음(튜브)', d.x > d.y*3 && d.x > d.z*3, JSON.stringify(d)); }
t('dispatch 연결(LIT-007/008이 일반형 대신 튜브)', nodes(build('LIT-007'))>=3 && nodes(build('LIT-008'))>=3);

console.log('=== 9b. 실모델 매핑 (짐벌·Insta360) ===');
t('DJI RS4 Pro 짐벌 SPECS(plate 좌표)', (()=>{const s=A.specOf('GIM-001');return Array.isArray(s.plate) && s.kind==='gimbal';})());
t('짐벌 빌더 메시 다수', nodes(A.djiRs4Pro(A.specOf('GIM-001')))>=6, nodes(A.djiRs4Pro(A.specOf('GIM-001'))));
t('Insta360 인식(제품명/ CAM-006)', A.isInsta360({id:'CAM-006'}) && A.isInsta360({product:'Insta360 X3'}));
t('Sony 카메라는 Insta360 아님', !A.isInsta360({id:'CAM-003',product:'Sony a7m4'}));
t('Insta360 빌더 메시 생성', nodes(A.insta360X3(A.specOf('CAM-006')))>=3);
{ const d=dim(A.insta360X3(A.specOf('CAM-006'))); t('세로로 긴 바디(360캠)', d.y>d.x && d.y>d.z, JSON.stringify(d)); }

console.log('=== 10. MOD-008(에그크레이트)/009 형태 ===');
t('MOD-008 = PavoTube 에그크레이트(6칸) 매핑', (()=>{const s=A.specOf('MOD-008');return s.kind==='ptgrid' && s.cells===6 && A.isPtGrid({id:'MOD-008'});})());
t('MOD-009 납작 플랙 SPECS', (()=>{const s=A.specOf('MOD-009');return s.kind==='flag' && s.d<=0.05;})());
t('MOD-008 그리드 메시 다수(칸막이)', nodes(build('MOD-008'))>=2);
{ const d=dim(A.ecPtii6c(A.specOf('MOD-008'))); t('MOD-008 가로로 긴 그리드(빌더)', d.x>0.2 && d.x>d.y*3, JSON.stringify(d)); }
t('MOD-009 메시 생성(납작)', (()=>{const d=dim(build('MOD-009'));return nodes(build('MOD-009'))>=1 && d.z < d.x && d.z < d.y;})());

console.log('=== 11. 신규 자산 모델 (전선릴·Mars·그립암, 자산번호 일치) ===');
// 인식
t('전선릴 인식(PWR-001/002/003)', A.isCableReel({id:'PWR-001'}) && A.isCableReel({id:'PWR-003'}) && A.isCableReel({product:'SEISE 전선릴'}));
t('Mars M1 인식(MON-002)', A.isMarsM1({id:'MON-002'}) && A.isMarsM1({product:'HOLLYLAND Mars M1'}));
t('Mars 400s 인식(ACC-005)', A.isMars400({id:'ACC-005'}) && A.isMars400({product:'Mars 400S PRO'}));
t('그립암 세트 인식(ACC-001/002/003)', A.isGripArmSet({id:'ACC-001'}) && A.isGripArmSet({id:'ACC-003'}));
// SPECS 등록(서버 덮어쓰기 방어 대상)
t('PWR-001 색상 SPECS', (()=>{const s=A.specOf('PWR-001');return s.color==='blue' && s.outlets===4;})());
t('PWR-003 노랑', A.specOf('PWR-003').color==='yellow');
t('MON-002 실측 SPECS(152×96×40)', (()=>{const s=A.specOf('MON-002');return near(s.w,0.152)&&near(s.h,0.096);})());
t('ACC-005 SPECS', (()=>{const s=A.specOf('ACC-005');return near(s.w,0.112);})());
t('ACC-001 그립암 로드 1m', (()=>{const s=A.specOf('ACC-001');return near(s.rodLen,1.016);})());
// 빌더 메시
t('전선릴 빌더 메시 다수', nodes(A.seiseX1Reel(A.specOf('PWR-001')))>=5, nodes(A.seiseX1Reel(A.specOf('PWR-001'))));
t('Mars M1 빌더 메시 다수', nodes(A.hollylandMarsM1(A.specOf('MON-002')))>=5);
t('Mars 400s 빌더 메시 다수', nodes(A.hollylandMars400s(A.specOf('ACC-005')))>=5);
t('그립암 세트 빌더 메시 다수', nodes(A.gripArmSet(A.specOf('ACC-001')))>=4);
{ const d=dim(A.gripArmSet(A.specOf('ACC-001'))); t('그립암은 가로로 1m 이상', d.x>0.9, JSON.stringify(d)); }
// dispatch 연결(일반 박스 대신 전용)
t('PWR-001 dispatch 전용 모델', nodes(build('PWR-001'))>=5);
t('MON-002 dispatch 전용 모델', nodes(build('MON-002'))>=5);
t('ACC-005 dispatch 전용 모델', nodes(build('ACC-005'))>=5);
t('ACC-001 dispatch 전용 모델', nodes(build('ACC-001'))>=4);

console.log('=== 12. 추가 자산 모델 (클램프·배터리·그립·카트·웨건) ===');
// 인식(자산번호 일치)
t('A클램프 인식(ACC-012/013/014)', A.isAClamp({id:'ACC-012'}) && A.isAClamp({id:'ACC-013'}) && A.isAClamp({id:'ACC-014'}));
t('E-CUBE 배터리 인식(BAT-V-001~003, 004 제외)', A.isECubeBat({id:'BAT-V-001'}) && A.isECubeBat({id:'BAT-V-003'}) && !A.isECubeBat({id:'BAT-V-004',product:'FXLION'}));
t('배터리 그립 인식(PWR-005, 004 아님)', A.isBtBgV({id:'PWR-005'}) && !A.isBtBgV({id:'PWR-004',product:'BH-FZ260-V'}));
t('카트 인식(ETC-001)', A.isRnrCart({id:'ETC-001'}) && A.isRnrCart({product:'RockNRoller R12RT'}));
t('웨건 인식(ETC-003)', A.isRoverWagon({id:'ETC-003'}) && A.isRoverWagon({product:'VENDICT ROVER 왜건'}));
t('구르마 인식(ETC-002)', A.isHandTruck({id:'ETC-002'}) && A.isHandTruck({product:'2in1 구르마'}) && !A.isHandTruck({id:'ETC-001'}));
// SPECS(서버 덮어쓰기 방어 대상)
t('ACC-012 9인치 vs ACC-013 6인치', A.specOf('ACC-012').size===9 && A.specOf('ACC-013').size===6);
t('BAT-V-001 실측(97×146×78)', (()=>{const s=A.specOf('BAT-V-001');return near(s.w,0.097)&&near(s.h,0.146);})());
t('PWR-005 실측', (()=>{const s=A.specOf('PWR-005');return near(s.w,0.102)&&near(s.h,0.1565);})());
t('ETC-001 카트 치수', (()=>{const s=A.specOf('ETC-001');return near(s.d,1.321)&&near(s.h,1.054);})());
t('ETC-003 웨건 치수', (()=>{const s=A.specOf('ETC-003');return near(s.w,0.600);})());
t('ETC-002 구르마 치수', (()=>{const s=A.specOf('ETC-002');return near(s.w,0.500)&&near(s.h,1.250);})());
// 빌더 메시
t('A클램프 빌더 메시', nodes(A.valensAClamp(A.specOf('ACC-012')))>=4);
t('E-CUBE 빌더 메시', nodes(A.gentreeECubeVMount(A.specOf('BAT-V-001')))>=5);
t('배터리 그립 빌더 메시', nodes(A.nanliteBtBgV(A.specOf('PWR-005')))>=5);
t('카트 빌더 메시 다수', nodes(A.rocknrollerR12rt(A.specOf('ETC-001')))>=5, nodes(A.rocknrollerR12rt(A.specOf('ETC-001'))));
{ const d=dim(A.rocknrollerR12rt(A.specOf('ETC-001'))); t('카트는 앞뒤로 긺(1m+)', d.z>1.0, JSON.stringify(d)); }
t('웨건 빌더 메시 다수', nodes(A.vendictRoverWagon(A.specOf('ETC-003')))>=5, nodes(A.vendictRoverWagon(A.specOf('ETC-003'))));
t('구르마 빌더 메시 다수', nodes(A.handTruck2in1(A.specOf('ETC-002')))>=6, nodes(A.handTruck2in1(A.specOf('ETC-002'))));
{ const d=dim(A.handTruck2in1(A.specOf('ETC-002'))); t('구르마 세로로 큼(핸드트럭)', d.y>1.0, JSON.stringify(d)); }
// dispatch 연결(일반 박스 대신 전용)
t('ACC-012 dispatch 전용', nodes(build('ACC-012'))>=4);
t('BAT-V-001 dispatch 전용', nodes(build('BAT-V-001'))>=5);
t('PWR-005 dispatch 전용', nodes(build('PWR-005'))>=5);
t('ETC-001 dispatch 전용', nodes(build('ETC-001'))>=5);
t('ETC-003 dispatch 전용', nodes(build('ETC-003'))>=6);
t('ETC-002 dispatch 전용', nodes(build('ETC-002'))>=6);

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
