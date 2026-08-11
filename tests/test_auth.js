const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`switchMode,sbLogin,sbRefresh,sbLogout,ensureAuth,authToken,isLoggedIn,authEmail,
 openLogin,closeLogin,doLogin,syncAuthUI,requireLogin,sbHeaders,saveShareSetup,sbCfg,sbReady,
 loadEquipmentFromServer,eqIsServer,saveEqToServer,addEquipment,retireEquipment,setEq,
 renderList,renderPalette,updateListSummary,applyEqEdits,dispName,specOf,
 EQ:()=>EQUIPMENT,SP:()=>SPECS,st:()=>state,cur:currentScene,
 setSrc:v=>{eqSource=v},getSrc:()=>eqSource`,{runTimers:true});
const A=H.api;
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const html=require('fs').readFileSync(APP,'utf-8');
const el=id=>H.store[id]||(H.store[id]=require('./harness.js').mkEl(id));
const tick=(ms=20)=>new Promise(r=>setTimeout(r,ms));
H.ctx.confirm=()=>true;

const ROWS=[
 {id:'CAM-001',nick:null,cat:'CAM',cat_label:'카메라 본체(CAM)',sub:'미러리스',product:'Sony Fx3',brand:'Sony',model:'FX3',status:'정상',location:'선반 A-1',note:null,sort_order:1},
 {id:'LEN-002',nick:'망원',cat:'LEN',cat_label:'렌즈(LEN)',sub:'줌',product:'Sony 70-200 F2.8 GM2',brand:'Sony',model:null,status:'정상',location:null,note:null,sort_order:2},
 {id:'TRP-001',nick:null,cat:'TRP',cat_label:'삼각대(TRP)',sub:'비디오',product:'manfrotto MVK504XTWINFA',brand:'Manfrotto',model:null,status:'수리필요',location:null,note:'헤드 뻑뻑함',sort_order:3},
];
const SPECROWS=[{id:'TRP-001',w:1.05,d:1.05,h:1.3,h_min:0.435,h_max:1.73,default_h:1.2,src:'제조사 공식'}];
let calls=[];
function mockServer(){
  calls=[];
  H.ctx.fetch=async(u,o={})=>{
    calls.push({u,method:o.method||'GET',headers:o.headers||{},body:o.body});
    if(u.includes('/auth/v1/token?grant_type=password')){
      const b=JSON.parse(o.body);
      if(b.password!=='good') return {ok:false,status:400,json:async()=>({error_description:'Invalid login credentials'})};
      return {ok:true,status:200,json:async()=>({access_token:'ACCESS1',refresh_token:'REFRESH1',
        expires_in:3600,user:{id:'u-1',email:b.email}})};
    }
    if(u.includes('grant_type=refresh_token'))
      return {ok:true,status:200,json:async()=>({access_token:'ACCESS2',refresh_token:'REFRESH2',expires_in:3600})};
    if(u.includes('/rest/v1/gear_equipment?select='))
      return {ok:true,status:200,json:async()=>ROWS,text:async()=>JSON.stringify(ROWS)};
    if(u.includes('/rest/v1/gear_specs?select='))
      return {ok:true,status:200,json:async()=>SPECROWS,text:async()=>JSON.stringify(SPECROWS)};
    return {ok:true,status:204,json:async()=>null,text:async()=>''};
  };
}
mockServer();
el('sb-url').value='https://abcdefgh.supabase.co';
el('sb-anon').value='sb_publishable_d0h34gAFmb3g5674LVgN4A_PUQgz';
A.saveShareSetup();

(async function main(){

console.log('=== 1. 로그인 ===');
t('처음엔 로그아웃', A.isLoggedIn()===false);
try { await A.sbLogin('dev@ehstudio.net','wrong'); t('틀린 비번은 실패',false); }
catch(e){ t('틀린 비번은 실패', /맞지 않습니다/.test(e.message), e.message); }
t('실패해도 로그인 안 됨', A.isLoggedIn()===false);
await A.sbLogin('dev@ehstudio.net','good');
t('로그인 성공', A.isLoggedIn()===true);
t('이메일 기억', A.authEmail()==='dev@ehstudio.net');
t('토큰 저장', A.authToken()==='ACCESS1');
t('새로고침해도 유지(localStorage)', A.st().auth.refresh==='REFRESH1');

console.log('=== 2. 토큰 갱신 ===');
A.st().auth.expires = Date.now() - 1000;        // 만료시킴
t('만료된 토큰은 안 씀', A.authToken()===null);
t('자동 갱신', await A.ensureAuth()===true);
t('새 토큰으로 교체', A.authToken()==='ACCESS2');
// 갱신 실패 = 로그아웃
H.ctx.fetch=async(u)=>u.includes('refresh_token')
  ? {ok:false,status:400,json:async()=>({}),text:async()=>''}
  : {ok:true,status:200,json:async()=>({}),text:async()=>''};
A.st().auth.expires = Date.now()-1000;
t('갱신 실패하면 로그아웃', await A.ensureAuth()===false);
t('세션 비워짐', A.isLoggedIn()===false);
mockServer();
await A.sbLogin('dev@ehstudio.net','good');

console.log('=== 3. 요청 헤더 ===');
{ const h=A.sbHeaders(A.sbCfg().anon);
  t('apikey 는 공개키', h.apikey.startsWith('sb_publishable_'));
  t('Authorization 은 사용자 토큰', h.Authorization==='Bearer ACCESS1', h.Authorization); }
A.sbLogout();
{ const h=A.sbHeaders(A.sbCfg().anon);
  t('로그아웃하면 사용자 토큰 없음', h.Authorization===undefined, h.Authorization); }
await A.sbLogin('dev@ehstudio.net','good');

console.log('=== 4. 서버에서 장비 읽기 ===');
t('불러오기 성공', await A.loadEquipmentFromServer()===true);
t('서버가 원본', A.eqIsServer()===true);
t('행 수 반영', A.EQ().length===3, A.EQ().length);
{ const e=A.EQ().find(x=>x.id==='CAM-001');
  t('필드 매핑', e.product==='Sony Fx3'&&e.loc==='선반 A-1'&&e.catLabel==='카메라 본체(CAM)',
    JSON.stringify(e)); }
{ const e=A.EQ().find(x=>x.id==='LEN-002');
  t('별칭 반영', e.nick==='망원');
  t('빈 값은 빈 문자열', e.model===''); }
{ const sp=A.specOf('TRP-001');
  t('치수도 서버에서', sp.hMax===1.73&&sp.hMin===0.435, JSON.stringify(sp));
  t('출처 코드 변환', sp.src==='spec', sp.src); }
t('표시 이름 계산 동작', A.dispName(A.EQ().find(x=>x.id==='CAM-001'))==='Fx3');

console.log('=== 5. 서버가 안 되면 파일 목록으로 ===');
H.ctx.fetch=async()=>({ok:false,status:503,json:async()=>({}),text:async()=>'down'});
const before=A.EQ().length;
t('실패 시 false', await A.loadEquipmentFromServer()===false);
t('로컬로 전환', A.eqIsServer()===false);
t('기존 목록 유지(앱이 죽지 않음)', A.EQ().length===before);
mockServer(); await A.loadEquipmentFromServer();

console.log('=== 6. 수정은 로그인해야 ===');
const cam=A.EQ().find(e=>e.id==='CAM-001');
A.setEq('CAM-001','nick','메인캠'); await tick();
t('로그인 상태면 수정됨', cam.nick==='메인캠');
{ const p=calls.filter(c=>c.method==='PATCH');
  t('서버로 PATCH', p.length===1, p.length);
  t('해당 장비만', p[0].u.includes('id=eq.CAM-001'));
  t('열 이름 매핑(nick)', JSON.parse(p[0].body).nick==='메인캠');
  t('사용자 토큰으로', p[0].headers.Authorization==='Bearer ACCESS1'); }
A.setEq('CAM-001','loc','케이스 2'); await tick();
{ const p=calls.filter(c=>c.method==='PATCH');
  t('보관위치는 location 열로', JSON.parse(p[1].body).location==='케이스 2'); }
A.setEq('CAM-001','note',''); await tick();
{ const p=calls.filter(c=>c.method==='PATCH');
  t('빈 값은 null 로', JSON.parse(p[2].body).note===null); }
// 로그아웃 상태에서는 막힌다
A.sbLogout();
const nick0=cam.nick;
A.setEq('CAM-001','nick','몰래수정'); await tick();
t('로그아웃이면 수정 차단', cam.nick===nick0, cam.nick);
t('로그인 창이 뜸', H.store['login-modal'].classList.contains('on'));
A.closeLogin();
await A.sbLogin('dev@ehstudio.net','good');

console.log('=== 7. 저장 실패하면 되돌린다 ===');
const len=A.EQ().find(e=>e.id==='LEN-002');
const old=len.nick;
H.ctx.fetch=async(u,o={})=>{
  if(u.includes('grant_type=refresh_token')) return {ok:true,status:200,json:async()=>({access_token:'A3',expires_in:3600})};
  if((o.method||'GET')==='PATCH') return {ok:false,status:403,json:async()=>({}),text:async()=>'권한 없음'};
  return {ok:true,status:200,json:async()=>ROWS,text:async()=>''};
};
A.setEq('LEN-002','nick','실패할값');
await tick(40);
t('실패하면 원래대로', len.nick===old, len.nick);
t('사용자에게 알림', H.alerts.some(a=>a.includes('저장하지 못했습니다')));
mockServer();

console.log('=== 8. 장비 추가 ===');
await A.loadEquipmentFromServer();
H.ctx.prompt=(q)=>/카테고리/.test(q)?'ACC':/제품명/.test(q)?'새 클램프':'';
await A.addEquipment();
{ const p=calls.filter(c=>c.method==='POST'&&c.u.includes('gear_equipment'));
  t('POST 로 추가', p.length===1, p.length);
  const b=JSON.parse(p[0].body);
  t('자산번호 자동 생성', /^ACC-\d{3}$/.test(b.id), b.id);
  t('카테고리 저장', b.cat==='ACC');
  t('제품명 저장', b.product==='새 클램프');
  t('기본 상태 정상', b.status==='정상'); }
// 없는 카테고리는 거부
H.ctx.prompt=(q)=>/카테고리/.test(q)?'ZZZ':'x';
const n0=calls.filter(c=>c.method==='POST').length;
await A.addEquipment();
t('없는 카테고리 거부', calls.filter(c=>c.method==='POST').length===n0);
t('안내 표시', H.alerts.some(a=>a.includes('없는 카테고리')));
// 로그아웃이면 막힘
A.sbLogout();
H.ctx.prompt=()=>'ACC';
const n1=calls.filter(c=>c.method==='POST').length;
await A.addEquipment();
t('로그아웃이면 추가 차단', calls.filter(c=>c.method==='POST').length===n1);
await A.sbLogin('dev@ehstudio.net','good');

console.log('=== 9. 목록에서 내리기 ===');
await A.loadEquipmentFromServer();
await A.retireEquipment('TRP-001'); await tick();
{ const p=calls.filter(c=>c.method==='PATCH');
  const last=p[p.length-1];
  t('active=false 로 표시', JSON.parse(last.body).active===false);
  t('완전 삭제가 아님', !calls.some(c=>c.method==='DELETE')); }

console.log('=== 10. 화면 ===');
t('로그인 칩', html.includes('id="auth-chip"'));
A.syncAuthUI();
t('로그인 상태 표시', el('auth-chip').innerHTML.includes('dev'), el('auth-chip').innerHTML);
t('서버 연결 전엔 숨김', html.includes("b.style.display = sbReady() ? 'inline-flex' : 'none'"));
A.renderList();
{ const sum=H.store['list-summary'].innerHTML;
  t('데이터 출처 표시', sum.includes('서버 · 수정 가능'), sum.slice(-120)); }
A.sbLogout(); A.renderList();
{ const sum=H.store['list-summary'].innerHTML;
  t('로그아웃하면 보기만', sum.includes('서버 · 보기만')); }
t('장비 추가 버튼', html.includes('addEquipment()'));
t('내리기 버튼', html.includes('retireEquipment('));
t('비밀번호 입력은 password 타입', html.includes('id="lg-pw" type="password"'));
t('엔터로 로그인', html.includes("if(event.key==='Enter')doLogin()"));

console.log('=== 11. 서버 없이도 동작 ===');
A.st().sb={url:'',anon:''};
A.setSrc('local');
t('서버 미연결', A.sbReady()===false);
t('로그인 요구 안 함', A.requireLogin('수정')===true);
{ const e=A.EQ()[0]; const before=e.nick;
  A.setEq(e.id,'nick','오프라인수정');
  t('브라우저에만 저장', e.nick==='오프라인수정');
  t('eqEdits 에 기록', !!(A.st().eqEdits||{})[e.id]); }

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
})();
