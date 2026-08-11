# 운영 메모

## 배포

`dist/index.html` 을 GitHub Pages 저장소에 `index.html` 로 올립니다.

- 저장소: `dev-parkjonghyun/Equipment-Hub`
- 주소: https://dev-parkjonghyun.github.io/Equipment-Hub/

## 계정

Supabase → Authentication → Users → Add user
**Auto Confirm User 를 켜야** 이메일 인증 없이 바로 로그인됩니다.

## 장비를 늘렸을 때

두 곳이 있습니다.

1. **서버** — 앱의 `＋ 장비 추가` 로 넣으면 끝 (로그인 필요)
2. **폴백 목록** — 서버가 죽었을 때 쓰는 `equipment_data.json`. 가끔 서버 기준으로 갱신하세요.

```sql
-- 서버에서 폴백용 JSON 뽑기
select json_agg(json_build_object(
  'id', id, 'nick', coalesce(nick,''), 'cat', cat, 'catLabel', coalesce(cat_label,''),
  'sub', coalesce(sub,''), 'product', coalesce(product,''), 'brand', coalesce(brand,''),
  'model', coalesce(model,''), 'status', status) order by sort_order)
from public.gear_equipment where active;
```

## 비용

| | 월 |
|---|---|
| Supabase Pro | $25 (이미 사용 중) |
| 컴퓨트 | b&a 프로젝트에 얹어서 **추가 없음** |
| GitHub Pages | 무료 |
| 사진 인식 | 미사용 (쓰면 사진 1장 30~50원) |

## 주의

- 공유 링크는 만료일이 강제됩니다. 회수는 씬 패널 → 보낸 링크 → 회수.
- `service_role` / `sb_secret_` 키는 어떤 경우에도 앱이나 저장소에 넣지 마세요.
