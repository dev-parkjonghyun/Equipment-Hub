const {APP,SUPA}=require('./paths.js');
const fs=require('fs');
const html=fs.readFileSync(APP,'utf-8');
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i||''))};

console.log('=== 1. 스페이스 + 드래그 = 화면 이동 ===');
t('spaceDown 상태 변수', html.includes('let spaceDown = false'));
t('Space keydown 감지', /e\.code === 'Space' && !spaceDown/.test(html));
t('Space keyup 해제', /keyup[\s\S]{0,120}e\.code === 'Space'[\s\S]{0,60}spaceDown = false/.test(html));
t('창 포커스 잃으면 해제', html.includes("window.addEventListener('blur', () => { spaceDown = false; keysDown.clear(); })"));
t('캔버스: 스페이스면 팬', /if \(spaceDown\) \{ e\.preventDefault\(\); startCanvasPan\(e\); return; \}/.test(html));
t('입력 중엔 무시', html.includes('function isTyping'));
t('커서 space 클래스', html.includes('#canvas.space{cursor:grab}'));

console.log('=== 2. 빈 곳 드래그 = 다중 선택 ===');
t('빈 곳 → 러버밴드', /canvas\.classList\.add\('marquee'\);\s*rubberCtx = \{/.test(html));
t('Shift는 누적 선택', html.includes('additive: e.shiftKey'));
t('제자리 클릭 = 선택 해제', /if \(!additive && selectedIds\.size\)/.test(html));

console.log('=== 3. 블록 → 블록 결합 ===');
t('드래그 중 대상 탐지', html.includes('document.elementFromPoint'));
t('자기 자신 pointer-events 해제', /me\.style\.pointerEvents = 'none'/.test(html));
t('순환 참조 차단', /!isAncestor\(dragCtx\.id, tbid, scene\)/.test(html));
t('적합/경고 하이라이트', /tgt\.classList\.add\(r\.ok \? 'drop-ok' : 'drop-warn'\)/.test(html));
t('놓으면 결합 실행', /if \(ctx\.moved && ctx\.hover[\s\S]{0,90}attachBlock\(ctx\.id, ctx\.hover\.bid, ctx\.hover\.res\)/.test(html));
t('결합 후 하이라이트 정리', /endDrag[\s\S]{0,400}remove\('drop-ok', 'drop-warn'\)/.test(html));

console.log('=== 4. Delete / Backspace 삭제 ===');
t('두 키 모두 처리', /e\.key === 'Delete' \|\| e\.key === 'Backspace'/.test(html));
t('배치도=블록 / 평면도=아이템 삭제', html.includes("md === 'layout' && selectedIds.size") && html.includes("md === 'floor' && fMulti.size"));
t('deleteSelectedBlocks 함수', html.includes('function deleteSelectedBlocks'));
t('하위 부품 포함 확인', html.includes('하위 부품을 포함해 총'));

console.log('=== 5. 레일 = 장비 카테고리 ===');
t('레일 동적 생성', html.includes('function renderRail'));
t('전체 버튼', html.includes("data-c=\"ALL\""));
t('주요/더보기 그룹 순회', html.includes('RAIL_MAIN.forEach') && html.includes('RAIL_MORE.forEach'));
t('개수 배지', html.includes('class="rc"'));
t('openCat 함수', html.includes('function openCat'));
t('팔레트 카테고리 필터', html.includes("if (activeCat !== 'ALL' && eq.cat !== activeCat) continue;"));
t('단일 카테고리면 헤더 숨김', html.includes("activeCat !== 'ALL' ? 'display:none' : ''"));
t('패널 제목 갱신', html.includes('equip-title'));
t('도구 3개 (씬·세트·조립)', (html.match(/rail-btn tool/g)||[]).length===3, (html.match(/rail-btn tool/g)||[]).length);
t('레일 스크롤(전체 영역)', /#rail\{[^}]*overflow-y:auto/.test(html));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
