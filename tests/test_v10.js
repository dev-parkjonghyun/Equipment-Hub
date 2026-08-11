const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`switchMode,ensureFloor,addFloorItem,renderFloor,build3D,showSel,
 rayPlaneY,startFreeDrag,moveFreeDrag,endFreeDrag,hoverItem,gizRay,nav3D,fitView3D,
 hRange,setItemPos,syncItemPanel,specOf,itemSize,activeCam,stepNav,keys:()=>keysDown,
 F:F,T:()=>THREE,setR3:v=>{R3=v},getR3:()=>R3,setSel:v=>{three3Sel=v},getSel:()=>three3Sel,
 getFree:()=>freeDrag,setSnap:v=>{snapEnabled=v},st:()=>state`,{runTimers:true});
const A=H.api, THREE=A.T();
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const html=require('fs').readFileSync(APP,'utf-8');
const near=(a,b,e=0.03)=>Math.abs(a-b)<=e;

// 실제 카메라로 R3 구성 (위에서 45° 내려다보는 시점)
function mkR3(){
  const cam=new THREE.PerspectiveCamera(45,4/3,0.1,200);
  const noop=()=>{};
  cam.position.set(5,8,13); cam.lookAt(5,0,5); cam.updateMatrixWorld();
  const scene=new THREE.Scene(), world=new THREE.Group(); scene.add(world);
  return {cam, scene, world, pvCam:new THREE.PerspectiveCamera(40,1.78,0.05,200),
    ray:new THREE.Raycaster(), picks:[], giz:null, helpers:[], frustum:null, lights:[],
    orbit:{tx:5,ty:1.2,tz:5,dist:11,theta:-0.9,phi:1.05},
    renderer:{domElement:{getBoundingClientRect:()=>({left:0,top:0,width:800,height:600})},
      setSize:noop,setScissorTest:noop,setViewport:noop,setScissor:noop,clearDepth:noop,render:noop,
      getSize:()=>new THREE.Vector2(800,600)}};
}

console.log('=== 1. 프리뷰에서 자기 몸체 숨김 ===');
t('카메라 자신을 숨김', html.includes("const own = R3.picks.find(m => m.userData.fid === fid);"));
t('프러스텀도 숨김', html.includes('if (R3.frustum) hid.push(R3.frustum);'));
t('기즈모도 숨김', /hid\.push\(R3\.giz\)/.test(html));
t('선택링·기준선도 숨김', html.includes('(R3.helpers || []).forEach(h => hid.push(h));'));
t('렌더 후 원상복구', html.includes('hid.forEach((m, i) => { m.visible = vis[i]; });'));
{ // 숨김→복구 로직 검증
  const blk=html.slice(html.indexOf('const hid = [];'), html.indexOf('hid.forEach((m, i)')+80);
  t('숨김이 렌더보다 앞', blk.indexOf('m.visible = false')<blk.indexOf('R3.renderer.render(R3.scene, R3.pvCam)'));
  t('복구가 렌더보다 뒤', blk.indexOf('vis[i]')>blk.indexOf('R3.renderer.render(R3.scene, R3.pvCam)'));
}
t('보조물 목록 매 빌드마다 초기화', html.includes('R3.giz = null; R3.helpers = [];'));

console.log('=== 2. 바닥 평면 광선 계산 ===');
A.setR3(mkR3());
const p0=A.rayPlaneY({clientX:400,clientY:300},0);
t('화면 중앙 → 주시점 근처 바닥', p0 && near(p0.x,5,0.6) && near(p0.z,5,0.6), p0&&`${p0.x.toFixed(2)},${p0.z.toFixed(2)}`);
t('바닥 높이 y=0', near(p0.y,0,0.001));
const pR=A.rayPlaneY({clientX:700,clientY:300},0);
t('오른쪽 → +X 쪽', pR.x>p0.x, `${p0.x.toFixed(2)} → ${pR.x.toFixed(2)}`);
const pU=A.rayPlaneY({clientX:400,clientY:100},0);
t('위쪽 → 더 먼 곳(-Z)', pU.z<p0.z, `${p0.z.toFixed(2)} → ${pU.z.toFixed(2)}`);
const p1=A.rayPlaneY({clientX:400,clientY:300},1.5);
t('높이 1.5m 평면도 계산', near(p1.y,1.5,0.001));
t('하늘을 보면 null', A.rayPlaneY({clientX:400,clientY:0},0)===null || A.rayPlaneY({clientX:400,clientY:0},0).z<p0.z);

console.log('=== 3. 장비 자유 드래그 ===');
A.setR3(mkR3()); A.switchMode('three');
const f=A.F(); f.items={}; f.subjects=[]; f.ceilH=2.7;
const fid=A.addFloorItem('LIT-009',3,3);
A.setSel(fid);
A.build3D();
const r3=A.getR3();
const it=f.items[fid];
t('실제 3D 메시 생성', r3.picks.length>0 && r3.picks.some(m=>m.userData.fid===fid), r3.picks.length);
t('기즈모 생성', !!r3.giz);
t('선택 보조물 생성', r3.helpers.length>0, r3.helpers.length);
A.setSnap(false);
t('드래그 시작', A.startFreeDrag({clientX:400,clientY:300},fid)===true);
const Y=it.h3||0;
const s0=A.rayPlaneY({clientX:400,clientY:300},Y), s1=A.rayPlaneY({clientX:520,clientY:360},Y);
A.moveFreeDrag({clientX:520,clientY:360});
t('커서 이동량만큼 정확히 따라옴',
   near(it.x, 3+(s1.x-s0.x), 0.02) && near(it.y, 3+(s1.z-s0.z), 0.02),
   `${it.x},${it.y} vs ${(3+s1.x-s0.x).toFixed(2)},${(3+s1.z-s0.z).toFixed(2)} (h3=${Y})`);
const mesh=r3.picks.find(m=>m.userData.fid===fid);
t('메시도 함께 이동', near(mesh.position.x,it.x,0.001)&&near(mesh.position.z,it.y,0.001));
t('기즈모도 따라옴', near(r3.giz.position.x,it.x,0.001)&&near(r3.giz.position.z,it.y,0.001));
t('패널 숫자 동기화', H.store['ip-x'].value===it.x.toFixed(2));
// 공간 밖으로 못 나감
A.startFreeDrag({clientX:400,clientY:300},fid);
it.x=0.1; A.moveFreeDrag({clientX:20,clientY:560});
t('벽 밖으로 안 나감', it.x>=0 && it.y>=0 && it.x<=40 && it.y<=30, `${it.x},${it.y}`);
// 스냅
A.setSnap(true); it.x=3; it.y=3;
A.startFreeDrag({clientX:400,clientY:300},fid);
A.moveFreeDrag({clientX:437,clientY:331});
t('스냅 켜면 5cm 격자', Math.abs(it.x*20-Math.round(it.x*20))<1e-6, it.x);
A.setSnap(false);
// 높이가 있으면 그 높이 평면에서 이동
it.h3=1.2; it.x=3; it.y=3;
A.startFreeDrag({clientX:400,clientY:300},fid);
const before={x:it.x,y:it.y};
A.moveFreeDrag({clientX:500,clientY:300});
t('공중에 뜬 장비는 높이 유지', it.h3===1.2);
t('공중에서도 이동됨', it.x!==before.x);
A.endFreeDrag();
t('놓으면 드래그 종료', A.getFree()===null);
t('놓을 때 저장', A.st().scenes!==undefined);

console.log('=== 4. 기즈모 우선 · 회전과 충돌 없음 ===');
const pd=html.slice(html.indexOf("canvas.addEventListener('pointerdown'"), html.indexOf("canvas.addEventListener('pointermove'"));
t('① 기즈모 → ② 장비 → ③ 회전 순서',
   pd.indexOf('pickGizmo')<pd.indexOf('startFreeDrag') && pd.indexOf('startFreeDrag')<pd.indexOf("mode = (e.button === 2"));
t('장비 잡으면 회전 안 함', pd.includes('canvas.setPointerCapture(e.pointerId);\n                return;'));
t('빈 곳이면 회전', pd.includes("mode = (e.button === 2 || e.shiftKey) ? 'pan' : 'rot';"));
t('드래그 중 회전 차단', html.includes('if (freeDrag) { moveFreeDrag(e); return; }'));
t('놓으면 확정', html.includes('if (freeDrag) endFreeDrag();'));
t('장비 위 커서 = move', html.includes("hoverItem(e) ? 'move' : ''"));

console.log('=== 5. 방향키 시점 이동 (등록만 확인 · 상세는 test_v11) ===');
A.setR3(mkR3());
{ const K=A.keys ? A.keys() : null; }
t('이동키는 누르는 동안 지속 처리', html.includes('WALK_KEYS.includes(e.code)')&&html.includes('keysDown.add(e.code)'));
t('매 프레임 stepNav', html.includes('stepNav(dt);'));
t('줌은 즉시 반응', html.includes("K === '+' || K === '='"));
{ const o=A.getR3().orbit, d0=o.dist;
  A.nav3D({key:'+',code:'Equal',preventDefault(){}});
  t('+ 줌인', o.dist<d0, o.dist.toFixed(2));
  A.nav3D({key:'-',code:'Minus',preventDefault(){}});
  A.nav3D({key:'-',code:'Minus',preventDefault(){}});
  t('- 줌아웃', o.dist>d0, o.dist.toFixed(2));
  let pd=false;
  A.nav3D({key:'ArrowUp',code:'ArrowUp',preventDefault(){pd=true}});
  t('방향키는 스크롤 차단', pd===true);
  t('상관없는 키는 통과', A.nav3D({key:'k',code:'KeyK',preventDefault(){}})===false); }

console.log('=== 6. 전체 보기 ===');
A.setR3(mkR3()); A.switchMode('three');
const f2=A.F(); f2.items={}; f2.rooms=[]; f2.subjects=[];
A.setR3(mkR3());
A.addFloorItem('LIT-009',2,2); A.addFloorItem('CAM-001',12,9);
A.fitView3D();
const ob=A.getR3().orbit;
t('중심이 장비 사이', near(ob.tx,7,0.1)&&near(ob.tz,5.5,0.1), `${ob.tx},${ob.tz}`);
t('거리가 범위를 담을 만큼', ob.dist>=10*1.4, ob.dist.toFixed(1));
t('Home 키로도 실행', html.includes("K === 'Home'"));
t('툴바 버튼', html.includes('fitView3D()') && html.includes('🎯 전체 보기'));
t('빈 씬에서도 안전', (()=>{const g=A.F();g.items={};g.rooms=[];g.subjects=[];try{A.fitView3D();return true}catch(e){return false}})());

console.log('=== 7. 안내 ===');
t('조작법 안내', html.includes('<b>장비를 끌면</b>')&&html.includes('<b>방향키</b>=시점'));
t('높이 기준선 대시 계산', html.includes('gl.computeLineDistances();'));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
