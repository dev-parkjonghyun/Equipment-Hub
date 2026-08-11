#!/usr/bin/env bash
# 빌드 → 문법 검사 → 테스트. 이 순서를 지키세요.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f vendor/three.min.js ]; then
  echo "Three.js 가 없습니다. 받아옵니다…"
  npm install three@0.149.0 --no-save --silent
  mkdir -p vendor && cp node_modules/three/build/three.min.js vendor/
fi

python3 generate_html.py

node -e "
const fs=require('fs');
const B=[...fs.readFileSync('dist/index.html','utf-8').matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
try { new Function(B[1].replace(/const EQUIPMENT = .*?;/s,'const EQUIPMENT=[];')); console.log('✅ JS 문법 OK'); }
catch(e){ console.error('❌ JS 문법 오류:', e.message); process.exit(1); }
"
./run-tests.sh
