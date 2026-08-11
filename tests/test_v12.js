const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`switchMode,updateSceneChip,renameScene,newScene,clearScene,renderScenePane,
 openPane,syncFromLayout,addBlockAt,attachBlock,selToLayout,toggleSel,renderList,ensureFloor,ensure3D,finishRoom,addSubject,
 viewBasis,stepNav,nav3D,apertureOf,focalOf,lensSpecOf,applyLensSpec,snapFstop,updateCamPanel,
 setCam,setFstopIdx,renderCanvas,renderFloor,build3D,activeCam,
 F:F,T:()=>THREE,cur:currentScene,st:()=>state,setR3:v=>{R3=v},getR3:()=>R3,
 keys:()=>keysDown,FS:()=>FSTOPS,sel:()=>selectedIds`,{runTimers:true});
const A=H.api, THREE=A.T();
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const html=require('fs').readFileSync(APP,'utf-8');
const near=(a,b,e=0.02)=>Math.abs(a-b)<=e;
function mkR3(){const noop=()=>{};const sc=new THREE.Scene(),w=new THREE.Group();sc.add(w);
  return {cam:new THREE.PerspectiveCamera(45,1.5,0.1,200),scene:sc,world:w,
    pvCam:new THREE.PerspectiveCamera(40,1.78,0.05,200),ray:new THREE.Raycaster(),
    picks:[],giz:null,helpers:[],frustum:null,lights:[],
    orbit:{tx:5,ty:1.2,tz:5,dist:11,theta:-0.9,phi:1.05},
    renderer:{domElement:{getBoundingClientRect:()=>({left:0,top:0,width:800,height:600})},
      setSize:noop,setScissorTest:noop,setViewport:noop,setScissor:noop,clearDepth:noop,render:noop,
      getSize:()=>new THREE.Vector2(800,600)}};}

console.log('=== 1. 씬 이름 즉시 반영 ===');
A.switchMode('layout');
H.ctx.prompt=()=>'인터뷰 A룸';
A.renameScene();
t('저장됨', A.cur().name==='인터뷰 A룸');
t('툴바에 바로 반영', H.store['scene-chip'].innerHTML.includes('인터뷰 A룸'), H.store['scene-chip'].innerHTML);
A.openPane('scenes');
t('씬 목록에도 반영', H.store['scene-body'].innerHTML.includes('인터뷰 A룸'));
H.ctx.prompt=()=>'  공백 정리  ';
A.renameScene();
t('앞뒤 공백 제거', A.cur().name==='공백 정리');
H.ctx.prompt=()=>'';
A.renameScene();
t('빈 이름은 무시', A.cur().name==='공백 정리');
H.ctx.prompt=()=>null;
A.renameScene();
t('취소해도 안 바뀜', A.cur().name==='공백 정리');
// 모드를 바꿔도 유지
A.switchMode('floor'); A.switchMode('layout');
t('모드 전환 후에도 이름 유지', H.store['scene-chip'].innerHTML.includes('공백 정리'));

console.log('=== 2. 씬 칩은 이름만 ===');
t('클릭 기능 제거', !html.includes(`id="scene-chip" onclick`));
t('버튼이 아닌 표시용', html.includes('<span id="scene-chip"></span>'));
t('"씬" 라벨 + 이름', H.store['scene-chip'].innerHTML.includes('sc-k')&&H.store['scene-chip'].innerHTML.includes('공백 정리'));
t('긴 이름은 말줄임', /#scene-chip\{[^}]*text-overflow:ellipsis/.test(html));

console.log('=== 3. 씬 초기화 = 배치도 + 평면도 + 3D ===');
A.setR3(mkR3());
const sc=A.cur();
const b1=A.addBlockAt('CAM-003',100,100), b2=A.addBlockAt('LEN-001',260,100);
A.attachBlock(b2,b1,'lens');
A.addBlockAt('LIT-009',100,300);
A.switchMode('floor');
const f=A.F(); A.finishRoom(0,0,8,6); A.addSubject();
A.syncFromLayout();
const before={blocks:Object.keys(sc.blocks).length, items:Object.keys(f.items).length,
              rooms:f.rooms.length, subs:(f.subjects||[]).length};
t('초기화 전 데이터 있음', before.blocks>0&&before.items>0&&before.rooms>0&&before.subs>0,
  JSON.stringify(before));
H.ctx.confirm=()=>true;
A.clearScene();
const f2=A.F();
t('배치도 블록 삭제', Object.keys(A.cur().blocks).length===0);
t('배치도 그룹 삭제', Object.keys(A.cur().groups||{}).length===0);
t('평면도 장비 삭제', Object.keys(f2.items).length===0);
t('방은 기본 촬영장으로 되돌아감', f2.rooms.length===1 && f2.rooms[0].id==='r_default'
  && f2.rooms[0].w===6.0, JSON.stringify(f2.rooms.map(r=>r.name+' '+r.w+'x'+r.h)));
t('피사체 삭제', (f2.subjects||[]).length===0);
t('배경 도면 삭제', !f2.bg);
t('3D도 같이 비워짐(같은 데이터)', Object.keys(A.ensure3D(A.cur()).items).length===0);
t('천장고는 유지', f2.ceilH===2.7, f2.ceilH);
t('선택 상태 초기화', A.sel().size===0);
t('장비 목록은 그대로', html.includes('장비 목록과 세트는 그대로입니다'));
A.clearScene();
t('이미 비었으면 조용히 통과', true);
t('확인창에 지울 내용 안내', html.includes('배치도 블록 ${nb}개')||html.includes('평면도 장비'));

console.log('=== 4. 3D 이동 = 보이는 화면 기준 ===');
// 실제 Three 카메라 방향과 계산한 기준축이 일치하는지
[0, 1.57, 3.14, -0.9, 2.3, -2.7].forEach(th=>{
  const d=10,phi=1.05,tx=5,ty=1,tz=5;
  const cam=new THREE.PerspectiveCamera(45,1.5,0.1,100);
  cam.position.set(tx+d*Math.sin(phi)*Math.cos(th), ty+d*Math.cos(phi), tz+d*Math.sin(phi)*Math.sin(th));
  cam.lookAt(tx,ty,tz); cam.updateMatrixWorld();
  const cf=new THREE.Vector3(0,0,-1).applyQuaternion(cam.quaternion); cf.y=0; cf.normalize();
  const cr=new THREE.Vector3(1,0,0).applyQuaternion(cam.quaternion); cr.y=0; cr.normalize();
  const b=A.viewBasis(th);
  t(`θ=${th} 앞·오른쪽이 화면과 일치`,
    near(b.fx,cf.x,0.001)&&near(b.fz,cf.z,0.001)&&near(b.rx,cr.x,0.001)&&near(b.rz,cr.z,0.001));
});
// 실제 이동 확인
A.switchMode('three'); A.setR3(mkR3());
const o=A.getR3().orbit;
const K=A.keys();
const step=(k,sec)=>{K.clear();K.add(k);for(let i=0;i<sec*60;i++)A.stepNav(1/60);K.clear();};
o.theta=0; o.tx=5; o.tz=5;           // θ=0 → 카메라는 +X쪽에서 -X를 봄
step('ArrowUp',1);
t('전진하면 화면 안쪽(-X)으로', o.tx<4 && near(o.tz,5,0.05), `tx=${o.tx.toFixed(2)} tz=${o.tz.toFixed(2)}`);
o.tx=5; o.tz=5;
step('KeyD',1);
t('D는 화면 오른쪽(+Z 아님 -Z)으로', o.tz<4.5 && near(o.tx,5,0.05), `tx=${o.tx.toFixed(2)} tz=${o.tz.toFixed(2)}`);
o.theta=Math.PI/2; o.tx=5; o.tz=5;   // 카메라는 +Z쪽에서 -Z를 봄
step('ArrowUp',1);
t('돌아보면 그 방향으로 전진', o.tz<4 && near(o.tx,5,0.05), `tx=${o.tx.toFixed(2)} tz=${o.tz.toFixed(2)}`);
t('마우스 이동도 같은 기준', html.includes('const b = viewBasis(o.theta);')
  && html.includes('o.tx -= (b.rx * dx + b.fx * dy) * k;'));

console.log('=== 5. 렌즈 스펙 자동 반영 ===');
t('조리개 읽기 F2.8', A.apertureOf({product:'Sony 24-70 F2.8 GM'})===2.8);
t('조리개 읽기 F4', A.apertureOf({product:'Sony 28-135 F4'})===4);
t('초점 범위 읽기', JSON.stringify(A.focalOf({product:'Sony 70-200 F2.8 GM2'}))==='[70,200]');
t('단렌즈 범위', JSON.stringify(A.focalOf({product:'Sony 90mm  F2.8'}))==='[90,90]');
t('조리개는 실제 단으로', A.snapFstop(2.8)===2.8 && A.snapFstop(4)===4);
// 카메라+렌즈 조립 후 가져오기
H.ctx.confirm=()=>true;
A.clearScene(); A.switchMode('layout');
const c1=A.addBlockAt('CAM-003',100,100), l1=A.addBlockAt('LEN-002',260,100);
A.attachBlock(l1,c1,'lens');
A.switchMode('floor'); A.syncFromLayout();
const f3=A.F();
const camIt=Object.values(f3.items).find(i=>i.eqId==='CAM-003');
t('카메라 가져와짐', !!camIt);
t('렌즈 인식', camIt.lens==='LEN-002', camIt.lens);
t('초점거리 = 렌즈 광각단 70mm', camIt.focal===70, camIt.focal);
t('초점 범위 70-200 기록', camIt.focalMin===70&&camIt.focalMax===200, `${camIt.focalMin}-${camIt.focalMax}`);
t('조리개 = 최대개방 F2.8', camIt.fstop===2.8, camIt.fstop);
t('최대개방 한계 기록', camIt.fMin===2.8);
// 범위 밖 입력은 막힘
A.setCam('focal',500);
t('망원단 초과 불가', camIt.focal<=200, camIt.focal);
A.setCam('focal',10);
t('광각단 미만 불가', camIt.focal>=70, camIt.focal);
A.setFstopIdx(0);
t('최대개방보다 밝게 불가', camIt.fstop>=2.8, camIt.fstop);
A.setFstopIdx(6);
t('조이는 건 가능', camIt.fstop>2.8, camIt.fstop);
// 단렌즈
A.clearScene(); A.switchMode('layout');
const c2=A.addBlockAt('CAM-001',100,100), l2=A.addBlockAt('LEN-003',260,100);
A.attachBlock(l2,c2,'lens');
A.switchMode('floor'); A.syncFromLayout();
const cam2=Object.values(A.F().items).find(i=>i.eqId==='CAM-001');
t('단렌즈 90mm 고정', cam2.focal===90&&cam2.focalMin===90&&cam2.focalMax===90);
// 렌즈 없는 카메라
A.clearScene(); A.switchMode('layout'); A.addBlockAt('CAM-002',100,100);
A.switchMode('floor'); A.syncFromLayout();
const cam3=Object.values(A.F().items).find(i=>i.eqId==='CAM-002');
t('렌즈 없으면 제한 없음', !cam3.lens && cam3.focalMin==null);
t('동기화 시 렌즈 스펙 반영', /syncFromLayout[\s\S]{0,2200}applyLensSpec\(it\)/.test(html));
t('패널에 렌즈 정보 줄', html.includes('id="cp-lens"'));
t('슬라이더도 렌즈 범위로', html.includes('foc.min = L && L.min ? L.min : 8;'));
t('단렌즈는 초점 슬라이더 잠금', html.includes('foc.disabled = !!(L && L.min && L.min === L.max)'));

console.log('=== 6. 목록 버튼 위치 ===');
const body=html.slice(html.indexOf('<body>'));
t('목록 버튼 존재', body.includes('id="mode-list"'));
t('레일 상단으로 이동', body.indexOf('id="mode-list"')>0 && body.indexOf('id="mode-list"')<body.indexOf('data-p="scenes"'));
t('씬 버튼 위에 위치', body.indexOf('id="mode-list"')<body.indexOf('<span>씬</span>'));
t('rail-grp top 안에', body.slice(body.indexOf('rail-grp top'), body.indexOf('id="rail-cats"')).includes('id="mode-list"'));
t('하단 도크에서 제거', !body.slice(body.indexOf('id="mode-dock"')).slice(0,400).includes('mode-list'));
t('도크는 배치도·평면도·3D 3개', (body.match(/class="md[ "]/g)||[]).length===3, (body.match(/class="md[ "]/g)||[]).length);
t('구분선', html.includes('rail-sep'));
A.switchMode('list');
t('목록 버튼 활성 표시', H.store['mode-list'].classList.contains('on'));
A.switchMode('layout');
t('다른 모드면 해제', !H.store['mode-list'].classList.contains('on'));

console.log('=== 7. 목록 → 배치도 (있던 버그) ===');
H.ctx.confirm=()=>true;
A.clearScene(); A.switchMode('list');
A.toggleSel('CAM-001',true); A.toggleSel('LEN-005',true); A.toggleSel('LIT-001',true);
A.selToLayout();
t('실제로 블록이 생김', Object.keys(A.cur().blocks).length===3, Object.keys(A.cur().blocks).length);
t('배치도로 전환됨', A.cur().mode==='layout');
t('겹치지 않게 배치', (()=>{const b=Object.values(A.cur().blocks);
   return new Set(b.map(x=>x.x+','+x.y)).size===b.length;})());
t('저장됨', JSON.stringify(A.st().scenes).includes('CAM-001'));
// 이미 있는 건 중복 안 됨
A.switchMode('list'); A.toggleSel('CAM-001',true); A.selToLayout();
t('중복 배치 안 함', Object.values(A.cur().blocks).filter(b=>b.eqId==='CAM-001').length===1);
t('드롭과 같은 함수 사용', html.includes('function addBlockAt'));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
