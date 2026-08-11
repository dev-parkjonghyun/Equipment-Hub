const {APP,SUPA}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`switchMode,renderList,listRows,groupRows,rowHTML,setEq,cycleStatus,
 toggleSel,toggleAll,selToSet,selToLayout,exportListCSV,suggestNick,suggestAllNicks,
 clearAutoNicks,isAutoNick,autoNickCount,applyEqEdits,updateListSummary,syncListTools,
 hardName,dispName,exportChangesCSV,sameProductCount,
 renderPalette,cur:currentScene,EQ:()=>EQUIPMENT,ls:()=>listState,sel:()=>listSel,st:()=>state`,
 {runTimers:true});
const A=H.api;
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const html=require('fs').readFileSync(APP,'utf-8');
const EQ=A.EQ(), L=A.ls(), SEL=A.sel();
const body=()=>H.store['list-body'].innerHTML;
const nRows=()=>(body().match(/class="lrow/g)||[]).length;

console.log('=== 1. 목록이 첫 화면 ===');
t('모드 도크 첫 자리', html.indexOf('id="mode-list"')<html.indexOf('id="mode-layout"'));
t('기본 시작 모드', html.includes("switchMode(currentScene().mode || 'list')"));
t('저장된 편집값 먼저 적용', html.indexOf('applyEqEdits();')<html.indexOf("switchMode(currentScene().mode || 'list')"));
A.switchMode('list');
t('목록 화면만 표시', H.store['list-wrap'].style.display==='block'
  && H.store['canvas-wrap'].style.display==='none' && H.store['three-wrap'].style.display==='none');
t('목록 툴바만 표시', H.store['list-tools'].style.display==='inline-flex'
  && H.store['layout-tools'].style.display==='none');
t('전체 111개 표시', nRows()===111, nRows());

console.log('=== 2. 요약 카드 ===');
const sum=()=>H.store['list-summary'].innerHTML;
t('전체 장비 수', sum().includes('>111<'));
t('수리 필요 2건', /수리 필요<\/span><span class="v">2</.test(sum()));
t('별칭 붙은 것 카운트', /별칭 붙은 것<\/span><span class="v">\d+</.test(sum()));
t('이름 어려움만 별도 표시', /이름 어려움<\/span><span class="v">7</.test(sum()), (sum().match(/이름 어려움<\/span><span class="v">(\d+)</)||[])[1]);
t('보관위치 없음 111건', /보관위치 없음<\/span><span class="v">111</.test(sum()));
t('빈 곳은 경고색', sum().includes('lsum gap'));

console.log('=== 3. 검색 · 필터 · 정렬 ===');
L.q='sony'; A.renderList();
t('제품명 검색', nRows()>0 && nRows()<111, nRows());
L.q='CAM-001'; A.renderList();
t('자산번호 검색', nRows()===1, nRows());
L.q='24-70'; A.renderList();
t('모델명 부분 검색', nRows()>=1, nRows());
L.q=''; L.status='수리필요'; A.renderList();
t('상태 필터', nRows()===2, nRows());
L.status=''; L.cat='CAM'; A.renderList();
t('카테고리 필터', nRows()===5, nRows());
L.cat='ALL'; L.q='없는장비이름123'; A.renderList();
t('결과 없으면 안내', body().includes('조건에 맞는 장비가 없어요'));
L.q='';
L.sort='id'; A.renderList();
const ids=[...body().matchAll(/class="lid">([^<]+)/g)].map(m=>m[1]);
t('자산번호순 정렬', ids.join()===[...ids].sort().join());
L.sort='cat'; A.renderList();
const cats=[...body().matchAll(/class="lid">([A-Z]+)/g)].map(m=>m[1]);
t('카테고리순 = 팔레트 순서', cats[0]==='CAM', cats.slice(0,4).join(','));
L.sort='status'; A.renderList();
t('상태순: 폐기·수리 먼저', body().indexOf('수리필요')<2000, body().indexOf('수리필요'));
L.sort='id'; A.renderList();

console.log('=== 4. 표에서 바로 고치기 ===');
const cam=EQ.find(e=>e.id==='CAM-001');
A.setEq('CAM-001','nick','FX3 (메인)');
t('별칭 입력', cam.nick==='FX3 (메인)');
t('저장됨', A.st().eqEdits['CAM-001'].nick==='FX3 (메인)');
A.setEq('CAM-001','loc','카메라 케이스 1');
t('보관위치 입력', cam.loc==='카메라 케이스 1');
A.setEq('CAM-001','note','24-70 상시 물림');
t('비고 입력', cam.note==='24-70 상시 물림');
A.renderList();
t('요약 즉시 반영', /별칭 붙은 것<\/span><span class="v">6</.test(sum()), (sum().match(/별칭 붙은 것<\/span><span class="v">(\d+)</)||[])[1]);
t('보관위치 카운트 반영', /보관위치 없음<\/span><span class="v">110</.test(sum()));
// 상태 순환
const st0=cam.status;
A.cycleStatus('CAM-001'); t('상태 클릭 → 수리필요', cam.status==='수리필요', cam.status);
A.cycleStatus('CAM-001'); t('한 번 더 → 폐기', cam.status==='폐기');
A.cycleStatus('CAM-001'); t('다시 → 정상', cam.status==='정상');
// 새로고침해도 유지
A.applyEqEdits();
t('새로고침 후에도 유지', EQ.find(e=>e.id==='CAM-001').nick==='FX3 (메인)');
t('별칭이 팔레트에도 반영', H.store['palette-list'].innerHTML.includes('FX3 (메인)'));

console.log('=== 5. 별칭 초안 자동 생성 ===');
t('브랜드 제거', A.suggestNick({product:'Sony Fx3'})==='Fx3');
t('한글 변환', A.suggestNick({product:'NANLITE Forza 500'})==='포르자 500');
t('고독스 제거', A.suggestNick({product:'고독스 AD300Pro'})==='AD300Pro');
t('괄호·대괄호 제거', A.suggestNick({product:'하이브리드광 HDMI 2.0 [10m]'})==='하이브리드광 HDMI 2.0',
  A.suggestNick({product:'하이브리드광 HDMI 2.0 [10m]'}));
t('구분 표기(GM2)가 잘리지 않음', A.suggestNick({product:'Sony 70-200 F2.8 GM2'})==='70-200 F2.8 GM2',
  A.suggestNick({product:'Sony 70-200 F2.8 GM2'}));
t('한글 제품은 그대로', A.suggestNick({product:'전기릴선'})==='전기릴선');
t('제품명 없으면 세부분류', A.suggestNick({product:'',sub:'샌드백'})==='샌드백');
// 일괄 채우기
H.ctx.confirm=()=>true;
const before=EQ.filter(A.hardName).length;
A.suggestAllNicks();
t('어려운 이름에만 별칭', EQ.filter(e=>!e.nick).length>90, EQ.filter(e=>!e.nick).length+'개는 그대로');
t('직접 입력한 건 안 건드림', EQ.find(e=>e.id==='CAM-001').nick==='FX3 (메인)');
t('자동 표시', A.autoNickCount()>0 && A.autoNickCount()<10, A.autoNickCount());
t('직접 입력분은 자동 아님', !A.isAutoNick('CAM-001'));
// 같은 이름 중복 시 번호
t('쉬운 이름은 안 건드림', EQ.filter(e=>(e.product||'')==='A 스탠드').every(e=>!e.nick));
A.renderList();
t('확인 필요 카드 표시', sum().includes('별칭 확인 필요'));
t('확인 필요 스타일', body().includes('ledit auto'));
// 손대면 확인됨
const anyAuto=EQ.find(e=>A.isAutoNick(e.id));
A.setEq(anyAuto.id,'nick','내가 부르는 이름');
t('고치면 확인됨 처리', !A.isAutoNick(anyAuto.id));
// 되돌리기
const autoN=A.autoNickCount();
A.clearAutoNicks();
t('초안만 되돌림', A.autoNickCount()===0);
t('직접 입력은 살아있음', EQ.find(e=>e.id==='CAM-001').nick==='FX3 (메인)');
t('고친 것도 살아있음', EQ.find(e=>e.id===anyAuto.id).nick==='내가 부르는 이름');

console.log('=== 6. 묶어보기 (수량) ===');
L.group=true; A.renderList();
const g=A.groupRows(A.listRows());
t('같은 제품 묶임', g.some(x=>x.items.length===4), g.filter(x=>x.items.length>1).length+'종 중복');
t('A 스탠드 4개 묶임', g.find(x=>x.key==='A 스탠드').items.length===4);
t('수량 뱃지 표시', body().includes('class="lqty">×4'));
L.group=false; A.renderList();
t('풀면 개별 표시', nRows()===111);

console.log('=== 7. 선택 → 세트 ===');
SEL.clear();
A.toggleSel('CAM-003',true); A.toggleSel('LEN-001',true); A.toggleSel('LIT-009',true);
t('3개 선택', SEL.size===3);
t('선택 도구 표시', H.store['lsel-tools'].style.display==='inline-flex');
t('선택 개수 표시', H.store['lsel-n'].textContent==='3개 선택');
t('선택 행 강조', body().includes('lrow sel'));
H.ctx.prompt=()=>'인터뷰 기본';
A.selToSet();
const sets=A.st().sets;
const made=Object.values(sets).find(x=>x.name==='인터뷰 기본');
t('세트 생성', !!made);
t('선택한 3개가 담김', made.eqIds.length===3 && made.eqIds.includes('CAM-003'), made.eqIds.join(','));
t('저장 후 선택 해제', SEL.size===0);
t('기존 세트 유지', Object.keys(sets).length>=2, Object.keys(sets).length);
// 전체 선택
L.cat='CAM'; A.renderList();
A.toggleAll(true);
t('보이는 것만 전체선택', SEL.size===5, SEL.size);
A.toggleAll(false); t('전체 해제', SEL.size===0);
L.cat='ALL'; A.renderList();

console.log('=== 8. 내보내기 ===');
let dl=null;
H.ctx.URL={createObjectURL:b=>{dl=b;return 'blob:x'}};
A.exportListCSV();
t('CSV 다운로드 실행', dl!==null);
t('엑셀 한글깨짐 방지(BOM)', (()=>{
   let n=0,i=-1;
   while((i=html.indexOf("const csv = '",i+1))>=0){
     if(html.charCodeAt(i+13)===0xFEFF || html.slice(i+13,i+19)==='\\ufeff') n++;
   }
   return n===2;})(), '내보내기 2종');
t('별칭·보관위치 포함', html.includes("['자산번호', '카테고리', '세부분류', '제품명', '별칭', '브랜드', '모델명', '상태', '보관위치', '비고']"));
t('필터 결과만 내보냄', html.includes('const rows = listRows();'));

console.log('=== 9. 다른 화면과 연결 ===');
t('배치도로 보내기 버튼', html.includes('selToLayout()'));
t('세트로 저장 버튼', html.includes('selToSet()'));
A.switchMode('layout');
t('배치도 전환 정상', H.store['canvas-wrap'].style.display==='block');
A.switchMode('list');
t('목록 복귀 정상', nRows()===111, nRows());

console.log('=== 10. 이름 표기 정책 ===');
t('별칭 없으면 정리한 제품명', A.dispName({id:'X',product:'Sony Fx3'})==='Fx3');
t('별칭 있으면 별칭 우선', A.dispName({id:'X',nick:'메인캠',product:'Sony Fx3'})==='메인캠');
t('둘 다 없으면 자산번호', A.dispName({id:'X-1',product:'',sub:''})==='X-1');
t('배치도 블록도 같은 규칙', html.includes('const label = b.label || dispName(eq);'));
t('평면도 라벨도 같은 규칙', html.includes('const label = it.label || dispName(eq);'));
t('팔레트도 같은 규칙', html.includes('const label = dispName(eq);'));
t('3D 선택 정보도 같은 규칙', html.includes('${eq.id} ${dispName(eq)}'));
t('렌즈는 어렵지 않음', !A.hardName({id:'L',product:'Sony 24-70 F2.8 GM'}));
t('카메라도 어렵지 않음', !A.hardName({id:'C',product:'Sony a7m4'}));
t('한글 이름은 어렵지 않음', !A.hardName({id:'S',product:'A 스탠드'}));
t('부품번호는 어려움', A.hardName({id:'T',product:'manfrotto MVK504XTWINFA'}));
t('별칭 있으면 판정 제외', !A.hardName({id:'T',nick:'큰삼각대',product:'manfrotto MVK504XTWINFA'}));
t('목록에 표시 이름 노출', body().includes('class="lfull"'));
t('별칭 붙은 건 태그 표시', html.includes('class="lnk-tag"'));
t('어려운 이름엔 물음표', html.includes('class="lhard"'));
t('열 제목이 정책 설명', html.includes('화면에 뜨는 이름 / 정식 제품명')&&html.includes('별칭 (어려울 때만)'));

console.log('=== 11. 엑셀 반영 ===');
t('고친 것만 내보내기 존재', html.includes('function exportChangesCSV'));
t('앱이 아는 열만', html.includes("const head = ['자산번호', '별칭', '상태', '보관위치', '비고'];"));
t('구매일·가격은 건드리지 않음', !/exportChangesCSV[\s\S]{0,700}구매/.test(html));
{ let dl2=null; H.ctx.URL={createObjectURL:b=>{dl2=b;return 'blob:y'}};
  A.exportChangesCSV();
  t('변경분 다운로드', dl2!==null); }
t('변경 없으면 안내', html.includes("alert('아직 고친 내용이 없습니다.')"));
t('같은 제품 여러 대 카드', sum().includes('같은 제품 여러 대'));
{ A.ls().only='dup'; A.renderList();
  t('중복 제품만 걸러보기', nRows()>0 && nRows()<111, nRows());
  A.ls().only=''; A.ls().group=false; A.renderList(); }

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
