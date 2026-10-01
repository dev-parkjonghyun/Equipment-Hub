// 목록 UI 개선: 카테고리 칩(한 분류씩)·세트(킷)·브랜드 필터·카드 뷰·상태 뱃지.
const {APP}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`switchMode,renderList,renderListChips,listRows,setListView,toggleKit,
 syncListTools,setEq,eqKids,eqOwned,
 EQ:()=>EQUIPMENT,ls:()=>listState,sel:()=>listSel,st:()=>state,kit:()=>kitOpen`,{runTimers:true});
const A=H.api;
const html=require('fs').readFileSync(APP,'utf-8');
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const EQ=A.EQ(), L=A.ls();
const body=()=>H.store['list-body'].innerHTML;
const chips=()=>H.store['list-chips'].innerHTML;
const nRows=()=>(body().match(/class="lrow/g)||[]).length;

A.switchMode('list');
L.cat='ALL'; L.q=''; L.status=''; L.brand=''; L.view='list'; L.group=false; L.only='';
A.renderList();

console.log('=== 1. 카테고리 칩 바 ===');
t('칩 바에 [전체]', chips().includes('전체') && chips().includes(`>${EQ.length}<`));
t('칩에 각 카테고리', chips().includes('카메라') && chips().includes('렌즈') && chips().includes('액세서리'));
t('전체 칩 활성(on)', /cat-chip on[^>]*>전체/.test(chips()) || chips().includes('cat-chip on'));
t('소속 데이터 없으면 [세트] 칩 숨김', !chips().includes('세트'));
t('칩 클릭이 listState.cat 설정', chips().includes("listState.cat='CAM'"));

console.log('=== 2. 한 분류씩 (확장성 핵심) ===');
const nCam=EQ.filter(e=>e.cat==='CAM').length;
L.cat='CAM'; A.renderList();
t('카메라 칩 → 카메라만', nRows()===nCam, nRows()+'/'+nCam);
t('해당 칩 활성', /cat-chip on[^>]*>카메라/.test(chips())||chips().includes('>카메라'));
L.cat='ALL'; A.renderList();
t('전체로 복귀', nRows()===EQ.length, nRows());

console.log('=== 3. 브랜드 필터 ===');
A.syncListTools();
const brands=[...new Set(EQ.map(e=>e.brand).filter(Boolean))];
t('브랜드 드롭다운 채워짐', brands.length>0 && H.store['lbrand'].innerHTML.includes(brands[0]));
const b0=brands[0];
L.brand=b0; A.renderList();
const onlyB0=A.listRows().every(e=>(e.brand||'')===b0);
t('선택 브랜드만 통과', onlyB0 && A.listRows().length>0, A.listRows().length);
t('다른 브랜드는 걸러짐', A.listRows().length<EQ.length);
L.brand=''; A.renderList();

console.log('=== 4. 소속(킷) 묶기 ===');
const parent=EQ.find(e=>e.cat==='CAM');
const child=EQ.find(e=>e.cat==='ACC');
child.owner=parent.id;                       // 이 부속을 카메라에 소속시킴
A.renderList();
t('킷 생기면 [세트] 칩 표시', chips().includes('세트'));
t('소속 자식은 eqOwned=true', A.eqOwned(child)===true);
t('부모의 자식 목록에 포함', A.eqKids(parent.id).some(e=>e.id===child.id));
// 전체 뷰: 자식은 기본 접힘(부모 아래), 부모에 🔗 뱃지
L.cat='ALL'; A.renderList();
t('부모 행에 🔗 킷 뱃지', body().includes('kit-badge') && body().includes(`toggleKit('${parent.id}')`));
t('접힌 상태: 자식 행 안 보임', !new RegExp(`data-id="${child.id}"`).test(body()));
t('자식이 상위 목록에서 빠짐', nRows()===EQ.length-1, nRows()+'/'+(EQ.length-1));
// 펼치면 자식이 .lsub 로 나옴
A.toggleKit(parent.id);
t('펼치면 자식 등장', new RegExp(`data-id="${child.id}"`).test(body()));
t('자식은 들여쓰기(lsub)+소속 태그', body().includes('lrow lsub') && body().includes('own-tag') && body().includes('소속'));
A.toggleKit(parent.id);                       // 접기
// 세트 뷰: 부모+자식 항상 펼침
L.cat='SET'; A.renderList();
t('세트 뷰: 부모 보임', new RegExp(`data-id="${parent.id}"`).test(body()));
t('세트 뷰: 자식 자동 펼침', new RegExp(`data-id="${child.id}"`).test(body()));
t('세트 뷰는 킷 있는 부모만', A.listRows().every(e=>A.eqKids(e.id).length>0));
delete child.owner;                           // 정리
L.cat='ALL'; A.renderList();

console.log('=== 5. 카드(갤러리) 뷰 ===');
A.setListView('card');
t('카드 컨테이너 렌더', body().includes('id="list-cards"') && body().includes('lcard'));
t('카드 뷰엔 표 행 없음', nRows()===0);
t('카드 수 = 상위 항목 수', (body().match(/class="lcard/g)||[]).length===EQ.length);
t('뷰 토글 상태 유지', L.view==='card');
A.setListView('list');
t('목록으로 복귀', body().includes('ltable') && nRows()===EQ.length);

console.log('=== 6. 상태 뱃지(점) ===');
t('상태 뱃지 점 CSS(.lstat::before)', html.includes('.lstat::before'));
t('상태 뱃지 마크업', body().includes('class="lstat ok"') || body().includes('lstat '));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
