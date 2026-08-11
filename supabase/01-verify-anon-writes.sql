-- ══════════════════════════════════════════════════════════
--  익명이 실제로 쓸 수 있는 게 있는지 확정 확인
--  b&a 프로젝트 SQL Editor 에서 실행 (읽기만 합니다)
-- ══════════════════════════════════════════════════════════

-- ① 익명 쓰기를 허용하는 정책이 하나라도 있는가?
--    결과가 0행이면 → GRANT 가 열려 있어도 익명은 아무것도 못 씁니다. 안전합니다.
select
  tablename                       as "테이블",
  policyname                      as "정책 이름",
  cmd                             as "동작",
  coalesce(with_check, qual, '(조건 없음)') as "허용 조건"
from pg_policies
where schemaname = 'public'
  and cmd in ('INSERT', 'UPDATE', 'DELETE', 'ALL')
  and ('anon' = any(roles) or 'public' = any(roles))
order by tablename, cmd;

-- ② 한 줄 판정
select
  case when count(*) = 0
    then '✅ 익명은 쓰기 불가 — anon 키가 공개돼도 데이터를 못 바꿉니다'
    else '⚠ 익명 쓰기 정책 ' || count(*) || '건 — 위 목록의 조건을 확인하세요'
  end as "판정"
from pg_policies
where schemaname = 'public'
  and cmd in ('INSERT', 'UPDATE', 'DELETE', 'ALL')
  and ('anon' = any(roles) or 'public' = any(roles));

-- ③ 익명이 읽을 수 있는 테이블 (읽기는 보통 의도된 것이지만 한 번 훑어보세요)
select
  tablename   as "테이블",
  policyname  as "정책",
  coalesce(qual, '(조건 없음 — 전체 공개)') as "읽기 조건"
from pg_policies
where schemaname = 'public'
  and cmd in ('SELECT', 'ALL')
  and ('anon' = any(roles) or 'public' = any(roles))
order by tablename;
