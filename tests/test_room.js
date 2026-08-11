const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`switchMode,activeRoom,roomPoly,pointInPoly,clampToRoom,confineItem,confineSubject,
 toggleConfine,reconfineAll,setRoomSize,syncRoomUI,syncConfineBtn,addBlockAt,addFloorItem,addSubject,
 syncFromLayout,startFloorDrag,doFloorDrag,endFloorDrag,setItemPos,setSubject,itemSize,specOf,
 rigFootprint,clearScene,finishRoom,build3D,renderFloor,startFreeDrag,moveFreeDrag,rayPlaneY,
 F:F,T:()=>THREE,cur:currentScene,EQ:()=>EQUIPMENT,setR3:v=>{R3=v},getR3:()=>R3,
 setSel3:v=>{three3Sel=v},setSnap:v=>{snapEnabled=v}`,{runTimers:true});
const A=H.api, THREE=A.T();
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const html=require('fs').readFileSync(APP,'utf-8');
const near=(a,b,e=0.02)=>Math.abs(a-b)<=e;
const items=()=>Object.values(A.F().items);
function mkR3(){const noop=()=>{};const sc=new THREE.Scene(),w=new THREE.Group();sc.add(w);
  const cam=new THREE.PerspectiveCamera(45,1.5,0.1,200);
  cam.position.set(4,9,12); cam.lookAt(4,0,3.5); cam.updateMatrixWorld();
  return {cam,scene:sc,world:w,pvCam:new THREE.PerspectiveCamera(40,1.78,0.05,200),
    ray:new THREE.Raycaster(),picks:[],giz:null,helpers:[],frustum:null,lights:[],
    orbit:{tx:4,ty:1.2,tz:3.5,dist:11,theta:-0.9,phi:1.05},
    renderer:{domElement:{getBoundingClientRect:()=>({left:0,top:0,width:800,height:600})},
      setSize:noop,setScissorTest:noop,setViewport:noop,setScissor:noop,clearDepth:noop,render:noop,
      getSize:()=>new THREE.Vector2(800,600)}};}
H.ctx.confirm=()=>true;

console.log('=== 1. 기본 방이 있다 ===');
A.switchMode('floor');
const r=A.activeRoom();
t('처음부터 방이 있음', !!r);
t('이름 = 촬영장', r.name==='촬영장');
t('6.0 × 4.5m', near(r.w,6)&&near(r.h,4.5), `${r.w}×${r.h}`);
t('27㎡', near(r.w*r.h,27,0.01));
t('원점에서 1m 띄움', r.x===1&&r.y===1);
t('사각형', r.type==='rect');
t('제한 기본 ON', A.F().confine===true);
t('평면도에 치수 표시', html.includes("${r.w.toFixed(2)}m")&&html.includes("${r.h.toFixed(2)}m"));
t('면적도 표시', html.includes("${(r.w * r.h).toFixed(2)}㎡"));

console.log('=== 2. 경계 계산 ===');
t('방 안은 그대로', (()=>{const c=A.clampToRoom(4,3,0.3);return c.x===4&&c.y===3&&!c.hit;})());
t('왼쪽 밖 → 안으로', (()=>{const c=A.clampToRoom(-5,3,0.3);return near(c.x,1.3)&&c.hit;})(),
  JSON.stringify(A.clampToRoom(-5,3,0.3)));
t('오른쪽 밖 → 안으로', near(A.clampToRoom(30,3,0.3).x, 6.7), A.clampToRoom(30,3,0.3).x);
t('위쪽 밖', near(A.clampToRoom(4,-9,0.3).y, 1.3));
t('아래쪽 밖', near(A.clampToRoom(4,25,0.3).y, 5.2), A.clampToRoom(4,25,0.3).y);
t('발자국 반경만큼 여유', A.clampToRoom(0,0,1.0).x===2.0, A.clampToRoom(0,0,1.0).x);
t('방보다 큰 장비는 중앙', (()=>{const c=A.clampToRoom(0,0,5);return c.x>=1&&c.x<=7;})(),
  JSON.stringify(A.clampToRoom(0,0,5)));

console.log('=== 3. 다각형 방 ===');
A.clearScene();
const f=A.F(); f.rooms=[{id:'p',name:'L자',type:'poly',x:0,y:0,
  pts:[{x:0,y:0},{x:6,y:0},{x:6,y:2},{x:3,y:2},{x:3,y:5},{x:0,y:5}]}];
t('안쪽 판정', A.pointInPoly(A.roomPoly(f.rooms[0]),1,1)===true);
t('바깥 판정', A.pointInPoly(A.roomPoly(f.rooms[0]),5,4)===false);
t('L자 오목부는 밖', A.pointInPoly(A.roomPoly(f.rooms[0]),4.5,4)===false);
const c1=A.clampToRoom(5,4,0.3);
t('오목부로 나가면 끌려옴', A.pointInPoly(A.roomPoly(f.rooms[0]),c1.x,c1.y), JSON.stringify(c1));
t('멀리 나가도 안으로', (()=>{const c=A.clampToRoom(20,20,0.3);
   return A.pointInPoly(A.roomPoly(f.rooms[0]),c.x,c.y);})());
t('안쪽은 유지', (()=>{const c=A.clampToRoom(1.5,1.5,0.2);return !c.hit;})());

console.log('=== 4. 배치·이동이 방을 벗어나지 않는다 ===');
A.clearScene(); A.switchMode('layout');
A.addBlockAt('LIT-009',100,100);
A.addBlockAt('CAM-003',300,100);
A.switchMode('floor');
const rm=A.activeRoom();
const inside=it=>{const sz=A.itemSize(it),rr=Math.max(sz.w,sz.h)/2;
  return it.x>=rm.x+rr-0.01 && it.x<=rm.x+rm.w-rr+0.01 && it.y>=rm.y+rr-0.01 && it.y<=rm.y+rm.h-rr+0.01;};
t('자동 배치가 방 안', items().every(inside), items().map(i=>`${i.eqId}(${i.x},${i.y})`).join(' '));
// 패널 입력
A.setSel3(Object.keys(A.F().items)[0]);
A.setItemPos('x',99);
t('숫자 입력도 막힘', inside(items().find(i=>i.eqId===A.F().items[Object.keys(A.F().items)[0]].eqId)),
  JSON.stringify(items()[0]));
A.setItemPos('y',-40);
t('음수 입력도 막힘', items().every(inside));
// 평면도 직접 놓기
A.addFloorItem('MON-001',30,25);
t('방 밖에 놓으려 해도 안으로', items().every(inside), items().map(i=>`${i.x},${i.y}`).join(' '));
// 3D 드래그
A.setR3(mkR3()); A.switchMode('three'); A.setSnap(false);
const fid=Object.keys(A.F().items)[0];
A.setSel3(fid); A.build3D();
A.startFreeDrag({clientX:400,clientY:300},fid);
A.moveFreeDrag({clientX:20,clientY:20});
t('3D 드래그도 방 안', inside(A.F().items[fid]), JSON.stringify(A.F().items[fid]));
A.moveFreeDrag({clientX:790,clientY:590});
t('반대쪽도 방 안', inside(A.F().items[fid]), JSON.stringify(A.F().items[fid]));

console.log('=== 5. 피사체도 제한 ===');
A.addSubject();
const sj=A.F().subjects[0];
t('피사체가 방 중앙에', sj.x>rm.x&&sj.x<rm.x+rm.w&&sj.y>rm.y&&sj.y<rm.y+rm.h, `${sj.x},${sj.y}`);
sj.x=50; sj.y=50; A.confineSubject(sj);
t('피사체도 방 안으로', sj.x<=rm.x+rm.w&&sj.y<=rm.y+rm.h, `${sj.x},${sj.y}`);
A.setSel3('s:'+sj.id);
A.setSubject('x',-10);
t('피사체 패널 입력도 막힘', sj.x>=rm.x, sj.x);

console.log('=== 6. 방 크기 변경 ===');
A.clearScene(); A.switchMode('floor');
A.addBlockAt('LIT-009',100,100);
const it0=items()[0];
it0.x=6.5; it0.y=5.0;   // 원래 방(1,1,6,4.5) 가장자리
A.setRoomSize('w',3);
const rm2=A.activeRoom();
t('폭 변경', near(rm2.w,3), rm2.w);
t('밖으로 나간 장비를 안으로', items()[0].x<=rm2.x+rm2.w, items()[0].x);
A.setRoomSize('h',2.5);
t('높이 변경', near(A.activeRoom().h,2.5));
t('다시 정리됨', items()[0].y<=A.activeRoom().y+2.5, items()[0].y);
A.setRoomSize('w',999);
t('최대 제한', A.activeRoom().w<=40, A.activeRoom().w);
A.setRoomSize('w',0);
t('최소 1m', A.activeRoom().w>=1, A.activeRoom().w);
A.setRoomSize('w',6); A.setRoomSize('h',4.5);
t('툴바에 방 크기 입력', html.includes('id="rm-w"')&&html.includes('id="rm-h"'));
t('3D 툴바에도', html.includes('id="rm-w2"')&&html.includes('id="rm-h2"'));
A.renderFloor();
t('입력칸 동기화', H.store['rm-w'].value==='6.00', H.store['rm-w'].value);

console.log('=== 7. 제한 해제 ===');
t('토글 버튼', html.includes('toggleConfine()')&&html.includes('id="cf-btn"'));
A.toggleConfine();
t('해제됨', A.F().confine===false);
const it1=items()[0];
it1.x=20; A.confineItem(it1);
t('해제하면 밖에도 놓임', it1.x===20, it1.x);
A.toggleConfine();
t('다시 켜면 안으로 회수', items()[0].x<=A.activeRoom().x+A.activeRoom().w, items()[0].x);
t('버튼 상태 표시', H.store['cf-btn'].textContent.includes('방 안으로 제한'));
t('상태 저장', A.F().confine===true);

console.log('=== 8. 방이 없으면 자유 ===');
A.F().rooms=[];
t('방 없음', !A.activeRoom());
const c9=A.clampToRoom(25,20,0.3);
t('세계 범위 안에서 자유', c9.x===25&&c9.y===20&&!c9.hit, JSON.stringify(c9));
t('세계 밖은 여전히 막힘', A.clampToRoom(999,999,0).x<=40);
t('크래시 없음', (()=>{try{A.reconfineAll();A.renderFloor();return true}catch(e){return false}})());

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
