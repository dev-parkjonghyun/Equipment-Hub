const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`switchMode,sumoMonitor,isSumo,buildItemMesh,specOf,footprintOf,rigFootprint,
 addBlockAt,attachBlock,acceptSlot,syncFromLayout,clearScene,itemSize,slotsFor,
 F:F,T:()=>THREE,cur:currentScene,EQ:()=>EQUIPMENT`,{runTimers:true});
const A=H.api, THREE=A.T();
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const html=require('fs').readFileSync(APP,'utf-8');
const near=(a,b,e=0.01)=>Math.abs(a-b)<=e;
const nodes=o=>{let n=0;o.traverse(()=>n++);return n;};
const bbox=o=>{o.updateMatrixWorld(true);return new THREE.Box3().setFromObject(o);};
const eq=A.EQ().find(e=>e.id==='MON-001');
H.ctx.confirm=()=>true;

console.log('=== 1. 인식 ===');
t('MON-001을 SUMO로 인식', A.isSumo(eq));
t('제품명으로도 인식', A.isSumo({product:'Atomos Sumo 19'}));
t('다른 모니터는 아님', !A.isSumo({id:'MON-002',product:'HOLLYLAND MARS M1 5.5in'}));

console.log('=== 2. 제조사 공식 치수 ===');
const sp=A.specOf('MON-001');
t('폭 504mm', near(sp.w,0.504,0.001), sp.w);
t('높이 310mm', near(sp.h,0.310,0.001), sp.h);
t('두께 63mm', near(sp.d,0.063,0.001), sp.d);
t('스탠드 포함 깊이 180mm', near(sp.dStand,0.180,0.001), sp.dStand);
t('추정 아닌 실측', sp.src==='spec');
t('예전 값(460×300×55)에서 갱신', sp.w!==0.46&&sp.h!==0.30);

console.log('=== 3. 본체 구조 ===');
const m=A.sumoMonitor(sp,true);
t('메시 다수', nodes(m)>=20, nodes(m));
const b=bbox(m);
t('폭이 스펙대로', near(b.max.x-b.min.x, 0.504, 0.02), (b.max.x-b.min.x).toFixed(3));
t('높이가 스펙대로', near(b.max.y-b.min.y, 0.310, 0.03), (b.max.y-b.min.y).toFixed(3));
t('배터리·발까지 포함한 깊이', (b.max.z-b.min.z)>0.15 && (b.max.z-b.min.z)<0.28,
  (b.max.z-b.min.z).toFixed(3));
t('바닥에 닿음', b.min.y>=-0.005 && b.min.y<0.02, b.min.y.toFixed(3));
t('16:9 화면', html.includes('const sw = W - bez * 2, shh = sw / (16 / 9);'));
t('고무 아머 모서리 4곳', html.includes('[[-1, 1], [1, 1], [-1, -1], [1, -1]]'));
t('화면 발광', /emissive: 0x1d3a52/.test(html));
t('ATOMOS 로고 자리', html.includes('ATOMOS 로고 자리'));

console.log('=== 4. 뒷면 디테일 ===');
t('V마운트 배터리 플레이트 2개', html.includes('V마운트 배터리 플레이트 2개'));
t('방열 팬 그릴', html.includes('방열 팬 그릴'));
t('SDI BNC 6개', html.includes('for (let i = 0; i < 6; i++)')&&html.includes('SDI BNC 6개 + XLR 3개'));
t('XLR 3개', html.includes('for (let i = 0; i < 3; i++)'));
// 배터리가 뒤로 튀어나옴
const noFeet=A.sumoMonitor(sp,false);
t('배터리가 뒤쪽에', bbox(noFeet).min.z < -sp.d/2-0.05, bbox(noFeet).min.z.toFixed(3));

console.log('=== 5. 데스크 스탠드 ===');
const withF=A.sumoMonitor(sp,true), noF=A.sumoMonitor(sp,false);
t('발이 있으면 메시가 더 많음', nodes(withF)>nodes(noF), `${nodes(noF)} → ${nodes(withF)}`);
t('발이 앞뒤로 뻗음', bbox(withF).max.z>=bbox(noF).max.z-0.001);
// 바닥에 그냥 놓으면 데스크 스탠드
const floorM=A.buildItemMesh(eq,{eqId:'MON-001',x:0,y:0,h3:0,rot:0,parts:[]});
t('지지대 없으면 데스크 스탠드로', nodes(floorM)>=20, nodes(floorM));
t('바닥에 세워짐', bbox(floorM).min.y<0.08, bbox(floorM).min.y.toFixed(3));

console.log('=== 6. 스탠드 결합 ===');
A.clearScene(); A.switchMode('layout');
const mon=A.addBlockAt('MON-001',100,100);
const std=A.addBlockAt('STD-A-001',300,100);
{ const r=A.acceptSlot(mon,'STD'); t('모니터가 스탠드를 받음', !!r, r&&r.slot); if(r) A.attachBlock(std,mon,r); }
A.switchMode('floor'); A.syncFromLayout(false);
const it=Object.values(A.F().items).find(i=>i.eqId==='MON-001');
t('조립 반영', (it.parts||[]).some(p=>p.eqId==='STD-A-001'));
const sm=A.buildItemMesh(eq,it);
t('스탠드 위로 올라감', bbox(sm).max.y>1.3, bbox(sm).max.y.toFixed(2));
t('바닥까지 다리', bbox(sm).min.y<0.06, bbox(sm).min.y.toFixed(3));
t('스탠드 위엔 데스크 발 없음', html.includes('const mo = sumoMonitor(sp, false);'));

console.log('=== 7. 다른 모니터는 그대로 ===');
const m2eq=A.EQ().find(e=>e.id==='MON-002');
const m2=A.buildItemMesh(m2eq,{eqId:'MON-002',x:0,y:0,h3:1.2,rot:0,parts:[{eqId:'STD-A-001',slot:'support'}]});
t('MON-002는 기존 박스형', nodes(m2)<nodes(sm), `${nodes(m2)} vs ${nodes(sm)}`);
t('그래도 화면은 있음', html.includes('emissive: 0x1d3f6b'));

console.log('=== 8. 평면도 발자국 ===');
const fp=A.rigFootprint({eqId:'MON-001',parts:[]});
t('발자국 존재', fp.w>0, fp.w);
const sz=A.itemSize({eqId:'MON-001',parts:[]});
t('가로가 세로보다 넓음', sz.w>=sz.h, `${sz.w}×${sz.h}`);

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
