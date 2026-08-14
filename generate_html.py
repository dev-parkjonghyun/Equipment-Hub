"""장비 배치도 웹앱 HTML 생성"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ROOT, 'equipment_data.json'), encoding='utf-8') as f:
    equipment = json.load(f)

DATA_JSON = json.dumps(equipment, ensure_ascii=False)

# 3D 워터마크 (샘플) — 자산 소유 표시용. 실제 로고로 바꾸려면 아래 SVG 를 교체하거나,
# 빌드된 HTML 의 #three-wm 태그 src 를 원하는 이미지 URL/데이터URI 로 바꾸면 됩니다.
import base64
_WM_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="112" viewBox="0 0 400 112">'
    '<rect x="8" y="8" width="384" height="96" rx="16" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.55"/>'
    '<text x="200" y="60" font-family="-apple-system,Segoe UI,Helvetica,sans-serif" font-size="44" '
    'font-weight="800" letter-spacing="6" text-anchor="middle" fill="#ffffff">EH STUDIO</text>'
    '<text x="200" y="88" font-family="-apple-system,Segoe UI,sans-serif" font-size="14" '
    'letter-spacing="9" text-anchor="middle" fill="#ffffff" opacity="0.85">SAMPLE WATERMARK</text></svg>')
WM_DATA = 'data:image/svg+xml;base64,' + base64.b64encode(_WM_SVG.encode('utf-8')).decode('ascii')

# Three.js (r149 UMD) 인라인 — 오프라인에서도 3D 동작
# Three.js 는 저장소에 두거나(vendor/) npm 으로 받습니다.
THREE_PATH = next((p for p in [
    os.path.join(ROOT, 'vendor', 'three.min.js'),
    os.path.join(ROOT, 'node_modules', 'three', 'build', 'three.min.js'),
    '/tmp/node_modules/three/build/three.min.js',
] if os.path.exists(p)), os.path.join(ROOT, 'vendor', 'three.min.js'))
THREE_SRC = open(THREE_PATH, encoding='utf-8').read() if os.path.exists(THREE_PATH) else ''
print(f"Three.js 인라인: {len(THREE_SRC)/1024:.0f} KB")

HTML = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>EH 장비 배치도</title>
<style>
:root{
  --bg-0:#0b0e13; --bg-1:#12161d; --bg-2:#171c24; --bg-3:#1e242e; --bg-4:#252c38;
  --line:#2b3340; --line-2:#36404f;
  --tx-0:#eef2f7; --tx-1:#b9c4d1; --tx-2:#8b97a6; --tx-3:#5f6b7a;
  --acc:#5b9dff; --acc-dim:#2f5a94; --acc-soft:rgba(91,157,255,.14);
  --warn:#ffb454; --danger:#ff6b6b; --ok:#5fd39a;
  --r-s:5px; --r-m:8px; --r-l:11px;
  --sh-1:0 1px 2px rgba(0,0,0,.4);
  --sh-2:0 4px 14px rgba(0,0,0,.45);
  --sh-3:0 12px 34px rgba(0,0,0,.55);
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{
  font-family:-apple-system,BlinkMacSystemFont,"Pretendard","Apple SD Gothic Neo",
    "Segoe UI","Noto Sans KR",sans-serif;
  background:var(--bg-0); color:var(--tx-0);
  height:100vh; overflow:hidden; user-select:none;
  -webkit-font-smoothing:antialiased; font-size:13px; letter-spacing:-0.01em;
}
#app{display:grid;grid-template-columns:288px 1fr;height:100vh}

/* 스크롤바 */
::-webkit-scrollbar{width:9px;height:9px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:#333c4a;border-radius:5px;border:2px solid transparent;background-clip:padding-box}
::-webkit-scrollbar-thumb:hover{background:#44506180;background-clip:padding-box}

/* ───── 버튼 ───── */
button{
  background:linear-gradient(180deg,var(--bg-4),var(--bg-3));
  border:1px solid var(--line-2); color:var(--tx-1);
  padding:6px 11px; border-radius:var(--r-s); font-size:12px; font-weight:500;
  font-family:inherit; cursor:pointer; letter-spacing:-0.01em;
  transition:background .13s,border-color .13s,color .13s,transform .06s;
  box-shadow:var(--sh-1); white-space:nowrap;
}
button:hover{background:linear-gradient(180deg,#2e3644,#262d38);border-color:#455163;color:var(--tx-0)}
button:active{transform:translateY(1px)}
button.primary{
  background:linear-gradient(180deg,#2f6fc4,#245aa3); border-color:#3b7fd4; color:#fff;
  box-shadow:0 1px 2px rgba(0,0,0,.4),0 0 0 1px rgba(91,157,255,.15) inset;
}
button.primary:hover{background:linear-gradient(180deg,#3a7cd4,#2a66b4)}
button.danger{background:linear-gradient(180deg,#7d3440,#682a34);border-color:#8f3f4c;color:#ffdfe2}
button.danger:hover{background:linear-gradient(180deg,#8d3c49,#75303b)}
select,input[type=text],input[type=number],input[type=search]{
  background:var(--bg-1); border:1px solid var(--line-2); color:var(--tx-0);
  padding:6px 9px; border-radius:var(--r-s); font-size:12px; font-family:inherit; outline:none;
  transition:border-color .13s,box-shadow .13s;
}
select:focus,input:focus{border-color:var(--acc);box-shadow:0 0 0 3px var(--acc-soft)}

/* ───── 좌측 팔레트 ───── */


#palette-header h1{font-size:14px;font-weight:650;letter-spacing:-0.02em;color:var(--tx-0)}
#search{width:100%;background:var(--bg-0);border:1px solid var(--line)}
#search::placeholder{color:var(--tx-3)}

#palette-tabs{display:flex;gap:2px;padding:0 10px 10px}
.ptab{
  flex:1;padding:7px 0;text-align:center;font-size:12px;font-weight:550;
  color:var(--tx-2);background:var(--bg-2);border:1px solid transparent;
  border-radius:var(--r-s);box-shadow:none;
}
.ptab:hover{color:var(--tx-1);background:var(--bg-3)}
.ptab.active{color:#fff;background:var(--acc-dim);border-color:#3d6fae}

#palette-list,#sets-list{overflow-y:auto;flex:1;padding:2px 8px 14px}
#sets-list{display:none}

.cat-group{--cat-color:#6b7684;margin-bottom:3px}
.cat-header{
  display:flex;align-items:center;justify-content:space-between;
  padding:7px 9px;border-radius:var(--r-s);cursor:pointer;
  font-size:11.5px;font-weight:600;color:var(--tx-2);letter-spacing:.01em;
  transition:background .12s,color .12s;
}
.cat-header:hover{background:var(--bg-2);color:var(--tx-1)}
.cat-group.open .cat-header{color:var(--tx-1)}
.cat-header .count{
  font-size:10.5px;color:var(--tx-3);background:var(--bg-2);
  padding:1px 7px;border-radius:9px;font-variant-numeric:tabular-nums;
}
.cat-items{padding:2px 0 8px 4px;display:none}
.cat-group.open .cat-items{display:block}

.eq-card{
  padding:7px 10px;margin:3px 0;background:var(--bg-2);border-radius:var(--r-m);
  cursor:grab;font-size:12px;border:1px solid transparent;
  border-left:3px solid var(--cat-color,#6b7684);
  display:flex;flex-direction:row;align-items:center;gap:10px;
  transition:background .12s,border-color .12s,transform .08s;
}
.eq-card:hover{background:var(--bg-3);border-color:var(--line-2);border-left-color:var(--cat-color)}
.eq-card:active{cursor:grabbing;transform:scale(.985)}
.eq-card.placed{opacity:.34}
.eq-card .txt{display:flex;flex-direction:column;gap:1px;min-width:0}
.eq-card .id{font-weight:650;font-size:10.5px;color:var(--tx-2);letter-spacing:.02em;
  font-variant-numeric:tabular-nums}
.eq-card .name{font-size:12px;color:var(--tx-0);line-height:1.35;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.eq-card .nick{font-size:11px;color:var(--acc);font-weight:500}

.cicon{width:23px;height:23px;flex:0 0 auto;color:var(--cat-color,#8b97a6)}
.cicon.hd{width:15px;height:15px;margin-right:7px;flex:0 0 auto}
.cicon.sm{width:13px;height:13px;flex:0 0 auto}
.cicon.blk{width:25px;height:25px}
.chead{display:inline-flex;align-items:center;min-width:0}

/* 세트 */
.set-card{margin:8px 2px;background:var(--bg-2);border-radius:var(--r-m);
  border:1px solid var(--line);overflow:hidden;transition:border-color .13s}
.set-card:hover{border-color:var(--line-2)}
.set-head{padding:10px 11px;background:linear-gradient(180deg,#22303f,#1c2733);
  display:flex;align-items:center;justify-content:space-between;cursor:grab;gap:8px}
.set-head:active{cursor:grabbing}
.set-title{font-size:12.5px;font-weight:600;color:var(--tx-0)}
.set-count{font-size:10.5px;color:#8fc0ff;font-variant-numeric:tabular-nums}
.set-actions{display:flex;gap:4px;margin-top:5px}
.set-actions button{padding:2px 7px;font-size:10px;box-shadow:none}
.set-body{padding:8px 11px 10px;display:none}
.set-card.open .set-body{display:block}
.set-item{font-size:11px;color:var(--tx-1);display:flex;gap:6px;align-items:center;
  border-left:2px solid var(--cat-color,#6b7684);padding:3px 0 3px 8px;margin:2px 0}
.set-item b{color:var(--tx-2);font-weight:600;font-variant-numeric:tabular-nums}
.set-item .miss{color:var(--warn);font-size:10px}
.set-hint{padding:12px 11px;font-size:11.5px;color:var(--tx-2);line-height:1.65}
.set-hint b{color:var(--tx-1)}
.set-drag-hint{font-size:10px;color:#7fb0f0;margin-top:2px}

/* ───── 메인 ───── */
#main{display:flex;flex-direction:column;overflow:hidden;background:var(--bg-0)}
#toolbar{
  background:var(--bg-1);padding:9px 14px;border-bottom:1px solid var(--line);
  display:flex;align-items:center;gap:8px;flex-wrap:wrap;row-gap:8px;
}
#scene-select{min-width:172px}
.divider{width:1px;height:20px;background:var(--line-2);margin:0 3px;flex:0 0 auto}
.mode-switch{display:flex;background:var(--bg-0);border-radius:var(--r-m);padding:3px;
  border:1px solid var(--line)}
.mode-switch button{background:transparent;border:none;padding:6px 13px;font-size:12px;
  border-radius:6px;color:var(--tx-2);box-shadow:none;font-weight:550}
.mode-switch button:hover{color:var(--tx-1);background:var(--bg-2)}
.mode-switch button.active{background:linear-gradient(180deg,#2f6fc4,#245aa3);color:#fff;
  box-shadow:var(--sh-1)}
#floor-tools,#layout-tools,#three-tools{display:flex;align-items:center;gap:8px;flex-wrap:wrap;row-gap:8px}

/* 드롭다운 */
.dropdown{position:relative;display:inline-block}
.dropdown-menu{display:none;position:absolute;top:calc(100% + 6px);left:0;
  background:var(--bg-3);border:1px solid var(--line-2);border-radius:var(--r-m);
  min-width:206px;z-index:1000;padding:5px;box-shadow:var(--sh-3)}
.dropdown.open .dropdown-menu{display:block}
.dropdown-menu button{display:block;width:100%;text-align:left;border:none;background:transparent;
  padding:7px 10px;font-size:12px;border-radius:6px;box-shadow:none;color:var(--tx-1);font-weight:450}
.dropdown-menu button:hover{background:var(--acc-dim);color:#fff}
.dropdown-menu .sep{height:1px;background:var(--line-2);margin:5px 3px}
.dropdown-menu .mlabel{font-size:10px;color:var(--tx-3);padding:7px 10px 3px;
  text-transform:uppercase;letter-spacing:.06em;font-weight:600}

/* ───── 배치도 캔버스 ───── */
#canvas-wrap{flex:1;overflow:auto;background:var(--bg-0);position:relative;
  background-image:radial-gradient(circle at 1px 1px,#ffffff0f 1px,transparent 0);
  background-size:24px 24px}
#canvas{width:2000px;height:1500px;position:relative;cursor:default}
#canvas.space{cursor:grab}
#canvas.panning{cursor:grabbing}
#canvas.marquee{cursor:crosshair}
.block{
  position:absolute;padding:8px 12px;background:linear-gradient(180deg,var(--bg-4),var(--bg-3));
  border-radius:var(--r-m);border:1px solid var(--line-2);
  border-left:3px solid var(--cat-color,#6b7684);
  box-shadow:var(--sh-2);cursor:grab;min-width:104px;font-size:12px;z-index:10;
  transition:box-shadow .14s,border-color .14s;touch-action:none;
  display:flex;align-items:center;gap:10px;
}
.block:hover{box-shadow:0 6px 20px rgba(0,0,0,.6);border-color:#4a5768}
.block.selected{outline:2px solid var(--acc);outline-offset:2px;
  box-shadow:0 6px 22px rgba(91,157,255,.28)}
.block .btxt{display:flex;flex-direction:column;gap:2px;min-width:0}
.block .b-id{font-weight:650;font-size:10.5px;color:var(--tx-2);letter-spacing:.02em}
.block .b-name{font-size:11.5px;color:var(--tx-0)}
.block .b-remove{position:absolute;top:-7px;right:-7px;width:18px;height:18px;border-radius:50%;
  background:#d84a4a;color:#fff;font-size:11px;line-height:1;display:none;
  align-items:center;justify-content:center;cursor:pointer;border:none;padding:0;box-shadow:var(--sh-2)}
.block:hover .b-remove{display:flex}
.group{position:absolute;border:1.5px dashed var(--acc);background:rgba(91,157,255,.045);
  border-radius:var(--r-l);z-index:5}
.group-label{position:absolute;top:-13px;left:10px;background:var(--acc);color:#08121f;
  padding:2px 11px;border-radius:6px;font-size:11px;font-weight:650;cursor:text;
  box-shadow:var(--sh-1)}
.group-handle{position:absolute;inset:0;cursor:move;touch-action:none}
#rubber-band{position:absolute;display:none;border:1px solid var(--acc);
  background:rgba(91,157,255,.1);z-index:100;pointer-events:none;border-radius:2px}

/* ───── 상태바 ───── */
#status{background:var(--bg-1);padding:7px 14px;font-size:11px;color:var(--tx-2);
  border-top:1px solid var(--line);display:flex;justify-content:space-between;
  align-items:center;gap:14px;flex-wrap:wrap}
#status-info{font-weight:500;color:var(--tx-1)}
.hint{color:var(--tx-3);font-size:10.5px}
#floor-stats{color:#8fc0ff;font-size:11px;font-variant-numeric:tabular-nums}
.warn{color:var(--warn)}

/* ───── 빈 상태 ───── */
.empty-ov{position:absolute;inset:0;display:none;align-items:center;justify-content:center;
  pointer-events:none;z-index:50}
.empty-card{background:rgba(23,28,36,.96);border:1px solid var(--line-2);border-radius:var(--r-l);
  padding:24px 30px;text-align:center;font-size:13px;color:var(--tx-1);line-height:1.75;
  pointer-events:auto;box-shadow:var(--sh-3);backdrop-filter:blur(8px)}
.empty-card b{color:#fff;font-size:14.5px;font-weight:650}
.empty-card .sub{color:var(--tx-2);font-size:12px}

/* ───── 평면도 ───── */
#floor-wrap{flex:1;overflow:auto;background:#0d1116;position:relative;display:none}
#floor-svg{display:block;background:#0f141a;cursor:default}
#floor-svg.space{cursor:grab}
#floor-svg.panning{cursor:grabbing}
.fitem{cursor:grab}
.fitem:active{cursor:grabbing}
.fitem .fp{stroke-width:.03}
.fitem .clr{fill-opacity:.09;stroke-dasharray:.12 .1;stroke-width:.025}
.fitem.sel .fp{stroke:#fff;stroke-width:.07}
.fitem text{fill:var(--tx-0);font-family:inherit;pointer-events:none;font-weight:500}
.froom{fill:rgba(91,157,255,.045);stroke:var(--acc);stroke-width:.05;cursor:move}
.froom.sel{stroke:#fff;stroke-width:.09}
.froom-label{fill:#8fc0ff;font-size:.32px;font-weight:650;pointer-events:none;font-family:inherit}
.fdim{fill:#7b8b9d;font-size:.26px;pointer-events:none;font-family:inherit}
.grid-line{stroke:#ffffff0f;stroke-width:.012}
.grid-line.major{stroke:#ffffff26;stroke-width:.022}
.calib-line{stroke:#ff5252;stroke-width:.05;stroke-dasharray:.15 .1}
.pen-line{stroke:var(--acc);stroke-width:.05;fill:rgba(91,157,255,.06)}
.pen-rubber{stroke:var(--acc);stroke-opacity:.6;stroke-width:.04;stroke-dasharray:.15 .1}
.pen-pt{fill:var(--acc)}
.pen-pt.first{fill:#fff;stroke:var(--acc);stroke-width:.05}
.vhandle{fill:#fff;stroke:var(--acc);stroke-width:.035;cursor:grab}
.edge-len{fill:#9dc6f5;font-size:.24px;pointer-events:none;font-family:inherit;font-weight:500}
.fsubj{cursor:grab}

/* ───── 3D ───── */
#three-wrap{flex:1;position:relative;display:none;background:#0a0d12}
#three-canvas{display:block;width:100%;height:100%}
#three-hud{position:absolute;left:14px;bottom:14px;pointer-events:none;font-size:11.5px;
  color:var(--tx-1);max-width:60%}
#nav-hint{position:absolute;left:50%;transform:translateX(-50%);bottom:12px;z-index:55;
  background:rgba(13,17,23,.86);border:1px solid var(--line);border-radius:999px;
  padding:6px 15px;font-size:10.5px;color:var(--tx-2);letter-spacing:.01em;
  backdrop-filter:blur(9px);white-space:nowrap;pointer-events:none;box-shadow:var(--sh-2)}
#nav-hint b{color:var(--tx-0);font-weight:650;background:var(--bg-2);
  padding:1px 5px;border-radius:4px;margin-right:1px}
#three-canvas.walking{cursor:crosshair}
#walk-btn.on{background:rgba(91,157,255,.16);border-color:var(--acc);color:var(--acc)}
#three-sel{background:rgba(16,20,26,.82);padding:8px 12px;border-radius:var(--r-m);
  border:1px solid var(--line);backdrop-filter:blur(6px);line-height:1.5}
#three-warn{margin-top:7px;color:var(--warn);font-weight:600;
  background:rgba(52,34,10,.8);padding:6px 11px;border-radius:var(--r-s);
  border:1px solid #6b4a1c;display:inline-block}
#three-warn:empty{display:none}
/* 3D 워터마크(샘플) — 자산 소유 표시. 시선이 머무는 가운데에 은은하게. pointer-events 없음.
   위치·크기·진하기는 top/left/width/opacity 로 조절, 이미지는 #three-wm src 교체. */
#three-wm{position:absolute;left:50%;top:47%;transform:translate(-50%,-50%);
  width:min(34%,320px);opacity:.13;pointer-events:none;user-select:none;z-index:42;
  filter:drop-shadow(0 1px 3px rgba(0,0,0,.6))}
.tlab{font-size:11.5px;color:var(--tx-2);display:inline-flex;align-items:center;gap:6px}
.tlab input{width:64px}
#lens-sel{max-width:178px}

#cam-panel{position:absolute;top:14px;right:14px;width:250px;
  background:rgba(20,25,32,.93);border:1px solid var(--line-2);border-radius:var(--r-l);
  padding:13px 14px;z-index:60;box-shadow:var(--sh-3);display:none;backdrop-filter:blur(10px)}
.cp-head{font-size:12.5px;font-weight:650;color:#fff;margin-bottom:11px;padding-bottom:9px;
  border-bottom:1px solid var(--line-2);letter-spacing:-.01em}
.cp-row{display:flex;align-items:center;gap:9px;margin:9px 0;font-size:11px}
.cp-row label{width:36px;color:var(--tx-2);flex:0 0 auto;font-weight:500}
.cp-row input[type=range]{flex:1;min-width:0;accent-color:var(--acc);height:3px;cursor:pointer}
.cp-row span{width:54px;text-align:right;color:var(--tx-0);font-variant-numeric:tabular-nums;
  flex:0 0 auto;font-weight:550}
.cp-row select{flex:1;padding:4px 6px;font-size:11px}
.cp-btns{display:flex;gap:5px;margin-top:9px}
.cp-btns button{flex:1;font-size:10.5px;padding:6px 4px}
.cp-info{margin-top:11px;font-size:11px;color:var(--tx-2);line-height:1.75;
  border-top:1px solid var(--line-2);padding-top:10px}
.cp-info b{color:var(--warn);font-weight:600;font-variant-numeric:tabular-nums}

#pv-frame{position:absolute;border:2px solid var(--warn);border-radius:3px;pointer-events:none;
  z-index:55;display:none;box-shadow:0 6px 24px rgba(0,0,0,.7)}
#pv-guides{position:absolute;inset:0}
#pv-guides.on{background:
  linear-gradient(to right,transparent 33.2%,rgba(255,255,255,.28) 33.2%,rgba(255,255,255,.28) 33.5%,transparent 33.5%,
   transparent 66.4%,rgba(255,255,255,.28) 66.4%,rgba(255,255,255,.28) 66.7%,transparent 66.7%),
  linear-gradient(to bottom,transparent 33.2%,rgba(255,255,255,.28) 33.2%,rgba(255,255,255,.28) 33.5%,transparent 33.5%,
   transparent 66.4%,rgba(255,255,255,.28) 66.4%,rgba(255,255,255,.28) 66.7%,transparent 66.7%)}
#pv-label{position:absolute;top:-23px;left:0;font-size:10.5px;color:var(--warn);
  background:rgba(16,20,26,.85);padding:2px 9px;border-radius:5px;white-space:nowrap;
  border:1px solid #5c4520;font-weight:550}


/* ───── 조립체(리그) ───── */
.block{flex-direction:column;align-items:stretch;gap:0;padding:0;min-width:212px;overflow:visible}
.rig-head{display:flex;align-items:center;gap:10px;padding:9px 12px;position:relative}
.rig-cnt{font-size:10.5px;color:var(--acc);background:rgba(91,157,255,.15);
  padding:2px 8px;border-radius:9px;font-weight:600;flex:0 0 auto}
.rig-kids{border-top:1px dashed var(--line-2);padding:5px 7px 7px}
.rig-kid{display:flex;align-items:center;gap:7px;padding:4px 6px;margin:2px 0;border-radius:6px;
  font-size:11px;background:rgba(255,255,255,.028);border-left:2px solid var(--cat-color,#6b7684);
  cursor:grab;transition:background .12s}
.rig-kid:hover{background:rgba(255,255,255,.075)}
.rig-kid.warn{border-left-color:var(--warn);background:rgba(255,180,84,.09)}
.rig-kid .cicon{width:14px;height:14px}
.kid-slot{font-size:9.5px;color:var(--tx-3);width:48px;flex:0 0 auto}
.kid-id{font-size:10px;font-weight:650;color:var(--tx-2);flex:0 0 auto}
.kid-nm{color:var(--tx-1);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1;min-width:0}
.kid-x{opacity:0;color:var(--danger);cursor:pointer;font-size:13px;padding:0 3px;flex:0 0 auto}
.rig-kid:hover .kid-x{opacity:1}
.rig-toggle{font-size:10px;color:var(--tx-3);text-align:center;padding:4px;cursor:pointer;
  border-top:1px dashed var(--line-2)}
.rig-toggle:hover{color:var(--acc)}
.block.drop-ok{outline:2px dashed var(--ok);outline-offset:3px;
  background:linear-gradient(180deg,#26382f,#1e2c26)}
.block.drop-warn{outline:2px dashed var(--warn);outline-offset:3px}
.block.loose{border-style:dashed;opacity:.9}
.block.loose .rig-head::after{content:'단독';position:absolute;top:-8px;right:24px;font-size:9px;
  background:var(--bg-2);color:var(--tx-3);padding:1px 6px;border-radius:6px;border:1px solid var(--line-2)}
#rig-links{position:absolute;left:0;top:0;pointer-events:none;z-index:4}
.seg{display:flex;background:var(--bg-0);border:1px solid var(--line);border-radius:8px;padding:3px;gap:2px}
.seg button{background:transparent;border:none;padding:5px 11px;font-size:11.5px;border-radius:6px;
  color:var(--tx-2);box-shadow:none}
.seg button.on{background:linear-gradient(180deg,#2f6fc4,#245aa3);color:#fff}


/* 팔레트 토글 */
#app.pal-hidden{grid-template-columns:0 1fr}
#app.pal-hidden #palette{display:none}
#pal-open{position:fixed;left:0;top:50%;transform:translateY(-50%);z-index:300;
  border-radius:0 8px 8px 0;padding:16px 5px;font-size:11px;display:none;
  background:linear-gradient(180deg,var(--bg-3),var(--bg-2));border-left:none}
#app.pal-hidden #pal-open{display:block}
#palette-header h1{display:flex;align-items:center;justify-content:space-between}
#pal-close{padding:2px 7px;font-size:10px;box-shadow:none;background:transparent;
  border-color:var(--line-2);color:var(--tx-3)}
#pal-close:hover{color:var(--tx-0);background:var(--bg-3)}

/* 3D 아이템 위치 패널 */
#item-panel{position:absolute;left:14px;top:14px;width:216px;display:none;z-index:60;
  background:rgba(20,25,32,.93);border:1px solid var(--line-2);border-radius:var(--r-l);
  padding:12px 13px;box-shadow:var(--sh-3);backdrop-filter:blur(10px)}
.cp-lens{font-size:10px;color:var(--acc);background:var(--acc-soft);border-radius:6px;
  padding:4px 8px;margin-bottom:9px;line-height:1.45}
#item-panel{transition:transform .22s cubic-bezier(.4,0,.2,1),width .22s;overflow:hidden}
#item-panel.fold{width:38px;padding:8px 6px}
#item-panel.fold #ip-body{display:none}
#item-panel.fold #ip-name{display:none}
#item-panel.fold .ip-fold{transform:rotate(180deg);margin:0 auto}
.ip-head{display:flex;align-items:center;gap:7px;font-size:11.5px;font-weight:650;color:var(--tx-0);
  margin-bottom:11px;padding-bottom:9px;border-bottom:1px solid var(--line)}
.ip-head #ip-name{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ip-dot{width:6px;height:6px;border-radius:50%;background:var(--acc);flex:none;box-shadow:0 0 7px var(--acc)}
.ip-fold{background:transparent;border:none;box-shadow:none;color:var(--tx-3);padding:2px 5px;
  font-size:13px;line-height:1;border-radius:6px;transition:transform .22s}
.ip-fold:hover{background:var(--bg-2);color:var(--tx-0)}
.ip-ax{display:flex;align-items:center;gap:7px;margin-bottom:8px}
.ip-ax label{width:38px;flex:none;display:flex;align-items:center;gap:5px;
  font-size:10.5px;font-weight:600;color:var(--tx-2)}
.ip-ax label i{width:3px;height:11px;border-radius:2px;display:block}
.ip-ax[data-ax=x] label i{background:#ff5f70}
.ip-ax[data-ax=z] label i{background:#5b9dff}
.ip-ax[data-ax=y] label i{background:#5ad696}
.ip-ax[data-ax=r] label i{background:#8792a2}
.ip-ax input[type=number]{width:52px;flex:none;padding:4px 6px;font-size:10.5px;text-align:right}
.ip-ax input[type=range]{flex:1;min-width:0;-webkit-appearance:none;appearance:none;height:3px;
  border-radius:2px;background:var(--line-2);padding:0;box-shadow:none;border:none;cursor:grab}
.ip-ax input[type=range]:active{cursor:grabbing}
.ip-ax input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:12px;height:12px;
  border-radius:50%;background:#e8eef7;border:2px solid #0f141a;box-shadow:0 1px 4px rgba(0,0,0,.5)}
.ip-ax[data-ax=x] input[type=range]::-webkit-slider-thumb{background:#ff5f70}
.ip-ax[data-ax=z] input[type=range]::-webkit-slider-thumb{background:#5b9dff}
.ip-ax[data-ax=y] input[type=range]::-webkit-slider-thumb{background:#5ad696}
.ip-pose{display:flex;gap:5px;margin:4px 0 8px}
.ip-pose button{flex:1;padding:6px 4px;font-size:10.5px;background:var(--bg-2);
  border:1px solid var(--line);border-radius:7px;box-shadow:none;color:var(--tx-2)}
.ip-pose button:hover{border-color:var(--line-2);color:var(--tx-0)}
.ip-pose button.on{background:var(--acc-soft);border-color:var(--acc);color:var(--acc);font-weight:650}
.ip-hint{font-size:9.5px;color:var(--tx-3);margin:2px 0 8px;line-height:1.5}


/* ═══ 레일 + 패널 (오늘의집 스타일) ═══ */
#app{grid-template-columns:78px 262px 1fr}
#app.pal-hidden{grid-template-columns:78px 0px 1fr}
#rail{grid-column:1;grid-row:1}
#panel{grid-column:2;grid-row:1}
#main{grid-column:3;grid-row:1;min-width:0}
#app.pal-hidden #panel{width:0;border-right:none;visibility:hidden;padding:0}

#rail{background:var(--bg-1);border-right:1px solid var(--line);
  display:flex;flex-direction:column;padding:12px 0 92px;z-index:20;
  overflow-y:auto;overflow-x:hidden;overscroll-behavior:contain}
#rail::-webkit-scrollbar{width:5px}
#rail::-webkit-scrollbar-thumb{background:var(--line-2);border-radius:3px}
#rail::-webkit-scrollbar-thumb:hover{background:var(--tx-3)}
#rail::-webkit-scrollbar-track{background:transparent}
.rail-grp{display:flex;flex-direction:column;gap:3px;padding:0 8px}
.rail-grp.bottom{border-top:1px solid var(--line);padding-top:12px;margin-top:12px}
.rail-btn{background:transparent;border:none;box-shadow:none;padding:11px 2px 9px;
  border-radius:10px;display:flex;flex-direction:column;align-items:center;gap:6px;
  color:var(--tx-3);font-size:10.5px;font-weight:550;line-height:1.25;text-align:center;width:100%}
.rail-btn svg{width:23px;height:23px}
.rail-btn:hover{background:var(--bg-2);color:var(--tx-1)}
.rail-btn.on{background:rgba(91,157,255,.13);color:var(--acc)}
.rail-btn.on svg{color:var(--acc)}

#panel{background:var(--bg-1);border-right:1px solid var(--line);
  display:flex;flex-direction:column;overflow:hidden;position:relative}
.pane{display:none;flex-direction:column;overflow:hidden;flex:1}
.pane.on{display:flex}
.pane-head{padding:16px 16px 10px;display:flex;flex-direction:column;gap:9px;flex:0 0 auto}
.pane-head h1{font-size:15px;font-weight:650;letter-spacing:-.02em}
.pane-sub{font-size:11.5px;color:var(--tx-2);line-height:1.65}
.pane-body{overflow-y:auto;flex:1;padding:0 14px 18px}
#palette-list,#sets-list{overflow-y:auto;flex:1;padding:2px 10px 16px}

/* 접기 탭 */
#panel-tab{position:fixed;left:339px;top:50%;transform:translateY(-50%);z-index:120;
  width:26px;height:62px;border-radius:0 12px 12px 0;border:1.5px solid var(--acc);border-left:none;
  background:var(--bg-1);color:var(--acc);font-size:15px;padding:0;box-shadow:3px 0 10px rgba(0,0,0,.35);
  transition:left .18s,background .13s}
#panel-tab:hover{background:var(--bg-2)}
#app.pal-hidden #panel-tab{left:78px}

/* 하단 2D/3D 도크 */
#mode-dock{position:fixed;left:0;bottom:0;z-index:130;display:flex;
  background:var(--bg-1);border-top:1px solid var(--line);border-right:1px solid var(--line);
  border-radius:0 12px 0 0;overflow:hidden;box-shadow:0 -3px 14px rgba(0,0,0,.35)}
.md{background:transparent;border:none;box-shadow:none;border-radius:0;
  padding:16px 0;width:113px;font-size:13.5px;font-weight:700;color:var(--tx-2);
  letter-spacing:-.02em;position:relative}
#app.pal-hidden .md{width:78px;font-size:12px}
#mode-dock .md{width:104px}
.md:hover{background:var(--bg-2);color:var(--tx-1)}
.md.on{background:rgba(91,157,255,.16);color:var(--acc)}
.md.on::after{content:'';position:absolute;right:0;bottom:0;
  border-style:solid;border-width:0 0 9px 9px;border-color:transparent transparent var(--acc) transparent}

/* 패널 내부 목록 */
.plist-item{background:var(--bg-2);border:1px solid var(--line);border-radius:8px;
  padding:9px 11px;margin:6px 0;display:flex;align-items:center;gap:9px;cursor:pointer;
  font-size:12px;transition:all .12s}
.plist-item:hover{background:var(--bg-3);border-color:var(--line-2)}
.plist-item.on{border-color:var(--acc);background:rgba(91,157,255,.1)}
.plist-item .pi-tx{flex:1;min-width:0}
.plist-item .pi-t{color:var(--tx-0);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.plist-item .pi-s{font-size:10.5px;color:var(--tx-2);margin-top:2px}
.plist-item .pi-x{color:var(--danger);font-size:12px;opacity:0;flex:0 0 auto}
.plist-item:hover .pi-x{opacity:1}
.pane-sec{font-size:10px;color:var(--tx-3);font-weight:600;text-transform:uppercase;
  letter-spacing:.06em;margin:16px 0 6px}
.pane-row{display:flex;align-items:center;gap:7px;margin:7px 0;font-size:11.5px;color:var(--tx-2)}
.pane-row input[type=number]{flex:1;min-width:0}
.pane-btns{display:flex;gap:6px;margin-top:9px;flex-wrap:wrap}
.pane-btns button{flex:1;min-width:74px;font-size:11px}
.slot-help{font-size:11px;color:var(--tx-2);line-height:1.85}
.slot-help b{color:var(--tx-0)}
.slot-help .sh-row{display:flex;gap:8px;padding:5px 0;border-bottom:1px solid var(--line)}
.slot-help .sh-k{color:var(--acc);font-weight:600;flex:0 0 74px}


.rail-scroll{flex:0 0 auto;padding:8px 7px;display:flex;
  flex-direction:column;gap:2px}
.rail-btn{padding:8px 2px 7px;gap:5px;font-size:9.5px}
.rail-btn svg{width:20px;height:20px}
.rail-btn.tool{padding:9px 2px 8px}
.rail-btn .rc{font-size:8.5px;color:var(--tx-3);font-variant-numeric:tabular-nums}
.rail-btn.on .rc{color:#8fc0ff}
#rail{padding:0 0 92px}
.rail-grp.bottom{padding:9px 7px 0;gap:2px;margin-top:0}


.rail-btn.more{color:var(--tx-3);border-top:1px dashed var(--line);border-radius:0;
  margin-top:5px;padding-top:11px}
.rail-btn.more:hover{color:var(--acc);background:transparent}
.rail-btn.more.open{color:var(--tx-2)}
.rail-btn.more svg{width:16px;height:16px}


.rail-btn.mode{padding:10px 2px 9px}
.rail-btn.mode.on{background:rgba(91,157,255,.15);color:var(--acc)}
.rail-sep{height:1px;background:var(--line);margin:6px 6px 5px}
.rail-grp.top{flex:0 0 auto;padding:10px 7px 9px;border-bottom:1px solid var(--line);gap:2px;margin-bottom:4px}
.rail-btn.head{border-bottom:1px dashed var(--line);border-radius:0;padding-bottom:10px;margin-bottom:4px;
  position:relative}
.rail-btn.head .chev{position:absolute;right:6px;top:9px;font-size:9px;color:var(--tx-3)}
#scene-chip{background:var(--bg-2);border:1px solid var(--line-2);color:var(--tx-1);
  padding:5px 11px;font-size:11.5px;border-radius:var(--r-m);
  display:inline-flex;align-items:center;gap:7px;white-space:nowrap;
  max-width:230px;overflow:hidden;text-overflow:ellipsis}
#scene-chip .sc-k{font-size:9.5px;color:var(--tx-3);background:var(--bg-0);
  padding:1px 6px;border-radius:5px;letter-spacing:.03em}


/* ═══ 공유 · 모달 ═══ */
#vo-bar{position:fixed;left:0;right:0;top:0;z-index:200;height:38px;
  display:flex;align-items:center;gap:10px;padding:0 16px;
  background:linear-gradient(90deg,#1b2735,#141a22);border-bottom:1px solid var(--line-2);
  font-size:12px;color:var(--tx-1)}
#vo-bar .vo-ic{font-size:14px}
#vo-bar .vo-tx b{color:var(--tx-0)}
#vo-bar .vo-sub{margin-left:auto;font-size:10.5px;color:var(--tx-3);letter-spacing:.02em}
/* 공유 링크(보기 전용): 좌측 레일·패널·상단 툴바를 감추고 캔버스만 보여준다.
   그리드 좌측 두 열을 0 으로 접어 캔버스가 전체 폭을 쓴다.
   하단 모드 도크(배치도/평면도/3D)는 남겨 감독님이 시점을 바꿀 수 있게 한다. */
#app.view-only{padding-top:38px;height:100vh;grid-template-columns:0 0 1fr}
#app.view-only #rail,
#app.view-only #panel,
#app.view-only #panel-tab,
#app.view-only #toolbar{display:none}
#app.view-only .eq-card{cursor:default;opacity:.85}
#app.view-only #mode-dock button{opacity:1;pointer-events:auto}
/* 공유 3D: 카메라 패널은 읽기 전용. 초점·조리개·프리뷰만 남기고
   높이·팬·틸트·포커스거리·화면비 행과 편집 버튼(.vo-edit)은 숨긴다.
   남는 슬라이더는 pointer-events 로 조작을 막아 값만 보이게 한다. */
#app.view-only #cpr-h,
#app.view-only #cpr-pan,
#app.view-only #cpr-tilt,
#app.view-only #cpr-fd,
#app.view-only #cpr-ar,
#app.view-only #cam-panel .vo-edit{display:none}
#app.view-only #cam-panel input,
#app.view-only #cam-panel select{pointer-events:none}

.modal{position:fixed;inset:0;z-index:400;background:rgba(6,9,13,.72);
  display:none;align-items:center;justify-content:center;backdrop-filter:blur(4px)}
.modal.on{display:flex}
.mbox{background:var(--bg-1);border:1px solid var(--line-2);border-radius:var(--r-l);
  padding:22px 24px;width:min(520px,92vw);box-shadow:var(--sh-3)}
.mhead{font-size:15px;font-weight:700;color:var(--tx-0);margin-bottom:9px}
.msub{font-size:12px;color:var(--tx-2);line-height:1.7;margin-bottom:16px}
.msub b{color:var(--tx-1)}
.mlab{display:block;font-size:10.5px;color:var(--tx-2);font-weight:600;margin:11px 0 5px}
.mbox input{width:100%;padding:9px 11px;font-size:12px;background:var(--bg-0);
  border:1px solid var(--line-2);border-radius:var(--r-m);color:var(--tx-0)}
.mrow{display:flex;gap:8px}
.mrow input{flex:1;min-width:0;font-family:ui-monospace,Menlo,monospace;font-size:11px}
.mmeta{font-size:11px;color:var(--tx-3);margin-top:9px}
.mbtns{display:flex;gap:8px;justify-content:flex-end;margin-top:18px}
.share-row{display:flex;align-items:center;gap:8px;padding:7px 9px;background:var(--bg-2);
  border-radius:var(--r-m);margin-bottom:6px;font-size:11px}
.share-row .sr-n{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--tx-1)}
.share-row .sr-d{color:var(--tx-3);font-size:10px}
.share-row.dead{opacity:.45}
.share-row.dead .sr-n{text-decoration:line-through}

/* ═══ 로그인 ═══ */
#auth-chip{background:var(--bg-2);border:1px solid var(--line-2);color:var(--tx-1);
  padding:5px 11px;font-size:11.5px;border-radius:var(--r-m);
  display:inline-flex;align-items:center;gap:7px;white-space:nowrap;box-shadow:none}
#auth-chip:hover{border-color:var(--acc);color:var(--tx-0)}
.ac-dot{width:6px;height:6px;border-radius:50%;background:var(--tx-3);flex:none}
.ac-dot.on{background:var(--ok);box-shadow:0 0 7px var(--ok)}
.lg-err{font-size:11.5px;color:var(--danger);margin-top:10px;min-height:16px;line-height:1.5}

/* ═══ 사진 인식 ═══ */
.mbox.wide{width:min(760px,94vw)}
.ph-wrap{display:grid;grid-template-columns:230px 1fr;gap:16px;align-items:start}
#photo-preview{width:100%;border-radius:var(--r-m);border:1px solid var(--line-2);
  background:var(--bg-0);object-fit:contain;max-height:360px}
#photo-body{max-height:360px;overflow:auto;padding-right:4px}
.ph-wait{display:flex;align-items:center;gap:11px;color:var(--tx-2);font-size:12px;padding:26px 4px}
.ph-spin{width:16px;height:16px;border:2px solid var(--line-2);border-top-color:var(--acc);
  border-radius:50%;animation:phspin .8s linear infinite;flex:none}
@keyframes phspin{to{transform:rotate(360deg)}}
.ph-err{padding:20px 4px;font-size:12px;color:var(--tx-2);line-height:1.8}
.ph-err b{display:block;color:var(--danger);font-size:13px;margin-bottom:5px}
.ph-hint{color:var(--tx-3);font-size:11px;margin-top:7px}
.ph-note{font-size:11px;color:var(--tx-2);background:var(--bg-2);padding:8px 11px;
  border-radius:var(--r-m);margin-bottom:11px;line-height:1.6}
.ph-sec{font-size:10.5px;font-weight:650;color:var(--tx-2);margin:13px 0 7px;
  padding-bottom:5px;border-bottom:1px solid var(--line)}
.ph-sec b{color:var(--tx-0)}
.ph-row{display:flex;align-items:center;gap:9px;padding:6px 8px;border-radius:var(--r-m);
  font-size:11.5px;cursor:pointer}
.ph-row:hover{background:var(--bg-2)}
.ph-row.low{background:rgba(255,180,84,.07)}
.ph-row.miss{opacity:.6;cursor:default}
.ph-id{font-family:ui-monospace,Menlo,monospace;font-size:10.5px;color:var(--tx-2);
  flex:none;width:80px}
.ph-nm{color:var(--tx-0);flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ph-src{font-size:10px;color:var(--tx-3);flex:none;max-width:150px;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.ph-warn{font-size:9.5px;font-weight:700;color:var(--warn);background:rgba(255,180,84,.15);
  padding:2px 6px;border-radius:4px;flex:none}

/* ═══ 장비 목록 화면 ═══ */
#list-wrap{display:none;height:100%;overflow:auto;background:var(--bg-0)}
#list-summary{display:flex;gap:9px;flex-wrap:wrap;padding:16px 18px 12px;
  position:sticky;top:0;background:linear-gradient(var(--bg-0) 72%,transparent);z-index:6}
.lsum{background:var(--bg-1);border:1px solid var(--line);border-radius:var(--r-l);
  padding:9px 14px;display:flex;align-items:center;gap:9px;cursor:pointer;transition:.13s}
.lsum:hover{border-color:var(--line-2);background:var(--bg-2)}
.lsum.on{border-color:var(--acc);background:var(--acc-soft)}
.lsum .k{font-size:10.5px;color:var(--tx-2);font-weight:550}
.lsum .v{font-size:16px;font-weight:700;color:var(--tx-0);letter-spacing:-.02em}
.lsum.warn .v{color:var(--warn)}
.lsum.gap .v{color:var(--danger)}

#list-body{padding:0 18px 40px}
.ltable{width:100%;border-collapse:separate;border-spacing:0;font-size:12px}
.ltable th{position:sticky;top:62px;background:var(--bg-1);z-index:5;
  text-align:left;font-size:10.5px;font-weight:650;color:var(--tx-2);
  padding:9px 10px;border-bottom:1px solid var(--line-2);border-top:1px solid var(--line);
  white-space:nowrap;cursor:pointer;user-select:none}
.ltable th:first-child{border-radius:var(--r-m) 0 0 0;width:34px;cursor:default}
.ltable th:last-child{border-radius:0 var(--r-m) 0 0}
.ltable th:hover{color:var(--tx-0)}
.ltable th .ar{color:var(--acc);margin-left:3px}
.ltable td{padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:middle}
.lrow{transition:background .1s}
.lrow:hover{background:var(--bg-1)}
.lrow.sel{background:var(--acc-soft)}
.lrow.dim{opacity:.45}
.lcat-bar{width:3px;padding:0!important;border-radius:2px}
.lid{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px;
  color:var(--tx-1);white-space:nowrap;font-weight:600}
.lname{color:var(--tx-0);font-weight:550;line-height:1.35}
.lfull{color:var(--tx-3);font-size:10.5px;margin-top:1px;line-height:1.3;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:290px}
.lnk-tag{font-size:9px;font-weight:700;color:var(--acc);background:var(--acc-soft);
  padding:1px 5px;border-radius:4px;margin-left:5px;vertical-align:1px}
.lhard{display:inline-flex;align-items:center;justify-content:center;width:14px;height:14px;
  border-radius:50%;background:rgba(255,180,84,.16);color:var(--warn);font-size:9.5px;
  font-weight:700;margin-left:5px;cursor:help;vertical-align:1px}
.licon{width:26px;height:26px;border-radius:7px;display:flex;align-items:center;
  justify-content:center;flex:none}
.licon svg{width:16px;height:16px}
.lnamecell{display:flex;align-items:center;gap:9px}
.lqty{background:var(--bg-3);color:var(--tx-1);font-size:10px;font-weight:700;
  padding:2px 7px;border-radius:999px;margin-left:6px}
.ledit{background:transparent;border:1px solid transparent;border-radius:6px;
  padding:4px 7px;font-size:11.5px;color:var(--tx-0);width:100%;min-width:70px;
  box-shadow:none;transition:.12s;font-family:inherit}
.ledit:hover{border-color:var(--line)}
.ledit:focus{border-color:var(--acc);background:var(--bg-0);outline:none}
.ledit::placeholder{color:var(--tx-3);font-style:italic}
.ledit.auto{color:var(--warn);border-bottom:1px dashed rgba(255,180,84,.5);border-radius:6px 6px 0 0}
.ledit.auto:focus{color:var(--tx-0);border-bottom-style:solid}
.ledit.empty{background:repeating-linear-gradient(-45deg,transparent,transparent 5px,
  rgba(255,180,84,.055) 5px,rgba(255,180,84,.055) 10px)}
.lstat{font-size:10.5px;font-weight:650;padding:3px 9px;border-radius:999px;
  border:1px solid;white-space:nowrap;cursor:pointer;background:transparent}
.lstat.ok{color:var(--ok);border-color:rgba(95,211,154,.35)}
.lstat.fix{color:var(--warn);border-color:rgba(255,180,84,.4);background:rgba(255,180,84,.08)}
.lstat.dead{color:var(--tx-3);border-color:var(--line)}
.lchk{width:15px;height:15px;accent-color:var(--acc);cursor:pointer}
.lcat-tag{font-size:10px;color:var(--tx-2);white-space:nowrap}
.lsum.src .vs{font-size:11.5px;font-weight:600;color:var(--tx-1)}
.lsum.src.warn .vs{color:var(--warn)}
.lact{width:30px;text-align:center}
.lx{background:transparent;border:none;box-shadow:none;color:var(--tx-3);
  padding:2px 6px;font-size:14px;line-height:1;border-radius:5px}
.lx:hover{background:rgba(255,107,107,.15);color:var(--danger)}
.lempty{text-align:center;padding:60px 20px;color:var(--tx-2)}
.lempty b{display:block;color:var(--tx-0);font-size:15px;margin-bottom:7px}
.lsub{background:var(--bg-1)}
.lsub td{padding-left:44px;font-size:11.5px;color:var(--tx-1)}
.lgrp-toggle{background:transparent;border:none;box-shadow:none;color:var(--tx-2);
  padding:2px 5px;font-size:10px}
#lgrp.on{background:var(--acc-soft);border-color:var(--acc);color:var(--acc)}

/* 카테고리 색 */
.cat-CAM{--cat-color:#5b9dff}.cat-LEN{--cat-color:#7cc0ff}.cat-LIT{--cat-color:#f2c14e}
.cat-MOD{--cat-color:#e08a3c}.cat-STD{--cat-color:#98a3af}.cat-TRP{--cat-color:#7d8794}
.cat-GIM{--cat-color:#b58aff}.cat-AUD{--cat-color:#5fc98a}.cat-MON{--cat-color:#2ec8d8}
.cat-BAT{--cat-color:#ef7676}.cat-PWR{--cat-color:#ff9166}.cat-STO{--cat-color:#c78aff}
.cat-CAB{--cat-color:#49bdb0}.cat-ACC{--cat-color:#a89076}.cat-ETC{--cat-color:#8fa0b0}
</style>
</head>
<body>
<div id="app">
    <aside id="rail">
      <div class="rail-grp top">
        <button class="rail-btn mode" id="mode-list" onclick="switchMode('list')" title="장비 목록">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M8.4 6.2h11.2M8.4 12h11.2M8.4 17.8h11.2"/>
            <circle cx="4.4" cy="6.2" r="1.3" fill="currentColor" stroke="none"/>
            <circle cx="4.4" cy="12" r="1.3" fill="currentColor" stroke="none"/>
            <circle cx="4.4" cy="17.8" r="1.3" fill="currentColor" stroke="none"/></svg>
          <span>목록</span></button>
        <div class="rail-sep"></div>
        <button class="rail-btn tool" data-p="scenes" onclick="openPane('scenes')" title="씬 관리">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2.8l9.2 4.6L12 12 2.8 7.4z"/><path d="M2.8 12.2L12 16.8l9.2-4.6"/>
            <path d="M2.8 16.8L12 21.4l9.2-4.6"/></svg>
          <span>씬</span></button>
        <button class="rail-btn tool" data-p="sets" onclick="openPane('sets')" title="세트">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
            stroke-linecap="round" stroke-linejoin="round">
            <rect x="2.6" y="4.5" width="18.8" height="15" rx="2"/><path d="M2.6 9.4h18.8M9 9.4v10.1"/></svg>
          <span>세트</span></button>
        <button class="rail-btn tool" data-p="rig" onclick="openPane('rig')" title="조립">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
            stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="5" r="2.6"/><circle cx="5.4" cy="18.6" r="2.6"/><circle cx="18.6" cy="18.6" r="2.6"/>
            <path d="M12 7.6v4.2M10.2 13.4L7 16.6M13.8 13.4l3.2 3.2"/></svg>
          <span>조립</span></button>
      </div>
      <div class="rail-scroll" id="rail-cats"></div>
    </aside>

    <aside id="panel">
      <div id="pane-equip" class="pane on">
        <div class="pane-head"><h1 id="equip-title">전체 장비</h1>
          <input id="search" placeholder="자산번호 · 이름 · 별칭 검색"></div>
        <div id="palette-list"></div>
      </div>
      <div id="pane-sets" class="pane">
        <div class="pane-head"><h1>세트</h1>
          <p class="pane-sub">자주 쓰는 장비 묶음. 캔버스로 끌어다 놓으면 한 번에 배치됩니다.</p></div>
        <div id="sets-list"></div>
      </div>
      <div id="pane-rig" class="pane">
        <div class="pane-head"><h1>조립</h1>
          <p class="pane-sub">장비를 조립체 위로 끌면 맞는 슬롯에 결합됩니다.</p></div>
        <div class="pane-body" id="rig-body"></div>
      </div>
      <div id="pane-scenes" class="pane">
        <div class="pane-head"><h1>씬 관리</h1></div>
        <div class="pane-body" id="scene-body"></div>
      </div>
    </aside>
    <button id="panel-tab" onclick="togglePalette()" title="패널 접기/펴기">›</button>

    <div id="vo-bar" style="display:none">
      <span class="vo-ic">👁</span>
      <span class="vo-tx"><b id="vo-name"></b> · 보기 전용으로 공유된 배치입니다</span>
      <span class="vo-sub">EH Studio 장비 배치도</span>
    </div>

    <div id="photo-modal" class="modal">
      <div class="mbox wide">
        <div class="mhead">📷 사진에서 장비 불러오기</div>
        <div class="ph-wrap">
          <img id="photo-preview" alt="">
          <div id="photo-body"></div>
        </div>
        <div class="mbtns">
          <button onclick="closePhoto()">닫기</button>
          <button onclick="photoToLayout()">→ 배치도로</button>
          <button class="primary" onclick="photoToSet()">📦 세트로 저장</button></div>
      </div>
    </div>

    <div id="login-modal" class="modal">
      <div class="mbox">
        <div class="mhead">스튜디오 계정 로그인</div>
        <p class="msub">로그인하면 장비를 <b>수정·추가</b>할 수 있습니다.<br>
          로그인하지 않아도 목록을 보고 배치도를 만드는 건 가능합니다.</p>
        <label class="mlab">이메일</label>
        <input id="lg-email" type="email" autocomplete="username" placeholder="name@ehstudio.net"
               onkeydown="if(event.key==='Enter')document.getElementById('lg-pw').focus()">
        <label class="mlab">비밀번호</label>
        <input id="lg-pw" type="password" autocomplete="current-password"
               onkeydown="if(event.key==='Enter')doLogin()">
        <div class="lg-err" id="lg-err"></div>
        <div class="mbtns">
          <button onclick="closeLogin()">취소</button>
          <button class="primary" id="lg-btn" onclick="doLogin()">로그인</button></div>
      </div>
    </div>

    <div id="share-modal" class="modal">
      <div class="mbox">
        <div class="mhead">🔗 공유 링크가 만들어졌습니다</div>
        <p class="msub">받은 사람은 <b>보기만</b> 할 수 있고, 장비를 옮기거나 지울 수 없습니다.</p>
        <div class="mrow"><input id="share-link" readonly onclick="this.select()">
          <button class="primary" onclick="copyShareLink()">복사</button></div>
        <div class="mmeta" id="share-meta"></div>
        <div class="mbtns"><button onclick="closeShare()">닫기</button></div>
      </div>
    </div>


    <div id="mode-dock">
      <button id="mode-layout" class="md" onclick="switchMode('layout')">배치도</button>
      <button id="mode-floor" class="md" onclick="switchMode('floor')">평면도</button>
      <button id="mode-3d" class="md" onclick="switchMode('three')">3D</button>
    </div>

    <main id="main">
        <div id="toolbar">
            <select id="scene-select" style="display:none"></select>
            <span id="scene-chip"></span>
            <button id="auth-chip" style="display:none"></button>
            <div class="divider"></div>
            <span id="list-tools">
                <input id="lq" type="search" placeholder="이름 · 자산번호 · 별칭 검색"
                       oninput="listState.q=this.value;renderList()" style="width:190px">
                <select id="lst" onchange="listState.status=this.value;renderList()">
                    <option value="">상태 전체</option>
                    <option value="정상">정상만</option>
                    <option value="수리필요">수리필요</option>
                    <option value="폐기">폐기</option>
                </select>
                <select id="lsort" onchange="listState.sort=this.value;renderList()">
                    <option value="id">자산번호순</option>
                    <option value="cat">카테고리순</option>
                    <option value="name">이름순</option>
                    <option value="status">상태순</option>
                    <option value="nick">별칭 있는 것 먼저</option>
                </select>
                <button id="lgrp" onclick="listState.group=!listState.group;renderList()"
                        title="같은 제품을 묶어서 수량으로 표시">🧮 묶어보기</button>
                <div class="divider"></div>
                <span id="lsel-tools" style="display:none">
                    <span id="lsel-n" class="tlab"></span>
                    <button class="primary" onclick="selToSet()">📦 세트로 저장</button>
                    <button onclick="selToLayout()">→ 배치도로</button>
                    <button onclick="listSel.clear();renderList()">선택 해제</button>
                    <div class="divider"></div>
                </span>
                <button class="primary" onclick="addEquipment()" title="새 장비를 등록합니다 (로그인 필요)">＋ 장비 추가</button>
                <div class="divider"></div>
                <button onclick="pickGearPhoto()" title="화이트보드 사진을 읽어 장비를 찾아냅니다 (서버 설치 필요)">📷 사진에서 불러오기</button>
                <div class="divider"></div>
                <button onclick="suggestAllNicks()" title="모델번호처럼 부르기 어려운 이름에만 별칭 초안을 답니다">✨ 어려운 이름만 별칭 제안</button>
                <button onclick="clearAutoNicks()" title="자동으로 채운 별칭만 되돌립니다">↺ 초안 되돌리기</button>
                <div class="divider"></div>
                <button onclick="exportListCSV()" title="지금 보이는 목록 전체를 CSV로">📄 전체 내보내기</button>
                <button onclick="exportChangesCSV()" title="앱에서 고친 항목만 — 엑셀 마스터에 안전하게 반영">📋 고친 것만</button>
            </span>
            <span id="layout-tools">
            <span class="seg" id="rig-view">
                <button data-v="nest" class="on" onclick="setRigView('nest')">중첩</button>
                <button data-v="link" onclick="setRigView('link')">선 연결</button>
                <button data-v="fold" onclick="setRigView('fold')">접기</button>
            </span>
            <div class="divider"></div>
            <button class="primary" onclick="createGroup()">📦 그룹 만들기</button>
            <button onclick="ungroup()">그룹 해제</button>
            <button onclick="saveAsSet()">⭐ 세트로 저장</button>
            <div class="divider"></div>
            <div class="dropdown" id="align-dd">
                <button onclick="toggleAlignMenu(event)">⇹ 정렬 ▾</button>
                <div class="dropdown-menu">
                    <div class="mlabel">그룹 안 정렬</div>
                    <button onclick="sortWithinGroups()">🗂 그룹 안 카테고리 정렬</button>
                    <div class="sep"></div>
                    <div class="mlabel">전체 배치</div>
                    <button onclick="autoArrangeByCategory()">📄 카테고리별 열 정리</button>
                    <button onclick="snapAll()">⊞ 전체 격자 맞춤</button>
                    <div class="sep"></div>
                    <div class="mlabel">선택 항목 정렬 (2개+)</div>
                    <button onclick="alignBlocks('left')">⇤ 왼쪽 정렬</button>
                    <button onclick="alignBlocks('hcenter')">⇔ 가로 가운데</button>
                    <button onclick="alignBlocks('right')">⇥ 오른쪽 정렬</button>
                    <button onclick="alignBlocks('top')">⤒ 위쪽 정렬</button>
                    <button onclick="alignBlocks('vcenter')">⇕ 세로 가운데</button>
                    <button onclick="alignBlocks('bottom')">⤓ 아래쪽 정렬</button>
                    <div class="sep"></div>
                    <div class="mlabel">균등 분배 (3개+)</div>
                    <button onclick="distributeBlocks('h')">↔ 가로 균등</button>
                    <button onclick="distributeBlocks('v')">↕ 세로 균등</button>
                    <div class="sep"></div>
                    <button onclick="gridifySelection()">▦ 선택 항목 격자 배열</button>
                </div>
            </div>
            <button id="snap-btn" onclick="toggleSnap()">⊞ 스냅 OFF</button>
            <div class="divider"></div>
            <button onclick="clearScene()">🗑 초기화</button>
            </span>
            <span id="floor-tools" style="display:none">
                <button onclick="reflowFromLayout()" title="평면도·3D의 장비를 방 안에 다시 정렬합니다">⬇ 배치도 기준 재정렬</button>
                <div class="divider"></div>
                <label class="tlab">방 <input id="rm-w" type="number" step="0.1" min="1" max="40"
                    value="6" onchange="setRoomSize('w',this.value)"> ×
                    <input id="rm-h" type="number" step="0.1" min="1" max="30"
                    value="4.5" onchange="setRoomSize('h',this.value)"> m</label>
                <label class="tlab">천장고 <input id="ceil-in2" type="number" step="0.1" min="1.8"
                    max="12" value="2.7" onchange="setCeiling(this.value)"> m</label>
                <button id="cf-btn2" class="primary" onclick="toggleConfine()"
                    title="장비가 방 밖으로 나가지 못하게 합니다">🚧 방 안으로 제한</button>
                <button onclick="addSubject()">👤 피사체</button>
                <div class="divider"></div>
                <button class="primary" onclick="startPen()">✏️ 펜으로 그리기</button>
                <button onclick="startRoomDraw()">▭ 사각형 방</button>
                <button onclick="addRoomByNumbers()">⌨ 치수 입력</button>
                <div class="divider"></div>
                <button onclick="pickBgImage()">🖼 배경 도면</button>
                <button onclick="startCalibrate()">📏 축척 보정</button>
                <button onclick="cycleBgOpacity()">◐ 투명도</button>
                <label class="tlab">폭 <input id="bg-w" type="number" step="0.1" min="0.5" max="80"
                    onchange="setBgWidth(this.value)" disabled> m</label>
                <button onclick="nudgeBg(1.1)">＋</button>
                <button onclick="nudgeBg(0.9)">－</button>
                <button id="bgmove-btn" onclick="toggleBgMove()">✥ 도면 이동</button>
                <div class="divider"></div>
                <button onclick="zoomFloor(1.25)">🔍+</button>
                <button onclick="zoomFloor(0.8)">🔍−</button>
                <button id="clr-btn" onclick="toggleClearance()">◌ 여유공간 ON</button>
                <div class="divider"></div>
                <button class="danger" onclick="deleteFloorSelection()">🗑 선택 삭제</button>
                <button onclick="clearFloor()">전체 비우기</button>
            </span>
            <span id="three-tools" style="display:none">
                <button onclick="reflowFromLayout()" title="평면도·3D의 장비를 방 안에 다시 정렬합니다">⬇ 배치도 기준 재정렬</button>
                <button onclick="fitView3D()" title="단축키 Home">🎯 전체 보기</button>
                <button id="walk-btn" onclick="toggleWalk()" title="단축키 V">🚶 1인칭</button>
                <div class="divider"></div>
                <label class="tlab">방 <input id="rm-w2" type="number" step="0.1" min="1" max="40"
                    value="6" onchange="setRoomSize('w',this.value)"> ×
                    <input id="rm-h2" type="number" step="0.1" min="1" max="30"
                    value="4.5" onchange="setRoomSize('h',this.value)"> m</label>
                <label class="tlab">천장고 <input id="ceil-in" type="number" step="0.1" min="1.8" max="12"
                    value="2.7" onchange="setCeiling(this.value)"> m</label>
                <button id="cf-btn" class="primary" onclick="toggleConfine()"
                    title="장비가 방 밖으로 나가지 못하게 합니다">🚧 방 안으로 제한</button>
                <div class="divider"></div>
                <label class="tlab">높이 <input id="h-in" type="number" step="0.05" min="0" max="10"
                    value="0" onchange="setItemHeight(this.value)" disabled> m</label>
                <button onclick="nudgeHeight(0.1)">▲</button>
                <button onclick="nudgeHeight(-0.1)">▼</button>
                <div class="divider"></div>
                <button id="fr-btn" onclick="toggleFrustum()">🎥 화각 표시</button>
                <select id="lens-sel" onchange="pickLens(this.value)"></select>
                <div class="divider"></div>
                <button id="sh-btn" onclick="toggleShadows()">🌑 그림자 ON</button>
                <button onclick="setView('iso')">아이소</button>
                <button onclick="setView('top')">탑</button>
                <button onclick="setView('front')">정면</button>
                <button onclick="setView('cam')">📷 카메라 시점</button>
                <div class="divider"></div>
                <button class="primary" onclick="renderPNG()">🖼 렌더 이미지 저장</button>
            </span>
        </div>
        <div id="list-wrap">
            <div id="list-summary"></div>
            <div id="list-body"></div>
        </div>
        <div id="canvas-wrap">
            <div id="canvas"></div>
        </div>
        <div id="floor-wrap">
            <svg id="floor-svg"></svg>
            <div id="floor-empty" class="empty-ov"></div>
        </div>
        <div id="three-wrap">
            <canvas id="three-canvas"></canvas>
            <img id="three-wm" src="__WATERMARK__" alt="" draggable="false">
            <div id="pv-frame"><div id="pv-guides"></div><div id="pv-label"></div></div>
            <div id="cam-panel">
                <div class="cp-head">📷 <span id="cp-name">카메라 없음</span></div>
                <div id="cp-lens" class="cp-lens"></div>
                <div id="cp-body">
                    <div class="cp-row" id="cpr-h"><label>높이</label>
                        <input type="range" id="cp-h" min="0.2" max="2.5" step="0.01" oninput="setCam('h3',this.value)">
                        <span id="cp-h-v">1.45m</span></div>
                    <div class="cp-row" id="cpr-pan"><label>팬</label>
                        <input type="range" id="cp-pan" min="-180" max="180" step="1" oninput="setCam('pan',this.value)">
                        <span id="cp-pan-v">0°</span></div>
                    <div class="cp-row" id="cpr-tilt"><label>틸트</label>
                        <input type="range" id="cp-tilt" min="-60" max="60" step="0.5" oninput="setCam('tilt',this.value)">
                        <span id="cp-tilt-v">0°</span></div>
                    <div class="cp-row" id="cpr-foc"><label>초점</label>
                        <input type="range" id="cp-foc" min="8" max="200" step="1" oninput="setCam('focal',this.value)">
                        <span id="cp-foc-v">35mm</span></div>
                    <div class="cp-row" id="cpr-fs"><label>조리개</label>
                        <input type="range" id="cp-fs" min="0" max="10" step="1" oninput="setFstopIdx(this.value)">
                        <span id="cp-fs-v">F2.8</span></div>
                    <div class="cp-row" id="cpr-fd"><label>포커스</label>
                        <input type="range" id="cp-fd" min="0.3" max="15" step="0.05" oninput="setCam('focus',this.value)">
                        <span id="cp-fd-v">3.00m</span></div>
                    <div class="cp-row" id="cpr-ar"><label>화면비</label>
                        <select id="cp-ar" onchange="setAspect(this.value)">
                            <option value="1.7778">16:9</option>
                            <option value="2.39">2.39:1 시네마</option>
                            <option value="1.5">3:2</option>
                            <option value="1">1:1</option>
                            <option value="0.8">4:5</option>
                            <option value="0.5625">9:16 세로</option>
                        </select></div>
                    <div class="cp-btns vo-edit">
                        <button onclick="lookAtSubject()">🎯 피사체 조준</button>
                        <button onclick="focusOnSubject()">◎ 피사체 포커스</button>
                    </div>
                    <div class="cp-btns vo-edit">
                        <button onclick="addSubject()">👤 피사체 추가</button>
                        <button id="dof-btn" onclick="toggleDOF()">◍ 심도 표시</button>
                    </div>
                    <div class="cp-btns">
                        <button id="pv-btn" onclick="togglePreview()">🖥 프리뷰 ON</button>
                        <button class="vo-edit" onclick="cyclePreviewSize()">⤢ 크기</button>
                        <button class="vo-edit" onclick="toggleGuides()">⊞ 가이드</button>
                    </div>
                    <div class="cp-info" id="cp-info"></div>
                </div>
            </div>
            <div id="three-empty" class="empty-ov"></div>
            <div id="nav-hint"></div>
            <div id="three-hud">
                <div id="three-sel">항목을 클릭해 선택 · 드래그=회전 · 휠=줌 · 우클릭드래그=이동</div>
                <div id="three-warn"></div>
            </div>
            <div id="item-panel">
                <div class="ip-head">
                    <span class="ip-dot"></span><span id="ip-name">선택 없음</span>
                    <button class="ip-fold" onclick="toggleItemPanel()" title="접기/펼치기">‹</button>
                </div>
                <div id="ip-body">
                    <div class="ip-ax" data-ax="x"><label><i></i>X</label>
                        <input type="range" id="ip-x-s" min="0" max="40" step="0.05"
                               oninput="setItemPos('x',this.value,1)" onchange="setItemPos('x',this.value)">
                        <input type="number" id="ip-x" step="0.05" onchange="setItemPos('x',this.value)"></div>
                    <div class="ip-ax" data-ax="z"><label><i></i>Z</label>
                        <input type="range" id="ip-z-s" min="0" max="30" step="0.05"
                               oninput="setItemPos('y',this.value,1)" onchange="setItemPos('y',this.value)">
                        <input type="number" id="ip-z" step="0.05" onchange="setItemPos('y',this.value)"></div>
                    <div class="ip-ax" data-ax="y"><label><i></i>Y</label>
                        <input type="range" id="ip-y-s" min="0" max="3" step="0.01"
                               oninput="setItemPos('h3',this.value,1)" onchange="setItemPos('h3',this.value)">
                        <input type="number" id="ip-y" step="0.05" onchange="setItemPos('h3',this.value)"></div>
                    <div class="ip-ax" data-ax="r"><label><i></i>회전</label>
                        <input type="range" id="ip-r-s" min="-180" max="180" step="1"
                               oninput="setItemPos('rot',this.value,1)" onchange="setItemPos('rot',this.value)">
                        <input type="number" id="ip-r" step="5" onchange="setItemPos('rot',this.value)"></div>
                    <div class="ip-pose" id="ip-pose" style="display:none">
                        <button data-pose="stand" onclick="setSubject('pose','stand')">🧍 서기</button>
                        <button data-pose="sit" onclick="setSubject('pose','sit')">🪑 앉기</button>
                    </div>
                    <div class="ip-hint" id="ip-hrange"></div>
                    <div class="cp-info" id="ip-info"></div>
                </div>
            </div>
        </div>
        <div id="status">
            <span id="status-info">준비</span>
            <span id="floor-stats"></span>
            <span class="hint">Space+드래그=화면 이동 · 빈 곳 드래그=범위 선택 · 블록을 다른 블록 위로=결합 · Del=삭제</span>
        </div>
    </main>
</div>

<script>/*__THREEJS__*/</script>
<script>
// ===================== 데이터 =====================
const EQUIPMENT = __DATA__;

// ===================== 상태 =====================
const STORAGE_KEY = 'eh_layout_v1';
let selectedIds = new Set();  // 선택된 블록/그룹 id
let dragCtx = null;
let activeTab = 'equip';
const GRID_SIZE = 20;
let snapEnabled = false;

// 기본 제공 세트 (사용자가 편집/삭제 가능)
const DEFAULT_SETS = {
    'set_beforeafter': {
        name: '시술 전후 사진',
        eqIds: ['CAM-003', 'LEN-001', 'LIT-009',
                'STD-C-001', 'STD-C-002', 'STD-A-001',
                'MOD-007', 'STD-AS-001', 'STD-AS-002', 'ACC-006']
    }
};
// 세트 스키마 버전 (올리면 낡은 프리셋을 정리한다)
const SETS_VERSION = 4;
// 더 이상 기본으로 제공하지 않는 세트 (저장분에서도 지움)
const RETIRED_SETS = ['set_whiteboard'];

function loadState() {
    let s;
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) s = JSON.parse(raw);
    } catch (e) {}
    if (!s) {
        s = {
            currentScene: 'default',
            scenes: {
                'default': { name: '기본 씬', blocks: {}, groups: {} }
            }
        };
    }
    // 세트 초기화 + 마이그레이션
    if (!s.sets) s.sets = {};
    if (s.setsVersion !== SETS_VERSION) {
        // 버전이 바뀔 때만 청소: 옛 프리셋과 더 이상 제공하지 않는 기본 세트 제거
        for (const key of Object.keys(s.sets)) {
            if (key.startsWith('preset_')) delete s.sets[key];
        }
        RETIRED_SETS.forEach(k => { delete s.sets[k]; });
    }
    // 기본 세트는 버전과 상관없이 항상 보충한다
    // (예전엔 버전 게이트 안에 있어서 한 번 지나가면 새 세트가 영영 안 들어왔다)
    for (const [k, v] of Object.entries(DEFAULT_SETS)) {
        if (!s.sets[k]) s.sets[k] = JSON.parse(JSON.stringify(v));
    }
    s.setsVersion = SETS_VERSION;
    return s;
}

// DEFAULT_SETS 선언 이후에 state 초기화 (TDZ 방지)
let state = loadState();
function saveState() {
    // 보기 전용(공유 링크)으로 열렸을 땐 절대 저장하지 않는다.
    // 안 그러면 공유 씬이 내 작업 데이터(scenes)를 덮어써 편집 내용이 사라진다.
    if (typeof viewOnly !== 'undefined' && viewOnly) return;
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (err) {
        console.warn('저장 실패', err);
        alert('브라우저 저장 공간이 부족합니다.\n배경 도면을 제거하거나 불필요한 씬을 삭제한 뒤 다시 시도해주세요.');
    }
    // 로그인했으면 서버(스튜디오 공용 작업공간)에도 저장 — 다른 기기에서 이어서 작업
    if (typeof isLoggedIn === 'function' && isLoggedIn()) scheduleWorkspaceSync();
}
// 현재 모드에서 이미 배치된 장비 id 집합
function placedEqSet() {
    const scene = currentScene();
    if (scene.mode === 'floor')
        return new Set(Object.values(ensureFloor(scene).items).map(i => i.eqId));
    return new Set(Object.values(scene.blocks).map(b => b.eqId));
}
function currentScene() { return state.scenes[state.currentScene]; }

// ===================== 팔레트 렌더 =====================
const CAT_ORDER = ['CAM', 'LEN', 'LIT', 'MOD', 'AUD', 'MON', 'TRP', 'STD', 'GIM', 'BAT', 'PWR', 'STO', 'CAB', 'ACC', 'ETC'];
const CAT_NAMES = {
    CAM: '카메라', LEN: '렌즈', LIT: '조명', MOD: '조명 모디파이어',
    AUD: '오디오', MON: '모니터', TRP: '삼각대', STD: '스탠드',
    GIM: '짐벌', BAT: '배터리', PWR: '전원/충전', STO: '저장매체',
    CAB: '케이블', ACC: '액세서리', ETC: '기타'
};
const CAT_ICONS = {
    CAM: '📷', LEN: '🔍', LIT: '💡', MOD: '🪟', AUD: '🎙', MON: '🖥',
    TRP: '🔺', STD: '🗼', GIM: '🌀', BAT: '🔋', PWR: '🔌', STO: '💾',
    CAB: '🔗', ACC: '🧰', ETC: '📦'
};

// ───────── 카테고리 인포그래픽 아이콘 (24×24 기준) ─────────
const ICONS = {
    // 카메라 바디 + 렌즈
    CAM: '<rect x="2.5" y="7.5" width="19" height="12" rx="2"/>' +
         '<path d="M8.2 7.5l1.6-2.6h4.4l1.6 2.6"/><circle cx="12" cy="13.5" r="3.3"/>',
    // 렌즈 (측면 배럴 + 전면 유리)
    LEN: '<rect x="2.5" y="7" width="14" height="10" rx="1.6"/>' +
         '<ellipse cx="18.6" cy="12" rx="2.9" ry="5"/>' +
         '<path d="M6.6 7v10M10.7 7v10"/>',
    // 조명 헤드 + 빛 퍼짐
    LIT: '<path d="M6.5 3.5h11l2.2 7.5H4.3z"/><path d="M8.6 11l-2.6 9M15.4 11l2.6 9M12 11v9"/>',
    // 소프트박스 (팔각형)
    MOD: '<path d="M8.6 3.2h6.8l5.4 5.4v6.8l-5.4 5.4H8.6L3.2 15.4V8.6z"/>' +
         '<path d="M12 3.2v17.6M3.2 12h17.6"/>',
    // 라이트 스탠드 (스피곳 마운트 + 높이조절 노브 + 넓은 3다리)
    STD: '<path d="M12 2v3.4M9.6 5.4h4.8"/><path d="M12 5.4v10.2"/>' +
         '<circle cx="12" cy="10.4" r="1.3"/>' +
         '<path d="M12 15.6L4 21.2M12 15.6l8 5.6M12 15.6v5.6"/>',
    // 삼각대 (넓은 카메라 플레이트 + 좁은 3다리)
    TRP: '<rect x="7.6" y="2.6" width="8.8" height="2.4" rx="0.7"/>' +
         '<path d="M12 5v5.6"/>' +
         '<path d="M12 10.6L7.6 21M12 10.6l4.4 10.4M12 10.6v10.4"/>',
    // 짐벌 (케이지에 물린 카메라 + 그립)
    GIM: '<rect x="8.4" y="2.6" width="7.2" height="5" rx="1"/><circle cx="12" cy="5.1" r="1.4"/>' +
         '<path d="M4.6 3.8v6.4a3.6 3.6 0 0 0 3.6 3.6h7.6a3.6 3.6 0 0 0 3.6-3.6V3.8"/>' +
         '<path d="M12 13.8v3.1"/><rect x="9.5" y="16.9" width="5" height="5.1" rx="2.4"/>',
    // 마이크
    AUD: '<rect x="9" y="2.5" width="6" height="11" rx="3"/>' +
         '<path d="M5.5 11a6.5 6.5 0 0 0 13 0"/><path d="M12 17.5v3.5M8.5 21h7"/>',
    // 모니터
    MON: '<rect x="2.5" y="4" width="19" height="12.5" rx="1.8"/>' +
         '<path d="M12 16.5V20M8.5 20h7"/>',
    // 배터리
    BAT: '<rect x="2.5" y="7" width="16.5" height="10" rx="2"/><path d="M21.8 10.5v3"/>' +
         '<path d="M6.2 10.5v3M9.8 10.5v3M13.4 10.5v3"/>',
    // 플러그
    PWR: '<path d="M9 2.5v6M15 2.5v6"/>' +
         '<path d="M5.5 8.5h13v2.8a6.5 6.5 0 0 1-13 0z"/><path d="M12 17.8v3.7"/>',
    // SD 카드
    STO: '<path d="M6.8 2.5h8L19 6.8V20a1.5 1.5 0 0 1-1.5 1.5h-9.2A1.5 1.5 0 0 1 6.8 20z"/>' +
         '<path d="M9.8 5.2v3.6M12.3 5.2v3.6M14.8 6.6v2.2"/>',
    // 케이블 (양끝 커넥터 + S자 선)
    CAB: '<rect x="1.4" y="4.2" width="6" height="4.6" rx="1.2"/>' +
         '<path d="M3.3 4.2V2.6M5.5 4.2V2.6"/>' +
         '<path d="M7.4 6.5c4.4 0 4.4 11 9.2 11"/>' +
         '<rect x="16.6" y="15.2" width="6" height="4.6" rx="1.2"/>' +
         '<path d="M18.5 19.8v1.6M20.7 19.8v1.6"/>',
    // 액세서리 (공구함)
    ACC: '<rect x="2.4" y="7.6" width="19.2" height="12.4" rx="2"/>' +
         '<path d="M8.8 7.6V5.8a2 2 0 0 1 2-2h2.4a2 2 0 0 1 2 2v1.8"/>' +
         '<path d="M2.4 13.2h19.2"/><rect x="9.8" y="11.4" width="4.4" height="3.6" rx="0.7"/>',
    // 상자
    ETC: '<path d="M3 7.4l9-4.4 9 4.4v9.2l-9 4.4-9-4.4z"/>' +
         '<path d="M3 7.4l9 4.4 9-4.4M12 11.8v9.6"/>'
};

// ───────── 자산별 전용 아이콘 (카테고리보다 우선) ─────────
const ICON_BY_ASSET = {
    // ── 카메라: 기종별 실루엣 ──
    // FX3 : 정육면체 박스형 시네마바디 (험프 없음) + 로드 마운트
    'CAM-001': '<rect x="4.4" y="6.4" width="15.2" height="14" rx="0.9"/>' +
               '<circle cx="12" cy="13.4" r="4.1"/>' +
               '<path d="M7.4 6.4V4.2h6.4v2.2"/>' +
               '<path d="M4.4 9h-2.2M19.6 9h2.2"/>',
    // FX6 : 가로로 긴 바디 + 오른쪽으로 돌출된 XLR 핸들
    'CAM-002': '<rect x="1.4" y="9.2" width="17" height="10.6" rx="1"/>' +
               '<path d="M3.8 9.2V6.4h18.4"/><circle cx="6" cy="5.2" r="1.05"/>' +
               '<circle cx="10" cy="14.5" r="3.5"/>' +
               '<path d="M18.4 12.4v4.2"/>',
    // a7m4 : 미러리스 — 펜타프리즘 험프 + 우측 그립
    'CAM-003': '<path d="M2.4 11.4a2 2 0 0 1 2-2h3.5l1.4-2.6h5.4l1.4 2.6h3.5a2 2 0 0 1 2 2v6.4a2 2 0 0 1-2 2H4.4a2 2 0 0 1-2-2z"/>' +
               '<circle cx="12" cy="14.2" r="3.7"/><circle cx="18.6" cy="11.9" r="0.9"/>',
    // Z90 : 캠코더 — 측면 실루엣 + 렌즈콘 + 상단 뷰파인더
    'CAM-004': '<rect x="1.7" y="8.3" width="13.6" height="9.6" rx="2"/>' +
               '<path d="M15.3 11.4l5.9-3v10.4l-5.9-3z"/>' +
               '<rect x="4.4" y="4.9" width="4.8" height="3.4" rx="0.9"/>' +
               '<circle cx="8.6" cy="13.1" r="1.5"/>',
    // a7m5 : 미러리스 (a7m4와 동일 계열)
    'CAM-005': '<path d="M2.4 11.4a2 2 0 0 1 2-2h3.5l1.4-2.6h5.4l1.4 2.6h3.5a2 2 0 0 1 2 2v6.4a2 2 0 0 1-2 2H4.4a2 2 0 0 1-2-2z"/>' +
               '<circle cx="12" cy="14.2" r="3.7"/><circle cx="18.6" cy="11.9" r="0.9"/>',

    // ── C스탠드 : 그립암 + 너클 + 층진 3다리 ──
    'STD-C':   '<circle cx="8.8" cy="4.5" r="1.35"/><path d="M10.2 4.5h8.2"/>' +
               '<circle cx="19.4" cy="4.5" r="0.95"/>' +
               '<path d="M8.8 5.9v10.4"/>' +
               '<path d="M7.4 9.4h2.8M7.4 12.6h2.8"/>' +
               '<path d="M8.8 16.3L2.6 21M8.8 16.3l5.6 4.7M8.8 16.3l9 3.2"/>',

    // ── 기타(ETC) : 이동수단 3종 + 나머지 ──
    // 카트 : 4바퀴 평판 대차 + 밀대 손잡이
    'ETC-001': '<rect x="2.2" y="13.4" width="14.8" height="2.3" rx="0.8"/>' +
               '<path d="M17 14.6V4.6h4"/>' +
               '<circle cx="6" cy="19.2" r="2.1"/><circle cx="14" cy="19.2" r="2.1"/>' +
               '<path d="M6 15.7v1.4M14 15.7v1.4"/>',
    // 구르마 : 2바퀴 핸드트럭 (사다리 프레임 + 앞으로 뻗은 발판)
    'ETC-002': '<path d="M6.2 3.4v12.4M10.8 3.4v12.4"/>' +
               '<path d="M6.2 3.4h4.6M6.2 7.6h4.6M6.2 11.8h4.6"/>' +
               '<path d="M5 15.8h11.4l-1 2.2H5.6z"/>' +
               '<circle cx="4.6" cy="18.6" r="2.4"/><circle cx="14.6" cy="20" r="1.1"/>',
    // 왜건 : 끌개 손잡이 + 사다리꼴 적재함 + 4바퀴
    'ETC-003': '<path d="M4.6 9.8h14.6l-1.8 6.6H6.4z"/>' +
               '<path d="M4.6 9.8L1.9 5.6M0.7 4.9l2.5-1.5"/>' +
               '<circle cx="8.4" cy="18.5" r="1.9"/><circle cx="15.4" cy="18.5" r="1.9"/>' +
               '<path d="M8.4 16.4v0.2M15.4 16.4v0.2"/>',
    // 카운터웨이트 : 중량 원판
    'ETC-004': '<circle cx="12" cy="12" r="8.6"/><circle cx="12" cy="12" r="2.5"/>' +
               '<path d="M12 3.4v3.2M12 17.4v3.2M3.4 12h3.2M17.4 12h3.2"/>',
    // 샌드백 : 늘어진 자루 + 손잡이 스트랩
    'ETC-005': '<path d="M6.6 8.8h10.8c2 3.4 3 7.2 2.4 10.8H4.2c-.6-3.6.4-7.4 2.4-10.8z"/>' +
               '<path d="M9 8.8c0-2.1 1.35-3.4 3-3.4s3 1.3 3 3.4"/>',
    'ETC-006': '<path d="M6.6 8.8h10.8c2 3.4 3 7.2 2.4 10.8H4.2c-.6-3.6.4-7.4 2.4-10.8z"/>' +
               '<path d="M9 8.8c0-2.1 1.35-3.4 3-3.4s3 1.3 3 3.4"/>',
    'ETC-007': '<path d="M6.6 8.8h10.8c2 3.4 3 7.2 2.4 10.8H4.2c-.6-3.6.4-7.4 2.4-10.8z"/>' +
               '<path d="M9 8.8c0-2.1 1.35-3.4 3-3.4s3 1.3 3 3.4"/>',
    'ETC-008': '<path d="M6.6 8.8h10.8c2 3.4 3 7.2 2.4 10.8H4.2c-.6-3.6.4-7.4 2.4-10.8z"/>' +
               '<path d="M9 8.8c0-2.1 1.35-3.4 3-3.4s3 1.3 3 3.4"/>',
    // 스탠드 바퀴 : 캐스터
    'ETC-009': '<rect x="7.6" y="3.2" width="8.8" height="3.4" rx="0.8"/>' +
               '<path d="M12 6.6v3.2"/><circle cx="12" cy="15" r="5.1"/><circle cx="12" cy="15" r="1.7"/>',
    'ETC-010': '<rect x="7.6" y="3.2" width="8.8" height="3.4" rx="0.8"/>' +
               '<path d="M12 6.6v3.2"/><circle cx="12" cy="15" r="5.1"/><circle cx="12" cy="15" r="1.7"/>',
    // 스위처 : 버튼 그리드 + T바 페이더
    'ETC-011': '<rect x="1.8" y="6.4" width="20.4" height="11.2" rx="1.6"/>' +
               '<rect x="4.2" y="9" width="2.7" height="2.2" rx="0.5"/>' +
               '<rect x="8" y="9" width="2.7" height="2.2" rx="0.5"/>' +
               '<rect x="11.8" y="9" width="2.7" height="2.2" rx="0.5"/>' +
               '<rect x="4.2" y="12.8" width="2.7" height="2.2" rx="0.5"/>' +
               '<rect x="8" y="12.8" width="2.7" height="2.2" rx="0.5"/>' +
               '<rect x="11.8" y="12.8" width="2.7" height="2.2" rx="0.5"/>' +
               '<path d="M18.4 9v6"/><circle cx="18.4" cy="10.7" r="1.15"/>'
};
const ASSET_ICON_KEYS = Object.keys(ICON_BY_ASSET).sort((a, b) => b.length - a.length);

// 장비 하나에 대한 아이콘 path 문자열 (자산 전용 → 카테고리 순)
function iconPathsFor(eq) {
    if (!eq) return ICONS.ETC;
    if (ICON_BY_ASSET[eq.id]) return ICON_BY_ASSET[eq.id];
    for (const k of ASSET_ICON_KEYS) if (eq.id.startsWith(k)) return ICON_BY_ASSET[k];
    return ICONS[eq.cat] || ICONS.ETC;
}
function wrapIcon(paths, cls) {
    return `<svg class="${cls || 'cicon'}" viewBox="0 0 24 24" fill="none" stroke="currentColor"
        stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${paths}</svg>`;
}
function iconSvg(cat, cls) { return wrapIcon(ICONS[cat] || ICONS.ETC, cls); }
function iconSvgFor(eq, cls) { return wrapIcon(iconPathsFor(eq), cls); }

// ═══════════════════════════════════════════════
//              모듈 조립 (마운트/슬롯)
// ═══════════════════════════════════════════════
// 조립체의 최상위가 될 수 있는 카테고리
const ROOT_CATS = ['CAM', 'LIT'];
// 카테고리별 결합 슬롯 (accept = 받아들이는 카테고리)
const SLOTS = {
    CAM: [
        { k: 'lens',    n: '렌즈',      max: 1, accept: ['LEN'] },
        { k: 'support', n: '지지대',    max: 1, accept: ['TRP', 'GIM'] },
        { k: 'card',    n: '메모리',    max: 2, accept: ['STO'] },
        { k: 'batt',    n: '배터리',    max: 2, accept: ['BAT'] },
        { k: 'shoe',    n: '슈',        max: 2, accept: ['MON', 'AUD'] },
        { k: 'rig',     n: '리그',      max: 2, accept: ['ACC', 'CAB'] }
    ],
    LIT: [
        { k: 'support', n: '스탠드',    max: 1, accept: ['STD'] },
        { k: 'mod',     n: '모디파이어', max: 2, accept: ['MOD'] },
        { k: 'power',   n: '전원',      max: 1, accept: ['BAT', 'PWR'] },
        { k: 'ctrl',    n: '제어/케이블', max: 1, accept: ['ACC', 'CAB'] }
    ],
    LEN: [{ k: 'filter', n: '필터', max: 1, accept: ['ACC'] }],
    MON: [{ k: 'power',  n: '전원', max: 1, accept: ['BAT', 'PWR'] }],
    AUD: [{ k: 'support', n: '붐/스탠드', max: 1, accept: ['STD', 'AUD'] },
          { k: 'cable',   n: '케이블',    max: 1, accept: ['CAB'] }],
    GIM: [{ k: 'batt',   n: '배터리', max: 1, accept: ['BAT'] }],
    TRP: [{ k: 'acc',    n: '부속',   max: 1, accept: ['ACC'] }],
    STD: [{ k: 'weight', n: '무게추', max: 2, accept: ['ETC'] }],
    MOD: [{ k: 'support', n: '스탠드', max: 1, accept: ['STD', 'TRP'] }], STO: [], BAT: [], PWR: [], CAB: [], ACC: [], ETC: []
};
// 자산별 추가 슬롯 (C스탠드 그립암 등)
function slotsFor(eq) {
    const base = (SLOTS[eq.cat] || []).slice();
    if (eq.id.startsWith('STD-C')) {
        // C스탠드는 기본이 '기둥 + 터틀베이스'뿐 — 그립암은 별도 액세서리다
        base.unshift({ k: 'hang', n: '암에 매달기', max: 2, accept: ['MOD', 'LIT', 'MON'] });
        base.unshift({ k: 'arm', n: '그립헤드·암 세트', max: 1, accept: ['ACC'] });
    }
    return base;
}
// 블록 트리 헬퍼 (scene.blocks 기준)
function rootBlocks(scene) {
    scene = scene || currentScene();
    return Object.entries(scene.blocks).filter(([k, b]) => !b.parent).map(([k, b]) => k);
}
function childBlocks(bid, scene) {
    scene = scene || currentScene();
    return Object.entries(scene.blocks).filter(([k, b]) => b.parent === bid).map(([k, b]) => k);
}
function descendantBlocks(bid, scene) {
    let out = [];
    childBlocks(bid, scene).forEach(c => { out.push(c); out = out.concat(descendantBlocks(c, scene)); });
    return out;
}
function eqOfBlock(bid, scene) {
    scene = scene || currentScene();
    const b = scene.blocks[bid];
    return b ? EQUIPMENT.find(e => e.id === b.eqId) : null;
}
function slotUsed(bid, k, scene) {
    scene = scene || currentScene();
    return childBlocks(bid, scene).filter(c => scene.blocks[c].slot === k).length;
}
// 부모 블록이 이 카테고리를 받을 수 있는 슬롯 → {slot,name,ok} | null
function acceptSlot(parentBid, childCat, scene) {
    scene = scene || currentScene();
    const pe = eqOfBlock(parentBid, scene);
    if (!pe) return null;
    const slots = slotsFor(pe);
    if (!slots.length) return null;
    // 1) 규격이 맞고 자리가 남은 슬롯
    for (const s of slots)
        if (s.accept.includes(childCat) && slotUsed(parentBid, s.k, scene) < s.max)
            return { slot: s.k, name: s.n, ok: true };
    // 2) 규격은 맞지만 자리가 참 → 경고
    for (const s of slots)
        if (s.accept.includes(childCat))
            return { slot: s.k, name: s.n, ok: false, full: true };
    // 3) 규격이 다르지만 빈 자리가 있음 → 경고 후 허용
    for (const s of slots)
        if (slotUsed(parentBid, s.k, scene) < s.max)
            return { slot: s.k, name: s.n, ok: false };
    return null;
}
// 순환 참조 방지
function isAncestor(maybeAncestor, bid, scene) {
    scene = scene || currentScene();
    let cur = scene.blocks[bid];
    while (cur && cur.parent) {
        if (cur.parent === maybeAncestor) return true;
        cur = scene.blocks[cur.parent];
    }
    return false;
}
const CAT_COLORS = {
    CAM: '#5b9dff', LEN: '#7cc0ff', LIT: '#f2c14e', MOD: '#e08a3c',
    AUD: '#5fc98a', MON: '#2ec8d8', TRP: '#7d8794', STD: '#98a3af',
    GIM: '#b58aff', BAT: '#ef7676', PWR: '#ff9166', STO: '#c78aff',
    CAB: '#49bdb0', ACC: '#a89076', ETC: '#8fa0b0'
};

function renderPalette() {
    const list = document.getElementById('palette-list');
    const search = document.getElementById('search').value.trim().toLowerCase();
    const placedEqIds = placedEqSet();

    // 카테고리별 그룹핑
    const byCategory = {};
    for (const eq of EQUIPMENT) {
        if (activeCat !== 'ALL' && eq.cat !== activeCat) continue;
        if (search) {
            const hay = (eq.id + ' ' + eq.nick + ' ' + eq.product + ' ' + eq.sub).toLowerCase();
            if (!hay.includes(search)) continue;
        }
        (byCategory[eq.cat] = byCategory[eq.cat] || []).push(eq);
    }

    let html = '';
    for (const cat of CAT_ORDER) {
        if (!byCategory[cat]) continue;
        const items = byCategory[cat];
        html += `<div class="cat-group open cat-${cat}" data-cat="${cat}">
            <div class="cat-header" style="${activeCat !== 'ALL' ? 'display:none' : ''}"
                 onclick="this.parentElement.classList.toggle('open')">
                <span class="chead">${iconSvg(cat, 'cicon hd')}${CAT_NAMES[cat]}</span>
                <span class="count">${items.length}</span>
            </div>
            <div class="cat-items">`;
        for (const eq of items) {
            const placed = placedEqIds.has(eq.id) ? 'placed' : '';
            const nick = eq.nick ? `<div class="nick">${esc(eq.nick)}</div>` : '';
            html += `<div class="eq-card cat-${eq.cat} ${placed}" draggable="true" data-eq="${eq.id}">
                ${iconSvgFor(eq)}
                <div class="txt">
                    <div class="id">${eq.id}</div>
                    <div class="name">${esc(eq.product || eq.sub)}</div>
                    ${nick}
                </div>
            </div>`;
        }
        html += `</div></div>`;
    }
    list.innerHTML = html;

    // 팔레트 → 캔버스 드래그
    list.querySelectorAll('.eq-card').forEach(card => {
        card.addEventListener('dragstart', e => {
            e.dataTransfer.setData('eq-id', card.dataset.eq);
            e.dataTransfer.effectAllowed = 'copy';
            dragPayload = { eqId: card.dataset.eq };
        });
        card.addEventListener('dragend', () => {
            dragPayload = null;
            document.querySelectorAll('.block').forEach(x => x.classList.remove('drop-ok', 'drop-warn'));
        });
    });
}
document.getElementById('search').addEventListener('input', renderPalette);

// ===================== 탭 전환 =====================
function switchTab(tab) {
    activeTab = tab;
    document.querySelectorAll('.ptab').forEach(b =>
        b.classList.toggle('active', b.dataset.tab === tab));
    document.getElementById('palette-list').style.display = tab === 'equip' ? 'block' : 'none';
    document.getElementById('sets-list').style.display = tab === 'sets' ? 'block' : 'none';
    document.getElementById('search').style.display = tab === 'equip' ? 'block' : 'none';
    if (tab === 'sets') renderSets();
}

// ===================== 세트 팔레트 렌더 =====================
function renderSets() {
    const list = document.getElementById('sets-list');
    const placedEqIds = placedEqSet();
    let html = `<div class="set-hint">
        세트를 캔버스로 <b>드래그</b>하면 포함 장비가 한 번에 배치되고 자동 그룹으로 묶여요.<br>
        캔버스에서 블록 선택 후 "⭐ 세트로 저장"으로 나만의 세트를 만들 수 있어요.
    </div>`;

    const setIds = Object.keys(state.sets);
    if (setIds.length === 0) {
        html += `<div class="set-hint">저장된 세트가 없습니다.</div>`;
    }
    for (const sid of setIds) {
        const set = state.sets[sid];
        const items = set.eqIds.map(id => EQUIPMENT.find(e => e.id === id)).filter(Boolean);
        const availCount = set.eqIds.filter(id => !placedEqIds.has(id)).length;
        html += `<div class="set-card" data-sid="${sid}">
            <div class="set-head" draggable="true" data-sid="${sid}"
                 onclick="this.parentElement.classList.toggle('open')">
                <div>
                    <div class="set-title">${set.name}</div>
                    <div class="set-drag-hint">↔ 드래그해서 배치</div>
                </div>
                <div style="text-align:right">
                    <div class="set-count">${availCount}/${set.eqIds.length}</div>
                    <div class="set-actions">
                        <button onclick="renameSet('${sid}', event)">이름</button>
                        <button onclick="deleteSet('${sid}', event)">삭제</button>
                    </div>
                </div>
            </div>
            <div class="set-body">`;
        for (const id of set.eqIds) {
            const eq = EQUIPMENT.find(e => e.id === id);
            if (!eq) {
                html += `<div class="set-item"><span class="miss">⚠ ${id} (없음)</span></div>`;
                continue;
            }
            const placed = placedEqIds.has(id) ? '<span class="miss">배치됨</span>' : '';
            const label = dispName(eq);
            html += `<div class="set-item cat-${eq.cat}">
                ${iconSvgFor(eq, 'cicon sm')}<b>${eq.id}</b> ${esc(label)} ${placed}
            </div>`;
        }
        html += `</div></div>`;
    }
    list.innerHTML = html;

    // 세트 드래그 → 캔버스
    list.querySelectorAll('.set-head[draggable]').forEach(head => {
        head.addEventListener('dragstart', e => {
            e.dataTransfer.setData('set-id', head.dataset.sid);
            e.dataTransfer.effectAllowed = 'copy';
        });
    });
}

// ===================== 세트 조작 =====================
function saveAsSet() {
    if (selectedIds.size === 0) {
        alert('캔버스에서 블록을 선택한 뒤 세트로 저장하세요.\n(빈 공간 드래그로 여러 개 선택 가능)');
        return;
    }
    const scene = currentScene();
    const eqIds = [];
    for (const bid of selectedIds) {
        const b = scene.blocks[bid];
        if (b) eqIds.push(b.eqId);
    }
    if (eqIds.length === 0) return;
    const name = prompt(`세트 이름 (${eqIds.length}개 장비)`, '새 세트');
    if (!name) return;
    const sid = 'set' + Date.now();
    state.sets[sid] = { name: name.trim(), eqIds };
    saveState();
    switchTab('sets');
    alert(`"${name}" 세트 저장 완료 (${eqIds.length}개 장비)`);
}
function renameSet(sid, e) {
    e.stopPropagation();
    const set = state.sets[sid];
    const nv = prompt('세트 이름 변경', set.name);
    if (nv) { set.name = nv.trim(); saveState(); renderSets(); }
}
function deleteSet(sid, e) {
    e.stopPropagation();
    if (!confirm(`"${state.sets[sid].name}" 세트를 삭제할까요?`)) return;
    delete state.sets[sid];
    saveState(); renderSets();
}

// ===================== 세트 → 캔버스 일괄 배치 =====================
function placeSet(sid, dropX, dropY) {
    const set = state.sets[sid];
    if (!set) return;
    const scene = currentScene();
    const placedEqIds = new Set(Object.values(scene.blocks).map(b => b.eqId));
    const toPlace = set.eqIds.filter(id =>
        EQUIPMENT.find(e => e.id === id) && !placedEqIds.has(id));

    if (toPlace.length === 0) {
        alert('이 세트의 장비가 모두 이미 배치되어 있습니다.');
        return;
    }

    // 그리드 배치 (한 줄에 3개)
    const COLS = 3, GAP_X = 155, GAP_Y = 70;
    const startX = Math.max(20, dropX);
    const startY = Math.max(20, dropY);
    const gid = 'g' + Date.now();
    const newBids = [];
    toPlace.forEach((eqId, i) => {
        const col = i % COLS, rowN = Math.floor(i / COLS);
        const bid = 'b' + Date.now() + i + Math.random().toString(36).slice(2, 5);
        scene.blocks[bid] = {
            eqId,
            x: startX + col * GAP_X,
            y: startY + rowN * GAP_Y,
            groupId: gid
        };
        newBids.push(bid);
    });

    // 그룹 영역 자동 계산
    let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
    for (const bid of newBids) {
        const b = scene.blocks[bid];
        x1 = Math.min(x1, b.x - 12); y1 = Math.min(y1, b.y - 20);
        x2 = Math.max(x2, b.x + BLOCK_W + 12); y2 = Math.max(y2, b.y + BLOCK_H + 12);
    }
    scene.groups[gid] = {
        name: set.name, x: x1, y: y1, w: x2 - x1, h: y2 - y1
    };

    const skipped = set.eqIds.length - toPlace.length;
    saveState(); renderPalette(); renderCanvas();
    if (skipped > 0) {
        setStatus(`"${set.name}" 배치: ${toPlace.length}개 (이미 배치된 ${skipped}개 제외)`);
    } else {
        setStatus(`"${set.name}" 세트 ${toPlace.length}개 배치 완료`);
    }
}
function setStatus(msg) {
    document.getElementById('status-info').textContent = msg;
    setTimeout(updateStatus, 3000);
}

function hexToRgba(hex, a) {
    const h = hex.replace('#', '');
    const n = parseInt(h.length === 3 ? h.split('').map(c => c + c).join('') : h, 16);
    return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
}

// ===================== 캔버스 렌더 =====================
function renderCanvas() {
    const canvas = document.getElementById('canvas');
    canvas.innerHTML = '';
    const scene = currentScene();

    // 그룹부터 렌더 (뒤에 깔림)
    for (const [gid, g] of Object.entries(scene.groups)) {
        const el = document.createElement('div');
        el.className = 'group';
        el.dataset.gid = gid;
        el.style.left = g.x + 'px'; el.style.top = g.y + 'px';
        el.style.width = g.w + 'px'; el.style.height = g.h + 'px';
        el.innerHTML = `
            <div class="group-label" contenteditable="true">${g.name}</div>
            <div class="group-handle"></div>
        `;
        // 카테고리 그룹이면 해당 색상 적용
        if (g.cat && CAT_COLORS[g.cat]) {
            const c = CAT_COLORS[g.cat];
            el.style.borderColor = c;
            el.style.background = hexToRgba(c, 0.06);
            const lb = el.querySelector('.group-label');
            if (lb) { lb.style.background = c; lb.style.color = '#111'; }
        }
        el.querySelector('.group-label').addEventListener('blur', e => {
            scene.groups[gid].name = e.target.textContent.trim() || '그룹';
            saveState();
        });
        el.querySelector('.group-handle').addEventListener('pointerdown', e => startDrag(e, 'group', gid));
        canvas.appendChild(el);
    }

    // 조립체 (루트 블록)
    for (const bid of rootBlocks(scene)) {
        canvas.appendChild(rigElement(bid, scene));
    }
    // 선 연결 모드: 자식도 독립 카드 + 수직 연결선
    if (rigView === 'link') {
        for (const bid of Object.keys(scene.blocks)) {
            if (!scene.blocks[bid].parent) continue;
            canvas.appendChild(rigElement(bid, scene));
        }
        drawRigLinks(scene);
    }
    updateStatus();
    if (activePane === 'rig') renderRigPane();
}

// 조립체 카드 하나 생성
function rigElement(bid, scene) {
    const b = scene.blocks[bid];
    const eq = eqOfBlock(bid, scene);
    const el = document.createElement('div');
    el.className = `block cat-${eq ? eq.cat : 'ETC'} ${selectedIds.has(bid) ? 'selected' : ''}`
        + (!b.parent && eq && !ROOT_CATS.includes(eq.cat) ? ' loose' : '');
    el.dataset.bid = bid;
    const pos = blockPos(bid, scene);
    el.style.left = pos.x + 'px'; el.style.top = pos.y + 'px';
    const label = b.label || dispName(eq);
    const kids = descendantBlocks(bid, scene);
    const showKids = rigView === 'nest' || (rigView === 'fold' && !b.folded);

    let h = `<div class="rig-head">
        ${eq ? iconSvgFor(eq, 'cicon blk') : ''}
        <div class="btxt">
            <div class="b-id">${eq ? eq.id : '?'}</div>
            <div class="b-name">${esc(label)}</div>
        </div>
        ${kids.length && rigView !== 'link' ? `<span class="rig-cnt">+${kids.length}</span>` : ''}
        <button class="b-remove" onclick="removeBlock('${bid}', event)">×</button>
    </div>`;

    if (rigView !== 'link' && showKids && kids.length) {
        h += '<div class="rig-kids">';
        h += kidRows(bid, 0, scene);
        h += '</div>';
    }
    if (rigView === 'fold' && kids.length)
        h += `<div class="rig-toggle" onclick="toggleRigFold('${bid}',event)">`
           + `${b.folded ? '▾ 펼치기 (' + kids.length + ')' : '▴ 접기'}</div>`;

    el.innerHTML = h;
    el.addEventListener('pointerdown', e => {
        if (e.target.classList.contains('b-remove') || e.target.classList.contains('rig-toggle')
            || e.target.classList.contains('kid-x')) return;
        handleBlockClick(bid, e);
        startDrag(e, 'block', bid);
    });
    el.addEventListener('dblclick', e => { e.stopPropagation(); editBlockLabel(bid); });
    // 팔레트/블록 드롭 대상
    el.addEventListener('dragover', e => { e.preventDefault(); e.stopPropagation(); hlDrop(el, bid); });
    el.addEventListener('dragleave', () => el.classList.remove('drop-ok', 'drop-warn'));
    el.addEventListener('drop', e => { e.preventDefault(); e.stopPropagation(); dropOnBlock(bid, e); });
    return el;
}
function kidRows(pid, depth, scene) {
    let h = '';
    for (const cid of childBlocks(pid, scene)) {
        const cb = scene.blocks[cid];
        const ce = eqOfBlock(cid, scene);
        if (!ce) continue;
        const pe = eqOfBlock(pid, scene);
        const sd = slotsFor(pe).find(s => s.k === cb.slot);
        h += `<div class="rig-kid cat-${ce.cat}${cb.warn ? ' warn' : ''}" data-bid="${cid}"
                 draggable="true" style="padding-left:${8 + depth * 13}px">
                ${iconSvgFor(ce, 'cicon sm')}
                <span class="kid-slot">${sd ? sd.n : (cb.slot || '')}</span>
                <span class="kid-id">${ce.id}</span>
                <span class="kid-nm">${esc(ce.nick || ce.product || ce.sub)}</span>
                <span class="kid-x" onclick="detachBlock('${cid}',event)">×</span>
              </div>`;
        if (rigView !== 'link') h += kidRows(cid, depth + 1, scene);
    }
    return h;
}
// 자식 블록의 화면 좌표 (선 연결 모드에서 자동 배치)
// 루트의 모든 자손을 깊이 우선으로 펼친 한 줄
function linkChain(rootBid, scene) {
    const out = [];
    (function walk(b) {
        childBlocks(b, scene).forEach(c => { out.push(c); walk(c); });
    })(rootBid);
    return out;
}
function rootOf(bid, scene) {
    let cur = bid;
    while (scene.blocks[cur] && scene.blocks[cur].parent) cur = scene.blocks[cur].parent;
    return cur;
}
const LINK_GAP = 72, LINK_TOP = 92;
function blockPos(bid, scene) {
    const b = scene.blocks[bid];
    if (!b.parent) return { x: b.x || 0, y: b.y || 0 };
    if (b.lx !== undefined) return { x: b.lx, y: b.ly };
    // 선 연결: 루트 아래로 한 줄 세로 나열
    const root = rootOf(bid, scene);
    const chain = linkChain(root, scene);
    const i = chain.indexOf(bid);
    const rp = blockPos(root, scene);
    return { x: rp.x + 30, y: rp.y + LINK_TOP + (i < 0 ? 0 : i) * LINK_GAP };
}
// 수직 연결선
function drawRigLinks(scene) {
    let svg = document.getElementById('rig-links');
    if (!svg) {
        svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.id = 'rig-links';
        document.getElementById('canvas').appendChild(svg);
    }
    svg.setAttribute('width', 2000); svg.setAttribute('height', 1500);
    let s = '';
    for (const rb of rootBlocks(scene)) {
        const chain = linkChain(rb, scene);
        if (!chain.length) continue;
        const rp = blockPos(rb, scene);
        const sx = rp.x + 14;                     // 세로 척추 x
        const last = blockPos(chain[chain.length - 1], scene);
        // 척추 한 줄
        s += `<path d="M${sx} ${rp.y + 54} V${last.y + 22}" stroke="#4a5768"
               stroke-width="1.6" fill="none" stroke-linecap="round"/>`;
        // 각 부품으로 짧은 가로 갈래
        chain.forEach(cid => {
            const c = blockPos(cid, scene);
            const eq = eqOfBlock(cid, scene);
            const col = CAT_COLORS[eq ? eq.cat : 'ETC'] || '#6b7684';
            s += `<path d="M${sx} ${c.y + 22} H${c.x - 2}" stroke="${col}"
                   stroke-width="1.6" fill="none" stroke-linecap="round" opacity="0.85"/>`
               + `<circle cx="${sx}" cy="${c.y + 22}" r="3" fill="${col}"/>`;
        });
    }
    svg.innerHTML = s;
}

function updateStatus() {
    const s = currentScene();
    if (s.mode === 'three') {
        const f = ensureFloor(s);
        const st = floorStats();
        document.getElementById('status-info').textContent =
            `씬: ${s.name} [3D] | 천장고 ${f.ceilH}m | 장비 ${st.count}개 | 공간 ${st.roomArea}㎡`;
    } else if (s.mode === 'floor') {
        const f = ensureFloor(s);
        document.getElementById('status-info').textContent =
            `씬: ${s.name} [평면도] | 축척 1m = ${f.zoom}px | 공간 ${f.rooms.length}개`;
    } else {
        const bc = Object.keys(s.blocks).length;
        const gc = Object.keys(s.groups).length;
        document.getElementById('status-info').textContent =
            `씬: ${s.name} | 배치: ${bc}개 블록, ${gc}개 그룹 | 선택: ${selectedIds.size}개`;
    }
    // 세트 탭 열려있으면 배치됨 상태 갱신
    if (activeTab === 'sets') renderSets();
}

// ===================== 드롭 (팔레트 → 캔버스) =====================
const canvasWrap = document.getElementById('canvas-wrap');
const canvas = document.getElementById('canvas');
// wrap에만 리스너 (canvas 이벤트는 버블링으로 올라옴 → 중복 실행 방지)
canvasWrap.addEventListener('dragover', e => { e.preventDefault(); e.dataTransfer.dropEffect = 'copy'; });
canvasWrap.addEventListener('drop', e => {
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const dropX = Math.round(e.clientX - rect.left);
    const dropY = Math.round(e.clientY - rect.top);

    // 세트 드롭
    const setId = e.dataTransfer.getData('set-id');
    if (setId) { placeSet(setId, dropX - 50, dropY - 20); return; }

    // 개별 장비 드롭
    const eqId = e.dataTransfer.getData('eq-id');
    if (!eqId) return;
    const scene = currentScene();
    const already = Object.values(scene.blocks).some(b => b.eqId === eqId);
    if (already) { alert(eqId + ' 는 이미 배치됨'); return; }
    const bid = addBlockAt(eqId, Math.max(0, dropX - 50), Math.max(0, dropY - 20));
    if (bid) { saveState(); renderPalette(); renderCanvas(); afterLayoutChange(); }
});
// 배치도에 블록 하나 추가 (이미 있으면 null)
function addBlockAt(eqId, x, y, quiet) {
    if (isViewOnly()) return null;
    const scene = currentScene();
    if (Object.values(scene.blocks).some(b => b.eqId === eqId)) {
        if (!quiet) alert(eqId + ' 는 이미 배치됨');
        return null;
    }
    const bid = 'b' + Date.now() + Math.random().toString(36).slice(2, 6);
    scene.blocks[bid] = { eqId, x: Math.max(0, x), y: Math.max(0, y) };
    assignGroupByPosition(bid);
    syncFromLayout(false);        // 어떤 경로로 올리든 평면도·3D에 바로 반영
    return bid;
}

// ===================== 휠클릭(가운데 버튼) 팬 이동 =====================
let panCtx = null;
canvasWrap.addEventListener('pointerdown', e => {
    if (e.button !== 1) return; // 가운데 버튼(휠클릭)만
    e.preventDefault();
    panCtx = {
        startX: e.clientX, startY: e.clientY,
        scrollL: canvasWrap.scrollLeft, scrollT: canvasWrap.scrollTop
    };
    canvasWrap.style.cursor = 'grabbing';
    document.addEventListener('pointermove', doPan);
    document.addEventListener('pointerup', endPan);
});
function doPan(e) {
    if (!panCtx) return;
    const dx = e.clientX - panCtx.startX, dy = e.clientY - panCtx.startY;
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) panCtx.moved = true;
    canvasWrap.scrollLeft = panCtx.scrollL - dx;
    canvasWrap.scrollTop = panCtx.scrollT - dy;
}
function endPan() {
    panCtx = null;
    canvasWrap.style.cursor = '';
    document.removeEventListener('pointermove', doPan);
    document.removeEventListener('pointerup', endPan);
}
// 가운데 버튼 클릭 시 브라우저 기본 오토스크롤 방지
canvasWrap.addEventListener('mousedown', e => { if (e.button === 1) e.preventDefault(); });

// ===================== 러버밴드 다중선택 (빈 공간 드래그) =====================
let rubberCtx = null;
const rubberEl = document.createElement('div');
rubberEl.id = 'rubber-band';
canvasWrap.appendChild(rubberEl);  // wrap에 부착 (renderCanvas의 innerHTML 초기화에 안 지워짐)

canvas.addEventListener('pointerdown', e => {
    if (e.button !== 0) return;               // 좌클릭만
    if (spaceDown) { e.preventDefault(); startCanvasPan(e); return; }   // 스페이스 = 화면 이동
    if (e.target !== canvas) return;           // 빈 공간에서 시작할 때만
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    canvas.classList.add('marquee');
    rubberCtx = { x0: e.clientX - rect.left, y0: e.clientY - rect.top, additive: e.shiftKey };
    document.addEventListener('pointermove', doRubber);
    document.addEventListener('pointerup', endRubber);
});
// 빈 캔버스 드래그 = 화면 이동
function startCanvasPan(e) {
    canvas.classList.add('panning');
    panCtx = { startX: e.clientX, startY: e.clientY,
               scrollL: canvasWrap.scrollLeft, scrollT: canvasWrap.scrollTop, moved: false };
    document.addEventListener('pointermove', doPan);
    document.addEventListener('pointerup', endCanvasPan);
}
function endCanvasPan() {
    const moved = panCtx && panCtx.moved;
    canvas.classList.remove('panning');
    panCtx = null;
    document.removeEventListener('pointermove', doPan);
    document.removeEventListener('pointerup', endCanvasPan);
    if (!moved && selectedIds.size) { selectedIds.clear(); renderCanvas(); }   // 제자리 클릭 = 선택 해제
}
function doRubber(e) {
    if (!rubberCtx) return;
    const rect = canvas.getBoundingClientRect();
    const x1 = e.clientX - rect.left;
    const y1 = e.clientY - rect.top;
    const x = Math.min(rubberCtx.x0, x1), y = Math.min(rubberCtx.y0, y1);
    const w = Math.abs(x1 - rubberCtx.x0), h = Math.abs(y1 - rubberCtx.y0);
    rubberCtx.box = { x, y, w, h };
    rubberEl.style.display = 'block';
    rubberEl.style.left = x + 'px'; rubberEl.style.top = y + 'px';
    rubberEl.style.width = w + 'px'; rubberEl.style.height = h + 'px';
}
function endRubber(e) {
    if (!rubberCtx) return;
    const box = rubberCtx.box;
    const additive = rubberCtx.additive;
    rubberCtx = null;
    rubberEl.style.display = 'none';
    canvas.classList.remove('marquee');
    document.removeEventListener('pointermove', doRubber);
    document.removeEventListener('pointerup', endRubber);
    if (!box || (box.w < 5 && box.h < 5)) {
        if (!additive && selectedIds.size) { selectedIds.clear(); renderCanvas(); }
        return;
    }
    if (!additive) selectedIds.clear();
    const scene = currentScene();
    for (const bid of rootBlocks(scene)) {
        const b = scene.blocks[bid];
        // 블록 사각형이 러버밴드와 겹치면 선택
        const overlap = !(b.x + BLOCK_W < box.x || b.x > box.x + box.w ||
                          b.y + BLOCK_H < box.y || b.y > box.y + box.h);
        if (overlap) selectedIds.add(bid);
    }
    renderCanvas();
}

// ===================== 그룹 자동 편입/제외 =====================
const BLOCK_W = 140, BLOCK_H = 56;

function blockCenter(b) {
    return { cx: b.x + BLOCK_W / 2, cy: b.y + BLOCK_H / 2 };
}

function assignGroupByPosition(bid) {
    const scene = currentScene();
    const b = scene.blocks[bid];
    if (!b) return;
    const { cx, cy } = blockCenter(b);
    let hit = null;
    for (const [gid, g] of Object.entries(scene.groups)) {
        if (cx >= g.x && cx <= g.x + g.w && cy >= g.y && cy <= g.y + g.h) {
            hit = gid; break;
        }
    }
    const prev = b.groupId;
    if (hit) {
        b.groupId = hit;
        expandGroupToFit(hit);
    } else if (prev) {
        delete b.groupId;
        shrinkGroupToFit(prev);
    }
}

function expandGroupToFit(gid) {
    const scene = currentScene();
    const g = scene.groups[gid];
    if (!g) return;
    let x1 = g.x, y1 = g.y, x2 = g.x + g.w, y2 = g.y + g.h;
    for (const b of Object.values(scene.blocks)) {
        if (b.groupId !== gid) continue;
        x1 = Math.min(x1, b.x - 12);
        y1 = Math.min(y1, b.y - 20);
        x2 = Math.max(x2, b.x + BLOCK_W + 12);
        y2 = Math.max(y2, b.y + BLOCK_H + 12);
    }
    g.x = x1; g.y = y1; g.w = x2 - x1; g.h = y2 - y1;
}

function shrinkGroupToFit(gid) {
    const scene = currentScene();
    const g = scene.groups[gid];
    if (!g) return;
    const members = Object.values(scene.blocks).filter(b => b.groupId === gid);
    if (members.length === 0) return; // 빈 그룹은 그대로 둠 (영역 유지)
    let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
    for (const b of members) {
        x1 = Math.min(x1, b.x - 12);
        y1 = Math.min(y1, b.y - 20);
        x2 = Math.max(x2, b.x + BLOCK_W + 12);
        y2 = Math.max(y2, b.y + BLOCK_H + 12);
    }
    g.x = x1; g.y = y1; g.w = x2 - x1; g.h = y2 - y1;
}

// ===================== 블록/그룹 이동 (pointer 기반) =====================
function startDrag(e, type, id) {
    if (isViewOnly()) return;               // 공유(보기 전용): 블록·그룹 이동 금지
    e.stopPropagation();
    e.preventDefault();
    const scene = currentScene();
    dragCtx = { type, id, startX: e.clientX, startY: e.clientY, offsets: {}, moved: false };
    let ids = [];
    if (type === 'block' && selectedIds.has(id)) ids = Array.from(selectedIds);
    else if (type === 'block') ids = [id];
    else if (type === 'group') {
        ids = [id];
        for (const [bid, b] of Object.entries(scene.blocks)) {
            if (b.groupId === id) ids.push(bid);
        }
    }
    for (const _id of ids) {
        const obj = scene.blocks[_id] || scene.groups[_id];
        if (obj) dragCtx.offsets[_id] = { x: obj.x, y: obj.y };
    }
    document.addEventListener('pointermove', doDrag);
    document.addEventListener('pointerup', endDrag);
}

function doDrag(e) {
    if (!dragCtx) return;
    const dx = e.clientX - dragCtx.startX;
    const dy = e.clientY - dragCtx.startY;
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) dragCtx.moved = true;
    const scene = currentScene();
    for (const [id, off] of Object.entries(dragCtx.offsets)) {
        const obj = scene.blocks[id] || scene.groups[id];
        if (!obj) continue;
        obj.x = Math.max(0, snapVal(off.x + dx));
        obj.y = Math.max(0, snapVal(off.y + dy));
        // DOM 직접 업데이트 (재렌더 없이 부드럽게)
        const el = canvas.querySelector(`[data-bid="${id}"], [data-gid="${id}"]`);
        if (el) { el.style.left = obj.x + 'px'; el.style.top = obj.y + 'px'; }
    }
    // 블록 하나만 끌 때: 다른 조립체 위에 올리면 결합 예고
    if (dragCtx.type === 'block' && Object.keys(dragCtx.offsets).length === 1) {
        const me = canvas.querySelector(`.block[data-bid="${dragCtx.id}"]`);
        if (me) me.style.pointerEvents = 'none';
        const hit = document.elementFromPoint(e.clientX, e.clientY);
        if (me) me.style.pointerEvents = '';
        const tgt = hit && hit.closest ? hit.closest('.block') : null;
        document.querySelectorAll('.block').forEach(x => x.classList.remove('drop-ok', 'drop-warn'));
        dragCtx.hover = null;
        const tbid = tgt && tgt.dataset.bid;
        const scene = currentScene();
        if (tbid && tbid !== dragCtx.id && scene.blocks[tbid]
            && !isAncestor(dragCtx.id, tbid, scene)) {
            const ce = eqOfBlock(dragCtx.id, scene);
            const r = ce ? acceptSlot(tbid, ce.cat, scene) : null;
            if (r) {
                tgt.classList.add(r.ok ? 'drop-ok' : 'drop-warn');
                dragCtx.hover = { bid: tbid, res: r };
            }
        }
    }
}

function endDrag() {
    if (!dragCtx) return;
    const ctx = dragCtx;
    dragCtx = null;
    document.removeEventListener('pointermove', doDrag);
    document.removeEventListener('pointerup', endDrag);
    document.querySelectorAll('.block').forEach(x => x.classList.remove('drop-ok', 'drop-warn'));
    // 다른 조립체 위에서 놓았으면 결합
    if (ctx.moved && ctx.hover && currentScene().blocks[ctx.id]) {
        attachBlock(ctx.id, ctx.hover.bid, ctx.hover.res);
        return;
    }
    if (ctx.moved) {
        // 이동한 블록들 → 그룹 자동 편입/제외 판정
        if (ctx.type === 'block') {
            for (const id of Object.keys(ctx.offsets)) {
                if (currentScene().blocks[id]) assignGroupByPosition(id);
            }
        }
        saveState();
        renderCanvas();
    }
}

// ===================== 선택 =====================
function handleBlockClick(bid, e) {
    if (e.shiftKey) {
        if (selectedIds.has(bid)) selectedIds.delete(bid);
        else selectedIds.add(bid);
    } else {
        if (!selectedIds.has(bid)) {
            selectedIds.clear();
            selectedIds.add(bid);
        }
    }
    renderCanvas();
}
// (빈 공간 클릭 시 선택 해제는 러버밴드 endRubber에서 처리)

// ===================== 그룹 =====================
function createGroup() {
    if (selectedIds.size < 2) { alert('블록 2개 이상 선택 후 그룹으로 묶어줘'); return; }
    const scene = currentScene();
    const name = prompt('그룹 이름 (예: 포토존, 인터뷰존)', '새 그룹');
    if (!name) return;
    const gid = 'g' + Date.now();
    let minX=Infinity, minY=Infinity, maxX=-Infinity, maxY=-Infinity;
    for (const bid of selectedIds) {
        const b = scene.blocks[bid]; if (!b || b.parent) continue;
        b.groupId = gid;
        minX = Math.min(minX, b.x); minY = Math.min(minY, b.y);
        maxX = Math.max(maxX, b.x + 140); maxY = Math.max(maxY, b.y + 60);
    }
    scene.groups[gid] = {
        name, x: minX - 12, y: minY - 20,
        w: maxX - minX + 24, h: maxY - minY + 32
    };
    selectedIds.clear();
    saveState(); renderCanvas();
}
function ungroup() {
    const scene = currentScene();
    const gids = new Set();
    for (const bid of selectedIds) {
        const b = scene.blocks[bid];
        if (b && b.groupId) gids.add(b.groupId);
    }
    for (const gid of gids) {
        delete scene.groups[gid];
        for (const b of Object.values(scene.blocks)) {
            if (b.groupId === gid) delete b.groupId;
        }
    }
    saveState(); renderCanvas();
}

// ===================== 블록 조작 =====================
function removeBlock(bid, e) {
    e.stopPropagation();
    const n = descendantBlocks(bid).length;
    if (n && !confirm(`하위 부품 ${n}개도 함께 제거됩니다. 계속할까요?`)) return;
    removeBlockTree(bid);
    selectedIds.delete(bid);
    saveState(); renderPalette(); renderCanvas();
}
function editBlockLabel(bid) {
    if (isViewOnly()) return;               // 공유(보기 전용): 블록 라벨 편집 금지
    const b = currentScene().blocks[bid];
    const eq = EQUIPMENT.find(e => e.id === b.eqId);
    const cur = b.label || dispName(eq);
    const nv = prompt('블록 라벨 (씬에서만 사용, 예: "메인 카메라 좌측")', cur);
    if (nv !== null) {
        b.label = nv.trim();
        saveState(); renderCanvas();
    }
}

// ===================== 정렬 기능 =====================
function toggleAlignMenu(e) {
    e.stopPropagation();
    document.getElementById('align-dd').classList.toggle('open');
}
document.addEventListener('click', () => {
    const dd = document.getElementById('align-dd');
    if (dd) dd.classList.remove('open');
});

function snapVal(v) {
    return snapEnabled ? Math.round(v / GRID_SIZE) * GRID_SIZE : Math.round(v);
}

function toggleSnap() {
    snapEnabled = !snapEnabled;
    state.snapEnabled = snapEnabled;
    saveState();
    const btn = document.getElementById('snap-btn');
    btn.textContent = snapEnabled ? '⊞ 스냅 ON' : '⊞ 스냅 OFF';
    btn.classList.toggle('primary', snapEnabled);
}

// 정렬로 움직인 블록이 속한 그룹 영역 재계산
function refreshGroupsOf(ids) {
    const scene = currentScene();
    const gids = new Set();
    ids.forEach(id => {
        const b = scene.blocks[id];
        if (b && b.groupId) gids.add(b.groupId);
    });
    gids.forEach(gid => shrinkGroupToFit(gid));
}

function selectedBlockIds() {
    const scene = currentScene();
    return Array.from(selectedIds).filter(id => scene.blocks[id] && !scene.blocks[id].parent);
}

// 🗂 그룹 안 카테고리 정렬 — 그룹은 유지하고 내부 블록만 카테고리순 재배치
const GRP_COLS = 4, GRP_GAP_X = 155, GRP_GAP_Y = 70, GRP_PAD = 14, GRP_LABEL_H = 28;

// 정렬용: 블록의 실제 렌더 발자국(px). 배치도 캔버스는 줌이 없어 1:1 로 잰다.
// 선 연결(link) 모드에선 부품이 루트 아래로 따로 뻗으므로 그만큼 더 잡는다.
function blockFootprint(bid, scene) {
    const canvas = document.getElementById('canvas');
    const el = canvas && canvas.querySelector(`.block[data-bid="${bid}"]`);
    let w = 220, h = 72;
    if (el && el.getBoundingClientRect) {
        const r = el.getBoundingClientRect();
        if (r.width) w = r.width;
        if (r.height) h = r.height;
    }
    const parts = linkChain(bid, scene).length;
    if (rigView === 'link' && parts > 0) {
        h = Math.max(h, LINK_TOP + (parts - 1) * LINK_GAP + 64);
        w += 30;                       // 부품이 +30px 우측으로 물림
    }
    return { w, h };
}

function sortOneGroup(gid) {
    const scene = currentScene();
    const g = scene.groups[gid];
    if (!g) return 0;
    const members = rootBlocks(scene).filter(bid => scene.blocks[bid].groupId === gid);
    if (members.length === 0) return 0;

    // 카테고리별 묶기
    const byCat = {};
    for (const bid of members) {
        const eq = EQUIPMENT.find(e => e.id === scene.blocks[bid].eqId);
        const cat = eq ? eq.cat : 'ETC';
        (byCat[cat] = byCat[cat] || []).push(bid);
    }

    // 실제 블록 크기 기준으로 셀 크기를 잡아 겹치지 않게 한다
    let cellW = 0, cellH = 0;
    for (const bid of members) {
        const s = blockFootprint(bid, scene);
        cellW = Math.max(cellW, s.w); cellH = Math.max(cellH, s.h);
    }
    const stepX = cellW + 26, stepY = cellH + 22;

    const x0 = g.x + GRP_PAD, y0 = g.y + GRP_LABEL_H;
    let row = 0, maxCols = 0;

    // CAT_ORDER 순서대로, 카테고리마다 새 행에서 시작
    for (const cat of CAT_ORDER) {
        const bids = byCat[cat];
        if (!bids || bids.length === 0) continue;
        bids.sort((a, b) => scene.blocks[a].eqId.localeCompare(scene.blocks[b].eqId));
        bids.forEach((bid, i) => {
            const b = scene.blocks[bid];
            b.x = x0 + (i % GRP_COLS) * stepX;
            b.y = y0 + (row + Math.floor(i / GRP_COLS)) * stepY;
        });
        maxCols = Math.max(maxCols, Math.min(GRP_COLS, bids.length));
        row += Math.ceil(bids.length / GRP_COLS);
    }

    // 그룹 박스 크기를 내용(실측 셀)에 맞게 재조정
    g.w = GRP_PAD * 2 + (maxCols - 1) * stepX + cellW;
    g.h = GRP_LABEL_H + (row - 1) * stepY + cellH + GRP_PAD;
    return members.length;
}

function sortWithinGroups() {
    const scene = currentScene();
    const sel = selectedBlockIds();
    let gids;

    if (sel.length > 0) {
        // 선택한 블록이 속한 그룹만
        gids = [...new Set(sel.map(id => scene.blocks[id].groupId).filter(Boolean))];
        if (gids.length === 0) {
            alert('선택한 블록이 그룹에 속해있지 않습니다.\n먼저 "📦 그룹 만들기"로 묶어주세요.');
            return;
        }
    } else {
        // 선택 없으면 전체 그룹
        gids = Object.keys(scene.groups);
        if (gids.length === 0) {
            alert('그룹이 없습니다.\n블록을 선택하고 "📦 그룹 만들기"로 먼저 묶어주세요.');
            return;
        }
    }

    renderCanvas();                    // 실측을 위해 현재 상태를 먼저 그린다
    let total = 0, done = 0;
    for (const gid of gids) {
        const n = sortOneGroup(gid);
        if (n > 0) { total += n; done++; }
    }
    if (done === 0) { alert('정렬할 블록이 있는 그룹이 없습니다.'); return; }

    saveState(); renderCanvas();
    setStatus(`${done}개 그룹 내부 정렬 완료 — 블록 ${total}개를 카테고리순으로 배치`);
}

// 카테고리별 자동 정리 (그룹 미소속 블록만)
function autoArrangeByCategory() {
    const scene = currentScene();
    const free = rootBlocks(scene).filter(bid => !scene.blocks[bid].groupId);
    if (free.length === 0) {
        alert('정리할 블록이 없습니다.\n(그룹에 속한 블록은 배치를 유지합니다)');
        return;
    }
    // 카테고리별 묶기
    const byCat = {};
    for (const bid of free) {
        const eq = EQUIPMENT.find(e => e.id === scene.blocks[bid].eqId);
        const cat = eq ? eq.cat : 'ETC';
        (byCat[cat] = byCat[cat] || []).push(bid);
    }
    // 기존 그룹 아래쪽부터 시작 (그룹과 겹치지 않게)
    let y0 = 20;
    for (const g of Object.values(scene.groups)) y0 = Math.max(y0, g.y + g.h + 40);

    renderCanvas();                    // 실측을 위해 먼저 그린다
    // 카테고리마다 '한 열' — 블록을 세로로 쌓고, 실제 크기만큼 띄워 겹치지 않게 한다
    const COL_GAP = 34, ROW_GAP = 26, X0 = 20;
    let x = X0, catCount = 0;
    for (const cat of CAT_ORDER) {
        const bids = byCat[cat];
        if (!bids) continue;
        catCount++;
        bids.sort((a, b) => scene.blocks[a].eqId.localeCompare(scene.blocks[b].eqId));
        let y = y0, colW = 0;
        for (const bid of bids) {
            const s = blockFootprint(bid, scene);
            scene.blocks[bid].x = x;
            scene.blocks[bid].y = y;
            y += s.h + ROW_GAP;         // 실제 높이만큼 내려 세로 겹침 방지
            colW = Math.max(colW, s.w);
        }
        x += colW + COL_GAP;            // 다음 카테고리 = 다음 열, 실제 폭만큼 띄워 가로 겹침 방지
    }
    saveState(); renderCanvas();
    setStatus(`카테고리별 정리 완료 — ${free.length}개 블록, ${catCount}개 열`);
}

// 전체 격자 맞춤
function snapAll() {
    const scene = currentScene();
    for (const bid of rootBlocks(scene)) {
        const b = scene.blocks[bid];
        b.x = Math.round((b.x||0) / GRID_SIZE) * GRID_SIZE;
        b.y = Math.round((b.y||0) / GRID_SIZE) * GRID_SIZE;
    }
    Object.keys(scene.groups).forEach(gid => shrinkGroupToFit(gid));
    saveState(); renderCanvas();
    setStatus(`조립체 ${rootBlocks(scene).length}개를 ${GRID_SIZE}px 격자에 맞춤`);
}

// 선택 항목 정렬
function alignBlocks(mode) {
    const scene = currentScene();
    const ids = selectedBlockIds();
    if (ids.length < 2) { alert('블록 2개 이상 선택 후 사용하세요.\n(빈 공간 드래그로 여러 개 선택)'); return; }
    const xs = ids.map(id => scene.blocks[id].x);
    const ys = ids.map(id => scene.blocks[id].y);
    const avg = arr => Math.round(arr.reduce((a, b) => a + b, 0) / arr.length);
    let target;
    switch (mode) {
        case 'left':    target = Math.min(...xs); ids.forEach(id => scene.blocks[id].x = target); break;
        case 'right':   target = Math.max(...xs); ids.forEach(id => scene.blocks[id].x = target); break;
        case 'hcenter': target = avg(xs);         ids.forEach(id => scene.blocks[id].x = target); break;
        case 'top':     target = Math.min(...ys); ids.forEach(id => scene.blocks[id].y = target); break;
        case 'bottom':  target = Math.max(...ys); ids.forEach(id => scene.blocks[id].y = target); break;
        case 'vcenter': target = avg(ys);         ids.forEach(id => scene.blocks[id].y = target); break;
    }
    refreshGroupsOf(ids);
    saveState(); renderCanvas();
    setStatus(`${ids.length}개 블록 정렬 완료`);
}

// 균등 분배
function distributeBlocks(dir) {
    const scene = currentScene();
    const ids = selectedBlockIds();
    if (ids.length < 3) { alert('블록 3개 이상 선택해야 균등 분배할 수 있어요.'); return; }
    const key = dir === 'h' ? 'x' : 'y';
    ids.sort((a, b) => scene.blocks[a][key] - scene.blocks[b][key]);
    const first = scene.blocks[ids[0]][key];
    const last = scene.blocks[ids[ids.length - 1]][key];
    const step = (last - first) / (ids.length - 1);
    ids.forEach((id, i) => { scene.blocks[id][key] = Math.round(first + step * i); });
    refreshGroupsOf(ids);
    saveState(); renderCanvas();
    setStatus(`${ids.length}개 블록 ${dir === 'h' ? '가로' : '세로'} 균등 분배`);
}

// 선택 항목 격자 배열
function gridifySelection() {
    const scene = currentScene();
    const ids = selectedBlockIds();
    if (ids.length < 2) { alert('블록 2개 이상 선택 후 사용하세요.'); return; }
    const x0 = Math.min(...ids.map(id => scene.blocks[id].x));
    const y0 = Math.min(...ids.map(id => scene.blocks[id].y));
    ids.sort((a, b) => scene.blocks[a].eqId.localeCompare(scene.blocks[b].eqId));
    const COLS = Math.ceil(Math.sqrt(ids.length));
    ids.forEach((id, i) => {
        scene.blocks[id].x = x0 + (i % COLS) * 155;
        scene.blocks[id].y = y0 + Math.floor(i / COLS) * 70;
    });
    refreshGroupsOf(ids);
    saveState(); renderCanvas();
    setStatus(`${ids.length}개 블록 격자 배열 (${COLS}열)`);
}

// ═══════════════════════════════════════════════
//                  평면도 모드
// ═══════════════════════════════════════════════
const WORLD_W = 40, WORLD_H = 30;          // 작업 영역 (미터)
let floorMode = 'idle';                     // idle | room | pen | calib
let floorSel = null;                        // {type:'item'|'room', id}
let fDrag = null, calibPts = [];
let penPts = [], penCursor = null, vDrag = null;
let fMulti = new Set();   // 평면도 다중 선택 (아이템 fid)

// ───────── 다각형 기하 ─────────
function polyArea(pts) {
    let a = 0;
    for (let i = 0; i < pts.length; i++) {
        const j = (i + 1) % pts.length;
        a += pts[i].x * pts[j].y - pts[j].x * pts[i].y;
    }
    return Math.abs(a) / 2;
}
function roomArea(r) {
    return r.type === 'poly' ? polyArea(r.pts) : r.w * r.h;
}
function roomCentroid(r) {
    if (r.type !== 'poly') return { x: r.x + r.w / 2, y: r.y + r.h / 2 };
    const p = r.pts;
    let cx = 0, cy = 0, a = 0;
    for (let i = 0; i < p.length; i++) {
        const j = (i + 1) % p.length;
        const f = p[i].x * p[j].y - p[j].x * p[i].y;
        a += f; cx += (p[i].x + p[j].x) * f; cy += (p[i].y + p[j].y) * f;
    }
    a /= 2;
    if (Math.abs(a) < 1e-9) {
        const mx = p.reduce((s, q) => s + q.x, 0) / p.length;
        const my = p.reduce((s, q) => s + q.y, 0) / p.length;
        return { x: r.x + mx, y: r.y + my };
    }
    return { x: r.x + cx / (6 * a), y: r.y + cy / (6 * a) };
}

// 장비 발자국 (미터) — 자산번호 prefix 우선, 없으면 카테고리
const FOOTPRINTS = {
    'STD-C':  { w: 1.10, h: 1.10, clear: 0.50, shape: 'circle' },
    'STD-AS': { w: 0.60, h: 0.60, clear: 0.30, shape: 'circle' },
    'STD-A':  { w: 0.90, h: 0.90, clear: 0.40, shape: 'circle' },
    'STD-T':  { w: 1.00, h: 1.00, clear: 0.40, shape: 'circle' },
    'TRP':    { w: 1.00, h: 1.00, clear: 0.60, shape: 'circle' },
    'CAM':    { w: 0.30, h: 0.30, clear: 0.80, shape: 'rect' },
    'LEN':    { w: 0.15, h: 0.15, clear: 0.10, shape: 'rect' },
    'LIT':    { w: 0.35, h: 0.35, clear: 0.60, shape: 'rect' },
    'MOD':    { w: 0.90, h: 0.90, clear: 0.30, shape: 'rect' },
    'AUD':    { w: 0.25, h: 0.25, clear: 0.30, shape: 'rect' },
    'MON':    { w: 0.40, h: 0.30, clear: 0.40, shape: 'rect' },
    'GIM':    { w: 0.35, h: 0.35, clear: 0.50, shape: 'rect' },
    'BAT':    { w: 0.15, h: 0.12, clear: 0.10, shape: 'rect' },
    'PWR':    { w: 0.35, h: 0.35, clear: 0.20, shape: 'rect' },
    'STO':    { w: 0.10, h: 0.10, clear: 0.05, shape: 'rect' },
    'CAB':    { w: 0.30, h: 0.30, clear: 0.15, shape: 'rect' },
    'ACC':    { w: 0.30, h: 0.30, clear: 0.20, shape: 'rect' },
    'ETC':    { w: 0.60, h: 1.00, clear: 0.40, shape: 'rect' }
};
const FP_KEYS = Object.keys(FOOTPRINTS).sort((a, b) => b.length - a.length);

function footprintOf(eqId) {
    let base = null;
    for (const k of FP_KEYS) if (eqId.startsWith(k)) { base = FOOTPRINTS[k]; break; }
    if (!base) {
        const eq = EQUIPMENT.find(e => e.id === eqId);
        base = FOOTPRINTS[eq ? eq.cat : 'ETC'] || FOOTPRINTS.ETC;
    }
    // 지지대는 3D 스펙(다리 벌림 폭)이 곧 발자국 — 평면도와 3D가 어긋나면 안 된다
    if (/^(TRP|STD)/.test(eqId)) {
        const sp = SPECS[eqId] || null;
        const k2 = SPEC_KEYS.find(k => k.length > 3 && eqId.startsWith(k));
        const sp2 = sp || (k2 ? SPECS[k2] : null);
        if (sp2 && sp2.w) return { w: sp2.w, h: sp2.d || sp2.w, clear: base.clear, shape: base.shape };
    }
    return base;
}
function itemSize(it) {
    const fp = rigFootprint(it);
    return { w: it.w || fp.w, h: it.h || fp.h, clear: (it.clear !== undefined ? it.clear : fp.clear), shape: fp.shape };
}
// ── 조립체 헬퍼 ──
function rigParts(it) { return it && it.parts ? it.parts : []; }
function partIn(it, slot) {
    const p = rigParts(it).find(x => x.slot === slot);
    return p ? p.eqId : null;
}
// 조립체의 지지대(삼각대/스탠드) 자산번호
function supportOf(it) { return partIn(it, 'support'); }
// 바닥 발자국 = 지지대가 있으면 지지대 기준
function rigFootprint(it) {
    const sup = supportOf(it);
    // 그립암 세트가 붙은 C스탠드는 암 길이만큼 여유 공간이 더 필요하다
    const armExtra = (sup || it.eqId || '').startsWith('STD-C') && armKitOf(it)
        ? (specOf(sup || it.eqId).arm || 1.0) : 0;
    if (sup) {
        const f = footprintOf(sup);
        return { w: f.w, h: f.h, shape: f.shape,
                 clear: Math.max(f.clear, footprintOf(it.eqId).clear) + armExtra * 0.5 };
    }
    const f0 = footprintOf(it.eqId);
    return armExtra ? { w: f0.w, h: f0.h, shape: f0.shape, clear: f0.clear + armExtra * 0.5 } : f0;
}
// 조립체 설치 높이 = 지지대 기본 높이, 없으면 카테고리 기본
function rigHeight(it) {
    const sup = supportOf(it);
    if (sup) {
        const sp = specOf(sup);
        return sp.h !== undefined ? sp.h : 1.5;
    }
    const eq = EQUIPMENT.find(e => e.id === it.eqId);
    return eq ? defaultHeight(eq) : 0;
}
// 조립체 높이 조절 범위 (지지대 스펙)
function rigRange(it) {
    const sup = supportOf(it);
    if (sup) {
        const sp = specOf(sup);
        if (sp.hMin !== undefined) return { min: sp.hMin, max: sp.hMax, src: sup };
    }
    return null;
}

const DEFAULT_ROOM = { w: 6.0, h: 4.5, name: '촬영장' };
function ensureFloor(scene) {
    if (!scene.floor) {
        scene.floor = {
            zoom: 50, items: {}, rooms: [], bg: null, showClear: true, confine: true,
            rooms: [{ id: 'r_default', name: DEFAULT_ROOM.name, type: 'rect',
                      x: 1.0, y: 1.0, w: DEFAULT_ROOM.w, h: DEFAULT_ROOM.h }]
        };
    }
    if (scene.floor.confine === undefined) scene.floor.confine = true;
    if (scene.floor.showClear === undefined) scene.floor.showClear = true;
    return scene.floor;
}
function F() { return ensureFloor(currentScene()); }

// ───────── 방 경계 ─────────
// 첫 번째 방을 '촬영 공간'으로 본다. 장비·피사체는 그 밖으로 못 나간다.
function activeRoom(f) {
    f = f || F();
    return (f.rooms && f.rooms.length) ? f.rooms[0] : null;
}
function roomPoly(r) {
    if (!r) return null;
    return r.type === 'poly'
        ? r.pts.map(p => ({ x: r.x + p.x, y: r.y + p.y }))
        : [{ x: r.x, y: r.y }, { x: r.x + r.w, y: r.y },
           { x: r.x + r.w, y: r.y + r.h }, { x: r.x, y: r.y + r.h }];
}
function pointInPoly(pts, x, y) {
    let inside = false;
    for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
        const a = pts[i], b = pts[j];
        if ((a.y > y) !== (b.y > y) &&
            x < (b.x - a.x) * (y - a.y) / (b.y - a.y) + a.x) inside = !inside;
    }
    return inside;
}
// 선분 위 최근접점
function closestOnSeg(a, b, x, y) {
    const dx = b.x - a.x, dy = b.y - a.y;
    const L = dx * dx + dy * dy;
    if (L < 1e-9) return { x: a.x, y: a.y, d: Math.hypot(x - a.x, y - a.y) };
    let t = ((x - a.x) * dx + (y - a.y) * dy) / L;
    t = Math.max(0, Math.min(1, t));
    const px = a.x + dx * t, py = a.y + dy * t;
    return { x: px, y: py, d: Math.hypot(x - px, y - py) };
}
// (x,y)를 방 안으로 끌어들인다. r = 장비 반경(발자국 절반)
function clampToRoom(x, y, r, f) {
    f = f || F();
    x = Math.max(0, Math.min(WORLD_W, x));
    y = Math.max(0, Math.min(WORLD_H, y));
    const room = activeRoom(f);
    if (!room || !f.confine) return { x, y, hit: false };
    r = r || 0;
    if (room.type !== 'poly') {
        const lo = { x: room.x + r, y: room.y + r };
        const hi = { x: room.x + room.w - r, y: room.y + room.h - r };
        const nx = Math.min(Math.max(x, Math.min(lo.x, hi.x)), Math.max(lo.x, hi.x));
        const ny = Math.min(Math.max(y, Math.min(lo.y, hi.y)), Math.max(lo.y, hi.y));
        return { x: +nx.toFixed(3), y: +ny.toFixed(3), hit: nx !== x || ny !== y };
    }
    // 다각형: 가장 가까운 벽을 찾아 '안쪽 법선' 방향으로 r 만큼 밀어넣는다.
    // 오목한 모서리에서는 한 번으로 안 끝나므로 몇 차례 반복 보정한다.
    const pts = roomPoly(room);
    const cx = pts.reduce((t, p) => t + p.x, 0) / pts.length;
    const cy = pts.reduce((t, p) => t + p.y, 0) / pts.length;
    let px = x, py = y, moved = false;
    for (let pass = 0; pass < 6; pass++) {
        let best = null, ba = null, bb = null;
        for (let i = 0; i < pts.length; i++) {
            const a = pts[i], b = pts[(i + 1) % pts.length];
            const c = closestOnSeg(a, b, px, py);
            if (!best || c.d < best.d) { best = c; ba = a; bb = b; }
        }
        const inside = pointInPoly(pts, px, py);
        if (inside && best.d >= r - 1e-6) break;
        // 벽에 수직인 두 방향 중 방 안쪽으로 들어가는 쪽
        const ex = bb.x - ba.x, ey = bb.y - ba.y, L2 = Math.hypot(ex, ey) || 1;
        const nx1 = -ey / L2, ny1 = ex / L2;
        const c1 = { x: best.x + nx1 * r, y: best.y + ny1 * r };
        const c2 = { x: best.x - nx1 * r, y: best.y - ny1 * r };
        let pick = pointInPoly(pts, c1.x, c1.y) ? c1
                 : pointInPoly(pts, c2.x, c2.y) ? c2 : null;
        if (!pick) {   // 둘 다 안 되면 중심 쪽으로
            let vx = cx - best.x, vy = cy - best.y;
            const L = Math.hypot(vx, vy) || 1;
            pick = { x: best.x + vx / L * r, y: best.y + vy / L * r };
        }
        px = pick.x; py = pick.y; moved = true;
    }
    return { x: +px.toFixed(3), y: +py.toFixed(3), hit: moved };
}
// 장비 한 개를 방 안으로 (발자국 반경 기준)
function confineItem(it) {
    const sz = itemSize(it);
    const r = Math.max(sz.w, sz.h) / 2;
    const c = clampToRoom(it.x, it.y, r);
    it.x = c.x; it.y = c.y;
    return c.hit;
}
function confineSubject(sj) {
    const c = clampToRoom(sj.x, sj.y, 0.25);
    sj.x = c.x; sj.y = c.y;
    return c.hit;
}
function toggleConfine() {
    const f = F();
    f.confine = !f.confine;
    if (f.confine) {
        Object.values(f.items).forEach(confineItem);
        (f.subjects || []).forEach(confineSubject);
    }
    saveState();
    if (currentScene().mode === 'three' && R3) { build3D(); showSel(); } else renderFloor();
    syncConfineBtn();
    setStatus(f.confine ? '장비를 방 안으로 제한합니다' : '방 밖에도 놓을 수 있습니다');
}
function syncConfineBtn() {
    const f = F();
    ['cf-btn', 'cf-btn2'].forEach(id => {
        const b = document.getElementById(id);
        if (b) { b.classList.toggle('primary', f.confine);
                 b.textContent = f.confine ? '🚧 방 안으로 제한' : '🚧 제한 해제됨'; }
    });
}

// ───────── 모드 전환 ─────────
// 툴바의 현재 씬 이름 (이름이 바뀌면 어디서든 바로 갱신)
function updateSceneChip() {
    const chip = document.getElementById('scene-chip');
    if (chip) chip.innerHTML = `<span class="sc-k">씬</span> ${esc(currentScene().name)}`;
}
function switchMode(m) {
    const scene = currentScene();
    scene.mode = m;
    const ml = document.getElementById('mode-list');
    if (ml) ml.classList.toggle('on', m === 'list');
    document.getElementById('mode-layout').classList.toggle('on', m === 'layout');
    document.getElementById('mode-floor').classList.toggle('on', m === 'floor');
    document.getElementById('mode-3d').classList.toggle('on', m === 'three');
    updateSceneChip();
    document.getElementById('list-wrap').style.display = m === 'list' ? 'block' : 'none';
    document.getElementById('canvas-wrap').style.display = m === 'layout' ? 'block' : 'none';
    document.getElementById('floor-wrap').style.display = m === 'floor' ? 'block' : 'none';
    document.getElementById('three-wrap').style.display = m === 'three' ? 'block' : 'none';
    document.getElementById('list-tools').style.display = m === 'list' ? 'inline-flex' : 'none';
    document.getElementById('layout-tools').style.display = m === 'layout' ? 'inline-flex' : 'none';
    document.getElementById('floor-tools').style.display = m === 'floor' ? 'inline-flex' : 'none';
    document.getElementById('three-tools').style.display = m === 'three' ? 'inline-flex' : 'none';
    if (m !== 'three') { keysDown.clear(); } else { updateNavHint(); }
    document.getElementById('floor-stats').textContent = '';
    saveState();
    renderPalette();
    if (m === 'floor' || m === 'three') syncFromLayout(false);
    if (m === 'three') {
        if (init3D()) {
            const f = ensure3D(scene);
            document.getElementById('ceil-in').value = f.ceilH;
            syncRoomUI();
            document.getElementById('fr-btn').classList.toggle('primary', frustumOn);
            document.getElementById('pv-btn').classList.toggle('primary', previewOn);
            resize3D(); build3D(); showSel(); updateStatus();
        }
    } else {
        const cp = document.getElementById('cam-panel');
        if (cp) cp.style.display = 'none';
        const pv = document.getElementById('pv-frame');
        if (pv) pv.style.display = 'none';
        if (m === 'floor') renderFloor();
        else if (m === 'list') renderList();
        else renderCanvas();
    }
}



// ═══════════════════════════════════════════════════
//  Supabase 연동 — 공유 링크 · 사진 인식
//  URL·anon 키는 공개돼도 되는 값입니다 (RLS 로 보호).
//  API 키 같은 비밀은 절대 여기 넣지 마세요 — Edge Function 시크릿에만 둡니다.
// ═══════════════════════════════════════════════════
// 서버 접속 정보 — 앱에 내장한다. 이 두 값은 공개돼도 안전하다(RLS 로 보호,
// publishable 키는 애초에 공개용). secret 키(sb_secret_…)는 절대 여기 두지 않는다.
const SB_DEFAULT = {
    url: 'https://hjngckjymvveafjtfxfh.supabase.co',
    anon: 'sb_publishable_d0h34gAFmb3g5674LVgN4A_PUQgzyyX',
};
function sbCfg() {
    const c = state.sb || {};
    return { url: (c.url || SB_DEFAULT.url).replace(/\/+$/, ''), anon: c.anon || SB_DEFAULT.anon };
}
function sbReady() { const c = sbCfg(); return !!(c.url && c.anon); }
// 키 형식에 맞는 헤더를 만든다.
//  · 옛 키(eyJ… JWT)  → apikey + Authorization 둘 다
//  · 새 키(sb_publishable_…) → apikey 만 (JWT 가 아니라 Authorization 에 넣으면 거부됨)
function sbHeaders(key) {
    const h = { apikey: key, 'Content-Type': 'application/json' };
    const tok = typeof authToken === 'function' ? authToken() : null;
    if (tok) h.Authorization = 'Bearer ' + tok;        // 로그인했으면 사용자 토큰
    else if (/^eyJ/.test(key)) h.Authorization = 'Bearer ' + key;
    return h;
}
async function sbFetch(path, opts) {
    const c = sbCfg();
    if (!c.url || !c.anon) throw new Error('서버 설정이 아직 없습니다');
    const r = await fetch(c.url + path, Object.assign({}, opts, {
        headers: Object.assign(sbHeaders(c.anon), (opts && opts.headers) || {}),
    }));
    if (!r.ok) {
        let d = ''; try { d = (await r.text()).slice(0, 300); } catch (e) {}
        throw new Error(`서버 오류 ${r.status} ${d}`);
    }
    // 본문이 비어 있을 수 있다 (204, 또는 Prefer: return=minimal 의 201).
    // 빈 본문에 r.json() 을 부르면 "Unexpected end of JSON input" 로 터진다.
    const text = await r.text();
    return text ? JSON.parse(text) : null;
}
// 추측하기 어려운 짧은 id
function shareId() {
    const A = 'abcdefghijkmnpqrstuvwxyz23456789';
    let out = '';
    const buf = new Uint8Array(12);
    (window.crypto || {}).getRandomValues
        ? window.crypto.getRandomValues(buf)
        : buf.forEach((_, i) => buf[i] = Math.floor(Math.random() * 256));
    for (let i = 0; i < 12; i++) out += A[buf[i] % A.length];
    return out;
}
// 공유용으로 담을 것만 추린다 (편집 상태·설정은 뺀다)
// 외부(감독님)에게 보내므로, "현재 씬에 실제로 놓인 장비"만 담는다.
// 씬과 무관한 재고의 보관위치·상태·메모(eqEdits)나 다른 세트는 내보내지 않는다.
function sceneForShare() {
    const sc = currentScene();
    const used = new Set([
        ...Object.values(sc.blocks || {}).map(b => b.eqId),
        ...Object.values((sc.floor && sc.floor.items) || {}).map(i => i.eqId),
    ].filter(Boolean));
    const allEdits = state.eqEdits || {};
    const eqEdits = {};
    for (const id of used) if (allEdits[id]) eqEdits[id] = allEdits[id];
    const allSets = state.sets || {};
    const sets = {};
    for (const [sid, s] of Object.entries(allSets))
        if ((s.eqIds || []).some(id => used.has(id))) sets[sid] = s;
    return {
        v: 1,
        name: sc.name,
        blocks: sc.blocks, groups: sc.groups,
        floor: sc.floor,
        sets,
        eqEdits,
        madeAt: new Date().toISOString(),
    };
}
const SHARE_DAYS = [7, 30, 90];
async function createShareLink() {
    const sc = currentScene();
    const days = SHARE_DAYS[Math.max(0, SHARE_DAYS.indexOf(+(state.shareDays || 30)))] || 30;
    const id = shareId();
    const payload = sceneForShare();
    const bytes = new Blob([JSON.stringify(payload)]).size;
    if (bytes > 2.8 * 1024 * 1024) {
        alert(`씬이 너무 큽니다 (${(bytes / 1024 / 1024).toFixed(1)}MB).\n배경 도면을 지우거나 더 작은 사진으로 바꿔주세요.`);
        return;
    }
    setStatus('공유 링크 만드는 중…');
    try {
        await sbFetch('/rest/v1/gear_scenes', {
            method: 'POST',
            headers: { Prefer: 'return=minimal' },
            body: JSON.stringify({
                id, name: sc.name, data: payload,
                is_public: true,
                expires_at: new Date(Date.now() + days * 864e5).toISOString(),
            }),
        });
    } catch (e) {
        alert('공유 링크를 만들지 못했습니다.\n\n' + e.message);
        setStatus('공유 실패');
        return;
    }
    const link = location.origin + location.pathname + '?s=' + id;
    state.shares = state.shares || [];
    state.shares.unshift({ id, name: sc.name, at: Date.now(), days, bytes });
    state.shares = state.shares.slice(0, 20);
    saveState();
    showShareResult(link, days, bytes);
    renderScenePane();
}
// 날짜+시간 표기 (예: "8/12 오후 2:30")
function fmtShareTime(t) {
    return new Date(t).toLocaleString('ko-KR',
        { month: 'numeric', day: 'numeric', hour: 'numeric', minute: '2-digit' });
}
function showShareResult(link, days, bytes) {
    const box = document.getElementById('share-modal');
    document.getElementById('share-link').value = link;
    const expiry = fmtShareTime(Date.now() + days * 864e5);
    document.getElementById('share-meta').textContent =
        `${days}일 후 만료 (${expiry}까지) · ${(bytes / 1024).toFixed(0)}KB · 보기 전용`;
    box.classList.add('on');
}
function copyShareLink() {
    const el = document.getElementById('share-link');
    el.select();
    if (navigator.clipboard) navigator.clipboard.writeText(el.value);
    else document.execCommand('copy');
    setStatus('링크를 복사했습니다');
}
function closeShare() { document.getElementById('share-modal').classList.remove('on'); }
async function revokeShare(id) {
    // 회수 = 씬을 is_public=false 로 UPDATE. 서버는 로그인한 스튜디오 계정에만
    // 수정 권한을 준다(익명은 permission denied 42501). 먼저 로그인부터 요구한다.
    if (!requireLogin('링크를 회수')) return;
    if (!confirm('이 링크를 지금 죽입니다. 받은 사람은 더 이상 볼 수 없습니다.\n계속할까요?')) return;
    try {
        if (!(await ensureAuth())) throw new Error('로그인이 만료되었습니다. 다시 로그인해 주세요.');
        await sbFetch(`/rest/v1/gear_scenes?id=eq.${encodeURIComponent(id)}`, {
            method: 'PATCH', headers: { Prefer: 'return=minimal' },
            body: JSON.stringify({ is_public: false }),
        });
    } catch (e) { alert('회수하지 못했습니다.\n' + e.message); return; }
    state.shares = (state.shares || []).map(x => x.id === id ? Object.assign({}, x, { dead: true }) : x);
    saveState(); renderScenePane();
    setStatus('링크를 회수했습니다');
}

// ── 읽기 전용 모드 (공유 링크로 열었을 때) ──
let viewOnly = false;
function isViewOnly() { return viewOnly; }
async function loadSharedScene(id) {
    const app = document.getElementById('app');
    try {
        const rows = await sbFetch(`/rest/v1/gear_scenes?id=eq.${encodeURIComponent(id)}&select=name,data,expires_at`);
        if (!rows || !rows.length) throw new Error('링크가 만료되었거나 회수되었습니다');
        const d = rows[0].data || {};
        state.scenes = { shared: {
            name: d.name || rows[0].name || '공유된 배치',
            blocks: d.blocks || {}, groups: d.groups || {},
            floor: d.floor || null, mode: 'floor',
        } };
        state.currentScene = 'shared';
        if (d.sets) state.sets = d.sets;
        if (d.eqEdits) { state.eqEdits = d.eqEdits; applyEqEdits(); }
        viewOnly = true;
        app.classList.add('view-only');
        document.getElementById('vo-name').textContent = state.scenes.shared.name;
        document.getElementById('vo-bar').style.display = 'flex';
        try { await sbFetch('/rest/v1/rpc/gear_bump_view', {
            method: 'POST', body: JSON.stringify({ p_id: id, p_ua: navigator.userAgent }) }); } catch (e) {}
        switchMode('floor');
        setStatus('보기 전용으로 열었습니다');
    } catch (e) {
        document.body.innerHTML =
            `<div style="display:flex;align-items:center;justify-content:center;height:100vh;
                 font-family:-apple-system,sans-serif;background:#0b0e13;color:#b9c4d1;text-align:center">
               <div><div style="font-size:44px;margin-bottom:14px">🔒</div>
               <div style="font-size:17px;color:#eef2f7;margin-bottom:8px">링크를 열 수 없습니다</div>
               <div style="font-size:13px;color:#8b97a6">${esc(e.message)}</div>
               <div style="font-size:12px;color:#5f6b7a;margin-top:18px">보낸 사람에게 새 링크를 요청해 주세요.</div>
               </div></div>`;
        throw e;
    }
}

// ═══════════════════════════════════════════════════
//  장비 목록을 서버에서 읽고 쓰기
//  · 서버가 연결돼 있으면 서버가 원본
//  · 연결이 없거나 실패하면 파일에 들어 있는 목록으로 동작 (오프라인)
// ═══════════════════════════════════════════════════
let eqSource = 'local';        // 'local' | 'server'
function eqIsServer() { return eqSource === 'server'; }

// 서버 행 → 앱이 쓰는 모양
function rowToEq(r) {
    return {
        id: r.id, nick: r.nick || '', cat: r.cat, catLabel: r.cat_label || '',
        sub: r.sub || '', product: r.product || '', brand: r.brand || '',
        model: r.model || '', status: r.status || '정상',
        loc: r.location || '', note: r.note || '',
    };
}
async function loadEquipmentFromServer() {
    if (!sbReady()) { eqSource = 'local'; return false; }
    try {
        const rows = await sbFetch('/rest/v1/gear_equipment'
            + '?select=id,nick,cat,cat_label,sub,product,brand,model,status,location,note,sort_order'
            + '&active=eq.true&order=sort_order.asc');
        if (!Array.isArray(rows) || !rows.length) throw new Error('장비가 비어 있습니다');
        EQUIPMENT.length = 0;
        rows.forEach(r => EQUIPMENT.push(rowToEq(r)));
        // 치수도 함께
        try {
            const sp = await sbFetch('/rest/v1/gear_specs?select=id,w,d,h,h_min,h_max,default_h,src');
            (sp || []).forEach(x => {
                if (x.w == null && x.h == null) return;
                SPECS[x.id] = Object.assign({}, SPECS[x.id], {
                    w: +x.w || undefined, d: +x.d || undefined, h: +x.h || undefined,
                    hMin: x.h_min == null ? undefined : +x.h_min,
                    hMax: x.h_max == null ? undefined : +x.h_max,
                    src: x.src && /공식/.test(x.src) ? 'spec' : x.src && /평균/.test(x.src) ? 'avg' : 'est',
                });
                Object.keys(SPECS[x.id]).forEach(k => SPECS[x.id][k] === undefined && delete SPECS[x.id][k]);
            });
        } catch (e) { /* 치수는 없어도 동작 */ }
        eqSource = 'server';
        _spc = null;                       // 같은 제품 수 캐시 초기화
        setStatus(`서버에서 장비 ${EQUIPMENT.length}개를 불러왔습니다`);
        return true;
    } catch (e) {
        eqSource = 'local';
        setStatus('서버에서 장비를 못 불러와 파일 목록으로 엽니다 — ' + e.message);
        return false;
    }
}
// 한 항목 저장
async function saveEqToServer(id, patch) {
    if (!(await ensureAuth())) throw new Error('로그인이 만료되었습니다. 다시 로그인해 주세요.');
    await sbFetch(`/rest/v1/gear_equipment?id=eq.${encodeURIComponent(id)}`, {
        method: 'PATCH', headers: { Prefer: 'return=minimal' },
        body: JSON.stringify(patch),
    });
}
// 장비 추가
async function addEquipment() {
    if (!requireLogin('장비를 추가')) return;
    if (!eqIsServer()) { alert('서버에 연결된 상태에서만 추가할 수 있습니다.'); return; }
    const cat = (prompt('카테고리 코드를 입력하세요.\n\n' + CAT_ORDER.join(' · '), 'ACC') || '').trim().toUpperCase();
    if (!cat) return;
    if (!CAT_ORDER.includes(cat)) { alert(`"${cat}" 는 없는 카테고리입니다.`); return; }
    const product = (prompt('제품명을 입력하세요.', '') || '').trim();
    if (!product) return;
    // 다음 번호 찾기
    const used = EQUIPMENT.filter(e => e.cat === cat)
        .map(e => { const m = e.id.match(/(\d+)$/); return m ? +m[1] : 0; });
    const next = (used.length ? Math.max(...used) : 0) + 1;
    const id = `${cat}-${String(next).padStart(3, '0')}`;
    if (!confirm(`새 자산번호는 ${id} 입니다.\n\n${product}\n\n추가할까요?`)) return;
    try {
        await ensureAuth();
        await sbFetch('/rest/v1/gear_equipment', {
            method: 'POST', headers: { Prefer: 'return=minimal' },
            body: JSON.stringify({
                id, cat, cat_label: CAT_NAMES[cat] || cat, product,
                status: '정상', sort_order: EQUIPMENT.length + 1,
            }),
        });
    } catch (e) { alert('추가하지 못했습니다.\n\n' + e.message); return; }
    await loadEquipmentFromServer();
    listState.q = id; syncListTools(); renderList(); renderPalette();
    setStatus(`${id} ${product} 를 추가했습니다`);
}
// 장비 숨기기 (이력은 남기고 목록에서만 제거)
async function retireEquipment(id) {
    if (!requireLogin('장비를 목록에서 내리')) return;
    const eq = EQUIPMENT.find(e => e.id === id);
    if (!eq) return;
    if (!confirm(`${id} ${dispName(eq)} 를 목록에서 내립니다.\n\n`
        + `기록은 서버에 남고, 목록·팔레트에서만 보이지 않게 됩니다.\n계속할까요?`)) return;
    try {
        await ensureAuth();
        await saveEqToServer(id, { active: false });
    } catch (e) { alert('처리하지 못했습니다.\n\n' + e.message); return; }
    await loadEquipmentFromServer();
    renderList(); renderPalette();
    setStatus(`${id} 를 목록에서 내렸습니다`);
}

// ═══════════════════════════════════════════════════
//  로그인 (Supabase Auth) — 수정·추가는 로그인한 계정만
// ═══════════════════════════════════════════════════
function authState() { return (state.auth = state.auth || {}); }
function authToken() {
    const a = authState();
    if (!a.access || !a.expires) return null;
    return Date.now() < a.expires - 30000 ? a.access : null;   // 30초 여유
}
function isLoggedIn() { return !!(authState().access && authState().email); }
function authEmail() { return authState().email || ''; }

async function sbLogin(email, password) {
    const c = sbCfg();
    const r = await fetch(c.url + '/auth/v1/token?grant_type=password', {
        method: 'POST',
        headers: { apikey: c.anon, 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    });
    const out = await r.json().catch(() => ({}));
    if (!r.ok) {
        const m = String(out.error_description || out.msg || out.message || '');
        if (/invalid.*credential|invalid login/i.test(m)) throw new Error('이메일 또는 비밀번호가 맞지 않습니다');
        if (/email not confirmed/i.test(m)) throw new Error('이메일 인증이 아직 안 됐습니다');
        throw new Error(m || `로그인 실패 (${r.status})`);
    }
    state.auth = {
        access: out.access_token,
        refresh: out.refresh_token,
        expires: Date.now() + (out.expires_in || 3600) * 1000,
        email: (out.user && out.user.email) || email,
        uid: out.user && out.user.id,
    };
    saveState();
    return state.auth;
}
async function sbRefresh() {
    const a = authState();
    if (!a.refresh) return false;
    const c = sbCfg();
    try {
        const r = await fetch(c.url + '/auth/v1/token?grant_type=refresh_token', {
            method: 'POST',
            headers: { apikey: c.anon, 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: a.refresh }),
        });
        if (!r.ok) throw new Error('refresh 실패');
        const out = await r.json();
        state.auth = Object.assign({}, a, {
            access: out.access_token,
            refresh: out.refresh_token || a.refresh,
            expires: Date.now() + (out.expires_in || 3600) * 1000,
        });
        saveState();
        return true;
    } catch (e) {
        state.auth = {};            // 세션 만료 → 로그아웃 처리
        saveState();
        return false;
    }
}
// 토큰이 곧 만료면 미리 갱신
async function ensureAuth() {
    const a = authState();
    if (!a.access) return false;
    if (authToken()) return true;
    return sbRefresh();
}
function sbLogout() {
    state.auth = {};
    saveState();
    syncAuthUI();
    renderScenePane(); renderList();
    setStatus('로그아웃했습니다 — 이제 보기만 가능합니다');
}

// ═══════════════════════════════════════════════════
//  작업공간(씬·세트) 서버 동기화
//  씬/세트는 원래 이 브라우저(localStorage)에만 있었다. 로그인하면 스튜디오 공용
//  작업공간(gear_workspaces, id='studio')에 저장해 다른 기기에서도 이어서 작업한다.
//  로그아웃·익명이면 저장하지 않고 이 브라우저에만 둔다(기존 동작). 보기 전용도 저장 안 함.
// ═══════════════════════════════════════════════════
function workspaceForServer() {
    return { scenes: state.scenes, sets: state.sets, currentScene: state.currentScene };
}
let _wsTimer = null;
function scheduleWorkspaceSync() {          // 저장 폭주를 막으려 1.5초 디바운스
    clearTimeout(_wsTimer);
    _wsTimer = setTimeout(() => { pushWorkspace(); }, 1500);
}
async function pushWorkspace() {
    if (!isLoggedIn() || viewOnly) return;
    try {
        if (!(await ensureAuth())) return;
        await sbFetch('/rest/v1/gear_workspaces', {
            method: 'POST',
            headers: { Prefer: 'resolution=merge-duplicates,return=minimal' },   // 단일 행 upsert
            body: JSON.stringify({
                id: 'studio',
                data: workspaceForServer(),
                updated_at: new Date().toISOString(),
            }),
        });
    } catch (e) { console.warn('작업공간 저장 실패 — 로컬엔 저장됨', e); }   // 오프라인이어도 앱은 정상
}
async function pullWorkspace() {
    if (!isLoggedIn()) return;
    try {
        const rows = await sbFetch('/rest/v1/gear_workspaces?id=eq.studio&select=data,updated_at');
        const d = rows && rows.length ? rows[0].data : null;
        if (d && d.scenes && Object.keys(d.scenes).length) {
            state.scenes = d.scenes;
            if (d.sets) state.sets = d.sets;
            state.currentScene = (d.currentScene && d.scenes[d.currentScene])
                ? d.currentScene : Object.keys(d.scenes)[0];
            try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) {}  // 로컬 캐시 갱신(다시 밀어올리지 않음)
        } else if (state.scenes && Object.keys(state.scenes).length) {
            await pushWorkspace();              // 서버에 아직 없으면 이 브라우저 씬을 처음으로 올린다
        }
    } catch (e) { console.warn('작업공간 불러오기 실패 — 로컬 사용', e); }
}

// ── 로그인 화면 ──
function openLogin() {
    document.getElementById('lg-err').textContent = '';
    document.getElementById('lg-email').value = authEmail();
    document.getElementById('lg-pw').value = '';
    document.getElementById('login-modal').classList.add('on');
    setTimeout(() => { const el = document.getElementById(authEmail() ? 'lg-pw' : 'lg-email'); if (el.focus) el.focus(); }, 60);
}
function closeLogin() { document.getElementById('login-modal').classList.remove('on'); }
async function doLogin() {
    const email = document.getElementById('lg-email').value.trim();
    const pw = document.getElementById('lg-pw').value;
    const err = document.getElementById('lg-err');
    if (!email || !pw) { err.textContent = '이메일과 비밀번호를 모두 입력해 주세요.'; return; }
    const btn = document.getElementById('lg-btn');
    btn.disabled = true; btn.textContent = '확인 중…';
    try {
        await sbLogin(email, pw);
        closeLogin();
        syncAuthUI();
        await pullWorkspace();            // 로그인 시 서버 작업공간 가져오기(없으면 내 씬을 올림)
        await loadEquipmentFromServer();
        switchMode(currentScene().mode || 'list');
        renderSceneSelect(); renderList(); renderPalette(); renderScenePane();
        setStatus(`${authEmail()} 로 로그인했습니다 — 이제 장비를 수정할 수 있어요`);
    } catch (e) {
        err.textContent = e.message;
    } finally {
        btn.disabled = false; btn.textContent = '로그인';
    }
}
function syncAuthUI() {
    const b = document.getElementById('auth-chip');
    if (!b) return;
    if (isLoggedIn()) {
        b.innerHTML = `<span class="ac-dot on"></span>${esc(authEmail().split('@')[0])}`;
        b.title = authEmail() + ' — 눌러서 로그아웃';
        b.onclick = () => { if (confirm('로그아웃할까요?\n로그아웃하면 장비를 수정할 수 없습니다.')) sbLogout(); };
    } else {
        b.innerHTML = `<span class="ac-dot"></span>로그인`;
        b.title = '스튜디오 계정으로 로그인';
        b.onclick = openLogin;
    }
    b.style.display = 'inline-flex';
}
// 수정하려 할 때 로그인 확인
function requireLogin(what) {
    if (isLoggedIn()) return true;
    setStatus(`${what || '수정'}하려면 로그인이 필요합니다`);
    openLogin();
    return false;
}

// ═══════════════════════════════════════════════════
//  사진으로 장비 불러오기 (화이트보드 · 손글씨 목록)
// ═══════════════════════════════════════════════════
let photoResult = null;
function pickGearPhoto() {
    const inp = document.createElement('input');
    inp.type = 'file'; inp.accept = 'image/*';
    inp.onchange = () => {
        const f = inp.files && inp.files[0];
        if (!f) return;
        const rd = new FileReader();
        rd.onload = () => downscaleImage(rd.result, (data) => sendGearPhoto(data));
        rd.readAsDataURL(f);
    };
    inp.click();
}
async function sendGearPhoto(dataUrl) {
    const box = document.getElementById('photo-modal');
    const body = document.getElementById('photo-body');
    box.classList.add('on');
    document.getElementById('photo-preview').src = dataUrl;
    body.innerHTML = `<div class="ph-wait"><div class="ph-spin"></div>
        사진을 읽는 중입니다… 손글씨는 10~20초쯤 걸려요.</div>`;
    const c = sbCfg();
    const eqList = EQUIPMENT.map(e => ({ id: e.id, product: e.product, nick: e.nick, cat: e.cat }));
    try {
        const r = await fetch(c.url + '/functions/v1/read-gear-photo', {
            method: 'POST',
            headers: sbHeaders(c.anon),
            body: JSON.stringify({ image: dataUrl, equipment: eqList }),
        });
        if (r.status === 404) {
            body.innerHTML = `<div class="ph-err"><b>사진 인식 기능은 아직 설치 전입니다</b>
                <div>공유 기능만 먼저 켜 둔 상태예요.</div>
                <div class="ph-hint">쓰려면 Supabase 에 <code>read-gear-photo</code> 함수를 올려야 합니다.
                  설치 안내서 3단계를 참고하세요.</div></div>`;
            return;
        }
        const out = await r.json();
        if (!r.ok) {
            const msg = String(out.error || '');
            if (/ANTHROPIC_API_KEY/.test(msg)) {
                body.innerHTML = `<div class="ph-err"><b>분석 키가 설정되지 않았습니다</b>
                    <div>서버에 <code>ANTHROPIC_API_KEY</code> 를 넣어주세요.</div></div>`;
                return;
            }
            if (/credit|billing|quota/i.test(msg)) {
                body.innerHTML = `<div class="ph-err"><b>분석 크레딧이 부족합니다</b>
                    <div>Anthropic 콘솔에서 크레딧을 충전해 주세요.</div></div>`;
                return;
            }
            throw new Error(msg || `서버 오류 ${r.status}`);
        }
        photoResult = out;
        renderPhotoResult(out);
    } catch (e) {
        body.innerHTML = `<div class="ph-err"><b>읽지 못했습니다</b>
            <div>${esc(e.message)}</div>
            <div class="ph-hint">글씨가 잘 보이게 다시 찍거나, 조명 반사를 줄여보세요.</div></div>`;
    }
}
function renderPhotoResult(out) {
    const body = document.getElementById('photo-body');
    const m = out.matched || [], u = out.unmatched || [];
    if (!m.length && !u.length) {
        body.innerHTML = `<div class="ph-err"><b>장비를 찾지 못했습니다</b>
            <div class="ph-hint">장비 목록이 적힌 부분이 잘 보이게 찍어주세요.</div></div>`;
        return;
    }
    let h = '';
    if (out.note) h += `<div class="ph-note">${esc(out.note)}</div>`;
    h += `<div class="ph-sec">찾은 장비 <b>${m.length}개</b> — 체크된 것만 담습니다</div>`;
    m.forEach((x, i) => {
        const eq = EQUIPMENT.find(e => e.id === x.eqId);
        if (!eq) return;
        const conf = typeof x.confidence === 'number' ? x.confidence : 1;
        const low = conf < 0.7;
        h += `<label class="ph-row${low ? ' low' : ''}">
            <input type="checkbox" class="lchk" data-i="${i}" ${low ? '' : 'checked'}>
            <span class="ph-id">${eq.id}</span>
            <span class="ph-nm">${esc(dispName(eq))}</span>
            <span class="ph-src">${esc(x.line || '')}</span>
            ${low ? '<span class="ph-warn">확인 필요</span>' : ''}
        </label>`;
    });
    if (u.length) {
        h += `<div class="ph-sec">못 찾은 것 <b>${u.length}개</b> — 목록에 없거나 읽기 어려웠어요</div>`;
        u.forEach(x => {
            h += `<div class="ph-row miss"><span class="ph-nm">${esc(x.line || '')}</span>
                  <span class="ph-src">${esc(x.reason || '')}</span></div>`;
        });
    }
    body.innerHTML = h;
}
function photoChecked() {
    const m = (photoResult && photoResult.matched) || [];
    return [...document.querySelectorAll('#photo-body input[data-i]')]
        .filter(el => el.checked)
        .map(el => m[+el.dataset.i])
        .filter(Boolean)
        .map(x => x.eqId);
}
function photoToSet() {
    const ids = photoChecked();
    if (!ids.length) { alert('담을 장비를 하나 이상 선택해 주세요.'); return; }
    const name = prompt(`선택한 ${ids.length}개를 세트로 저장합니다.\n세트 이름을 입력하세요.`,
        '사진에서 불러온 세트');
    if (!name) return;
    state.sets = state.sets || {};
    const sid = 'set_' + Date.now().toString(36);
    state.sets[sid] = { name: name.trim(), eqIds: [...new Set(ids)] };
    saveState();
    closePhoto(); renderPalette();
    if (typeof renderSets === 'function') renderSets();
    setStatus(`"${name.trim()}" 세트에 ${ids.length}개를 저장했습니다`);
}
function photoToLayout() {
    const ids = photoChecked();
    if (!ids.length) { alert('담을 장비를 하나 이상 선택해 주세요.'); return; }
    closePhoto();
    switchMode('layout');
    let n = 0, dup = 0, i = 0;
    [...new Set(ids)].forEach(id => {
        const bid = addBlockAt(id, 60 + (i % 6) * 130, 80 + Math.floor(i / 6) * 110, true);
        if (bid) { n++; i++; } else dup++;
    });
    saveState(); renderCanvas(); renderPalette();
    setStatus(`사진에서 ${n}개를 배치도에 올렸습니다` + (dup ? ` (이미 있는 ${dup}개 제외)` : ''));
}
function closePhoto() { document.getElementById('photo-modal').classList.remove('on'); photoResult = null; }

// ═══════════════════════════════════════════════════
//  장비 목록 화면 — 앱의 중심
// ═══════════════════════════════════════════════════
let listState = { q: '', status: '', sort: 'id', group: false, cat: 'ALL', only: '' };
const listSel = new Set();

// 사용자가 고친 값(별칭·보관위치·상태·비고)은 원본 위에 덮어쓴다
function eqEdits() { return (state.eqEdits = state.eqEdits || {}); }
function applyEqEdits() {
    if (eqIsServer()) return;      // 서버가 원본이면 로컬 수정분은 쓰지 않는다
    const E = eqEdits();
    EQUIPMENT.forEach(eq => {
        const e = E[eq.id];
        eq.loc = eq.loc || '';
        eq.note = eq.note || '';
        if (e) { if (e.nick !== undefined) eq.nick = e.nick;
                 if (e.loc !== undefined) eq.loc = e.loc;
                 if (e.status !== undefined) eq.status = e.status;
                 if (e.note !== undefined) eq.note = e.note; }
    });
}
const EQ_COL = { nick: 'nick', loc: 'location', status: 'status', note: 'note' };
function setEq(id, key, val) {
    if (isViewOnly()) return;
    const eq = EQUIPMENT.find(e => e.id === id);
    if (!eq) return;
    const v = String(val == null ? '' : val).trim();
    const before = eq[key];
    // 서버가 원본이면 로그인해야 고칠 수 있다
    if (eqIsServer()) {
        if (!requireLogin('장비를 수정')) { renderList(); return; }
        eq[key] = v;
        const col = EQ_COL[key];
        if (col) {
            saveEqToServer(id, { [col]: v || null }).catch(e => {
                eq[key] = before;                    // 실패하면 되돌린다
                renderList();
                alert('저장하지 못했습니다.\n\n' + e.message);
            });
        }
        updateListSummary(); renderPalette();
        if (key === 'nick') {
            const md = currentScene().mode;
            if (md === 'floor') renderFloor();
            else if (md === 'layout') renderCanvas();
            else if (md === 'three' && R3) build3D();
        }
        return;
    }
    eq[key] = v;
    const E = eqEdits();
    (E[id] = E[id] || {})[key] = v;
    if (key === 'nick') delete E[id].nickAuto;      // 손대면 '확인됨'
    saveState();
    updateListSummary();
    renderPalette();
    if (key === 'nick') {                       // 별칭은 다른 화면에도 바로 반영
        const md = currentScene().mode;
        if (md === 'floor') renderFloor();
        else if (md === 'layout') renderCanvas();
        else if (md === 'three' && R3) build3D();
    }
}
const STAT_CYCLE = ['정상', '수리필요', '폐기'];
function cycleStatus(id) {
    const eq = EQUIPMENT.find(e => e.id === id);
    if (!eq) return;
    const i = STAT_CYCLE.indexOf(eq.status || '정상');
    setEq(id, 'status', STAT_CYCLE[(i + 1) % STAT_CYCLE.length]);
    renderList();
}
function statClass(st) { return st === '수리필요' ? 'fix' : st === '폐기' ? 'dead' : 'ok'; }

// 필터·정렬을 거친 목록
function listRows() {
    const q = listState.q.trim().toLowerCase();
    let rows = EQUIPMENT.filter(eq => {
        if (listState.cat !== 'ALL' && eq.cat !== listState.cat) return false;
        if (listState.status && (eq.status || '정상') !== listState.status) return false;
        if (listState.only === 'hard' && !hardName(eq)) return false;
        if (listState.only === 'nick' && !eq.nick) return false;
        if (listState.only === 'auto' && !isAutoNick(eq.id)) return false;
        if (listState.only === 'dup' && sameProductCount(eq) < 2) return false;
        if (q) {
            const hay = [eq.id, eq.nick, eq.product, eq.sub, eq.brand, eq.model, eq.loc]
                .filter(Boolean).join(' ').toLowerCase();
            if (!hay.includes(q)) return false;
        }
        return true;
    });
    const ci = c => { const i = CAT_ORDER.indexOf(c); return i < 0 ? 99 : i; };
    const S = {
        id: (a, b) => a.id.localeCompare(b.id),
        cat: (a, b) => ci(a.cat) - ci(b.cat) || a.id.localeCompare(b.id),
        name: (a, b) => (a.product || a.sub || '').localeCompare(b.product || b.sub || ''),
        status: (a, b) => STAT_CYCLE.indexOf(b.status || '정상') - STAT_CYCLE.indexOf(a.status || '정상')
                          || a.id.localeCompare(b.id),
        nick: (a, b) => (b.nick ? 1 : 0) - (a.nick ? 1 : 0) || a.id.localeCompare(b.id)
    };
    return rows.sort(S[listState.sort] || S.id);
}
// 같은 제품끼리 묶기
function groupRows(rows) {
    const m = new Map();
    rows.forEach(eq => {
        const k = (eq.product || eq.sub || eq.id).trim();
        (m.get(k) || m.set(k, []).get(k)).push(eq);
    });
    return [...m.entries()].map(([k, v]) => ({ key: k, items: v }));
}

// ───────── 별칭 자동 제안 ─────────
// 제품명에서 브랜드·군더더기를 걷어내고 현장에서 부를 만한 짧은 이름을 만든다.
const NICK_BRANDS = ['Sony', 'NANLITE', 'Nanlite', 'nanlite', 'Manfrotto', 'manfrotto',
    'Godox', '고독스', 'GenTree', 'RODE', 'Rode', 'SanDisk', 'Samsung', 'Aputure', 'DJI'];
const NICK_WORDS = [
    [/Forza/i, '포르자'], [/PavoTube/i, '파보튜브'], [/Pavoslim/i, '파보슬림'],
    [/PavoSlim/i, '파보슬림'], [/MixPanel/i, '믹스패널'], [/Softbox/i, '소프트박스'],
    [/Umbrella/i, '엄브렐라'], [/Reflector/i, '리플렉터'], [/Battery/i, '배터리'],
    [/Charger/i, '충전기'], [/Monitor/i, '모니터'], [/Tripod/i, '삼각대']
];
// 화면에 뿌릴 이름: 별칭이 있으면 별칭, 없으면 브랜드 뗀 제품명
// (별칭은 '이름이 어려울 때만' 쓰는 보조 수단)
function dispName(eq) {
    if (!eq) return '?';
    return eq.nick || suggestNick(eq) || eq.id;
}
// 이름만으로 알아듣기 어려운 장비인지 (별칭이 필요한 후보)
function hardName(eq) {
    if (eq.nick) return false;                       // 이미 별칭이 있으면 끝
    const bare = suggestNick(eq);
    if (!bare) return true;                          // 이름 자체가 없음
    if (/[가-힣]/.test(bare)) return false;           // 한글 이름은 부르기 쉬움
    // 렌즈 화각·조리개 표기(24-70 F2.8 GM)는 현장에서 그대로 쓰는 이름
    if (/^\d+(\s*-\s*\d+)?\s*(mm)?\s*(F[\d.]+)?/i.test(bare) && /F[\d.]/i.test(bare)) return false;
    // 부품번호처럼 생긴 토막: 글자+숫자+글자 (MVK504XTWINFA, TSN6CF-Q, AD300Pro)
    return bare.split(/\s+/).some(w =>
        /[A-Za-z]{2,}\d{1,4}[A-Za-z]/.test(w) || w.length >= 10);
}
let _spc = null;
function sameProductCount(eq) {
    if (!_spc) {
        _spc = {};
        EQUIPMENT.forEach(e => { const k = (e.product || e.sub || '').trim();
            _spc[k] = (_spc[k] || 0) + 1; });
    }
    return _spc[(eq.product || eq.sub || '').trim()] || 1;
}
function suggestNick(eq) {
    let t = String(eq.product || eq.sub || '').trim();
    NICK_BRANDS.forEach(b => { t = t.replace(new RegExp('^' + b + '\\s*', 'i'), ''); });
    NICK_WORDS.forEach(([re, ko]) => { t = t.replace(re, ko); });
    t = t.replace(/\[[^\]]*\]/g, ' ').replace(/\([^)]*\)/g, ' ');   // [10m] (구형) 같은 부가정보 제거
    t = t.replace(/\s{2,}/g, ' ').replace(/^[-·,]\s*/, '').trim();
    if (!t) t = eq.sub || eq.id;
    if (t.length > 20) {                       // 아주 긴 것만, 단어 중간에서 자르지 않는다
        const cut = t.slice(0, 21);
        const sp = cut.lastIndexOf(' ');
        t = (sp > 8 ? cut.slice(0, sp) : t.slice(0, 20)).trim();
    }
    return t;
}
function suggestAllNicks() {
    const targets = EQUIPMENT.filter(hardName);
    if (!targets.length) { setStatus('별칭이 필요해 보이는 장비가 없습니다'); return; }
    if (!confirm(`이름만으로 알아듣기 어려운 ${targets.length}개에만 별칭 초안을 답니다.\n`
        + `(긴 모델번호 · 같은 제품이 여러 대라 구분이 필요한 것)\n\n`
        + `나머지 ${EQUIPMENT.length - targets.length}개는 제품명 그대로 부르면 되니 비워 둡니다.`)) return;
    // 같은 이름이 여러 개면 뒤에 번호를 붙인다
    const byName = {};
    targets.forEach(e => { const n = suggestNick(e); (byName[n] = byName[n] || []).push(e); });
    const E = eqEdits();
    let n = 0;
    Object.entries(byName).forEach(([base, list]) => {
        list.forEach((eq, i) => {
            const nick = list.length > 1 ? `${base} ${i + 1}` : base;
            eq.nick = nick;
            (E[eq.id] = E[eq.id] || {}).nick = nick;
            E[eq.id].nickAuto = true;         // 확인 필요 표시
            n++;
        });
    });
    saveState(); renderList(); renderPalette();
    setStatus(`${n}개에 별칭 초안을 채웠습니다 — 실제로 부르는 이름으로 고쳐주세요`);
}
function clearAutoNicks() {
    const E = eqEdits();
    let n = 0;
    EQUIPMENT.forEach(eq => {
        if (E[eq.id] && E[eq.id].nickAuto) { eq.nick = ''; delete E[eq.id]; n++; }
    });
    saveState(); renderList(); renderPalette();
    setStatus(`자동 제안 별칭 ${n}개를 지웠습니다`);
}
function isAutoNick(id) { const E = state.eqEdits || {}; return !!(E[id] && E[id].nickAuto); }
function autoNickCount() { return EQUIPMENT.filter(e => isAutoNick(e.id)).length; }

function updateListSummary() {
    const el = document.getElementById('list-summary');
    if (!el) return;
    const all = EQUIPMENT.length;
    const fix = EQUIPMENT.filter(e => e.status === '수리필요').length;
    const dead = EQUIPMENT.filter(e => e.status === '폐기').length;
    const hard = EQUIPMENT.filter(hardName).length;
    const noLoc = EQUIPMENT.filter(e => !e.loc).length;
    const nick = EQUIPMENT.filter(e => e.nick).length;
    const cards = [
        { k: '전체 장비', v: all, act: "listState.cat='ALL';listState.status='';listState.q='';listState.only='';syncListTools();renderList()" },
        { k: '수리 필요', v: fix, cls: fix ? 'warn' : '', act: "listState.only='';listState.status='수리필요';syncListTools();renderList()" },
        { k: '폐기', v: dead, act: "listState.only='';listState.status='폐기';syncListTools();renderList()" },
        { k: '별칭 붙은 것', v: nick, act: "listState.only='nick';listState.q='';syncListTools();renderList()" },
        { k: '이름 어려움', v: hard, cls: hard ? 'warn' : '',
          act: "listState.only='hard';listState.q='';listState.status='';syncListTools();renderList()" },
        { k: '보관위치 없음', v: noLoc, cls: noLoc ? 'gap' : '', act: "listState.only='';listState.sort='id';renderList()" },
        { k: '같은 제품 여러 대', v: EQUIPMENT.filter(e => sameProductCount(e) > 1).length,
          act: "listState.only='dup';listState.group=true;listState.q='';syncListTools();renderList()" }
    ];
    const auto = autoNickCount();
    if (auto) cards.push({ k: '별칭 확인 필요', v: auto, cls: 'warn',
        act: "listState.only='auto';listState.q='';syncListTools();renderList()" });
    const src = eqIsServer()
        ? (isLoggedIn() ? { t: '서버 · 수정 가능', c: '' } : { t: '서버 · 보기만', c: 'warn' })
        : { t: '이 브라우저', c: '' };
    el.innerHTML = cards.map(c =>
        `<div class="lsum ${c.cls || ''}" onclick="${c.act}">
           <span class="k">${c.k}</span><span class="v">${c.v}</span></div>`).join('')
        + `<div class="lsum src ${src.c}" onclick="${!isLoggedIn() ? 'openLogin()' : ''}">
             <span class="k">데이터</span><span class="vs">${src.t}</span></div>`;
}
function syncListTools() {
    const q = document.getElementById('lq'), st = document.getElementById('lst'),
          so = document.getElementById('lsort'), gp = document.getElementById('lgrp');
    if (q) q.value = listState.q;
    if (st) st.value = listState.status;
    if (so) so.value = listState.sort;
    if (gp) gp.classList.toggle('on', listState.group);
    const t = document.getElementById('lsel-tools'), n = document.getElementById('lsel-n');
    if (t) t.style.display = listSel.size ? 'inline-flex' : 'none';
    if (n) n.textContent = `${listSel.size}개 선택`;
}

function renderList() {
    const body = document.getElementById('list-body');
    if (!body) return;
    updateListSummary();
    syncListTools();
    const rows = listRows();
    if (!rows.length) {
        body.innerHTML = `<div class="lempty"><b>조건에 맞는 장비가 없어요</b>
            검색어나 필터를 바꿔보세요.</div>`;
        return;
    }
    const TH = [['', ''], ['자산번호', 'id'], ['화면에 뜨는 이름 / 정식 제품명', 'name'], ['별칭 (어려울 때만)', 'nick'],
                ['카테고리', 'cat'], ['상태', 'status'], ['보관위치', ''], ['비고', ''], ['', '']];
    let h = `<table class="ltable"><thead><tr>
        <th><input type="checkbox" class="lchk" ${allChecked(rows) ? 'checked' : ''}
             onchange="toggleAll(this.checked)"></th>`;
    TH.slice(1).forEach(([lab, key]) => {
        const ar = key && listState.sort === key ? '<span class="ar">▾</span>' : '';
        h += `<th ${key ? `onclick="listState.sort='${key}';renderList()"` : ''}>${lab}${ar}</th>`;
    });
    h += `</tr></thead><tbody>`;

    if (listState.group) {
        groupRows(rows).forEach(g => {
            const first = g.items[0];
            h += rowHTML(first, g.items.length > 1 ? g.items.length : 0, g.items);
            if (g.items.length > 1 && listSel.has(first.id) === false) {
                g.items.slice(1).forEach(eq => { h += rowHTML(eq, 0, null, true); });
            }
        });
    } else {
        rows.forEach(eq => { h += rowHTML(eq); });
    }
    body.innerHTML = h + `</tbody></table>`;
}
function rowHTML(eq, qty, group, isSub) {
    const col = CAT_COLORS[eq.cat] || '#888';
    const st = eq.status || '정상';
    const sel = listSel.has(eq.id) ? ' sel' : '';
    const dim = st === '폐기' ? ' dim' : '';
    return `<tr class="lrow${sel}${dim}${isSub ? ' lsub' : ''}" data-id="${eq.id}">
        <td><input type="checkbox" class="lchk" ${listSel.has(eq.id) ? 'checked' : ''}
             onchange="toggleSel('${eq.id}',this.checked)"></td>
        <td class="lid">${eq.id}</td>
        <td><div class="lnamecell">
            <div class="licon" style="background:${col}22">${iconSvgFor(eq)}</div>
            <div style="min-width:0">
                <div class="lname">${esc(dispName(eq))}
                    ${qty ? `<span class="lqty">×${qty}</span>` : ''}
                    ${eq.nick ? '<span class="lnk-tag">별칭</span>' : ''}
                    ${hardName(eq) ? '<span class="lhard" title="모델번호라 부르기 어려워 보여요 — 별칭을 붙이면 좋습니다">?</span>' : ''}</div>
                <div class="lfull">${esc(eq.product || eq.sub || '')}${eq.brand ? ' · ' + esc(eq.brand) : ''}</div>
            </div>
        </div></td>
        <td><input class="ledit${eq.nick ? (isAutoNick(eq.id) ? ' auto' : '') : ' empty'}"
             value="${esc(eq.nick || '')}" placeholder="현장에서 부르는 이름"
             title="${isAutoNick(eq.id) ? '자동 제안 — 실제로 부르는 이름인지 확인하세요' : ''}"
             onchange="setEq('${eq.id}','nick',this.value)"></td>
        <td class="lcat-tag">${CAT_NAMES[eq.cat] || eq.cat}</td>
        <td><button class="lstat ${statClass(st)}" onclick="cycleStatus('${eq.id}')"
             title="눌러서 상태 변경">${st}</button></td>
        <td><input class="ledit${eq.loc ? '' : ' empty'}" value="${esc(eq.loc || '')}"
             placeholder="선반 A-2 · 케이스 1"
             onchange="setEq('${eq.id}','loc',this.value)"></td>
        <td><input class="ledit" value="${esc(eq.note || '')}" placeholder="—"
             onchange="setEq('${eq.id}','note',this.value)"></td>
        <td class="lact">${eqIsServer() && isLoggedIn()
            ? `<button class="lx" title="목록에서 내리기" onclick="retireEquipment('${eq.id}')">×</button>` : ''}</td>
    </tr>`;
}
function allChecked(rows) { return rows.length > 0 && rows.every(r => listSel.has(r.id)); }
function toggleSel(id, on) { on ? listSel.add(id) : listSel.delete(id); renderList(); }
function toggleAll(on) {
    listRows().forEach(r => on ? listSel.add(r.id) : listSel.delete(r.id));
    renderList();
}
// 선택 → 세트 저장
function selToSet() {
    if (!listSel.size) return;
    const name = prompt(`선택한 ${listSel.size}개를 세트로 저장합니다.\n세트 이름을 입력하세요.`,
        '새 세트');
    if (!name) return;
    state.sets = state.sets || {};
    const id = 'set_' + Date.now().toString(36);
    state.sets[id] = { name: name.trim(), eqIds: [...listSel] };
    saveState();
    listSel.clear();
    renderList(); renderPalette();
    if (typeof renderSets === 'function') renderSets();
    setStatus(`"${name.trim()}" 세트에 ${state.sets[id].eqIds.length}개를 저장했습니다`);
}
// 선택 → 배치도로
function selToLayout() {
    if (!listSel.size) return;
    const ids = [...listSel];
    listSel.clear();
    switchMode('layout');
    let n = 0, dup = 0, i = 0;
    ids.forEach(eqId => {
        const bid = addBlockAt(eqId, 60 + (i % 6) * 130, 80 + Math.floor(i / 6) * 110, true);
        if (bid) { n++; i++; } else dup++;
    });
    saveState(); renderCanvas(); renderPalette(); syncFromLayout(false);
    setStatus(`${n}개를 배치도에 올렸습니다 (평면도·3D에도 반영)` + (dup ? ` (이미 있는 ${dup}개 제외)` : ''));
}
// 엑셀 마스터에 반영할 '고친 것만' 뽑기
// (구매일·가격처럼 앱이 모르는 열을 덮어쓰지 않도록 앱이 관리하는 열만 내보낸다)
function exportChangesCSV() {
    const E = state.eqEdits || {};
    const ids = Object.keys(E);
    if (!ids.length) { alert('아직 고친 내용이 없습니다.'); return; }
    const head = ['자산번호', '별칭', '상태', '보관위치', '비고'];
    const esc2 = v => `"${String(v == null ? '' : v).replace(/"/g, '""')}"`;
    const body = ids.map(id => {
        const eq = EQUIPMENT.find(e => e.id === id);
        return eq ? [eq.id, eq.nick, eq.status, eq.loc, eq.note].map(esc2).join(',') : null;
    }).filter(Boolean);
    const csv = '\ufeff' + [head.map(esc2).join(','), ...body].join('\r\n');
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    a.download = `EH_변경분_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    setStatus(`고친 ${body.length}개 항목만 내보냈습니다 — 엑셀 마스터에 반영하세요`);
}
// CSV 내보내기 (엑셀에서 바로 열림)
function exportListCSV() {
    const rows = listRows();
    const head = ['자산번호', '카테고리', '세부분류', '제품명', '별칭', '브랜드', '모델명', '상태', '보관위치', '비고'];
    const esc2 = v => `"${String(v == null ? '' : v).replace(/"/g, '""')}"`;
    const body = rows.map(e => [e.id, CAT_NAMES[e.cat] || e.cat, e.sub, e.product, e.nick,
        e.brand, e.model, e.status || '정상', e.loc, e.note].map(esc2).join(','));
    const csv = '﻿' + [head.map(esc2).join(','), ...body].join('\r\n');
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    a.download = `EH_장비리스트_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    setStatus(`${rows.length}개를 CSV로 내보냈습니다`);
}

// ───────── 렌더 ─────────
// ───────── 평면도 라벨 레이어 ─────────
// 텍스트를 scale(zoom) 밖 화면 픽셀 좌표로 그린다.
// (미터 단위 폰트는 브라우저가 서브픽셀로 뭉개서 글자가 겹쳐 보임)
const CJK = /[\u1100-\u11FF\u2E80-\u9FFF\uA960-\uA97F\uAC00-\uD7FF\uFF00-\uFFEF]/;
function labelW(t, fs) {
    let w = 0;
    for (const ch of String(t)) w += CJK.test(ch) ? fs : fs * 0.55;
    return w;
}
// 우선순위가 높은 라벨부터 자리를 잡고, 겹치면 위아래로 밀고, 그래도 겹치면 숨김
function layoutLabels(LB, z) {
    const put = [], out = [];
    LB.sort((a, b) => b.pri - a.pri);
    for (const L of LB) {
        const fs = L.fs;
        let w = labelW(L.t, fs) + 9, h = fs + 7;
        if (L.rot) { const t = w; w = h; h = t; }
        const px = L.x * z, py = L.y * z;
        const bx0 = L.anchor === 'start' ? px : px - w / 2;
        let bx = bx0, by = 0, ok = false;
        const tries = L.fixed ? [0] : [0, h + 2, -(h + 2), 2 * h + 4, -(2 * h + 4), 3 * h + 6];
        for (const dy of tries) {
            by = py + dy - h / 2;
            if (!put.some(r => bx < r.x + r.w && bx + w > r.x && by < r.y + r.h && by + h > r.y)) { ok = true; break; }
        }
        if (!ok) continue;
        put.push({ x: bx, y: by, w, h });
        out.push(Object.assign({}, L, { bx, by, w, h }));
    }
    return out;
}
function labelSVG(LB, z) {
    let s = '<g class="flabels" style="pointer-events:none">';
    for (const L of layoutLabels(LB, z)) {
        const cx = L.bx + L.w / 2, cy = L.by + L.h / 2 + L.fs * 0.35;
        if (L.pill !== false)
            s += `<rect x="${L.bx.toFixed(1)}" y="${L.by.toFixed(1)}" width="${L.w.toFixed(1)}"
                   height="${L.h.toFixed(1)}" rx="5" fill="#0b0f14" fill-opacity="${L.pill === 'soft' ? 0.55 : 0.78}"/>`;
        const rot = L.rot ? ` transform="rotate(${L.rot} ${cx.toFixed(1)} ${cy.toFixed(1)})"` : '';
        s += `<text x="${cx.toFixed(1)}" y="${cy.toFixed(1)}" text-anchor="middle"
               font-size="${L.fs}" fill="${L.fill}" font-weight="${L.bold ? 650 : 500}"${rot}>${esc(L.t)}</text>`;
    }
    return s + '</g>';
}

// 방이 바뀌면 밖으로 나간 장비를 안으로 데려온다
// 툴바에서 방 크기 바꾸기 (사각형 방만)
function setRoomSize(k, v) {
    const f = F(), r = activeRoom(f);
    if (!r) { alert('방이 없습니다. 공간 도구에서 먼저 만들어주세요.'); return; }
    if (r.type === 'poly') { alert('다각형 방은 꼭짓점을 끌어서 조절해주세요.'); return; }
    const val = Math.max(1, Math.min(k === 'w' ? WORLD_W : WORLD_H, parseFloat(v) || 1));
    r[k] = +val.toFixed(2);
    const n = reconfineAll();
    saveState(); syncRoomUI();
    if (currentScene().mode === 'three' && R3) { build3D(); showSel(); } else renderFloor();
    setStatus(`방 ${r.w.toFixed(2)} × ${r.h.toFixed(2)}m (${(r.w * r.h).toFixed(2)}㎡)`
        + (n ? ` · 밖에 있던 ${n}개를 안으로 옮겼습니다` : ''));
}
function syncRoomUI() {
    const r = activeRoom();
    const rect = r && r.type !== 'poly';
    [['rm-w', 'w'], ['rm-w2', 'w'], ['rm-h', 'h'], ['rm-h2', 'h']].forEach(([id, k]) => {
        const el = document.getElementById(id);
        if (el) { el.value = rect ? r[k].toFixed(2) : ''; el.disabled = !rect; }
    });
    syncConfineBtn();
}
function reconfineAll() {
    const f = F();
    if (!f.confine || !activeRoom(f)) return 0;
    let n = 0;
    Object.values(f.items).forEach(it => { if (confineItem(it)) n++; });
    (f.subjects || []).forEach(sj => { if (confineSubject(sj)) n++; });
    if (n) saveState();
    return n;
}
function renderFloor() {
    const f = F();
    const z = f.zoom;
    const svg = document.getElementById('floor-svg');
    svg.setAttribute('width', WORLD_W * z);
    svg.setAttribute('height', WORLD_H * z);

    let s = `<g transform="scale(${z})">`;
    const LB = [];   // 라벨 (미터 좌표로 push → 마지막에 픽셀 레이어로 렌더)

    // 배경 도면
    if (f.bg) {
        s += `<image class="fbg" href="${f.bg.data}" x="${f.bg.x}" y="${f.bg.y}"
               width="${f.bg.w}" height="${f.bg.h}"
               opacity="${f.bg.opacity}" preserveAspectRatio="none"
               style="${bgMove ? 'cursor:move;pointer-events:auto' : 'pointer-events:none'}"/>`;
        if (bgMove) {
            s += `<rect class="bg-frame" x="${f.bg.x}" y="${f.bg.y}" width="${f.bg.w}" height="${f.bg.h}"
                   fill="none" stroke="#ff9166" stroke-width="0.05" stroke-dasharray="0.2 0.14"/>`;
            s += `<circle class="bg-handle" cx="${f.bg.x + f.bg.w}" cy="${f.bg.y + f.bg.h}" r="0.16"
                   fill="#ff9166" stroke="#fff" stroke-width="0.03"/>`;
            LB.push({ x: f.bg.x + f.bg.w / 2, y: f.bg.y - 0.2, fs: 11.5, fill: '#ffb089', pri: 8,
                      t: `도면 ${f.bg.w.toFixed(2)} × ${f.bg.h.toFixed(2)} m` });
        }
    }

    // 1m 격자
    for (let i = 0; i <= WORLD_W; i++)
        s += `<line class="grid-line${i % 5 === 0 ? ' major' : ''}" x1="${i}" y1="0" x2="${i}" y2="${WORLD_H}"/>`;
    for (let i = 0; i <= WORLD_H; i++)
        s += `<line class="grid-line${i % 5 === 0 ? ' major' : ''}" x1="0" y1="${i}" x2="${WORLD_W}" y2="${i}"/>`;

    // 방
    f.rooms.forEach(r => {
        const isSel = floorSel && floorSel.type === 'room' && floorSel.id === r.id;
        const sel = isSel ? ' sel' : '';
        if (r.type === 'poly') {
            const pd = r.pts.map(p => `${p.x},${p.y}`).join(' ');
            s += `<polygon class="froom${sel}" data-room="${r.id}" transform="translate(${r.x},${r.y})" points="${pd}"/>`;
            const c = roomCentroid(r);
            LB.push({ x: c.x, y: c.y, fs: 13, fill: '#a8ccff', bold: true, pri: 7, t: r.name });
            LB.push({ x: c.x, y: c.y + 0.34, fs: 11, fill: '#8792a2', pri: 3, pill: 'soft',
                      t: `${roomArea(r).toFixed(2)}㎡` });
            for (let i = 0; i < r.pts.length; i++) {
                const a = r.pts[i], b = r.pts[(i + 1) % r.pts.length];
                const len = Math.hypot(b.x - a.x, b.y - a.y);
                if (len < 0.25) continue;
                const mx = r.x + (a.x + b.x) / 2, my = r.y + (a.y + b.y) / 2;
                // 변에 수직으로 살짝 바깥에 표기
                const nx = -(b.y - a.y) / len, ny = (b.x - a.x) / len;
                LB.push({ x: mx + nx * 0.26, y: my + ny * 0.26, fs: 11.5, fill: '#cfe0ff', pri: 5,
                          t: `${len.toFixed(2)}m` });
            }
            if (isSel) r.pts.forEach((p, i) =>
                s += `<circle class="vhandle" data-vroom="${r.id}" data-vidx="${i}" cx="${r.x + p.x}" cy="${r.y + p.y}" r="0.13"/>`);
        } else {
            s += `<rect class="froom${sel}" data-room="${r.id}" x="${r.x}" y="${r.y}" width="${r.w}" height="${r.h}"/>`;
            LB.push({ x: r.x + 0.16, y: r.y + 0.34, fs: 13, fill: '#a8ccff', bold: true,
                      anchor: 'start', pri: 7, t: r.name });
            LB.push({ x: r.x + r.w / 2, y: r.y - 0.2, fs: 11.5, fill: '#cfe0ff', pri: 6, fixed: true,
                      t: `${r.w.toFixed(2)}m` });
            LB.push({ x: r.x - 0.24, y: r.y + r.h / 2, fs: 11.5, fill: '#cfe0ff', pri: 6, rot: -90, fixed: true,
                      t: `${r.h.toFixed(2)}m` });
            LB.push({ x: r.x + r.w / 2, y: r.y + r.h - 0.3, fs: 11, fill: '#8792a2', pri: 3, pill: 'soft',
                      t: `${(r.w * r.h).toFixed(2)}㎡` });
            if (isSel) {
                const hs = [[r.x, r.y], [r.x + r.w, r.y], [r.x + r.w, r.y + r.h], [r.x, r.y + r.h]];
                hs.forEach((p, i) =>
                    s += `<circle class="vhandle" data-rrect="${r.id}" data-ridx="${i}" cx="${p[0]}" cy="${p[1]}" r="0.13"/>`);
            }
        }
    });

    // 장비
    for (const [fid, it] of Object.entries(f.items)) {
        const eq = EQUIPMENT.find(e => e.id === it.eqId);
        if (!eq) continue;
        const sz = itemSize(it);
        const col = CAT_COLORS[eq.cat] || '#888';
        const sel = ((floorSel && floorSel.type === 'item' && floorSel.id === fid) || fMulti.has(fid)) ? ' sel' : '';
        const label = it.label || dispName(eq);
        s += `<g class="fitem${sel}" data-fid="${fid}" transform="translate(${it.x},${it.y}) rotate(${it.rot || 0})">`;
        if (f.showClear) {
            const cr = Math.max(sz.w, sz.h) / 2 + sz.clear;
            s += `<circle class="clr" r="${cr}" fill="${col}" stroke="${col}"/>`;
        }
        if (sz.shape === 'circle')
            s += `<circle class="fp" r="${Math.max(sz.w, sz.h) / 2}" fill="${col}" fill-opacity="0.75" stroke="${col}"/>`;
        else
            s += `<rect class="fp" x="${-sz.w / 2}" y="${-sz.h / 2}" width="${sz.w}" height="${sz.h}" rx="0.04"
                   fill="${col}" fill-opacity="0.75" stroke="${col}"/>`;
        // 인포그래픽 아이콘 (발자국 크기에 맞춰 축소)
        const im = Math.min(0.62, Math.max(0.2, Math.min(sz.w, sz.h) * 0.82));
        const k = im / 24;
        s += `<g class="ficon" transform="translate(${-im / 2},${-im / 2}) scale(${k})"
               fill="none" stroke="#0f1216" stroke-opacity="0.9" stroke-width="1.7"
               stroke-linecap="round" stroke-linejoin="round">${iconPathsFor(eq)}</g>`;
        LB.push({ x: it.x, y: it.y + Math.max(sz.h / 2, 0.18) + 0.22, fs: 12, fill: '#e8eef7',
                  pri: 10, t: label });
        // 조립체 부품 표시
        const pts2 = rigParts(it);
        if (pts2.length) {
            const supId = supportOf(it);
            const sub = (supId ? supId.split('-').slice(0, 2).join('-') + ' · ' : '') + `부품 ${pts2.length}`;
            LB.push({ x: it.x, y: it.y + Math.max(sz.h / 2, 0.18) + 0.46, fs: 10, fill: '#8fc0ff',
                      pri: 4, pill: 'soft', t: sub });
            // 조립 표시 링
            s += `<circle r="${Math.max(sz.w, sz.h) / 2 + 0.07}" fill="none" stroke="${col}"
                   stroke-width="0.022" stroke-dasharray="0.08 0.06" opacity="0.85"/>`;
        }
        s += `</g>`;
    }

    // 피사체 (사람)
    for (const sub of (f.subjects || [])) {
        const on = (floorSel && floorSel.type === 'subject' && floorSel.id === sub.id) || fMulti.has(sub.id);
        const c = on ? '#ffffff' : '#64d29a';
        s += `<g class="fsubj" data-subj="${sub.id}">`
           + `<circle cx="${sub.x}" cy="${sub.y}" r="0.28" fill="#64d29a" fill-opacity="0.25" stroke="${c}" stroke-width="0.05"/>`
           + `<circle cx="${sub.x}" cy="${sub.y - 0.08}" r="0.09" fill="${c}"/>`
           + `<path d="M${sub.x - 0.12} ${sub.y + 0.18} q0.12 -0.18 0.24 0" stroke="${c}" stroke-width="0.05" fill="none"/>`
           + `</g>`;
        LB.push({ x: sub.x, y: sub.y + 0.44, fs: 10.5, fill: '#8de3b4', pri: 9, t: `${sub.h.toFixed(2)}m` });
    }

    // 범위 선택 박스
    if (fMq && fMq.box)
        s += `<rect x="${fMq.box.x}" y="${fMq.box.y}" width="${fMq.box.w}" height="${fMq.box.h}"
               fill="rgba(91,157,255,0.12)" stroke="#5b9dff" stroke-width="0.03"/>`;

    // 펜툴 미리보기
    if (floorMode === 'pen' && penPts.length) {
        const d = penPts.map((p, i) => `${i ? 'L' : 'M'}${p.x},${p.y}`).join(' ');
        s += `<path class="pen-line" d="${d}${penPts.length > 2 ? ' Z' : ''}"/>`;
        // 확정된 변 길이
        for (let i = 1; i < penPts.length; i++) {
            const a = penPts[i - 1], b = penPts[i];
            const len = Math.hypot(b.x - a.x, b.y - a.y);
            LB.push({ x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 - 0.16, fs: 11.5, fill: '#cfe0ff', pri: 12,
                      t: `${len.toFixed(2)}m` });
        }
        // 커서까지 고무줄
        if (penCursor) {
            const last = penPts[penPts.length - 1];
            const len = Math.hypot(penCursor.x - last.x, penCursor.y - last.y);
            s += `<line class="pen-rubber" x1="${last.x}" y1="${last.y}" x2="${penCursor.x}" y2="${penCursor.y}"/>`;
            LB.push({ x: (last.x + penCursor.x) / 2, y: (last.y + penCursor.y) / 2 - 0.16, fs: 11.5,
                      fill: '#ffd479', pri: 14, t: `${len.toFixed(2)}m` });
        }
        penPts.forEach((p, i) =>
            s += `<circle class="pen-pt${i === 0 ? ' first' : ''}" cx="${p.x}" cy="${p.y}" r="${i === 0 ? 0.17 : 0.1}"/>`);
        if (penPts.length >= 3) {
            const a = polyArea(penPts);
            const cx = penPts.reduce((t, p) => t + p.x, 0) / penPts.length;
            const cy = penPts.reduce((t, p) => t + p.y, 0) / penPts.length;
            LB.push({ x: cx, y: cy, fs: 11.5, fill: '#8792a2', pri: 11, t: `${a.toFixed(1)}㎡` });
        }
    }

    // 축척 보정 중 표시
    if (calibPts.length === 1)
        s += `<circle cx="${calibPts[0].x}" cy="${calibPts[0].y}" r="0.12" fill="#ff5252"/>`;

    s += `</g>`;
    s += labelSVG(LB, z);
    svg.innerHTML = s;

    // 이벤트 연결
    svg.querySelectorAll('.fitem').forEach(el =>
        el.addEventListener('pointerdown', e => startFloorDrag(e, 'item', el.dataset.fid)));
    svg.querySelectorAll('.froom').forEach(el =>
        el.addEventListener('pointerdown', e => startFloorDrag(e, 'room', el.dataset.room)));
    svg.querySelectorAll('.vhandle').forEach(el =>
        el.addEventListener('pointerdown', e => startVertexDrag(e, el.dataset.vroom, +el.dataset.vidx)));
    svg.querySelectorAll('.fsubj').forEach(el =>
        el.addEventListener('pointerdown', e => startFloorDrag(e, 'subject', el.dataset.subj)));
    svg.querySelectorAll('[data-rrect]').forEach(el =>
        el.addEventListener('pointerdown', e => startRectResize(e, el.dataset.rrect, +el.dataset.ridx)));
    if (bgMove) {
        svg.querySelectorAll('.fbg,.bg-frame').forEach(el =>
            el.addEventListener('pointerdown', e => startFloorDrag(e, 'bg', 'bg')));
        svg.querySelectorAll('.bg-handle').forEach(el =>
            el.addEventListener('pointerdown', e => startBgResize(e)));
    }
    syncBgUI();

    updateFloorStats();
    updateEmptyHints();
    syncRoomUI();
}
function esc(t) {
    return String(t == null ? '' : t).replace(/[&<>"]/g, c =>
        ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

// ───────── 전역 키보드 ─────────
let spaceDown = false;
function isTyping(t) {
    const tag = (t && t.tagName || '').toLowerCase();
    return tag === 'input' || tag === 'textarea' || tag === 'select' || (t && t.isContentEditable);
}
document.addEventListener('keydown', e => {
    if (isTyping(e.target)) return;
    if (e.code === 'Space' && !spaceDown) {
        spaceDown = true;
        e.preventDefault();
        const c = document.getElementById('canvas');
        const fs = document.getElementById('floor-svg');
        if (c) c.classList.add('space');
        if (fs) fs.classList.add('space');
    }
    // 3D: 방향키로 시점 조작
    if (currentScene().mode === 'three' && R3 && nav3D(e)) return;
    // Delete / Backspace → 선택 삭제
    if (e.key === 'Delete' || e.key === 'Backspace') {
        if (isViewOnly()) return;
        const md = currentScene().mode;
        if (md === 'layout' && selectedIds.size) { e.preventDefault(); deleteSelectedBlocks(); }
        else if (md === 'floor' && fMulti.size) { e.preventDefault(); deleteFloorMulti(); }
        else if (md === 'three' && isSubjKey(three3Sel)) {
            e.preventDefault();
            const f2 = ensure3D(currentScene());
            f2.subjects = (f2.subjects || []).filter(x => 's:' + x.id !== three3Sel);
            three3Sel = null; saveState(); build3D(); showSel();
            setStatus('피사체를 삭제했습니다');
        }
    }
});
// ───────── 1인칭 걷기 (게임처럼 공간 안을 이동) ─────────
let walkMode = false;
const keysDown = new Set();
let navLast = 0;
const WALK_KEYS = ['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','KeyW','KeyS','KeyA','KeyD',
                   'KeyQ','KeyE','PageUp','PageDown','ShiftLeft','ShiftRight'];
function toggleWalk(on) {
    if (!R3) return;
    walkMode = on === undefined ? !walkMode : !!on;
    const f = ensure3D(currentScene());
    if (walkMode) {
        // 지금 보고 있는 시점에서 그대로 걸어 들어간다
        const o = R3.orbit;
        R3.walk = {
            x: o.tx - Math.sin(o.theta) * Math.min(o.dist * 0.55, 3.5),
            z: o.tz - Math.cos(o.theta) * Math.min(o.dist * 0.55, 3.5),
            eye: Math.min(1.65, (f.ceilH || 2.7) - 0.25),
            yaw: o.theta + Math.PI / 2,
            pitch: -(o.phi - Math.PI / 2) * 0.5
        };
        R3.walk.x = Math.max(0.2, Math.min(WORLD_W - 0.2, R3.walk.x));
        R3.walk.z = Math.max(0.2, Math.min(WORLD_H - 0.2, R3.walk.z));
        setStatus('1인칭 모드 — ↑↓ 또는 W/S 전진·후진 · ←→ 방향 전환 · A/D 옆걸음 · Q/E 시선 높이 · 드래그로 둘러보기');
    } else {
        // 걷던 자리를 중심으로 다시 내려다보기
        const w = R3.walk;
        if (w) {
            const o = R3.orbit;
            o.theta = w.yaw - Math.PI / 2;
            o.phi = 1.05; o.dist = 8;
            o.tx = w.x + Math.sin(w.yaw) * 3.5;
            o.tz = w.z - Math.cos(w.yaw) * 3.5;
            o.ty = 1.2;
        }
        setStatus('둘러보기 모드로 돌아왔습니다');
    }
    keysDown.clear();
    const b = document.getElementById('walk-btn');
    if (b) { b.classList.toggle('on', walkMode); b.textContent = walkMode ? '🚶 1인칭 (켜짐)' : '🚶 1인칭'; }
    const c = document.getElementById('three-canvas');
    if (c) c.classList.toggle('walking', walkMode);
    updateNavHint();
    saveState();
}
function updateNavHint() {
    const el = document.getElementById('nav-hint');
    if (!el) return;
    el.innerHTML = walkMode
        ? '<b>W/S · ↑↓</b> 전진·후진 &nbsp; <b>A/D</b> 옆걸음 &nbsp; <b>←→</b> 방향 전환 &nbsp; '
        + '<b>Q/E</b> 시선 높이 &nbsp; <b>Shift</b> 빠르게 &nbsp; <b>드래그</b> 둘러보기 &nbsp; <b>V</b> 나가기'
        : '<b>↑↓</b> 앞뒤 이동 &nbsp; <b>←→</b> 방향 전환 &nbsp; <b>A/D</b> 옆걸음 &nbsp; '
        + '<b>Q/E</b> 높이 &nbsp; <b>+/−</b> 줌 &nbsp; <b>Home</b> 전체보기 &nbsp; <b>V</b> 1인칭';
}
// 화면 기준 방향 벡터 (바닥 평면)
//   앞 = 카메라가 바라보는 쪽, 오른쪽 = 화면 오른쪽
function viewBasis(theta) {
    return { fx: -Math.cos(theta), fz: -Math.sin(theta),
             rx:  Math.sin(theta), rz: -Math.cos(theta) };
}
// 매 프레임 이동 처리 (키를 누르고 있으면 계속 움직인다)
function stepNav(dt) {
    if (!R3 || !keysDown.size) return;
    const k = c => keysDown.has(c);
    const fast = k('ShiftLeft') || k('ShiftRight') ? 2.6 : 1;
    const fwd = (k('ArrowUp') || k('KeyW') ? 1 : 0) - (k('ArrowDown') || k('KeyS') ? 1 : 0);
    const side = (k('KeyD') ? 1 : 0) - (k('KeyA') ? 1 : 0);
    const turn = (k('ArrowRight') ? 1 : 0) - (k('ArrowLeft') ? 1 : 0);
    const up = (k('KeyE') || k('PageUp') ? 1 : 0) - (k('KeyQ') || k('PageDown') ? 1 : 0);
    if (!fwd && !side && !turn && !up) return;
    const f = ensure3D(currentScene());
    const ceil = f.ceilH || 2.7;
    if (walkMode) {
        const w = R3.walk;
        const sp = 2.6 * fast * dt;                  // 걷는 속도 m/s
        w.yaw -= turn * 1.9 * dt * fast;
        w.x += (-Math.sin(w.yaw) * fwd + Math.cos(w.yaw) * side) * sp;
        w.z += (-Math.cos(w.yaw) * fwd - Math.sin(w.yaw) * side) * sp;
        w.x = Math.max(0.15, Math.min(WORLD_W - 0.15, w.x));
        w.z = Math.max(0.15, Math.min(WORLD_H - 0.15, w.z));
        w.eye = Math.max(0.25, Math.min(ceil - 0.12, w.eye + up * 1.1 * dt * fast));
    } else {
        const o = R3.orbit;
        const sp = Math.max(1.2, o.dist * 0.42) * fast * dt;
        o.theta += turn * 1.5 * dt * fast;
        // 화면에 보이는 방향 기준으로 시점 전체가 이동
        const b = viewBasis(o.theta);
        o.tx += (b.fx * fwd + b.rx * side) * sp;
        o.tz += (b.fz * fwd + b.rz * side) * sp;
        o.tx = Math.max(-6, Math.min(WORLD_W + 6, o.tx));
        o.tz = Math.max(-6, Math.min(WORLD_H + 6, o.tz));
        o.ty = Math.max(0.1, Math.min(ceil * 3, o.ty + up * 1.4 * dt * fast));
    }
}

// 나머지 단축키 (줌 · 전체보기 · 모드 전환)
function nav3D(e) {
    const o = R3.orbit, K = e.key;
    if (WALK_KEYS.includes(e.code)) {      // 이동키: 누르고 있는 동안 계속 (stepNav)
        keysDown.add(e.code);
        e.preventDefault();
        return true;
    }
    if (K === '+' || K === '=') o.dist = Math.max(1.2, o.dist * 0.88);
    else if (K === '-' || K === '_') o.dist = Math.min(60, o.dist * 1.14);
    else if (K === 'Home') { toggleWalk(false); fitView3D(); }
    else if (K === 'v' || K === 'V') toggleWalk();
    else if (K === 'Escape' && walkMode) toggleWalk(false);
    else return false;
    e.preventDefault();
    return true;
}
// 배치된 장비 전체가 보이도록 시점 맞춤
function fitView3D() {
    const f = ensure3D(currentScene());
    const pts = Object.values(f.items).map(i => [i.x, i.y])
        .concat((f.subjects || []).map(s => [s.x, s.y]));
    if (f.rooms.length) {
        const r = f.rooms[0];
        if (r.type === 'poly') r.pts.forEach(p => pts.push([r.x + p.x, r.y + p.y]));
        else pts.push([r.x, r.y], [r.x + r.w, r.y + r.h]);
    }
    if (!pts.length) return;
    const xs = pts.map(p => p[0]), zs = pts.map(p => p[1]);
    const cx = (Math.min(...xs) + Math.max(...xs)) / 2, cz = (Math.min(...zs) + Math.max(...zs)) / 2;
    const span = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...zs) - Math.min(...zs), 2);
    const o = R3.orbit;
    o.tx = cx; o.tz = cz; o.ty = (f.ceilH || 2.7) * 0.45;
    o.dist = Math.max(3, span * 1.45);
    setStatus('시점을 전체 보기로 맞췄습니다 (Home)');
}

document.addEventListener('keyup', e => {
    keysDown.delete(e.code);
    if (e.code === 'Space') {
        spaceDown = false;
        const c = document.getElementById('canvas');
        const fs = document.getElementById('floor-svg');
        if (c) c.classList.remove('space');
        if (fs) fs.classList.remove('space');
    }
});
window.addEventListener('blur', () => { spaceDown = false; keysDown.clear(); });

function deleteSelectedBlocks() {
    const scene = currentScene();
    const ids = Array.from(selectedIds).filter(id => scene.blocks[id]);
    if (!ids.length) return;
    let total = ids.length;
    ids.forEach(id => total += descendantBlocks(id, scene).length);
    if (total > ids.length && !confirm(`선택한 ${ids.length}개와 하위 부품을 포함해 총 ${total}개를 삭제할까요?`)) return;
    ids.forEach(id => removeBlockTree(id));
    selectedIds.clear();
    saveState(); renderPalette(); renderCanvas();
    const sy = afterLayoutChange();
    setStatus(`${total}개 삭제` + (sy.removed ? ` · 평면도·3D에서도 ${sy.removed}개 내림` : ''));
}

// ───────── 조립 / 분리 ─────────
let rigView = 'nest';           // nest | link | fold
let dragPayload = null;         // {eqId} 또는 {bid}

function setRigView(v) {
    rigView = v;
    state.rigView = v;
    document.querySelectorAll('#rig-view button').forEach(b =>
        b.classList.toggle('primary', b.dataset.v === v));
    const svg = document.getElementById('rig-links');
    if (svg && v !== 'link') svg.innerHTML = '';
    saveState(); renderCanvas();
}
function toggleRigFold(bid, e) {
    e.stopPropagation();
    const b = currentScene().blocks[bid];
    b.folded = !b.folded;
    saveState(); renderCanvas();
}
function hlDrop(el, bid) {
    document.querySelectorAll('.block').forEach(x => x.classList.remove('drop-ok', 'drop-warn'));
    if (!dragPayload) return;
    const scene = currentScene();
    let cat = null;
    if (dragPayload.eqId) {
        const e = EQUIPMENT.find(x => x.id === dragPayload.eqId);
        cat = e && e.cat;
    } else if (dragPayload.bid) {
        if (dragPayload.bid === bid || isAncestor(dragPayload.bid, bid, scene)) return;
        const e = eqOfBlock(dragPayload.bid, scene);
        cat = e && e.cat;
    }
    if (!cat) return;
    const r = acceptSlot(bid, cat, scene);
    el.classList.add(r ? (r.ok ? 'drop-ok' : 'drop-warn') : 'drop-warn');
}
function dropOnBlock(bid, e) {
    if (isViewOnly()) return;               // 공유(보기 전용): 블록 결합 금지
    const scene = currentScene();
    if (!dragPayload) return;
    document.querySelectorAll('.block').forEach(x => x.classList.remove('drop-ok', 'drop-warn'));

    let childBid = null, cat = null;
    if (dragPayload.eqId) {
        if (Object.values(scene.blocks).some(b => b.eqId === dragPayload.eqId)) {
            setStatus(dragPayload.eqId + ' 는 이미 배치되어 있습니다'); dragPayload = null; return;
        }
        const eq = EQUIPMENT.find(x => x.id === dragPayload.eqId);
        if (!eq) { dragPayload = null; return; }
        cat = eq.cat;
        childBid = 'b' + Date.now() + Math.random().toString(36).slice(2, 5);
        scene.blocks[childBid] = { eqId: eq.id, x: 0, y: 0 };
    } else if (dragPayload.bid) {
        childBid = dragPayload.bid;
        if (childBid === bid || isAncestor(childBid, bid, scene)) {
            setStatus('자기 자신이나 하위 부품에는 붙일 수 없습니다'); dragPayload = null; return;
        }
        const e = eqOfBlock(childBid, scene);
        cat = e && e.cat;
    }
    const r = acceptSlot(bid, cat, scene);
    if (!r) {
        if (dragPayload.eqId) delete scene.blocks[childBid];
        setStatus(`${eqOfBlock(bid, scene).id} 에는 결합할 자리가 없습니다`);
        dragPayload = null; return;
    }
    attachBlock(childBid, bid, r);
    dragPayload = null;
}
function attachBlock(childBid, parentBid, r) {
    const scene = currentScene();
    const cb = scene.blocks[childBid];
    cb.parent = parentBid;
    cb.slot = r.slot;
    cb.warn = !r.ok;
    delete cb.lx; delete cb.ly;
    delete cb.groupId;
    const pe = eqOfBlock(parentBid, scene), ce = eqOfBlock(childBid, scene);
    selectedIds.clear();
    saveState(); renderPalette(); renderCanvas(); afterLayoutChange();
    if (r.ok) setStatus(`✓ ${pe.id} · ${r.name} ← ${ce.id} 결합`);
    else setStatus(`⚠ ${pe.id} · ${r.name} ← ${ce.id} — 규격이 다르지만 연결했습니다`);
}
function detachBlock(bid, e) {
    e && e.stopPropagation();
    const scene = currentScene();
    const b = scene.blocks[bid];
    if (!b || !b.parent) return;
    const pp = blockPos(b.parent, scene);
    const kids = descendantBlocks(bid, scene).length;
    delete b.parent; delete b.slot; delete b.warn; delete b.lx; delete b.ly;
    b.x = pp.x + 40; b.y = pp.y + 150;
    saveState(); renderPalette(); renderCanvas(); afterLayoutChange();
    setStatus(`${eqOfBlock(bid, scene).id} 분리` + (kids ? ` (하위 ${kids}개 함께)` : ''));
}
// 블록 제거 시 하위도 함께
function removeBlockTree(bid) {
    const scene = currentScene();
    descendantBlocks(bid, scene).forEach(c => delete scene.blocks[c]);
    delete scene.blocks[bid];
}

// ───────── 통계 ─────────
function floorStats() {
    const f = F();
    const items = Object.values(f.items);
    let foot = 0, clear = 0;
    const circles = [];
    for (const it of items) {
        const sz = itemSize(it);
        foot += sz.w * sz.h;
        const cr = Math.max(sz.w, sz.h) / 2 + sz.clear;
        clear += Math.PI * cr * cr;
        circles.push({ x: it.x, y: it.y, r: cr });
    }
    let conflicts = 0;
    for (let i = 0; i < circles.length; i++)
        for (let j = i + 1; j < circles.length; j++) {
            const dx = circles[i].x - circles[j].x, dy = circles[i].y - circles[j].y;
            if (Math.hypot(dx, dy) < circles[i].r + circles[j].r) conflicts++;
        }
    const total = f.rooms.reduce((a, r) => a + roomArea(r), 0);
    return {
        count: items.length,
        foot: +foot.toFixed(2),
        clear: +clear.toFixed(2),
        roomArea: +total.toFixed(2),
        ratio: total > 0 ? +((clear / total) * 100).toFixed(0) : null,
        conflicts
    };
}
function updateFloorStats() {
    const st = floorStats();
    let t = `장비 ${st.count}개 · 발자국 ${st.foot}㎡ · 여유포함 ${st.clear}㎡`;
    if (st.roomArea > 0) t += ` · 공간 ${st.roomArea}㎡ 중 ${st.ratio}% 사용`;
    if (st.conflicts > 0) t += `  ⚠ 여유공간 겹침 ${st.conflicts}쌍`;
    const el = document.getElementById('floor-stats');
    el.textContent = t;
    el.className = st.conflicts > 0 ? 'warn' : '';
}

// ───────── 평면도 범위 선택 ─────────
let fMq = null;
function startFloorMarquee(e) {
    const p = toMeters(e);
    fMq = { x0: p.x, y0: p.y, add: e.shiftKey, moved: false };
    document.addEventListener('pointermove', doFloorMarquee);
    document.addEventListener('pointerup', endFloorMarquee);
}
function doFloorMarquee(e) {
    if (!fMq) return;
    const p = toMeters(e);
    if (Math.abs(p.x - fMq.x0) > 0.05 || Math.abs(p.y - fMq.y0) > 0.05) fMq.moved = true;
    fMq.box = { x: Math.min(fMq.x0, p.x), y: Math.min(fMq.y0, p.y),
                w: Math.abs(p.x - fMq.x0), h: Math.abs(p.y - fMq.y0) };
    renderFloor();
}
function endFloorMarquee() {
    const m = fMq; fMq = null;
    document.removeEventListener('pointermove', doFloorMarquee);
    document.removeEventListener('pointerup', endFloorMarquee);
    if (!m) return;
    if (!m.moved) {                       // 제자리 클릭 = 선택 해제
        fMulti.clear(); floorSel = null; renderFloor(); return;
    }
    const f = F(), b = m.box;
    if (!m.add) fMulti.clear();
    for (const [fid, it] of Object.entries(f.items)) {
        const sz = itemSize(it);
        const hit = !(it.x + sz.w / 2 < b.x || it.x - sz.w / 2 > b.x + b.w ||
                      it.y + sz.h / 2 < b.y || it.y - sz.h / 2 > b.y + b.h);
        if (hit) fMulti.add(fid);
    }
    (f.subjects || []).forEach(sj => {
        if (sj.x >= b.x && sj.x <= b.x + b.w && sj.y >= b.y && sj.y <= b.y + b.h)
            fMulti.add(sj.id);
    });
    floorSel = null;
    renderFloor();
    if (fMulti.size) setStatus(`${fMulti.size}개 선택 — 드래그로 함께 이동, Del로 삭제`);
}

// ───────── 평면도 화면 이동 ─────────
let fPan = null;
function startFloorPan(e) {
    const wrap = document.getElementById('floor-wrap');
    const svg = document.getElementById('floor-svg');
    svg.classList.add('panning');
    fPan = { sx: e.clientX, sy: e.clientY, sl: wrap.scrollLeft, st: wrap.scrollTop, moved: false };
    document.addEventListener('pointermove', doFloorPan);
    document.addEventListener('pointerup', endFloorPan);
}
function doFloorPan(e) {
    if (!fPan) return;
    const wrap = document.getElementById('floor-wrap');
    const dx = e.clientX - fPan.sx, dy = e.clientY - fPan.sy;
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) fPan.moved = true;
    wrap.scrollLeft = fPan.sl - dx;
    wrap.scrollTop = fPan.st - dy;
}
function endFloorPan() {
    const moved = fPan && fPan.moved;
    document.getElementById('floor-svg').classList.remove('panning');
    fPan = null;
    document.removeEventListener('pointermove', doFloorPan);
    document.removeEventListener('pointerup', endFloorPan);
    if (!moved && floorSel) { floorSel = null; renderFloor(); }
}

// ───────── 좌표 변환 ─────────
function toMeters(e) {
    const svg = document.getElementById('floor-svg');
    const r = svg.getBoundingClientRect();
    const z = F().zoom;
    return { x: (e.clientX - r.left) / z, y: (e.clientY - r.top) / z };
}

// ───────── 드래그 ─────────
function startFloorDrag(e, type, id) {
    if (isViewOnly()) return;
    if (floorMode !== 'idle') return;
    e.stopPropagation(); e.preventDefault();
    const f = F();
    floorSel = { type, id };
    const p = toMeters(e);
    const obj = type === 'item' ? f.items[id]
              : type === 'subject' ? (f.subjects || []).find(x => x.id === id)
              : type === 'bg' ? f.bg
              : f.rooms.find(r => r.id === id);
    if (!obj) return;
    // 선택 집합에 포함된 항목을 함께 이동
    const grp = [];
    if ((type === 'item' || type === 'subject') && fMulti.has(id)) {
        fMulti.forEach(k => {
            const o = f.items[k] || (f.subjects || []).find(x => x.id === k);
            if (o) grp.push({ o, ox: o.x, oy: o.y });
        });
    } else if (type === 'room') {
        grp.push({ o: obj, ox: obj.x, oy: obj.y });
        // 방(벽)을 옮기면 그 안에 놓인 장비·피사체도 함께 이동
        const poly = roomPoly(obj);
        Object.values(f.items).forEach(o => { if (pointInPoly(poly, o.x, o.y)) grp.push({ o, ox: o.x, oy: o.y }); });
        (f.subjects || []).forEach(o => { if (pointInPoly(poly, o.x, o.y)) grp.push({ o, ox: o.x, oy: o.y }); });
    } else {
        if (type === 'item' || type === 'subject') { fMulti.clear(); fMulti.add(id); }
        grp.push({ o: obj, ox: obj.x, oy: obj.y });
    }
    fDrag = { type, id, ox: obj.x, oy: obj.y, px: p.x, py: p.y, moved: false, grp };
    document.addEventListener('pointermove', doFloorDrag);
    document.addEventListener('pointerup', endFloorDrag);
    renderFloor();
}
function doFloorDrag(e) {
    if (!fDrag) return;
    const f = F(), p = toMeters(e);
    const dx = p.x - fDrag.px, dy = p.y - fDrag.py;
    if (Math.abs(dx) > 0.02 || Math.abs(dy) > 0.02) fDrag.moved = true;
    const obj = fDrag.type === 'item' ? f.items[fDrag.id]
              : fDrag.type === 'subject' ? (f.subjects || []).find(x => x.id === fDrag.id)
              : fDrag.type === 'bg' ? f.bg
              : f.rooms.find(r => r.id === fDrag.id);
    if (!obj) return;
    const put = (o, gx, gy) => {
        if (snapEnabled) { gx = Math.round(gx * 10) / 10; gy = Math.round(gy * 10) / 10; }
        o.x = +gx.toFixed(3); o.y = +gy.toFixed(3);
        // 장비·피사체만 방 안으로 가둔다. 방(room)·배경(bg)을 가두면 자기 자신 안으로
        // 클램프되며 엉뚱한 곳으로 튄다 → 벽 이동이 끊겨 이상한 위치에 놓이던 버그.
        if (fDrag.type === 'subject') confineSubject(o);
        else if (fDrag.type === 'item') confineItem(o);
    };
    if (fDrag.grp && fDrag.grp.length > 1) fDrag.grp.forEach(g => put(g.o, g.ox + dx, g.oy + dy));
    else put(obj, fDrag.ox + dx, fDrag.oy + dy);
    renderFloor();
}
function endFloorDrag() {
    if (fDrag && fDrag.moved) saveState();
    fDrag = null;
    document.removeEventListener('pointermove', doFloorDrag);
    document.removeEventListener('pointerup', endFloorDrag);
}

// ───────── 장비 추가 (팔레트 드롭) ─────────
function addFloorItem(eqId, xm, ym) {
    const f = F();
    if (Object.values(f.items).some(i => i.eqId === eqId)) {
        alert(eqId + ' 는 이미 평면도에 배치되어 있습니다.');
        return null;
    }
    const fid = 'f' + Date.now() + Math.random().toString(36).slice(2, 5);
    const it = { eqId, x: +xm.toFixed(2), y: +ym.toFixed(2), rot: 0, parts: [] };
    it.h3 = rigHeight(it);
    confineItem(it);
    f.items[fid] = it;
    // 배치도에도 같은 장비를 올려 둔다 (한쪽에만 있는 상태를 만들지 않는다)
    const sc = currentScene();
    if (!Object.values(sc.blocks).some(b => b.eqId === eqId)) {
        const n = Object.keys(sc.blocks).length;
        addBlockAt(eqId, 60 + (n % 6) * 130, 80 + Math.floor(n / 6) * 110, true);
    }
    saveState();
    return fid;
}
function placeSetOnFloor(sid, xm, ym) {
    const set = state.sets[sid];
    if (!set) return;
    const f = F();
    const placed = new Set(Object.values(f.items).map(i => i.eqId));
    const todo = set.eqIds.filter(id => EQUIPMENT.find(e => e.id === id) && !placed.has(id));
    if (todo.length === 0) { alert('이 세트의 장비가 모두 배치되어 있습니다.'); return; }
    todo.forEach((eqId, i) => {
        addFloorItem(eqId, xm + (i % 4) * 1.3, ym + Math.floor(i / 4) * 1.3);
    });
    renderFloor(); renderPalette();
    setStatus(`"${set.name}" ${todo.length}개를 평면도에 배치`);
}

// ───────── 펜툴 (다각형 방) ─────────
function startPen() {
    floorMode = 'pen'; penPts = []; penCursor = null; floorSel = null;
    document.getElementById('floor-svg').style.cursor = 'crosshair';
    setStatus('펜툴: 모서리를 차례로 클릭 · Shift=45°각 고정 · 첫 점 클릭 또는 Enter=완성 · Esc=취소');
    renderFloor();
}
function penSnapPoint(p, shift) {
    let q = { x: p.x, y: p.y };
    if (shift && penPts.length) {
        const last = penPts[penPts.length - 1];
        const dx = q.x - last.x, dy = q.y - last.y;
        const step = Math.PI / 4;
        const ang = Math.round(Math.atan2(dy, dx) / step) * step;
        const len = Math.hypot(dx, dy);
        q = { x: last.x + Math.cos(ang) * len, y: last.y + Math.sin(ang) * len };
    }
    if (snapEnabled) { q.x = Math.round(q.x * 10) / 10; q.y = Math.round(q.y * 10) / 10; }
    return { x: +q.x.toFixed(3), y: +q.y.toFixed(3) };
}
function penClick(p, shift) {
    // 첫 점 근처 클릭 → 닫기
    if (penPts.length >= 3) {
        const f0 = penPts[0];
        if (Math.hypot(p.x - f0.x, p.y - f0.y) < 0.35) { finishPen(); return; }
    }
    penPts.push(penSnapPoint(p, shift));
    renderFloor();
}
function finishPen() {
    if (penPts.length < 3) {
        alert('점을 3개 이상 찍어야 공간이 됩니다.');
        return;
    }
    const minX = Math.min(...penPts.map(p => p.x));
    const minY = Math.min(...penPts.map(p => p.y));
    const pts = penPts.map(p => ({ x: +(p.x - minX).toFixed(3), y: +(p.y - minY).toFixed(3) }));
    const area = polyArea(pts);
    const name = prompt(`공간 이름 (면적 ${area.toFixed(1)}㎡)`, '촬영장') || '공간';
    F().rooms.push({
        id: 'r' + Date.now(), name, type: 'poly',
        x: +minX.toFixed(3), y: +minY.toFixed(3), pts
    });
    cancelPen();
    saveState(); renderFloor(); updateStatus();
}
function cancelPen() {
    penPts = []; penCursor = null; floorMode = 'idle';
    document.getElementById('floor-svg').style.cursor = '';
}
function undoPenPoint() {
    if (penPts.length) { penPts.pop(); renderFloor(); }
}

// ───────── 사각형 방 모서리 리사이즈 ─────────
let rectRz = null;
function startRectResize(e, rid, idx) {
    e.stopPropagation(); e.preventDefault();
    const r = F().rooms.find(x => x.id === rid);
    if (!r || r.type === 'poly') return;
    rectRz = { rid, idx, x: r.x, y: r.y, w: r.w, h: r.h, p: toMeters(e) };
    document.addEventListener('pointermove', doRectResize);
    document.addEventListener('pointerup', endRectResize);
}
function doRectResize(e) {
    if (!rectRz) return;
    const r = F().rooms.find(x => x.id === rectRz.rid);
    if (!r) return;
    const p = toMeters(e);
    let dx = p.x - rectRz.p.x, dy = p.y - rectRz.p.y;
    if (snapEnabled) { dx = Math.round(dx * 10) / 10; dy = Math.round(dy * 10) / 10; }
    let { x, y, w, h } = rectRz;
    if (rectRz.idx === 0) { x += dx; y += dy; w -= dx; h -= dy; }
    if (rectRz.idx === 1) { y += dy; w += dx; h -= dy; }
    if (rectRz.idx === 2) { w += dx; h += dy; }
    if (rectRz.idx === 3) { x += dx; w -= dx; h += dy; }
    if (w < 0.3 || h < 0.3) return;
    r.x = +x.toFixed(2); r.y = +y.toFixed(2);
    r.w = +w.toFixed(2); r.h = +h.toFixed(2);
    renderFloor();
}
function endRectResize() {
    reconfineAll();
    if (rectRz) saveState();
    rectRz = null;
    document.removeEventListener('pointermove', doRectResize);
    document.removeEventListener('pointerup', endRectResize);
}
// 배경 도면 크기 핸들
let bgRz = null;
function startBgResize(e) {
    e.stopPropagation(); e.preventDefault();
    const f = F();
    bgRz = { w: f.bg.w, h: f.bg.h, p: toMeters(e) };
    document.addEventListener('pointermove', doBgResize);
    document.addEventListener('pointerup', endBgResize);
}
function doBgResize(e) {
    if (!bgRz) return;
    const f = F(), p = toMeters(e);
    const nw = Math.max(0.5, bgRz.w + (p.x - bgRz.p.x));
    const k = nw / bgRz.w;
    f.bg.w = +nw.toFixed(3);
    f.bg.h = +(bgRz.h * k).toFixed(3);
    renderFloor();
}
function endBgResize() {
    if (bgRz) { saveState(); syncBgUI(); }
    bgRz = null;
    document.removeEventListener('pointermove', doBgResize);
    document.removeEventListener('pointerup', endBgResize);
}

// ───────── 정점 편집 ─────────
function startVertexDrag(e, rid, idx) {
    e.stopPropagation(); e.preventDefault();
    const r = F().rooms.find(x => x.id === rid);
    if (!r || !r.pts) return;
    const p = toMeters(e);
    vDrag = { rid, idx, ox: r.pts[idx].x, oy: r.pts[idx].y, px: p.x, py: p.y, moved: false };
    document.addEventListener('pointermove', doVertexDrag);
    document.addEventListener('pointerup', endVertexDrag);
}
function doVertexDrag(e) {
    if (!vDrag) return;
    const r = F().rooms.find(x => x.id === vDrag.rid);
    if (!r) return;
    const p = toMeters(e);
    let nx = vDrag.ox + (p.x - vDrag.px), ny = vDrag.oy + (p.y - vDrag.py);
    if (snapEnabled) { nx = Math.round(nx * 10) / 10; ny = Math.round(ny * 10) / 10; }
    r.pts[vDrag.idx] = { x: +nx.toFixed(3), y: +ny.toFixed(3) };
    vDrag.moved = true;
    renderFloor();
}
function endVertexDrag() {
    if (vDrag && vDrag.moved) {
        reconfineAll();
        // 음수 좌표 생기면 원점 기준으로 정규화
        const r = F().rooms.find(x => x.id === vDrag.rid);
        if (r) {
            const mx = Math.min(...r.pts.map(p => p.x)), my = Math.min(...r.pts.map(p => p.y));
            if (mx !== 0 || my !== 0) {
                r.x = +(r.x + mx).toFixed(3); r.y = +(r.y + my).toFixed(3);
                r.pts = r.pts.map(p => ({ x: +(p.x - mx).toFixed(3), y: +(p.y - my).toFixed(3) }));
            }
        }
        saveState();
    }
    vDrag = null;
    document.removeEventListener('pointermove', doVertexDrag);
    document.removeEventListener('pointerup', endVertexDrag);
    renderFloor();
}
function addVertexToSelected() {
    if (!floorSel || floorSel.type !== 'room') return;
    const r = F().rooms.find(x => x.id === floorSel.id);
    if (!r || !r.pts) { alert('다각형 공간을 선택해주세요.'); return; }
    // 가장 긴 변을 반으로 나눠 점 추가
    let bi = 0, best = -1;
    for (let i = 0; i < r.pts.length; i++) {
        const a = r.pts[i], b = r.pts[(i + 1) % r.pts.length];
        const l = Math.hypot(b.x - a.x, b.y - a.y);
        if (l > best) { best = l; bi = i; }
    }
    const a = r.pts[bi], b = r.pts[(bi + 1) % r.pts.length];
    r.pts.splice(bi + 1, 0, { x: +((a.x + b.x) / 2).toFixed(3), y: +((a.y + b.y) / 2).toFixed(3) });
    saveState(); renderFloor();
}
function removeVertexFromSelected() {
    if (!floorSel || floorSel.type !== 'room') return;
    const r = F().rooms.find(x => x.id === floorSel.id);
    if (!r || !r.pts) return;
    if (r.pts.length <= 3) { alert('삼각형보다 적게는 줄일 수 없습니다.'); return; }
    // 가장 짧은 변의 끝점 제거
    let bi = 0, best = Infinity;
    for (let i = 0; i < r.pts.length; i++) {
        const a = r.pts[i], b = r.pts[(i + 1) % r.pts.length];
        const l = Math.hypot(b.x - a.x, b.y - a.y);
        if (l < best) { best = l; bi = (i + 1) % r.pts.length; }
    }
    r.pts.splice(bi, 1);
    saveState(); renderFloor();
}

// ───────── 배치도 → 평면도/3D 가져오기 ─────────
// ═══════════════════════════════════════════════════
//  배치도 → 평면도 · 3D 자동 동기화
//  배치도가 "무엇이 있고 어떻게 조립됐는가"의 기준이 된다.
//  평면도·3D는 "그게 어디에 놓였는가"만 따로 기억한다.
// ═══════════════════════════════════════════════════
function freeSpotsIn(f, n, taken) {
    let ox = 1, oz = 1, usableW = 8;
    if (f.rooms.length) {
        const r = f.rooms[0];
        if (r.type === 'poly') {
            const mx = Math.max(...r.pts.map(p => p.x));
            ox = r.x + 0.7; oz = r.y + 0.7; usableW = Math.max(1.5, mx - 1.4);
        } else { ox = r.x + 0.7; oz = r.y + 0.7; usableW = Math.max(1.5, r.w - 1.4); }
    }
    const GAP = 1.1, cols = Math.max(1, Math.floor(usableW / GAP));
    const out = [];
    let i = 0;
    while (out.length < n && i < n + 400) {
        const x = +Math.min(WORLD_W, ox + (i % cols) * GAP).toFixed(2);
        const y = +Math.min(WORLD_H, oz + Math.floor(i / cols) * GAP).toFixed(2);
        i++;
        if (taken.some(p => Math.hypot(p.x - x, p.y - y) < GAP * 0.7)) continue;
        out.push({ x, y });
        taken.push({ x, y });
    }
    return out;
}
// reflow=true 면 위치까지 다시 깔아준다 (수동 "다시 정렬")
function syncFromLayout(reflow) {
    const s = currentScene(), f = ensureFloor(s);
    ensure3D(s);
    const roots = rootBlocks(s).map(k => [k, s.blocks[k]])
        .filter(([, b]) => EQUIPMENT.some(e => e.id === b.eqId));
    // 같은 그룹끼리 모이도록
    roots.sort((a, b) => {
        const ga = a[1].groupId || '', gb = b[1].groupId || '';
        return ga === gb ? a[1].eqId.localeCompare(b[1].eqId) : ga.localeCompare(gb);
    });
    const wanted = new Set(roots.map(([, b]) => b.eqId));
    let added = 0, updated = 0, removed = 0;

    // ① 배치도에서 빠진 장비는 평면도·3D에서도 내린다
    for (const [fid, it] of Object.entries(f.items)) {
        if (!wanted.has(it.eqId)) {
            delete f.items[fid];
            if (three3Sel === fid) three3Sel = null;
            if (floorSel && floorSel.id === fid) floorSel = null;
            fMulti.delete(fid);
            removed++;
        }
    }
    // ② 있는 것은 조립 구성을 최신으로, 없는 것은 새로 놓는다
    const taken = reflow ? [] : Object.values(f.items).map(i => ({ x: i.x, y: i.y }));
    const news = [];
    for (const [bid, b] of roots) {
        const eq = EQUIPMENT.find(e => e.id === b.eqId);
        const parts = descendantBlocks(bid, s).map(cid => ({
            eqId: s.blocks[cid].eqId,
            slot: s.blocks[cid].slot,
            parent: s.blocks[cid].parent === bid ? null : s.blocks[s.blocks[cid].parent].eqId
        }));
        const hit = Object.entries(f.items).find(([, i]) => i.eqId === b.eqId);
        if (hit) {
            const it = hit[1];
            if (JSON.stringify(it.parts || []) !== JSON.stringify(parts)) {
                it.parts = parts;
                const [lo, hi] = hRange(it);
                if (it.h3 === undefined || it.h3 < lo || it.h3 > hi)
                    it.h3 = +Math.max(lo, Math.min(hi, rigHeight(it))).toFixed(2);
                if (eq.cat === 'CAM') {
                    delete it.focalMin; delete it.fMin; delete it.lens;
                    applyLensSpec(it);
                }
                updated++;
            }
            if (reflow) news.push(it);
        } else {
            const it = { eqId: b.eqId, rot: 0, parts, x: 1, y: 1 };
            it.h3 = rigHeight(it);
            if (eq.cat === 'CAM') applyLensSpec(it);
            const fid = 'f' + Date.now() + added + Math.random().toString(36).slice(2, 5);
            f.items[fid] = it;
            news.push(it);
            added++;
        }
    }
    // ③ 새로 들어온 것(또는 재정렬 시 전부)에 자리를 준다
    const spots = freeSpotsIn(f, news.length, taken);
    news.forEach((it, i) => { if (spots[i]) { it.x = spots[i].x; it.y = spots[i].y; } confineItem(it); });

    if (added || updated || removed) saveState();
    return { added, updated, removed };
}
// 배치도가 바뀐 뒤 호출 — 평면도·3D를 즉시 맞춘다
function afterLayoutChange() {
    const r = syncFromLayout(false);
    const md = currentScene().mode;
    if (md === 'floor') renderFloor();
    else if (md === 'three' && R3) { build3D(); showSel(); }
    return r;
}
// 수동: 위치까지 다시 깔기
function reflowFromLayout() {
    const s = currentScene();
    if (!rootBlocks(s).length) { alert('배치도에 배치된 장비가 없습니다.'); return; }
    if (!confirm('평면도·3D의 장비 위치를 방 안에 다시 정렬합니다.\n직접 옮겨둔 위치는 사라집니다. 계속할까요?')) return;
    const r = syncFromLayout(true);
    if (currentScene().mode === 'three' && R3) { build3D(); showSel(); } else renderFloor();
    renderPalette();
    setStatus(`배치도 기준으로 다시 정렬했습니다 (${Object.keys(ensureFloor(s).items).length}개)`);
}

// ───────── 빈 상태 안내 ─────────
function updateEmptyHints() {
    const s = currentScene(), f = ensureFloor(s);
    const nItems = Object.keys(f.items).length;
    const nBlocks = Object.keys(s.blocks).length;
    let msg = '';
    if (nItems === 0) {
        msg = nBlocks > 0
            ? `<div class="empty-card"><b>여기엔 아직 장비가 없습니다</b><br>
                 <span class="sub">배치도(📋)와 평면도/3D는 배치를 따로 저장합니다.</span><br>
                 배치도에 <b>${nBlocks}개</b>가 놓여 있어요.
                 <div style="margin-top:12px">
                   <button class="primary" onclick="reflowFromLayout()">⬇ 배치도의 ${nBlocks}개 정렬해서 놓기</button>
                 </div></div>`
            : `<div class="empty-card"><b>장비를 배치해주세요</b><br>
                 <span class="sub">왼쪽 팔레트에서 장비 또는 세트를 끌어다 놓으면<br>
                 평면도와 3D에 동시에 반영됩니다.</span></div>`;
    }
    ['three-empty', 'floor-empty'].forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        el.innerHTML = msg;
        el.style.display = msg ? 'flex' : 'none';
    });
}

// ───────── 방 그리기 ─────────
function startRoomDraw() {
    floorMode = 'room';
    setStatus('방 그리기: 캔버스에서 드래그해 사각형을 그리세요 (Esc 취소)');
    document.getElementById('floor-svg').style.cursor = 'crosshair';
}
function addRoomByNumbers() {
    const w = parseFloat(prompt('가로 길이 (m)', '6'));
    if (!w || w <= 0) return;
    const h = parseFloat(prompt('세로 길이 (m)', '4'));
    if (!h || h <= 0) return;
    const name = prompt('공간 이름', '촬영장') || '공간';
    const f = F();
    f.rooms.push({ id: 'r' + Date.now(), name, x: 1, y: 1, w: +w.toFixed(2), h: +h.toFixed(2) });
    saveState(); renderFloor();
}
function finishRoom(x1, y1, x2, y2) {
    const w = Math.abs(x2 - x1), h = Math.abs(y2 - y1);
    if (w < 0.3 || h < 0.3) return;
    const name = prompt(`공간 이름 (${w.toFixed(1)} × ${h.toFixed(1)} m)`, '촬영장') || '공간';
    F().rooms.push({
        id: 'r' + Date.now(), name,
        x: +Math.min(x1, x2).toFixed(2), y: +Math.min(y1, y2).toFixed(2),
        w: +w.toFixed(2), h: +h.toFixed(2)
    });
    saveState(); renderFloor();
}

// ───────── 배경 도면 ─────────
function pickBgImage() {
    const f = F();
    if (f.bg && !confirm('배경 도면을 교체할까요? (취소하면 제거)')) {
        f.bg = null; saveState(); renderFloor(); return;
    }
    const inp = document.createElement('input');
    inp.type = 'file'; inp.accept = 'image/*';
    inp.onchange = e => {
        const file = e.target.files[0]; if (!file) return;
        const rd = new FileReader();
        rd.onload = ev => downscaleImage(ev.target.result, (data, iw, ih) => {
            const wM = 10, hM = 10 * (ih / iw);
            F().bg = { data, x: 0, y: 0, w: wM, h: +hM.toFixed(2), opacity: 0.55 };
            saveState(); renderFloor();
            setStatus('배경 도면 추가 — "📏 축척 보정"으로 실제 크기를 맞춰주세요');
        });
        rd.readAsDataURL(file);
    };
    inp.click();
}
function downscaleImage(dataUrl, cb) {
    const img = new Image();
    img.onload = () => {
        const MAX = 1400;
        let w = img.width, h = img.height;
        if (w > MAX || h > MAX) { const r = Math.min(MAX / w, MAX / h); w = Math.round(w * r); h = Math.round(h * r); }
        const c = document.createElement('canvas');
        c.width = w; c.height = h;
        c.getContext('2d').drawImage(img, 0, 0, w, h);
        cb(c.toDataURL('image/jpeg', 0.72), w, h);
    };
    img.src = dataUrl;
}
// ───────── 패널 접기 / 레일 전환 ─────────
function togglePalette() {
    const app = document.getElementById('app');
    app.classList.toggle('pal-hidden');
    const hid = app.classList.contains('pal-hidden');
    state.palHidden = hid;
    const tab = document.getElementById('panel-tab');
    if (tab) tab.textContent = hid ? '›' : '‹';
    saveState();
    if (currentScene().mode === 'three') setTimeout(resize3D, 220);
    else if (currentScene().mode === 'floor') setTimeout(syncBgUI, 0);
}
let activePane = 'equip';
let activeCat = 'ALL';
let railMore = false;
let railCats = true;
function toggleRailCats() {
    const app = document.getElementById('app');
    if (!railCats) {                       // 접혀 있으면 펼치면서 전체 선택
        railCats = true; state.railCats = true;
        if (app.classList.contains('pal-hidden')) togglePalette();
        activeCat = 'ALL'; activePane = 'equip'; state.cat = 'ALL'; state.pane = 'equip';
        document.querySelectorAll('.pane').forEach(el => el.classList.toggle('on', el.id === 'pane-equip'));
        document.querySelectorAll('.rail-btn.tool').forEach(b => b.classList.remove('on'));
        const t2 = document.getElementById('equip-title');
        if (t2) t2.textContent = '전체 장비';
        saveState(); renderRail(); renderPalette();
        return;
    }
    if (activeCat !== 'ALL' || activePane !== 'equip') { openCat('ALL'); return; }
    railCats = false; state.railCats = false;
    saveState(); renderRail();
}
// 레일 표시 순서
const RAIL_MAIN = ['CAM', 'LEN', 'TRP', 'AUD', 'LIT', 'MOD', 'STD'];
const RAIL_MORE = ['GIM', 'BAT', 'PWR', 'STO', 'MON', 'CAB', 'ACC', 'ETC'];
const RAIL_LABEL = { CAM: '카메라', LEN: '렌즈', TRP: '삼각대', AUD: '오디오', LIT: '조명',
    MOD: '조명모디', STD: '스탠드', GIM: '짐벌', BAT: '배터리', PWR: '전원', STO: '저장',
    MON: '모니터', CAB: '케이블', ACC: '액세서리', ETC: '기타' };
function toggleRailMore() {
    railMore = !railMore;
    state.railMore = railMore;
    saveState(); renderRail();
}

// ───────── 레일: 장비 카테고리 ─────────
function renderRail() {
    const box = document.getElementById('rail-cats');
    if (!box) return;
    const counts = {};
    EQUIPMENT.forEach(e => counts[e.cat] = (counts[e.cat] || 0) + 1);
    let h = `<button class="rail-btn head ${activeCat === 'ALL' && activePane === 'equip' ? 'on' : ''} ${railCats ? 'open' : ''}"
        data-c="ALL" onclick="toggleRailCats()" title="장비 카테고리">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
          stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="7.4" height="7.4" rx="1.4"/><rect x="13.6" y="3" width="7.4" height="7.4" rx="1.4"/>
          <rect x="3" y="13.6" width="7.4" height="7.4" rx="1.4"/><rect x="13.6" y="13.6" width="7.4" height="7.4" rx="1.4"/></svg>
        <span>전체</span><span class="rc">${EQUIPMENT.length}</span>
        <span class="chev">${railCats ? '▴' : '▾'}</span></button>`;
    const btn = c => {
        const on = activeCat === c && activePane === 'equip';
        return `<button class="rail-btn cat-${c} ${on ? 'on' : ''}" data-c="${c}"
                onclick="openCat('${c}')" title="${CAT_NAMES[c]}">
                ${iconSvg(c, '')}
                <span>${RAIL_LABEL[c] || CAT_NAMES[c]}</span>
                <span class="rc">${counts[c]}</span></button>`;
    };
    if (railCats) {
    RAIL_MAIN.forEach(c => { if (counts[c]) h += btn(c); });
    const moreN = RAIL_MORE.filter(c => counts[c]).reduce((a, c) => a + counts[c], 0);
    h += `<button class="rail-btn more ${railMore ? 'open' : ''}" onclick="toggleRailMore()"
            title="${railMore ? '접기' : '더보기'}">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round">
              ${railMore ? '<path d="M6 14.5l6-6 6 6"/>' : '<path d="M6 9.5l6 6 6-6"/>'}</svg>
            <span>${railMore ? '접기' : '더보기'}</span>
            ${railMore ? '' : `<span class="rc">${moreN}</span>`}</button>`;
    if (railMore) RAIL_MORE.forEach(c => { if (counts[c]) h += btn(c); });
    }
    box.innerHTML = h;
}
function openCat(c, init) {
    const app = document.getElementById('app');
    if (!init) {
        if (activeCat === c && activePane === 'equip' && !app.classList.contains('pal-hidden')) {
            togglePalette(); return;
        }
        if (app.classList.contains('pal-hidden')) togglePalette();
    }
    if (RAIL_MORE.includes(c)) railMore = true;
    activeCat = c; activePane = 'equip';
    state.cat = c; state.pane = 'equip';
    document.querySelectorAll('.pane').forEach(el => el.classList.toggle('on', el.id === 'pane-equip'));
    document.querySelectorAll('.rail-btn.tool').forEach(b => b.classList.remove('on'));
    const t = document.getElementById('equip-title');
    if (t) t.textContent = c === 'ALL' ? '전체 장비' : CAT_NAMES[c];
    renderRail(); renderPalette(); saveState();
}

function openPane(p, init) {
    const app = document.getElementById('app');
    if (!init) {
        // 같은 탭을 다시 누르면 접기/펴기
        if (activePane === p && !app.classList.contains('pal-hidden')) { togglePalette(); return; }
        if (app.classList.contains('pal-hidden')) togglePalette();
    }
    activePane = p;
    state.pane = p;
    document.querySelectorAll('.rail-btn.tool').forEach(b => b.classList.toggle('on', b.dataset.p === p));
    document.querySelectorAll('.pane').forEach(el => el.classList.toggle('on', el.id === 'pane-' + p));
    renderRail();
    if (p === 'sets') renderSets();
    if (p === 'rig') renderRigPane();
    if (p === 'scenes') renderScenePane();
    saveState();
}
// 기존 switchTab 호환
function switchTab(t) { openPane(t === 'sets' ? 'sets' : 'equip'); }

// ───────── 공간 패널 ─────────
function renderSpacePane() {
    const box = document.getElementById('space-body');
    if (!box) return;
    const s = currentScene(), f = ensureFloor(s);
    let h = `<div class="pane-sec">천장고</div>
      <div class="pane-row"><input type="number" id="sp-ceil" step="0.1" min="1.8" max="12"
        value="${f.ceilH !== undefined ? f.ceilH : 2.7}" onchange="setCeiling(this.value)"> m</div>`;
    h += `<div class="pane-sec">공간 (${f.rooms.length})</div>`;
    if (!f.rooms.length) h += `<div class="pane-sub">평면도에서 방을 그려주세요.</div>`;
    f.rooms.forEach(r => {
        const on = floorSel && floorSel.type === 'room' && floorSel.id === r.id;
        const dim = r.type === 'poly'
            ? `${r.pts.length}각형 · ${roomArea(r).toFixed(2)}㎡`
            : `${r.w.toFixed(2)} × ${r.h.toFixed(2)} m · ${(r.w * r.h).toFixed(2)}㎡`;
        h += `<div class="plist-item ${on ? 'on' : ''}" onclick="selectRoom('${r.id}')">
                <div class="pi-tx"><div class="pi-t">${esc(r.name)}</div><div class="pi-s">${dim}</div></div>
                <span class="pi-x" onclick="deleteRoom('${r.id}',event)">×</span></div>`;
    });
    h += `<div class="pane-btns">
            <button class="primary" onclick="startPen()">✏️ 펜</button>
            <button onclick="startRoomDraw()">▭ 사각형</button>
            <button onclick="addRoomByNumbers()">⌨ 치수</button></div>`;
    h += `<div class="pane-sec">배경 도면</div>`;
    if (f.bg) {
        h += `<div class="pane-row">폭 <input type="number" id="sp-bgw" step="0.1" min="0.5"
                value="${f.bg.w.toFixed(2)}" onchange="setBgWidth(this.value)"> m</div>
              <div class="pane-sub">높이 ${f.bg.h.toFixed(2)} m · 투명도 ${Math.round(f.bg.opacity * 100)}%</div>
              <div class="pane-btns">
                <button onclick="startCalibrate()">📏 축척</button>
                <button onclick="cycleBgOpacity()">◐ 투명도</button>
                <button onclick="toggleBgMove()">✥ 이동</button></div>
              <div class="pane-btns"><button class="danger" onclick="removeBg()">도면 제거</button></div>`;
    } else {
        h += `<div class="pane-sub">현장 도면 사진을 올리면 그 위에 배치할 수 있습니다.</div>
              <div class="pane-btns"><button class="primary" onclick="pickBgImage()">🖼 도면 올리기</button></div>`;
    }
    const st = floorStats();
    h += `<div class="pane-sec">현황</div>
      <div class="slot-help">
        <div class="sh-row"><span class="sh-k">장비</span><b>${st.count}대</b></div>
        <div class="sh-row"><span class="sh-k">발자국</span><b>${st.foot}㎡</b></div>
        <div class="sh-row"><span class="sh-k">여유포함</span><b>${st.clear}㎡</b></div>
        ${st.roomArea > 0 ? `<div class="sh-row"><span class="sh-k">공간 사용</span><b>${st.ratio}%</b></div>` : ''}
        ${st.conflicts ? `<div class="sh-row"><span class="sh-k">겹침</span><b style="color:var(--warn)">${st.conflicts}쌍</b></div>` : ''}
      </div>`;
    box.innerHTML = h;
}
function selectRoom(id) {
    floorSel = { type: 'room', id };
    if (currentScene().mode !== 'floor') switchMode('floor'); else renderFloor();
    renderSpacePane();
}
function deleteRoom(id, e) {
    e.stopPropagation();
    const f = F();
    f.rooms = f.rooms.filter(r => r.id !== id);
    floorSel = null;
    saveState(); renderFloor(); renderSpacePane();
}
function removeBg() {
    const f = F();
    if (!f.bg || !confirm('배경 도면을 제거할까요?')) return;
    f.bg = null; bgMove = false;
    saveState(); renderFloor(); renderSpacePane();
}

// ───────── 조립 패널 ─────────
function renderRigPane() {
    const box = document.getElementById('rig-body');
    if (!box) return;
    const s = currentScene();
    const roots = rootBlocks(s);
    let h = `<div class="pane-sec">표시 방식</div>
      <div class="pane-btns" id="rig-view">
        <button data-v="nest" class="${rigView === 'nest' ? 'primary' : ''}" onclick="setRigView('nest')">중첩</button>
        <button data-v="link" class="${rigView === 'link' ? 'primary' : ''}" onclick="setRigView('link')">선 연결</button>
        <button data-v="fold" class="${rigView === 'fold' ? 'primary' : ''}" onclick="setRigView('fold')">접기</button>
      </div>`;
    h += `<div class="pane-sec">조립체 (${roots.length})</div>`;
    if (!roots.length) h += `<div class="pane-sub">배치도에 카메라나 조명을 놓아 조립체를 만드세요.</div>`;
    roots.forEach(bid => {
        const eq = eqOfBlock(bid, s);
        if (!eq) return;
        const kids = descendantBlocks(bid, s).length;
        const isRoot = ROOT_CATS.includes(eq.cat);
        h += `<div class="plist-item ${selectedIds.has(bid) ? 'on' : ''}" onclick="focusBlock('${bid}')">
                ${iconSvgFor(eq, 'cicon sm')}
                <div class="pi-tx"><div class="pi-t">${eq.id}</div>
                  <div class="pi-s">${kids ? '부품 ' + kids + '개' : (isRoot ? '부품 없음' : '단독 배치')}</div></div>
              </div>`;
    });
    h += `<div class="pane-sec">조립이란</div><div class="slot-help">
      실제로 한 몸으로 움직이는 장비를 하나로 묶는 기능입니다.<br>
      <b>삼각대 + 카메라 + 렌즈 + 메모리</b>를 묶으면 배치도에서 한 덩어리로 이동하고,
      평면도·3D에서는 <b>삼각대 발자국(1.0m)과 높이(0.27~1.57m)</b>가 자동 적용됩니다.
      </div>
      <div class="pane-sec">사용법</div><div class="slot-help">
        <div class="sh-row"><span class="sh-k">① 기준</span>카메라 또는 조명을 캔버스에 놓습니다</div>
        <div class="sh-row"><span class="sh-k">② 결합</span>팔레트나 다른 블록을 그 위로 끌어다 놓습니다</div>
        <div class="sh-row"><span class="sh-k">③ 확인</span>초록=규격 적합 · 노랑=경고(연결은 됨)</div>
        <div class="sh-row"><span class="sh-k">④ 분리</span>부품 행의 ×를 누르면 떨어져 나옵니다</div>
        <div class="sh-row"><span class="sh-k">⑤ 반영</span>평면도·3D에 <b>자동으로</b> 나타납니다 (조립 그대로)</div>
      </div>
      <div class="pane-sec">결합 가능한 자리</div><div class="slot-help">
      <div class="sh-row"><span class="sh-k">카메라</span>렌즈1 · 지지대1 · 메모리2 · 배터리2 · 슈2</div>
      <div class="sh-row"><span class="sh-k">조명</span>스탠드1 · 모디파이어2 · 전원1</div>
      <div class="sh-row"><span class="sh-k">렌즈</span>필터1</div>
      <div class="sh-row"><span class="sh-k">C스탠드</span>그립헤드·암 세트1 · 암에 매달기2 · 웨이트2</div>
      <div style="margin-top:9px;color:var(--tx-3)">최상위는 카메라·조명만 될 수 있습니다.
      그 외 장비를 단독으로 놓으면 "단독"으로 표시됩니다.</div>
      </div>`;
    box.innerHTML = h;
}
function focusBlock(bid) {
    selectedIds.clear(); selectedIds.add(bid);
    if (currentScene().mode !== 'layout') switchMode('layout'); else renderCanvas();
    renderRigPane();
}

// ───────── 씬 패널 ─────────
function renderScenePane() {
    const box = document.getElementById('scene-body');
    if (!box) return;
    if (typeof viewOnly !== 'undefined' && viewOnly) { box.innerHTML =
        '<div class="slot-help">보기 전용으로 열린 배치입니다.</div>'; return; }
    let h = '';
    for (const [id, sc] of Object.entries(state.scenes)) {
        const on = id === state.currentScene;
        const nb = Object.keys(sc.blocks || {}).length;
        const nf = sc.floor ? Object.keys(sc.floor.items || {}).length : 0;
        h += `<div class="plist-item ${on ? 'on' : ''}" onclick="gotoScene('${id}')">
                <div class="pi-tx"><div class="pi-t">${esc(sc.name)}</div>
                  <div class="pi-s">배치 ${nb} · 평면 ${nf}${sc.mode === 'three' ? ' · 3D' : ''}</div></div>
              </div>`;
    }
    h += `<div class="pane-btns">
            <button class="primary" onclick="newScene()">+ 새 씬</button>
            <button onclick="renameScene()">이름 변경</button></div>
          <div class="pane-btns">
            <button onclick="clearScene()">🗑 초기화</button>
            <button class="danger" onclick="deleteScene()">씬 삭제</button></div>
          <div class="pane-sec">외부 공유</div>
          <div class="slot-help" style="margin-bottom:8px">
            링크를 만들면 클라이언트·협력사가 <b>보기만</b> 할 수 있습니다.<br>회수는 로그인 후 언제든 가능합니다.
          </div>
          <div class="pane-btns">
            <button class="primary" onclick="createShareLink()">🔗 공유 링크 만들기</button>
          </div>
          ${(state.shares || []).length ? `<div class="pane-sec">보낸 링크</div>` +
            (state.shares || []).slice(0, 6).map(x => `
              <div class="share-row ${x.dead ? 'dead' : ''}">
                <span class="sr-n">${esc(x.name)}</span>
                <span class="sr-d">${fmtShareTime(x.at)}${x.days ? ` · ${x.days}일` : ''}</span>
                ${x.dead ? '<span class="sr-d">회수됨</span>'
                  : `<button class="danger" style="padding:3px 8px;font-size:10px"
                       onclick="revokeShare('${x.id}')">회수</button>`}
              </div>`).join('') : ''}
          <div class="pane-sec">저장</div>
          <div class="slot-help">
            ${isLoggedIn()
              ? '작업 내용이 <b>서버에 저장</b>돼 다른 기기에서도 이어서 작업할 수 있습니다.'
              : '작업 내용은 <b>이 브라우저에만</b> 저장됩니다. <b>로그인하면 서버에 저장</b>돼 다른 기기에서도 이어집니다.'}
          </div>`;
    box.innerHTML = h;
}
function gotoScene(id) {
    state.currentScene = id;
    selectedIds.clear(); floorSel = null; three3Sel = null;
    saveState();
    applyEqEdits();
    switchMode(currentScene().mode || 'list');   // 선택한 씬의 모드로 전환하며 다시 그림
    renderScenePane();
}

// ───────── 배경 도면 크기/이동 ─────────
let bgMove = false;
function setBgWidth(v) {
    const f = F();
    if (!f.bg) return;
    const w = parseFloat(v);
    if (!w || w <= 0) return;
    const k = w / f.bg.w;
    f.bg.w = +w.toFixed(3);
    f.bg.h = +(f.bg.h * k).toFixed(3);
    saveState(); renderFloor(); syncBgUI();
}
function nudgeBg(k) {
    const f = F();
    if (!f.bg) { alert('배경 도면이 없습니다.'); return; }
    setBgWidth(f.bg.w * k);
}
function toggleBgMove() {
    const f = F();
    if (!f.bg) { alert('배경 도면이 없습니다.'); return; }
    bgMove = !bgMove;
    document.getElementById('bgmove-btn').classList.toggle('primary', bgMove);
    setStatus(bgMove ? '도면 이동 모드 — 도면을 드래그해 위치를 맞추세요'
                     : '도면 이동 모드 해제');
    renderFloor();
}
function syncBgUI() {
    const f = F();
    const el = document.getElementById('bg-w');
    if (!el) return;
    el.disabled = !f.bg;
    el.value = f.bg ? f.bg.w.toFixed(2) : '';
    const mb = document.getElementById('bgmove-btn');
    if (mb) mb.classList.toggle('primary', bgMove && !!f.bg);
}
function cycleBgOpacity() {
    const f = F();
    if (!f.bg) { alert('배경 도면이 없습니다.'); return; }
    const steps = [0.25, 0.55, 0.85];
    const i = steps.findIndex(s => Math.abs(s - f.bg.opacity) < 0.01);
    f.bg.opacity = steps[(i + 1) % steps.length];
    saveState(); renderFloor();
}

// ───────── 축척 보정 ─────────
function startCalibrate() {
    if (!F().bg) { alert('먼저 "🖼 배경 도면"으로 도면을 올려주세요.'); return; }
    floorMode = 'calib'; calibPts = [];
    setStatus('축척 보정: 길이를 아는 두 지점을 차례로 클릭하세요 (예: 문 폭, 벽 길이)');
    document.getElementById('floor-svg').style.cursor = 'crosshair';
}
function applyCalibration(p1, p2, realM) {
    const f = F();
    const cur = Math.hypot(p2.x - p1.x, p2.y - p1.y);
    if (cur < 0.01) return;
    const k = realM / cur;
    f.bg.w = +(f.bg.w * k).toFixed(3);
    f.bg.h = +(f.bg.h * k).toFixed(3);
    f.bg.x = +(f.bg.x * k).toFixed(3);
    f.bg.y = +(f.bg.y * k).toFixed(3);
    saveState(); renderFloor();
    setStatus(`축척 보정 완료 — 도면 실제 폭 ${f.bg.w.toFixed(1)}m`);
}

// ───────── 기타 조작 ─────────
function zoomFloor(k) {
    const f = F();
    f.zoom = Math.max(12, Math.min(160, Math.round(f.zoom * k)));
    saveState(); renderFloor();
}
function toggleClearance() {
    const f = F();
    f.showClear = !f.showClear;
    document.getElementById('clr-btn').textContent = f.showClear ? '◌ 여유공간 ON' : '◌ 여유공간 OFF';
    saveState(); renderFloor();
}
function deleteFloorMulti() {
    const f = F();
    let n = 0, blk = 0;
    fMulti.forEach(k => {
        if (f.items[k]) {
            blk += removeLayoutBlockFor(f.items[k].eqId);
            delete f.items[k]; n++;
        } else if ((f.subjects || []).some(x => x.id === k)) {
            f.subjects = f.subjects.filter(x => x.id !== k); n++;
        }
    });
    fMulti.clear();
    saveState(); renderFloor(); renderPalette(); renderCanvas();
    setStatus(`${n}개 삭제` + (blk ? ` · 배치도에서도 ${blk}개 내림` : ''));
}
// 평면도에서 내린 장비는 배치도에서도 내린다 (조립 부품은 남긴다)
function removeLayoutBlockFor(eqId) {
    const sc = currentScene();
    const hit = Object.entries(sc.blocks).find(([, b]) => b.eqId === eqId && !b.parent);
    if (!hit) return 0;
    childBlocks(hit[0], sc).forEach(cid => {
        const cb = sc.blocks[cid];
        delete cb.parent; delete cb.slot; delete cb.warn; delete cb.lx; delete cb.ly;
        cb.x = (cb.x || 0) + 40; cb.y = (cb.y || 0) + 150;
    });
    delete sc.blocks[hit[0]];
    return 1;
}
function deleteFloorSelection() {
    if (!floorSel) { alert('삭제할 항목을 먼저 클릭해 선택하세요.'); return; }
    const f = F();
    if (floorSel.type === 'item') delete f.items[floorSel.id];
    else if (floorSel.type === 'subject') f.subjects = (f.subjects || []).filter(x => x.id !== floorSel.id);
    else f.rooms = f.rooms.filter(r => r.id !== floorSel.id);
    floorSel = null;
    saveState(); renderFloor(); renderPalette();
}
function clearFloor() {
    if (!confirm('평면도의 장비와 공간을 모두 지울까요? (배경 도면은 유지)')) return;
    const f = F();
    f.items = {}; f.rooms = [];
    floorSel = null;
    saveState(); renderFloor(); renderPalette();
}
function rotateFloorSelection(deg) {
    if (!floorSel || floorSel.type !== 'item') return;
    const it = F().items[floorSel.id];
    it.rot = ((it.rot || 0) + deg) % 360;
    saveState(); renderFloor();
}
function editFloorSize() {
    if (!floorSel || floorSel.type !== 'item') return;
    const it = F().items[floorSel.id];
    const sz = itemSize(it);
    const w = parseFloat(prompt('가로 (m)', sz.w)); if (!w) return;
    const h = parseFloat(prompt('세로 (m)', sz.h)); if (!h) return;
    const c = parseFloat(prompt('작업 여유 반경 (m)', sz.clear));
    it.w = w; it.h = h; if (!isNaN(c)) it.clear = c;
    saveState(); renderFloor();
}

// ───────── 평면도 캔버스 이벤트 ─────────
(function initFloorEvents() {
    const wrap = document.getElementById('floor-wrap');
    const svg = document.getElementById('floor-svg');

    // 팔레트 드롭
    wrap.addEventListener('dragover', e => { e.preventDefault(); e.dataTransfer.dropEffect = 'copy'; });
    wrap.addEventListener('drop', e => {
        e.preventDefault();
        const p = toMeters(e);
        const setId = e.dataTransfer.getData('set-id');
        if (setId) { placeSetOnFloor(setId, p.x, p.y); return; }
        const eqId = e.dataTransfer.getData('eq-id');
        if (!eqId) return;
        if (addFloorItem(eqId, p.x, p.y)) { renderFloor(); renderPalette(); }
    });

    // 클릭 (방 그리기 / 축척 보정 / 선택 해제)
    let roomStart = null;
    svg.addEventListener('pointerdown', e => {
        if (e.button !== 0) return;
        const p = toMeters(e);
        if (floorMode === 'pen') { e.preventDefault(); penClick(p, e.shiftKey); return; }
        if (floorMode === 'room') { roomStart = p; return; }
        if (floorMode === 'calib') {
            calibPts.push(p);
            if (calibPts.length === 2) {
                const d = prompt('두 지점의 실제 거리 (m)', '1');
                const real = parseFloat(d);
                if (real > 0) applyCalibration(calibPts[0], calibPts[1], real);
                calibPts = []; floorMode = 'idle'; svg.style.cursor = '';
                updateStatus();
            }
            renderFloor();
            return;
        }
        if (e.target === svg || e.target.classList.contains('grid-line')
            || e.target.classList.contains('froom')) {
            if (spaceDown) startFloorPan(e);
            else if (e.target.classList.contains('froom')) return;   // 방은 기존 이동 유지
            else startFloorMarquee(e);
        }
    });
    // 펜툴 미리보기 (커서 추적)
    svg.addEventListener('pointermove', e => {
        if (floorMode !== 'pen' || penPts.length === 0) return;
        penCursor = penSnapPoint(toMeters(e), e.shiftKey);
        renderFloor();
    });
    svg.addEventListener('dblclick', e => {
        if (floorMode === 'pen' && penPts.length >= 3) { e.preventDefault(); finishPen(); }
    });

    svg.addEventListener('pointerup', e => {
        if (floorMode === 'room' && roomStart) {
            const p = toMeters(e);
            finishRoom(roomStart.x, roomStart.y, p.x, p.y);
            roomStart = null; floorMode = 'idle'; svg.style.cursor = '';
            updateStatus();
        }
    });

    // 키보드
    document.addEventListener('keydown', e => {
        if (currentScene().mode !== 'floor') return;
        const tag = (e.target.tagName || '').toLowerCase();
        if (tag === 'input' || tag === 'select' || e.target.isContentEditable) return;
        if (e.key === 'Escape') {
            cancelPen(); calibPts = []; floorMode = 'idle';
            svg.style.cursor = ''; renderFloor(); updateStatus(); return;
        }
        if (floorMode === 'pen') {
            if (e.key === 'Enter') { e.preventDefault(); finishPen(); }
            if (e.key === 'Backspace') { e.preventDefault(); undoPenPoint(); }
            return;
        }
        if ((e.key === 'Delete' || e.key === 'Backspace') && floorSel) { e.preventDefault(); deleteFloorSelection(); }
        if (e.key === 'r' || e.key === 'R') rotateFloorSelection(e.shiftKey ? -15 : 15);
        if (e.key === 'e' || e.key === 'E') editFloorSize();
        if (e.key === '+' || e.key === '=') addVertexToSelected();
        if (e.key === '-' || e.key === '_') removeVertexFromSelected();
    });
})();

// ═══════════════════════════════════════════════
//                   3D 모드
// ═══════════════════════════════════════════════
// 치수 스펙 (m). w=폭 d=깊이 h=높이, hMin/hMax=조절범위, src: spec=제조사공식 / est=추정
const SPECS = {
    // ── 카메라 (제조사 공식) ──
    'CAM-001': { w: 0.130, h: 0.078, d: 0.085, src: 'spec' },   // Sony FX3
    'CAM-002': { w: 0.153, h: 0.114, d: 0.116, src: 'est' },    // Sony FX6
    'CAM-003': { w: 0.131, h: 0.096, d: 0.080, src: 'spec' },   // Sony a7 IV
    'CAM-004': { w: 0.109, h: 0.156, d: 0.293, src: 'est' },    // PXW-Z90
    'CAM-005': { w: 0.131, h: 0.096, d: 0.080, src: 'est' },    // a7 V
    // ── 조명 헤드 (제조사 공식) ──
    'LIT-001': { w: 0.231, h: 0.231, d: 0.399, src: 'spec' },   // Forza 500
    'LIT-002': { w: 0.231, h: 0.231, d: 0.399, src: 'spec' },   // Forza 500B II
    'LIT-003': { w: 0.310, h: 0.620, d: 0.060, src: 'est' },    // Pavoslim 240B
    'LIT-004': { w: 0.360, h: 0.530, d: 0.090, src: 'est' },    // MixPanel 150
    'LIT-005': { w: 0.104, h: 0.084, d: 0.198, src: 'spec' },   // Forza 60B
    'LIT-006': { w: 0.104, h: 0.084, d: 0.198, src: 'spec' },   // Forza 60B II
    'LIT-007': { w: 0.055, h: 0.055, d: 0.530, src: 'est' },    // PavoTube
    'LIT-008': { w: 0.055, h: 0.055, d: 0.530, src: 'est' },
    'LIT-009': { w: 0.100, h: 0.090, d: 0.190, src: 'spec' },   // Godox AD300Pro
    'LIT-010': { w: 0.076, h: 0.190, d: 0.100, src: 'est' },    // Godox V1
    // ── 스탠드 (제조사 공식) ──
    'STD-A':  { w: 0.90, d: 0.90, h: 2.00, hMin: 1.08, hMax: 2.88, src: 'spec' },  // Nanlite LS-288 108~288cm
    'STD-AS': { w: 0.60, d: 0.60, h: 1.30, hMin: 0.49, hMax: 1.90, src: 'avg' },   // 컴팩트 스탠드 표준 49~190cm
    'STD-C':  { w: 1.05, d: 1.05, h: 2.20, hMin: 1.35, hMax: 3.20, arm: 1.02, src: 'spec' }, // Matthews 40" 최대 10.5ft
    'STD-T':  { w: 1.00, d: 1.00, h: 1.80, hMin: 1.00, hMax: 2.40, src: 'avg' },   // 배경 T스탠드 평균
    // ── 삼각대 (제조사 공식) ──
    'TRP-001': { w: 1.05, d: 1.05, h: 1.30, hMin: 0.435, hMax: 1.73, src: 'spec' },  // 504X+645FAST 10.6~61.8in
    'TRP-002': { w: 0.80, d: 0.80, h: 1.10, hMin: 0.43, hMax: 1.51, src: 'spec' },  // Befree Live 17~59.5in
    'TRP-003': { w: 0.90, d: 0.90, h: 1.20, hMin: 0.66, hMax: 1.75, src: 'spec' },  // Teris TSN6CF-Q PLUS 655~1745mm
    // ── 기타 주요 ──
    'GIM-001': { w: 0.202, h: 0.415, d: 0.268, src: 'spec' },   // DJI RS4 Pro
    'MON-001': { w: 0.504, h: 0.310, d: 0.063, dStand: 0.180, src: 'spec' },    // Atomos Sumo 19
    'MON-002': { w: 0.150, h: 0.090, d: 0.030, src: 'est' },    // Mars M1 5.5"
    'MOD-001': { w: 0.60, h: 0.60, d: 0.45, src: 'est' },       // Softbox 60B
    'MOD-002': { w: 0.90, h: 0.90, d: 0.70, src: 'est' },       // Softbox 500
    'MOD-003': { w: 0.85, h: 0.85, d: 0.85, src: 'est' },       // 젬볼
    'MOD-007': { w: 0.75, h: 0.90, d: 0.03, src: 'est' },       // 디퓨저 750×900
    'MOD-010': { w: 1.24, h: 0.60, d: 0.42, src: 'spec' },       // Triflector 반사판
    'ETC-001': { w: 0.60, h: 1.00, d: 0.95, src: 'est' },       // 카트
    'ETC-002': { w: 0.50, h: 1.25, d: 0.55, src: 'est' },       // 구르마
    'ETC-003': { w: 0.60, h: 0.95, d: 0.95, src: 'est' },       // 왜건
    'ETC-004': { w: 0.24, h: 0.06, d: 0.24, src: 'est' },       // 카운터웨이트
    'ETC-005': { w: 0.36, h: 0.14, d: 0.22, src: 'est' },       // 샌드백
    'ETC-011': { w: 0.30, h: 0.06, d: 0.20, src: 'est' },       // ATEM 스위처
    'ACC-015': { w: 3.00, h: 2.40, d: 0.02, src: 'est' },       // 크로마키
    // ── 카테고리 기본값 ──
    CAM: { w: 0.14, h: 0.10, d: 0.10 }, LEN: { w: 0.09, h: 0.09, d: 0.13 },
    LIT: { w: 0.22, h: 0.22, d: 0.30 }, MOD: { w: 0.80, h: 0.80, d: 0.50 },
    STD: { w: 0.90, d: 0.90, h: 2.00, hMin: 1.00, hMax: 2.80 },
    TRP: { w: 0.95, d: 0.95, h: 1.20, hMin: 0.50, hMax: 1.60 },
    GIM: { w: 0.20, h: 0.40, d: 0.26 }, AUD: { w: 0.08, h: 0.08, d: 0.25 },
    MON: { w: 0.30, h: 0.20, d: 0.05 }, BAT: { w: 0.15, h: 0.08, d: 0.10 },
    PWR: { w: 0.30, h: 0.18, d: 0.30 }, STO: { w: 0.05, h: 0.01, d: 0.06 },
    CAB: { w: 0.28, h: 0.10, d: 0.28 }, ACC: { w: 0.25, h: 0.15, d: 0.25 },
    ETC: { w: 0.45, h: 0.40, d: 0.45 }
};
const SPEC_KEYS = Object.keys(SPECS).sort((a, b) => b.length - a.length);

function specOf(eqId) {
    if (SPECS[eqId]) return SPECS[eqId];
    for (const k of SPEC_KEYS) if (eqId.startsWith(k) && k.length > 3) return SPECS[k];
    const eq = EQUIPMENT.find(e => e.id === eqId);
    return SPECS[eq ? eq.cat : 'ETC'] || SPECS.ETC;
}
// 스탠드/삼각대에 올라가는 장비 → 기본 설치 높이
const MOUNTED = { LIT: 2.0, MOD: 1.85, CAM: 1.45, MON: 1.30 };
function defaultHeight(eq) {
    if (eq.cat === 'STD' || eq.cat === 'TRP') return specOf(eq.id).h;
    return MOUNTED[eq.cat] !== undefined ? MOUNTED[eq.cat] : 0;
}
// 렌즈 초점거리 추출 ("Sony 24-70 F2.8 GM" → [24,70])
// 렌즈 최대개방 조리개 (F2.8 → 2.8)
function apertureOf(eq) {
    const m = (eq.product || eq.model || '').match(/F\s*\/?\s*([\d.]+)/i);
    return m ? +m[1] : null;
}
// 실제 존재하는 조리개 단으로 맞춤 (아래로는 내려가지 않게)
function snapFstop(v) {
    let best = FSTOPS[0];
    for (const f of FSTOPS) if (f <= v + 0.001) best = f;
    return Math.abs(v - best) < 0.001 ? best : (FSTOPS.find(f => f >= v) || FSTOPS[0]);
}
// 조립체에 물린 렌즈 → 초점거리 범위 · 최대개방
function lensSpecOf(item) {
    const p = (item.parts || []).find(x => {
        const e = EQUIPMENT.find(q => q.id === x.eqId);
        return e && e.cat === 'LEN';
    });
    if (!p) return null;
    const le = EQUIPMENT.find(q => q.id === p.eqId);
    if (!le) return null;
    const fr = focalOf(le), ap = apertureOf(le);
    return { id: le.id, name: dispName(le),
             min: fr ? fr[0] : null, max: fr ? fr[1] : null,
             wide: ap, zoom: fr ? fr[0] !== fr[1] : false };
}
// 렌즈 스펙을 카메라 항목에 적용
function applyLensSpec(item) {
    const L = lensSpecOf(item);
    if (!L) return null;
    item.lens = L.id;
    if (L.min) {
        item.focalMin = L.min; item.focalMax = L.max;
        // 줌이면 광각단, 단렌즈면 그 값
        if (item.focal == null || item.focal < L.min || item.focal > L.max)
            item.focal = L.zoom ? L.min : L.min;
    }
    if (L.wide) {
        item.fMin = snapFstop(L.wide);
        if (item.fstop == null || item.fstop < item.fMin) item.fstop = item.fMin;
    }
    return L;
}
function focalOf(eq) {
    const m = (eq.product || '').match(/(\d{1,3})\s*-\s*(\d{1,3})/);
    if (m) return [+m[1], +m[2]];
    const s = (eq.product || '').match(/(\d{1,3})\s*mm/i);
    if (s) return [+s[1], +s[1]];
    return null;
}

let R3 = null;        // {renderer, scene, cam, ...}
let three3Sel = null; // 선택된 fid
let frustumOn = true, shadowsOn = true, focalMM = 35;
let previewOn = true, previewAR = 1.7778, previewScale = 0.34, guidesOn = true, dofOn = true;
const PV_SIZES = [0.26, 0.34, 0.46, 0.62];

// 현재 조작 대상 카메라 [fid, item] — 선택된 게 카메라면 그것, 아니면 첫 카메라
function activeCam() {
    const f = ensureFloor(currentScene());
    if (three3Sel && f.items[three3Sel]) {
        const eq = EQUIPMENT.find(e => e.id === f.items[three3Sel].eqId);
        if (eq && eq.cat === 'CAM') return [three3Sel, f.items[three3Sel]];
    }
    for (const [fid, it] of Object.entries(f.items)) {
        const eq = EQUIPMENT.find(e => e.id === it.eqId);
        if (eq && eq.cat === 'CAM') return [fid, it];
    }
    return [null, null];
}
function camDir(it) {
    const p = (it.pan || 0) * Math.PI / 180, t = (it.tilt || 0) * Math.PI / 180;
    return { x: Math.sin(p) * Math.cos(t), y: Math.sin(t), z: Math.cos(p) * Math.cos(t) };
}
function camEyeY(it) { return (it.h3 || 1.45) + 0.09; }

// ───────── 조리개 · 피사계 심도 ─────────
const FSTOPS = [1.2, 1.4, 1.8, 2.0, 2.8, 4.0, 5.6, 8.0, 11, 16, 22];
const COC_FF = 0.029;   // 풀프레임 허용 착란원(mm)

// 가장 가까운 피사체까지 거리 (없으면 null)
function nearestSubjectDist(f, it) {
    const subs = (f.subjects || []);
    if (!subs.length || !it) return null;
    let bd = Infinity;
    subs.forEach(s => { const d = Math.hypot(s.x - it.x, s.y - it.y); if (d < bd) bd = d; });
    return bd;
}
function focusDistOf(f, it) {
    if (it.focus) return it.focus;
    const d = nearestSubjectDist(f, it);
    return d !== null ? +d.toFixed(2) : 3.0;
}
// 심도 계산 (모두 m 단위 반환)
function dofOf(focalMM, fstop, focusM) {
    const f = focalMM, N = fstop, c = COC_FF;
    const H = (f * f) / (N * c) + f;              // 과초점거리 (mm)
    const s = focusM * 1000;                       // 초점거리 (mm)
    const near = (s * (H - f)) / (H + s - 2 * f);
    const denom = H - s;
    const far = denom <= 0 ? Infinity : (s * (H - f)) / denom;
    return {
        hyper: H / 1000,
        near: near / 1000,
        far: far === Infinity ? Infinity : far / 1000,
        total: far === Infinity ? Infinity : (far - near) / 1000
    };
}

function ensure3D(scene) {
    const f = ensureFloor(scene);
    if (f.ceilH === undefined) f.ceilH = 2.7;
    for (const it of Object.values(f.items)) {
        if (it.h3 === undefined) {
            const eq = EQUIPMENT.find(e => e.id === it.eqId);
            it.h3 = eq ? defaultHeight(eq) : 0;
        }
    }
    return f;
}

// ───────── 초기화 ─────────
function init3D() {
    if (R3) return true;
    if (typeof THREE === 'undefined') { alert('3D 라이브러리를 불러오지 못했습니다.'); return false; }
    const canvas = document.getElementById('three-canvas');
    let renderer;
    try {
        renderer = new THREE.WebGLRenderer({
            canvas, antialias: true, preserveDrawingBuffer: true
        });
        renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.outputColorSpace = THREE.SRGBColorSpace;
    } catch (err) {
        console.warn('WebGL 초기화 실패', err);
        const el = document.getElementById('three-sel');
        if (el) el.textContent = '이 브라우저/기기에서 3D(WebGL)를 사용할 수 없습니다.';
        return false;
    }

    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;

    const scene = new THREE.Scene();
    scene.background = gradientSky();
    scene.fog = new THREE.Fog(0x11161d, 22, 65);
    const cam = new THREE.PerspectiveCamera(45, 1, 0.05, 200);
    const pvCam = new THREE.PerspectiveCamera(40, 1.7778, 0.05, 200);

    // 3점 조명 세팅 (장면 자체를 보기 좋게)
    scene.add(new THREE.HemisphereLight(0xa8c4e8, 0x20242b, 0.85));
    const key = new THREE.DirectionalLight(0xfff4e6, 1.05);
    key.position.set(7, 12, 5);
    key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048);
    key.shadow.camera.near = 1; key.shadow.camera.far = 45;
    key.shadow.camera.left = -16; key.shadow.camera.right = 16;
    key.shadow.camera.top = 16; key.shadow.camera.bottom = -16;
    key.shadow.bias = -0.0012;
    key.shadow.normalBias = 0.02;
    scene.add(key);
    const fill = new THREE.DirectionalLight(0x9fc2ff, 0.32);
    fill.position.set(-8, 6, -6);
    scene.add(fill);
    const rim = new THREE.DirectionalLight(0xffd9b0, 0.28);
    rim.position.set(-3, 4, 10);
    scene.add(rim);

    R3 = {
        renderer, scene, cam, pvCam,
        world: new THREE.Group(),      // 방 + 장비
        picks: [],                     // 레이캐스트 대상
        orbit: { tx: 4, ty: 1.2, tz: 3, dist: 11, theta: -0.9, phi: 1.05 },
        ray: new THREE.Raycaster(),
        frustum: null, lights: []
    };
    scene.add(R3.world);
    attachOrbit(canvas);
    (function loop() { requestAnimationFrame(loop); draw3D(); })();
    return true;
}

function resize3D(retry) {
    if (!R3) return;
    setTimeout(syncPreviewFrame, 0);
    const w = document.getElementById('three-wrap');
    let W = w.clientWidth, H = w.clientHeight;
    // 레이아웃이 아직 잡히지 않은 첫 프레임 → 다음 프레임에 재시도
    if ((!W || !H) && !retry && typeof requestAnimationFrame === 'function') {
        requestAnimationFrame(() => resize3D(true));
        W = W || 900; H = H || 620;
    }
    W = W || 900; H = H || 620;
    R3.renderer.setSize(W, H, false);
    R3.cam.aspect = W / H;
    R3.cam.updateProjectionMatrix();
}
window.addEventListener('resize', resize3D);

function draw3D() {
    if (!R3 || currentScene().mode !== 'three') return;
    const now = (typeof performance !== 'undefined' ? performance.now() : Date.now()) / 1000;
    const dt = Math.min(0.05, navLast ? now - navLast : 0.016);
    navLast = now;
    stepNav(dt);

    const o = R3.orbit;
    if (walkMode && R3.walk) {
        const w = R3.walk;
        w.pitch = Math.max(-1.3, Math.min(1.3, w.pitch));
        R3.cam.position.set(w.x, w.eye, w.z);
        R3.cam.lookAt(
            w.x - Math.sin(w.yaw) * Math.cos(w.pitch),
            w.eye + Math.sin(w.pitch),
            w.z - Math.cos(w.yaw) * Math.cos(w.pitch));
    } else {
        o.phi = Math.max(0.08, Math.min(Math.PI - 0.08, o.phi));
        R3.cam.position.set(
            o.tx + o.dist * Math.sin(o.phi) * Math.cos(o.theta),
            o.ty + o.dist * Math.cos(o.phi),
            o.tz + o.dist * Math.sin(o.phi) * Math.sin(o.theta)
        );
        R3.cam.lookAt(o.tx, o.ty, o.tz);
    }

    const size = R3.renderer.getSize(new THREE.Vector2());
    const W = size.x, H = size.y;
    R3.renderer.setScissorTest(false);
    R3.renderer.setViewport(0, 0, W, H);
    R3.renderer.setScissor(0, 0, W, H);
    R3.renderer.autoClear = true;
    if (R3.giz) {
        const gd = walkMode && R3.walk
            ? R3.cam.position.distanceTo(R3.giz.position) : R3.orbit.dist;
        R3.giz.scale.setScalar(Math.max(0.35, gd * 0.115));
    }
    R3.renderer.render(R3.scene, R3.cam);

    // ── 카메라 프리뷰 (PiP) ──
    const [fid, it] = activeCam();
    const box = previewBox(W, H);
    if (previewOn && it && box) {
        const eyeY = camEyeY(it), d = camDir(it);
        R3.pvCam.position.set(it.x, eyeY, it.y);
        R3.pvCam.lookAt(it.x + d.x, eyeY + d.y, it.y + d.z);
        // 초점거리 → 수직 화각 (풀프레임 24mm 높이 기준, 화면비 반영)
        const fl = it.focal || focalMM;
        const sensorW = 0.036, sensorH = sensorW / previewAR;
        R3.pvCam.fov = 2 * Math.atan(sensorH / (2 * fl / 1000)) * 180 / Math.PI;
        R3.pvCam.aspect = previewAR;
        R3.pvCam.updateProjectionMatrix();
        // 카메라 자신의 몸체·프러스텀·기즈모는 프리뷰에 찍히면 안 됨
        // (렌즈 바로 앞이라 '렌즈캡'처럼 화면을 가림)
        const hid = [];
        const own = R3.picks.find(m => m.userData.fid === fid);
        if (own) hid.push(own);
        if (R3.frustum) hid.push(R3.frustum);
        if (R3.giz) hid.push(R3.giz);
        (R3.helpers || []).forEach(h => hid.push(h));
        const vis = hid.map(m => m.visible);
        hid.forEach(m => { m.visible = false; });

        R3.renderer.setScissorTest(true);
        R3.renderer.setViewport(box.x, box.y, box.w, box.h);
        R3.renderer.setScissor(box.x, box.y, box.w, box.h);
        R3.renderer.autoClear = false;
        R3.renderer.clearDepth();
        R3.renderer.render(R3.scene, R3.pvCam);
        R3.renderer.setScissorTest(false);
        R3.renderer.autoClear = true;

        hid.forEach((m, i) => { m.visible = vis[i]; });
    }
}
// 프리뷰 사각형 (WebGL 좌표: 좌하단 원점)
function previewBox(W, H) {
    if (!W || !H) return null;
    const pw = Math.round(W * previewScale);
    const ph = Math.round(pw / previewAR);
    if (ph > H * 0.85) {
        const ph2 = Math.round(H * 0.85);
        return { x: W - Math.round(ph2 * previewAR) - 14, y: 14,
                 w: Math.round(ph2 * previewAR), h: ph2 };
    }
    return { x: W - pw - 14, y: 14, w: pw, h: ph };
}
// CSS 오버레이(테두리·가이드) 위치 갱신
function syncPreviewFrame() {
    const el = document.getElementById('pv-frame');
    const lab = document.getElementById('pv-label');
    const g = document.getElementById('pv-guides');
    if (!el) return;
    const [fid, it] = activeCam();
    const wrap = document.getElementById('three-wrap');
    const W = wrap.clientWidth, H = wrap.clientHeight;
    const box = previewBox(W, H);
    if (!previewOn || !it || !box) { el.style.display = 'none'; return; }
    el.style.display = 'block';
    el.style.left = box.x + 'px';
    el.style.top = (H - box.y - box.h) + 'px';   // CSS는 위쪽 원점
    el.style.width = box.w + 'px';
    el.style.height = box.h + 'px';
    g.className = guidesOn ? 'on' : '';
    const eq = EQUIPMENT.find(e => e.id === it.eqId);
    const sel = document.getElementById('cp-ar');
    const opt = sel && sel.options ? sel.options[sel.selectedIndex] : null;
    const arTxt = opt && opt.text ? opt.text : previewAR.toFixed(2) + ':1';
    const fsv = it.fstop || 2.8;
    lab.textContent = `${eq ? dispName(eq) : '카메라'} · ${it.focal || focalMM}mm `
        + `F${fsv < 10 ? fsv.toFixed(1) : fsv} · ${arTxt} · H ${(it.h3 || 0).toFixed(2)}m`;
}

// ───────── 궤도 조작 ─────────
// ───────── 이동 기즈모 (X/Y/Z 축) ─────────
const GIZ_COL = { x: 0xff5f70, y: 0x5ad696, z: 0x5b9dff };
function buildGizmo(flat) {
    const g = new THREE.Group();
    g.name = 'gizmo';
    (flat ? ['x', 'z'] : ['x', 'y', 'z']).forEach(ax => {
        const arm = new THREE.Group();
        const m = new THREE.MeshBasicMaterial({ color: GIZ_COL[ax], depthTest: false, transparent: true, opacity: 0.96 });
        const sh = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.52, 10), m);
        sh.position.y = 0.26;
        const hd = new THREE.Mesh(new THREE.ConeGeometry(0.052, 0.15, 16), m);
        hd.position.y = 0.60;
        const hit = new THREE.Mesh(new THREE.CylinderGeometry(0.085, 0.085, 0.7, 6),
            new THREE.MeshBasicMaterial({ visible: false }));
        hit.position.y = 0.35;
        [sh, hd, hit].forEach(x => { x.renderOrder = 998; x.userData.giz = ax; arm.add(x); });
        if (ax === 'x') arm.rotation.z = -Math.PI / 2;
        if (ax === 'z') arm.rotation.x = Math.PI / 2;
        g.add(arm);
    });
    // 중심 구
    const c = new THREE.Mesh(new THREE.SphereGeometry(0.05, 14, 10),
        new THREE.MeshBasicMaterial({ color: 0xffffff, depthTest: false, transparent: true, opacity: 0.9 }));
    c.renderOrder = 998;
    g.add(c);
    return g;
}
function gizRay(e) {
    const c = R3.renderer.domElement, r = c.getBoundingClientRect();
    R3.ray.setFromCamera(new THREE.Vector2(
        ((e.clientX - r.left) / r.width) * 2 - 1,
        -((e.clientY - r.top) / r.height) * 2 + 1), R3.cam);
    return R3.ray.ray;
}
function pickGizmo(e) {
    if (!R3 || !R3.giz) return null;
    gizRay(e);
    const h = R3.ray.intersectObjects(R3.giz.children, true);
    return h.length ? h[0].object.userData.giz : null;
}
// 마우스 광선과 축 직선의 최근접점 → 축 위 스칼라 t
function axisT(e, origin, dir) {
    const ray = gizRay(e);
    const w0 = new THREE.Vector3().subVectors(origin, ray.origin);
    const a = dir.dot(dir), b = dir.dot(ray.direction), c = ray.direction.dot(ray.direction);
    const d = dir.dot(w0), f2 = ray.direction.dot(w0);
    const den = a * c - b * b;
    if (Math.abs(den) < 1e-7) return null;
    return (b * f2 - c * d) / den;
}
let gizDrag = null, freeDrag = null;
// 광선 ↔ 수평면 교점
function rayPlaneY(e, y) {
    const ray = gizRay(e);
    if (Math.abs(ray.direction.y) < 1e-6) return null;
    const t = (y - ray.origin.y) / ray.direction.y;
    if (t < 0) return null;
    return ray.origin.clone().addScaledVector(ray.direction, t);
}
function startFreeDrag(e, fid) {
    if (isViewOnly()) return false;
    const so = selObj(fid);
    if (!so) return false;
    const it = so.o;
    const p = rayPlaneY(e, so.kind === 'subj' ? 0 : (it.h3 || 0));
    if (!p) return false;
    freeDrag = { it, fid, ox: it.x, oy: it.y, px: p.x, pz: p.z, moved: false,
                 mesh: R3.picks.find(m => m.userData.fid === fid) };
    return true;
}
function moveFreeDrag(e) {
    if (!freeDrag) return;
    const p = rayPlaneY(e, isSubjKey(freeDrag.fid) ? 0 : (freeDrag.it.h3 || 0));
    if (!p) return;
    const it = freeDrag.it;
    let nx = freeDrag.ox + (p.x - freeDrag.px), ny = freeDrag.oy + (p.z - freeDrag.pz);
    if (Math.abs(p.x - freeDrag.px) > 0.02 || Math.abs(p.z - freeDrag.pz) > 0.02) freeDrag.moved = true;
    if (snapEnabled) { nx = Math.round(nx * 20) / 20; ny = Math.round(ny * 20) / 20; }
    it.x = +nx.toFixed(2); it.y = +ny.toFixed(2);
    if (isSubjKey(freeDrag.fid)) confineSubject(it); else confineItem(it);
    const baseY = isSubjKey(freeDrag.fid) ? 0 : (it.h3 || 0);
    if (freeDrag.mesh) freeDrag.mesh.position.set(it.x, baseY, it.y);
    if (R3.giz) R3.giz.position.set(it.x, baseY + 0.06, it.y);
    (R3.helpers || []).forEach(h => { if (h.position) h.position.x = it.x, h.position.z = it.y; });
    syncItemPanel(it);
}
function endFreeDrag() {
    if (!freeDrag) return;
    const moved = freeDrag.moved;
    freeDrag = null;
    saveState(); build3D(); showSel(); updateCamPanel();
    if (moved) setStatus('위치를 옮겼습니다');
}
const AXV = { x: new THREE.Vector3(1, 0, 0), y: new THREE.Vector3(0, 1, 0), z: new THREE.Vector3(0, 0, 1) };
// 3D에서 선택된 대상 (장비 또는 피사체)
function selObj(key) {
    key = key === undefined ? three3Sel : key;
    if (!key) return null;
    const f = ensure3D(currentScene());
    if (String(key).startsWith('s:')) {
        const sj = (f.subjects || []).find(x => x.id === String(key).slice(2));
        return sj ? { kind: 'subj', o: sj } : null;
    }
    return f.items[key] ? { kind: 'item', o: f.items[key] } : null;
}
function isSubjKey(k) { return String(k || '').startsWith('s:'); }

function hRange(it) {
    const f = ensure3D(currentScene());
    const ceil = f.ceilH || 2.7;
    // ① 조립된 지지대(삼각대·스탠드)의 조절 범위
    const rg = rigRange(it);
    if (rg) return [rg.min, +Math.min(rg.max, ceil - 0.05).toFixed(3)];
    const sp = specOf(it.eqId) || {};
    // ② 자기 자신이 높이 조절되는 장비 (삼각대·스탠드를 단독으로 놓은 경우)
    if (sp.hMin !== undefined) return [sp.hMin, +Math.min(sp.hMax, ceil - 0.05).toFixed(3)];
    // ③ 그 외에는 바닥~천장
    return [0, +Math.max(0, ceil - (sp.h || 0.2)).toFixed(3)];
}
// 높이 범위의 출처 설명 (패널에 표시)
function hRangeSrc(it) {
    const rg = rigRange(it);
    if (rg) return { kind: 'rig', id: rg.src, label: `${rg.src} 조절 범위` };
    const sp = specOf(it.eqId) || {};
    if (sp.hMin !== undefined) return { kind: 'self', id: it.eqId, label: '이 장비의 조절 범위' };
    return { kind: 'ceil', id: null, label: '천장 기준' };
}
function startGizDrag(e, ax) {
    if (isViewOnly()) return;
    const so = selObj();
    if (!so) return;
    const it = so.o;
    const org = new THREE.Vector3(it.x, so.kind === 'subj' ? 0 : (it.h3 || 0), it.y);
    const t0 = axisT(e, org, AXV[ax]);
    if (t0 == null) return;
    gizDrag = { ax, it, org, t0, sx: it.x, sy: it.y, sh: it.h3 || 0,
                mesh: R3.picks.find(m => m.userData.fid === three3Sel) };
    setStatus(`${ax.toUpperCase()}축 이동 중 — 놓으면 확정`);
}
function moveGizDrag(e) {
    if (!gizDrag) return;
    const t = axisT(e, gizDrag.org, AXV[gizDrag.ax]);
    if (t == null) return;
    const d = t - gizDrag.t0, it = gizDrag.it;
    if (gizDrag.ax === 'x') { it.x = +(gizDrag.sx + d).toFixed(2);
        isSubjKey(three3Sel) ? confineSubject(it) : confineItem(it); }
    else if (gizDrag.ax === 'z') { it.y = +(gizDrag.sy + d).toFixed(2);
        isSubjKey(three3Sel) ? confineSubject(it) : confineItem(it); }
    else if (!isSubjKey(three3Sel)) {
        const [lo, hi] = hRange(it); it.h3 = +Math.max(lo, Math.min(hi, gizDrag.sh + d)).toFixed(2);
    }
    // 프레임 단위로는 메시만 옮겨서 부드럽게
    const by = isSubjKey(three3Sel) ? 0 : (it.h3 || 0);
    if (gizDrag.mesh) gizDrag.mesh.position.set(it.x, by, it.y);
    if (R3.giz) R3.giz.position.set(it.x, by + 0.06, it.y);
    syncItemPanel(it);
}
function endGizDrag() {
    if (!gizDrag) return;
    gizDrag = null;
    saveState(); build3D(); showSel(); updateCamPanel();
    setStatus('위치를 옮겼습니다');
}

function attachOrbit(canvas) {
    let mode = null, lx = 0, ly = 0;
    canvas.addEventListener('contextmenu', e => e.preventDefault());
    canvas.addEventListener('pointerdown', e => {
        lx = e.clientX; ly = e.clientY;
        if (e.button === 0 && !e.shiftKey) {
            const ax = pickGizmo(e);
            if (ax) { startGizDrag(e, ax); canvas.setPointerCapture(e.pointerId); return; }
            // 장비를 직접 잡으면 바닥 위에서 자유 이동
            const fid = pick3D(e);
            if (fid && startFreeDrag(e, fid)) {
                canvas.style.cursor = 'grabbing';
                canvas.setPointerCapture(e.pointerId);
                return;
            }
        }
        mode = (e.button === 2 || e.shiftKey) ? 'pan' : 'rot';
        canvas.setPointerCapture(e.pointerId);
    });
    canvas.addEventListener('pointermove', e => {
        if (gizDrag) { moveGizDrag(e); return; }
        if (freeDrag) { moveFreeDrag(e); return; }
        if (!mode) {
            if (R3) canvas.style.cursor = pickGizmo(e) ? 'grab' : (hoverItem(e) ? 'move' : '');
            return;
        }
        const dx = e.clientX - lx, dy = e.clientY - ly;
        lx = e.clientX; ly = e.clientY;
        if (walkMode && R3.walk) {
            const w = R3.walk;
            if (mode === 'rot') { w.yaw -= dx * 0.005; w.pitch -= dy * 0.004; }
            else { w.x += (-Math.sin(w.yaw) * dy * 0.012 + Math.cos(w.yaw) * -dx * 0.012);
                   w.z += (-Math.cos(w.yaw) * dy * 0.012 - Math.sin(w.yaw) * -dx * 0.012); }
            return;
        }
        const o = R3.orbit;
        if (mode === 'rot') { o.theta += dx * 0.006; o.phi -= dy * 0.006; }
        else {
            const k = o.dist * 0.0018;
            const b = viewBasis(o.theta);
            // 오른쪽으로 끌면 바닥이 오른쪽으로 → 시점은 왼쪽으로
            o.tx -= (b.rx * dx + b.fx * dy) * k;
            o.tz -= (b.rz * dx + b.fz * dy) * k;
        }
    });
    const stop = () => { mode = null; canvas.style.cursor = '';
        if (gizDrag) endGizDrag(); if (freeDrag) endFreeDrag(); };
    canvas.addEventListener('pointerup', stop);
    canvas.addEventListener('pointercancel', stop);
    canvas.addEventListener('wheel', e => {
        e.preventDefault();
        if (walkMode && R3.walk) {
            const f = ensure3D(currentScene());
            R3.walk.eye = Math.max(0.25, Math.min((f.ceilH || 2.7) - 0.12,
                R3.walk.eye - e.deltaY * 0.0016));
            return;
        }
        R3.orbit.dist = Math.max(1.2, Math.min(60, R3.orbit.dist * (e.deltaY > 0 ? 1.1 : 0.9)));
    }, { passive: false });
}

// ───────── 재질 ─────────
const MAT = {};
function mat(hex, opts) {
    const k = hex + JSON.stringify(opts || {});
    if (!MAT[k]) MAT[k] = new THREE.MeshStandardMaterial(
        Object.assign({ color: hex, roughness: 0.72, metalness: 0.12 }, opts || {}));
    return MAT[k];
}
const M = {
    alu:    () => mat(0xb4bcc6, { metalness: 0.88, roughness: 0.32 }),   // 알루미늄 리저
    aluDk:  () => mat(0x767e88, { metalness: 0.8, roughness: 0.42 }),    // 어두운 금속
    black:  () => mat(0x22262c, { metalness: 0.35, roughness: 0.55 }),   // 무광 블랙 플라스틱
    rubber: () => mat(0x15181c, { metalness: 0.05, roughness: 0.92 }),   // 고무 발
    knob:   () => mat(0x2f343b, { metalness: 0.45, roughness: 0.45 }),
    diff:   () => mat(0xfdf6e8, { emissive: 0xfff0d4, emissiveIntensity: 0.9, roughness: 0.9 }),
    glass:  () => mat(0x0e1116, { metalness: 0.6, roughness: 0.12 }),
    skin:   () => mat(0x6fd6a4, { roughness: 0.65, metalness: 0.02 }),
    cloth:  () => mat(0x3f8f6d, { roughness: 0.9, metalness: 0.0 }),
    chrome: () => mat(0xdde3ea, { metalness: 0.97, roughness: 0.14 }),   // C스탠드 크롬
    chromeD:() => mat(0xa9b2bd, { metalness: 0.95, roughness: 0.24 }),
    manne:  () => mat(0xe8e6e2, { roughness: 0.55, metalness: 0.03 }),   // 데생 인형 몸통
    manneJ: () => mat(0xcfccc6, { roughness: 0.45, metalness: 0.06 }),   // 관절
    sbOut:  () => mat(0x14161a, { roughness: 0.94, metalness: 0.02 }),   // 소프트박스 외피
    sbRib:  () => mat(0xc8ced6, { metalness: 0.85, roughness: 0.3 })     // 지지살
};
function tint(cat, o) {
    return mat(parseInt((CAT_COLORS[cat] || '#999999').slice(1), 16),
        Object.assign({ metalness: 0.3, roughness: 0.5 }, o || {}));
}
function addMesh(g, geo, m, x, y, z, cast) {
    const me = new THREE.Mesh(geo, m);
    me.position.set(x || 0, y || 0, z || 0);
    me.castShadow = cast !== false; me.receiveShadow = true;
    g.add(me); return me;
}
// 배경 그라디언트
function gradientSky() {
    const c = document.createElement('canvas');
    c.width = 4; c.height = 256;
    const ctx2 = (c && typeof c.getContext === 'function') ? c.getContext('2d') : null;
    if (!ctx2 || typeof ctx2.createLinearGradient !== 'function') return new THREE.Color(0x121821);
    const g = ctx2.createLinearGradient(0, 0, 0, 256);
    g.addColorStop(0.0, '#20293a');
    g.addColorStop(0.55, '#141a23');
    g.addColorStop(1.0, '#0a0d12');
    ctx2.fillStyle = g;
    ctx2.fillRect(0, 0, 4, 256);
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
}

// ───────── 부품 빌더 ─────────
// 삼각대/스탠드 다리 (2단 + 고무발)



// ───────── Atomos SUMO 19 (19" 모니터-리코더) ─────────
// 공식 치수 504 × 310 × 63mm, 데스크 스탠드 포함 깊이 180mm
function sumoMonitor(sp, withFeet) {
    const g = new THREE.Group();
    const W = sp.w || 0.504, H = sp.h || 0.310, D = sp.d || 0.063;
    const bez = 0.030;                       // 고무 베젤 두께
    const shell = mat(0x24272c, { roughness: 0.62, metalness: 0.35 });
    const rub = mat(0x17191d, { roughness: 0.93, metalness: 0.05 });

    // 본체
    const body = new THREE.Mesh(new THREE.BoxGeometry(W, H, D), shell);
    body.position.y = H / 2; body.castShadow = true;
    g.add(body);
    // 고무 아머 (모서리·상하 범퍼)
    [[-1, 1], [1, 1], [-1, -1], [1, -1]].forEach(([sx, sy]) => {
        const c = new THREE.Mesh(new THREE.BoxGeometry(0.062, 0.052, D + 0.012), rub);
        c.position.set(sx * (W / 2 - 0.031), H / 2 + sy * (H / 2 - 0.026), 0);
        g.add(c);
    });
    [1, -1].forEach(sy => {
        const bar = new THREE.Mesh(new THREE.BoxGeometry(W - 0.12, 0.016, D + 0.008), rub);
        bar.position.set(0, H / 2 + sy * (H / 2 - 0.008), 0);
        g.add(bar);
    });
    // 화면 (16:9)
    const sw = W - bez * 2, shh = sw / (16 / 9);
    const screen = new THREE.Mesh(new THREE.PlaneGeometry(sw, shh),
        mat(0x101820, { roughness: 0.16, metalness: 0.5,
                        emissive: 0x1d3a52, emissiveIntensity: 0.5 }));
    screen.position.set(0, H / 2 + 0.012, D / 2 + 0.002);
    g.add(screen);
    // 하단 조작바 + ATOMOS 로고 자리
    const bar2 = new THREE.Mesh(new THREE.BoxGeometry(sw, 0.028, 0.004),
        mat(0x1b1e23, { roughness: 0.7 }));
    bar2.position.set(0, H / 2 - shh / 2 - 0.004, D / 2 + 0.003);
    g.add(bar2);
    const dot = new THREE.Mesh(new THREE.CircleGeometry(0.011, 16),
        mat(0x9aa6b4, { roughness: 0.4, metalness: 0.6 }));
    dot.position.set(0, H / 2 - shh / 2 - 0.004, D / 2 + 0.006);
    g.add(dot);

    // 뒷면: V마운트 배터리 플레이트 2개
    [-1, 1].forEach(sx => {
        const pl = new THREE.Mesh(new THREE.BoxGeometry(0.098, 0.135, 0.026),
            mat(0x1c1f24, { roughness: 0.7 }));
        pl.position.set(sx * 0.115, H / 2 + 0.045, -D / 2 - 0.013);
        g.add(pl);
        const bt = new THREE.Mesh(new THREE.BoxGeometry(0.088, 0.125, 0.042),
            mat(0x141619, { roughness: 0.8 }));
        bt.position.set(sx * 0.115, H / 2 + 0.045, -D / 2 - 0.047);
        bt.castShadow = true;
        g.add(bt);
    });
    // 방열 팬 그릴
    const fan = new THREE.Mesh(new THREE.CylinderGeometry(0.026, 0.026, 0.006, 16),
        mat(0x101215, { roughness: 0.9 }));
    fan.rotation.x = Math.PI / 2;
    fan.position.set(-0.055, H / 2 + 0.088, -D / 2 - 0.004);
    g.add(fan);
    // SDI BNC 6개 + XLR 3개
    for (let i = 0; i < 6; i++) {
        const bnc = new THREE.Mesh(new THREE.CylinderGeometry(0.0075, 0.0075, 0.016, 10),
            mat(0xb9c1cb, { metalness: 0.9, roughness: 0.3 }));
        bnc.rotation.x = Math.PI / 2;
        bnc.position.set(-W / 2 + 0.055 + i * 0.021, H / 2 - 0.095, -D / 2 - 0.008);
        g.add(bnc);
    }
    for (let i = 0; i < 3; i++) {
        const xlr = new THREE.Mesh(new THREE.CylinderGeometry(0.0115, 0.0115, 0.018, 12),
            mat(0x1a1d21, { roughness: 0.65 }));
        xlr.rotation.x = Math.PI / 2;
        xlr.position.set(0.075 + i * 0.036, H / 2 - 0.098, -D / 2 - 0.009);
        g.add(xlr);
    }

    // 데스크 스탠드 발 2개 (깊이 180mm까지)
    if (withFeet) {
        [-1, 1].forEach(sx => {
            const foot = new THREE.Mesh(new THREE.BoxGeometry(0.034, 0.014, 0.155),
                mat(0x1b1e23, { roughness: 0.8 }));
            foot.position.set(sx * 0.12, 0.007, -0.035);
            foot.castShadow = true;
            g.add(foot);
            const leg = new THREE.Mesh(new THREE.BoxGeometry(0.030, 0.05, 0.030),
                mat(0x1b1e23, { roughness: 0.8 }));
            leg.position.set(sx * 0.12, 0.033, 0.006);
            g.add(leg);
        });
    }
    return g;
}
function isSumo(eq) {
    return eq && (eq.id === 'MON-001' || /sumo/i.test(eq.product || ''));
}

// ───────── Triflector MkII (3분할 반사판) ─────────
// 가운데 패널 + 좌우 날개 3장. 패널 14"×23"(35.6×58.4cm) 기준.
function roundRectShape(w, h, r) {
    const sh = new THREE.Shape();
    const x = -w / 2, y = -h / 2;
    r = Math.min(r, w / 2, h / 2);
    sh.moveTo(x + r, y);
    sh.lineTo(x + w - r, y);      sh.quadraticCurveTo(x + w, y, x + w, y + r);
    sh.lineTo(x + w, y + h - r);  sh.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    sh.lineTo(x + r, y + h);      sh.quadraticCurveTo(x, y + h, x, y + h - r);
    sh.lineTo(x, y + r);          sh.quadraticCurveTo(x, y, x + r, y);
    return sh;
}
// 반사판 한 장 (검정 테두리 + 은반사면)
function reflectorPanel(w, h, r) {
    const g = new THREE.Group();
    const back = new THREE.Mesh(new THREE.ShapeGeometry(roundRectShape(w + 0.028, h + 0.028, r + 0.014), 16),
        mat(0x14161a, { roughness: 0.85, metalness: 0.1, side: THREE.DoubleSide }));
    back.position.z = -0.004; back.castShadow = true;
    g.add(back);
    const face = new THREE.Mesh(new THREE.ShapeGeometry(roundRectShape(w, h, r), 16),
        mat(0xf2f4f7, { roughness: 0.28, metalness: 0.72,
                        emissive: 0x2a2e34, emissiveIntensity: 0.35, side: THREE.DoubleSide }));
    g.add(face);
    return g;
}
function triflectorMesh(sp) {
    const g = new THREE.Group();
    // 가운데 패널 (정면), 좌우 날개는 앞으로 접힌다
    const cw = 0.46, chh = 0.50;          // 가운데
    const ww = 0.36, wh = 0.58;           // 날개 (14"×23")
    const center = reflectorPanel(cw, chh, 0.10);
    center.position.y = chh / 2;
    g.add(center);
    [-1, 1].forEach(sd => {
        const wing = reflectorPanel(ww, wh, 0.16);
        const pivot = new THREE.Group();
        pivot.position.set(sd * (cw / 2 + 0.03), chh / 2, 0);
        wing.position.x = sd * (ww / 2 + 0.02);
        wing.rotation.z = sd * -0.42;      // 바깥쪽이 위로 들리며 부챗살처럼 벌어진다
        pivot.add(wing);
        pivot.rotation.y = -sd * 0.66;     // 피사체를 감싸듯 앞(+Z)으로
        g.add(pivot);
        // 힌지 클램프
        const kn = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.036, 0.036), M.black());
        kn.position.set(sd * (cw / 2 + 0.02), chh / 2, 0.012);
        g.add(kn);
        const bolt = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.05, 10), M.knob());
        bolt.rotation.z = Math.PI / 2;
        bolt.position.set(sd * (cw / 2 + 0.045), chh / 2, 0.012);
        g.add(bolt);
    });
    // 프레임 가로바 + 중앙 지지대
    const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.009, 0.009, cw + 0.1, 8), M.aluDk());
    bar.rotation.z = Math.PI / 2; bar.position.y = chh / 2;
    g.add(bar);
    const post = new THREE.Mesh(new THREE.CylinderGeometry(0.011, 0.011, chh * 0.55, 10), M.aluDk());
    post.position.y = -chh * 0.1;
    g.add(post);
    const yoke = new THREE.Mesh(new THREE.BoxGeometry(0.048, 0.04, 0.04), M.black());
    yoke.position.y = -chh * 0.34;
    g.add(yoke);
    return g;
}
function isTriflector(eq) {
    return eq && (eq.id === 'MOD-010' || /triflector|반사판/i.test(eq.product || ''));
}

// ───────── 파라볼릭 딥 소프트박스 ─────────
// 뒤쪽 스피드링에서 시작해 앞으로 벌어지는 포물면 + 지지살 + 확산 천
function parabolicSoftbox(R, D, ribs) {
    const g = new THREE.Group();
    ribs = ribs || 16;
    const N = 14, prof = [];
    for (let i = 0; i <= N; i++) {
        const u = i / N;
        const r = 0.038 + (R - 0.038) * Math.sin(u * Math.PI / 2);   // 뒤는 좁고 앞으로 벌어짐
        const y = D * Math.pow(u, 1.55);
        prof.push(new THREE.Vector2(r, y));
    }
    // 외피 (검정, 각진 면이 보이도록 세그먼트 = 살 개수)
    const shell = new THREE.Mesh(
        new THREE.LatheGeometry(prof, ribs),
        mat(0x14161a, { roughness: 0.94, metalness: 0.02, side: THREE.DoubleSide }));
    shell.castShadow = true;
    g.add(shell);
    // 지지살 (은색 곡선 로드)
    const curve = new THREE.CatmullRomCurve3(prof.map(p => new THREE.Vector3(p.x, p.y, 0)));
    const ribGeo = new THREE.TubeGeometry(curve, 12, Math.max(0.004, R * 0.016), 5, false);
    for (let i = 0; i < ribs; i++) {
        const rib = new THREE.Mesh(ribGeo, M.sbRib());
        rib.rotation.y = (i / ribs) * Math.PI * 2;
        g.add(rib);
    }
    // 앞 테두리 링
    const rim = new THREE.Mesh(new THREE.TorusGeometry(R, R * 0.022, 6, ribs * 2), M.sbRib());
    rim.rotation.x = Math.PI / 2; rim.position.y = D;
    g.add(rim);
    // 확산 천 (발광면)
    const face = new THREE.Mesh(new THREE.CircleGeometry(R * 0.995, ribs * 2), M.diff());
    face.rotation.x = -Math.PI / 2; face.position.y = D - 0.004;
    g.add(face);
    // 스피드링 + 마운트
    const ring = new THREE.Mesh(new THREE.CylinderGeometry(0.052, 0.052, 0.03, 18), M.aluDk());
    ring.position.y = -0.012; g.add(ring);
    return g;
}


// 두 점을 잇는 봉 (다리·팔·그립암 공용)
function rodBetween(g, p0, p1, r, m, r2) {
    const d = new THREE.Vector3().subVectors(p1, p0);
    const len = d.length();
    if (len < 1e-5) return null;
    const me = new THREE.Mesh(new THREE.CylinderGeometry(r2 === undefined ? r : r2, r, len, 10), m);
    me.position.copy(p0).addScaledVector(d, 0.5);
    me.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.clone().normalize());
    me.castShadow = true;
    g.add(me);
    return me;
}
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

// ───────── COB 모노라이트 헤드 (NANLITE Forza 500 등) ─────────
// 형태: 원통 배럴 + 뒤쪽 원주 방열핀 + 앞 보웬스 마운트 링/리플렉터/발광면
//       + 뒤판 OLED·다이얼·커넥터 + 상단 손잡이. 빛은 +Z(앞) 방향.
// 로컬 원점 = 헤드 중심(호출부에서 y 높이 배치). 크기는 sp(w/d/h, m) 로 스케일.
function cobHeadMesh(sp) {
    const g = new THREE.Group();
    const rB = sp.w * 0.30;                                 // 배럴 반경
    const zBack = -sp.d * 0.36, zFront = sp.d * 0.42;
    const zc = (zBack + zFront) / 2, len = zFront - zBack;
    // 배럴 본체
    const body = addMesh(g, new THREE.CylinderGeometry(rB, rB, len, 28), M.black(), 0, 0, zc);
    body.rotation.x = Math.PI / 2;
    // 원주 방열핀(뒤쪽 절반) + 감싸는 링
    const finN = 22, finZ0 = zBack + 0.008, finZ1 = zc, finMz = (finZ0 + finZ1) / 2, finLz = finZ1 - finZ0;
    for (let i = 0; i < finN; i++) {
        const a = (i / finN) * Math.PI * 2;
        const fin = addMesh(g, new THREE.BoxGeometry(0.0035, rB * 0.34, finLz), M.aluDk(),
            Math.cos(a) * rB * 1.14, Math.sin(a) * rB * 1.14, finMz);
        fin.rotation.z = a;
    }
    for (let i = 0; i < 3; i++) {
        const rr = addMesh(g, new THREE.CylinderGeometry(rB * 1.2, rB * 1.2, 0.005, 28, 1, true), M.aluDk(),
            0, 0, finZ0 + finLz * (0.18 + 0.32 * i));
        rr.rotation.x = Math.PI / 2;
    }
    // 보웬스 마운트 링(앞) + 탭 4개
    const mount = addMesh(g, new THREE.CylinderGeometry(rB * 1.28, rB * 1.16, sp.d * 0.10, 28), M.aluDk(),
        0, 0, zFront - sp.d * 0.05);
    mount.rotation.x = Math.PI / 2;
    for (let k = 0; k < 4; k++) {
        const a = k * Math.PI / 2 + Math.PI / 4;
        const tab = addMesh(g, new THREE.BoxGeometry(0.02, 0.011, 0.012), M.alu(),
            Math.cos(a) * rB * 1.3, Math.sin(a) * rB * 1.3, zFront - sp.d * 0.02);
        tab.rotation.z = a;
    }
    // 리플렉터(안쪽 원뿔) + 발광면
    const ref = addMesh(g, new THREE.CylinderGeometry(rB * 1.08, rB * 0.5, sp.d * 0.15, 24, 1, true),
        mat(0xd8dde3, { metalness: 0.9, roughness: 0.2, side: THREE.DoubleSide }), 0, 0, zFront - sp.d * 0.02);
    ref.rotation.x = -Math.PI / 2;
    addMesh(g, new THREE.CircleGeometry(rB * 0.5, 24), M.diff(), 0, 0, zFront - sp.d * 0.10, false);
    // 뒤판 + OLED + 다이얼 + 커넥터
    const cap = addMesh(g, new THREE.CylinderGeometry(rB, rB, 0.012, 28), M.black(), 0, 0, zBack + 0.006);
    cap.rotation.x = Math.PI / 2;
    addMesh(g, new THREE.BoxGeometry(rB * 0.72, rB * 0.34, 0.006),
        mat(0x0b0d10, { emissive: 0x2a4a6a, emissiveIntensity: 0.5, roughness: 0.4 }),
        0, rB * 0.30, zBack - 0.002, false);
    const dial = addMesh(g, new THREE.CylinderGeometry(rB * 0.17, rB * 0.17, 0.02, 16), M.knob(),
        rB * 0.44, -rB * 0.28, zBack - 0.006);
    dial.rotation.x = Math.PI / 2;
    [-1, 1].forEach(s => {
        const cn = addMesh(g, new THREE.CylinderGeometry(rB * 0.1, rB * 0.1, 0.02, 10), M.aluDk(),
            s * rB * 0.48, -rB * 0.52, zBack - 0.006);
        cn.rotation.x = Math.PI / 2;
    });
    // 상단 손잡이
    const hb = addMesh(g, new THREE.TorusGeometry(rB * 0.55, 0.006, 8, 18, Math.PI), M.black(),
        0, rB + 0.004, zc);
    hb.rotation.y = Math.PI / 2;
    return g;
}
function isForza500(eq) {
    return eq && (['LIT-001', 'LIT-002'].includes(eq.id) || /forza\s*500/i.test(eq.product || ''));
}

// ───────── 랜턴(구형) 소프트박스 (NANLITE Lantern Softbox) ─────────
// 흰 구형 확산 글로브 + 뒤쪽 검은 스커트 + 스피드링 마운트. 빛은 사방/앞(+Z).
function lanternMesh(sp) {
    const g = new THREE.Group();
    const R = sp.w * 0.5;
    const globe = addMesh(g, new THREE.SphereGeometry(R, 24, 18),
        mat(0xfdf7ec, { emissive: 0xfff2da, emissiveIntensity: 0.55, roughness: 0.96 }), 0, 0, 0);
    globe.scale.set(1, 0.92, 1);
    // 위도 링(랜턴 패널 라인)
    for (let i = 1; i <= 2; i++) {
        const rr = addMesh(g, new THREE.TorusGeometry(R * Math.cos(i * 0.5), 0.004, 6, 28), M.aluDk(),
            0, R * 0.92 * Math.sin(i * 0.5) - R * 0.0, 0);
        rr.rotation.x = Math.PI / 2;
    }
    // 뒤쪽 검은 스커트(마운트로 좁아짐)
    const skirt = addMesh(g, new THREE.CylinderGeometry(R * 0.6, R * 0.18, R * 0.75, 22, 1, true),
        M.black(), 0, 0, -R * 0.6);
    skirt.rotation.x = Math.PI / 2;
    // 스피드링 마운트
    const ring = addMesh(g, new THREE.CylinderGeometry(R * 0.2, R * 0.2, R * 0.14, 20), M.aluDk(),
        0, 0, -R * 0.92);
    ring.rotation.x = Math.PI / 2;
    return g;
}
function isLanternSoftbox(eq) {
    return eq && (eq.id === 'MOD-003' || /jemball|lantern|랜턴/i.test(eq.product || ''));
}

// ───────── 프로젝션 어태치먼트/스누트 (NANLITE PJ-FZ60) ─────────
// 테이퍼 배럴 + 포커스 그립 + 앞 렌즈 후드/렌즈 + 뒤 보웬스 마운트 + 상단 고보 슬롯.
// 빛은 앞(+Z)으로 나가고, 뒤(-Z)가 조명에 물리는 마운트.
function projectionMesh(sp) {
    const g = new THREE.Group();
    const rB = sp.w * 0.26;
    const zBack = -sp.d * 0.5, zFront = sp.d * 0.5, len = zFront - zBack;
    const barrel = addMesh(g, new THREE.CylinderGeometry(rB * 1.15, rB, len * 0.68, 24), M.black(),
        0, 0, (zBack + zFront) / 2 - len * 0.04);
    barrel.rotation.x = Math.PI / 2;
    const grip = addMesh(g, new THREE.CylinderGeometry(rB * 1.22, rB * 1.22, len * 0.2, 24), M.knob(),
        0, 0, zBack + len * 0.5);
    grip.rotation.x = Math.PI / 2;
    // 앞 렌즈 후드 + 유리 렌즈
    const hood = addMesh(g, new THREE.CylinderGeometry(rB * 1.35, rB * 1.12, len * 0.22, 24), M.aluDk(),
        0, 0, zFront - len * 0.11);
    hood.rotation.x = Math.PI / 2;
    addMesh(g, new THREE.CircleGeometry(rB * 1.12, 24), M.glass(), 0, 0, zFront - 0.006, false);
    // 뒤 보웬스 마운트 + 탭
    const mount = addMesh(g, new THREE.CylinderGeometry(rB * 1.5, rB * 1.32, sp.d * 0.10, 26), M.aluDk(),
        0, 0, zBack + sp.d * 0.05);
    mount.rotation.x = Math.PI / 2;
    for (let k = 0; k < 4; k++) {
        const a = k * Math.PI / 2 + Math.PI / 4;
        const tab = addMesh(g, new THREE.BoxGeometry(0.02, 0.011, 0.012), M.alu(),
            Math.cos(a) * rB * 1.55, Math.sin(a) * rB * 1.55, zBack + sp.d * 0.03);
        tab.rotation.z = a;
    }
    // 상단 고보 슬롯 + 하단 지지 노브
    addMesh(g, new THREE.BoxGeometry(rB * 0.9, rB * 0.5, 0.03), M.black(), 0, rB * 1.25, zBack + len * 0.42);
    addMesh(g, new THREE.CylinderGeometry(0.012, 0.012, rB * 0.6, 10), M.knob(),
        0, -rB * 1.3, zBack + len * 0.4);
    return g;
}
function isProjection(eq) {
    return eq && (eq.id === 'MOD-004' || /projection|프로젝션|pj-?fz/i.test(eq.product || ''));
}

// ───────── C 스탠드 (참고 사진: 크롬 터틀베이스 + 2단 리저) ─────────
function cStandBase(g, spread) {
    const R = Math.max(0.42, spread * 0.5);
    // 터틀 베이스: 세 다리가 기둥의 서로 다른 높이에 물려 접힌다
    const hs = [0.315, 0.225, 0.135];
    for (let i = 0; i < 3; i++) {
        const a = (i / 3) * Math.PI * 2 + 0.45;
        const y0 = hs[i];
        const reach = R * (1 + i * 0.06);
        const c = Math.cos(a), sn = Math.sin(a);
        const kn = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.05, 12), M.chromeD());
        kn.position.set(0, y0, 0); g.add(kn);
        // 경사부 → 완만부 → 발
        const p0 = V3(c * 0.028, y0, sn * 0.028);
        const p1 = V3(c * reach * 0.55, y0 * 0.36, sn * reach * 0.55);
        const p2 = V3(c * reach, 0.035, sn * reach);
        rodBetween(g, p0, p1, 0.0125, M.chrome());
        rodBetween(g, p1, p2, 0.0115, M.chrome());
        const foot = new THREE.Mesh(new THREE.SphereGeometry(0.019, 10, 8), M.rubber());
        foot.position.set(c * reach, 0.022, sn * reach); g.add(foot);
    }
    // 베이스 칼라 + 조임 손잡이
    const col = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.032, 0.075, 14), M.chromeD());
    col.position.y = 0.225; g.add(col);
    tHandle(g, 0.036, 0.245, 0);
}
// T형 조임 손잡이
function tHandle(g, x, y, z, ang) {
    const a = ang || 0;
    const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.007, 0.007, 0.052, 8), M.chromeD());
    stem.rotation.z = Math.PI / 2; stem.rotation.y = a;
    stem.position.set(x, y, z); g.add(stem);
    const knob = new THREE.Mesh(new THREE.CylinderGeometry(0.011, 0.011, 0.034, 10), M.black());
    knob.rotation.z = Math.PI / 2; knob.rotation.y = a;
    knob.position.set(x + Math.cos(a) * 0.03, y, z - Math.sin(a) * 0.03); g.add(knob);
}
// 크롬 텔레스코픽 기둥
function chromeRiser(g, fromY, h, sections) {
    const secH = (h - fromY) / sections;
    for (let i = 0; i < sections; i++) {
        const r = 0.0185 - i * 0.0035;
        const tube = new THREE.Mesh(new THREE.CylinderGeometry(r, r, secH * 1.03, 14), M.chrome());
        tube.position.y = fromY + secH * (i + 0.5);
        tube.castShadow = true; g.add(tube);
        if (i > 0) {
            const cl = new THREE.Mesh(new THREE.CylinderGeometry(r * 1.7, r * 1.7, 0.052, 14), M.chromeD());
            cl.position.y = fromY + secH * i; g.add(cl);
            tHandle(g, r * 1.7 + 0.018, fromY + secH * i, 0);
        }
    }
    // 상단 베이비 핀 (5/8")
    const pin = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.052, 10), M.chromeD());
    pin.position.y = h + 0.026; g.add(pin);
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.0125, 0.0125, 0.012, 10), M.chromeD());
    cap.position.y = h + 0.001; g.add(cap);
}
// 그립헤드·암 세트 (기둥에 물리는 그립헤드 + 크롬 암 + 끝 그립헤드)
function gripArm(g, len, y, yaw, hung) {
    const arm = new THREE.Group();
    gripHead(arm, 0, 0, 0);                                  // 기둥 쪽
    rodBetween(arm, V3(0.03, 0, 0), V3(len, 0, 0), 0.0115, M.chrome());
    gripHead(arm, len, 0, 0);                                // 암 끝
    (hung || []).forEach(p => {
        const as = specOf(p.eqId);
        const w = as.w || 0.5, hh = as.h || 0.5;
        addMesh(arm, new THREE.BoxGeometry(w, hh, Math.max(0.02, as.d || 0.04)),
            M.diff(), len, -hh / 2 - 0.07, 0);
    });
    arm.position.y = y; arm.rotation.y = yaw;
    g.add(arm);
    return arm;
}
// 그립헤드 (사진의 T핸들 달린 클램프)
function gripHead(g, x, y, z) {
    const body = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.055, 0.042), M.chromeD());
    body.position.set(x, y, z); body.castShadow = true; g.add(body);
    const jaw = new THREE.Mesh(new THREE.CylinderGeometry(0.021, 0.021, 0.05, 12), M.chrome());
    jaw.rotation.x = Math.PI / 2; jaw.position.set(x, y, z); g.add(jaw);
    tHandle(g, x + 0.042, y + 0.012, z, 0);
    return body;
}
// 조립체에 그립암 세트가 붙어 있는가
function armKitOf(it) {
    const p = rigParts(it).find(x => x.slot === 'arm');
    return p ? p.eqId : null;
}

function legSet(g, spread, topY, opt) {
    opt = opt || {};
    const n = 3, ang = opt.stagger ? [0, 0.34, 0.68] : [0, 0, 0];
    for (let i = 0; i < n; i++) {
        const a = (i / n) * Math.PI * 2 + (opt.rot || 0);
        const r = spread * 0.46 * (1 + (ang[i] || 0) * 0.12);
        const fx = Math.cos(a) * r, fz = Math.sin(a) * r;
        const legTop = topY * (opt.stagger ? [1, 0.82, 0.64][i] : 1);
        const len = Math.hypot(r, legTop);
        const leg = new THREE.Group();
        const upper = new THREE.Mesh(
            new THREE.CylinderGeometry(0.017, 0.013, len * 0.56, 8), M.alu());
        upper.position.y = -len * 0.28; upper.castShadow = true;
        const lower = new THREE.Mesh(
            new THREE.CylinderGeometry(0.012, 0.0095, len * 0.5, 8), M.aluDk());
        lower.position.y = -len * 0.75; lower.castShadow = true;
        const foot = new THREE.Mesh(new THREE.CylinderGeometry(0.019, 0.023, 0.026, 10), M.rubber());
        foot.position.y = -len + 0.012;
        const lock = new THREE.Mesh(new THREE.CylinderGeometry(0.019, 0.019, 0.03, 10), M.knob());
        lock.position.y = -len * 0.53;
        leg.add(upper); leg.add(lower); leg.add(foot); leg.add(lock);
        // 다리 축(-Y)을 바깥·아래 방향으로 회전
        const dir = new THREE.Vector3(fx, -legTop, fz).normalize();
        leg.quaternion.setFromUnitVectors(new THREE.Vector3(0, -1, 0), dir);
        leg.position.set(0, legTop, 0);
        g.add(leg);
    }
}
// 텔레스코픽 리저 (단수만큼 굵기 감소)
function riser(g, h, sections, baseR) {
    const secH = h / sections;
    for (let i = 0; i < sections; i++) {
        const r = baseR * (1 - i * 0.22);
        const tube = new THREE.Mesh(
            new THREE.CylinderGeometry(r, r, secH * 1.04, 12),
            i === 0 ? M.aluDk() : M.alu());
        tube.position.y = secH * (i + 0.5);
        tube.castShadow = true; g.add(tube);
        if (i > 0) {
            const kn = new THREE.Mesh(new THREE.CylinderGeometry(r * 1.55, r * 1.55, 0.026, 12), M.knob());
            kn.position.y = secH * i; g.add(kn);
        }
    }
}
function spigot(g, y) {
    addMesh(g, new THREE.CylinderGeometry(0.0155, 0.0155, 0.055, 10), M.aluDk(), 0, y + 0.027, 0);
    addMesh(g, new THREE.CylinderGeometry(0.024, 0.028, 0.022, 12), M.knob(), 0, y - 0.006, 0);
}
// 그립 헤드(너클)
function knuckle(g, x, y, z) {
    const k = new THREE.Group();
    addMesh(k, new THREE.CylinderGeometry(0.032, 0.032, 0.042, 14), M.aluDk(), 0, 0, 0);
    const bolt = addMesh(k, new THREE.CylinderGeometry(0.011, 0.011, 0.072, 8), M.knob(), 0, 0, 0);
    bolt.rotation.z = Math.PI / 2;
    addMesh(k, new THREE.SphereGeometry(0.019, 10, 8), M.knob(), 0.042, 0, 0);
    k.position.set(x, y, z); g.add(k);
    return k;
}

// ───────── 장비 메시 ─────────
function buildItemMesh(eq, it) {
    const sp = specOf(eq.id);
    const grp = new THREE.Group();
    const h = it.h3 || 0;
    const yaw = -(it.rot || 0) * Math.PI / 180;

    if (eq.cat === 'TRP') {                       // ── 삼각대 ──
        legSet(grp, sp.w, h * 0.86);
        addMesh(grp, new THREE.CylinderGeometry(0.021, 0.021, h * 0.3, 10), M.alu(), 0, h * 0.86 + h * 0.13, 0);
        // 미드 스프레더
        for (let i = 0; i < 3; i++) {
            const a = (i / 3) * Math.PI * 2;
            const bar = addMesh(grp, new THREE.CylinderGeometry(0.008, 0.008, sp.w * 0.42, 6), M.aluDk(),
                Math.cos(a) * sp.w * 0.21, h * 0.34, Math.sin(a) * sp.w * 0.21);
            bar.rotation.z = Math.PI / 2; bar.rotation.y = -a;
        }
        // 볼 + 플루이드 헤드 + 팬바
        const head = new THREE.Group();
        addMesh(head, new THREE.CylinderGeometry(0.055, 0.042, 0.05, 14), M.black(), 0, 0.025, 0);
        addMesh(head, new THREE.BoxGeometry(0.085, 0.045, 0.115), M.black(), 0, 0.072, 0);
        addMesh(head, new THREE.BoxGeometry(0.075, 0.012, 0.16), tint(eq.cat, { roughness: 0.6 }), 0, 0.1, 0.01);
        const pan = addMesh(head, new THREE.CylinderGeometry(0.0075, 0.0075, 0.26, 8), M.aluDk(), 0.03, 0.045, -0.13);
        pan.rotation.x = 1.15; pan.rotation.z = -0.22;
        head.position.y = h; head.rotation.y = yaw;
        grp.add(head);
    } else if (eq.cat === 'STD') {                // ── 스탠드 ──
        const isC = eq.id.startsWith('STD-C');
        if (isC) {
            cStandBase(grp, sp.w);
            chromeRiser(grp, 0.26, h, 2);
            // 그립암은 별도 액세서리 — 결합했을 때만 그린다
            if (armKitOf(it))
                gripArm(grp, sp.arm || 1.0, h - 0.02, yaw,
                    rigParts(it).filter(p => p.slot === 'hang'));
        } else {
            legSet(grp, sp.w, h * 0.3);
            riser(grp, h, 3, 0.019);
            spigot(grp, h);
        }
    } else if (MOUNTED[eq.cat] !== undefined) {   // ── 스탠드 위에 올라가는 장비 ──
        const standH = h;
        // 조립체에 실제 지지대가 있으면 그 규격으로 다리를 만든다
        const supId = supportOf(it);
        if (supId) {
            const ssp = specOf(supId);
            const isGim = supId.startsWith('GIM');
            if (isGim) {                          // 짐벌 = 다리 없이 그립
                addMesh(grp, new THREE.CylinderGeometry(0.026, 0.026, standH * 0.42, 10), M.aluDk(),
                    0, standH * 0.79, 0);
                const grip = addMesh(grp, new THREE.CylinderGeometry(0.032, 0.036, 0.2, 12), M.black(),
                    0, standH * 0.5, 0);
                addMesh(grp, new THREE.BoxGeometry(0.05, 0.03, 0.05), M.knob(), 0, standH * 0.62, 0);
            } else {
                const isTrp = supId.startsWith('TRP');
                const isCStand = supId.startsWith('STD-C');
                if (isCStand) { cStandBase(grp, ssp.w); chromeRiser(grp, 0.26, standH, 2); }
                else { legSet(grp, ssp.w, standH * (isTrp ? 0.84 : 0.3));
                       riser(grp, standH, 3, isTrp ? 0.021 : 0.018); }
                if (isTrp) {   // 미드 스프레더
                    for (let i = 0; i < 3; i++) {
                        const a2 = (i / 3) * Math.PI * 2;
                        const bar = addMesh(grp, new THREE.CylinderGeometry(0.008, 0.008, ssp.w * 0.42, 6),
                            M.aluDk(), Math.cos(a2) * ssp.w * 0.21, standH * 0.34, Math.sin(a2) * ssp.w * 0.21);
                        bar.rotation.z = Math.PI / 2; bar.rotation.y = -a2;
                    }
                }
                // 그립암 세트를 결합했을 때만 (실제로 1m 옆으로 뻗어 공간을 차지한다)
                if (isCStand && armKitOf(it))
                    gripArm(grp, ssp.arm || 1.0, standH - 0.02, yaw,
                        rigParts(it).filter(p => p.slot === 'hang'));
                addMesh(grp, new THREE.CylinderGeometry(0.045, 0.036, 0.042, 14), M.black(), 0, standH + 0.021, 0);
            }
            // 스탠드에 매단 무게추 / 바닥에 놓은 전원
            rigParts(it).filter(p => p.slot === 'weight').forEach((p, i) => {
                const ws = specOf(p.eqId);
                addMesh(grp, new THREE.BoxGeometry(ws.w || 0.34, ws.h || 0.12, ws.d || 0.2),
                    mat(0x2a2d33, { roughness: .95 }), 0, (ws.h || 0.12) / 2, ssp.w * 0.22 + i * 0.12);
            });
            rigParts(it).filter(p => p.slot === 'power' || p.slot === 'batt').forEach((p, i) => {
                const bs = specOf(p.eqId);
                addMesh(grp, new THREE.BoxGeometry(bs.w || 0.09, bs.h || 0.14, bs.d || 0.06),
                    mat(0x23272e, { roughness: .7 }), 0.055, standH * 0.42 + i * 0.16, 0.045);
            });
        } else {
            legSet(grp, Math.max(0.75, sp.w * 0.9), standH * 0.3);
            riser(grp, standH, 3, 0.018);
        }
        const head = new THREE.Group();
        head.name = 'head_' + eq.cat;
        head.position.y = standH;
        if (eq.cat === 'CAM') {          // 카메라는 팬/틸트를 그대로 따라감
            head.rotation.order = 'YXZ';
            head.rotation.y = (it.pan || 0) * Math.PI / 180;
            head.rotation.x = -(it.tilt || 0) * Math.PI / 180;
        } else head.rotation.y = yaw;

        if (eq.cat === 'LIT') {
            // 요크(U 브래킷)
            const yw = sp.w * 0.78;
            [-1, 1].forEach(s => {
                const arm = addMesh(head, new THREE.BoxGeometry(0.016, sp.h * 0.95, 0.03), M.aluDk(),
                    s * yw, sp.h * 0.5 + 0.03, 0);
            });
            addMesh(head, new THREE.BoxGeometry(yw * 2, 0.018, 0.035), M.aluDk(), 0, 0.035, 0);
            // 헤드 — 제품별 전용 형태 우선, 없으면 일반 헤드
            if (isForza500(eq)) {
                const cob = cobHeadMesh(sp);
                cob.position.y = sp.h * 0.55 + 0.03;
                head.add(cob);
            } else {
                // 헤드 본체
                const body = addMesh(head, new THREE.CylinderGeometry(sp.w * 0.52, sp.w * 0.52, sp.d * 0.72, 16),
                    M.black(), 0, sp.h * 0.55 + 0.03, 0);
                body.rotation.x = Math.PI / 2;
                // 방열 핀
                for (let i = 0; i < 5; i++)
                    addMesh(head, new THREE.BoxGeometry(sp.w * 1.02, 0.006, 0.03), M.aluDk(),
                        0, sp.h * 0.55 + 0.03, -sp.d * 0.36 + i * 0.014);
                // 리플렉터 + 발광면
                const ref = addMesh(head, new THREE.CylinderGeometry(sp.w * 1.15, sp.w * 0.55, sp.d * 0.62, 20, 1, true),
                    mat(0xd8dde3, { metalness: 0.85, roughness: 0.22, side: THREE.DoubleSide }),
                    0, sp.h * 0.55 + 0.03, sp.d * 0.62);
                ref.rotation.x = -Math.PI / 2;
                const face = addMesh(head, new THREE.CircleGeometry(sp.w * 1.12, 22), M.diff(),
                    0, sp.h * 0.55 + 0.03, sp.d * 0.92, false);
                face.rotation.y = 0;
                // 카테고리 컬러 밴드
                const band = addMesh(head, new THREE.CylinderGeometry(sp.w * 0.545, sp.w * 0.545, 0.022, 16),
                    tint(eq.cat, { emissive: parseInt((CAT_COLORS[eq.cat]).slice(1), 16), emissiveIntensity: 0.25 }),
                    0, sp.h * 0.55 + 0.03, -sp.d * 0.3);
                band.rotation.x = Math.PI / 2;
            }
            // 조립체 모디파이어(소프트박스/디퓨저) → 조명 앞에 장착
            rigParts(it).filter(p => p.slot === 'mod').forEach(p => {
                const ms = specOf(p.eqId);
                const me = EQUIPMENT.find(e => e.id === p.eqId);
                const yy = sp.h * 0.55 + 0.03;
                if (isTriflector(me)) {          // 반사판은 조명 앞에 세워 둔다
                    const tf = triflectorMesh(ms);
                    tf.position.set(0, yy - 0.25, sp.d * 0.5 + 0.35);
                    head.add(tf);
                    return;
                }
                if (isLanternSoftbox(me)) {      // 랜턴(구형) 소프트박스
                    const m = lanternMesh(ms);
                    m.position.set(0, yy, sp.d * 0.5 + (ms.w || 0.8) * 0.5);
                    head.add(m);
                    return;
                }
                if (isProjection(me)) {          // 프로젝션 스누트
                    const m = projectionMesh(ms);
                    m.position.set(0, yy, sp.d * 0.5 + (ms.d || 0.5) * 0.5);
                    head.add(m);
                    return;
                }
                const isBox = (ms.d || 0.4) > 0.2;
                if (isBox) {
                    const sb = parabolicSoftbox(Math.max(0.25, (ms.w || 0.9) / 2),
                        Math.max(0.22, ms.d || 0.5), 16);
                    sb.rotation.x = Math.PI / 2;           // 확산면이 조명 앞(+Z)을 향하게
                    sb.position.set(0, yy, sp.d * 0.5);
                    head.add(sb);
                } else {   // 얇은 디퓨저 패널
                    addMesh(head, new THREE.BoxGeometry(ms.w, ms.h, Math.max(0.02, ms.d)),
                        M.diff(), 0, yy, sp.d * 0.5 + 0.42);
                    addMesh(head, new THREE.CylinderGeometry(0.008, 0.008, 0.42, 6), M.aluDk(),
                        0, yy, sp.d * 0.5 + 0.21).rotation.x = Math.PI / 2;
                }
            });
        } else if (eq.cat === 'MOD') {
            if (isTriflector(eq)) {
                const tf = triflectorMesh(sp);
                tf.position.y = 0.06;
                head.add(tf);
            } else if (isLanternSoftbox(eq)) {
                const m = lanternMesh(sp);
                m.position.y = sp.h * 0.5;
                head.add(m);
            } else if (isProjection(eq)) {
                const m = projectionMesh(sp);
                m.position.y = sp.h * 0.5;
                head.add(m);
            } else {
                const sb = parabolicSoftbox(Math.max(0.25, sp.w * 0.6), Math.max(0.22, sp.d), 16);
                sb.rotation.x = Math.PI / 2;
                sb.position.set(0, sp.h * 0.5, 0);
                head.add(sb);
            }
        } else if (eq.cat === 'CAM') {
            // 바디 + 렌즈 + 후드 + 상단 핸들
            addMesh(head, new THREE.BoxGeometry(sp.w, sp.h, sp.d), M.black(), 0, sp.h / 2 + 0.03, 0);
            addMesh(head, new THREE.BoxGeometry(sp.w * 0.92, 0.012, sp.d * 0.9),
                tint(eq.cat), 0, sp.h + 0.032, 0);
            const mount = addMesh(head, new THREE.CylinderGeometry(0.031, 0.031, 0.02, 16), M.aluDk(),
                0, sp.h / 2 + 0.03, sp.d / 2 + 0.01);
            mount.rotation.x = Math.PI / 2;
            const lens = addMesh(head, new THREE.CylinderGeometry(0.037, 0.041, 0.115, 20), M.black(),
                0, sp.h / 2 + 0.03, sp.d / 2 + 0.075);
            lens.rotation.x = Math.PI / 2;
            const ring = addMesh(head, new THREE.CylinderGeometry(0.0395, 0.0395, 0.018, 20), M.knob(),
                0, sp.h / 2 + 0.03, sp.d / 2 + 0.06);
            ring.rotation.x = Math.PI / 2;
            const hood = addMesh(head, new THREE.CylinderGeometry(0.048, 0.041, 0.05, 20, 1, true),
                mat(0x14171b, { roughness: 0.9, side: THREE.DoubleSide }),
                0, sp.h / 2 + 0.03, sp.d / 2 + 0.155);
            hood.rotation.x = Math.PI / 2;
            addMesh(head, new THREE.CircleGeometry(0.033, 18), M.glass(),
                0, sp.h / 2 + 0.03, sp.d / 2 + 0.133, false);
            if (eq.id === 'CAM-001' || eq.id === 'CAM-002') {   // 시네마 카메라 상단 핸들
                addMesh(head, new THREE.BoxGeometry(sp.w * 0.75, 0.014, 0.03), M.aluDk(), 0, sp.h + 0.078, -0.01);
                [-1, 1].forEach(s => addMesh(head, new THREE.BoxGeometry(0.014, 0.045, 0.028), M.aluDk(),
                    s * sp.w * 0.32, sp.h + 0.055, -0.01));
            }
            // 조립체 렌즈 → 실제 길이/구경 반영
            const lensId = partIn(it, 'lens');
            if (lensId) {
                const ls = specOf(lensId);
                const L = Math.max(0.08, ls.d || 0.13), R = Math.max(0.03, (ls.w || 0.09) / 2);
                const lz = sp.d / 2 + 0.02 + L / 2;
                const bar = addMesh(head, new THREE.CylinderGeometry(R, R * 1.05, L, 22), M.black(),
                    0, sp.h / 2 + 0.03, lz);
                bar.rotation.x = Math.PI / 2;
                const rg = addMesh(head, new THREE.CylinderGeometry(R * 1.06, R * 1.06, L * 0.16, 22), M.knob(),
                    0, sp.h / 2 + 0.03, lz - L * 0.22);
                rg.rotation.x = Math.PI / 2;
                addMesh(head, new THREE.CircleGeometry(R * 0.82, 20), M.glass(),
                    0, sp.h / 2 + 0.03, lz + L / 2 + 0.001, false);
            }
            // 렌즈 앞 필터
            if (lensId && rigParts(it).some(p => p.slot === 'filter')) {
                const ls2 = specOf(lensId);
                const R2 = Math.max(0.03, (ls2.w || 0.09) / 2) * 1.04;
                const L2 = Math.max(0.08, ls2.d || 0.13);
                const fr = addMesh(head, new THREE.CylinderGeometry(R2, R2, 0.012, 22), M.knob(),
                    0, sp.h / 2 + 0.03, sp.d / 2 + 0.02 + L2 + 0.006);
                fr.rotation.x = Math.PI / 2;
            }
            // 배터리 (뒷면)
            rigParts(it).filter(p => p.slot === 'batt').forEach((p, i) => {
                const bs = specOf(p.eqId);
                addMesh(head, new THREE.BoxGeometry(bs.w || 0.04, bs.h || 0.06, bs.d || 0.02),
                    mat(0x1b1e24, { roughness: .8 }),
                    (i === 0 ? -sp.w * 0.18 : sp.w * 0.18), sp.h / 2 + 0.03, -sp.d / 2 - (bs.d || 0.02) / 2);
            });
            // 슈에 붙은 모니터/마이크
            const shoeIds = rigParts(it).filter(p => p.slot === 'shoe').map(p => p.eqId);
            shoeIds.forEach((sid, i) => {
                const ss = specOf(sid);
                const m = addMesh(head, new THREE.BoxGeometry(ss.w, ss.h, ss.d),
                    mat(0x1e2228, { roughness: .6 }),
                    (i === 0 ? 0 : sp.w * 0.42), sp.h + 0.055 + ss.h / 2, -0.02);
                if (sid.startsWith('MON'))
                    addMesh(head, new THREE.BoxGeometry(ss.w * 0.88, ss.h * 0.8, 0.003),
                        mat(0x2a4d7a, { emissive: 0x1d3f6b, emissiveIntensity: .5 }),
                        (i === 0 ? 0 : sp.w * 0.42), sp.h + 0.055 + ss.h / 2, -0.02 + ss.d / 2 + 0.003, false);
            });
        } else {   // MON
            if (isSumo(eq)) {
                const mo = sumoMonitor(sp, false);
                mo.position.y = 0.03;
                head.add(mo);
                // 스탠드 요크
                addMesh(head, new THREE.BoxGeometry(0.05, 0.045, 0.05), M.black(), 0, 0.012, 0);
            } else {
                addMesh(head, new THREE.BoxGeometry(sp.w, sp.h, sp.d), M.black(), 0, sp.h / 2 + 0.03, 0);
                addMesh(head, new THREE.BoxGeometry(sp.w * 0.9, sp.h * 0.82, 0.004),
                    mat(0x2a4d7a, { emissive: 0x1d3f6b, emissiveIntensity: 0.55, roughness: 0.35 }),
                    0, sp.h / 2 + 0.03, sp.d / 2 + 0.004, false);
            }
        }
        grp.add(head);
    } else if (isSumo(eq)) {                      // ── 데스크 스탠드로 세워 둔 모니터 ──
        const mo = sumoMonitor(sp, true);
        mo.position.y = h + 0.05;
        mo.rotation.y = yaw;
        grp.add(mo);
    } else {                                      // ── 바닥 물건 ──
        const body = addMesh(grp, new THREE.BoxGeometry(sp.w, sp.h, sp.d),
            mat(0x2b3037, { roughness: 0.75, metalness: 0.2 }), 0, h + sp.h / 2, 0);
        body.rotation.y = yaw;
        const cap = addMesh(grp, new THREE.BoxGeometry(sp.w * 1.02, 0.012, sp.d * 1.02),
            tint(eq.cat), 0, h + sp.h + 0.006, 0);
        cap.rotation.y = yaw;
    }

    // 바닥 식별 디스크 (카테고리 색)
    const disc = new THREE.Mesh(
        new THREE.RingGeometry(Math.max(0.12, sp.w * 0.42), Math.max(0.16, sp.w * 0.5), 28),
        new THREE.MeshBasicMaterial({
            color: parseInt((CAT_COLORS[eq.cat] || '#999999').slice(1), 16),
            transparent: true, opacity: 0.55, side: THREE.DoubleSide
        }));
    disc.rotation.x = -Math.PI / 2; disc.position.y = 0.008;
    grp.add(disc);

    grp.userData = { fid: null, eqId: eq.id, topY: itemTopY(eq, it) };
    return grp;
}
function itemTopY(eq, it) {
    const sp = specOf(eq.id);
    const h = it.h3 || 0;
    if (eq.cat === 'STD' || eq.cat === 'TRP') return h + 0.09;
    if (MOUNTED[eq.cat] !== undefined) return h + sp.h + 0.04;
    return h + sp.h;
}

// ───────── 씬 구성 ─────────
function build3D() {
    const f = ensure3D(currentScene());
    updateEmptyHints();
    if (!R3) return;
    const W = R3.world;
    while (W.children.length) W.remove(W.children[0]);
    R3.picks = []; R3.lights = [];

    // 바닥 + 방
    const rooms = f.rooms.length ? f.rooms : [{ id: '_d', name: '기본', x: 0, y: 0, w: 8, h: 6 }];
    let cx = 0, cz = 0, n = 0;
    rooms.forEach(r => {
        const pts = r.type === 'poly'
            ? r.pts.map(p => new THREE.Vector2(r.x + p.x, r.y + p.y))
            : [new THREE.Vector2(r.x, r.y), new THREE.Vector2(r.x + r.w, r.y),
               new THREE.Vector2(r.x + r.w, r.y + r.h), new THREE.Vector2(r.x, r.y + r.h)];
        const shape = new THREE.Shape(pts);
        const floorM = new THREE.Mesh(new THREE.ShapeGeometry(shape),
            new THREE.MeshStandardMaterial({ color: 0x333a43, roughness: 0.88, metalness: 0.05,
                side: THREE.DoubleSide }));
        floorM.rotation.x = Math.PI / 2;
        floorM.position.y = 0;
        floorM.receiveShadow = true;
        W.add(floorM);
        // 1m 바닥 격자
        const gpts = [];
        const bx = Math.min(...pts.map(p => p.x)), bz = Math.min(...pts.map(p => p.y));
        const ex = Math.max(...pts.map(p => p.x)), ez = Math.max(...pts.map(p => p.y));
        for (let gx = Math.ceil(bx); gx <= ex; gx++)
            gpts.push(new THREE.Vector3(gx, 0.004, bz), new THREE.Vector3(gx, 0.004, ez));
        for (let gz = Math.ceil(bz); gz <= ez; gz++)
            gpts.push(new THREE.Vector3(bx, 0.004, gz), new THREE.Vector3(ex, 0.004, gz));
        W.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(gpts),
            new THREE.LineBasicMaterial({ color: 0x5d6a7a, transparent: true, opacity: 0.32 })));
        // 벽 + 걸레받이 + 천장 몰딩
        for (let i = 0; i < pts.length; i++) {
            const a = pts[i], b = pts[(i + 1) % pts.length];
            const len = a.distanceTo(b);
            if (len < 0.05) continue;
            const mx = (a.x + b.x) / 2, mz = (a.y + b.y) / 2;
            const rotY = -Math.atan2(b.y - a.y, b.x - a.x);
            const wall = new THREE.Mesh(new THREE.PlaneGeometry(len, f.ceilH),
                new THREE.MeshStandardMaterial({
                    color: 0x8c99a8, transparent: true, opacity: 0.13,
                    side: THREE.DoubleSide, roughness: 0.95
                }));
            wall.position.set(mx, f.ceilH / 2, mz);
            wall.rotation.y = rotY;
            W.add(wall);
            // 걸레받이
            const base = new THREE.Mesh(new THREE.BoxGeometry(len, 0.09, 0.022),
                mat(0x424b57, { roughness: 0.85 }));
            base.position.set(mx, 0.045, mz); base.rotation.y = rotY;
            base.receiveShadow = true; W.add(base);
            // 천장 라인
            W.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([
                new THREE.Vector3(a.x, f.ceilH, a.y), new THREE.Vector3(b.x, f.ceilH, b.y)]),
                new THREE.LineBasicMaterial({ color: 0x8fc4ff, transparent: true, opacity: 0.75 })));
            // 모서리 기둥
            W.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([
                new THREE.Vector3(a.x, 0, a.y), new THREE.Vector3(a.x, f.ceilH, a.y)]),
                new THREE.LineBasicMaterial({ color: 0x8fc4ff, transparent: true, opacity: 0.4 })));
        }
        pts.forEach(p => { cx += p.x; cz += p.y; n++; });
    });
    // 시점 중심(오빗 타깃)은 이 씬을 '처음' 그릴 때만 방 중심으로 맞춘다.
    // 매 렌더마다 리셋하면 카메라를 옮길 때 사용자가 돌려둔 시점이 튄다.
    // 언제든 Home(fitView3D) 으로 다시 맞출 수 있다.
    if (n && R3._framed !== state.currentScene) {
        R3.orbit.tx = cx / n; R3.orbit.tz = cz / n; R3.orbit.ty = f.ceilH * 0.45;
        R3._framed = state.currentScene;
    }

    // 장비
    const over = [];
    for (const [fid, it] of Object.entries(f.items)) {
        const eq = EQUIPMENT.find(e => e.id === it.eqId);
        if (!eq) continue;
        const m = buildItemMesh(eq, it);
        m.position.set(it.x, 0, it.y);
        m.userData.fid = fid;
        m.traverse(o => { if (o.isMesh) o.userData.fid = fid; });
        W.add(m);
        R3.picks.push(m);
        if (m.userData.topY > f.ceilH + 0.001)
            over.push(`${eq.id} ${(m.userData.topY).toFixed(2)}m`);
    }

    // 피사체 (장비처럼 선택·이동 가능)
    (f.subjects || []).forEach(sj => {
        const m = subjectMesh(sj);
        m.position.set(sj.x, 0, sj.y);
        const key = 's:' + sj.id;
        m.userData.fid = key;
        m.traverse(x => { if (x.isMesh) x.userData.fid = key; });
        W.add(m);
        R3.picks.push(m);
    });

    // 선택 하이라이트 + 이동 기즈모
    R3.giz = null; R3.helpers = [];
    const selNow = selObj();
    if (selNow) {
        const it = selNow.o;
        const isSubj = selNow.kind === 'subj';
        const ring = new THREE.Mesh(new THREE.RingGeometry(0.42, 0.5, 24),
            new THREE.MeshBasicMaterial({ color: 0x7abaff, side: THREE.DoubleSide }));
        ring.rotation.x = -Math.PI / 2;
        ring.position.set(it.x, 0.012, it.y);
        W.add(ring); R3.helpers.push(ring);
        // 높이 기준선 (바닥 ↔ 현재 높이)
        if (!isSubj && (it.h3 || 0) > 0.02) {
            const gm = new THREE.BufferGeometry().setFromPoints(
                [new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, it.h3, 0)]);
            const gl = new THREE.Line(gm, new THREE.LineDashedMaterial(
                { color: 0x5ad696, dashSize: 0.09, gapSize: 0.07, transparent: true, opacity: 0.7 }));
            gl.computeLineDistances();
            gl.position.set(it.x, 0, it.y);
            W.add(gl); R3.helpers.push(gl);
        }
        if (!isViewOnly()) {
            R3.giz = buildGizmo(isSubj);   // 피사체는 바닥에 서 있으므로 Y축 없음
            R3.giz.position.set(it.x, isSubj ? 0.06 : (it.h3 || 0) + 0.06, it.y);
            W.add(R3.giz);
        }
    }

    buildFrustum(f);
    updateWarn(over, f);
    populateLensSelect();
    updateEmptyHints();
    updateCamPanel();
}

// ───────── 카메라 화각 프러스텀 ─────────
function buildFrustum(f) {
    if (!frustumOn) return;
    const [fid, it] = activeCam();
    if (!it) return;
    const fl = it.focal || focalMM;
    const SW = 0.036, SH = SW / previewAR;           // 풀프레임 센서 + 선택 화면비
    const hF = 2 * Math.atan(SW / (2 * fl / 1000));
    const vF = 2 * Math.atan(SH / (2 * fl / 1000));
    // 방 크기에 맞춰 길이 제한 (밖으로 과하게 뻗지 않게)
    let L = 6;
    if (f.rooms.length) {
        const r0 = f.rooms[0];
        const dim = r0.type === 'poly'
            ? Math.max(...r0.pts.map(p => Math.hypot(p.x, p.y)))
            : Math.hypot(r0.w, r0.h);
        L = Math.max(2, Math.min(9, dim * 0.95));
    }
    const hw = Math.tan(hF / 2) * L, hh = Math.tan(vF / 2) * L;
    const y = camEyeY(it);
    const g = new THREE.Group();
    const corners = [[hw, hh], [-hw, hh], [-hw, -hh], [hw, -hh]].map(c =>
        new THREE.Vector3(c[0], c[1], L));
    const pts = [];
    corners.forEach(c => { pts.push(new THREE.Vector3(0, 0, 0), c.clone()); });
    for (let i = 0; i < 4; i++) pts.push(corners[i].clone(), corners[(i + 1) % 4].clone());
    const lines = new THREE.LineSegments(
        new THREE.BufferGeometry().setFromPoints(pts),
        new THREE.LineBasicMaterial({ color: 0xffd54f, transparent: true, opacity: 0.9 }));
    g.add(lines);
    const planeM = new THREE.Mesh(new THREE.PlaneGeometry(hw * 2, hh * 2),
        new THREE.MeshBasicMaterial({
            color: 0xffd54f, transparent: true, opacity: 0.06, side: THREE.DoubleSide }));
    planeM.position.z = L;
    g.add(planeM);

    // ── 피사계 심도 시각화 ──
    if (dofOn) {
        const focusM = focusDistOf(f, it);
        const dof = dofOf(fl, it.fstop || 2.8, focusM);
        const rectAt = (dist, color, op, dash) => {
            const w2 = Math.tan(hF / 2) * dist, h2 = Math.tan(vF / 2) * dist;
            const pts = [
                new THREE.Vector3(-w2, -h2, dist), new THREE.Vector3(w2, -h2, dist),
                new THREE.Vector3(w2, h2, dist), new THREE.Vector3(-w2, h2, dist),
                new THREE.Vector3(-w2, -h2, dist)];
            const m = dash
                ? new THREE.LineDashedMaterial({ color, dashSize: 0.12, gapSize: 0.09,
                    transparent: true, opacity: op })
                : new THREE.LineBasicMaterial({ color, transparent: true, opacity: op });
            const ln = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), m);
            if (dash) ln.computeLineDistances();
            return ln;
        };
        const nearD = Math.max(0.15, dof.near);
        const farD = dof.far === Infinity ? L : Math.min(dof.far, L * 1.6);
        // 심도 구간 반투명 볼륨
        const wN = Math.tan(hF / 2) * nearD, hN = Math.tan(vF / 2) * nearD;
        const wF = Math.tan(hF / 2) * farD, hF2 = Math.tan(vF / 2) * farD;
        const geo = new THREE.BufferGeometry();
        const V = [
            -wN, -hN, nearD, wN, -hN, nearD, wF, -hF2, farD, -wF, -hF2, farD,   // 아래
            -wN, hN, nearD, wN, hN, nearD, wF, hF2, farD, -wF, hF2, farD        // 위
        ];
        geo.setAttribute('position', new THREE.Float32BufferAttribute(V, 3));
        geo.setIndex([0,1,2, 0,2,3, 4,5,6, 4,6,7, 0,4,7, 0,7,3, 1,5,6, 1,6,2]);
        geo.computeVertexNormals();
        const vol = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({
            color: 0x5fd39a, transparent: true, opacity: 0.055,
            side: THREE.DoubleSide, depthWrite: false }));
        g.add(vol);
        g.add(rectAt(nearD, 0x5fd39a, 0.65, true));
        if (dof.far !== Infinity && dof.far < L * 1.6) g.add(rectAt(farD, 0x5fd39a, 0.65, true));
        // 초점면 (선명한 초록)
        g.add(rectAt(focusM, 0x37e39a, 1.0, false));
        const fw = Math.tan(hF / 2) * focusM;
        g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(-fw * 1.12, 0, focusM), new THREE.Vector3(fw * 1.12, 0, focusM)]),
            new THREE.LineBasicMaterial({ color: 0x37e39a, transparent: true, opacity: 0.8 })));
    }
    g.position.set(it.x, y, it.y);
    // 팬/틸트 반영 (없으면 방 중앙을 향하도록 초기화)
    if (it.pan === undefined) {
        it.pan = +(Math.atan2(R3.orbit.tx - it.x, R3.orbit.tz - it.y) * 180 / Math.PI).toFixed(1);
        it.tilt = it.tilt || 0;
    }
    g.rotation.order = 'YXZ';
    g.rotation.y = (it.pan || 0) * Math.PI / 180;
    g.rotation.x = -(it.tilt || 0) * Math.PI / 180;   // +tilt = 위쪽
    R3.world.add(g);
    R3.frustum = g;
}

function updateWarn(over, f) {
    const el = document.getElementById('three-warn');
    el.textContent = over.length
        ? `⚠ 천장(${f.ceilH}m) 초과: ${over.join(', ')}`
        : '';
}

// ───────── 선택 ─────────
function pick3D(e) {
    if (!R3) return;
    const c = R3.renderer.domElement;
    const r = c.getBoundingClientRect();
    const mouse = new THREE.Vector2(
        ((e.clientX - r.left) / r.width) * 2 - 1,
        -((e.clientY - r.top) / r.height) * 2 + 1);
    R3.ray.setFromCamera(mouse, R3.cam);
    const hits = R3.ray.intersectObjects(R3.picks, true);
    const fid = hits.length ? hits[0].object.userData.fid : null;
    if (fid && fid !== three3Sel) { three3Sel = fid; build3D(); showSel(); }
    else if (!fid && three3Sel) { three3Sel = null; build3D(); showSel(); }
    return fid;
}
// 커서 아래에 장비가 있는지 (커서 모양용)
function hoverItem(e) {
    if (!R3 || !R3.picks.length) return null;
    gizRay(e);
    const h = R3.ray.intersectObjects(R3.picks, true);
    return h.length ? h[0].object.userData.fid : null;
}
function showSel() {
    const el = document.getElementById('three-sel');
    const hin = document.getElementById('h-in');
    const ip = document.getElementById('item-panel');
    const f = ensure3D(currentScene());
    const so = selObj();
    const pr = document.getElementById('ip-pose');
    if (so && so.kind === 'subj') {           // ── 피사체 ──
        const sj = so.o;
        el.innerHTML = `👤 피사체 · 키 ${sj.h.toFixed(2)}m · `
            + `${sj.pose === 'sit' ? '앉은 자세' : '선 자세'} · 눈높이 ${subjectEyeY(sj).toFixed(2)}m`;
        hin.disabled = true;
        if (ip) {
            ip.style.display = 'block';
            document.getElementById('ip-name').textContent = '피사체';
            const ys = document.getElementById('ip-y-s');
            if (ys) { ys.min = 1.0; ys.max = 2.1; ys.step = 0.01; }
            const yl = document.querySelector('.ip-ax[data-ax=y] label');
            if (yl) yl.innerHTML = '<i></i>키';
            const hh = document.getElementById('ip-hrange');
            if (hh) hh.textContent = '키 1.00~2.10m · 눈높이는 카메라 높이 맞출 때 기준이 됩니다';
            syncItemPanel({ x: sj.x, y: sj.y, h3: sj.h, rot: sj.rot || 0 });
            if (pr) { pr.style.display = 'flex'; syncPoseBtns(sj); }
            document.getElementById('ip-info').innerHTML =
                `눈높이 <b>${subjectEyeY(sj).toFixed(2)}m</b><br>`
                + `${sj.pose === 'sit' ? '의자 높이 ' + (sj.h * 0.257).toFixed(2) + 'm 기준' : '바닥에 선 자세'}`;
        }
        return;
    }
    if (pr) pr.style.display = 'none';
    const yl2 = document.querySelector('.ip-ax[data-ax=y] label');
    if (yl2) yl2.innerHTML = '<i></i>Y';
    if (!three3Sel || !f.items[three3Sel]) {
        el.innerHTML = '<b>장비를 끌면</b> 바닥 위 자유 이동 · <b>화살표</b>는 축 고정 이동 · '
        + '<b>빈 곳 드래그</b>=회전 · <b>방향키</b>=시점 · <b>Shift+방향키</b>=평행이동 · <b>+/−</b>=줌 · <b>Home</b>=전체보기';
        hin.disabled = true; hin.value = 0;
        if (ip) ip.style.display = 'none';
        return;
    }
    const it = f.items[three3Sel];
    const eq = EQUIPMENT.find(e => e.id === it.eqId);
    const sp = specOf(eq.id);
    const dim = `${(sp.w * 100).toFixed(0)}×${(sp.d * 100).toFixed(0)}×${(sp.h * 100).toFixed(0)}cm`;
    const rg = rigRange(it);
    const rng = rg ? ` · 조절 ${rg.min}~${rg.max}m (${rg.src})` : '';
    const src = sp.src === 'spec' ? '공식' : sp.src === 'avg' ? '평균' : '추정';
    const parts = rigParts(it);
    el.textContent = `${eq.id} ${dispName(eq)} · ${dim}(${src}) · 높이 ${(it.h3 || 0).toFixed(2)}m${rng}`
        + (parts.length ? ` · 부품 ${parts.length}개` : '');
    hin.disabled = false; hin.value = (it.h3 || 0).toFixed(2);
    if (state.ipFold) ip && ip.classList.add('fold');
    // 위치 패널
    if (ip) {
        ip.style.display = 'block';
        document.getElementById('ip-name').textContent = `${eq.id} ${dispName(eq)}`;
        const [lo, hi] = hRange(it);
        const ys = document.getElementById('ip-y-s');
        if (ys) { ys.min = lo; ys.max = Math.max(lo + 0.01, hi); }
        const hh = document.getElementById('ip-hrange');
        if (hh) hh.textContent = rg
            ? `Y 높이 ${lo}~${hi}m (${rg.src === 'spec' ? '지지대 공식 스펙' : '평균값'})`
            : `Y 높이 0~${hi.toFixed(2)}m (천장 ${f.ceilH}m 기준)`;
        syncItemPanel(it);
        let info = `발자국 ${(itemSize(it).w * 100).toFixed(0)}cm`;
        if (rg) info += ` · 높이 ${rg.min}~${rg.max}m`;
        if (parts.length) {
            info += '<br>' + parts.map(p => {
                const sd = p.slot === 'support' ? '지지' : p.slot === 'lens' ? '렌즈'
                    : p.slot === 'mod' ? '모디' : p.slot === 'shoe' ? '슈' : p.slot || '';
                return `<span style="color:#8fc0ff">${sd}</span> ${p.eqId}`;
            }).join('<br>');
        }
        document.getElementById('ip-info').innerHTML = info;
    }
}
function syncItemPanel(it) {
    const set = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
    set('ip-x', (it.x || 0).toFixed(2)); set('ip-x-s', it.x || 0);
    set('ip-z', (it.y || 0).toFixed(2)); set('ip-z-s', it.y || 0);
    set('ip-y', (it.h3 || 0).toFixed(2)); set('ip-y-s', it.h3 || 0);
    set('ip-r', (it.rot || 0).toFixed(0)); set('ip-r-s', it.rot || 0);
}
function toggleItemPanel() {
    const ip = document.getElementById('item-panel');
    if (!ip) return;
    ip.classList.toggle('fold');
    state.ipFold = ip.classList.contains('fold');
    saveState();
}
// X / Z / 높이 / 회전 직접 입력
// 피사체 속성 변경
function setSubject(key, v, live) {
    const so = selObj();
    if (!so || so.kind !== 'subj') return;
    const sj = so.o;
    if (key === 'pose') { sj.pose = v; }
    else {
        const val = parseFloat(v);
        if (isNaN(val)) return;
        if (key === 'x') { sj.x = +val.toFixed(2); confineSubject(sj); }
        else if (key === 'y') { sj.y = +val.toFixed(2); confineSubject(sj); }
        else if (key === 'h') sj.h = +Math.max(1.0, Math.min(2.1, val)).toFixed(2);
        else if (key === 'rot') sj.rot = +val.toFixed(0);
    }
    syncItemPanel({ x: sj.x, y: sj.y, h3: sj.h, rot: sj.rot || 0 });
    if (live && key !== 'pose' && key !== 'h') {
        const m = R3 && R3.picks.find(x => x.userData.fid === three3Sel);
        if (m) { m.position.set(sj.x, 0, sj.y);
                 if (key === 'rot') m.rotation.y = 0; }
        if (R3 && R3.giz) R3.giz.position.set(sj.x, 0.06, sj.y);
        if (key === 'rot') { saveState(); build3D(); }
        return;
    }
    saveState(); build3D(); showSel();
    if (key === 'pose') setStatus(v === 'sit' ? '피사체를 앉은 자세로 바꿨습니다' : '피사체를 선 자세로 바꿨습니다');
}
function syncPoseBtns(sj) {
    document.querySelectorAll('#ip-pose button').forEach(b =>
        b.classList.toggle('on', b.dataset.pose === (sj.pose || 'stand')));
}
function setItemPos(key, v, live) {
    if (isSubjKey(three3Sel)) {
        return setSubject(key === 'h3' ? 'h' : key, v, live);
    }
    const f = ensure3D(currentScene());
    if (!three3Sel || !f.items[three3Sel]) return;
    const it = f.items[three3Sel];
    let val = parseFloat(v);
    if (isNaN(val)) return;
    if (key === 'x') { it.x = +val.toFixed(2); confineItem(it); }
    else if (key === 'y') { it.y = +val.toFixed(2); confineItem(it); }
    else if (key === 'rot') it.rot = +val.toFixed(0);
    else if (key === 'h3') {
        const [lo, hi] = hRange(it);
        it.h3 = +Math.max(lo, Math.min(hi, val)).toFixed(2);
    }
    syncItemPanel(it);
    if (live) {                       // 슬라이더 드래그 중: 메시만 옮겨 부드럽게
        const m = R3 && R3.picks.find(x => x.userData.fid === three3Sel);
        if (m) {
            m.position.set(it.x, it.h3 || 0, it.y);
            if (key === 'rot') m.rotation.y = -(it.rot || 0) * Math.PI / 180;
        }
        if (R3 && R3.giz) R3.giz.position.set(it.x, (it.h3 || 0) + 0.06, it.y);
        return;
    }
    saveState(); build3D(); showSel(); updateCamPanel();
}

// ───────── 피사체 ─────────
function addSubject() {
    if (isViewOnly()) return;               // 공유(보기 전용): 피사체 추가 금지
    const f = ensure3D(currentScene());
    if (!f.subjects) f.subjects = [];
    let cx = 4, cz = 3;
    const rm = activeRoom(f);
    if (rm) { const c = roomCentroid(rm); cx = c.x; cz = c.y; }
    f.subjects.push({ id: 's' + Date.now(), x: +cx.toFixed(2), y: +cz.toFixed(2),
                      h: 1.70, pose: 'stand', rot: 0 });
    saveState();
    if (currentScene().mode === 'three') build3D(); else renderFloor();
    setStatus('피사체(키 1.70m)를 추가했습니다. 3D에서 클릭해 옮기고 앉은 자세로 바꿀 수 있어요.');
}
function subjectMesh(s) {
    const g = new THREE.Group();
    const H = s.h || 1.7;
    const sit = s.pose === 'sit';
    const yaw = -(s.rot || 0) * Math.PI / 180;
    const body = new THREE.Group();
    const B = M.manne(), J = M.manneJ();
    const ball = (p, r) => {
        const b = new THREE.Mesh(new THREE.SphereGeometry(r, 14, 10), J);
        b.position.copy(p); b.castShadow = true; body.add(b); return b;
    };

    // ── 관절 좌표 (서기 기준, 앉으면 하체만 접힌다) ──
    const hipY = sit ? H * 0.285 : H * 0.500;      // 앉으면 골반이 의자 높이로
    const drop = H * 0.500 - hipY;                 // 상체 전체가 그만큼 내려온다
    const P = {
        head:  V3(0, H * 0.930 - drop, 0),
        neck:  V3(0, H * 0.858 - drop, 0),
        chestT:V3(0, H * 0.820 - drop, 0),
        chestB:V3(0, H * 0.625 - drop, 0),
        waist: V3(0, H * 0.598 - drop, 0),
        pelvis:V3(0, H * 0.530 - drop, 0),
        shoulder: sd => V3(sd * H * 0.108, H * 0.808 - drop, 0),
        elbow:    sd => V3(sd * H * 0.128, H * 0.640 - drop, sit ? H * 0.02 : 0),
        wrist:    sd => V3(sd * H * 0.138, H * 0.478 - drop, sit ? H * 0.10 : 0),
        hip:      sd => V3(sd * H * 0.058, hipY, 0),
        knee:     sd => V3(sd * H * 0.062, sit ? hipY - H * 0.012 : H * 0.283, sit ? H * 0.245 : 0),
        ankle:    sd => V3(sd * H * 0.062, H * 0.048, sit ? H * 0.235 : 0)
    };

    // ── 몸통 (가슴·골반 블록) ──
    const chestH = P.chestT.y - P.chestB.y;
    const chest = new THREE.Mesh(new THREE.CylinderGeometry(H * 0.118, H * 0.082, chestH, 8), B);
    chest.position.set(0, (P.chestT.y + P.chestB.y) / 2, 0);
    chest.scale.z = 0.62; chest.rotation.y = Math.PI / 8; chest.castShadow = true;
    body.add(chest);
    const shoulderCap = new THREE.Mesh(new THREE.SphereGeometry(H * 0.118, 16, 10), B);
    shoulderCap.position.set(0, P.chestT.y - H * 0.005, 0);
    shoulderCap.scale.set(1, 0.42, 0.62); body.add(shoulderCap);
    ball(P.waist, H * 0.048);
    const pelvis = new THREE.Mesh(new THREE.CylinderGeometry(H * 0.088, H * 0.098, H * 0.10, 8), B);
    pelvis.position.set(0, P.pelvis.y, 0);
    pelvis.scale.z = 0.68; pelvis.rotation.y = Math.PI / 8; pelvis.castShadow = true;
    body.add(pelvis);

    // ── 목 + 머리 (달걀형, 얼굴 없음) ──
    rodBetween(body, P.chestT, P.neck, H * 0.026, J);
    const head = new THREE.Mesh(new THREE.SphereGeometry(H * 0.052, 20, 16), B);
    head.position.copy(P.head); head.scale.set(0.94, 1.30, 1.0);
    head.castShadow = true; body.add(head);

    // ── 팔 (상완 · 전완 · 벙어리손) ──
    [-1, 1].forEach(sd => {
        const sh = P.shoulder(sd), el = P.elbow(sd), wr = P.wrist(sd);
        ball(sh, H * 0.036);
        rodBetween(body, sh, el, H * 0.028, B, H * 0.033);
        ball(el, H * 0.028);
        rodBetween(body, el, wr, H * 0.022, B, H * 0.026);
        ball(wr, H * 0.021);
        const hand = new THREE.Mesh(new THREE.SphereGeometry(H * 0.026, 12, 10), B);
        const dir = new THREE.Vector3().subVectors(wr, el).normalize();
        hand.position.copy(wr).addScaledVector(dir, H * 0.045);
        hand.scale.set(0.72, 1.55, 0.42);
        hand.quaternion.setFromUnitVectors(V3(0, 1, 0), dir);
        hand.castShadow = true; body.add(hand);
    });

    // ── 다리 (허벅지 · 종아리 · 발) ──
    [-1, 1].forEach(sd => {
        const hp = P.hip(sd), kn = P.knee(sd), an = P.ankle(sd);
        ball(hp, H * 0.040);
        rodBetween(body, hp, kn, H * 0.032, B, H * 0.042);
        ball(kn, H * 0.032);
        rodBetween(body, kn, an, H * 0.024, B, H * 0.032);
        ball(an, H * 0.021);
        const foot = new THREE.Mesh(new THREE.SphereGeometry(H * 0.030, 12, 10), B);
        foot.position.set(an.x, H * 0.026, an.z + H * 0.038);
        foot.scale.set(0.85, 0.55, 1.75);
        foot.castShadow = true; body.add(foot);
    });

    body.rotation.y = yaw;
    g.add(body);

    // ── 앉은 자세면 간단한 의자 ──
    if (sit) {
        const ch = new THREE.Group();
        const seatY = hipY - H * 0.028;
        const sw = H * 0.24;
        const seat = new THREE.Mesh(new THREE.BoxGeometry(sw, H * 0.018, sw * 0.92),
            mat(0x4a5058, { roughness: 0.8 }));
        seat.position.set(0, seatY, H * 0.055); seat.castShadow = true; ch.add(seat);
        [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([a, b]) => {
            rodBetween(ch, V3(a * sw * 0.42, seatY - H * 0.01, H * 0.055 + b * sw * 0.4),
                V3(a * sw * 0.42, 0, H * 0.055 + b * sw * 0.4), H * 0.011, M.aluDk());
        });
        const back = new THREE.Mesh(new THREE.BoxGeometry(sw, H * 0.20, H * 0.016),
            mat(0x4a5058, { roughness: 0.8 }));
        back.position.set(0, seatY + H * 0.105, H * 0.055 - sw * 0.44);
        back.castShadow = true; ch.add(back);
        ch.rotation.y = yaw;
        g.add(ch);
    }

    // ── 눈높이 기준선 + 바닥 디스크 ──
    const eye = P.head.y + H * 0.045;
    g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(
        [V3(-0.3, eye, 0), V3(0.3, eye, 0)]),
        new THREE.LineBasicMaterial({ color: 0x64d29a, transparent: true, opacity: 0.45 })));
    const disc = new THREE.Mesh(new THREE.RingGeometry(0.2, 0.245, 30),
        new THREE.MeshBasicMaterial({ color: 0x64d29a, transparent: true, opacity: 0.5, side: THREE.DoubleSide }));
    disc.rotation.x = -Math.PI / 2; disc.position.y = 0.006;
    g.add(disc);
    g.userData.eyeY = eye;
    return g;
}
function subjectAim(s) {
    // 앉으면 얼굴 높이가 내려간다
    const drop = s.pose === 'sit' ? s.h * 0.215 : 0;
    return { x: s.x, y: s.h * 0.88 - drop, z: s.y };
}
// 피사체 눈높이 (카메라 높이 맞출 때 참고)
function subjectEyeY(s) { return s.h * (s.pose === 'sit' ? 0.760 : 0.975); }

// ───────── 카메라 세부 조절 ─────────
function setCam(prop, v) {
    if (isViewOnly()) return;               // 공유(보기 전용): 카메라 값 조정 금지
    const f = ensure3D(currentScene());
    const [fid, it] = activeCam();
    if (!it) return;
    const val = parseFloat(v);
    if (isNaN(val)) return;
    if (prop === 'h3') {
        const sp = specOf(it.eqId);
        it.h3 = +Math.max(0.1, val).toFixed(2);
    } else if (prop === 'focal') {
        let fv = Math.round(val);
        if (it.focalMin) fv = Math.max(it.focalMin, Math.min(it.focalMax, fv));
        it.focal = fv; focalMM = it.focal;
        const fi = document.getElementById('foc-in'); if (fi) fi.value = it.focal;
    } else if (prop === 'focus') {
        it.focus = +Math.max(0.3, val).toFixed(2);
    } else it[prop] = +val.toFixed(1);
    saveState(); build3D(); updateCamPanel();
}
function setFstopIdx(i) {
    if (isViewOnly()) return;               // 공유(보기 전용): 조리개 조정 금지
    const [fid, it] = activeCam();
    if (!it) return;
    let idx = Math.max(0, Math.min(FSTOPS.length - 1, Math.round(+i)));
    if (it.fMin) idx = Math.max(idx, FSTOPS.indexOf(it.fMin));
    it.fstop = FSTOPS[idx];
    saveState(); build3D(); updateCamPanel();
}
function focusOnSubject() {
    if (isViewOnly()) return;               // 공유(보기 전용): 포커스 변경 금지
    const f = ensure3D(currentScene());
    const [fid, it] = activeCam();
    if (!it) { alert('카메라를 먼저 배치해주세요.'); return; }
    const d = nearestSubjectDist(f, it);
    if (d === null) { alert('피사체가 없습니다. "👤 피사체 추가"를 먼저 눌러주세요.'); return; }
    it.focus = +d.toFixed(2);
    saveState(); build3D(); updateCamPanel();
    setStatus(`피사체(${d.toFixed(2)}m)에 포커스를 맞췄습니다.`);
}
function toggleDOF() {
    dofOn = !dofOn;
    document.getElementById('dof-btn').classList.toggle('primary', dofOn);
    build3D();
}
function setAspect(v) {
    if (isViewOnly()) return;               // 공유(보기 전용): 화면비 조정 금지
    previewAR = parseFloat(v) || 1.7778;
    syncPreviewFrame(); updateCamPanel();
}
function togglePreview() {
    previewOn = !previewOn;
    document.getElementById('pv-btn').textContent = previewOn ? '🖥 프리뷰 ON' : '🖥 프리뷰 OFF';
    document.getElementById('pv-btn').classList.toggle('primary', previewOn);
    syncPreviewFrame();
}
function cyclePreviewSize() {
    const i = PV_SIZES.indexOf(previewScale);
    previewScale = PV_SIZES[(i + 1) % PV_SIZES.length];
    syncPreviewFrame();
}
function toggleGuides() { guidesOn = !guidesOn; syncPreviewFrame(); }

function lookAtSubject() {
    if (isViewOnly()) return;               // 공유(보기 전용): 카메라 조준 변경 금지
    const f = ensure3D(currentScene());
    const [fid, it] = activeCam();
    if (!it) { alert('카메라를 먼저 배치해주세요.'); return; }
    const subs = f.subjects || [];
    if (!subs.length) { alert('피사체가 없습니다. "👤 피사체 추가"를 먼저 눌러주세요.'); return; }
    // 가장 가까운 피사체
    let best = subs[0], bd = Infinity;
    subs.forEach(s => {
        const d = Math.hypot(s.x - it.x, s.y - it.y);
        if (d < bd) { bd = d; best = s; }
    });
    const a = subjectAim(best);
    const dx = a.x - it.x, dz = a.z - it.y, dy = a.y - camEyeY(it);
    it.pan = +(Math.atan2(dx, dz) * 180 / Math.PI).toFixed(1);
    it.tilt = +(Math.atan2(dy, Math.hypot(dx, dz)) * 180 / Math.PI).toFixed(1);
    it.focus = +bd.toFixed(2);              // 조준한 피사체 거리로 포커스도 자동 설정
    saveState(); build3D(); updateCamPanel();
    setStatus(`피사체를 조준하고 포커스를 맞췄습니다 (거리 ${bd.toFixed(2)}m)`);
}

function updateCamPanel() {
    const panel = document.getElementById('cam-panel');
    if (!panel) return;
    if (currentScene().mode !== 'three') { panel.style.display = 'none'; return; }
    const f = ensure3D(currentScene());
    // 선택된 항목이 '카메라'일 때만 패널을 보여준다 (아무것도 선택 안 하면 숨김)
    const fid = three3Sel, it = fid && f.items[fid];
    const selEq = it && EQUIPMENT.find(e => e.id === it.eqId);
    if (!it || !selEq || selEq.cat !== 'CAM') { panel.style.display = 'none'; return; }
    panel.style.display = 'block';
    const eq = EQUIPMENT.find(e => e.id === it.eqId);
    const L = lensSpecOf(it);
    if (L && it.focalMin == null) applyLensSpec(it);
    const fl = it.focal || focalMM;
    document.getElementById('cp-name').textContent = `${eq.id} ${dispName(eq)}`;
    // 물린 렌즈가 있으면 그 렌즈가 낼 수 있는 값으로 슬라이더를 좁힌다
    const foc = document.getElementById('cp-foc'), fsl = document.getElementById('cp-fs');
    if (foc) {
        foc.min = L && L.min ? L.min : 8;
        foc.max = L && L.max ? L.max : 200;
        foc.disabled = !!(L && L.min && L.min === L.max);   // 단렌즈는 고정
    }
    if (fsl) fsl.min = it.fMin ? Math.max(0, FSTOPS.indexOf(it.fMin)) : 0;
    const ln = document.getElementById('cp-lens');
    if (ln) ln.innerHTML = L
        ? `🔎 ${esc(L.name)} · ${L.zoom ? `${L.min}–${L.max}mm` : `${L.min}mm`} · 최대개방 F${L.wide || '?'}`
        : '<span style="color:var(--tx-3)">렌즈 미장착 — 배치도에서 카메라에 렌즈를 물리면 스펙이 반영됩니다</span>';
    const set = (id, v, txt) => {
        const el = document.getElementById(id); if (el) el.value = v;
        const s = document.getElementById(id + '-v'); if (s) s.textContent = txt;
    };
    const fs = it.fstop || 2.8;
    const focusM = focusDistOf(f, it);
    const [hlo, hhi] = hRange(it);
    const ch = document.getElementById('cp-h');
    if (ch) { ch.min = hlo; ch.max = Math.max(hlo + 0.01, hhi); }
    set('cp-h', it.h3 || 1.45, (it.h3 || 1.45).toFixed(2) + 'm');
    set('cp-pan', it.pan || 0, (it.pan || 0).toFixed(0) + '°');
    set('cp-tilt', it.tilt || 0, (it.tilt || 0).toFixed(1) + '°');
    set('cp-foc', fl, fl + 'mm');
    set('cp-fs', Math.max(0, FSTOPS.indexOf(fs)), 'F' + (fs < 10 ? fs.toFixed(1) : fs));
    set('cp-fd', focusM, focusM.toFixed(2) + 'm');
    document.getElementById('dof-btn').classList.toggle('primary', dofOn);
    // 화각
    const hf = 2 * Math.atan(0.036 / (2 * fl / 1000)) * 180 / Math.PI;
    const sensorH = 0.036 / previewAR;
    const vf = 2 * Math.atan(sensorH / (2 * fl / 1000)) * 180 / Math.PI;
    let info = `화각 가로 <b>${hf.toFixed(1)}°</b> · 세로 <b>${vf.toFixed(1)}°</b>`;
    // 프레이밍
    const subs = f.subjects || [];
    if (subs.length) {
        let best = subs[0], bd = Infinity;
        subs.forEach(s => { const d = Math.hypot(s.x - it.x, s.y - it.y); if (d < bd) { bd = d; best = s; } });
        const frameH = 2 * bd * Math.tan(vf * Math.PI / 360);
        const ratio = best.h / frameH * 100;
        let shot = ratio > 105 ? '클로즈업(잘림)' : ratio > 78 ? '바스트~미디엄'
                 : ratio > 52 ? '미디엄 풀' : ratio > 34 ? '풀샷' : '와이드';
        info += `<br>피사체 <b>${bd.toFixed(2)}m</b> · 세로 <b>${frameH.toFixed(2)}m</b> 담김`;
        info += `<br>인물 ${best.h}m → <b>${ratio.toFixed(0)}%</b> · ${shot}`;
    } else {
        info += `<br><span style="color:#8b97a6">피사체를 추가하면 프레이밍이 계산됩니다</span>`;
    }
    // 심도
    const dof = dofOf(fl, fs, focusM);
    const farTxt = dof.far === Infinity ? '∞' : dof.far.toFixed(2) + 'm';
    const totTxt = dof.total === Infinity ? '∞' : (dof.total < 1
        ? (dof.total * 100).toFixed(0) + 'cm' : dof.total.toFixed(2) + 'm');
    info += `<div style="margin-top:7px;padding-top:7px;border-top:1px solid #2b3340">`;
    info += `포커스 <b>${focusM.toFixed(2)}m</b> · F${fs < 10 ? fs.toFixed(1) : fs}`;
    info += `<br>심도 <b>${dof.near.toFixed(2)}m</b> ~ <b>${farTxt}</b>`;
    info += `<br>깊이 <b>${totTxt}</b> · 과초점 ${dof.hyper.toFixed(1)}m`;
    // 피사체가 심도 안에 들어오는지
    if (subs.length) {
        const bd = nearestSubjectDist(f, it);
        const inFocus = bd >= dof.near && (dof.far === Infinity || bd <= dof.far);
        info += `<br><span style="color:${inFocus ? '#5fd39a' : '#ff8a65'};font-weight:600">`
             + `${inFocus ? '✓ 피사체 초점 범위 안' : '⚠ 피사체가 초점 범위 밖'}</span>`;
    }
    info += `</div>`;
    document.getElementById('cp-info').innerHTML = info;
    syncPreviewFrame();
}

// ───────── 조작 ─────────
function setCeiling(v) {
    const f = ensure3D(currentScene());
    f.ceilH = Math.max(1.8, Math.min(12, parseFloat(v) || 2.7));
    ['ceil-in', 'ceil-in2'].forEach(id => {
        const el = document.getElementById(id); if (el) el.value = f.ceilH;
    });
    saveState();
    if (currentScene().mode === 'three') build3D(); else renderFloor();
    updateStatus();
}
function setItemHeight(v) {
    const f = ensure3D(currentScene());
    if (!three3Sel || !f.items[three3Sel]) return;
    const it = f.items[three3Sel];
    let h = parseFloat(v); if (isNaN(h)) return;
    const rg = rigRange(it);
    if (rg) h = Math.max(rg.min, Math.min(rg.max, h));
    it.h3 = Math.max(0, +h.toFixed(2));
    saveState(); build3D(); showSel();
}
function nudgeHeight(d) {
    const f = ensure3D(currentScene());
    if (!three3Sel || !f.items[three3Sel]) { alert('먼저 장비를 클릭해 선택하세요.'); return; }
    setItemHeight((f.items[three3Sel].h3 || 0) + d);
}
function toggleFrustum() {
    frustumOn = !frustumOn;
    document.getElementById('fr-btn').classList.toggle('primary', frustumOn);
    build3D();
}
function toggleShadows() {
    shadowsOn = !shadowsOn;
    document.getElementById('sh-btn').textContent = shadowsOn ? '🌑 그림자 ON' : '🌑 그림자 OFF';
    if (R3) R3.renderer.shadowMap.enabled = shadowsOn;
    build3D();
}
function setFocal(v) {
    focalMM = Math.max(8, Math.min(400, parseFloat(v) || 35));
    const fi = document.getElementById('foc-in'); if (fi) fi.value = focalMM;   // 툴바 입력 제거됨 → 방어
    build3D();
}
function pickLens(v) {
    if (!v) return;
    setFocal(v);
}
function populateLensSelect() {
    const sel = document.getElementById('lens-sel');
    if (sel.dataset.filled) return;
    let html = '<option value="">렌즈 선택…</option>';
    EQUIPMENT.filter(e => e.cat === 'LEN').forEach(e => {
        const f = focalOf(e);
        if (!f) return;
        if (f[0] === f[1]) html += `<option value="${f[0]}">${e.id} ${f[0]}mm</option>`;
        else {
            html += `<option value="${f[0]}">${e.id} ${f[0]}mm (광각단)</option>`;
            html += `<option value="${f[1]}">${e.id} ${f[1]}mm (망원단)</option>`;
        }
    });
    sel.innerHTML = html;
    sel.dataset.filled = '1';
}
function setView(k) {
    const f = ensure3D(currentScene());
    if (!R3) return;
    const o = R3.orbit;
    if (k === 'top') { o.phi = 0.12; o.theta = -Math.PI / 2; o.dist = 14; }
    if (k === 'front') { o.phi = 1.5; o.theta = -Math.PI / 2; o.dist = 12; }
    if (k === 'iso') { o.phi = 1.05; o.theta = -0.9; o.dist = 11; }
    if (k === 'cam') {
        const ci = Object.values(f.items).find(it => {
            const eq = EQUIPMENT.find(e => e.id === it.eqId);
            return eq && eq.cat === 'CAM';
        });
        if (!ci) { alert('평면도에 카메라를 먼저 배치해주세요.'); return; }
        const rad = -(ci.rot || 0) * Math.PI / 180;
        o.tx = ci.x + Math.sin(rad) * 3;
        o.tz = ci.y + Math.cos(rad) * 3;
        o.ty = (ci.h3 || 1.45) + 0.1;
        o.dist = 3; o.phi = Math.PI / 2; o.theta = rad - Math.PI / 2;
    }
}
function renderPNG() {
    if (!R3) { alert('3D를 사용할 수 없어 렌더 이미지를 만들 수 없습니다.'); return; }
    const pv = previewOn; previewOn = false;      // 저장 이미지엔 프리뷰(PiP) 를 넣지 않는다
    draw3D();
    const url = R3.renderer.domElement.toDataURL('image/png');
    previewOn = pv; draw3D();                      // 화면의 프리뷰는 원래대로 복원
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentScene().name}_3D_${new Date().toISOString().slice(0, 10)}.png`;
    a.click();
    setStatus('렌더 이미지를 저장했습니다.');
}

// ===================== 씬 관리 =====================
function renderSceneSelect() {
    const sel = document.getElementById('scene-select');
    sel.innerHTML = '';
    for (const [id, s] of Object.entries(state.scenes)) {
        const opt = document.createElement('option');
        opt.value = id; opt.textContent = s.name;
        if (id === state.currentScene) opt.selected = true;
        sel.appendChild(opt);
    }
}
document.getElementById('scene-select').addEventListener('change', e => {
    state.currentScene = e.target.value;
    selectedIds.clear(); floorSel = null;
    saveState();
    applyEqEdits();
    switchMode(currentScene().mode || 'list');   // 선택한 씬으로 전환
});
function newScene() {
    const name = prompt('새 씬 이름 (예: 시술전후 촬영, 인터뷰 세팅)', '새 씬');
    if (!name) return;
    const id = 's' + Date.now();
    state.scenes[id] = { name: name.trim(), blocks: {}, groups: {}, mode: 'layout' };
    state.currentScene = id;
    saveState(); renderSceneSelect(); renderPalette(); renderScenePane(); switchMode('layout');
}
function renameScene() {
    const s = currentScene();
    const nv = prompt('씬 이름 변경', s.name);
    if (!nv || !nv.trim()) return;
    s.name = nv.trim();
    saveState();
    updateSceneChip();          // 툴바
    renderScenePane();          // 씬 목록
    renderSceneSelect();
    updateStatus();
    setStatus(`씬 이름을 "${s.name}"(으)로 바꿨습니다`);
}
function deleteScene() {
    if (Object.keys(state.scenes).length <= 1) { alert('마지막 씬은 삭제 불가'); return; }
    if (!confirm(`"${currentScene().name}" 씬을 삭제할까?`)) return;
    delete state.scenes[state.currentScene];
    state.currentScene = Object.keys(state.scenes)[0];
    saveState(); renderSceneSelect(); renderPalette(); renderCanvas();
}
function clearScene() {
    const s = currentScene();
    const f = s.floor || {};
    const nb = Object.keys(s.blocks || {}).length;
    const ng = Object.keys(s.groups || {}).length;
    const nf = Object.keys(f.items || {}).length;
    const nr = (f.rooms || []).length;
    const ns = (f.subjects || []).length;
    if (!nb && !nf && !nr && !ns && !f.bg) { setStatus('이미 비어 있습니다'); return; }
    if (!confirm(`"${s.name}" 씬을 완전히 비웁니다.\n\n`
        + `· 배치도 블록 ${nb}개 (그룹 ${ng}개)\n`
        + `· 평면도 장비 ${nf}개 · 방 ${nr}개 · 피사체 ${ns}개${f.bg ? ' · 배경 도면' : ''}\n`
        + `· 3D 배치 (평면도와 같은 데이터)\n\n`
        + `장비 목록과 세트는 그대로입니다. 계속할까요?`)) return;
    // 배치도
    s.blocks = {}; s.groups = {};
    // 평면도 + 3D (같은 저장소를 씀)
    s.floor = { zoom: 50, items: {}, subjects: [], bg: null,
                showClear: f.showClear !== undefined ? f.showClear : true,
                confine: f.confine !== undefined ? f.confine : true,
                ceilH: f.ceilH || 2.7,
                rooms: [{ id: 'r_default', name: DEFAULT_ROOM.name, type: 'rect',
                          x: 1.0, y: 1.0, w: DEFAULT_ROOM.w, h: DEFAULT_ROOM.h }] };
    // 선택·편집 상태
    selectedIds.clear();
    if (typeof fMulti !== 'undefined') fMulti.clear();
    three3Sel = null; floorSel = null;
    if (typeof penPts !== 'undefined') penPts = [];
    if (typeof calibPts !== 'undefined') calibPts = [];
    saveState();
    renderPalette(); renderScenePane();
    const m = s.mode;
    if (m === 'three' && R3) { build3D(); showSel(); }
    else if (m === 'floor') renderFloor();
    else if (m === 'list') renderList();
    else renderCanvas();
    updateStatus(); updateEmptyHints();
    setStatus(`"${s.name}" 씬을 초기화했습니다 (배치도 · 평면도 · 3D)`);
}

// ===================== JSON I/O =====================
function exportJSON() {
    const blob = new Blob([JSON.stringify(state, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `장비배치_${new Date().toISOString().slice(0,10)}.json`;
    a.click(); URL.revokeObjectURL(url);
}
function importJSON() {
    const input = document.createElement('input');
    input.type = 'file'; input.accept = '.json';
    input.onchange = e => {
        const f = e.target.files[0]; if (!f) return;
        const reader = new FileReader();
        reader.onload = ev => {
            try {
                const data = JSON.parse(ev.target.result);
                if (!data.scenes || !data.currentScene) throw new Error('형식 오류');
                if (confirm('현재 배치를 덮어씁니다. 계속?')) {
                    state = data;
                    saveState(); renderSceneSelect(); renderPalette(); renderCanvas();
                }
            } catch (err) { alert('불러오기 실패: ' + err.message); }
        };
        reader.readAsText(f);
    };
    input.click();
}

// ===================== 초기 렌더 =====================
// 저장된 스냅 설정 복원
if (state.snapEnabled) {
    snapEnabled = true;
    const sb = document.getElementById('snap-btn');
    sb.textContent = '⊞ 스냅 ON';
    sb.classList.add('primary');
}
if (state.palHidden) {
    document.getElementById('app').classList.add('pal-hidden');
    document.getElementById('panel-tab').textContent = '›';
} else document.getElementById('panel-tab').textContent = '‹';
if (state.rigView) rigView = state.rigView;
renderSceneSelect();
renderPalette();
activeCat = state.cat || 'ALL';
railMore = !!state.railMore;
railCats = state.railCats !== false;
if (RAIL_MORE.includes(activeCat)) railMore = true;
renderRail();
if ((state.pane || 'equip') === 'equip') openCat(activeCat, true);
else openPane(state.pane, true);
applyEqEdits();
(async function boot() {
    const sid = new URLSearchParams(location.search).get('s');
    if (sid) { loadSharedScene(sid).catch(() => {}); return; }
    switchMode(currentScene().mode || 'list');
    if (sbReady()) {
        await ensureAuth();
        syncAuthUI();
        if (isLoggedIn()) await pullWorkspace();       // 로그인 상태면 서버 작업공간을 먼저 가져온다
        await loadEquipmentFromServer();
        switchMode(currentScene().mode || 'list');     // 가져온 씬으로 화면 다시 그림
        renderSceneSelect(); renderScenePane(); renderList(); renderPalette();
    }
})();
</script>
</body>
</html>
"""

HTML = HTML.replace('__DATA__', DATA_JSON)
HTML = HTML.replace('/*__THREEJS__*/', THREE_SRC)
HTML = HTML.replace('__WATERMARK__', WM_DATA)

OUT = os.path.join(ROOT, 'dist', 'index.html')
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(HTML)

import os
print(f"✅ {OUT}")
print(f"크기: {os.path.getsize(OUT):,} bytes")
