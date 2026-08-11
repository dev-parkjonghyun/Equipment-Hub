const {APP,SUPA}=require('./paths.js');
const fs=require('fs');
const html=fs.readFileSync(APP,'utf-8');
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i||''))};

console.log('=== 1. 패널 접기가 캔버스에 영향 없도록 ===');
t('grid-column 명시 (rail=1)', /#rail\{[^}]*grid-column:1/.test(html));
t('grid-column 명시 (panel=2)', /#panel\{[^}]*grid-column:2/.test(html));
t('grid-column 명시 (main=3)', /#main\{[^}]*grid-column:3/.test(html));
t('main에 min-width:0', /#main\{[^}]*min-width:0/.test(html));
t('접힘 시 display:none 대신 width:0', html.includes('#app.pal-hidden #panel{width:0'));
t('접힘 시 테두리 제거', html.includes('border-right:none;visibility:hidden'));
t('display:none 사용 안 함', !html.includes('#app.pal-hidden #panel{display:none}'));

console.log('=== 2. 빈 캔버스 드래그 = 화면 이동 ===');
t('startCanvasPan 함수', html.includes('function startCanvasPan'));
t('endCanvasPan 함수', html.includes('function endCanvasPan'));
t('스페이스 없으면 범위 선택', /canvas\.classList\.add\('marquee'\)/.test(html));
t('스페이스면 팬', /if \(spaceDown\) \{ e\.preventDefault\(\); startCanvasPan\(e\); return; \}/.test(html));
t('팬 중 moved 추적', /function doPan[\s\S]{0,300}panCtx\.moved = true/.test(html));
t('제자리 클릭은 선택 해제', html.includes('제자리 클릭 = 선택 해제'));
t('스페이스 시 커서 grab', html.includes('#canvas.space{cursor:grab}'));
t('드래그 중 grabbing', html.includes('#canvas.panning{cursor:grabbing}'));
t('범위선택 중 crosshair', html.includes('#canvas.marquee{cursor:crosshair}'));

console.log('=== 3. 평면도도 동일 ===');
t('startFloorPan 함수', html.includes('function startFloorPan'));
t('평면도 스페이스 → 팬', /if \(spaceDown\) startFloorPan\(e\);/.test(html));
t('평면도 스페이스 커서', html.includes('#floor-svg.space{cursor:grab}'));
t('평면도 제자리 클릭 = 선택 해제', /endFloorPan[\s\S]{0,220}floorSel = null/.test(html));

console.log('=== 4. 블록 드래그는 그대로 ===');
t('블록 pointerdown → startDrag', html.includes("startDrag(e, 'block', bid)"));
t('블록에서 시작하면 캔버스 팬 안 함 (target 체크)', html.includes('if (e.target !== canvas) return;'));

console.log('=== 5. 휠클릭 팬 유지 ===');
t('가운데 버튼 팬 유지', html.includes('if (e.button !== 1) return;'));

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
