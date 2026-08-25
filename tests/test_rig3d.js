const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`switchMode,addBlockAt,attachBlock,acceptSlot,syncFromLayout,build3D,
 hRange,hRangeSrc,rigRange,rigHeight,rigFootprint,specOf,supportOf,rigParts,partIn,
 buildItemMesh,ensure3D,setCam,updateCamPanel,clearScene,applyLensSpec,
 F:F,T:()=>THREE,cur:currentScene,setR3:v=>{R3=v},getR3:()=>R3,EQ:()=>EQUIPMENT`,{runTimers:true});
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
function add(id,x,y){const b=A.addBlockAt(id,x,y);if(!b)throw new Error('추가실패 '+id);return b;}
function link(cid,pid){const b=A.cur().blocks[cid];const eq=A.EQ().find(e=>e.id===b.eqId);
  const r=A.acceptSlot(pid,eq.cat);if(!r)throw new Error('슬롯거부 '+b.eqId);A.attachBlock(cid,pid,r);return r.slot;}
H.ctx.confirm=()=>true;

console.log('=== 1. 삼각대 스펙 (제조사 공식) ===');
const trp=A.specOf('TRP-001');
t('최대 높이 173cm', near(trp.hMax,1.73,0.001), trp.hMax);
t('최소 높이 43.5cm', near(trp.hMin,0.435,0.001), trp.hMin);
t('기본 높이가 범위 안', trp.h>=trp.hMin && trp.h<=trp.hMax, trp.h);
t('공식 스펙 표시', trp.src==='spec');
const t2=A.specOf('TRP-002');
t('Befree Live 43~151cm 유지', near(t2.hMin,0.43,0.01)&&near(t2.hMax,1.51,0.01), `${t2.hMin}~${t2.hMax}`);

console.log('=== 2. 높이 범위가 장비 스펙을 따른다 ===');
A.switchMode('floor');
const f=A.F(); f.items={}; f.ceilH=2.7;
f.items['solo']={eqId:'TRP-001',x:2,y:2,h3:1.2,parts:[]};
let r=A.hRange(f.items['solo']);
t('삼각대 단독 = 자기 조절 범위', near(r[0],0.435)&&near(r[1],1.73), r.join('~'));
t('천장 기준이 아님', r[1]!==2.7-trp.h, r[1]);
t('범위 출처 안내', A.hRangeSrc(f.items['solo']).kind==='self');
f.items['std']={eqId:'STD-A-001',x:3,y:3,h3:1.5,parts:[]};
const rs=A.hRange(f.items['std']), sa=A.specOf('STD-A-001');
t('A스탠드도 자기 범위', near(rs[0],sa.hMin)&&near(rs[1],Math.min(sa.hMax,2.65)), rs.join('~'));
t('천장보다 높이 못 올림', rs[1]<=2.65, rs[1]);
// 천장이 낮으면 잘림
f.ceilH=2.0;
t('낮은 천장이면 상한도 낮아짐', A.hRange(f.items['solo'])[1]<=1.95, A.hRange(f.items['solo'])[1]);
f.ceilH=2.7;
// 카메라 단독은 천장 기준
f.items['cam']={eqId:'CAM-003',x:4,y:4,h3:1,parts:[]};
t('삼각대 없는 카메라는 천장 기준', A.hRangeSrc(f.items['cam']).kind==='ceil');
f.items={};

console.log('=== 3. 조립하면 지지대 범위를 따른다 ===');
A.clearScene(); A.switchMode('layout');
const cam=add('CAM-003',100,100);
link(add('TRP-001',300,100),cam);
link(add('LEN-002',400,100),cam);
link(add('BAT-FZ-001',500,100),cam);
link(add('STO-001',600,100),cam);
A.switchMode('floor'); A.syncFromLayout();
const it=Object.values(A.F().items).find(i=>i.eqId==='CAM-003');
t('부품 4개 전달', A.rigParts(it).length===4, A.rigParts(it).length);
t('지지대 인식', A.supportOf(it)==='TRP-001');
const hr=A.hRange(it);
t('카메라 높이 = 삼각대 범위', near(hr[0],0.435)&&near(hr[1],1.73), hr.join('~'));
t('범위 출처 = 삼각대', A.hRangeSrc(it).id==='TRP-001');
t('기본 높이도 범위 안', it.h3>=hr[0]&&it.h3<=hr[1], it.h3);
A.setCam && (it.h3=1.2);
t('발자국도 삼각대 기준', near(A.rigFootprint(it).w, A.specOf('TRP-001').w, 0.01), A.rigFootprint(it).w);
t('렌즈 스펙 반영', it.focalMin===70 && it.fstop===2.8, `${it.focalMin}mm F${it.fstop}`);

console.log('=== 4. 조립을 바꾸면 3D도 갱신된다 (있던 버그) ===');
A.switchMode('layout');
// 배터리 하나 더, 모니터 추가
link(add('MON-001',700,100),cam);
A.switchMode('floor'); A.syncFromLayout();
const it2=Object.values(A.F().items).find(i=>i.eqId==='CAM-003');
t('새 부품이 반영됨', A.rigParts(it2).some(p=>p.eqId==='MON-001'), A.rigParts(it2).map(p=>p.eqId).join(','));
t('기존 부품 유지', A.rigParts(it2).length===5, A.rigParts(it2).length);
t('위치는 그대로', it2.x===it.x && it2.y===it.y);
// 지지대 교체 → 높이 범위도 따라 바뀜
A.switchMode('layout');
const s2=A.cur();
Object.entries(s2.blocks).forEach(([k,b])=>{ if(b.eqId==='TRP-001') delete s2.blocks[k]; });
link(add('TRP-002',800,100),cam);
A.switchMode('floor'); A.syncFromLayout();
const it3=Object.values(A.F().items).find(i=>i.eqId==='CAM-003');
t('지지대 교체 반영', A.supportOf(it3)==='TRP-002', A.supportOf(it3));
const hr3=A.hRange(it3);
t('높이 범위도 새 삼각대로', near(hr3[1],1.51,0.01), hr3.join('~'));
t('구성이 다르면 갱신', html.includes("if (JSON.stringify(it.parts || []) !== JSON.stringify(parts))"));
t('자동 동기화가 담당', html.includes('function syncFromLayout')&&html.includes('function afterLayoutChange'));

console.log('=== 5. 3D 메시에 부품이 실제로 반영 ===');
A.setR3(mkR3());
const mesh=A.buildItemMesh(A.EQ().find(e=>e.id==='CAM-003'), it3);
let n=0; mesh.traverse(()=>n++);
t('메시 생성', n>10, n+'개 노드');
// 삼각대 없는 카메라와 비교
const bare={eqId:'CAM-003',x:1,y:1,h3:1.2,parts:[]};
let n2=0; A.buildItemMesh(A.EQ().find(e=>e.id==='CAM-003'),bare).traverse(()=>n2++);
t('조립 부품만큼 메시가 늘어남', n>n2, `${n2} → ${n}`);
// 배터리·필터
const withBat={eqId:'CAM-003',x:1,y:1,h3:1.2,parts:[{eqId:'TRP-001',slot:'support'},{eqId:'BAT-FZ-001',slot:'batt'}]};
const noBat={eqId:'CAM-003',x:1,y:1,h3:1.2,parts:[{eqId:'TRP-001',slot:'support'}]};
let a=0,b=0; A.buildItemMesh(A.EQ().find(e=>e.id==='CAM-003'),withBat).traverse(()=>a++);
A.buildItemMesh(A.EQ().find(e=>e.id==='CAM-003'),noBat).traverse(()=>b++);
t('배터리가 3D에 그려짐', a>b, `${b} → ${a}`);
t('렌즈 필터 반영', html.includes("p.slot === 'filter'"));
t('C스탠드 그립암은 세트 결합 시에만', html.includes('isCStandPro(supEq)')&&html.includes('armKitOf(it)')&&html.includes("p.slot === 'hang'"));
t('무게추 반영', html.includes("p.slot === 'weight'"));
t('조명 전원 반영', html.includes("p.slot === 'power' || p.slot === 'batt'"));
// C스탠드에 매단 조명
const litC={eqId:'LIT-005',x:1,y:1,h3:1.8,parts:[{eqId:'STD-C-001',slot:'support'},{eqId:'MOD-007',slot:'arm'}]};
let c1=0; A.buildItemMesh(A.EQ().find(e=>e.id==='LIT-005'),litC).traverse(()=>c1++);
const litC0={eqId:'LIT-005',x:1,y:1,h3:1.8,parts:[{eqId:'STD-C-001',slot:'support'}]};
let c0=0; A.buildItemMesh(A.EQ().find(e=>e.id==='LIT-005'),litC0).traverse(()=>c0++);
t('그립암 장비가 3D에 추가됨', c1>c0, `${c0} → ${c1}`);

console.log('=== 6. 조명 조립 ===');
A.clearScene(); A.switchMode('layout');
const lit=add('LIT-001',100,100);
link(add('STD-A-001',300,100),lit);
link(add('MOD-002',400,100),lit);
A.switchMode('floor'); A.syncFromLayout();
const li=Object.values(A.F().items).find(i=>i.eqId==='LIT-001');
t('조명 부품 전달', A.rigParts(li).length===2, A.rigParts(li).map(p=>p.slot+':'+p.eqId).join(' '));
t('스탠드가 지지대', A.supportOf(li)==='STD-A-001');
t('모디파이어 슬롯', A.partIn(li,'mod')==='MOD-002');
const lr=A.hRange(li), spA=A.specOf('STD-A-001');
t('조명 높이 = 스탠드 범위', near(lr[0],spA.hMin)&&near(lr[1],Math.min(spA.hMax,2.65)), lr.join('~'));
t('발자국 = 스탠드', near(A.rigFootprint(li).w, spA.w, 0.01));

console.log('=== 7. 평면도와 3D가 같은 치수를 쓴다 ===');
['TRP-001','TRP-002','TRP-003','STD-A-001','STD-C-001','STD-AS-001','STD-T-001'].forEach(id=>{
  const fp=A.rigFootprint({eqId:id,parts:[]}), sp=A.specOf(id);
  t(id+' 발자국 일치', near(fp.w,sp.w,0.001), `평면도 ${fp.w} / 3D ${sp.w}`);
});
t('지지대는 스펙 폭을 발자국으로', html.includes('/^(TRP|STD)/.test(eqId)'));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
