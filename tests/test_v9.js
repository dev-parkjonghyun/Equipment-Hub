const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`switchMode,ensureFloor,finishRoom,addFloorItem,addSubject,renderFloor,
 labelW,layoutLabels,labelSVG,buildGizmo,axisT,gizRay,pickGizmo,startGizDrag,moveGizDrag,endGizDrag,
 hRange,setItemPos,syncItemPanel,toggleItemPanel,showSel,specOf,itemSize,
 F:F,T:()=>THREE,setR3:(v)=>{R3=v},getR3:()=>R3,setSel:(v)=>{three3Sel=v},st:()=>state`,{runTimers:true});
const A=H.api, THREE=A.T();
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const html=require('fs').readFileSync(APP,'utf-8');
const near=(a,b,e=0.02)=>Math.abs(a-b)<=e;

console.log('=== 1. 라벨 레이어 분리 ===');
A.switchMode('floor');
const f=A.F(); f.items={};f.rooms=[];f.subjects=[];f.zoom=113;f.showClear=false;
A.finishRoom(0.5,0.3,9.5,8.2); f.rooms[0].name='촬영장';
[[2,2],[4.5,2.9],[3.5,4.1],[6.5,2.8],[8.5,3.6],[7.5,6]].forEach(p=>f.subjects.push({id:'s'+p[0]+'_'+p[1],x:p[0],y:p[1],h:1.7}));
const c1=A.addFloorItem('CAM-003',6.3,3.1), c2=A.addFloorItem('CAM-001',5.7,5.6);
A.renderFloor();
let inner=H.store['floor-svg'].innerHTML;
const scaled=inner.split('flabels')[0], layer=inner.split('flabels')[1]||'';
t('scale(z) 안에 텍스트 없음', !scaled.includes('<text'), (scaled.match(/<text/g)||[]).length+'개 남음');
t('라벨 레이어 존재', inner.includes('class="flabels"'));
t('라벨 개수 충분', (layer.match(/<text/g)||[]).length>=10, (layer.match(/<text/g)||[]).length);
t('폰트가 픽셀 단위(10px 이상)', !/font-size="0\./.test(layer) && /font-size="1[0-3]/.test(layer));
t('라벨은 클릭 통과', inner.includes('pointer-events:none'));

console.log('=== 2. 겹침 자동 회피 ===');
// 완전히 같은 자리에 라벨 5개 → 서로 다른 y로 밀려야 함
const dup=[0,1,2,3,4].map(i=>({x:5,y:5,fs:12,fill:'#fff',pri:10-i,t:'LABEL'+i}));
const laid=A.layoutLabels(dup,100);
t('5개 모두 배치', laid.length===5, laid.length);
const ys=laid.map(l=>Math.round(l.by));
t('y좌표 전부 다름', new Set(ys).size===5, ys.join(','));
let ov=0;
for(let i=0;i<laid.length;i++)for(let j=i+1;j<laid.length;j++){const a=laid[i],b=laid[j];
  if(a.bx<b.bx+b.w&&a.bx+a.w>b.bx&&a.by<b.by+b.h&&a.by+a.h>b.by) ov++;}
t('상자 겹침 0건', ov===0, ov+'건');
t('우선순위 높은 게 원위치', laid[0].t==='LABEL0' && near(laid[0].by, 500-laid[0].h/2, 1));
// 7개 이상이면 초과분은 숨김
const many=Array.from({length:12},(_,i)=>({x:5,y:5,fs:12,fill:'#fff',pri:i,t:'X'}));
t('과밀하면 초과분 숨김', A.layoutLabels(many,100).length<12);
// 한글 폭 계산
t('한글은 영문보다 넓게 계산', A.labelW('가나다',12)>A.labelW('abc',12));
t('한글 폭 ≈ 폰트크기', near(A.labelW('가나',12),24,0.5), A.labelW('가나',12));

console.log('=== 3. 실제 평면도 라벨 검증 ===');
const rects=[...layer.matchAll(/<rect x="([-\d.]+)" y="([-\d.]+)" width="([\d.]+)"\s*height="([\d.]+)"/g)]
  .map(m=>({x:+m[1],y:+m[2],w:+m[3],h:+m[4]}));
let ov2=0;
for(let i=0;i<rects.length;i++)for(let j=i+1;j<rects.length;j++){const a=rects[i],b=rects[j];
  if(a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y) ov2++;}
t('실제 화면 라벨 겹침 0건', ov2===0, ov2+'건 / 라벨 '+rects.length+'개');
t('방 이름 표시', layer.includes('촬영장'));
t('가로 치수 9.00m', layer.includes('9.00m'));
t('세로 치수 7.90m', layer.includes('7.90m'));
t('세로 치수는 회전', /rotate\(-90/.test(layer));
t('피사체 키 표시', layer.includes('1.70m'));
t('장비 이름 표시(자산번호 아닌 제품명)', layer.includes('a7m4')&&layer.includes('Fx3'), layer.match(/>[^<]*(a7m4|Fx3)[^<]*</g));
// 줌아웃해도 텍스트는 읽을 수 있는 크기 유지
f.zoom=14; A.renderFloor();
const zo=(H.store['floor-svg'].innerHTML.split('flabels')[1]||'');
t('줌아웃해도 폰트 크기 유지', /font-size="1[0-3]/.test(zo));
t('줌아웃 시 라벨 수 감소(겹침 제거)', (zo.match(/<text/g)||[]).length < (layer.match(/<text/g)||[]).length,
   (zo.match(/<text/g)||[]).length+' < '+(layer.match(/<text/g)||[]).length);
f.zoom=113;

console.log('=== 4. 기즈모 기하 ===');
const g=A.buildGizmo();
t('축 3개 + 중심', g.children.length===4, g.children.length);
const axes=[];
g.traverse(o=>{ if(o.userData&&o.userData.giz) axes.push(o.userData.giz); });
t('x·y·z 축 모두 존재', ['x','y','z'].every(a=>axes.includes(a)), [...new Set(axes)].join(','));
t('축마다 샤프트·헤드·히트영역', axes.filter(a=>a==='x').length===3);
// 각 축 화살표 끝이 올바른 방향을 향하는지
const tip={};
g.children.forEach(arm=>{ if(!arm.children.length) return;
  const head=arm.children[1]; if(!head) return;
  const v=head.position.clone(); arm.updateMatrixWorld(true); v.applyEuler(arm.rotation);
  const ax=arm.children[0].userData.giz; tip[ax]=v; });
t('X축 화살표가 +X 방향', tip.x && near(tip.x.x,0.6,0.01) && near(tip.x.y,0,0.01), tip.x&&`${tip.x.x.toFixed(2)},${tip.x.y.toFixed(2)},${tip.x.z.toFixed(2)}`);
t('Y축 화살표가 +Y 방향(위)', tip.y && near(tip.y.y,0.6,0.01), tip.y&&tip.y.y.toFixed(2));
t('Z축 화살표가 +Z 방향', tip.z && near(tip.z.z,0.6,0.01) && near(tip.z.y,0,0.01), tip.z&&`${tip.z.x.toFixed(2)},${tip.z.y.toFixed(2)},${tip.z.z.toFixed(2)}`);
t('깊이 무시(항상 보임)', html.includes('depthTest: false'));
t('거리 비례 크기 고정', html.includes('R3.giz.scale.setScalar'));

console.log('=== 5. 축 이동 수학 ===');
// 실제 카메라로 axisT 검증: 화면 중앙을 향한 광선 → 축 위 정확한 지점
const _r3=A.getR3();
const cam=new THREE.PerspectiveCamera(45,4/3,0.1,100);
cam.position.set(0,0,10); cam.lookAt(0,0,0); cam.updateMatrixWorld();
A.setR3({cam, ray:new THREE.Raycaster(), picks:[], giz:null,
  renderer:{domElement:{getBoundingClientRect:()=>({left:0,top:0,width:800,height:600})}}});
const O=new THREE.Vector3(0,0,0), DX=new THREE.Vector3(1,0,0);
const t0=A.axisT({clientX:400,clientY:300},O,DX);
t('화면 중앙 → 원점(t=0)', near(t0,0,0.001), t0);
// 오른쪽으로 이동하면 t 증가, 왼쪽이면 감소
const tR=A.axisT({clientX:600,clientY:300},O,DX);
const tL=A.axisT({clientX:200,clientY:300},O,DX);
t('오른쪽 드래그 → +X', tR>0.5, tR&&tR.toFixed(2));
t('왼쪽 드래그 → -X', tL<-0.5, tL&&tL.toFixed(2));
t('좌우 대칭', near(tR,-tL,0.001), `${tR.toFixed(3)} / ${(-tL).toFixed(3)}`);
// Y축: 위로 드래그하면 +Y
const DY=new THREE.Vector3(0,1,0);
t('위로 드래그 → +Y', A.axisT({clientX:400,clientY:100},O,DY)>0.5);
t('아래로 드래그 → -Y', A.axisT({clientX:400,clientY:500},O,DY)<-0.5);
// 카메라 정면과 평행한 축(Z)은 계산 불가여야 하지만 den으로 방어
t('평행축도 안전(크래시 없음)', (()=>{try{A.axisT({clientX:400,clientY:300},O,new THREE.Vector3(0,0,1));return true}catch(e){return false}})());

A.setR3(_r3);
console.log('=== 6. 높이 제한 = 공간 최소/최대 ===');
A.switchMode('three');
const f3=A.F(); f3.ceilH=2.7;
const camFid=Object.keys(f3.items).find(k=>f3.items[k].eqId==='CAM-001');
const camIt=f3.items[camFid];
let [lo,hi]=A.hRange(camIt);
t('지지대 없으면 0부터', lo===0, lo);
t('천장고 - 장비높이가 상한', near(hi, 2.7-A.specOf('CAM-001').h, 0.01), hi.toFixed(2));
f3.ceilH=4.0;
t('천장고 올리면 상한도 상승', A.hRange(camIt)[1]>hi);
f3.ceilH=2.7;
// 삼각대 결합 시 스펙 범위
const trFid=A.addFloorItem?null:null;
A.setSel(camFid);
A.setItemPos('h3',99);
t('상한 초과 입력 → 클램프', camIt.h3<=A.hRange(camIt)[1]+0.001, camIt.h3);
A.setItemPos('h3',-5);
t('하한 미만 입력 → 클램프', camIt.h3>=A.hRange(camIt)[0]-0.001, camIt.h3);
A.setItemPos('x',999); t('X는 공간 밖으로 못 나감', camIt.x<=40, camIt.x);
A.setItemPos('y',-3);  t('Z도 0 미만 불가', camIt.y>=0, camIt.y);

console.log('=== 7. 좌측 패널 슬라이드 ===');
t('X/Z/Y/회전 슬라이더 4개', (html.match(/type="range" id="ip-/g)||[]).length===4);
t('드래그 중 실시간 반영(oninput)', html.includes("oninput=\"setItemPos('x',this.value,1)\""));
t('놓으면 확정(onchange)', html.includes("onchange=\"setItemPos('x',this.value)\""));
t('접기 버튼', html.includes('toggleItemPanel()'));
t('슬라이드 애니메이션', html.includes('#item-panel{transition:transform'));
t('축 색이 기즈모와 일치', html.includes('.ip-ax[data-ax=x] label i{background:#ff5f70}')
   && html.includes('.ip-ax[data-ax=z] label i{background:#5b9dff}')
   && html.includes('.ip-ax[data-ax=y] label i{background:#5ad696}'));
A.toggleItemPanel();
t('접기 동작', H.store['item-panel'].classList.contains('fold'));
t('접힘 상태 저장', A.st().ipFold===true);
A.toggleItemPanel();
t('다시 펼침', !H.store['item-panel'].classList.contains('fold'));
A.syncItemPanel({x:3.25,y:4.5,h3:1.2,rot:45});
t('숫자칸 동기화', H.store['ip-x'].value==='3.25' && H.store['ip-y'].value==='1.20');
t('슬라이더 동기화', H.store['ip-x-s'].value===3.25 && H.store['ip-r-s'].value===45);

console.log('=== 8. 3D 조작 배선 ===');
t('기즈모가 회전보다 우선', html.indexOf('const ax = pickGizmo(e);')<html.indexOf("mode = (e.button === 2"));
t('드래그 중 회전 차단', html.includes('if (gizDrag) { moveGizDrag(e); return; }'));
t('놓으면 저장', html.includes('if (gizDrag) endGizDrag();'));
t('축 위 커서 변경', html.includes("pickGizmo(e) ? 'grab' : (hoverItem(e) ? 'move' : '')"));
t('높이 기준선 표시', html.includes('LineDashedMaterial'));
t('안내문에 사용법', html.includes('<b>화살표</b>는 축 고정 이동'));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
