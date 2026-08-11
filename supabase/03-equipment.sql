-- ══════════════════════════════════════════════════════════
--  장비 마스터를 Supabase 로 — 테이블 + 권한
--  SQL Editor 에 붙여넣고 실행하세요. 기존 테이블은 건드리지 않습니다.
--
--  읽기 : 누구나 (앱을 여는 사람 모두)
--  쓰기 : 로그인한 스튜디오 계정만
-- ══════════════════════════════════════════════════════════

-- ── 장비 마스터 ──────────────────────────────────────────
create table if not exists public.gear_equipment (
  id            text primary key,               -- 자산번호 (CAM-001)
  nick          text,                           -- 별칭 (현장에서 부르는 이름)
  cat           text not null,                  -- 카테고리 코드 (CAM)
  cat_label     text,                           -- 카테고리 표기 (카메라 본체(CAM))
  sub           text,                           -- 세부분류
  product       text,                           -- 제품명
  brand         text,
  model         text,
  serial        text,
  status        text not null default '정상',   -- 정상 · 수리필요 · 폐기
  location      text,                           -- 보관위치
  image_url     text,
  purchased_on  date,
  vendor        text,
  price         integer,
  checked_on    date,
  check_cycle   integer,
  next_check    date,
  note          text,
  sort_order    integer,
  active        boolean not null default true,  -- false = 목록에서 숨김 (이력은 남김)
  updated_at    timestamptz not null default now(),
  updated_by    uuid
);
create index if not exists gear_equipment_cat_idx on public.gear_equipment (cat, id);

-- ── 3D · 평면도 치수 ─────────────────────────────────────
create table if not exists public.gear_specs (
  id         text primary key references public.gear_equipment(id) on delete cascade,
  w          numeric,      -- 폭 (m)
  d          numeric,      -- 깊이 (m)
  h          numeric,      -- 높이 (m)
  h_min      numeric,      -- 최소높이 (스탠드·삼각대)
  h_max      numeric,      -- 최대높이
  default_h  numeric,      -- 기본 설치높이
  src        text,         -- 치수 출처 (제조사 공식 · 평균 · 추정)
  rule       text,         -- 적용 규칙
  basis      text,         -- 근거
  updated_at timestamptz not null default now()
);

-- ── 수정 시각 자동 기록 ──────────────────────────────────
create or replace function public.gear_touch()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  if to_jsonb(new) ? 'updated_by' then new.updated_by = auth.uid(); end if;
  return new;
end $$;

drop trigger if exists gear_equipment_touch on public.gear_equipment;
create trigger gear_equipment_touch before update on public.gear_equipment
  for each row execute function public.gear_touch();

drop trigger if exists gear_specs_touch on public.gear_specs;
create trigger gear_specs_touch before update on public.gear_specs
  for each row execute function public.gear_touch();

-- ── 접근 권한 ────────────────────────────────────────────
alter table public.gear_equipment enable row level security;
alter table public.gear_specs     enable row level security;

-- 읽기는 누구나 (공유 링크로 들어온 사람도 장비 이름을 봐야 함)
drop policy if exists "gear: anyone reads equipment" on public.gear_equipment;
create policy "gear: anyone reads equipment"
  on public.gear_equipment for select to anon, authenticated using (true);

drop policy if exists "gear: anyone reads specs" on public.gear_specs;
create policy "gear: anyone reads specs"
  on public.gear_specs for select to anon, authenticated using (true);

-- 쓰기는 로그인한 계정만
drop policy if exists "gear: authed writes equipment" on public.gear_equipment;
create policy "gear: authed writes equipment"
  on public.gear_equipment for all to authenticated using (true) with check (true);

drop policy if exists "gear: authed writes specs" on public.gear_specs;
create policy "gear: authed writes specs"
  on public.gear_specs for all to authenticated using (true) with check (true);

-- Data API 노출 (Automatically expose new tables 를 꺼둔 경우에도 동작하게)
grant select on public.gear_equipment to anon, authenticated;
grant select on public.gear_specs     to anon, authenticated;
grant insert, update, delete on public.gear_equipment to authenticated;
grant insert, update, delete on public.gear_specs     to authenticated;

-- 익명은 읽기만 — 권한 자체를 없애 이중으로 잠근다
revoke insert, update, delete, truncate on public.gear_equipment from anon;
revoke insert, update, delete, truncate on public.gear_specs     from anon;

-- ══════════════════════════════════════════════════════════
--  확인 — 모두 true 여야 합니다
-- ══════════════════════════════════════════════════════════
select
  (select count(*) from pg_tables where schemaname='public'
     and tablename in ('gear_equipment','gear_specs')) = 2          as "테이블 2개",
  (select bool_and(rowsecurity) from pg_tables where schemaname='public'
     and tablename in ('gear_equipment','gear_specs'))              as "RLS 켜짐",
  has_table_privilege('anon','public.gear_equipment','SELECT')      as "누구나 읽기",
  not has_table_privilege('anon','public.gear_equipment','UPDATE')  as "익명 수정 불가",
  not has_table_privilege('anon','public.gear_equipment','INSERT')  as "익명 추가 불가",
  has_table_privilege('authenticated','public.gear_equipment','UPDATE') as "로그인 수정 가능";
