const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`switchMode,triflectorMesh,reflectorPanel,roundRectShape,isTriflector,
 buildItemMesh,specOf,footprintOf,rigFootprint,addBlockAt,attachBlock,acceptSlot,syncFromLayout,
 clearScene,itemSize,parabolicSoftbox,
 F:F,T:()=>THREE,cur:currentScene,EQ:()=>EQUIPMENT`,{runTimers:true});
const A=H.api, THREE=A.T();
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const html=require('fs').readFileSync(APP,'utf-8');
const near=(a,b,e=0.03)=>Math.abs(a-b)<=e;
const nodes=o=>{let n=0;o.traverse(()=>n++);return n;};
const bbox=o=>{o.updateMatrixWorld(true);return new THREE.Box3().setFromObject(o);};
const eq=A.EQ().find(e=>e.id==='MOD-010');
H.ctx.confirm=()=>true;

console.log('=== 1. 인식 ===');
t('MOD-010을 트라이플렉터로 인식', A.isTriflector(eq));
t('제품명으로도 인식', A.isTriflector({product:'Lastolite Triflector MkII'}));
t('반사판 표기도 인식', A.isTriflector({product:'3분할 반사판 키트'}));
t('소프트박스는 아님', !A.isTriflector({id:'MOD-002',product:'Softbox 500'}));
t('디퓨저도 아님', !A.isTriflector({id:'MOD-007',product:'디퓨저 750 x 900'}));

console.log('=== 2. 실측 스펙 반영 ===');
const sp=A.specOf('MOD-010');
t('펼침 폭 1.24m', near(sp.w,1.24,0.001), sp.w);
t('높이 0.60m', near(sp.h,0.60,0.001), sp.h);
t('앞뒤 두께 0.42m (날개가 감싸므로)', near(sp.d,0.42,0.001), sp.d);
t('추정 아닌 실측', sp.src==='spec', sp.src);
t('예전 얇은 판 스펙 아님', sp.d>0.1);

console.log('=== 3. 3장 구조 ===');
const tf=A.triflectorMesh(sp);
t('메시 다수', nodes(tf)>=12, nodes(tf));
const b=bbox(tf);
t('펼친 폭이 스펙과 비슷', near(b.max.x-b.min.x, 1.24, 0.25), (b.max.x-b.min.x).toFixed(2));
t('날개가 앞으로 감쌈', b.max.z>0.12, b.max.z.toFixed(2));
t('중앙 패널 높이', b.max.y>0.45, b.max.y.toFixed(2));
t('좌우 대칭', near(Math.abs(b.max.x), Math.abs(b.min.x), 0.05), `${b.min.x.toFixed(2)} / ${b.max.x.toFixed(2)}`);
// 패널 한 장
const pn=A.reflectorPanel(0.36,0.58,0.16);
t('패널 = 검정테두리 + 은반사면', nodes(pn)===3, nodes(pn));
const pb=bbox(pn);
t('테두리가 조금 더 큼', pb.max.x-pb.min.x>0.36, (pb.max.x-pb.min.x).toFixed(3));
t('둥근 모서리', html.includes('function roundRectShape')&&html.includes('quadraticCurveTo'));
t('힌지 클램프', html.includes('힌지 클램프'));
t('프레임 가로바·중앙 지지대', html.includes('const bar = new THREE.Mesh')&&html.includes('const post = new THREE.Mesh'));
t('은반사 재질', /metalness: 0\.72/.test(html));

console.log('=== 4. 소프트박스와 구분 ===');
const sb=A.parabolicSoftbox(0.45,0.42,16);
t('소프트박스는 그대로 보울', bbox(sb).max.y-bbox(sb).min.y>0.35);
const modMesh=A.buildItemMesh(eq,{eqId:'MOD-010',x:0,y:0,h3:1.3,rot:0,parts:[]});
const sbEq=A.EQ().find(e=>e.id==='MOD-002');
const sbMesh=A.buildItemMesh(sbEq,{eqId:'MOD-002',x:0,y:0,h3:1.3,rot:0,parts:[]});
t('반사판은 옆으로 넓다', (bbox(modMesh).max.x-bbox(modMesh).min.x)>1.0,
  (bbox(modMesh).max.x-bbox(modMesh).min.x).toFixed(2));
t('소프트박스는 앞뒤로 깊다', (bbox(sbMesh).max.z-bbox(sbMesh).min.z)>0.2,
  (bbox(sbMesh).max.z-bbox(sbMesh).min.z).toFixed(2));

console.log('=== 5. 스탠드·조명과 조립 ===');
A.clearScene(); A.switchMode('layout');
const mod=A.addBlockAt('MOD-010',100,100);
const std=A.addBlockAt('STD-A-001',300,100);
{ const r=A.acceptSlot(mod,'STD'); if(r) A.attachBlock(std,mod,r); }
A.switchMode('floor'); A.syncFromLayout(false);
const it=Object.values(A.F().items).find(i=>i.eqId==='MOD-010');
t('스탠드 결합', !!it && (it.parts||[]).some(p=>p.eqId==='STD-A-001'), JSON.stringify(it&&it.parts));
const m2=A.buildItemMesh(eq,it);
t('스탠드 위에 올라감', bbox(m2).max.y>1.2, bbox(m2).max.y.toFixed(2));
t('바닥까지 다리', bbox(m2).min.y<0.06, bbox(m2).min.y.toFixed(3));
// 조명 앞 반사판
const lit=A.buildItemMesh(A.EQ().find(e=>e.id==='LIT-009'),
  {eqId:'LIT-009',x:0,y:0,h3:1.6,rot:0,parts:[{eqId:'STD-A-001',slot:'support'},{eqId:'MOD-010',slot:'mod'}]});
t('조명 앞에 세워짐', bbox(lit).max.z>0.5, bbox(lit).max.z.toFixed(2));
t('반사판 분기 존재', html.includes('반사판은 조명 앞에 세워 둔다'));

console.log('=== 6. 평면도 발자국 ===');
const fp=A.rigFootprint({eqId:'MOD-010',parts:[]});
t('발자국 존재', fp.w>0);
const fp2=A.rigFootprint({eqId:'MOD-010',parts:[{eqId:'STD-A-001',slot:'support'}]});
t('스탠드 결합 시 스탠드 발자국', near(fp2.w, A.specOf('STD-A-001').w, 0.01), fp2.w);

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
