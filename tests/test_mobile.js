// 모바일 최적화: 뷰포트 메타, 서랍 네비, isMobile, 핀치 헬퍼, 훅 연결.
const {APP}=require('./paths.js');
const {makeHarness}=require('./harness.js');
const H=makeHarness(`isMobile,toggleNav,closeNav,pinchInfo,switchMode,
 cur:currentScene`,{runTimers:true});
const A=H.api;
const html=require('fs').readFileSync(APP,'utf-8');
let pass=0,fail=0;
const t=(n,c,i)=>{c?(pass++,console.log('  ✅',n)):(fail++,console.log('  ❌',n,i===undefined?'':i))};
const near=(a,b,e=0.001)=>Math.abs(a-b)<=e;

console.log('=== 1. 뷰포트 메타 ===');
t('viewport 메타 존재', /<meta name="viewport"/.test(html));
t('device-width', /width=device-width/.test(html));
t('앱처럼 고정(user-scalable=no)', /user-scalable=no/.test(html));
t('viewport-fit=cover(노치 대응)', /viewport-fit=cover/.test(html));
t('100dvh 사용(주소창 대응)', html.includes('100dvh'));

console.log('=== 2. 반응형 CSS ===');
t('모바일 브레이크포인트 @media 720px', html.includes('@media (max-width:720px)'));
t('레일/패널 오프캔버스(fixed)', html.includes('#rail, #panel{position:fixed'));
t('서랍 슬라이드 인(nav-open)', html.includes('#app.nav-open #rail'));
t('스크림 표시', html.includes('#app.nav-open #nav-scrim'));
t('햄버거 버튼 마크업', html.includes('id="nav-ham"') && html.includes('toggleNav()'));
t('스크림 마크업', html.includes('id="nav-scrim"') && html.includes('closeNav()'));
t('모드도크 전체폭 3등분', html.includes('#mode-dock .md{flex:1'));
t('3D 캔버스 touch-action:none', html.includes('#three-canvas{display:block;width:100%;height:100%;touch-action:none}'));
t('평면도 svg touch-action:none', /#floor-svg\{[^}]*touch-action:none/.test(html));

console.log('=== 3. isMobile() ===');
H.ctx.__mobile=false;
t('데스크톱이면 false', A.isMobile()===false);
H.ctx.__mobile=true;
t('모바일이면 true', A.isMobile()===true);

console.log('=== 4. 서랍 토글 ===');
const app=H.store['app'];
app.classList.remove('nav-open');
A.toggleNav();
t('toggleNav로 열림', app.classList.contains('nav-open'));
A.toggleNav();
t('toggleNav로 닫힘', !app.classList.contains('nav-open'));
app.classList.add('nav-open');
A.closeNav();
t('closeNav로 닫힘', !app.classList.contains('nav-open'));

console.log('=== 5. 모드 전환 시 서랍 닫힘(모바일) ===');
H.ctx.__mobile=true;
app.classList.add('nav-open');
A.switchMode('list');
t('모바일: 모드 고르면 서랍 닫힘', !app.classList.contains('nav-open'));
H.ctx.__mobile=false;
app.classList.add('nav-open');
A.switchMode('list');
t('데스크톱: 서랍 상태 안 건드림', app.classList.contains('nav-open'));

console.log('=== 6. 핀치 헬퍼 ===');
const pi=A.pinchInfo([{x:0,y:0},{x:6,y:8}]);
t('거리=10', near(pi.dist,10), pi.dist);
t('중점=(3,4)', near(pi.mx,3)&&near(pi.my,4), `${pi.mx},${pi.my}`);
const pj=A.pinchInfo([{x:10,y:10},{x:10,y:10}]);
t('겹치면 거리 0', pj.dist===0);

console.log('=== 7. 핀치 클램프(코드 확인) ===');
t('3D 핀치 줌이 orbit.dist를 clamp(1.2~60)', html.includes('o.dist = Math.max(1.2, Math.min(60, o.dist * pinch.dist / pi.dist))'));
t('평면도 핀치가 zoom clamp(12~160)', html.includes('Math.max(12, Math.min(160, Math.round(floorPinch.zoom0 * pi.dist / floorPinch.dist0)))'));
t('평면도 핀치 진행 중 드래그/마퀴/팬 차단', html.includes('if (!fDrag || floorPinching)') && html.includes('if (!fMq || floorPinching)') && html.includes('if (!fPan || floorPinching)'));
t('평면도 핀치 초기화 연결', html.includes('attachFloorPinch(wrap)'));

console.log('=== 8. openCat/openPane 모바일 가드 ===');
t('openCat 모바일 가드', html.includes('if (!init && !isMobile())') );
t('두 곳(openCat·openPane) 모두 가드', (html.match(/if \(!init && !isMobile\(\)\)/g)||[]).length>=2);

console.log('\n결과: '+pass+' 통과 / '+fail+' 실패');
process.exit(fail?1:0);
