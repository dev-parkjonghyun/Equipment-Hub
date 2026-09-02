// 서버 gear_specs 치수가 전용(정밀) 클라이언트 SPECS 를 덮지 않는지 검증.
// (로그인 시 서버 옛 치수로 전용 3D 모델이 틀어지던 문제)
const {makeHarness}=require('./harness.js');
const H=makeHarness(`applyServerSpecs,specOf,T:()=>THREE,EQ:()=>EQUIPMENT`,{runTimers:true});
const A=H.api;
const html=require('fs').readFileSync(require('./paths.js').APP,'utf-8');
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const near=(a,b,e=0.001)=>Math.abs(a-b)<=e;

// 적용 전 전용 치수 기억
const pav0=A.specOf('LIT-007');
const proj0=A.specOf('MOD-004');

console.log('=== 1. 서버 옛 치수(어긋난 값)를 흘려도 전용 스펙 보존 ===');
A.applyServerSpecs([
  {id:'LIT-007', w:0.055, h:0.055, d:0.53, src:'추정'},   // 옛 PavoTube (틀린 값)
  {id:'MOD-004', w:0.8,  h:0.8,  d:0.5,  src:'추정'},      // 제네릭 (프로젝션 아님)
  {id:'GIM-001', w:0.202, h:0.415, d:0.268, src:'제조사 공식'}, // w/d 뒤바뀜
  {id:'LIT-001', w:0.231, h:0.231, d:0.399, src:'제조사 공식'}, // 옛 Forza500
  {id:'STD-A-001', w:0.9, d:0.9, h:2.0, src:'제조사 공식'},     // 발자국 축소된 값
  {id:'AUD-003', w:0.08, h:0.08, d:0.25, src:'추정'},      // 제네릭(전용 스펙 없음)
]);

t('PavoTube(LIT-007) 서버로 안 덮임(튜브 유지)', (()=>{const s=A.specOf('LIT-007');return s.len===0.250 && near(s.h,0.038);})(), JSON.stringify(A.specOf('LIT-007')));
t('프로젝션(MOD-004) 서버 제네릭으로 안 덮임', (()=>{const s=A.specOf('MOD-004');return s.w<0.3 && s.w>0.05;})(), JSON.stringify(A.specOf('MOD-004')));
t('짐벌(GIM-001) w/d 안 뒤집힘', (()=>{const s=A.specOf('GIM-001');return near(s.w,0.2678) && near(s.d,0.2019);})(), JSON.stringify(A.specOf('GIM-001')));
t('Forza500(LIT-001) FC-500C 유지(h 0.149)', (()=>{const s=A.specOf('LIT-001');return near(s.h,0.149);})(), JSON.stringify(A.specOf('LIT-001')));
t('A스탠드 발자국 유지(1.28)', (()=>{const s=A.specOf('STD-A-001');return near(s.w,1.28);})(), JSON.stringify(A.specOf('STD-A-001')));

console.log('=== 2. 전용 스펙 없는 제네릭은 서버값 적용 ===');
t('AUD-003 서버 치수 반영', (()=>{const s=A.specOf('AUD-003');return near(s.w,0.08) && near(s.d,0.25);})(), JSON.stringify(A.specOf('AUD-003')));

console.log('=== 3. 코드 가드 존재 ===');
t('applyServerSpecs 가드', html.includes('if (SPECS[x.id]) return;'));
t('loadEquipmentFromServer 가 함수 호출', html.includes('applyServerSpecs(sp);'));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
