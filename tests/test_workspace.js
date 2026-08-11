// 씬·세트를 스튜디오 공용 작업공간(gear_workspaces)에 서버 저장하는 기능 검증.
const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const fs=require('fs');
const H=makeHarness(`switchMode,saveState,pullWorkspace,pushWorkspace,scheduleWorkspaceSync,
 workspaceForServer,isLoggedIn,addBlockAt,
 cur:currentScene,st:()=>state,EQ:()=>EQUIPMENT,setVO:v=>{viewOnly=v}`,{runTimers:true});
const A=H.api;
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const html=fs.readFileSync(APP,'utf-8');
const tick=(ms=15)=>new Promise(r=>setTimeout(r,ms));   // 실제 Node 타이머로 async flush
const login =()=>{A.st().auth={access:'ACCESS',email:'dev@ehstudio.net',expires:Date.now()+3600000};};
const logout=()=>{A.st().auth={};};
const empty =()=>({ok:true,status:201,json:async()=>null,text:async()=>''});
const okJson=(b)=>({ok:true,status:200,json:async()=>b,text:async()=>JSON.stringify(b)});

(async function main(){
let calls=[];
const record=(handler)=>{ H.ctx.fetch=async(u,o)=>{ calls.push({u,o:o||{method:'GET'}}); return handler? handler(u,o) : empty(); }; };

console.log('=== 1. 로그인 상태에서 저장 → 서버 upsert ===');
calls=[]; login();
record((u,o)=> u.includes('gear_workspaces') && (!o||(o.method||'GET')==='GET') ? okJson([]) : empty());
A.cur().blocks['b1']={eqId:'CAM-003',x:1,y:1};
A.saveState();
await tick();
const post=calls.find(c=>c.u.includes('/rest/v1/gear_workspaces') && c.o.method==='POST');
t('작업공간 upsert POST 발생', !!post);
t('공용 단일 행(id=studio)', post && JSON.parse(post.o.body).id==='studio');
t('씬 데이터 포함', post && JSON.parse(post.o.body).data && JSON.parse(post.o.body).data.scenes!==undefined);
t('merge-duplicates upsert 헤더', post && String(post.o.headers.Prefer||'').includes('resolution=merge-duplicates'));
t('updated_at 함께 보냄', post && !!JSON.parse(post.o.body).updated_at);

console.log('=== 2. 로그아웃이면 서버 저장 안 함 ===');
calls=[]; logout();
record();
A.cur().blocks['b2']={eqId:'LIT-001',x:2,y:2};
A.saveState();
await tick();
t('로그아웃 시 gear_workspaces 미호출', !calls.some(c=>c.u.includes('gear_workspaces')));

console.log('=== 3. 보기 전용이면 서버 저장 안 함 ===');
calls=[]; login(); A.setVO(true);
record();
await A.pushWorkspace();
A.saveState();                       // viewOnly 라 early-return
await tick();
t('보기 전용 시 gear_workspaces 미호출', !calls.some(c=>c.u.includes('gear_workspaces')));
A.setVO(false);

console.log('=== 4. 로그인 시 서버 작업공간을 가져옴 ===');
login();
H.ctx.fetch=async(u,o)=>{
  if(u.includes('gear_workspaces') && (!o||(o.method||'GET')==='GET'))
    return okJson([{updated_at:'2026-01-01T00:00:00Z',
      data:{scenes:{sv:{name:'서버씬',blocks:{},groups:{},floor:null,mode:'floor'}},sets:{},currentScene:'sv'}}]);
  return empty();
};
await A.pullWorkspace();
t('서버 씬으로 교체', !!A.st().scenes.sv && A.cur().name==='서버씬');
t('현재 씬도 서버 값', A.st().currentScene==='sv');

console.log('=== 5. 서버가 비어있으면 로컬 씬을 올린다(마이그레이션) ===');
login();
let migrated=false;
H.ctx.fetch=async(u,o)=>{
  if(u.includes('gear_workspaces') && o && o.method==='POST'){ migrated=true; return empty(); }
  if(u.includes('gear_workspaces')) return okJson([]);   // 서버에 행 없음
  return empty();
};
await A.pullWorkspace();
await tick();
t('서버 비면 로컬 씬 push(마이그레이션)', migrated);

console.log('=== 6. 오프라인/서버오류여도 앱은 정상 ===');
login();
H.ctx.fetch=async()=>{ throw new Error('network down'); };
let threw=false;
try { await A.pushWorkspace(); await A.pullWorkspace(); } catch(e){ threw=true; }
t('서버 실패해도 예외 안 남', !threw);
t('상태 그대로 유지', !!A.cur());

console.log('=== 7. SQL 안전성 (05-workspace.sql) ===');
const wsql=fs.readFileSync(SUPA('05-workspace.sql'),'utf-8');
t('gear_ 접두 테이블', wsql.includes('public.gear_workspaces'));
t('RLS 켜짐', wsql.includes('enable row level security'));
t('공용 단일 행(id=studio)', wsql.includes("default 'studio'"));
t('로그인 계정만 정책', wsql.includes('to authenticated'));
t('익명에 권한/정책 없음', !wsql.includes('to anon') && wsql.includes('revoke all on public.gear_workspaces from anon'));
t('접두사 없는 테이블 없음', !/create table if not exists public\.(?!gear_)/.test(wsql));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
})();
