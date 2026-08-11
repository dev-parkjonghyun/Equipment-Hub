# EH Studio 장비 배치도

영상 프로덕션 스튜디오(EH Studio)의 촬영 장비를 관리하고, 촬영장 배치를 설계·공유하는 도구.

---

## 가장 먼저 알아야 할 것

**`dist/index.html` 을 직접 고치지 마세요.** 그 파일은 빌드 결과물입니다.
모든 앱 코드(HTML·CSS·JS)는 `generate_html.py` 안의 문자열 템플릿에 들어 있습니다.

```bash
./build.sh          # 빌드 → JS 문법 검사 → 전체 테스트 (이것만 쓰면 됩니다)
python3 generate_html.py   # 빌드만
./run-tests.sh             # 테스트만
```

**사용자에게 결과물을 주기 전에 반드시 `./build.sh` 가 통과해야 합니다.**
과거에 문법이 깨진 파일을 그대로 전달해 앱이 완전히 죽은 적이 있습니다.

---

## 구조

```
generate_html.py      앱 전체 소스 (약 7,600줄). 여기만 고칩니다.
equipment_data.json   장비 목록 폴백 (서버 연결 전 / 오프라인용)
vendor/three.min.js   Three.js r149 — 빌드 시 통째로 인라인됩니다
dist/index.html       빌드 결과 (약 970KB, GitHub Pages 에 올리는 파일)
tests/                Node vm 위에서 도는 테스트 22개, 1,060항목
supabase/             테이블·RLS SQL, Edge Function
docs/SETUP.md         서버 설치 안내 (사용자용)
data/                 원본 엑셀
```

앱은 **단일 HTML 파일**입니다. 빌드 도구도, 번들러도, 런타임 의존성도 없습니다.
더블클릭하면 열리고, 인터넷이 끊겨도 동작합니다. 이 성질을 깨지 마세요.

---

## 테스트

`tests/harness.js` 가 Node `vm` 안에 DOM 을 흉내 내고 `dist/index.html` 의 스크립트를 실행합니다.
브라우저 없이 실제 앱 코드를 돌려서 검증합니다.

```js
const H = makeHarness('함수1,함수2,별칭:내부이름,get x(){return 내부변수}');
H.api.함수1();          // 앱 함수 호출
H.store['id']           // DOM 요소
H.alerts                // alert() 기록
H.fire('keydown', {key:'ArrowUp', code:'ArrowUp'});
```

**테스트가 실패하면 먼저 앱 코드가 맞는지 확인하세요.** 의도한 동작 변경이면 테스트를 고치고,
아니면 앱을 고칩니다. 테스트를 무작정 맞추지 마세요.

### 3D·SVG 는 눈으로 확인합니다

코드 검사만으로는 형태가 틀린 걸 못 잡습니다. 이렇게 확인해 왔습니다.

- 메시를 SVG 로 투영해 PNG 로 굽고 실제로 봅니다 (`cairosvg`)
- 이 방법으로 **소프트박스가 뒤를 향하던 버그**, **평면도 글자가 겹치던 원인**을 찾았습니다
- 디버그 렌더러에 면 법선 기반 음영을 넣어두면 어두운 장비도 형태가 보입니다

### SQL 은 파서로 검증합니다

```bash
pip install pglast --break-system-packages
python3 -c "from pglast import parse_sql; parse_sql(open('supabase/03-equipment.sql').read())"
```

문자열 치환을 겹쳐 적용해 `gear_gear_scene_views_id_seq` 같은 이름이 생긴 적이 있습니다.
**정의된 이름과 참조된 이름을 대조하는 검사**를 꼭 돌리세요.

---

## 데이터 모델

### 장비

```js
{ id:'CAM-003', nick:'', cat:'CAM', catLabel:'카메라 본체(CAM)',
  sub:'미러리스', product:'Sony a7m4', brand:'Sony', model:'',
  status:'정상', loc:'', note:'' }
```

자산번호는 `[카테고리 3자]-[일련번호]`. 스탠드·배터리는 2단계:
`STD-C-001`(C스탠드), `STD-A-001`(A스탠드), `STD-AS-001`(작은 A스탠드), `BAT-FZ-001`.

카테고리 15종: `CAM LEN LIT MOD AUD MON TRP STD GIM BAT PWR STO CAB ACC ETC`

### 표시 이름 규칙 (중요)

**별칭은 이름이 어려울 때만 씁니다.** 사용자가 명시한 원칙입니다.

```js
dispName(eq)   // 별칭 있으면 별칭, 없으면 브랜드 뗀 제품명
               // "Sony a7m4" → "a7m4",  "NANLITE Forza 500" → "포르자 500"
hardName(eq)   // 부품번호처럼 생겨 별칭이 필요한가 (112개 중 7개만 해당)
```

목록·배치도·평면도·3D 가 **모두 `dispName()` 을 씁니다.** 새 화면을 만들면 여기에 맞추세요.

### 치수

`SPECS[assetId]` = `{w, d, h, hMin, hMax, src}` (미터).
`src` 는 `'spec'`(제조사 공식) · `'avg'`(평균) · `'est'`(추정).

**평면도 발자국과 3D 치수는 같은 값을 써야 합니다.** 예전에 따로 관리하다 어긋났습니다.
지지대(TRP·STD)는 `footprintOf()` 가 `SPECS` 를 참조하도록 되어 있습니다.

### 조립 (모듈)

배치도에서 블록을 다른 블록 위로 끌면 결합됩니다. 루트는 **카메라·조명만**.

```js
SLOTS.CAM = [lens, support, card, batt, shoe, rig]
SLOTS.LIT = [support, mod, power, ctrl]
slotsFor(eq)  // STD-C 는 arm(그립헤드·암 세트) + hang(암에 매달기) 추가
```

C 스탠드는 **기본이 기둥+베이스뿐**이고, 그립암은 ACC 를 결합했을 때만 그려집니다.

### 씬

```js
scene = { name, mode, blocks:{}, groups:{}, floor:{ zoom, items:{}, rooms:[], subjects:[], ceilH, confine } }
```

배치도(`blocks`)와 평면도·3D(`floor.items`)는 **다른 저장소**이고 `syncFromLayout()` 이 잇습니다.
배치도가 "무엇이 있고 어떻게 조립됐는가", 평면도가 "어디에 놓였는가"입니다.

---

## 화면

| 모드 | 하는 일 |
|---|---|
| **목록** | 앱의 첫 화면. 장비 112개, 검색·필터·인라인 수정 |
| 배치도 | 추상 블록 배치, 그룹, 조립 |
| 평면도 | 미터 단위 실측, 방 그리기(사각형·펜툴), 배경 도면 |
| 3D | Three.js. 카메라 화각·심도 시뮬레이션, 1인칭 걷기 |

좌측 레일 상단에 목록, 그 아래 씬·세트·조립 도구, 그 아래 카테고리.

---

## 서버 (Supabase)

**b&a 프로젝트에 테이블만 얹었습니다.** 모든 이름이 `gear_` 로 시작합니다.
(별도 프로젝트를 만들면 컴퓨트 크레딧이 조직당 1개뿐이라 월 $10 이 더 붙습니다)

| 테이블 | 용도 | 익명 | 로그인 |
|---|---|---|---|
| `gear_equipment` | 장비 마스터 112개 | 읽기 | 전체 |
| `gear_specs` | 3D·평면도 치수 | 읽기 | 전체 |
| `gear_scenes` | 공유된 배치 | 살아있는 것만 읽기 | 전체 |
| `gear_scene_views` | 조회 기록 | 기록만 | 읽기 |

### 절대 지킬 것

- **`sb_secret_` / `service_role` 키는 앱에 넣지 않습니다.** 앱에는 `sb_publishable_` 만.
- `ANTHROPIC_API_KEY` 는 Edge Function 시크릿에만.
- 공유 링크는 만료일이 SQL 수준에서 **강제**됩니다 (최대 180일).
- 익명에게는 쓰기 권한을 GRANT 하지 않습니다 (RLS 와 이중 잠금).

### 키 형식

Supabase 가 최근 키를 바꿨습니다. 새 키(`sb_publishable_…`)는 JWT 가 아니라서
`Authorization` 헤더에 넣으면 거부됩니다. `sbHeaders()` 가 형식을 보고 처리합니다.

```js
apikey: <publishable key>              // 항상
Authorization: Bearer <사용자 토큰>     // 로그인했을 때
Authorization: Bearer <anon 키>        // 옛 eyJ… 형식일 때만
```

---

## 지금 상태

### 되는 것

- 장비 목록 112개가 **서버에서** 로드됨. 로그인하면 별칭·보관위치·상태 수정이 서버에 저장
- 장비 추가(자산번호 자동 채번) / 목록에서 내리기(`active=false`, 기록은 보존)
- 배치도 → 평면도 → 3D 자동 동기화
- 공유 링크 생성·회수, 읽기 전용 모드
- 서버가 안 되면 `equipment_data.json` 으로 폴백

### 남은 것

1. **사용자가 아직 안 한 것** — Supabase Authentication 에 계정 생성, `dist/index.html` 을
   GitHub Pages(`dev-parkjonghyun/Equipment-Hub`)에 업로드, 앱에서 로그인 테스트
2. **사진 인식** — Edge Function 코드는 있으나 배포 안 함. Anthropic 크레딧이 유료라 보류.
   `READER=clova` 로 네이버 CLOVA(월 무료 한도 있음) 전환 경로를 코드에 열어뒀습니다.
3. 3D 2단 조립 — `parts[].parent` 를 저장은 하지만 3D 렌더가 `slot` 만 봅니다.
   짐벌→카메라→렌즈처럼 3단으로 엮으면 위치가 틀립니다.
4. TRP-003 (Teris TSN6CF-Q) 높이 스펙 미검증

---

## 이 프로젝트에서 배운 것

**사용자는 개발자가 아닙니다.** 영상 프로덕션을 운영합니다.
명령어를 던지지 말고, 무엇을 왜 하는지 먼저 설명하세요. 화면 캡처를 받으면 그걸 기준으로 짚어주세요.

**현장 용어를 씁니다.** 화이트보드에 이렇게 적습니다.

```
M4                        → a7m4 (CAM-003)
M5 + 70200² + 24702²      → a7m5 + 70-200 GM2 + 24-70 GM2   (위첨자 2 = Mark II)
60b + 프레넬 + A           → Forza 60B + 프레넬 + A스탠드      (+ 로 이어지면 한 세트)
500 + soft + A            → Forza 500 + 소프트박스 + A스탠드
```

이 규칙은 `supabase/functions/read-gear-photo/index.ts` 의 `SHORTHAND` 상수에 모아뒀습니다.

**추측하지 말고 재세요.** 장비 치수는 제조사 사양을 검색해 확인했습니다.
삼각대 최대 높이를 173cm 대신 157cm 로 넣어뒀다가 사용자가 발견한 적이 있습니다.

**UI 문구는 한국어이고, 사용자를 탓하지 않습니다.** "오류" 대신 무엇을 하면 되는지 씁니다.
