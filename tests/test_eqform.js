// 장비 추가·수정 폼 모달: 자동 채번, 추가(POST)·수정(PATCH), 가드.
const {APP}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`openEqForm,closeEqForm,submitEqForm,nextAssetId,addEquipment,eqFormCatChanged,
 fillEqCatSelect,loadEquipmentFromServer,renderList,renderPalette,
 setEqSrc:v=>{eqSource=v},getEqFormId:()=>eqFormId,
 EQ:()=>EQUIPMENT,st:()=>state`,{runTimers:true});
const A=H.api;
const html=require('fs').readFileSync(APP,'utf-8');
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const el=id=>H.store[id]||(H.store[id]=require('./harness.js').mkEl(id));

// 로그인 + 서버 연결 상태로 만든다
const login=()=>{ A.st().auth={access:'ACCESS',email:'dev@ehstudio.net',expires:Date.now()+3600000}; A.setEqSrc('server'); };
const logout=()=>{ A.st().auth={}; };
// sbFetch 는 r.text() 를 파싱한다. GET 은 현재 EQUIPMENT 를 서버 행 모양으로 돌려준다.
const rowsJSON=()=>JSON.stringify(A.EQ().map(e=>({id:e.id,nick:e.nick,cat:e.cat,cat_label:e.catLabel,sub:e.sub,product:e.product,brand:e.brand,model:e.model,status:e.status,location:e.loc,note:e.note,sort_order:1})));
const mkFetch=(rec)=>async(u,o)=>{
  if(rec) rec(u,o);
  const body = (o&&(o.method==='POST'||o.method==='PATCH')) ? '' : rowsJSON();
  return {ok:true,status:200,text:async()=>body,json:async()=>JSON.parse(body||'[]')};
};

(async function main(){

console.log('=== 1. 마크업·CSS 존재 ===');
t('#eq-modal 존재', html.includes('id="eq-modal"'));
t('제품명 입력 필드', html.includes('id="eqf-product"'));
t('카테고리 select', html.includes('id="eqf-cat"'));
t('자산번호 readonly', /id="eqf-id" readonly/.test(html));
t('저장 버튼 → submitEqForm', html.includes('onclick="submitEqForm()"'));
t('.eq-form 그리드 CSS', html.includes('.eq-form{display:grid'));
t('목록 행에 수정 버튼(openEqForm)', html.includes("openEqForm('${eq.id}')"));

console.log('=== 2. nextAssetId 자동 채번 ===');
const etc=A.EQ().filter(e=>e.cat==='ETC').map(e=>+((e.id.match(/(\d+)$/)||[])[1]||0));
const expect='ETC-'+String(Math.max(0,...etc)+1).padStart(3,'0');
t('ETC 다음 번호 = 최대+1(3자리)', A.nextAssetId('ETC')===expect, A.nextAssetId('ETC'));
t('빈 카테고리는 001', /^ZZZ-001$/.test('ZZZ-'+String(1).padStart(3,'0')) && A.nextAssetId('ZZZ')==='ZZZ-001');

console.log('=== 3. openEqForm 추가 모드 ===');
login();
A.openEqForm();
t('모달 열림', H.store['eq-modal'].classList.contains('on'));
t('추가 모드(eqFormId=null)', A.getEqFormId()===null);
t('카테고리 기본 ACC', H.store['eqf-cat'].value==='ACC');
t('자산번호 미리보기 채움', H.store['eqf-id'].value===A.nextAssetId('ACC'), H.store['eqf-id'].value);
t('제품명 비어 있음', H.store['eqf-product'].value==='');
// 카테고리 바꾸면 미리보기 갱신
H.store['eqf-cat'].value='ETC';
A.eqFormCatChanged();
t('카테고리 변경 → 자산번호 갱신', H.store['eqf-id'].value===A.nextAssetId('ETC'), H.store['eqf-id'].value);

console.log('=== 4. submitEqForm 추가 → POST ===');
let sent=null;
H.ctx.fetch=mkFetch((u,o)=>{ if(o&&o.method==='POST'&&u.includes('/rest/v1/gear_equipment')) sent={u,body:JSON.parse(o.body)}; });
H.store['eqf-cat'].value='ACC';
H.store['eqf-product'].value='매트박스';
H.store['eqf-sub'].value='필터';
H.store['eqf-brand'].value='SmallRig';
H.store['eqf-model'].value='3196';
H.store['eqf-nick'].value='';
H.store['eqf-loc'].value='선반 B-1';
H.store['eqf-note'].value='4x5.65';
await A.submitEqForm();
t('POST 발생', !!sent && sent.u.includes('/gear_equipment'));
t('body에 제품명', sent.body.product==='매트박스');
t('body에 세부분류·브랜드·모델', sent.body.sub==='필터'&&sent.body.brand==='SmallRig'&&sent.body.model==='3196');
t('body에 보관위치·비고', sent.body.location==='선반 B-1'&&sent.body.note==='4x5.65');
t('body에 cat_label', typeof sent.body.cat_label==='string'&&sent.body.cat_label.length>0);
t('body에 active:true', sent.body.active===true);
t('자산번호 ACC-계열', /^ACC-\d{3}$/.test(sent.body.id), sent.body.id);
t('저장 후 모달 닫힘', !H.store['eq-modal'].classList.contains('on'));

console.log('=== 5. 제품명 필수 ===');
sent=null;
A.openEqForm();
H.store['eqf-product'].value='   ';
await A.submitEqForm();
t('제품명 비면 POST 안 함', sent===null);
t('에러 메시지 표시', H.store['eqf-err'].textContent.includes('제품명'));
A.closeEqForm();

console.log('=== 6. openEqForm 수정 모드 → PATCH ===');
const target=A.EQ().find(e=>e.cat==='CAM');
A.openEqForm(target.id);
t('수정 모드(eqFormId=id)', A.getEqFormId()===target.id);
t('제품명 채워짐', H.store['eqf-product'].value===target.product, H.store['eqf-product'].value);
t('자산번호=기존 id', H.store['eqf-id'].value===target.id);
t('카테고리 잠금(disabled)', H.store['eqf-cat'].disabled===true);
let patched=null;
H.ctx.fetch=mkFetch((u,o)=>{ if(o&&o.method==='PATCH'&&u.includes('/rest/v1/gear_equipment')) patched={u,body:JSON.parse(o.body)}; });
H.store['eqf-product'].value='새 제품명';
H.store['eqf-brand'].value='새 브랜드';
await A.submitEqForm();
t('PATCH 발생', !!patched && patched.u.includes('id=eq.'+target.id));
t('바뀐 제품명 전송', patched.body.product==='새 제품명');
t('바뀐 브랜드 전송', patched.body.brand==='새 브랜드');
t('PATCH에는 자산번호·카테고리 없음', patched.body.id===undefined&&patched.body.cat===undefined);

console.log('=== 7. 비로그인·오프라인 가드 ===');
let called=false;
H.ctx.fetch=async()=>{called=true;return {ok:true,status:200,json:async()=>[],text:async()=>'[]'};};
logout();
H.store['eq-modal'].classList.remove('on');
A.openEqForm();
t('비로그인은 폼 안 열림', !H.store['eq-modal'].classList.contains('on'));
login(); A.setEqSrc('local');
H.alerts.length=0;
A.openEqForm();
t('오프라인(local)은 폼 안 열림', !H.store['eq-modal'].classList.contains('on'));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
})();
