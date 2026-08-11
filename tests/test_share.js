const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`switchMode,sbCfg,sbReady,shareId,sceneForShare,createShareLink,copyShareLink,
 closeShare,revokeShare,loadSharedScene,openShareSetup,closeShareSetup,saveShareSetup,isViewOnly,
 pickGearPhoto,sendGearPhoto,renderPhotoResult,photoChecked,photoToSet,photoToLayout,closePhoto,
 addBlockAt,setEq,startFloorDrag,startFreeDrag,renderScenePane,openPane,addSubject,syncFromLayout,
 F:F,cur:currentScene,st:()=>state,EQ:()=>EQUIPMENT,setVO:v=>{viewOnly=v},
 setPR:v=>{photoResult=v},getPR:()=>photoResult`,{runTimers:true});
const A=H.api;
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const html=require('fs').readFileSync(APP,'utf-8');
const fs=require('fs');
const el=id=>H.store[id]||(H.store[id]=require('./harness.js').mkEl(id));
H.ctx.confirm=()=>true;

(async function main(){
console.log('=== 1. 비밀은 앱에 없다 ===');
t('anon 키 자리만 있고 값은 비어 있음', /const SB_DEFAULT = \{ url: '', anon: '' \}/.test(html));
t('API 키 값이 앱에 없음', !/sk-ant-[A-Za-z0-9_-]{10,}/.test(html));
t('앱이 API 키를 저장·전송하지 않음', (()=>{
  // 키 이름이 안내 문구에 나오는 건 괜찮다. 실제로 다루지만 않으면 된다.
  const bad = /ANTHROPIC_API_KEY\s*[:=]|state\.\w*apiKey|headers[^}]*x-api-key/i;
  return !bad.test(html);})());
t('키 이름은 안내 목적으로만', (html.match(/ANTHROPIC_API_KEY/g)||[]).length<=2);
t('비밀 키 경고', html.includes('Secret key(sb_secret_…)는 절대 넣지 마세요')||html.includes('이 키는 접근 제한을 무시하므로'));
t('anon 키는 공개돼도 된다고 안내', html.includes('anon 키는 공개돼도 되는 값'));
const fn=fs.readFileSync(SUPA('functions/read-gear-photo/index.ts'),'utf-8');
const sql=fs.readFileSync(SUPA('schema.sql'),'utf-8');
const audit=fs.readFileSync(SUPA('00-audit-existing.sql'),'utf-8');
t('API 키는 함수 시크릿에서만', fn.includes("Deno.env.get('ANTHROPIC_API_KEY')"));
t('키 없으면 거부', fn.includes('ANTHROPIC_API_KEY 가 설정되지 않았습니다'));

console.log('=== 2. 서버 설정 ===');
t('설정 없으면 비활성', A.sbReady()===false);
el('sb-url').value='https://abcdefgh.supabase.co';
el('sb-anon').value='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abcdefghijklmnopqrstuvwxyz0123456789';
A.saveShareSetup();
t('저장됨', A.sbReady()===true);
t('주소 정규화', A.sbCfg().url==='https://abcdefgh.supabase.co');
// 잘못된 값 거부
el('sb-url').value='http://내서버.com';
A.saveShareSetup();
t('잘못된 주소 거부', A.sbCfg().url==='https://abcdefgh.supabase.co', A.sbCfg().url);
t('안내 표시', H.alerts.some(a=>a.includes('주소 형식')));
el('sb-url').value='https://abcdefgh.supabase.co';
el('sb-anon').value='짧음';
A.saveShareSetup();
t('엉뚱한 키 거부', A.sbCfg().anon.length>40);
// 새 형식 키
el('sb-anon').value='sb_publishable_d0h34gAFmb3g5674LVgN4A_PUQgz';
A.saveShareSetup();
t('새 형식(sb_publishable_) 허용', A.sbCfg().anon.startsWith('sb_publishable_'));
// 비밀 키는 막는다
el('sb-anon').value='sb_secret_rbF69abcdefghijklmnop';
A.saveShareSetup();
t('Secret key 차단', !A.sbCfg().anon.startsWith('sb_secret_'), A.sbCfg().anon.slice(0,14));
t('경고 표시', H.alerts.some(a=>a.includes('비밀 키')));
el('sb-anon').value='sb_publishable_d0h34gAFmb3g5674LVgN4A_PUQgz';
A.saveShareSetup();

console.log('=== 3. 공유 링크 id ===');
const ids=new Set(); for(let i=0;i<400;i++) ids.add(A.shareId());
t('400개 모두 다름', ids.size===400);
t('길이 12자', A.shareId().length===12);
t('헷갈리는 글자(l,o,0,1) 제외', !/[lo01]/.test([...ids].join('')));
t('추측 어려운 공간', Math.pow(32,12)>1e18);

console.log('=== 4. 공유 데이터 ===');
A.switchMode('layout');
A.addBlockAt('CAM-003',100,100); A.addBlockAt('LIT-001',260,100);
A.switchMode('floor'); A.addSubject();
const pay=A.sceneForShare();
t('씬 이름 포함', !!pay.name);
t('배치도 포함', Object.keys(pay.blocks).length===2);
t('평면도 포함', !!pay.floor && Object.keys(pay.floor.items).length===2);
t('세트 포함', !!pay.sets);
t('별칭 수정분 포함', pay.eqEdits!==undefined);
t('서버 키는 안 담김', pay.sb===undefined && !JSON.stringify(pay).includes('eyJhbGci'));
t('보낸 링크 목록도 안 담김', pay.shares===undefined);
t('만든 시각 기록', !!pay.madeAt);
{ const bytes=JSON.stringify(pay).length;
  t('현실적인 크기', bytes<200000, (bytes/1024).toFixed(1)+'KB'); }

console.log('=== 5. 공유 링크 만들기 ===');
let sent=null;
H.ctx.fetch=async(u,o)=>{ sent={u,o}; return {ok:true,status:201,json:async()=>({}),text:async()=>''} ; };
H.ctx.location={origin:'https://ehstudio.github.io',pathname:'/gear/',search:''};
H.ctx.Blob=function(a){ this.size=JSON.stringify(a).length; };
H.ctx.navigator={clipboard:{writeText(){}},userAgent:'test'};
await A.createShareLink();
t('POST 요청', sent && sent.o.method==='POST');
t('gear_scenes 테이블로', sent.u.includes('/rest/v1/gear_scenes'));
t('apikey 헤더 전송', !!sent.o.headers.apikey);
t('새 키는 Authorization 안 붙임', sent.o.headers.apikey.startsWith('sb_')
   ? sent.o.headers.Authorization===undefined : true,
   JSON.stringify(Object.keys(sent.o.headers)));
{ const b=JSON.parse(sent.o.body);
  t('만료일 설정', !!b.expires_at, b.expires_at);
  t('공개 플래그', b.is_public===true);
  t('id 포함', b.id && b.id.length===12); }
t('링크 표시', el('share-link').value.includes('?s='), el('share-link').value);
t('링크 형태', /^https:\/\/ehstudio\.github\.io\/gear\/\?s=[a-z2-9]{12}$/.test(el('share-link').value));
t('만료 안내', el('share-meta').textContent.includes('만료'));
t('보낸 링크 기록', (A.st().shares||[]).length===1);
t('보기 전용 명시', el('share-meta').textContent.includes('보기 전용'));

console.log('=== 6. 링크 회수 ===');
const sid=A.st().shares[0].id;
sent=null;
await A.revokeShare(sid);
t('PATCH 요청', sent && sent.o.method==='PATCH');
t('해당 씬만', sent.u.includes('id=eq.'+sid));
t('공개 해제', JSON.parse(sent.o.body).is_public===false);
t('목록에 회수 표시', A.st().shares[0].dead===true);

console.log('=== 7. 읽기 전용 모드 ===');
t('평상시엔 편집 가능', A.isViewOnly()===false);
A.setVO(true);
t('읽기 전용 진입', A.isViewOnly()===true);
const before=Object.keys(A.cur().blocks).length;
A.addBlockAt('MON-001',100,100);
t('블록 추가 차단', Object.keys(A.cur().blocks).length===before);
const eq0=A.EQ().find(e=>e.id==='CAM-003');
const nick0=eq0.nick;
A.setEq('CAM-003','nick','바꿔보기');
t('별칭 수정 차단', eq0.nick===nick0, eq0.nick);
t('평면도 드래그 차단', html.includes('function startFloorDrag(e, type, id) {\n    if (isViewOnly()) return;'));
t('3D 드래그 차단', html.includes('function startFreeDrag(e, fid) {\n    if (isViewOnly()) return false;'));
t('기즈모 자체를 안 만듦', html.includes('if (!isViewOnly()) {\n            R3.giz = buildGizmo(isSubj);'));
t('Delete 차단', html.includes("if (e.key === 'Delete' || e.key === 'Backspace') {\n        if (isViewOnly()) return;"));
A.openPane('scenes');
t('씬 패널에 공유 도구 숨김', el('scene-body').innerHTML.includes('보기 전용으로 열린 배치'));
t('배너 마크업', html.includes('id="vo-bar"')&&html.includes('보기 전용으로 공유된 배치'));
t('편집 UI 숨김 CSS', html.includes('#app.view-only #list-tools'));
t('3D·평면도 전환은 허용', html.includes('#app.view-only #mode-dock button{opacity:1;pointer-events:auto}'));
A.setVO(false);

console.log('=== 8. 공유 링크 열기 ===');
H.ctx.fetch=async(u)=>{
  if(u.includes('/rest/v1/gear_scenes?id=eq.'))
    return {ok:true,status:200,json:async()=>[{name:'인터뷰 A룸',expires_at:null,
      data:{name:'인터뷰 A룸',blocks:{b1:{eqId:'CAM-003',x:10,y:10}},groups:{},
            floor:{zoom:50,items:{},rooms:[],subjects:[]},sets:{},eqEdits:{}}}]};
  return {ok:true,status:200,json:async()=>({})};
};
await A.loadSharedScene('abcdefghijkm');
t('읽기 전용으로 진입', A.isViewOnly()===true);
t('공유된 씬만 남음', Object.keys(A.st().scenes).join()==='shared');
t('이름 반영', A.cur().name==='인터뷰 A룸');
t('배너에 이름', el('vo-name').textContent==='인터뷰 A룸');
t('배너 표시', el('vo-bar').style.display==='flex');
t('조회수 기록 호출', html.includes('/rest/v1/rpc/gear_bump_view'));
A.setVO(false);

console.log('=== 9. 사진 인식 ===');
t('버튼 존재', html.includes('pickGearPhoto()')&&html.includes('사진에서 불러오기'));
t('서버 없으면 안내', html.includes("alert('먼저 서버를 연결해 주세요."));
t('업로드 전 축소', html.includes('downscaleImage(rd.result, (data) => sendGearPhoto(data))'));
t('보유 장비를 함께 전송', html.includes('const eqList = EQUIPMENT.map'));
// 결과 렌더
A.setPR({matched:[
  {line:'M4',eqId:'CAM-003',why:'M4=a7m4',confidence:0.95},
  {line:'60b + 프레넬',eqId:'LIT-005',confidence:0.9},
  {line:'애매한 글씨',eqId:'AUD-003',confidence:0.4}],
  unmatched:[{line:'아이패드 세트',reason:'보유 목록에 없음'}], note:'조명 3세트로 보입니다'});
A.renderPhotoResult(A.getPR());
const pb=el('photo-body').innerHTML;
t('찾은 장비 표시', pb.includes('CAM-003')&&pb.includes('LIT-005'));
t('원문도 같이', pb.includes('M4')&&pb.includes('60b + 프레넬'));
t('못 찾은 것 표시', pb.includes('아이패드 세트')&&pb.includes('보유 목록에 없음'));
t('총평 표시', pb.includes('조명 3세트로 보입니다'));
t('확신 낮으면 체크 해제', (pb.match(/checked/g)||[]).length===2, (pb.match(/checked/g)||[]).length);
t('확인 필요 표시', pb.includes('확인 필요'));
t('결과 없으면 안내', html.includes('장비를 찾지 못했습니다'));
t('실패 시 안내', html.includes('조명 반사를 줄여보세요'));
t('서버 미설치 시 안내', html.includes('사진 인식 기능은 아직 설치 전입니다'));
t('키 없을 때 안내', html.includes('분석 키가 설정되지 않았습니다'));
t('크레딧 부족 안내', html.includes('분석 크레딧이 부족합니다'));

console.log('=== 10. 사진 → 세트 · 배치도 ===');
t('서버가 없는 자산번호를 걸러냄', fn.includes('const valid = new Set(equipment.map')&&fn.includes('valid.has(x.eqId)'));
t('세트 저장 버튼', html.includes('photoToSet()'));
t('배치도로 버튼', html.includes('photoToLayout()'));
t('선택된 것만 담음', html.includes('.filter(el => el.checked)'));
t('중복 제거', html.includes('[...new Set(ids)]'));
t('업로드 크기 상한', fn.includes('maxBytes: 5 * 1024 * 1024'));
t('이미지 형식 검사', fn.includes('JPEG · PNG · WebP 만 지원합니다'));
t('현장 약어 이해 지시', fn.includes('"M4"=a7m4')&&fn.includes('Mark II'));
t('약어 규칙이 한곳에 모임', fn.includes('const SHORTHAND'));
t('모델을 시크릿으로 교체 가능', fn.includes("Deno.env.get('AI_MODEL')"));
t('읽기 엔진 교체 가능', fn.includes("Deno.env.get('READER')")&&fn.includes('readWithClova'));
t('어느 경로를 탔는지 응답에', fn.includes('engine: res.engine'));
t('억지 매칭 금지 지시', fn.includes('틀린 매칭이 빈칸보다 나쁩니다'));



console.log('=== 11. 기존 프로젝트에 얹기 ===');
t('모든 테이블에 gear_ 접두사', sql.includes('public.gear_scenes')&&sql.includes('public.gear_scene_views'));
t('접두사 없는 테이블 없음', !/create table if not exists public\.(?!gear_)/.test(sql));
t('함수도 gear_', sql.includes('public.gear_bump_view')&&sql.includes('public.gear_purge_expired'));
t('정책 이름도 구분', sql.includes('"gear: anon reads live scenes"'));
t('버킷도 gear-', sql.includes("'gear-photos'")&&sql.includes("'gear-plans'"));
t('기존 테이블 건드리지 않음', (()=>{
  const risky = sql.split('\n').filter(l=>{
    const t=l.trim().toLowerCase();
    if(t.startsWith('--')) return false;
    if(!/^(drop table|truncate|alter table|revoke|grant)/.test(t)) return false;
    // gear_ 대상이거나 schema public 전체 usage 부여만 허용
    return !/gear_/.test(t) && !/grant usage on schema public/.test(t);
  });
  return risky.length===0;})(), '위험 구문 확인');
t('이미 있으면 유지', sql.includes('create table if not exists')&&sql.includes('기존 데이터 유지'));
t('사전 점검 SQL 제공', audit.includes('RLS 꺼진 테이블')&&audit.includes('익명 수정·삭제 권한'));
t('점검은 읽기만 (쓰기 구문 없음)', (()=>{
  const stmts = audit.replace(/--.*$/gm,'').split(/\n\s*\n/)
    .map(x=>x.trim()).filter(Boolean);
  return stmts.every(x=>/^select/i.test(x));
})(), audit.replace(/--.*$/gm,'').split(/\n\s*\n/).map(x=>x.trim()).filter(Boolean)
  .filter(x=>!/^select/i.test(x)).map(x=>x.slice(0,40)));
t('앱도 gear_ 경로 사용', html.includes('/rest/v1/gear_scenes')&&!html.includes('/rest/v1/scenes'));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
})();
