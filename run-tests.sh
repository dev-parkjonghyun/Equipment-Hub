#!/usr/bin/env bash
# 전체 테스트 실행. 하나라도 실패하면 0 이 아닌 코드로 끝납니다.
set -uo pipefail
cd "$(dirname "$0")"

if [ ! -f dist/index.html ]; then
  echo "dist/index.html 이 없습니다. 먼저 빌드하세요:  python3 generate_html.py"
  exit 1
fi

total=0; failed=0
for f in tests/test_*.js; do
  out=$(node "$f" 2>&1 | tail -1)
  n=$(echo "$out"  | grep -oP '\d+(?= 통과)' || echo 0)
  bad=$(echo "$out" | grep -oP '\d+(?= 실패)' || echo 1)
  total=$((total + n))
  if [ "$bad" != "0" ]; then
    failed=$((failed + 1))
    printf '\033[31m✗ %-16s %s\033[0m\n' "$(basename "$f" .js)" "$out"
    node "$f" 2>&1 | grep "❌" | head -5 | sed 's/^/    /'
  else
    printf '\033[32m✓\033[0m %-16s %s개\n' "$(basename "$f" .js)" "$n"
  fi
done

echo "────────────────────────────"
if [ "$failed" -eq 0 ]; then
  printf '\033[32m전체 %d개 통과\033[0m\n' "$total"
else
  printf '\033[31m%d개 파일 실패 (통과 %d개)\033[0m\n' "$failed" "$total"
  exit 1
fi
