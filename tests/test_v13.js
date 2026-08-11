const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`switchMode,addSubject,subjectMesh,subjectAim,subjectEyeY,buildItemMesh,
 parabolicSoftbox,cStandBase,chromeRiser,gripArm,rodBetween,buildGizmo,selObj,isSubjKey,
 setSubject,syncItemPanel,syncPoseBtns,showSel,build3D,pick3D,startFreeDrag,moveFreeDrag,
 endFreeDrag,rayPlaneY,specOf,ensure3D,setItemPos,
 F:F,T:()=>THREE,cur:currentScene,EQ:()=>EQUIPMENT,
 setR3:v=>{R3=v},getR3:()=>R3,setSel:v=>{three3Sel=v},getSel:()=>three3Sel`,{runTimers:true});
const A=H.api, THREE=A.T();
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const html=require('fs').readFileSync(APP,'utf-8');
const near=(a,b,e=0.02)=>Math.abs(a-b)<=e;
function mkR3(){const noop=()=>{};const sc=new THREE.Scene(),w=new THREE.Group();sc.add(w);
  const cam=new THREE.PerspectiveCamera(45,1.5,0.1,200);
  cam.position.set(5,8,13); cam.lookAt(5,0,5); cam.updateMatrixWorld();
  return {cam,scene:sc,world:w,pvCam:new THREE.PerspectiveCamera(40,1.78,0.05,200),
    ray:new THREE.Raycaster(),picks:[],giz:null,helpers:[],frustum:null,lights:[],
    orbit:{tx:5,ty:1.2,tz:5,dist:11,theta:-0.9,phi:1.05},
    renderer:{domElement:{getBoundingClientRect:()=>({left:0,top:0,width:800,height:600})},
      setSize:noop,setScissorTest:noop,setViewport:noop,setScissor:noop,clearDepth:noop,render:noop,
      getSize:()=>new THREE.Vector2(800,600)}};}
const nodes=o=>{let n=0;o.traverse(()=>n++);return n;};
const bbox=o=>{o.updateMatrixWorld(true);return new THREE.Box3().setFromObject(o);};
// 눈높이선·바닥디스크 같은 보조선을 뺀 실제 몸통 크기
const bodyBox=o=>{o.updateMatrixWorld(true);const b=new THREE.Box3();
  o.traverse(x=>{if(x.isMesh && x.geometry && !(x.material&&x.material.isMeshBasicMaterial))
    b.expandByObject(x);});return b;};

console.log('=== 1. 조명 자동 빛·그림자 제거 ===');
t('SpotLight 생성 코드 없음', !html.includes('new THREE.SpotLight'));
t('조명→광원 블록 제거', !html.includes('조명 → 실제 광원'));
t('sl.target 자동 조준 제거', !html.includes('sl.target.position.set'));
t('장면 기본 조명은 유지', html.includes('HemisphereLight')&&html.includes('DirectionalLight'));
t('그림자 토글 자체는 유지', html.includes('shadowsOn = !shadowsOn'));

console.log('=== 2. 피사체 모델 (데생 인형) ===');
const st=A.subjectMesh({h:1.7,pose:'stand',x:0,y:0});
t('관절 단위로 조립된 인형', nodes(st)>=30, nodes(st)+'개 노드');
const bs=bbox(st);
t('키 1.7m에 맞음', near(bs.max.y-0.0, 1.75, 0.12), (bs.max.y).toFixed(2));
t('바닥에서 시작', bs.min.y>=-0.01 && bs.min.y<0.05, bs.min.y.toFixed(3));
{ const bd=bodyBox(st);
  t('어깨 폭이 사람다움', near(bd.max.x-bd.min.x, 0.42, 0.14), (bd.max.x-bd.min.x).toFixed(2));
  t('앞뒤 두께가 사람다움', (bd.max.z-bd.min.z)>0.15 && (bd.max.z-bd.min.z)<0.45, (bd.max.z-bd.min.z).toFixed(2)); }
t('관절 재질 존재', html.includes('manneJ:')&&html.includes('manne:'));
t('달걀형 머리', html.includes('head.scale.set(0.94, 1.30, 1.0)'));
t('벙어리손', html.includes('hand.scale.set(0.72, 1.55, 0.42)'));
// 키를 바꾸면 비례해서 커짐
const tall=bbox(A.subjectMesh({h:2.0,pose:'stand',x:0,y:0}));
t('키에 비례', tall.max.y>bs.max.y*1.1, `${bs.max.y.toFixed(2)} → ${tall.max.y.toFixed(2)}`);

console.log('=== 3. 앉은 자세 ===');
const si=A.subjectMesh({h:1.7,pose:'sit',x:0,y:0});
const bi=bbox(si);
t('앉으면 낮아짐', bi.max.y < bs.max.y*0.85, `${bs.max.y.toFixed(2)} → ${bi.max.y.toFixed(2)}`);
t('앉은 키가 사람다움', bi.max.y>1.1 && bi.max.y<1.5, bi.max.y.toFixed(2));
t('앞으로 다리가 나옴', bi.max.z > bs.max.z + 0.15, `${bs.max.z.toFixed(2)} → ${bi.max.z.toFixed(2)}`);
t('의자도 같이 나옴', nodes(si) > nodes(st), `${nodes(st)} → ${nodes(si)}`);
t('바닥에 발이 닿음', bi.min.y>=-0.01 && bi.min.y<0.05, bi.min.y.toFixed(3));
t('앉은 눈높이가 더 낮음', A.subjectEyeY({h:1.7,pose:'sit'}) < A.subjectEyeY({h:1.7,pose:'stand'}),
  `${A.subjectEyeY({h:1.7,pose:'sit'}).toFixed(2)} vs ${A.subjectEyeY({h:1.7,pose:'stand'}).toFixed(2)}`);
t('앉은 눈높이 ≈1.29m', near(A.subjectEyeY({h:1.7,pose:'sit'}),1.29,0.05));
t('조준점도 자세 반영', A.subjectAim({h:1.7,pose:'sit',x:0,y:0}).y < A.subjectAim({h:1.7,pose:'stand',x:0,y:0}).y);

console.log('=== 4. 파라볼릭 소프트박스 ===');
const sb=A.parabolicSoftbox(0.45,0.42,16);
t('메시 다수(살 포함)', nodes(sb)>16, nodes(sb));
const bb=bbox(sb);
t('지름 = 반지름×2', near(bb.max.x-bb.min.x, 0.9, 0.05), (bb.max.x-bb.min.x).toFixed(2));
t('깊이 반영', near(bb.max.y-bb.min.y, 0.44, 0.06), (bb.max.y-bb.min.y).toFixed(2));
t('포물면 프로파일', html.includes('Math.pow(u, 1.55)'));
t('16개 지지살', html.includes('ribs = ribs || 16')&&html.includes('rib.rotation.y = (i / ribs)'));
t('앞 테두리 링', html.includes('TorusGeometry(R, R * 0.022'));
t('확산 천 발광', html.includes('new THREE.CircleGeometry(R * 0.995'));
t('스피드링', html.includes('스피드링'));
t('확산면이 조명 앞을 향함', html.includes('sb.rotation.x = Math.PI / 2;           // 확산면이 조명 앞'));
// 조명 조립체에서 확산면이 +Z (앞)에 있는지
const lit=A.buildItemMesh(A.EQ().find(e=>e.id==='LIT-001'),
  {eqId:'LIT-001',x:0,y:0,h3:1.9,rot:0,parts:[{eqId:'STD-A-001',slot:'support'},{eqId:'MOD-002',slot:'mod'}]});
const lb=bbox(lit);
t('소프트박스가 조명 앞쪽으로 뻗음', lb.max.z>0.35, lb.max.z.toFixed(2));
t('뒤로는 거의 안 나감', lb.min.z>-0.5, lb.min.z.toFixed(2));

console.log('=== 5. C 스탠드 ===');
const cs=new THREE.Group(); A.cStandBase(cs,1.05); A.chromeRiser(cs,0.26,2.2,2);
t('베이스+기둥 메시', nodes(cs)>18, nodes(cs));
const cb=bbox(cs);
t('다리 벌림 = 스펙 폭', near(cb.max.x-cb.min.x, 1.05, 0.2), (cb.max.x-cb.min.x).toFixed(2));
t('기둥 높이', near(cb.max.y, 2.25, 0.1), cb.max.y.toFixed(2));
t('바닥에 닿음', cb.min.y<0.05, cb.min.y.toFixed(3));
t('터틀베이스(다리 높이 다름)', html.includes('const hs = [0.315, 0.225, 0.135]'));
t('크롬 재질', html.includes('chrome: () => mat(0xdde3ea'));
t('T형 조임 손잡이', html.includes('function tHandle'));
t('베이비 핀(5/8")', html.includes('상단 베이비 핀'));
const cs2=new THREE.Group(); A.gripArm(cs2,1.02,2.18,0,[]);
t('그립암 1m', near(bbox(cs2).max.x,1.05,0.1), bbox(cs2).max.x.toFixed(2));
// 실제 STD-C 렌더
const cstand=A.buildItemMesh(A.EQ().find(e=>e.id==='STD-C-001'),{eqId:'STD-C-001',x:0,y:0,h3:2.2,rot:0,parts:[]});
t('STD-C가 새 모델 사용 (암 없이 기둥+베이스)', nodes(cstand)>=20 && nodes(cstand)<32, nodes(cstand));
t('A스탠드는 기존 모델', html.includes('legSet(grp, sp.w, h * 0.3);'));

console.log('=== 6. 3D에서 피사체 선택·이동 ===');
A.setR3(mkR3()); A.switchMode('three');
const f=A.F(); f.items={}; f.subjects=[]; f.rooms=[];
A.addSubject();
const sj=f.subjects[0];
t('피사체 추가', !!sj);
t('기본 자세 = 서기', sj.pose==='stand');
A.build3D();
const r3=A.getR3();
t('피사체가 클릭 대상에 포함', r3.picks.some(m=>m.userData.fid==='s:'+sj.id),
  r3.picks.map(m=>m.userData.fid).join(','));
A.setSel('s:'+sj.id);
t('선택 키 인식', A.isSubjKey(A.getSel()));
const so=A.selObj();
t('selObj가 피사체 반환', so && so.kind==='subj' && so.o===sj);
A.build3D();
t('기즈모 생성', !!A.getR3().giz);
t('피사체는 X·Z만 (Y축 없음)', A.getR3().giz.children.length===3, A.getR3().giz.children.length);
t('기즈모가 바닥에', near(A.getR3().giz.position.y,0.06,0.001));
t('장비는 Y축 포함', A.buildGizmo(false).children.length===4);
// 드래그 이동
sj.x=5; sj.y=5;
A.build3D();
t('드래그 시작', A.startFreeDrag({clientX:400,clientY:300},'s:'+sj.id)===true);
const p0=A.rayPlaneY({clientX:400,clientY:300},0), p1=A.rayPlaneY({clientX:520,clientY:360},0);
A.moveFreeDrag({clientX:520,clientY:360});
t('커서 따라 이동', near(sj.x,5+(p1.x-p0.x),0.05)&&near(sj.y,5+(p1.z-p0.z),0.05), `${sj.x},${sj.y}`);
A.endFreeDrag();
t('공간 밖으로 못 나감', sj.x>=0&&sj.x<=40&&sj.y>=0&&sj.y<=30);

console.log('=== 7. 피사체 패널 ===');
A.setSel('s:'+sj.id);
A.showSel();
t('패널 표시', H.store['item-panel'].style.display==='block');
t('이름 = 피사체', H.store['ip-name'].textContent==='피사체');
t('포즈 버튼 노출', H.store['ip-pose'].style.display==='flex');
t('상태줄에 눈높이', H.store['three-sel'].innerHTML.includes('눈높이'));
t('키 슬라이더 범위', H.store['ip-y-s'].min===1.0 && H.store['ip-y-s'].max===2.1);
A.setSubject('pose','sit');
t('앉기로 전환', sj.pose==='sit');
A.showSel();
t('상태줄에 앉은 자세', H.store['three-sel'].innerHTML.includes('앉은 자세'));
A.setSubject('h',1.55);
t('키 변경', sj.h===1.55);
A.setSubject('h',3);
t('키 상한 2.1m', sj.h<=2.1, sj.h);
A.setSubject('h',0.5);
t('키 하한 1.0m', sj.h>=1.0, sj.h);
A.setSubject('rot',45);
t('회전', sj.rot===45);
A.setSubject('pose','stand');
t('서기로 복귀', sj.pose==='stand');
t('슬라이더가 피사체로 연결', html.includes('if (isSubjKey(three3Sel)) {'));
t('Delete로 피사체 삭제', html.includes("md === 'three' && isSubjKey(three3Sel)"));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
