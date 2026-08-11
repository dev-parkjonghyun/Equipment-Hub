// ══════════════════════════════════════════════════════════
//  read-gear-photo — 화이트보드/장비목록 사진 → EH 자산번호
//
//  받는 것 : { image: "data:image/jpeg;base64,...", equipment: [{id,product,nick,cat}] }
//  주는 것 : { lines, matched, unmatched, note, engine, usage }
//
//  ── 나중에 바꿀 수 있는 것 (코드 수정 없이 시크릿만 변경) ──
//    AI_MODEL   기본 claude-sonnet-5
//               비용을 5배 줄이려면 claude-haiku-4-5-20251001
//    READER     기본 claude  (사진 읽기 + 매칭을 한 번에)
//               clova 로 바꾸면 읽기를 네이버 CLOVA 로 넘김 (아래 readWithClova 참고)
//
//  ANTHROPIC_API_KEY 는 시크릿으로만 두고 절대 앱에 넣지 않습니다.
// ══════════════════════════════════════════════════════════

const CFG = {
  model: Deno.env.get('AI_MODEL') ?? 'claude-sonnet-5',
  reader: (Deno.env.get('READER') ?? 'claude').toLowerCase(),
  maxBytes: 5 * 1024 * 1024,
};

const CORS = {
  'Access-Control-Allow-Origin': Deno.env.get('ALLOWED_ORIGIN') ?? '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};
const json = (b: unknown, s = 200) =>
  new Response(JSON.stringify(b), { status: s, headers: { ...CORS, 'Content-Type': 'application/json' } });

// ── 현장 약어 규칙 ────────────────────────────────────────
//    새 약어가 생기면 여기만 고치면 됩니다.
const SHORTHAND = `현장 약어를 이해해야 합니다.
- "M4"=a7m4, "M5"=a7m5, "M3"=a7m3 (소니 알파 바디)
- "60b"=Forza 60B, "500"=Forza 500, "300"=AD300Pro
- "24702"·"2470²"=24-70 GM2, "70200²"=70-200 GM2 (위첨자·끝의 2는 Mark II)
- "soft"=소프트박스, "프레넬"=프레넬 렌즈, "디퓨저"=디퓨저 패널
- "A"=A 스탠드, "C"=C 스탠드, "작은 A"=작은 A 스탠드
- 한 줄에 "+"로 이어진 것은 하나의 조립 세트입니다 ("60b + 프레넬 + A")
- 수량 표기(×2, x2, *2)는 같은 제품을 그 개수만큼 배정합니다
- 가로줄(───)로 나뉜 구역은 카메라·조명·오디오 같은 분류 단위입니다`;

const SYSTEM = `당신은 한국 영상 프로덕션 스튜디오의 장비 담당자입니다.
촬영 준비용 화이트보드나 손으로 쓴 장비 목록을 읽고, 스튜디오 자산번호와 대조합니다.

${SHORTHAND}

확실하지 않으면 억지로 매칭하지 말고 unmatched 로 남기세요.
틀린 매칭이 빈칸보다 나쁩니다. confidence 는 정직하게 매기세요.

출력은 JSON 하나만. 설명·마크다운·코드펜스 금지.
{
  "lines": [{"text":"읽은 원문 그대로","group":"카메라|조명|오디오|기타"}],
  "matched": [{"line":"원문","eqId":"CAM-003","why":"M4=a7m4","confidence":0.0~1.0}],
  "unmatched": [{"line":"원문","reason":"보유 목록에 없음"}],
  "note": "전체적으로 눈에 띄는 점 한 줄"
}`;

async function callClaude(body: unknown) {
  const key = Deno.env.get('ANTHROPIC_API_KEY');
  if (!key) throw new Error('ANTHROPIC_API_KEY 가 설정되지 않았습니다');
  const r = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'x-api-key': key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`분석 실패 (${r.status}) ${(await r.text()).slice(0, 300)}`);
  return r.json();
}

function parseJsonOut(out: any) {
  const text = (out?.content ?? []).filter((c: any) => c.type === 'text')
    .map((c: any) => c.text).join('\n').trim();
  const clean = text.replace(/^```(?:json)?\s*/i, '').replace(/```\s*$/, '').trim();
  return JSON.parse(clean);
}

// ══════════════════════════════════════════════════════════
//  ① 읽기 단계 — 여기만 갈아끼우면 다른 OCR 로 바꿀 수 있습니다
// ══════════════════════════════════════════════════════════

// (기본) Claude 비전 — 읽기와 매칭을 한 번에. 문맥 추론이 강합니다.
async function readAndMatchWithClaude(mediaType: string, b64: string, list: string) {
  const out = await callClaude({
    model: CFG.model,
    max_tokens: 4096,
    system: SYSTEM,
    messages: [{
      role: 'user',
      content: [
        { type: 'image', source: { type: 'base64', media_type: mediaType, data: b64 } },
        { type: 'text', text: `우리 스튜디오 보유 장비입니다 (자산번호 · 제품명 · 별칭):\n${list}\n\n`
            + `첨부한 사진을 읽고, 적혀 있는 장비를 위 자산번호와 대조해 주세요.\n`
            + `같은 제품이 여러 대면 아직 배정되지 않은 번호를 차례로 쓰세요.` },
      ],
    }],
  });
  return { parsed: parseJsonOut(out), usage: out?.usage ?? null, engine: `claude:${CFG.model}` };
}

// (대안) 네이버 CLOVA 로 글자만 읽고, 매칭은 저렴한 텍스트 모델에 맡기는 구조.
//
//  쓰려면:
//   1. 네이버 클라우드 → CLOVA OCR 도메인 생성 → APIGW Invoke URL 과 Secret Key 발급
//   2. 시크릿 추가:  CLOVA_URL, CLOVA_SECRET
//   3. 시크릿 변경:  READER=clova,  AI_MODEL=claude-haiku-4-5-20251001
//
//  한글 손글씨는 CLOVA 가 더 정확할 수 있습니다. 실제 사진으로 비교해보고 정하세요.
async function readWithClova(mediaType: string, b64: string): Promise<string[]> {
  const url = Deno.env.get('CLOVA_URL');
  const secret = Deno.env.get('CLOVA_SECRET');
  if (!url || !secret) throw new Error('CLOVA_URL / CLOVA_SECRET 이 설정되지 않았습니다');
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'X-OCR-SECRET': secret, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      version: 'V2',
      requestId: crypto.randomUUID(),
      timestamp: Date.now(),
      lang: 'ko',
      images: [{ format: mediaType.split('/')[1], name: 'gear', data: b64 }],
    }),
  });
  if (!r.ok) throw new Error(`CLOVA 오류 (${r.status}) ${(await r.text()).slice(0, 300)}`);
  const out = await r.json();
  const fields = out?.images?.[0]?.fields ?? [];
  // lineBreak 플래그로 줄을 복원
  const lines: string[] = [];
  let cur = '';
  for (const f of fields) {
    cur += (cur ? ' ' : '') + (f.inferText ?? '');
    if (f.lineBreak) { lines.push(cur.trim()); cur = ''; }
  }
  if (cur.trim()) lines.push(cur.trim());
  return lines.filter(Boolean);
}

// 읽어낸 글자만 가지고 매칭 (사진 없이 텍스트 모델 — 훨씬 쌉니다)
async function matchFromLines(lines: string[], list: string) {
  const out = await callClaude({
    model: CFG.model,
    max_tokens: 4096,
    system: SYSTEM,
    messages: [{
      role: 'user',
      content: `우리 스튜디오 보유 장비입니다 (자산번호 · 제품명 · 별칭):\n${list}\n\n`
        + `아래는 화이트보드에서 읽어낸 글자입니다. 오독이 있을 수 있으니 감안해서 대조해 주세요.\n\n`
        + lines.map(l => '- ' + l).join('\n'),
    }],
  });
  return { parsed: parseJsonOut(out), usage: out?.usage ?? null, engine: `clova+${CFG.model}` };
}

// ══════════════════════════════════════════════════════════
//  ② 요청 처리
// ══════════════════════════════════════════════════════════
Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS });
  if (req.method !== 'POST') return json({ error: 'POST 만 허용됩니다' }, 405);

  let body: any;
  try { body = await req.json(); }
  catch { return json({ error: '잘못된 요청 형식입니다' }, 400); }

  const { image, equipment } = body ?? {};
  if (typeof image !== 'string' || !image.startsWith('data:image/'))
    return json({ error: '이미지가 없습니다' }, 400);
  if (!Array.isArray(equipment) || !equipment.length)
    return json({ error: '장비 목록이 없습니다' }, 400);

  const m = image.match(/^data:(image\/(?:jpeg|png|webp));base64,(.+)$/);
  if (!m) return json({ error: 'JPEG · PNG · WebP 만 지원합니다' }, 400);
  const [, mediaType, b64] = m;
  if (b64.length * 0.75 > CFG.maxBytes)
    return json({ error: '사진이 너무 큽니다 (5MB 이하로 줄여주세요)' }, 413);

  // 보유 장비를 짧게 정리 (토큰 절약)
  const list = equipment
    .map((e: any) => `${e.id}\t${e.product ?? ''}${e.nick ? ` (${e.nick})` : ''}`)
    .join('\n');

  let res;
  try {
    res = CFG.reader === 'clova'
      ? await matchFromLines(await readWithClova(mediaType, b64), list)
      : await readAndMatchWithClaude(mediaType, b64, list);
  } catch (e) {
    return json({ error: String((e as Error).message ?? e) }, 502);
  }

  const parsed = res.parsed ?? {};
  // 존재하지 않는 자산번호는 걸러낸다 (모델이 지어낼 수 있음)
  const valid = new Set(equipment.map((e: any) => e.id));
  const all = parsed.matched ?? [];
  const matched = all.filter((x: any) => valid.has(x.eqId));
  const dropped = all.filter((x: any) => !valid.has(x.eqId));

  return json({
    lines: parsed.lines ?? [],
    matched,
    unmatched: [
      ...(parsed.unmatched ?? []),
      ...dropped.map((d: any) => ({ line: d.line, reason: `없는 자산번호 ${d.eqId}` })),
    ],
    note: parsed.note ?? '',
    engine: res.engine,
    usage: res.usage,
  });
});
