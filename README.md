# EH Studio 장비 배치도

촬영 장비를 관리하고, 촬영장 배치를 설계·공유하는 단일 HTML 앱.

```bash
./build.sh      # 빌드 + 문법 검사 + 테스트
```

결과물은 `dist/index.html` 하나입니다. 더블클릭하면 열립니다.

## 화면

- **목록** — 장비 112개. 검색·필터·표에서 바로 수정
- **배치도** — 블록으로 장비 구성과 조립 설계
- **평면도** — 미터 단위 실측 배치, 방 그리기, 도면 위 배치
- **3D** — 카메라 화각·심도 확인, 1인칭으로 공간 걷기

## 문서

- [CLAUDE.md](CLAUDE.md) — 개발할 때 먼저 읽으세요
- [docs/SETUP.md](docs/SETUP.md) — 서버 설치 (사용자용)

## 서버

Supabase 에 장비 마스터와 공유 씬을 둡니다. 서버 없이도 앱은 동작합니다.

```
supabase/03-equipment.sql       장비 테이블
supabase/04-equipment-data.sql  엑셀 데이터 112개
supabase/schema.sql             공유 링크 테이블
```
