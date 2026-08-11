-- ══════════════════════════════════════════════════════════
--  EH Studio 장비 배치도 — Supabase 스키마
--  Supabase 대시보드 → SQL Editor 에 붙여넣고 실행하세요.
--
--  모든 이름에 gear_ 접두사가 붙어 있어, 전용 프로젝트든
--  기존 프로젝트(b&a)에 얹든 그대로 실행됩니다.
--  기존 테이블은 하나도 건드리지 않습니다.
--
--  "Automatically expose new tables" 를 껐어도 필요한 권한을
--  이 파일이 직접 부여하므로 그대로 동작합니다.
-- ══════════════════════════════════════════════════════════

-- 안전장치: 같은 이름의 테이블이 이미 있으면 멈춘다
do $$
begin
  if exists (select 1 from pg_tables
             where schemaname='public' and tablename in ('gear_scenes','gear_scene_views')) then
    raise notice 'gear_ 테이블이 이미 있습니다. 아래 구문은 건너뜁니다 (기존 데이터 유지).';
  end if;
end $$;

-- ── 공유 씬 ──────────────────────────────────────────────
create table if not exists public.gear_scenes (
  id          text primary key,                    -- 링크에 쓰이는 짧은 임의 문자열
  name        text not null default '촬영 배치',
  data        jsonb not null,                      -- 씬 전체 (블록·평면도·3D)
  bg_path     text,                                -- Storage 에 올린 배경 도면 경로
  is_public   boolean not null default true,       -- false 로 바꾸면 링크가 즉시 죽음
  expires_at  timestamptz,                         -- null 이면 만료 없음
  views       integer not null default 0,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

create index if not exists gear_scenes_created_idx on public.gear_scenes (created_at desc);

-- 살아있는 링크인지 판단하는 기준을 한 곳에 모아둔다
create or replace function public.gear_scene_is_live(s public.gear_scenes)
returns boolean language sql immutable as $$
  select s.is_public and (s.expires_at is null or s.expires_at > now())
$$;

alter table public.gear_scenes enable row level security;

-- 익명(공유 링크로 들어온 사람): 살아있는 씬만 읽기. 쓰기는 전부 차단.
drop policy if exists "gear: anon reads live scenes" on public.gear_scenes;
create policy "gear: anon reads live scenes"
  on public.gear_scenes for select
  to anon
  using (is_public and (expires_at is null or expires_at > now()));

-- 우리 스튜디오(로그인한 사용자): 전부 가능
drop policy if exists "gear: authed full access" on public.gear_scenes;
create policy "gear: authed full access"
  on public.gear_scenes for all
  to authenticated
  using (true) with check (true);

-- ⚠ 로그인 없이 편집기에서 바로 공유 링크를 만들려면 아래 정책이 필요합니다.
--   대신 누구나 씬을 만들 수 있게 되므로, 쓰기 제한을 Edge Function 으로 옮기거나
--   스튜디오 계정 로그인을 붙이는 편이 안전합니다. (SETUP.md 6단계 참고)
drop policy if exists "gear: anon creates scenes" on public.gear_scenes;
create policy "gear: anon creates scenes"
  on public.gear_scenes for insert
  to anon
  with check (
    is_public = true
    and expires_at is not null                    -- 만료 없는 영구 링크는 금지
    and expires_at < now() + interval '180 days'
    and length(data::text) < 3000000              -- 3MB 상한 (도면 포함)
  );

-- Data API(PostgREST)가 이 테이블에 닿을 수 있게 권한을 명시적으로 준다.
-- "Automatically expose new tables" 를 꺼둔 프로젝트에서도 동작하게 하기 위함.
-- 실제 접근 제어는 위의 RLS 정책이 담당한다.
grant usage on schema public to anon, authenticated;
grant select on public.gear_scenes to anon;
grant insert on public.gear_scenes to anon;              -- '누구나 공유 링크 생성' 정책을 지웠다면 이 줄도 지우세요
grant select, insert, update, delete on public.gear_scenes to authenticated;

-- ── 조회 기록 (누가 언제 열었는지) ────────────────────────
create table if not exists public.gear_scene_views (
  id          bigserial primary key,
  scene_id    text not null references public.gear_scenes(id) on delete cascade,
  viewed_at   timestamptz not null default now(),
  ua          text
);
alter table public.gear_scene_views enable row level security;

drop policy if exists "gear: anon logs view" on public.gear_scene_views;
create policy "gear: anon logs view"
  on public.gear_scene_views for insert to anon with check (true);

drop policy if exists "gear: authed reads views" on public.gear_scene_views;
create policy "gear: authed reads views"
  on public.gear_scene_views for select to authenticated using (true);

grant insert on public.gear_scene_views to anon;
grant select on public.gear_scene_views to authenticated;
grant usage, select on sequence public.gear_scene_views_id_seq to anon, authenticated;

-- 프로젝트에 "Automatically expose new tables" 가 켜져 있으면 새 테이블에
-- anon 전체 권한이 자동으로 붙습니다. 우리 테이블에서만 필요 없는 것을 되돌립니다.
-- (RLS 가 이미 막지만 권한 자체를 없애 이중으로 잠급니다. 기존 테이블은 건드리지 않습니다.)
revoke update, delete, truncate on public.gear_scenes from anon;
revoke update, delete, truncate on public.gear_scene_views from anon;
revoke select on public.gear_scene_views from anon;      -- 조회 기록은 우리만 봅니다

-- 조회수 증가 (RLS 를 우회해야 하므로 security definer)
create or replace function public.gear_bump_view(p_id text, p_ua text default null)
returns void language plpgsql security definer set search_path = public as $$
begin
  update public.gear_scenes set views = views + 1 where id = p_id;
  insert into public.gear_scene_views (scene_id, ua) values (p_id, left(coalesce(p_ua,''), 300));
end $$;

revoke all on function public.gear_bump_view(text, text) from public;
grant execute on function public.gear_bump_view(text, text) to anon, authenticated;

-- ── 만료된 씬 정리 (선택: pg_cron 으로 매일 돌리면 좋음) ──
create or replace function public.gear_purge_expired()
returns integer language plpgsql security definer set search_path = public as $$
declare n integer;
begin
  delete from public.gear_scenes
   where expires_at is not null and expires_at < now() - interval '7 days';
  get diagnostics n = row_count;
  return n;
end $$;

-- ── Storage 버킷 ─────────────────────────────────────────
-- 대시보드 → Storage → New bucket 에서 만들어도 됩니다.
insert into storage.buckets (id, name, public)
values ('gear-photos', 'gear-photos', false)
on conflict (id) do nothing;

insert into storage.buckets (id, name, public)
values ('gear-plans', 'gear-plans', true)      -- 공유 링크에서 보여줄 배경 도면
on conflict (id) do nothing;

-- 배경 도면은 공개 읽기, 업로드는 로그인 사용자만
drop policy if exists "gear: public reads plans" on storage.objects;
create policy "gear: public reads plans" on storage.objects
  for select to anon using (bucket_id = 'gear-plans');

drop policy if exists "gear: authed writes plans" on storage.objects;
create policy "gear: authed writes plans" on storage.objects
  for insert to authenticated with check (bucket_id = 'gear-plans');


-- ══════════════════════════════════════════════════════════
--  설치 확인 — 아래를 실행해 결과가 모두 true 인지 보세요
-- ══════════════════════════════════════════════════════════
select
  (select count(*) from pg_tables
    where schemaname='public' and tablename in ('gear_scenes','gear_scene_views')) = 2   as "테이블 2개",
  (select bool_and(rowsecurity) from pg_tables
    where schemaname='public' and tablename in ('gear_scenes','gear_scene_views'))       as "RLS 켜짐",
  (select count(*) from pg_policies
    where schemaname='public' and tablename='gear_scenes') >= 2                     as "정책 있음",
  has_table_privilege('anon','public.gear_scenes','SELECT')                         as "익명 읽기 가능",
  not has_table_privilege('anon','public.gear_scenes','UPDATE')                     as "익명 수정 불가",
  not has_table_privilege('anon','public.gear_scenes','DELETE')                     as "익명 삭제 불가",
  not has_table_privilege('anon','public.gear_scene_views','SELECT')                as "조회기록 비공개",
  (select count(*) from storage.buckets
    where id in ('gear-photos','gear-plans')) = 2                              as "버킷 2개";
