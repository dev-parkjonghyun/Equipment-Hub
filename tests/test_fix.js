const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const html=require('fs').readFileSync(APP,'utf-8');
const S=o=>JSON.stringify(Object.assign({currentScene:'default',scenes:{default:{name:'기본 씬',blocks:{},groups:{}}}},o));
const boot=seed=>makeHarness('openPane,renderSets,selToSet,switchMode,toggleSel,st:()=>state,sel:()=>listSel',seed?{seed}:{});

console.log('=== 1. 기본 세트가 항상 도착한다 ===');
[['저장 없음',null],['v2 저장',S({sets:{a:{name:'A',eqIds:['CAM-001']}},setsVersion:2})],
 ['v3 저장',S({sets:{a:{name:'A',eqIds:['CAM-001']}},setsVersion:3})],
 ['현재 버전 저장',S({sets:{a:{name:'A',eqIds:['CAM-001']}},setsVersion:4})],
 ['sets 키 없음',S({})],['sets 빈 객체',S({sets:{},setsVersion:4})]
].forEach(([n,seed])=>{
  const H=boot(seed);
  t(n+' → 기본 세트 존재', !!H.api.st().sets.set_beforeafter);
});
t('버전 게이트 밖에서 병합', (()=>{
  const i=html.indexOf('s.setsVersion !== SETS_VERSION');
  const j=html.indexOf('for (const [k, v] of Object.entries(DEFAULT_SETS))');
  const close=html.indexOf('RETIRED_SETS.forEach');
  return j>close;   // 청소 블록이 닫힌 뒤에 병합
})());

console.log('=== 2. 사용자 세트는 절대 안 건드림 ===');
{ const H=boot(S({sets:{set_mine:{name:'내 세트',eqIds:['CAM-001','LEN-002']}},setsVersion:2}));
  const st=H.api.st();
  t('내 세트 보존', st.sets.set_mine && st.sets.set_mine.eqIds.length===2);
  t('기본 세트도 추가', !!st.sets.set_beforeafter);
  t('이름 안 바뀜', st.sets.set_mine.name==='내 세트'); }
{ const H=boot(S({sets:{set_beforeafter:{name:'내가 고친 이름',eqIds:['CAM-002']}},setsVersion:2}));
  t('같은 키를 고쳐 썼으면 덮어쓰지 않음',
    H.api.st().sets.set_beforeafter.name==='내가 고친 이름'); }

console.log('=== 3. 예시 세트는 회수 ===');
t('회수 목록 존재', html.includes("const RETIRED_SETS = ['set_whiteboard']"));
t('기본에서 제거됨', !html.includes("'set_whiteboard': {"));
{ const H=boot(S({sets:{set_whiteboard:{name:'화이트보드',eqIds:['CAM-003']},set_mine:{name:'내 것',eqIds:['CAM-001']}},setsVersion:3}));
  t('저장분에서도 지워짐', !H.api.st().sets.set_whiteboard);
  t('같이 있던 내 세트는 남음', !!H.api.st().sets.set_mine); }
{ const H=boot(S({sets:{set_whiteboard:{name:'화이트보드',eqIds:['CAM-003']}},setsVersion:4}));
  t('이미 최신 버전이면 유지(재삭제 안 함)', !!H.api.st().sets.set_whiteboard); }

console.log('=== 4. 세트 패널이 실제로 내용을 그린다 ===');
{ const H=boot(null);
  H.api.openPane('sets');
  const h=H.store['sets-list'].innerHTML;
  t('세트 카드 렌더', h.includes('set-card'));
  t('세트 이름 표시', h.includes('시술 전후 사진'));
  t('포함 개수 표시', /10\/10|10<\/span>/.test(h)||h.includes('10'));
  t('"저장된 세트가 없습니다" 아님', !h.includes('저장된 세트가 없습니다'));
  // 목록에서 만든 세트도 즉시 보임
  H.api.switchMode('list');
  H.api.toggleSel('CAM-001',true); H.api.toggleSel('LEN-003',true);
  H.ctx.prompt=()=>'야외 인터뷰';
  H.api.selToSet();
  H.api.openPane('sets');
  const h2=H.store['sets-list'].innerHTML;
  t('목록에서 만든 세트가 패널에 보임', h2.includes('야외 인터뷰'));
  const made=Object.values(H.api.st().sets).find(x=>x.name==='야외 인터뷰');
  t('내용도 담김', made && made.eqIds.length===2, made&&made.eqIds.join(',')); }

console.log('=== 5. 레일 스크롤 ===');
t('레일 전체가 스크롤 영역', /#rail\{[^}]*overflow-y:auto/.test(html));
t('스크롤 튐 방지', /#rail\{[^}]*overscroll-behavior:contain/.test(html));
t('안쪽 이중 스크롤 제거', /\.rail-scroll\{flex:0 0 auto/.test(html));
t('도구 그룹이 찌그러지지 않음', /\.rail-grp\.top\{flex:0 0 auto/.test(html));
t('스크롤바 스타일', html.includes('#rail::-webkit-scrollbar-thumb'));
t('하단 모드 도크 자리 확보', /#rail\{[^}]*padding:12px 0 92px/.test(html));
t('카테고리·도구 모두 한 스크롤에', (()=>{
  const b=html.slice(html.indexOf('<aside id="rail"'), html.indexOf('</aside>'));
  return b.includes('rail-grp top') && b.includes('id="rail-cats"');})());

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
