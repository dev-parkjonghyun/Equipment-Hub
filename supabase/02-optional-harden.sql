-- ══════════════════════════════════════════════════════════
--  (선택) 불필요한 GRANT 회수 — 이중 잠금
--
--  RLS 가 이미 막고 있으므로 필수는 아닙니다.
--  "정책도 있고 권한도 있어야 통과" 대신 "권한부터 없음" 으로
--  한 겹 더 두르고 싶을 때만 쓰세요.
--
--  ⚠ 먼저 01-verify-anon-writes.sql 을 돌려서
--     익명 쓰기 정책이 0건인지 확인하세요.
--     쓰기 정책이 있는 테이블에 이걸 돌리면 그 기능이 멈춥니다.
-- ══════════════════════════════════════════════════════════

-- 1단계: 실행할 구문을 '보기만' 합니다. 결과를 눈으로 확인하세요.
select
  'revoke update, delete, truncate on public.' || tablename || ' from anon;' as "실행할 구문"
from pg_tables t
where schemaname = 'public'
  -- 익명 쓰기 정책이 없는 테이블만 대상
  and not exists (
    select 1 from pg_policies p
    where p.schemaname = 'public' and p.tablename = t.tablename
      and p.cmd in ('INSERT','UPDATE','DELETE','ALL')
      and ('anon' = any(p.roles) or 'public' = any(p.roles))
  )
  and exists (
    select 1 from information_schema.role_table_grants g
    where g.table_schema = 'public' and g.table_name = t.tablename
      and g.grantee = 'anon' and g.privilege_type in ('UPDATE','DELETE','TRUNCATE')
  )
order by tablename;

-- 2단계: 위 결과가 납득되면, 아래 블록의 주석을 풀고 실행하세요.
/*
do $$
declare r record;
begin
  for r in
    select tablename from pg_tables t
    where schemaname = 'public'
      and not exists (
        select 1 from pg_policies p
        where p.schemaname='public' and p.tablename=t.tablename
          and p.cmd in ('INSERT','UPDATE','DELETE','ALL')
          and ('anon' = any(p.roles) or 'public' = any(p.roles)))
  loop
    execute format('revoke update, delete, truncate on public.%I from anon', r.tablename);
    raise notice '회수: %', r.tablename;
  end loop;
end $$;
*/
