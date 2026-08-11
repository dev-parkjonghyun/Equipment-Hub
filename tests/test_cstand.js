const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`switchMode,addBlockAt,attachBlock,acceptSlot,syncFromLayout,slotsFor,
 buildItemMesh,cStandBase,chromeRiser,gripArm,gripHead,armKitOf,rigFootprint,itemSize,
 specOf,supportOf,rigParts,clearScene,build3D,
 F:F,T:()=>THREE,cur:currentScene,EQ:()=>EQUIPMENT,setR3:v=>{R3=v},getR3:()=>R3`,{runTimers:true});
const A=H.api, THREE=A.T();
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const html=require('fs').readFileSync(APP,'utf-8');
const near=(a,b,e=0.02)=>Math.abs(a-b)<=e;
const nodes=o=>{let n=0;o.traverse(()=>n++);return n;};
const bbox=o=>{o.updateMatrixWorld(true);return new THREE.Box3().setFromObject(o);};
const CS=A.EQ().find(e=>e.id==='STD-C-001');
function add(id,x,y){const b=A.addBlockAt(id,x,y);if(!b)throw new Error('추가실패 '+id);return b;}
function link(cid,pid){const b=A.cur().blocks[cid];const eq=A.EQ().find(e=>e.id===b.eqId);
  const r=A.acceptSlot(pid,eq.cat);if(!r)throw new Error('슬롯거부 '+b.eqId);A.attachBlock(cid,pid,r);return r;}
H.ctx.confirm=()=>true;

console.log('=== 1. C스탠드 기본형 = 기둥 + 베이스만 ===');
const bare=A.buildItemMesh(CS,{eqId:'STD-C-001',x:0,y:0,h3:2.2,rot:0,parts:[]});
const bb=bbox(bare);
t('암이 없다', !A.armKitOf({parts:[]}));
t('옆으로 안 뻗음', bb.max.x<0.62, bb.max.x.toFixed(2));
t('기둥 높이는 유지', near(bb.max.y,2.25,0.12), bb.max.y.toFixed(2));
t('베이스는 그대로', bb.min.y<0.05 && (bb.max.x-bb.min.x)>0.9, (bb.max.x-bb.min.x).toFixed(2));

console.log('=== 2. 그립헤드·암 세트를 붙이면 나타난다 ===');
const withArm=A.buildItemMesh(CS,{eqId:'STD-C-001',x:0,y:0,h3:2.2,rot:0,
  parts:[{eqId:'ACC-001',slot:'arm'}]});
const ab=bbox(withArm);
t('암 인식', A.armKitOf({parts:[{eqId:'ACC-001',slot:'arm'}]})==='ACC-001');
t('1m 옆으로 뻗음', ab.max.x>0.95, ab.max.x.toFixed(2));
t('메시가 늘어남', nodes(withArm)>nodes(bare), `${nodes(bare)} → ${nodes(withArm)}`);
t('그립헤드 2개(기둥·암끝)', html.includes('gripHead(arm, 0, 0, 0)')&&html.includes('gripHead(arm, len, 0, 0)'));
t('그립헤드에 T핸들', html.includes('function gripHead')&&/gripHead[\s\S]{0,400}tHandle/.test(html));

console.log('=== 3. 암에 매단 장비는 암 끝에 ===');
const hung=A.buildItemMesh(CS,{eqId:'STD-C-001',x:0,y:0,h3:2.2,rot:0,
  parts:[{eqId:'ACC-001',slot:'arm'},{eqId:'MOD-007',slot:'hang'}]});
t('매단 장비 렌더', nodes(hung)>nodes(withArm), `${nodes(withArm)} → ${nodes(hung)}`);
const hb=bbox(hung);
t('암 끝쪽에 걸림', hb.max.x>1.0, hb.max.x.toFixed(2));
t('암 아래로 늘어짐', hb.max.y>=ab.max.y-0.01);
// 암 없이 매달면 안 그려짐(암이 있어야 매달 수 있음)
const hangNoArm=A.buildItemMesh(CS,{eqId:'STD-C-001',x:0,y:0,h3:2.2,rot:0,parts:[{eqId:'MOD-007',slot:'hang'}]});
t('암 없으면 매단 것도 없음', nodes(hangNoArm)===nodes(bare), `${nodes(bare)} vs ${nodes(hangNoArm)}`);

console.log('=== 4. 슬롯이 분리됨 ===');
const sl=A.slotsFor(CS);
const arm=sl.find(x=>x.k==='arm'), hg=sl.find(x=>x.k==='hang');
t('그립암 세트 슬롯 존재', !!arm && arm.n==='그립헤드·암 세트');
t('액세서리만 받음', JSON.stringify(arm.accept)==='["ACC"]', JSON.stringify(arm.accept));
t('암 세트는 1개', arm.max===1);
t('매달기 슬롯 분리', !!hg && JSON.stringify(hg.accept)==='["MOD","LIT","MON"]', hg&&JSON.stringify(hg.accept));
t('A스탠드엔 암 슬롯 없음', !A.slotsFor(A.EQ().find(e=>e.id==='STD-A-001')).some(x=>x.k==='arm'));
t('도움말도 갱신', html.includes('그립헤드·암 세트1 · 암에 매달기2'));
// 실제 결합 경로
A.clearScene(); A.switchMode('layout');
const lit=add('LIT-005',100,100);
const cst=add('STD-C-001',300,100); t('스탠드→조명 = 지지대', link(cst,lit).slot==='support');
const accB=add('ACC-001',500,100);
t('암 세트 → C스탠드 = arm', link(accB,cst).slot==='arm');
const modB=add('MOD-007',700,100);
t('디퓨저 → C스탠드 = hang', link(modB,cst).slot==='hang');

console.log('=== 5. 조립체로 3D에 전달 ===');
A.switchMode('floor'); A.syncFromLayout();
const it=Object.values(A.F().items).find(i=>i.eqId==='LIT-005');
t('부품 3개 전달', A.rigParts(it).length===3, A.rigParts(it).map(p=>p.slot).join(','));
t('지지대 = C스탠드', A.supportOf(it)==='STD-C-001');
t('암 세트 인식', A.armKitOf(it)==='ACC-001');
const m=A.buildItemMesh(A.EQ().find(e=>e.id==='LIT-005'), it);
t('조명+C스탠드+암이 함께 그려짐', bbox(m).max.x>0.9, bbox(m).max.x.toFixed(2));
// 암 없는 경우와 비교
const noArm=Object.assign({},it,{parts:it.parts.filter(p=>p.slot!=='arm'&&p.slot!=='hang')});
t('암 빼면 좁아짐', bbox(A.buildItemMesh(A.EQ().find(e=>e.id==='LIT-005'),noArm)).max.x<0.62,
  bbox(A.buildItemMesh(A.EQ().find(e=>e.id==='LIT-005'),noArm)).max.x.toFixed(2));

console.log('=== 6. 평면도 여유 공간에도 반영 ===');
const c1=A.rigFootprint({eqId:'LIT-005',parts:[{eqId:'STD-C-001',slot:'support'}]});
const c2=A.rigFootprint({eqId:'LIT-005',parts:[{eqId:'STD-C-001',slot:'support'},{eqId:'ACC-001',slot:'arm'}]});
t('암 붙으면 여유 공간 늘어남', c2.clear>c1.clear, `${c1.clear.toFixed(2)} → ${c2.clear.toFixed(2)}`);
t('발자국 자체는 그대로', near(c1.w,c2.w,0.001), `${c1.w} / ${c2.w}`);
t('암 길이의 절반만큼', near(c2.clear-c1.clear, 0.51, 0.06), (c2.clear-c1.clear).toFixed(2));
const s1=A.rigFootprint({eqId:'STD-C-001',parts:[]});
const s2=A.rigFootprint({eqId:'STD-C-001',parts:[{eqId:'ACC-001',slot:'arm'}]});
t('단독 C스탠드도 동일', s2.clear>s1.clear, `${s1.clear.toFixed(2)} → ${s2.clear.toFixed(2)}`);
t('A스탠드는 영향 없음', near(A.rigFootprint({eqId:'STD-A-001',parts:[]}).clear,
   A.rigFootprint({eqId:'STD-A-001',parts:[{eqId:'ACC-001',slot:'arm'}]}).clear, 0.001));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
