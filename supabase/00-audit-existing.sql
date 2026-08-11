-- ══════════════════════════════════════════════════════════
--  기존 프로젝트(b&a)에 테이블을 얹기 전 안전 점검
--
--  기존 Supabase 프로젝트의 SQL Editor 에서 실행하세요.
--  아무것도 바꾸지 않고 읽기만 합니다.
-- ══════════════════════════════════════════════════════════

-- ① RLS 가 꺼진 테이블이 있는가?  → 있으면 anon 키로 통째로 읽힙니다
select
  tablename                                   as "테이블",
  case when rowsecurity then '잠김' else '⚠ 열림' end as "RLS"
from pg_tables
where schemaname = 'public'
order by rowsecurity, tablename;

-- ② 익명(anon)에게 권한이 열린 테이블
select
  table_name                                  as "테이블",
  string_agg(privilege_type, ', ' order by privilege_type) as "anon 권한"
from information_schema.role_table_grants
where grantee = 'anon' and table_schema = 'public'
group by table_name
order by table_name;

-- ③ 익명이 통과할 수 있는 정책 (조건이 true 면 사실상 전면 허용)
select
  tablename       as "테이블",
  policyname      as "정책",
  cmd             as "동작",
  coalesce(qual, '(없음)')       as "읽기 조건",
  coalesce(with_check, '(없음)') as "쓰기 조건"
from pg_policies
where schemaname = 'public'
  and ('anon' = any(roles) or 'public' = any(roles))
order by tablename, cmd;

-- ④ 한 줄 요약
--    · "RLS 꺼진 테이블" 과 "익명 무조건 허용 정책" 은 반드시 0 이어야 합니다.
--    · "익명 수정·삭제 권한" 은 Supabase 기본값이라 0 이 아닌 게 정상입니다.
--      RLS 가 켜져 있으면(첫 칸 0) 이 권한만으로는 아무것도 못 합니다.
--      확실히 하려면 01-verify-anon-writes.sql 을 이어서 실행하세요.
select
  (select count(*) from pg_tables
     where schemaname='public' and not rowsecurity)                     as "RLS 꺼진 테이블",
  (select count(*) from information_schema.role_table_grants
     where grantee='anon' and table_schema='public'
       and privilege_type in ('UPDATE','DELETE','TRUNCATE'))            as "익명 수정·삭제 권한",
  (select count(*) from pg_policies
     where schemaname='public' and ('anon'=any(roles) or 'public'=any(roles))
       and cmd in ('UPDATE','DELETE','ALL')
       and (qual is null or qual = 'true'))                             as "익명 무조건 허용 정책";
