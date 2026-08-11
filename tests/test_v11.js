const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`switchMode,addFloorItem,build3D,draw3D,toggleWalk,stepNav,nav3D,fitView3D,
 updateNavHint,ensure3D,F:F,T:()=>THREE,setR3:v=>{R3=v},getR3:()=>R3,
 keys:()=>keysDown,walk:()=>walkMode,setWalkFlag:v=>{walkMode=v},cur:currentScene`,{runTimers:true});
const A=H.api, THREE=A.T();
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const html=require('fs').readFileSync(APP,'utf-8');
const near=(a,b,e=0.03)=>Math.abs(a-b)<=e;
function mkR3(){
  const noop=()=>{}; const scene=new THREE.Scene(), world=new THREE.Group(); scene.add(world);
  return {cam:new THREE.PerspectiveCamera(45,4/3,0.05,200), scene, world,
    pvCam:new THREE.PerspectiveCamera(40,1.78,0.05,200), ray:new THREE.Raycaster(),
    picks:[], giz:null, helpers:[], frustum:null, lights:[],
    orbit:{tx:5,ty:1.2,tz:5,dist:11,theta:0,phi:1.05},
    renderer:{domElement:{getBoundingClientRect:()=>({left:0,top:0,width:800,height:600})},
      setSize:noop,setScissorTest:noop,setViewport:noop,setScissor:noop,clearDepth:noop,render:noop,
      getSize:()=>new THREE.Vector2(800,600)}};
}
const K=A.keys();
const hold=(...c)=>{K.clear(); c.forEach(x=>K.add(x));};
const run=(sec,dt=1/60)=>{ for(let i=0;i<Math.round(sec/dt);i++) A.stepNav(dt); };

A.setR3(mkR3()); A.switchMode('three');
const f=A.F(); f.ceilH=2.7; f.items={}; f.rooms=[]; f.subjects=[];

console.log('=== 1. 누르고 있으면 계속 움직인다 ===');
t('키를 keysDown에 등록', (()=>{K.clear(); A.nav3D({code:'ArrowUp',key:'ArrowUp',preventDefault(){}}); return K.has('ArrowUp');})());
t('매 프레임 이동 처리', html.includes('stepNav(dt);') && html.includes('const dt = Math.min(0.05,'));
t('프레임 간격 기준(기기 성능 무관)', html.includes('navLast ? now - navLast : 0.016'));
t('키 떼면 해제', (()=>{const e={code:'ArrowUp'}; K.add('ArrowUp'); H.fire('keyup',e); return !K.has('ArrowUp');})()
  || html.includes("keysDown.delete(e.code);"));
t('창 벗어나면 전부 해제', html.includes('keysDown.clear();'));

console.log('=== 2. 둘러보기 모드: 화면 자체가 이동 ===');
const o=A.getR3().orbit;
o.tx=5; o.tz=5; o.theta=0; o.ty=1.2;
// θ=0 → 카메라는 +X쪽에 서서 -X를 본다 (앞 = -X, 오른쪽 = -Z)
hold('ArrowUp'); run(1);
t('↑ 화면 안쪽으로 전진', o.tx<4 && near(o.tz,5,0.05), `tx=${o.tx.toFixed(2)} tz=${o.tz.toFixed(2)}`);
const adv=5-o.tx;
t('1초에 걸을 만한 거리', adv>1.5 && adv<10, adv.toFixed(2)+'m/s');
hold('ArrowDown'); run(1);
t('↓ 후진 (되돌아옴)', near(o.tx,5,0.15), o.tx.toFixed(2));
hold('ArrowUp','ShiftLeft'); run(1);
const fastAdv=5-o.tx;
t('Shift 누르면 빨라짐', fastAdv>adv*2, `${adv.toFixed(2)} → ${fastAdv.toFixed(2)}`);
o.tx=5; o.tz=5;
hold('KeyD'); run(1);
t('D 화면 오른쪽으로', o.tz<4.5 && near(o.tx,5,0.05), `tx=${o.tx.toFixed(2)} tz=${o.tz.toFixed(2)}`);
hold('KeyA'); run(1);
t('A 화면 왼쪽으로 (되돌아옴)', near(o.tz,5,0.15), o.tz.toFixed(2));
o.tx=5; o.tz=5;
const th0=o.theta; hold('ArrowRight'); run(0.5);
t('→ 방향 전환', o.theta>th0);
hold('ArrowLeft'); run(0.5);
t('← 반대 전환', near(o.theta,th0,0.02));
// 90° 돌면 전진 방향도 같이 돈다
o.theta=Math.PI/2; o.tx=5; o.tz=5;
hold('ArrowUp'); run(1);
t('돌아본 방향으로 전진', o.tz<4 && near(o.tx,5,0.1), `tx=${o.tx.toFixed(2)} tz=${o.tz.toFixed(2)}`);
const ty0=o.ty; hold('KeyE'); run(0.5); t('E 시선 높이 상승', o.ty>ty0);
hold('KeyQ'); run(2); t('Q 하강 (바닥 아래 불가)', o.ty>=0.1);
hold(); run(0.5);
t('키 떼면 멈춤', (()=>{const a=o.tx; run(1); return a===o.tx;})());

console.log('=== 3. 1인칭 걷기 ===');
t('토글 버튼', html.includes('id="walk-btn"')&&html.includes('toggleWalk()'));
t('단축키 V', html.includes("K === 'v' || K === 'V'"));
A.toggleWalk(true);
t('걷기 모드 진입', A.walk()===true);
const w=A.getR3().walk;
t('눈높이 1.65m', near(w.eye,1.65,0.01), w.eye);
t('천장보다 낮게', w.eye < f.ceilH);
t('공간 안에서 시작', w.x>=0.2&&w.x<=40&&w.z>=0.2&&w.z<=30, `${w.x.toFixed(2)},${w.z.toFixed(2)}`);
// 걷기
w.x=5; w.z=5; w.yaw=0;   // yaw 0 → -Z 방향
hold('KeyW'); run(1);
const walked=5-w.z;
t('W 전진', w.z<5 && near(w.x,5,0.01), `z=${w.z.toFixed(2)}`);
t('사람 걷는 속도(2~3m/s)', walked>2 && walked<3.2, walked.toFixed(2)+'m/s');
t('전진해도 눈높이 유지', near(w.eye,1.65,0.001));
w.z=5;
hold('KeyD'); run(1); t('D 오른쪽 옆걸음', w.x>5.5, w.x.toFixed(2));
w.x=5;
const y0=w.yaw; hold('ArrowRight'); run(0.5); t('→ 몸 돌리기', w.yaw!==y0);
w.yaw=0;
// 벽 통과 금지
hold('KeyW'); run(20);
t('공간 밖으로 못 나감', w.z>=0.15, w.z.toFixed(2));
w.x=5; w.z=5;
hold('KeyE'); run(5);
t('시선 높이 천장 아래로 제한', w.eye<=f.ceilH-0.1, w.eye.toFixed(2));
hold('KeyQ'); run(5);
t('바닥 아래로 안 내려감', w.eye>=0.25, w.eye.toFixed(2));
hold();

console.log('=== 4. 걷기 카메라 배치 ===');
w.x=3; w.z=7; w.eye=1.65; w.yaw=0; w.pitch=0;
A.draw3D();
const cam=A.getR3().cam;
t('카메라가 사람 위치에', near(cam.position.x,3,0.001)&&near(cam.position.z,7,0.001));
t('카메라가 눈높이에', near(cam.position.y,1.65,0.001), cam.position.y);
const dir=new THREE.Vector3(0,0,-1).applyQuaternion(cam.quaternion);
t('yaw=0 → -Z를 봄', near(dir.z,-1,0.02)&&near(dir.x,0,0.02), `${dir.x.toFixed(2)},${dir.y.toFixed(2)},${dir.z.toFixed(2)}`);
w.yaw=Math.PI/2; A.draw3D();
const dir2=new THREE.Vector3(0,0,-1).applyQuaternion(cam.quaternion);
t('90° 돌면 -X를 봄', near(dir2.x,-1,0.02), `${dir2.x.toFixed(2)},${dir2.z.toFixed(2)}`);
w.yaw=0; w.pitch=0.5; A.draw3D();
const dir3=new THREE.Vector3(0,0,-1).applyQuaternion(cam.quaternion);
t('고개 들면 위를 봄', dir3.y>0.4, dir3.y.toFixed(2));
w.pitch=3; A.draw3D();
t('고개 뒤집힘 방지', Math.abs(w.pitch)<=1.3, w.pitch);
w.pitch=0;

console.log('=== 5. 모드 전환 ===');
A.toggleWalk(false);
t('둘러보기로 복귀', A.walk()===false);
const o2=A.getR3().orbit;
t('걷던 자리를 중심으로', o2.tx>0&&o2.tz>0&&o2.dist>0, `${o2.tx.toFixed(1)},${o2.tz.toFixed(1)} d=${o2.dist}`);
t('전환 시 키 초기화', A.keys().size===0);
A.toggleWalk(true); A.toggleWalk();
t('V로 껐다 켜기', A.walk()===false);
t('Esc로 나가기', html.includes("K === 'Escape' && walkMode"));
t('Home은 걷기 해제 후 전체보기', html.includes("toggleWalk(false); fitView3D();"));
t('3D 나가면 키 해제', html.includes("if (m !== 'three') { keysDown.clear(); }"));

console.log('=== 6. 마우스 연동 ===');
t('걷기 중 드래그 = 둘러보기', html.includes('if (mode === \'rot\') { w.yaw -= dx * 0.005; w.pitch -= dy * 0.004; }'));
t('걷기 중 휠 = 시선 높이', html.includes('R3.walk.eye = Math.max(0.25,'));
t('걷기 중 기즈모 크기는 실제 거리 기준', html.includes('R3.cam.position.distanceTo(R3.giz.position)'));

console.log('=== 7. 화면 안내 ===');
A.updateNavHint();
t('안내 바 존재', html.includes('id="nav-hint"'));
const hint=H.store['nav-hint'].innerHTML;
t('둘러보기 안내', hint.includes('앞뒤 이동')&&hint.includes('옆걸음'));
A.toggleWalk(true); A.updateNavHint();
t('1인칭 안내로 전환', H.store['nav-hint'].innerHTML.includes('전진·후진'));
t('버튼 상태 표시', H.store['walk-btn'].textContent.includes('켜짐'));
A.toggleWalk(false);
t('버튼 원복', !H.store['walk-btn'].textContent.includes('켜짐'));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
