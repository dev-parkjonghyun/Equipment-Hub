# EH Studio 장비 배치도 — 서버 설치 안내

공유 링크와 사진 인식을 쓰려면 두 가지가 필요합니다.

| | 무엇을 | 왜 |
|---|---|---|
| **GitHub Pages** | HTML 파일을 인터넷에 올림 | 외부인이 링크로 열려면 어딘가 올라가 있어야 함 |
| **Supabase** | 씬 데이터 저장 + 사진 분석 | 짧은 링크·회수·도면 저장, API 키 숨기기 |

전부 무료 범위 안에서 됩니다. 30~40분쯤 걸려요.

---

## 0. 먼저 정하기 — 새 프로젝트 vs 기존 프로젝트

Supabase의 컴퓨트 크레딧 **$10은 조직당 한 번**만 나옵니다. 이미 b&a 프로젝트가 쓰고 있어서,
프로젝트를 새로 만들면 **매달 $10이 더 붙습니다.**

| | 새 프로젝트 | 기존(b&a)에 얹기 |
|---|---|---|
| 추가 비용 | 월 $10 | **$0** |
| 데이터 분리 | 완전 분리 | 테이블만 분리 (`gear_` 접두사) |
| 보안 | 독립 | **b&a의 RLS 상태에 함께 묶임** |
| 운영 사고 | 서로 무관 | 마이그레이션 실수 시 함께 위험 |

**기존 프로젝트에 얹기로 했다면 아래 점검을 먼저 하세요.** 3단계로 건너뛰지 마세요.

### 0-1. 기존 프로젝트 안전 점검 (필수)

b&a 프로젝트의 SQL Editor 에서 `supabase/00-audit-existing.sql` 을 실행합니다.
읽기만 하므로 아무것도 바뀌지 않습니다.

마지막 요약 세 칸이 **모두 0** 이어야 합니다.

| 항목 | 0이 아니면 |
|---|---|
| RLS 꺼진 테이블 | 그 테이블은 anon 키로 통째로 읽힙니다. **RLS를 켜세요.** |
| 익명 수정·삭제 권한 | 외부인이 데이터를 고칠 수 있습니다. 권한을 회수하세요. |
| 익명 무조건 허용 정책 | 조건 없는 정책입니다. 조건을 붙이세요. |

> **왜 중요한가**
> 장비 앱을 GitHub Pages에 올리면 anon 키가 웹에 공개됩니다. 이건 Supabase의 정상 설계라
> RLS만 제대로 있으면 안전합니다. 하지만 b&a에 RLS가 빠진 테이블이 하나라도 있으면,
> 그 키로 b&a 데이터까지 닿을 수 있습니다.
>
> 점검 결과가 깨끗하면 → 기존 프로젝트에 얹어도 안전합니다.
> 0이 아닌 항목이 있으면 → **b&a부터 고치거나**, 새 프로젝트로 분리하세요.

### 0-2. 기존 프로젝트를 쓰기로 했다면

1단계(프로젝트 생성)를 건너뛰고 **2단계**부터 진행하세요.
스키마의 모든 이름에 `gear_` 접두사가 붙어 있어 기존 테이블과 섞이지 않습니다.

---

## 1. Supabase 프로젝트 만들기 (새로 만들 때만)

New project 화면에서 이렇게 맞춰주세요.

| 항목 | 설정 | 이유 |
|---|---|---|
| Project name | `Equipment Hub` | 자유 |
| Compute size | **MICRO** 그대로 | 씬 하나가 4KB라 한참 남습니다 |
| Database password | **Generate a password** 로 만들고 저장 | 잃어버리면 재설정해야 합니다 |
| Region | **Northeast Asia (Seoul)** | 목록을 펼쳐 서울을 직접 고르세요 |
| Enable Data API | **켜기** | 이 앱이 `/rest/v1/` 로 통신합니다 |
| Automatically expose new tables | **끄기** | 새 테이블이 자동 공개되지 않게. schema.sql 이 필요한 권한만 직접 줍니다 |
| Enable automatic RLS | **켜기** | 실수로 RLS 없는 테이블을 만들어도 자동으로 잠깁니다 |

> **Region이 "Asia-Pacific" 으로만 보이면 펼쳐서 Seoul을 고르세요.** 그룹 이름이라 그대로 두면
> 도쿄나 싱가포르에 잡힐 수 있습니다. 나중에 못 바꾸고 프로젝트를 새로 만들어야 합니다.

> b&a 프로젝트와 분리했습니다. 데이터가 섞이지 않고 권한 설정도 독립적입니다.

## 2. 테이블 만들기

대시보드 → **SQL Editor** → New query → `supabase/schema.sql` 내용을 통째로 붙여넣고 **Run**.

만들어지는 것 (전부 `gear_` 로 시작 — 기존 테이블은 건드리지 않습니다):

- `gear_scenes` — 공유된 씬 (만료일·공개여부·조회수)
- `gear_scene_views` — 누가 언제 열었는지
- `gear-photos` / `gear-plans` — 사진·도면 저장소
- **RLS 정책** — 외부인은 *살아있는 씬만 읽기*, 쓰기는 차단

실행 후 파일 맨 아래 **설치 확인 쿼리**를 돌려보세요. 8개 항목이 모두 `true` 여야 합니다.

| 확인 항목 | 뜻 |
|---|---|
| 테이블 2개 | `gear_scenes`, `gear_scene_views` 생성됨 |
| RLS 켜짐 | 둘 다 정책 검사를 거침 |
| 정책 있음 | 읽기·쓰기 정책이 걸림 |
| 익명 읽기 가능 | 공유 링크로 씬을 볼 수 있음 |
| 익명 수정 불가 | 외부인이 씬을 못 고침 |
| 익명 삭제 불가 | 외부인이 씬을 못 지움 |
| 조회기록 비공개 | 누가 열었는지는 우리만 봄 |
| 버킷 2개 | 사진·도면 저장소 생성됨 |

### 여기서 결정할 것 하나

기본 SQL에는 **로그인 없이도 공유 링크를 만들 수 있는 정책**이 들어 있습니다 (`anon creates scenes`). 편하지만, 주소를 아는 사람이면 누구나 씬을 만들 수 있습니다.

- **지금은 이대로 두기** — 주소가 알려지지 않았고, 만료 강제·용량 제한이 걸려 있어 실질 위험은 낮습니다
- **더 안전하게** — 그 정책만 지우고(`drop policy "anon creates scenes" on public.scenes;`) 스튜디오 계정 로그인을 붙입니다. 나중에 필요해지면 알려주세요

## 3. 주소와 키 가져오기

대시보드 → **Project Settings → API**

- **Project URL** → `https://xxxxx.supabase.co`
- **anon public** 키 → `eyJhbGci...`

> ⚠️ **service_role 키는 절대 앱에 넣지 마세요.** RLS를 무시하는 마스터 키입니다.
> anon 키는 공개돼도 괜찮습니다 — RLS가 막아줍니다.

## 4. Edge Function 올리기 — **나중에 해도 됩니다**

> 공유 기능만 쓸 거라면 이 단계를 건너뛰고 **5단계**로 가세요.
> 사진 인식은 Anthropic API 크레딧(선불)이 필요하지만, 공유 기능은 추가 비용이 없습니다.
> 함수가 없는 상태에서 사진 버튼을 눌러도 앱이 "아직 설치 전"이라고 안내만 하고 넘어갑니다.

### 무료로 하고 싶다면

네이버 **CLOVA OCR** 은 월 무료 한도가 있어서, 사용량이 적으면 실질 0원으로 쓸 수 있습니다.
다만 읽은 글자를 자산번호로 연결하는 단계는 여전히 어떤 형태로든 필요합니다.
나중에 이 부분을 다룰 때 다시 정리하겠습니다.


Anthropic 콘솔(https://console.anthropic.com)에서 API 키를 하나 만들어 두세요.

### 방법 A — 대시보드에서 (터미널 불필요, 권장)

1. 대시보드 → **Edge Functions** → **Deploy a new function** → **Via Editor**
2. 이름을 정확히 `read-gear-photo` 로 입력 (앱이 이 이름으로 호출합니다)
3. 기본 예제 코드를 전부 지우고 `supabase/functions/read-gear-photo/index.ts` 내용을 붙여넣기
4. **Deploy function**
5. **Edge Functions → Secrets** 에서 `ANTHROPIC_API_KEY` 추가

대시보드 편집기는 버전 관리·롤백이 안 됩니다. 원본이 이 폴더에 있으니 문제가 생기면
다시 붙여넣으면 됩니다.

### 방법 B — 터미널에서

```bash
npm install -g supabase
supabase login
supabase link --project-ref xxxxx        # URL의 xxxxx 부분

# API 키는 서버에만 저장 (앱에는 절대 넣지 않음)
supabase secrets set ANTHROPIC_API_KEY=sk-ant-...

# 공유 페이지 주소만 호출을 허용 (선택이지만 권장)
supabase secrets set ALLOWED_ORIGIN=https://ehstudio.github.io

supabase functions deploy read-gear-photo
```

### 나중에 바꿀 수 있는 것 — 코드 수정 없이 시크릿만

| 시크릿 | 기본값 | 바꾸면 |
|---|---|---|
| `AI_MODEL` | `claude-sonnet-5` | `claude-haiku-4-5-20251001` → 비용 1/5 |
| `READER` | `claude` | `clova` → 읽기를 네이버 CLOVA 로 (아래 참고) |
| `ALLOWED_ORIGIN` | `*` | 공유 페이지 주소만 허용 |

**CLOVA 로 바꾸려면** — 한글 손글씨는 CLOVA 가 더 정확할 수 있습니다.

1. 네이버 클라우드 → CLOVA OCR 도메인 생성 → Invoke URL 과 Secret Key 발급
2. 시크릿 추가: `CLOVA_URL`, `CLOVA_SECRET`
3. 시크릿 변경: `READER=clova`, `AI_MODEL=claude-haiku-4-5-20251001`

함수 코드는 손댈 필요 없습니다. 응답의 `engine` 값으로 어느 경로를 탔는지 확인할 수 있습니다.

**현장 약어를 추가하려면** — 함수 코드의 `SHORTHAND` 상수만 고치면 됩니다.
`M4`, `70200²`, `60b + 프레넬 + A` 같은 규칙이 거기 모여 있습니다.

동작 확인:

```bash
curl -i -X POST "https://xxxxx.supabase.co/functions/v1/read-gear-photo" \
  -H "Authorization: Bearer <anon 키>" \
  -H "Content-Type: application/json" \
  -d '{"image":"x","equipment":[{"id":"CAM-001"}]}'
# → 400 "이미지가 없습니다" 가 나오면 정상 (함수가 살아있다는 뜻)
```

## 5. GitHub Pages에 올리기

```bash
mkdir eh-gear-web && cd eh-gear-web
git init
cp /경로/장비배치도.html index.html
git add . && git commit -m "장비 배치도"
git branch -M main
git remote add origin https://github.com/<계정>/eh-gear-web.git
git push -u origin main
```

GitHub 저장소 → **Settings → Pages** → Source를 `main` / `/ (root)` 로 지정 → 저장.

1~2분 뒤 `https://<계정>.github.io/eh-gear-web/` 에서 열립니다.

> **저장소를 Public으로 두면 index.html을 누구나 볼 수 있습니다.** 안에 비밀은 없지만(anon 키뿐), 장비 목록이 노출되는 게 싫으면 Private + Pages를 쓰거나 Cloudflare Pages를 쓰세요.

## 6. 앱에 연결하기

1. 올라간 페이지를 엽니다
2. 좌측 레일 → **씬** → **⚙ 서버 연결하기**
3. Project URL과 anon 키를 붙여넣고 저장

이제 두 기능이 켜집니다.

- **🔗 공유 링크 만들기** (씬 패널) → `?s=a1b2c3...` 링크 생성, 30일 후 자동 만료
- **📷 사진에서 불러오기** (목록 화면 툴바) → 화이트보드 사진 → 자산번호 매칭

---

## 운영하면서 알아둘 것

### 일시정지 (유료 플랜이면 해당 없음)

무료 플랜은 7일 쉬면 멈춰서 보낸 링크가 전부 죽습니다.
**Pro 플랜을 쓰고 있으니 이 문제는 없습니다.** `ping.yml` 은 안 써도 됩니다.

무료 조직으로 옮길 일이 생기면 그때 다시 켜세요.

### 비용

| | 포함량 | 예상 사용량 |
|---|---|---|
| Supabase DB (Pro 8GB) | 씬 1개 4KB → 사실상 무제한 |
| Storage (Pro 100GB) | 도면 200KB → 50만 장 |
| Edge Function (Pro 200만/월) | 사진 월 20장 |
| Micro compute | $10/월 (프로젝트당) |
| Claude API | 사진 1장 30~50원 (종량제) |

Pro 플랜 안에서 다 커버되고, **추가로 드는 건 compute $10/월과 사진 인식 실비**입니다.
사진을 월 20장 넣어도 1,000원 안쪽이에요.

### 링크 관리

- 만든 링크는 씬 패널 **보낸 링크**에 남습니다
- **회수** 버튼을 누르면 즉시 죽습니다 (상대가 열어둔 탭도 새로고침하면 막힘)
- 만료 7일 뒤 자동 삭제됩니다 (`purge_expired_scenes`)

### 정기 청소 (선택)

SQL Editor에서:

```sql
select cron.schedule('gear-purge', '0 4 * * *', $$select public.gear_purge_expired()$$);
```

---

## 문제가 생기면

| 증상 | 원인 | 해결 |
|---|---|---|
| 링크가 "열 수 없습니다" | 만료·회수됨, 또는 프로젝트 일시정지 | 대시보드 접속해 깨우기 |
| 공유 만들기 실패 (401) | anon 키 오타 | Settings → API에서 다시 복사 |
| 공유 만들기 실패 (403) | RLS 정책 누락 | schema.sql 다시 실행 |
| 사진 인식 500 | ANTHROPIC_API_KEY 미설정 | `supabase secrets set` 다시 |
| 사진 인식 CORS 오류 | ALLOWED_ORIGIN 불일치 | 실제 페이지 주소와 맞추기 |
| 공유 만들기 404 | 테이블 이름 불일치 | `gear_scenes` 가 만들어졌는지 확인 |
| 사진을 못 읽음 | 반사·흐림·잘림 | 정면에서 다시 촬영 |
