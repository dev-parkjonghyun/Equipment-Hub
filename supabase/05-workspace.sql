-- ══════════════════════════════════════════════════════════
--  스튜디오 작업공간(씬·세트)을 Supabase 로 — 테이블 + 권한
--  SQL Editor 에 붙여넣고 실행하세요. 기존 테이블은 건드리지 않습니다.
--
--  씬/세트는 원래 브라우저(localStorage)에만 있었습니다. 이 테이블에 저장하면
--  로그인한 스튜디오 계정이 다른 기기·브라우저에서도 이어서 작업할 수 있습니다.
--
--  · 스튜디오 공용 단일 행(id='studio') — 로그인한 계정끼리 같은 씬을 공유
--  · 읽기/쓰기 : 로그인한 스튜디오 계정만
--  · 익명(공유 링크로 들어온 사람) : 접근 없음 (정책·권한 모두 없음)
-- ══════════════════════════════════════════════════════════

-- 안전장치: 같은 이름의 테이블이 이미 있으면 알린다
do $$
begin
  if exists (select 1 from pg_tables
             where schemaname='public' and tablename='gear_workspaces') then
    raise notice 'gear_workspaces 가 이미 있습니다. 아래 구문은 건너뜁니다 (기존 데이터 유지).';
  end if;
end $$;

-- ── 작업공간 ─────────────────────────────────────────────
create table if not exists public.gear_workspaces (
  id          text primary key default 'studio',   -- 스튜디오 공용 단일 행
  data        jsonb not null,                       -- { scenes, sets, currentScene }
  updated_at  timestamptz not null default now()    -- 앱이 저장할 때마다 함께 보냄 (마지막 저장 우선)
);

alter table public.gear_workspaces enable row level security;

-- 로그인한 스튜디오 계정: 읽기/쓰기 전부. (동시 수정 시 마지막 저장이 이김)
drop policy if exists "gear: authed reads workspace" on public.gear_workspaces;
create policy "gear: authed reads workspace"
  on public.gear_workspaces for select to authenticated using (true);

drop policy if exists "gear: authed writes workspace" on public.gear_workspaces;
create policy "gear: authed writes workspace"
  on public.gear_workspaces for insert to authenticated with check (true);

drop policy if exists "gear: authed updates workspace" on public.gear_workspaces;
create policy "gear: authed updates workspace"
  on public.gear_workspaces for update to authenticated using (true) with check (true);

-- Data API 노출 (Automatically expose new tables 를 꺼둔 경우에도 동작하게)
grant usage on schema public to authenticated;
grant select, insert, update on public.gear_workspaces to authenticated;

-- 익명에게는 어떤 권한도 주지 않는다 (RLS 와 이중 잠금)
revoke all on public.gear_workspaces from anon;

-- ══════════════════════════════════════════════════════════
--  확인 — 모두 true 여야 합니다
-- ══════════════════════════════════════════════════════════
select
  (select count(*) from pg_tables where schemaname='public'
     and tablename='gear_workspaces') = 1                                  as "테이블 존재",
  (select bool_and(rowsecurity) from pg_tables where schemaname='public'
     and tablename='gear_workspaces')                                      as "RLS 켜짐",
  (select count(*) from pg_policies where schemaname='public'
     and tablename='gear_workspaces') >= 3                                 as "정책 3개",
  has_table_privilege('authenticated','public.gear_workspaces','INSERT')   as "로그인 저장 가능",
  has_table_privilege('authenticated','public.gear_workspaces','UPDATE')   as "로그인 수정 가능",
  not has_table_privilege('anon','public.gear_workspaces','SELECT')        as "익명 읽기 불가",
  not has_table_privilege('anon','public.gear_workspaces','INSERT')        as "익명 저장 불가";
