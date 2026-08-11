const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`renderRail,toggleRailMore,openCat,openPane,renderCanvas,setRigView,
 blockPos,linkChain,rootOf,attachBlock,acceptSlot,cur:currentScene,
 get more(){return railMore},get cat(){return activeCat},
 MAIN:RAIL_MAIN,MORE:RAIL_MORE,st:()=>state`);
const A=H.api;
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i||''))};
const S=()=>A.cur();

console.log('=== 1. 레일 순서 ===');
t('주요 7개 순서 = 카메라·렌즈·삼각대·오디오·조명·조명모디·스탠드',
  A.MAIN.join(',')==='CAM,LEN,TRP,AUD,LIT,MOD,STD', A.MAIN.join(','));
t('숨김에 짐벌·배터리·전원·저장 포함',
  ['GIM','BAT','PWR','STO'].every(c=>A.MORE.includes(c)));
t('주요/숨김 중복 없음', A.MAIN.every(c=>!A.MORE.includes(c)));
t('15개 전부 배치', A.MAIN.length+A.MORE.length===15, A.MAIN.length+A.MORE.length);

A.renderRail();
let r=H.store['rail-cats'].innerHTML;
const order=[...r.matchAll(/data-c="(\w+)"/g)].map(m=>m[1]);
t('접힘 상태: 전체+주요 7개만', order.join(',')==='ALL,CAM,LEN,TRP,AUD,LIT,MOD,STD', order.join(','));
t('짐벌 숨겨짐', !order.includes('GIM'));
t('더보기 버튼 존재', r.includes('rail-btn more'));
t('더보기에 숨긴 개수 표시', /more[\s\S]{0,300}class="rc">(\d+)</.test(r));

console.log('=== 2. 더보기 토글 ===');
A.toggleRailMore();
t('펼침 상태', A.more===true);
r=H.store['rail-cats'].innerHTML;
const order2=[...r.matchAll(/data-c="(\w+)"/g)].map(m=>m[1]);
t('전체 16개 표시', order2.length===16, order2.length);
t('숨김 순서 = 짐벌·배터리·전원·저장·모니터·케이블·액세서리·기타',
  order2.slice(8).join(',')==='GIM,BAT,PWR,STO,MON,CAB,ACC,ETC', order2.slice(8).join(','));
t('접기 라벨로 변경', r.includes('>접기<'));
A.toggleRailMore();
t('다시 접힘', A.more===false);
t('상태 저장', A.st().railMore===false);

console.log('=== 3. 숨긴 카테고리 선택 시 자동 펼침 ===');
A.openCat('BAT');
t('배터리 선택하면 더보기 자동 펼침', A.more===true && A.cat==='BAT');

console.log('=== 4. 선 연결: 한 줄 세로 나열 ===');
A.openPane('rig');
const sc=S(); sc.blocks={};
const mk=e=>{const id='b'+Math.random().toString(36).slice(2,7);sc.blocks[id]={eqId:e,x:200,y:100};return id;};
const cam=mk('CAM-001');
const trp=mk('TRP-001'); A.attachBlock(trp,cam,A.acceptSlot(cam,'TRP'));
const len=mk('LEN-001'); A.attachBlock(len,cam,A.acceptSlot(cam,'LEN'));
const flt=mk('ACC-010'); A.attachBlock(flt,len,A.acceptSlot(len,'ACC'));
const sto=mk('STO-001'); A.attachBlock(sto,cam,A.acceptSlot(cam,'STO'));
A.setRigView('link');
const chain=A.linkChain(cam,sc);
t('체인 4개 (깊이 우선)', chain.length===4, chain.length);
t('필터가 렌즈 바로 뒤', chain.indexOf(flt)===chain.indexOf(len)+1);
t('rootOf: 필터 → 카메라', A.rootOf(flt,sc)===cam);
const P=chain.map(b=>A.blockPos(b,sc));
const rootP=A.blockPos(cam,sc);
t('모든 부품 x 동일 (한 줄)', new Set(P.map(p=>p.x)).size===1, JSON.stringify(P.map(p=>p.x)));
t('x는 루트에서 30px 안쪽', P[0].x===rootP.x+30, `${P[0].x} vs ${rootP.x}`);
t('y가 균등 간격 72px', P.every((p,i)=>i===0||p.y-P[i-1].y===72), JSON.stringify(P.map(p=>p.y)));
t('첫 부품은 루트 아래 92px', P[0].y===rootP.y+92, `${P[0].y} vs ${rootP.y}`);

console.log('=== 5. 연결선 = 척추 1개 ===');
A.renderCanvas();
const svg=H.store['rig-links'].innerHTML;
const spines=(svg.match(/stroke="#4a5768"/g)||[]).length;
t('세로 척추 1개', spines===1, 'n='+spines);
const branches=(svg.match(/<circle/g)||[]).length;
t('부품마다 갈래점 4개', branches===4, 'n='+branches);
t('꺾인 경로(V..H..V) 없음', !svg.includes('V') || !/d="M[\d.]+ [\d.]+ V[\d.]+ H[\d.]+ V/.test(svg));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
