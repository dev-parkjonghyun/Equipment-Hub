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
  # macOS(BSD)·Linux(GNU) 모두에서 도는 sed 로 개수를 뽑는다 (grep -oP 는 맥에서 안 됨)
  n=$(echo "$out"   | sed -n 's/.*결과: \([0-9]*\) 통과.*/\1/p'); n=${n:-0}
  bad=$(echo "$out" | sed -n 's/.*통과 \/ \([0-9]*\) 실패.*/\1/p'); bad=${bad:-1}
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
