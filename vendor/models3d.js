// ============================================================================
//  models3d.js — 사용자 제작 고품질 3D 모델 (Downloads/3d 통합)
//  generate_html.py 가 /*__MODELS3D__*/ 자리에 인라인합니다.
//  이 코드는 M / mat / SPECS / THREE 가 정의된 뒤 실행됩니다.
//  폴더의 자산번호는 실제 DB와 달라서, SPECS 는 실제 자산 id 로 새로 등록합니다.
// ============================================================================

// ── 부족한 헬퍼 보강 ─────────────────────────────────────────────────────────
M.silver = () => mat(0xd2d7de, { metalness: 0.9, roughness: 0.22 });   // 밝은 리플렉터 내피
// 발광면 표시(현재 렌더는 emissive 재질로 이미 빛나므로 태그만 남긴다)
function markEmitter(mesh, opts) { if (mesh) mesh.userData.emitter = opts || {}; return mesh; }
// 봉 헬퍼 별칭 — 삼각대는 rod(), 스탠드는 _rod() (동일 시그니처)
function rod(a, b, r, seg) { return _rod(a, b, r, seg); }
// 여러 지오메트리 조각을 하나로 합친다. 조각 = {geo, pos?[x,y,z], rot?[x,y,z], quat?}
function geoBatch(parts) {
    const posArr = [], nrmArr = [];
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(),
          e = new THREE.Euler(), v = new THREE.Vector3(1, 1, 1), p = new THREE.Vector3();
    for (const part of parts) {
        let g = part.geo.index ? part.geo.toNonIndexed() : part.geo.clone();
        if (part.quat) q.copy(part.quat);
        else if (part.rot) q.setFromEuler(e.set(part.rot[0] || 0, part.rot[1] || 0, part.rot[2] || 0));
        else q.identity();
        p.set(part.pos ? (part.pos[0] || 0) : 0, part.pos ? (part.pos[1] || 0) : 0, part.pos ? (part.pos[2] || 0) : 0);
        m4.compose(p, q, v);
        g.applyMatrix4(m4);
        const pa = g.attributes.position.array; for (let i = 0; i < pa.length; i++) posArr.push(pa[i]);
        if (g.attributes.normal) { const na = g.attributes.normal.array; for (let i = 0; i < na.length; i++) nrmArr.push(na[i]); }
        if (g !== part.geo) g.dispose && g.dispose();
    }
    const out = new THREE.BufferGeometry();
    out.setAttribute('position', new THREE.Float32BufferAttribute(posArr, 3));
    if (nrmArr.length === posArr.length) out.setAttribute('normal', new THREE.Float32BufferAttribute(nrmArr, 3));
    else out.computeVertexNormals();
    return out;
}

// ── 빌더 함수 (사용자 제작, 원본 그대로) ──
// ── fs60bHead  (출처: LIT-002_FS-60B/LIT-002_threejs.js) ──
function fs60bHead(sp) {
    const g = new THREE.Group();
    const H = sp.h, BW = sp.bodyW, zF = sp.zFront, zB = sp.zBack;
    const shell = M.black(), alu = M.aluDk(), knobM = M.knob(), rub = M.rubber();

    const add = (geo, mat, x = 0, y = 0, z = 0) => {
        const m = new THREE.Mesh(geo, mat);
        m.position.set(x, y, z);
        g.add(m);
        return m;
    };

    const plateT = 0.012;
    const zBody = zB + 0.030;                 // 리브 본체 후면 (상판이 뒤로 더 나옴)
    const bodyL = (zF - plateT) - zBody;

    // 상판 — 윗면 전체를 덮고 뒤로 30mm 돌출
    const hoodL = (zF - plateT) - zB;
    add(new THREE.BoxGeometry(BW + 0.005, 0.008, hoodL), shell, 0, H / 2 + 0.001, zB + hoodL / 2);

    // 리브 본체 + 방열 홈 3줄
    add(new THREE.BoxGeometry(BW, H, bodyL), shell, 0, 0, zBody + bodyL / 2);
    for (let i = -1; i <= 1; i++) {
        add(new THREE.BoxGeometry(BW + 0.0016, 0.005, bodyL * 0.88), alu,
            0, i * 0.019, zBody + bodyL / 2);
    }

    // 측면 옐로 액센트
    add(new THREE.BoxGeometry(BW + 0.0018, 0.026, 0.007),
        mat(0xe8b400, { roughness: 0.5, metalness: 0.1 }), 0, 0, zF - plateT - 0.012);

    // 전면 마운트 판 — 모서리 깎인 사각판 + 원형 개구
    const ringR = 0.039;
    const pw = (BW + 0.006) / 2, ph = (H + 0.006) / 2, ch = 0.010;
    const shape = new THREE.Shape();
    shape.moveTo(-pw + ch, -ph);
    shape.lineTo(pw - ch, -ph); shape.lineTo(pw, -ph + ch);
    shape.lineTo(pw, ph - ch); shape.lineTo(pw - ch, ph);
    shape.lineTo(-pw + ch, ph); shape.lineTo(-pw, ph - ch);
    shape.lineTo(-pw, -ph + ch); shape.closePath();
    const hole = new THREE.Path();
    hole.absarc(0, 0, ringR, 0, Math.PI * 2, true);
    shape.holes.push(hole);
    add(new THREE.ExtrudeGeometry(shape, { depth: plateT, bevelEnabled: false, curveSegments: 16 }),
        shell, 0, 0, zF - plateT);

    // FM 마운트 캐비티 + COB
    add(new THREE.CylinderGeometry(ringR, ringR, 0.0115, 16, 1, true), alu, 0, 0, zF - 0.0058)
        .rotation.x = Math.PI / 2;
    add(new THREE.CircleGeometry(ringR, 16), shell, 0, 0, zF - plateT + 0.0005);
    add(new THREE.CircleGeometry(0.020, 16), M.diff(), 0, 0, zF - plateT + 0.0010);
    const cob = add(new THREE.CircleGeometry(0.0145, 16),
        mat(0xf2dd7a, { roughness: 0.85, metalness: 0, emissive: 0xffe9a8, emissiveIntensity: 1.0 }),
        0, 0, zF - plateT + 0.0015);
    markEmitter(cob, { coneDeg: sp.beam, softness: 0, shape: 'disc', size: 0.029 });

    // 후면 컨트롤 패널
    const zP = zBody - 0.004;
    add(new THREE.BoxGeometry(BW - 0.008, H - 0.008, 0.008), alu, 0, 0, zP + 0.004);
    add(new THREE.BoxGeometry(0.032, 0.019, 0.003), rub, 0, 0.016, zP);                  // LCD
    add(new THREE.CylinderGeometry(0.0075, 0.0075, 0.005, 12),
        mat(0x3fa9dc, { roughness: 0.5, metalness: 0.1 }), -0.022, -0.009, zP - 0.001)
        .rotation.x = Math.PI / 2;                                                       // 파란 다이얼
    add(new THREE.BoxGeometry(0.011, 0.005, 0.003), knobM, -0.002, -0.011, zP);          // MODE
    add(new THREE.CylinderGeometry(0.008, 0.008, 0.005, 12), knobM, 0.017, -0.009, zP - 0.001)
        .rotation.x = Math.PI / 2;
    add(new THREE.BoxGeometry(0.021, 0.011, 0.004), rub, -0.013, -0.031, zP);            // AC 인렛
    add(new THREE.BoxGeometry(0.013, 0.009, 0.004), knobM, 0.019, -0.031, zP);           // 전원 스위치

    // 요크 (U자 스트랩) — 전폭 134mm는 틸트 노브 끝 기준
    const ax = 0.0545;
    const path = new THREE.CatmullRomCurve3([
        new THREE.Vector3(ax, 0.014, 0), new THREE.Vector3(ax, -0.055, 0),
        new THREE.Vector3(ax * 0.88, -0.095, 0), new THREE.Vector3(ax * 0.42, -0.112, 0),
        new THREE.Vector3(0, -0.115, 0),
        new THREE.Vector3(-ax * 0.42, -0.112, 0), new THREE.Vector3(-ax * 0.88, -0.095, 0),
        new THREE.Vector3(-ax, -0.055, 0), new THREE.Vector3(-ax, 0.014, 0),
    ], false, 'catmullrom', 0.2);
    add(new THREE.TubeGeometry(path, 22, 0.0075, 5, false), alu);
    for (const s of [-1, 1]) {
        add(new THREE.CylinderGeometry(0.0105, 0.0105, 0.009, 12), knobM, s * 0.0625, 0, 0)
            .rotation.z = Math.PI / 2;
    }

    // 스탠드 스피곳 (5/8")
    const sTop = -0.114, sBot = -sp.yokeDrop;
    add(new THREE.CylinderGeometry(0.0145, 0.0145, sTop - sBot, 12), alu, 0, (sTop + sBot) / 2, 0);
    add(new THREE.CylinderGeometry(0.0125, 0.0125, 0.020, 12), knobM, -0.025, -0.140, 0)
        .rotation.z = Math.PI / 2;

    return g;
}

// ── fs60bReflector  (출처: LIT-002_FS-60B/LIT-002_threejs.js) ──
function fs60bReflector(sp) {
    const g = new THREE.Group();
    const rN = sp.neckD / 2, rA = sp.apertureD / 2, L = sp.depth;

    const prof = [
        new THREE.Vector2(rN * 0.83, 0),
        new THREE.Vector2(rN, 0.006),
        new THREE.Vector2(rN, 0.024),
        new THREE.Vector2(rN + (rA - rN) * 0.30, L * 0.32),
        new THREE.Vector2(rN + (rA - rN) * 0.66, L * 0.68),
        new THREE.Vector2(rA * 0.975, L * 0.94),
        new THREE.Vector2(rA, L),
    ];

    const outer = new THREE.Mesh(new THREE.LatheGeometry(prof, 16), M.black());
    outer.rotation.x = Math.PI / 2;              // Lathe 축 Y → +Z (부호 주의)
    g.add(outer);

    const innerMat = M.silver().clone();
    innerMat.side = THREE.BackSide;
    const inner = new THREE.Mesh(
        new THREE.LatheGeometry(prof.map(p => new THREE.Vector2(p.x - 0.0018, p.y)), 16), innerMat);
    inner.rotation.x = Math.PI / 2;
    g.add(inner);

    for (let i = 0; i < 3; i++) {                // 외피 홈 3줄
        const t = 0.30 + i * 0.20;
        const r = rN + (rA - rN) * (t * 0.9);
        const ring = new THREE.Mesh(
            new THREE.CylinderGeometry(r + 0.0012, r + 0.0012, 0.004, 16, 1, true), M.aluDk());
        ring.rotation.x = Math.PI / 2;
        ring.position.z = L * t;
        g.add(ring);
    }

    const rim = new THREE.Mesh(
        new THREE.CylinderGeometry(rA + 0.0015, rA + 0.0015, 0.006, 16, 1, true), M.aluDk());
    rim.rotation.x = Math.PI / 2;
    rim.position.z = L - 0.003;
    g.add(rim);

    const face = new THREE.Mesh(new THREE.CircleGeometry(rA - 0.002, 16), M.diff());
    face.position.z = L - 0.001;
    markEmitter(face, { coneDeg: sp.beam, softness: 0, shape: 'disc', size: sp.apertureD });
    g.add(face);

    return g;
}

// ── ad300ProIIHead  (출처: LIT-003_AD300ProII/LIT-003_threejs.js) ──
function ad300ProIIHead(sp) {
    const g = new THREE.Group();
    const AY = sp.axisY, zF = sp.zFront, zB = sp.zBack;
    const R = sp.h / 2;
    const shell = M.black(), alu = M.aluDk(), knobM = M.knob(), rub = M.rubber();

    const add = (geo, mat, x = 0, y = 0, z = 0) => {
        const m = new THREE.Mesh(geo, mat);
        m.position.set(x, y, z);
        g.add(m);
        return m;
    };

    // 후면 하우징 (컨트롤 패널 쪽이 살짝 넓습니다)
    const rearL = 0.098;
    add(new THREE.BoxGeometry(sp.w, sp.h, rearL), shell, 0, AY, zB + rearL / 2);

    // 전면 배럴 — 앞쪽 16mm 는 마운트 캐비티로 비워둡니다
    const zCav = zF - 0.016;
    const barL = zCav - (zB + rearL);
    add(new THREE.CylinderGeometry(R, R, barL, 16), shell, 0, AY, zB + rearL + barL / 2)
        .rotation.x = Math.PI / 2;

    // 그레이 액센트 밴드
    add(new THREE.CylinderGeometry(R + 0.0015, R + 0.0015, 0.013, 16), alu, 0, AY, zF - 0.058)
        .rotation.x = Math.PI / 2;

    // 측면 방열 슬롯 (홈 3줄)
    for (let i = -1; i <= 1; i++) {
        add(new THREE.BoxGeometry(sp.w + 0.0016, 0.005, 0.030), rub, 0, AY + i * 0.011, zB + 0.030);
    }

    // Godox 마운트 링 + 발광부
    add(new THREE.CylinderGeometry(R, R, 0.016, 16, 1, true), alu, 0, AY, zF - 0.008)
        .rotation.x = Math.PI / 2;
    add(new THREE.CircleGeometry(R - 0.003, 16), shell, 0, AY, zCav + 0.0005);

    const tube = add(new THREE.CircleGeometry(0.024, 16), M.diff(), 0, AY, zCav + 0.001);
    markEmitter(tube, { coneDeg: sp.beam, softness: 0, shape: 'disc', size: 0.048 });
    add(new THREE.CircleGeometry(R - 0.006, 16), M.glass(), 0, AY, zF - 0.004);   // 보호 유리
    add(new THREE.CircleGeometry(0.009, 12),
        mat(0xf5e6c0, { roughness: 0.8, metalness: 0, emissive: 0xffeec4, emissiveIntensity: 0.8 }),
        0, AY, zCav + 0.0015);                                                    // 모델링 LED

    // 후면 컨트롤 패널
    const zP = zB + 0.003;
    add(new THREE.BoxGeometry(sp.w - 0.008, sp.h - 0.008, 0.006), alu, 0, AY, zP);
    add(new THREE.BoxGeometry(0.040, 0.026, 0.003), rub, -0.018, AY + 0.008, zP - 0.003);
    add(new THREE.BoxGeometry(0.028, 0.012, 0.003), rub, -0.016, AY - 0.024, zP - 0.003);
    for (const [bx, by] of [[0.028, 0.014], [0.028, -0.002], [0.028, -0.018]]) {
        add(new THREE.CylinderGeometry(0.004, 0.004, 0.004, 8), knobM, bx, AY + by, zP - 0.003)
            .rotation.x = Math.PI / 2;
    }
    add(new THREE.BoxGeometry(0.006, 0.004, 0.026),
        mat(0xc8352e, { roughness: 0.5, metalness: 0.1 }), 0.030, AY + sp.h / 2, zB + 0.026);

    // 틸트 브래킷 (플레이트 + 노브 + 스피곳)
    add(new THREE.BoxGeometry(0.030, AY + 0.010, 0.040), alu, 0, (AY - 0.010) / 2, 0);
    for (const s of [-1, 1]) {
        add(new THREE.CylinderGeometry(0.012, 0.012, 0.010, 12), knobM, s * 0.019, 0, 0)
            .rotation.z = Math.PI / 2;
    }
    add(new THREE.CylinderGeometry(0.0145, 0.0145, sp.yokeDrop - 0.010, 12), alu,
        0, -(0.010 + sp.yokeDrop) / 2, 0);

    return g;
}

// ── pjFmmBody  (출처: MOD-001_PJ-FMM-36/MOD-001_threejs.js) ──
function pjFmmBody(sp) {
    const g = new THREE.Group();
    const D = sp.d, alu = M.aluDk(), shell = M.black(), knobM = M.knob();

    const add = (geo, mat, x = 0, y = 0, z = 0) => {
        const m = new THREE.Mesh(geo, mat);
        m.position.set(x, y, z);
        g.add(m);
        return m;
    };

    // 배럴 = 회전체 1덩어리 (마운트 칼라 → 콘덴서 → 고보 구간 → 포커스 → 렌즈 클램프 링)
    const prof = [
        [0.036, 0.000], [0.044, 0.000], [0.044, 0.015],
        [0.050, 0.018], [0.050, 0.072],
        [0.047, 0.076], [0.047, 0.126],
        [0.048, 0.130], [0.048, 0.168],
        [0.066, 0.174], [0.066, D],
        [0.052, D],
    ].map(([r, z]) => new THREE.Vector2(r, z));
    const barrel = new THREE.Mesh(new THREE.LatheGeometry(prof, 16), shell);
    barrel.rotation.x = Math.PI / 2;          // Lathe 축 Y → +Z (부호 주의)
    g.add(barrel);

    add(new THREE.CircleGeometry(0.036, 16), alu, 0, 0, 0.004);        // 콘덴서 막음면

    // 고보 하우징 + 슬롯 보스 + 손나사
    add(new THREE.BoxGeometry(0.098, 0.098, 0.052), shell, 0, 0, 0.101);
    add(new THREE.BoxGeometry(0.052, 0.020, 0.030), alu, 0, 0.058, 0.101);
    add(new THREE.CylinderGeometry(0.010, 0.010, 0.013, 12), knobM, 0, 0.0745, 0.101);

    // 젤홀더 탭 — 전폭 160mm를 만드는 부분
    for (const s of [-1, 1]) {
        add(new THREE.BoxGeometry(0.032, 0.030, 0.010), alu, s * 0.064, 0, D - 0.008);
    }

    // 지지 다리 + 스탠드 스피곳
    const legTop = -0.046, legBot = -0.128;
    add(new THREE.BoxGeometry(0.030, legTop - legBot, 0.036), alu,
        0, (legTop + legBot) / 2, 0.096);
    add(new THREE.CylinderGeometry(0.0145, 0.0145, legBot - sp.yBot, 12), alu,
        0, (legBot + sp.yBot) / 2, 0.096);
    add(new THREE.CylinderGeometry(0.0125, 0.0125, 0.020, 12), knobM, -0.025, -0.140, 0.096)
        .rotation.z = Math.PI / 2;

    return g;
}

// ── pjFmmLens  (출처: MOD-001_PJ-FMM-36/MOD-001_threejs.js) ──
function pjFmmLens(sp) {
    const g = new THREE.Group();
    const R = sp.barrelD / 2, L = sp.len;
    const shell = M.black(), alu = M.aluDk(), knobM = M.knob();

    const prof = [
        [0.050, 0.000], [0.064, 0.000], [0.064, 0.022],
        [R * 0.93, 0.028], [R * 0.93, 0.112],
        [R, 0.118], [R, L],
        [R - 0.006, L],
    ].map(([r, z]) => new THREE.Vector2(r, z));
    const barrel = new THREE.Mesh(new THREE.LatheGeometry(prof, 16), shell);
    barrel.rotation.x = Math.PI / 2;
    g.add(barrel);

    const grip = new THREE.Mesh(
        new THREE.CylinderGeometry(R * 0.96, R * 0.96, 0.032, 16, 1, true), alu);
    grip.rotation.x = Math.PI / 2;
    grip.position.z = 0.062;
    g.add(grip);

    const knob = new THREE.Mesh(new THREE.CylinderGeometry(0.011, 0.011, 0.018, 12), knobM);
    knob.rotation.z = Math.PI / 2;
    knob.position.set(-0.070, 0, 0.011);
    g.add(knob);

    const glass = new THREE.Mesh(
        new THREE.SphereGeometry(R - 0.006, 16, 6, 0, Math.PI * 2, 0, Math.PI * 0.30), M.glass());
    glass.rotation.x = -Math.PI / 2;          // 볼록면이 +Z
    glass.position.z = L - 0.034;
    g.add(glass);

    const face = new THREE.Mesh(new THREE.CircleGeometry(R - 0.007, 16), M.diff());
    face.position.z = L - 0.002;
    markEmitter(face, { coneDeg: sp.beam, softness: 0, shape: 'disc', size: sp.barrelD });
    g.add(face);

    return g;
}

// ── fl11Fresnel  (출처: MOD-002_FL-11/MOD-002_threejs.js) ──
function fl11Fresnel(sp) {
    const g = new THREE.Group();
    const D = sp.d, RO = sp.outerD / 2, RL = sp.lensD / 2;
    const shell = M.black(), alu = M.aluDk(), knobM = M.knob();

    const add = (geo, mat, x = 0, y = 0, z = 0) => {
        const m = new THREE.Mesh(geo, mat);
        m.position.set(x, y, z);
        g.add(m);
        return m;
    };

    // 배럴 = 회전체 1덩어리 (마운트 칼라 → 포커스 배럴 → 베젤 링 → 앞면 링)
    const prof = [
        [0.040, 0.000], [0.046, 0.000], [0.046, 0.014],
        [0.050, 0.018], [0.050, 0.026],
        [0.048, 0.030], [0.048, 0.094],
        [0.046, 0.098], [0.046, 0.106],
        [RO, 0.112], [RO, D],
        [RL, D],
    ].map(([r, z]) => new THREE.Vector2(r, z));
    const barrel = new THREE.Mesh(new THREE.LatheGeometry(prof, 16), shell);
    barrel.rotation.x = Math.PI / 2;      // Lathe 축 Y → +Z (부호 주의)
    g.add(barrel);

    // 널링 포커스 그립 (스팟↔플러드)
    const grip = new THREE.Mesh(
        new THREE.CylinderGeometry(0.0485, 0.0485, 0.058, 16, 1, true), alu);
    grip.rotation.x = Math.PI / 2;
    grip.position.z = 0.062;
    g.add(grip);

    // 프레넬 렌즈 — 동심 계단을 회전체로 실제로 깎습니다 (텍스처 없이 무늬 표현)
    const N = 6, stepZ = 0.0022, backZ = -0.006;
    const lp = [new THREE.Vector2(0, 0)];
    for (let i = 1; i <= N; i++) {
        const r = RL * i / N;
        lp.push(new THREE.Vector2(r, -stepZ));   // 경사면
        lp.push(new THREE.Vector2(r, 0));        // 계단 턱
    }
    lp.push(new THREE.Vector2(RL, backZ));
    lp.push(new THREE.Vector2(0, backZ));
    const lens = new THREE.Mesh(new THREE.LatheGeometry(lp, 16), M.glass());
    lens.rotation.x = Math.PI / 2;
    lens.position.z = D - 0.004;
    g.add(lens);

    // 발광면 — 렌즈 바로 뒤 (앞에 두면 프레넬 무늬가 가려집니다). 법선 +Z
    const face = new THREE.Mesh(new THREE.CircleGeometry(RL - 0.001, 16), M.diff());
    face.position.z = D - 0.012;
    markEmitter(face, { coneDeg: sp.beam, softness: 0.15, shape: 'disc', size: sp.lensD });
    g.add(face);

    // 반도어 장착 브래킷 4개 (베젤 가장자리에만)
    for (const [dx, dy] of [[0, 1], [0, -1], [1, 0], [-1, 0]]) {
        add(new THREE.BoxGeometry(dx ? 0.012 : 0.018, dy ? 0.012 : 0.018, 0.013), alu,
            dx * (RO + 0.003), dy * (RO + 0.003), D - 0.007);
    }

    // 마운트 잠금 레버
    add(new THREE.CylinderGeometry(0.009, 0.009, 0.020, 12), knobM, -0.052, 0, 0.012)
        .rotation.z = Math.PI / 2;

    return g;
}

// ── fl11Barndoors  (출처: MOD-002_FL-11/MOD-002_threejs.js) ──
function fl11Barndoors(sp) {
    const g = new THREE.Group();
    const alu = M.aluDk(), leafM = M.rubber();   // 무광 검정 금속판
    const R = sp.ringD / 2;
    const ang = THREE.MathUtils.degToRad(20 + 45 * sp.open);

    const ring = new THREE.Mesh(new THREE.CylinderGeometry(R, R, 0.014, 16, 1, true), alu);
    ring.rotation.x = Math.PI / 2;
    ring.position.z = 0.006;
    g.add(ring);

    for (const [dx, dy] of [[0, 1], [0, -1], [1, 0], [-1, 0]]) {
        const b = new THREE.Mesh(
            new THREE.BoxGeometry(dx ? 0.012 : 0.020, dy ? 0.012 : 0.020, 0.014), alu);
        b.position.set(dx * (R + 0.002), dy * (R + 0.002), 0.007);
        g.add(b);
    }

    // 날개 4장 — 힌지 모서리를 원점으로 옮긴 뒤 벌립니다
    const leaf = (w, h, L, rot, axis, px, py) => {
        const geo = new THREE.BoxGeometry(w, h, L);
        geo.translate(0, 0, L / 2);
        const m = new THREE.Mesh(geo, leafM);
        m.rotation[axis] = rot;
        m.position.set(px, py, 0.010);
        g.add(m);
    };
    leaf(sp.bigW, 0.0018, sp.bigL, -ang, 'x', 0, R);
    leaf(sp.bigW, 0.0018, sp.bigL, ang, 'x', 0, -R);
    leaf(0.0018, sp.smallW, sp.smallL, ang, 'y', R, 0);
    leaf(0.0018, sp.smallW, sp.smallL, -ang, 'y', -R, 0);

    return g;
}

// ── _rod  (출처: STD-001_PRO-403A/STD-001_threejs.js) ──
function _rod(a, b, r, seg = 8) {
    const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b);
    const dir = new THREE.Vector3().subVectors(B, A);
    const geo = new THREE.CylinderGeometry(r, r, dir.length(), seg);
    const quat = new THREE.Quaternion().setFromUnitVectors(
        new THREE.Vector3(0, 1, 0), dir.clone().normalize());
    return { geo, pos: A.clone().addScaledVector(dir, 0.5).toArray(), quat };
}

// ── valensPro403a  (출처: STD-001_PRO-403A/STD-001_threejs.js) ──
function valensPro403a(sp) {
    const g = new THREE.Group();
    const rA = sp.tubeA / 2, rB = sp.tubeB / 2, rC = sp.tubeC / 2;
    const legR = sp.legTube / 2, footR = sp.spreadD / 2;

    // 단 인출량 — 조인트 2개가 균등하게 나옵니다
    const secL = sp.hMin - sp.yHub - sp.spigotL;     // 0.78
    const ext = Math.max(0, (sp.h - sp.hMin) / 2);
    const yC = sp.yHub + secL;
    const yB = yC + ext;
    const yA = yB + ext;

    const cyl = (r, y0, y1, seg = 10) => ({
        geo: new THREE.CylinderGeometry(r, r, y1 - y0, seg),
        pos: [0, (y0 + y1) / 2, 0],
    });

    // 1. 컬럼 3단 (C + B + A)
    //    C 튜브는 다리 결합부 바로 아래에서 끝납니다 (바닥까지 내려오지 않음)
    const yBrace = sp.yHub - 0.042;
    const yColBase = yBrace - 0.022;
    g.add(new THREE.Mesh(geoBatch([
        cyl(rC, yColBase, yC),
        cyl(rB, yC - 0.020, yB),
        cyl(rA, yB - 0.020, yA),
    ]), M.aluDk()));

    // 2. 상단 스피곳 (16mm, 1/4"·3/8" 나사)
    g.add(new THREE.Mesh(geoBatch([
        cyl(0.014, yA, yA + 0.018, 10),
        cyl(sp.spigotD / 2, yA + 0.018, yA + sp.spigotL - 0.006, 10),
        cyl(0.0048, yA + sp.spigotL - 0.006, yA + sp.spigotL, 8),
    ]), M.chrome()));

    // 3. 클램프 칼라 2개 (+ 조임 노브)
    const clampParts = [];
    for (const [y, r] of [[yC, rC], [yB, rB]]) {
        clampParts.push({ geo: new THREE.CylinderGeometry(r + 0.008, r + 0.008, 0.038, 10),
                          pos: [0, y - 0.014, 0] });
        clampParts.push({ geo: new THREE.CylinderGeometry(0.007, 0.007, 0.030, 8),
                          pos: [r + 0.020, y - 0.014, 0], rot: [0, 0, Math.PI / 2] });
        clampParts.push({ geo: new THREE.BoxGeometry(0.006, 0.020, 0.026),
                          pos: [r + 0.036, y - 0.014, 0] });
    }
    g.add(new THREE.Mesh(geoBatch(clampParts), M.knob()));

    // 4. 다리 3개 + 브레이스 3개
    const legParts = [];
    for (let i = 0; i < 3; i++) {
        const a = (i / 3) * Math.PI * 2;
        const cx = Math.cos(a), cz = Math.sin(a);
        legParts.push(_rod([cx * (rC + 0.012), sp.yHub, cz * (rC + 0.012)],
                           [cx * footR, 0.018, cz * footR], legR));
        legParts.push(_rod([cx * (rC + 0.010), yBrace, cz * (rC + 0.010)],
                           [cx * footR * 0.52, 0.018 + (sp.yHub - 0.018) * 0.48, cz * footR * 0.52],
                           0.0055, 6));
    }
    g.add(new THREE.Mesh(geoBatch(legParts), M.aluDk()));

    // 5. 고무 발 3개
    const footParts = [];
    for (let i = 0; i < 3; i++) {
        const a = (i / 3) * Math.PI * 2;
        footParts.push({ geo: new THREE.CylinderGeometry(0.014, 0.017, 0.020, 8),
                         pos: [Math.cos(a) * footR, 0.010, Math.sin(a) * footR] });
    }
    g.add(new THREE.Mesh(geoBatch(footParts), M.rubber()));

    // 6. 다리 허브 + 브레이스 칼라
    g.add(new THREE.Mesh(geoBatch([
        { geo: new THREE.CylinderGeometry(rC + 0.011, rC + 0.011, 0.052, 10), pos: [0, sp.yHub - 0.018, 0] },
        { geo: new THREE.CylinderGeometry(rC + 0.008, rC + 0.008, 0.030, 10), pos: [0, yBrace, 0] },
    ]), M.alu()));

    return g;
}

// ── valensVl3000g  (출처: ACC-006_ASSY-BGS-001/ACC-006_threejs.js) ──
// VALENS VL-3000G 3.2m 이동 배경용 크로스바 (봉 단품). X축으로 눕힌 튜브.
function valensVl3000g(sp) {
    const g = new THREE.Group();

    const N = Math.max(1, Math.min(4, sp.sections));
    const L = sp.secL * N;
    const R = sp.tubeD / 2;
    const anod = mat(0x1f2328, { roughness: 0.32, metalness: 0.72 });   // 흑색 아노다이징

    const cylX = (r, len, x, seg) => ({
        geo: new THREE.CylinderGeometry(r, r, len, seg),
        pos: [x, 0, 0], rot: [0, 0, Math.PI / 2],
    });

    const sprd = Math.max(0, sp.spread || 0);
    const tube = [], joints = [];

    if (sprd === 0) {
        tube.push(cylX(R, L, 0, 10));
        for (let i = 1; i < N; i++) joints.push(cylX(R + 0.0012, 0.014, -L / 2 + i * sp.secL, 8));
    } else {
        const total = N * sp.secL + (N - 1) * sprd;
        for (let i = 0; i < N; i++) {
            const x0 = -total / 2 + i * (sp.secL + sprd);
            tube.push(cylX(R, sp.secL, x0 + sp.secL / 2, 10));
            if (i < N - 1) {
                const out = Math.min(sprd + 0.010, sp.ferruleL);
                joints.push(cylX(sp.ferruleD / 2, out, x0 + sp.secL + out / 2 - 0.005, 8));
            }
        }
    }
    const half = sprd === 0 ? L / 2 : (N * sp.secL + (N - 1) * sprd) / 2;
    for (const s of [-1, 1]) tube.push(cylX(R + 0.0008, 0.010, s * (half - 0.005), 8));

    g.add(new THREE.Mesh(geoBatch(tube), anod));
    if (joints.length) g.add(new THREE.Mesh(geoBatch(joints), M.chrome()));
    return g;
}

// ── backdropRig  (출처: ACC-006_ASSY-BGS-001) — 앱 자산에 맞게 각색 ──
// 배경 스탠드 2대(A스탠드 PRO-403A) + 크로스바 봉. 원점 = 리그 바닥 정중앙,
// 로컬 X축이 두 스탠드를 잇는 방향. span=스탠드 간격, h=봉 높이.
function backdropRig(opts) {
    const g = new THREE.Group();
    const cb = SPECS['ACC-006'];
    // 배경 스탠드는 배경지를 걸 만큼 높이 세우므로 풀사이즈 A스탠드 형상을 씀
    const st = opts.standSpec || _aStandSpec(1.0);
    const sections = Math.max(1, Math.min(4, opts.sections || cb.sections));
    const barLen = cb.secL * sections;
    const h = Math.min(Math.max(opts.h || 2.30, st.hMin), st.hMax);
    const span = Math.min(opts.span || 2.90, barLen - 0.20);   // 봉 안쪽으로

    [-1, 1].forEach(s => {
        const m = valensPro403a(Object.assign({}, st, { h }));
        m.position.x = s * span / 2;
        m.rotation.y = Math.PI / 2;      // 다리 하나가 배경(-Z) 쪽을 보게
        g.add(m);
    });

    const bar = valensVl3000g(Object.assign({}, cb, { sections }));
    bar.position.y = h - cb.yDrop;
    g.add(bar);
    return g;
}

// ── valensPro40t  (출처: STD-002_PRO-40T/STD-002_threejs.js) ──
function valensPro40t(sp) {
    const g = new THREE.Group();
    const rA = sp.tubeA / 2, rB = sp.tubeB / 2, rC = sp.tubeC / 2;
    const legR = sp.legTube / 2, footR = sp.spreadD / 2;
    const steel = M.chrome(), alu = M.alu();

    const secL = sp.hMin - sp.yBase - sp.spigotL;      // 1.08
    const ext = Math.max(0, (sp.h - sp.hMin) / 2);
    const yC = sp.yBase + secL;
    const yB = yC + ext;
    const yA = yB + ext;

    const cyl = (r, y0, y1, seg = 8, open = false) => ({
        geo: new THREE.CylinderGeometry(r, r, y1 - y0, seg, 1, open),
        pos: [0, (y0 + y1) / 2, 0],
    });

    // 1. 컬럼 3단 + 상단 스피곳
    g.add(new THREE.Mesh(geoBatch([
        cyl(rC, sp.yBase - 0.060, yC, 8, true),
        cyl(rB, yC - 0.020, yB, 8, true),
        cyl(rA, yB - 0.020, yA, 8, true),
        cyl(0.013, yA, yA + 0.016),
        cyl(sp.spigotD / 2, yA + 0.016, yA + sp.spigotL - 0.005),
        cyl(0.0048, yA + sp.spigotL - 0.005, yA + sp.spigotL, 6),
    ]), steel));

    // 2. 클램프 칼라 2개 + T노브
    const clampParts = [];
    for (const [y, r] of [[yC, rC], [yB, rB]]) {
        clampParts.push(cyl(r + 0.009, y - 0.036, y + 0.002, 8, true));
        clampParts.push({ geo: new THREE.CylinderGeometry(0.006, 0.006, 0.026, 6),
                          pos: [r + 0.020, y - 0.017, 0], rot: [0, 0, Math.PI / 2] });
        clampParts.push({ geo: new THREE.BoxGeometry(0.007, 0.030, 0.011),
                          pos: [r + 0.035, y - 0.017, 0] });
    }
    g.add(new THREE.Mesh(geoBatch(clampParts), alu));

    // 3. 터틀 베이스 보스 — 다리 3개가 서로 다른 높이에 물립니다
    const bossParts = [];
    for (const y of sp.legY) bossParts.push(cyl(sp.legHubR, y - 0.024, y + 0.024, 8, true));
    bossParts.push(cyl(0.024, 0.264, sp.yBase, 8));                 // 컬럼 소켓
    bossParts.push({ geo: new THREE.BoxGeometry(0.008, 0.075, 0.030), pos: [0.036, 0.245, 0] });
    g.add(new THREE.Mesh(geoBatch(bossParts), steel));

    // 4. 다리 3개 — 직선 암 → 한 번 꺾임 → 직선 끝단
    //    펼침각(α)은 스펙이 아니라 계산값입니다. 끝단이 바닥에 닿도록 다리마다
    //    따로 풉니다. 보스가 3단 스태거라 다리별로 각이 조금씩 달라집니다.
    const th = THREE.MathUtils.degToRad(sp.bendDeg);
    const L1 = sp.legArm, L2 = sp.legTip, FOOT_R = 0.0125;
    const FOLD = THREE.MathUtils.degToRad(-82);   // 접으면 암이 컬럼과 나란해집니다

    const bisect = (target) => {
        const f = a => L1 * Math.sin(a) + L2 * Math.sin(a + th) - target;
        let lo = -0.6, hi = 1.2;
        for (let i = 0; i < 48; i++) { const m = (lo + hi) / 2; if (f(m) < 0) lo = m; else hi = m; }
        return (lo + hi) / 2;
    };
    // 발이 비스듬히 붙어 있어 띄울 높이가 α 에 의존합니다 — 2패스로 수렴시킵니다
    const solveAlpha = (y0) => {
        let a = bisect(y0 - FOOT_R);
        for (let k = 0; k < 3; k++) a = bisect(y0 - FOOT_R * Math.cos(a + th));
        return a;
    };

    const legParts = [], footParts = [];
    for (let i = 0; i < 3; i++) {
        const ang = (i / 3) * Math.PI * 2 + Math.PI / 6;
        const cx = Math.cos(ang), cz = Math.sin(ang), y0 = sp.legY[i];
        const a = THREE.MathUtils.lerp(solveAlpha(y0), FOLD, sp.fold);

        // (반경 u, 높이 v) 평면에서 계산한 뒤 3D 로 올립니다
        const d1 = [Math.cos(a), -Math.sin(a)];
        const d2 = [Math.cos(a + th), -Math.sin(a + th)];
        const p0 = [sp.legHubR - 0.002, y0];
        const pb = [p0[0] + L1 * d1[0], p0[1] + L1 * d1[1]];   // 꺾이는 지점
        const pt = [pb[0] + L2 * d2[0], pb[1] + L2 * d2[1]];   // 끝단
        const go = (p, d, t) => [p[0] + d[0] * t, p[1] + d[1] * t];
        const V = q => new THREE.Vector3(cx * q[0], q[1], cz * q[0]);

        // 꺾임을 둥글게 — 코너 앞뒤에 점을 넣고 CatmullRom 으로 잇습니다
        const curve = new THREE.CatmullRomCurve3([
            V(p0), V(go(p0, d1, L1 * 0.55)),
            V(go(pb, d1, -L1 * 0.10)), V(go(pb, d2, L2 * 0.18)),
            V(pt),
        ], false, 'catmullrom', 0.5);
        legParts.push({ geo: new THREE.TubeGeometry(curve, 10, legR, 5, false) });

        // 고무 발 — 끝단 축을 따라 붙습니다
        footParts.push(_rod(V(go(pt, d2, -0.030)).toArray(), V(pt).toArray(), FOOT_R, 6));
    }
    g.add(new THREE.Mesh(geoBatch(legParts), steel));
    g.add(new THREE.Mesh(geoBatch(footParts), M.rubber()));

    // 6. 베이스 잠금 T노브
    g.add(new THREE.Mesh(geoBatch([
        { geo: new THREE.CylinderGeometry(0.006, 0.006, 0.030, 6),
          pos: [-0.032, sp.legY[2], 0], rot: [0, 0, Math.PI / 2] },
        { geo: new THREE.BoxGeometry(0.007, 0.032, 0.012), pos: [-0.049, sp.legY[2], 0] },
    ]), alu));

    return g;
}

// ── terisTsn6cfTripod  (출처: TRP-001_TSN6CF-Q-PLUS/TRP-001_threejs.js) ──
function terisTsn6cfTripod(sp) {
    const g = new THREE.Group();
    
    const yS = sp.hBowl - 0.055;               // 스파이더 힌지 높이
    const dy = yS - 0.020;

    // 펼침 폭은 스프레더로 정하지만, 다리 길이가 물리적으로 가능한 범위를
    // 벗어나면 폭을 자동으로 보정합니다 (낮게 쓰면 다리를 더 벌려야 합니다).
    let R = sp.spreadD / 2;
    const legLen = Math.hypot(dy, R - sp.hingeR);
    if (legLen > sp.legMax) R = sp.hingeR + Math.sqrt(Math.max(0, sp.legMax ** 2 - dy ** 2));
    if (legLen < sp.legMin) R = sp.hingeR + Math.sqrt(Math.max(0, sp.legMin ** 2 - dy ** 2));
    const carbon = mat(0x24262b, { roughness: 0.42, metalness: 0.25 });
    const red = mat(0xc0261f, { roughness: 0.45, metalness: 0.10 });
    const cast = M.aluDk();

    const legParts = [], stripeParts = [], castParts = [], spdParts = [];

    // ── 스파이더 + 75mm 볼 캐스팅 ─────────────────────────────────────────
    const cyl = (r, y0, y1, seg = 10, open = false) => ({
        geo: new THREE.CylinderGeometry(r, r, y1 - y0, seg, 1, open),
        pos: [0, (y0 + y1) / 2, 0],
    });
    castParts.push(cyl(0.056, yS - 0.014, yS + 0.034, 10));                 // 캐스팅 몸통
    castParts.push({ geo: new THREE.CylinderGeometry(0.056, 0.040, 0.022, 10),
                     pos: [0, sp.hBowl - 0.011, 0] });                      // 볼 시트 테이퍼
    castParts.push(cyl(sp.ball / 2 + 0.004, sp.hBowl - 0.004, sp.hBowl, 12)); // 볼 개구부 림
    castParts.push({ geo: new THREE.CylinderGeometry(0.007, 0.007, 0.052, 6),
                     pos: [0.062, yS + 0.010, 0], rot: [0, 0, Math.PI / 2] }); // 볼 클램프 핸들

    // 원버튼 언락 중앙 로드 — 스프레더 허브까지 내려옵니다
    castParts.push(cyl(0.011, 0.030, yS - 0.010, 6));

    for (let i = 0; i < 3; i++) {
        const a = (i / 3) * Math.PI * 2 + Math.PI / 2;
        const cx = Math.cos(a), cz = Math.sin(a);
        const tx = -cz, tz = cx;                                    // 접선 방향 (트윈튜브 오프셋)

        const A = new THREE.Vector3(cx * sp.hingeR, yS, cz * sp.hingeR);
        const B = new THREE.Vector3(cx * R, 0.020, cz * R);
        const Mid = A.clone().lerp(B, 0.52);

        const off = (p, s, d) => [p.x + tx * s * d, p.y, p.z + tz * s * d];

        // 트윈튜브 — 상단 2 + 하단 2
        for (const s of [-1, 1]) {
            legParts.push(rod(off(A, s, sp.twinGap / 2), off(Mid, s, sp.twinGap / 2), sp.tubeUp / 2, 5));
            legParts.push(rod(off(Mid.clone().lerp(B, -0.05), s, sp.twinGap / 2 - 0.002),
                              off(B, s, sp.twinGap / 2 - 0.002), sp.tubeLo / 2, 5));
        }
        // 레드 스트라이프 — 두 튜브 사이
        stripeParts.push(rod([A.x, A.y, A.z], [Mid.x, Mid.y, Mid.z], 0.0055, 4));

        // 힌지 브래킷 + 중간 클램프
        castParts.push({ geo: new THREE.BoxGeometry(0.030, 0.046, 0.026),
                         pos: [cx * 0.052, yS - 0.006, cz * 0.052], rot: [0, -a, 0] });
        const cl = rod(off(Mid.clone().lerp(A, 0.05), 0, 0), off(Mid.clone().lerp(B, 0.05), 0, 0), 0.026, 6);
        cl.geo = new THREE.BoxGeometry(0.052, 0.052, 0.055);
        castParts.push({ geo: cl.geo, pos: cl.pos, quat: cl.quat });

        // 그라운드 스프레더 — 허브에서 각 발까지
        spdParts.push(rod([0, 0.022, 0], [B.x, 0.022, B.z], 0.014, 4));
        spdParts.push({ geo: new THREE.BoxGeometry(0.050, 0.036, 0.044),
                        pos: [B.x, 0.018, B.z], rot: [0, -a, 0] });          // 발 클램프
    }

    // 스프레더 허브
    spdParts.push(cyl(0.030, 0.010, 0.034, 8));

    g.add(new THREE.Mesh(geoBatch(legParts), carbon));
    g.add(new THREE.Mesh(geoBatch(stripeParts), red));
    g.add(new THREE.Mesh(geoBatch(castParts), cast));
    g.add(new THREE.Mesh(geoBatch(spdParts), M.black()));

    return g;
}

// ── terisTsn6Head  (출처: TRP-001_TSN6CF-Q-PLUS/TRP-001_threejs.js) ──
function terisTsn6Head(sp) {
    const g = new THREE.Group();
    
    const body = M.black(), alu = M.aluDk(), knobM = M.knob();
    const red = mat(0xc0261f, { roughness: 0.45, metalness: 0.10 });

    const add = (geo, m, x = 0, y = 0, z = 0) => {
        const me = new THREE.Mesh(geo, m);
        me.position.set(x, y, z);
        g.add(me);
        return me;
    };

    // ── 볼 (75mm 반구) + 클램프 칼라 ──────────────────────────────────────
    const bR = sp.ball / 2;
    add(new THREE.SphereGeometry(bR, 14, 6, 0, Math.PI * 2, Math.PI * 0.52, Math.PI * 0.48),
        alu, 0, -sp.yBowl + bR * 0.55, 0);
    add(new THREE.CylinderGeometry(0.040, 0.040, 0.020, 12), alu, 0, -sp.yBowl + 0.044, 0);

    // ── 헤드 본체 ─────────────────────────────────────────────────────────
    add(new THREE.BoxGeometry(0.098, 0.070, 0.116), body, 0, -0.004, 0.004);
    add(new THREE.BoxGeometry(0.086, 0.026, 0.100), alu, 0, -0.042, 0.004);   // 팬 베이스

    // 측면 드래그 다이얼 (좌우) + 로고면
    for (const s of [-1, 1]) {
        add(new THREE.CylinderGeometry(0.031, 0.031, 0.010, 14), alu, s * 0.052, -0.004, 0.006)
            .rotation.z = Math.PI / 2;
    }
    add(new THREE.CylinderGeometry(0.018, 0.018, 0.004, 12),
        mat(0xc8a24a, { roughness: 0.5, metalness: 0.6 }), -0.058, -0.004, 0.006)
        .rotation.z = Math.PI / 2;                                            // TERIS 로고 디스크

    // 카운터밸런스 / 틸트 잠금 노브
    add(new THREE.CylinderGeometry(0.013, 0.013, 0.020, 10), knobM, 0.056, -0.026, -0.038)
        .rotation.z = Math.PI / 2;

    // ── QR 플레이트 (슬라이딩) + 레드 릴리즈 레버 ─────────────────────────
    add(new THREE.BoxGeometry(sp.plateW, 0.014, sp.plateL), alu, 0, sp.yPlate - 0.007, 0.010);
    add(new THREE.BoxGeometry(0.070, 0.016, 0.090), body, 0, sp.yPlate - 0.022, 0.006); // 플레이트 베이스
    add(new THREE.BoxGeometry(0.030, 0.014, 0.026), red, 0.048, sp.yPlate - 0.016, 0.030);

    // 수평계
    add(new THREE.CylinderGeometry(0.008, 0.008, 0.006, 10),
        mat(0x9fe8a0, { roughness: 0.3, metalness: 0, emissive: 0x2f5a30, emissiveIntensity: 0.4 }),
        -0.034, -0.030, 0.058);

    // ── 팬바 — 마운트에서 뒤·오른쪽으로 뻗습니다 ──────────────────────────
    const barDir = new THREE.Vector3(0.62, 0.14, -0.77).normalize();
    const mount = new THREE.Vector3(0.044, -0.020, -0.046);
    const barGeo = new THREE.CylinderGeometry(0.008, 0.008, sp.barLen * 0.62, 8);
    const bar = add(barGeo, alu);
    bar.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), barDir);
    bar.position.copy(mount).addScaledVector(barDir, sp.barLen * 0.31);

    const gripGeo = new THREE.CylinderGeometry(0.013, 0.012, sp.barLen * 0.40, 10);
    const grip = add(gripGeo, M.rubber());
    grip.quaternion.copy(bar.quaternion);
    grip.position.copy(mount).addScaledVector(barDir, sp.barLen * 0.80);

    add(new THREE.CylinderGeometry(0.014, 0.014, 0.018, 10), knobM, mount.x, mount.y, mount.z)
        .quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), barDir);

    return g;
}

// ── 추가 빌더 (2차: PavoSlim·MixPanel·V1·NANLINK) ──
// ── pavoSlim240bPanel  (출처: LIT-004_PavoSlim240B/LIT-004_threejs.js) ──
function pavoSlim240bPanel(sp) {
    const g = new THREE.Group();

    const HW = sp.w / 2, H = sp.h, T = sp.t, B = sp.border;
    const zb = sp.zBack, zf = zb + T;
    const frameM = M.black(), alu = M.aluDk();
    const blue = mat(0x1f8fbf, { roughness: 0.45, metalness: 0.25 });   // NANLITE 블루 노브

    const box = (w, h, d, x, y, z) => ({ geo: new THREE.BoxGeometry(w, h, d), pos: [x, y, z] });
    const phi = THREE.MathUtils.degToRad(90 * sp.fold);

    // ── 좌/우 반쪽 — 세로 중앙 힌지에서 대칭으로 접힙니다 ─────────────────
    for (const s of [-1, 1]) {
        const half = new THREE.Group();
        half.rotation.y = -s * phi;          // 바깥 모서리가 앞(+Z)으로 모입니다
        g.add(half);

        const cx = s * HW / 2;               // 반쪽 중심 (힌지 기준)

        // 프레임 + 방열 리브 + 코너 블록
        const shell = [box(HW, H, T, cx, 0, zb + T / 2)];
        for (let i = 0; i < 4; i++) {
            shell.push(box(HW * 0.86, 0.010, 0.004,
                cx, (i - 1.5) * H * 0.19, zb - 0.002));                 // 후면 방열 리브
        }
        for (const ux of [-1, 1]) for (const uy of [-1, 1]) {
            shell.push(box(0.030, 0.030, T + 0.004,
                cx + ux * (HW / 2 - 0.015), uy * (H / 2 - 0.015), zb + T / 2));  // 코너 블록
        }
        half.add(new THREE.Mesh(geoBatch(shell), frameM));

        // 확산면 = 발광면 (법선 +Z)
        const face = new THREE.Mesh(
            new THREE.PlaneGeometry(HW - B * 2, H - B * 2), M.diff());
        face.position.set(cx, 0, zf + 0.0008);
        markEmitter(face, {
            coneDeg: sp.beam, softness: 0.6, shape: 'disc',
            size: Math.sqrt(4 * (HW - B * 2) * (H - B * 2) / Math.PI),   // 등가 원 지름
        });
        half.add(face);
    }

    // ── 스위블 홀더 (패널 뒷면 → 틸트축 → 5/8" 리시버) ────────────────────
    const hold = [];
    hold.push(box(0.130, 0.110, 0.006, 0, 0, zb - 0.004));              // 패널 부착 플레이트
    hold.push(box(0.036, 0.052, 0.040, 0, -0.014, zb - 0.026));         // 틸트 브래킷
    hold.push({ geo: new THREE.CylinderGeometry(0.017, 0.017, 0.046, 12),
                pos: [0, 0, 0], rot: [0, 0, Math.PI / 2] });            // 틸트축 허브
    hold.push({ geo: new THREE.CylinderGeometry(0.0145, 0.0145, 0.052, 12),
                pos: [0, -0.042, 0] });                                  // 5/8" 리시버
    hold.push(box(0.024, 0.010, 0.030, 0, 0.062, zb - 0.008));          // DC 커넥터 포트
    g.add(new THREE.Mesh(geoBatch(hold), alu));

    // 틸트 잠금 노브 (블루)
    const knob = new THREE.Mesh(new THREE.CylinderGeometry(0.021, 0.021, 0.018, 12), blue);
    knob.rotation.z = Math.PI / 2;
    knob.position.set(-0.032, 0, 0);
    g.add(knob);

    return g;
}

// ── mixPanel150  (출처: LIT-005_MixPanel150/LIT-005_threejs.js) ──
function mixPanel150(sp) {
    const g = new THREE.Group();

    const HW = sp.w / 2, HH = sp.h / 2, HD = sp.d / 2, B = sp.border;
    const body = M.black(), alu = M.aluDk(), knobM = M.knob();
    const carbon = mat(0x1a1c20, { roughness: 0.52, metalness: 0.30 });

    const box = (w, h, d, x, y, z) => ({ geo: new THREE.BoxGeometry(w, h, d), pos: [x, y, z] });
    const cylX = (r, len, x, y, z, seg = 12) => ({
        geo: new THREE.CylinderGeometry(r, r, len, seg), pos: [x, y, z], rot: [0, 0, Math.PI / 2],
    });
    const cylZ = (r, len, x, y, z, seg = 12) => ({
        geo: new THREE.CylinderGeometry(r, r, len, seg), pos: [x, y, z], rot: [Math.PI / 2, 0, 0],
    });

    // ── 1. 패널 본체 + 전면 베젤 + 코너 브래킷 ────────────────────────────
    const shell = [box(sp.w, sp.h, sp.d, 0, 0, 0)];
    for (const [ux, uy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
        shell.push(box(0.034, 0.034, sp.d + 0.004,
            ux * (HW - 0.019), uy * (HH - 0.019), 0));                    // 코너 브래킷
    }
    shell.push(box(0.070, 0.012, 0.030, -0.06, HH + 0.004, 0));           // 상단 마운팅 탭
    shell.push(box(0.070, 0.012, 0.030, 0.06, -HH - 0.004, 0));           // 하단 마운팅 탭
    g.add(new THREE.Mesh(geoBatch(shell), body));

    // ── 2. 발광면 (LED 어레이 + 전면 확산) ────────────────────────────────
    const face = new THREE.Mesh(
        new THREE.PlaneGeometry(sp.w - B * 2, sp.h - B * 2), M.diff());
    face.position.z = HD + 0.001;
    markEmitter(face, {
        coneDeg: sp.beam, softness: 0.55, shape: 'disc',
        size: Math.sqrt(4 * (sp.w - B * 2) * (sp.h - B * 2) / Math.PI),   // 등가 원 지름
    });
    g.add(face);

    // ── 3. 후면 — 카본 백플레이트 + V마운트 + 방열 그릴 ───────────────────
    const rear = [];
    rear.push(box(sp.w - 0.030, sp.h - 0.030, 0.004, 0, 0, -HD - 0.001));  // 백플레이트
    rear.push(box(0.098, 0.084, 0.014, 0, HH * 0.42, -HD - 0.009));        // V마운트 플레이트
    for (const s of [-1, 1]) {
        rear.push(box(0.072, 0.062, 0.006, s * 0.120, HH * 0.42, -HD - 0.005));  // 방열 그릴
    }
    g.add(new THREE.Mesh(geoBatch(rear), carbon));

    // ── 4. 후면 컨트롤 패널 ───────────────────────────────────────────────
    const cy = -HH * 0.30;
    const ctrl = [];
    ctrl.push(box(0.230, 0.110, 0.010, 0, cy, -HD - 0.006));               // 패널 베이스
    for (let i = 0; i < 3; i++) {
        ctrl.push(cylZ(0.011, 0.010, 0.034 + i * 0.030, cy + 0.030, -HD - 0.013, 10));  // 노브 3
    }
    for (let r = 0; r < 2; r++) for (let c = 0; c < 3; c++) {
        ctrl.push(box(0.020, 0.010, 0.004, 0.034 + c * 0.030, cy - 0.006 - r * 0.018, -HD - 0.012));
    }
    g.add(new THREE.Mesh(geoBatch(ctrl), alu));

    const lcd = new THREE.Mesh(new THREE.PlaneGeometry(0.062, 0.048),
        mat(0x0e1319, { roughness: 0.10, metalness: 0.05 }));
    lcd.position.set(-0.050, cy + 0.004, -HD - 0.0115);
    lcd.rotation.y = Math.PI;
    g.add(lcd);

    // ── 5. 측면 핸들 ──────────────────────────────────────────────────────
    const handle = new THREE.Mesh(new THREE.BoxGeometry(0.020, 0.100, 0.026), M.rubber());
    handle.position.set(-HW + 0.048, -HH * 0.28, -HD - 0.014);
    g.add(handle);

    // ── 6. 요크 (패널 양옆을 잡고 아래로 내려오는 U 브래킷) ────────────────
    const ax = HW + sp.yokeGap;
    const yTop = HH * 0.52, yBot = -HH - 0.030;
    const path = new THREE.CatmullRomCurve3([
        new THREE.Vector3(ax, yTop, 0), new THREE.Vector3(ax, yBot + 0.040, 0),
        new THREE.Vector3(ax * 0.86, yBot + 0.006, 0), new THREE.Vector3(0, yBot, 0),
        new THREE.Vector3(-ax * 0.86, yBot + 0.006, 0), new THREE.Vector3(-ax, yBot + 0.040, 0),
        new THREE.Vector3(-ax, yTop, 0),
    ], false, 'catmullrom', 0.2);
    g.add(new THREE.Mesh(new THREE.TubeGeometry(path, 22, 0.009, 5, false), alu));

    // 틸트 노브 2 + 스탠드 스피곳 리시버
    const hw = [];
    for (const s of [-1, 1]) hw.push(cylX(0.017, 0.024, s * (ax + 0.012), 0, 0, 12));
    hw.push({ geo: new THREE.CylinderGeometry(0.0155, 0.0155, yBot + sp.yokeDrop, 12),
              pos: [0, (yBot - sp.yokeDrop) / 2, 0] });                   // 5/8" 스피곳 리시버
    g.add(new THREE.Mesh(geoBatch(hw), knobM));

    return g;
}

// ── v1RoundedRect  (출처: LIT-006_GodoxV1/LIT-006_threejs.js) ──
function v1RoundedRect(hw, hh, r) {
    const s = new THREE.Shape();
    s.moveTo(-hw + r, -hh);
    s.lineTo(hw - r, -hh); s.quadraticCurveTo(hw, -hh, hw, -hh + r);
    s.lineTo(hw, hh - r);  s.quadraticCurveTo(hw, hh, hw - r, hh);
    s.lineTo(-hw + r, hh); s.quadraticCurveTo(-hw, hh, -hw, hh - r);
    s.lineTo(-hw, -hh + r); s.quadraticCurveTo(-hw, -hh, -hw + r, -hh);
    return s;
}

// ── godoxV1  (출처: LIT-006_GodoxV1/LIT-006_threejs.js) ──
function godoxV1(sp) {
    const g = new THREE.Group();

    const HW = sp.w / 2, BD = sp.bodyD;
    const zBack = -0.043, zFrontBody = zBack + BD;
    const body = M.black(), alu = M.aluDk(), knobM = M.knob();

    const box = (w, h, d, x, y, z) => ({ geo: new THREE.BoxGeometry(w, h, d), pos: [x, y, z] });

    // ── 1. 바디 — 라운드 사각 단면을 앞뒤로 압출 ──────────────────────────
    const geo = new THREE.ExtrudeGeometry(
        v1RoundedRect(HW, (sp.yBodyTop - 0.020) / 2, 0.008),
        { depth: BD, bevelEnabled: false, curveSegments: 3 });
    geo.translate(0, 0.020 + (sp.yBodyTop - 0.020) / 2, zBack);
    g.add(new THREE.Mesh(geo, body));

    // ── 2. 핫슈 발 + 잠금 링 ──────────────────────────────────────────────
    const foot = [];
    foot.push(box(0.052, 0.005, 0.032, 0, 0.0025, zBack + 0.020));            // 슈 발판
    foot.push({ geo: new THREE.CylinderGeometry(0.019, 0.019, 0.013, 12),
                pos: [0, 0.0115, zBack + 0.020] });                            // 잠금 링
    foot.push(box(0.062, 0.008, 0.040, 0, 0.022, zBack + 0.020));              // 슈 베이스
    g.add(new THREE.Mesh(geoBatch(foot), knobM));

    // ── 3. 후면 컨트롤 (LCD + 다이얼 + 버튼) ──────────────────────────────
    const rear = [];
    rear.push(box(0.062, 0.040, 0.004, 0, 0.084, zBack - 0.001));              // LCD 베젤
    rear.push({ geo: new THREE.CylinderGeometry(0.016, 0.016, 0.005, 12),
                pos: [0, 0.046, zBack - 0.001], rot: [Math.PI / 2, 0, 0] });   // 셀렉트 다이얼
    for (const x of [-0.024, 0.024]) {
        rear.push(box(0.014, 0.008, 0.003, x, 0.030, zBack - 0.001));          // 버튼
    }
    g.add(new THREE.Mesh(geoBatch(rear), alu));

    const lcd = new THREE.Mesh(new THREE.PlaneGeometry(0.052, 0.032),
        mat(0x1b2a24, { roughness: 0.15, metalness: 0.05 }));
    lcd.position.set(0, 0.084, zBack - 0.0032);
    lcd.rotation.y = Math.PI;
    g.add(lcd);

    // 전면 AF 보조광 창
    const af = new THREE.Mesh(new THREE.BoxGeometry(0.028, 0.018, 0.003),
        mat(0x4a1010, { roughness: 0.25, metalness: 0.05, transparent: true, opacity: 0.85 }));
    af.position.set(0, 0.062, zFrontBody + 0.0005);
    g.add(af);

    // ── 4. 헤드 — 틸트/스위블 하는 라운드 헤드 ────────────────────────────
    const swivel = new THREE.Group();
    swivel.position.set(0, sp.yPivot, sp.zPivot);
    swivel.rotation.y = THREE.MathUtils.degToRad(sp.swivel);
    g.add(swivel);

    const tilt = new THREE.Group();
    tilt.rotation.x = -THREE.MathUtils.degToRad(sp.tilt);   // + 는 위로
    swivel.add(tilt);

    const R = sp.headD / 2, L = sp.headLen;
    const zc = sp.h - sp.yPivot - R;          // 헤드 중심 높이가 전체 197mm 를 만듭니다
    const zF = sp.zHeadFront;                 // 헤드 앞면 (틸트 로컬). 전체 깊이 93mm 를 만듭니다
    const headParts = [];
    // 앞 뚜껑이 발광면을 가리므로 통은 열린 원통(openEnded)으로 만들고 뒤판만 따로 덮습니다
    headParts.push({ geo: new THREE.CylinderGeometry(R, R, L, 16, 1, true),
                     pos: [0, zc, zF - L / 2], rot: [Math.PI / 2, 0, 0] });       // 헤드 통
    headParts.push({ geo: new THREE.CylinderGeometry(R - 0.001, R - 0.001, 0.005, 16),
                     pos: [0, zc, zF - L + 0.0025], rot: [Math.PI / 2, 0, 0] });  // 헤드 뒤판
    headParts.push({ geo: new THREE.CylinderGeometry(R - 0.004, R - 0.004, 0.004, 16),
                     pos: [0, zc, zF - 0.010], rot: [Math.PI / 2, 0, 0] });       // 발광면 뒤 배플
    headParts.push({ geo: new THREE.BoxGeometry(0.040, 0.028, 0.030),
                     pos: [0, zc - R * 0.86, zF - L + 0.010] });                  // 넥
    tilt.add(new THREE.Mesh(geoBatch(headParts), body));

    // 발광면 → 모델링 LED → 프레넬 커버 순서 (법선 +Z, 림 안쪽으로 살짝 들어감)
    const face = new THREE.Mesh(new THREE.CircleGeometry(R - 0.006, 16), M.diff());
    face.position.set(0, zc, zF - 0.0070);
    markEmitter(face, {
        coneDeg: sp.beam, softness: 0, shape: 'disc', size: (R - 0.006) * 2,
    });
    tilt.add(face);

    // 모델링 LED (헤드 중앙, 3200K)
    const led = new THREE.Mesh(new THREE.CircleGeometry(0.006, 10),
        mat(0xf0e2c0, { roughness: 0.8, metalness: 0, emissive: 0xffeec8, emissiveIntensity: 0.5 }));
    led.position.set(0, zc, zF - 0.0060);
    tilt.add(led);

    const fres = new THREE.Mesh(new THREE.CircleGeometry(R - 0.004, 16), M.glass());
    fres.position.set(0, zc, zF - 0.0020);
    tilt.add(fres);

    return g;
}

// ── nanlinkBoxWsTb1  (출처: ACC-001_WS-TB-1/ACC-001_threejs.js) ──
function nanlinkBoxWsTb1(sp) {
    const g = new THREE.Group();

    const hw = sp.w / 2, hh = sp.h / 2, cx = sp.chamX, cy = sp.chamY;
    const BD = sp.bodyD;
    const alu = mat(0x9aa0a6, { roughness: 0.42, metalness: 0.70 });   // 알루미늄 샌드블라스트
    const dark = M.knob();

    // ── 1. 본체 — 모서리 잘린 팔각 판을 앞뒤로 압출 ───────────────────────
    const s = new THREE.Shape();
    s.moveTo(-hw + cx, -hh);
    s.lineTo(hw - cx, -hh); s.lineTo(hw, -hh + cy);
    s.lineTo(hw, hh - cy);  s.lineTo(hw - cx, hh);
    s.lineTo(-hw + cx, hh); s.lineTo(-hw, hh - cy);
    s.lineTo(-hw, -hh + cy); s.closePath();

    const geo = new THREE.ExtrudeGeometry(s, { depth: BD, bevelEnabled: false });
    geo.translate(0, hh, -BD / 2);      // 바닥면을 y=0 으로, 두께 중심을 z=0 으로
    g.add(new THREE.Mesh(geo, alu));

    // ── 2. 벨트 클립 (-Z) + 섀시 일체형 링 ────────────────────────────────
    const back = [];
    back.push({ geo: new THREE.BoxGeometry(0.032, 0.048, 0.004),
                pos: [0, hh - 0.004, -sp.d + BD / 2 + 0.004] });             // 클립 판
    back.push({ geo: new THREE.BoxGeometry(0.030, 0.009, 0.008),
                pos: [0, hh + 0.022, -BD / 2 - 0.003] });                    // 클립 목
    back.push({ geo: new THREE.TorusGeometry(0.0055, 0.0014, 3, 6),
                pos: [-hw + 0.004, sp.h - 0.008, 0], rot: [0, Math.PI / 2, 0] }); // 링
    g.add(new THREE.Mesh(geoBatch(back), dark));

    // ── 3. 코너 나사 4 + USB-C 포트 + 중간 이음새 ─────────────────────────
    const det = [];
    for (const [sx, sy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
        det.push({ geo: new THREE.CylinderGeometry(0.0028, 0.0028, 0.002, 5),
                   pos: [sx * (hw - 0.011), hh + sy * (hh - 0.010), BD / 2 - 0.0005],
                   rot: [Math.PI / 2, 0, 0] });
    }
    det.push({ geo: new THREE.BoxGeometry(0.010, 0.004, 0.003),
               pos: [0, 0.008, BD / 2 - 0.0008] });                          // USB-C
    det.push({ geo: new THREE.BoxGeometry(sp.w * 0.92, 0.0015, 0.0016),
               pos: [0, sp.h * 0.30, BD / 2 - 0.0004] });                     // 이음새
    g.add(new THREE.Mesh(geoBatch(det), dark));

    // ── 4. 바닥 1/4" 소켓 ─────────────────────────────────────────────────
    const socket = new THREE.Mesh(new THREE.CylinderGeometry(0.0058, 0.0058, 0.005, 8), dark);
    socket.position.set(0, 0.0025, 0);
    g.add(socket);

    return g;
}

// ── pavoTubeII6c — NANLITE PavoTube II 6C (가로 튜브, +Z 발광) → LIT-007/008 ──
//   (출처: LIT-008_PavoTubeII6C/LIT-008_threejs.js, 제품명 기준 매핑)
function ptRoundedRect(hw, hh, r) {
    const s = new THREE.Shape();
    s.moveTo(-hw + r, -hh);
    s.lineTo(hw - r, -hh); s.quadraticCurveTo(hw, -hh, hw, -hh + r);
    s.lineTo(hw, hh - r);  s.quadraticCurveTo(hw, hh, hw - r, hh);
    s.lineTo(-hw + r, hh); s.quadraticCurveTo(-hw, hh, -hw, hh - r);
    s.lineTo(-hw, -hh + r); s.quadraticCurveTo(-hw, -hh, -hw + r, -hh);
    return s;
}
function pavoTubeII6c(sp) {
    const g = new THREE.Group();
    const L = sp.len || sp.w, HL = L / 2, HW = sp.h / 2, HD = sp.d / 2;
    const alu = M.aluDk(), knobM = M.knob(), body = M.black();
    const blue = mat(0x1f8fd0, { roughness: 0.40, metalness: 0.20 });
    const box = (w, h, d, x, y, z) => ({ geo: new THREE.BoxGeometry(w, h, d), pos: [x, y, z] });

    const shellGeo = new THREE.ExtrudeGeometry(
        ptRoundedRect(HW, HD, 0.007), { depth: L, bevelEnabled: false, curveSegments: 2 });
    shellGeo.rotateY(Math.PI / 2); shellGeo.translate(-HL, 0, 0);
    g.add(new THREE.Mesh(shellGeo, alu));

    const dw = sp.diffuser || 0.03;
    const diff = new THREE.Mesh(new THREE.BoxGeometry(L - 0.016, dw, 0.004), M.diff());
    diff.position.set(0, 0, HD - 0.002); g.add(diff);
    const face = new THREE.Mesh(new THREE.PlaneGeometry(L - 0.020, dw - 0.003), M.diff());
    face.position.set(0, 0, HD - 0.0002);
    markEmitter(face, { coneDeg: sp.beam || 180, softness: 0.7, shape: 'tube', size: L - 0.020 });
    g.add(face);

    const caps = [];
    for (const s of [-1, 1]) {
        caps.push(box(0.008, sp.h, sp.d, s * (HL - 0.004), 0, 0));
        caps.push({ geo: new THREE.CylinderGeometry(0.0055, 0.0055, 0.005, 10),
                    pos: [s * (HL - 0.0026), 0, 0], rot: [0, 0, Math.PI / 2] });
    }
    g.add(new THREE.Mesh(geoBatch(caps), knobM));

    const ctrl = [];
    ctrl.push(box(0.062, 0.026, 0.003, -0.070, 0, -HD + 0.0015));
    for (let i = 0; i < 4; i++) ctrl.push(box(0.007, 0.007, 0.003, 0.010 + i * 0.013, 0, -HD + 0.0015));
    ctrl.push(box(0.010, 0.005, 0.003, 0.080, 0, -HD + 0.0015));
    g.add(new THREE.Mesh(geoBatch(ctrl), body));

    const line = [];
    for (const s of [-1, 1]) line.push(box(L - 0.020, 0.003, 0.002, 0, s * (HW - 0.004), HD - 0.002));
    g.add(new THREE.Mesh(geoBatch(line), blue));
    return g;
}

// ── djiRs4Pro — DJI RS 4 Pro 짐벌 (그립 바닥 원점, plate=[x,y,z] 카메라 자리) → GIM-001 ──
//   (출처: GMB-001_RS4Pro/GMB-001_threejs.js, 제품명 기준 매핑)
function gmRoundedRect(hw, hh, r) {
    const s = new THREE.Shape();
    s.moveTo(-hw + r, -hh);
    s.lineTo(hw - r, -hh); s.quadraticCurveTo(hw, -hh, hw, -hh + r);
    s.lineTo(hw, hh - r);  s.quadraticCurveTo(hw, hh, hw - r, hh);
    s.lineTo(-hw + r, hh); s.quadraticCurveTo(-hw, hh, -hw, hh - r);
    s.lineTo(-hw, -hh + r); s.quadraticCurveTo(-hw, -hh, -hw + r, -hh);
    return s;
}
function gmPivot(parent, [px, py, pz], apply) {
    const outer = new THREE.Group(); outer.position.set(px, py, pz); apply(outer);
    const inner = new THREE.Group(); inner.position.set(-px, -py, -pz);
    outer.add(inner); parent.add(outer); return inner;
}
function djiRs4Pro(sp) {
    const g = new THREE.Group();
    const D = THREE.MathUtils.degToRad, zc = sp.zCol;
    const [tx, ty, tz] = sp.tiltPos, [px, py, pz] = sp.plate;
    const body = M.black(), alu = M.aluDk(), knobM = M.knob();
    const carbon = mat(0x1b1e23, { roughness: 0.48, metalness: 0.35 });
    const motor = mat(0x2a2e34, { roughness: 0.44, metalness: 0.50 });
    const plate = mat(0x3a4046, { roughness: 0.40, metalness: 0.60 });
    const red = mat(0xb92330, { roughness: 0.45, metalness: 0.15 });
    const box = (w, h, d, x, y, z) => ({ geo: new THREE.BoxGeometry(w, h, d), pos: [x, y, z] });
    const cylY = (r, len, x, y, z, seg = 12) => ({ geo: new THREE.CylinderGeometry(r, r, len, seg), pos: [x, y, z] });
    const cylX = (r, len, x, y, z, seg = 14) => ({ geo: new THREE.CylinderGeometry(r, r, len, seg), pos: [x, y, z], rot: [0, 0, Math.PI / 2] });
    const cylZ = (r, len, x, y, z, seg = 14) => ({ geo: new THREE.CylinderGeometry(r, r, len, seg), pos: [x, y, z], rot: [Math.PI / 2, 0, 0] });
    const bag = () => ({ body: [], alu: [], carbon: [], red: [], knob: [], motor: [], plate: [] });
    const PAN = bag(), ROLL = bag(), TILT = bag();

    const gripGeo = new THREE.ExtrudeGeometry(gmRoundedRect(sp.gripW / 2, sp.gripD / 2, 0.011),
        { depth: sp.gripH, bevelEnabled: false, curveSegments: 2 });
    gripGeo.rotateX(-Math.PI / 2); gripGeo.translate(0, 0, zc);
    g.add(new THREE.Mesh(gripGeo, body));
    g.add(new THREE.Mesh(geoBatch([
        cylY(0.023, 0.010, 0, 0.120, zc, 12),
        box(0.030, 0.008, 0.012, 0, 0.062, zc + 0.021),
        cylY(0.0095, 0.006, 0, 0.003, zc, 10),
    ]), knobM));

    const pan = gmPivot(g, [0, sp.yPan, zc], o => { o.rotation.y = D(sp.pan || 0); });
    PAN.motor.push(cylY(0.026, 0.040, 0, sp.yPan, zc));
    PAN.motor.push(cylY(0.021, 0.008, 0, sp.yPan + 0.024, zc, 12));
    PAN.carbon.push(box(0.030, 0.090, 0.026, 0, 0.207, zc));
    PAN.body.push(box(0.056, 0.066, 0.022, 0, 0.203, zc + 0.024));
    PAN.knob.push(cylZ(0.007, 0.006, 0, 0.176, zc + 0.036, 10));
    for (const x of [-0.018, 0.018]) PAN.knob.push(box(0.012, 0.007, 0.004, x, 0.176, zc + 0.036));
    PAN.red.push(box(0.056, 0.004, 0.003, 0, 0.170, zc + 0.0245));
    PAN.motor.push(cylZ(0.031, 0.058, 0, sp.yRoll, zc));
    PAN.motor.push(cylZ(0.026, 0.008, 0, sp.yRoll, zc - 0.0339, 12));
    PAN.body.push(cylZ(0.019, 0.004, 0, sp.yRoll, zc + 0.030, 12));
    const scr = new THREE.Mesh(new THREE.PlaneGeometry(0.044, 0.032), mat(0x0d1116, { roughness: 0.10, metalness: 0.05 }));
    scr.position.set(0, 0.209, zc + 0.0352); pan.add(scr);

    const roll = gmPivot(pan, [0, sp.yRoll, zc], o => { o.rotation.z = D(sp.roll || 0); });
    ROLL.carbon.push(rod([0.010, sp.yRoll + 0.024, zc], [0.028, 0.366, zc], 0.011, 8));
    ROLL.carbon.push(rod([0.028, 0.366, zc], [tx - 0.020, ty, tz], 0.011, 8));
    ROLL.motor.push(cylX(0.032, 0.054, tx, ty, tz));
    ROLL.body.push(cylX(0.019, 0.004, tx + 0.026, ty, tz, 12));
    ROLL.red.push(cylX(0.0325, 0.007, tx + 0.020, ty, tz, 14));

    const tilt = gmPivot(roll, [tx, ty, tz], o => { o.rotation.x = -D(sp.tilt || 0); });
    TILT.carbon.push(box(0.215, 0.014, 0.056, -0.0598, 0.373, pz - 0.029));
    TILT.carbon.push(box(0.030, 0.030, 0.050, 0.036, 0.373, pz - 0.029));
    TILT.plate.push(box(0.052, 0.012, 0.150, px, py - 0.006, pz));
    TILT.plate.push(box(0.062, 0.008, 0.034, px, py - 0.016, pz - 0.030));
    TILT.knob.push(cylX(0.011, 0.030, px + 0.040, py - 0.014, pz - 0.030, 10));
    TILT.knob.push(box(0.012, 0.005, 0.140, px - 0.029, py - 0.002, pz));

    const MATS = { body, alu, carbon, red, knob: knobM, motor, plate };
    for (const [target, set] of [[pan, PAN], [roll, ROLL], [tilt, TILT]])
        for (const k of Object.keys(set)) if (set[k].length) target.add(new THREE.Mesh(geoBatch(set[k]), MATS[k]));
    return g;
}

// ── nanliteFc500c — NANLITE FC-500C COB (요크·스피곳 포함) → Forza 500 (LIT-001/002) ──
//   (출처: LIT-007_FC-500C/LIT-007_threejs.js, 사용자 지정: Forza 500에 적용)
function nanliteFc500c(sp) {
    const g = new THREE.Group();
    const HW = sp.bodyW / 2, HH = sp.h / 2, zF = sp.zFront, zB = sp.zBack;
    const shell = M.black(), alu = M.aluDk(), knobM = M.knob();
    const grayTop = mat(0x70767d, { roughness: 0.52, metalness: 0.40 });
    const blue = mat(0x1f8fd0, { roughness: 0.40, metalness: 0.20 });
    const box = (w, h, d, x, y, z) => ({ geo: new THREE.BoxGeometry(w, h, d), pos: [x, y, z] });
    const cylX = (r, len, x, y, z, seg = 14) => ({ geo: new THREE.CylinderGeometry(r, r, len, seg), pos: [x, y, z], rot: [0, 0, Math.PI / 2] });
    const cylZ = (r, len, x, y, z, seg = 20) => ({ geo: new THREE.CylinderGeometry(r, r, len, seg), pos: [x, y, z], rot: [Math.PI / 2, 0, 0] });
    const yTop = HH - 0.017, zBody = zB + 0.021, zPlate = 0.093;

    const zStep = 0.030, frontW = sp.bodyW - 0.022;
    g.add(new THREE.Mesh(geoBatch([
        box(sp.bodyW, yTop + HH, zStep - zBody, 0, (yTop - HH) / 2, (zBody + zStep) / 2),
        box(frontW, yTop + HH - 0.006, zPlate + 0.005 - zStep, 0, (yTop - HH) / 2 + 0.003, (zStep + zPlate + 0.005) / 2),
        box(sp.bodyW + 0.004, 0.112, 0.010, 0, -0.004, zBody - 0.004),
    ]), shell));
    const topL = zStep - zB;
    g.add(new THREE.Mesh(geoBatch([
        box(sp.bodyW + 0.006, 0.017, topL, 0, yTop + 0.0085, zB + topL / 2),
        box(frontW + 0.006, 0.017, 0.110 - zStep, 0, yTop + 0.0085, (zStep + 0.110) / 2),
    ]), grayTop));
    const blueParts = [];
    for (const s of [-1, 1]) {
        blueParts.push(box(0.004, 0.007, topL * 0.82, s * (HW + 0.0035), yTop - 0.005, zB + topL * 0.52));
        blueParts.push(cylX(0.030, 0.006, s * (HW + 0.005), 0, 0, 16));
    }
    g.add(new THREE.Mesh(geoBatch(blueParts), blue));
    const vent = [];
    vent.push(box(sp.bodyW - 0.030, 0.004, 0.200, 0, -HH + 0.0035, zBody + 0.115));
    for (let i = 0; i < 3; i++) vent.push(box(sp.bodyW - 0.036, 0.006, 0.005, 0, 0.052 - i * 0.011, zBody - 0.008));
    g.add(new THREE.Mesh(geoBatch(vent), alu));
    const ringR = 0.049;
    const tubeZ = (r, len, z, seg = 20) => ({ geo: new THREE.CylinderGeometry(r, r, len, seg, 1, true), pos: [0, 0, z], rot: [Math.PI / 2, 0, 0] });
    g.add(new THREE.Mesh(geoBatch([
        tubeZ(0.0525, 0.056, zF - 0.028), tubeZ(0.0555, 0.012, zF - 0.006),
        cylZ(0.0525, 0.005, 0, 0, zF - 0.0535, 20),
    ]), alu));
    const floor = new THREE.Mesh(new THREE.CircleGeometry(ringR, 20), shell);
    floor.position.z = zPlate + 0.014; g.add(floor);
    const ring = new THREE.Mesh(new THREE.CircleGeometry(0.030, 20), M.diff());
    ring.position.z = zPlate + 0.0150; g.add(ring);
    const cob = new THREE.Mesh(new THREE.CircleGeometry(0.021, 20),
        mat(0xf2dd7a, { roughness: 0.85, metalness: 0, emissive: 0xffe9a8, emissiveIntensity: 1.0 }));
    cob.position.z = zPlate + 0.0156;
    markEmitter(cob, { coneDeg: sp.beam || 65, softness: 0, shape: 'disc', size: 0.042 });
    g.add(cob);
    const zP = zBody - 0.009, ctrl = [];
    ctrl.push(cylX(0.014, 0.012, -0.046, -0.028, zP + 0.004, 12));
    for (const x of [-0.006, 0.014]) ctrl.push(box(0.014, 0.008, 0.005, x, -0.030, zP));
    g.add(new THREE.Mesh(geoBatch(ctrl), knobM));
    const knobBlue = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.012, 12), blue);
    knobBlue.rotation.z = Math.PI / 2; knobBlue.position.set(0.046, -0.028, zP + 0.004); g.add(knobBlue);
    const lcd = new THREE.Mesh(new THREE.PlaneGeometry(0.056, 0.026), mat(0x0e1319, { roughness: 0.10, metalness: 0.05 }));
    lcd.position.set(0, -0.004, zP - 0.0012); lcd.rotation.y = Math.PI; g.add(lcd);
    const ax = HW + 0.0165, yBot = -0.163;
    g.add(new THREE.Mesh(geoBatch([
        box(0.011, 0.212, 0.062, -ax, yBot / 2 + 0.041, 0),
        box(0.011, 0.212, 0.062, ax, yBot / 2 + 0.041, 0),
        box(ax * 2 + 0.011, 0.016, 0.062, 0, yBot, 0),
        { geo: new THREE.CylinderGeometry(0.0145, 0.0145, sp.yokeDrop - 0.171, 12), pos: [0, -(0.171 + sp.yokeDrop) / 2, 0] },
    ]), alu));
    const knobs = [];
    for (const s of [-1, 1]) knobs.push(cylX(0.020, 0.020, s * (sp.w / 2 - 0.010), 0, 0, 14));
    knobs.push({ geo: new THREE.CylinderGeometry(0.012, 0.012, 0.022, 10), pos: [-0.026, -0.163, 0], rot: [0, 0, Math.PI / 2] });
    g.add(new THREE.Mesh(geoBatch(knobs), knobM));
    return g;
}

// ── insta360X3 — INSTA360 X3 360캠 (바닥면 원점) → CAM-006 ──
//   (출처: CAM-002_X3/CAM-002_threejs.js, 사용자 지정: 새 카메라로 추가)
function x3RoundedRect(hw, hh, r) {
    const s = new THREE.Shape();
    s.moveTo(-hw + r, -hh);
    s.lineTo(hw - r, -hh); s.quadraticCurveTo(hw, -hh, hw, -hh + r);
    s.lineTo(hw, hh - r);  s.quadraticCurveTo(hw, hh, hw - r, hh);
    s.lineTo(-hw + r, hh); s.quadraticCurveTo(-hw, hh, -hw, hh - r);
    s.lineTo(-hw, -hh + r); s.quadraticCurveTo(-hw, -hh, -hw + r, -hh);
    return s;
}
function insta360X3(sp) {
    const g = new THREE.Group();
    const W = sp.w, H = sp.h, D = sp.d, BD = sp.bodyD;
    const zF = BD / 2;
    const body = M.black(), alu = M.aluDk(), knobM = M.knob();
    const geo = new THREE.ExtrudeGeometry(x3RoundedRect(W / 2, BD / 2, sp.cornerR),
        { depth: H, bevelEnabled: false, curveSegments: 4 });
    geo.rotateX(-Math.PI / 2); g.add(new THREE.Mesh(geo, body));
    const R = sp.lensDomeR, phi = THREE.MathUtils.degToRad(sp.lensCapDeg), rimR = R * Math.sin(phi);
    const glass = mat(0x141a20, { roughness: 0.06, metalness: 0.20 });
    const domes = [], bezels = [];
    for (const s of [1, -1]) {
        domes.push({ geo: new THREE.SphereGeometry(R, 12, 4, 0, Math.PI * 2, 0, phi),
            pos: [0, sp.lensY, s * (D / 2 - R)], rot: [s > 0 ? Math.PI / 2 : -Math.PI / 2, 0, 0] });
        bezels.push({ geo: new THREE.CylinderGeometry(rimR + 0.0018, rimR + 0.0018, 0.003, 14),
            pos: [0, sp.lensY, s * (BD / 2 - 0.0012)], rot: [Math.PI / 2, 0, 0] });
    }
    g.add(new THREE.Mesh(geoBatch(domes), glass));
    g.add(new THREE.Mesh(geoBatch(bezels), alu));
    const screen = new THREE.Mesh(new THREE.PlaneGeometry(sp.screenW, sp.screenH), mat(0x10151b, { roughness: 0.10, metalness: 0.05 }));
    screen.position.set(0, 0.040, zF + 0.0006); g.add(screen);
    const btn = [];
    btn.push({ geo: new THREE.CylinderGeometry(0.0055, 0.0055, 0.0022, 10), pos: [-W / 2 - 0.0002, 0.086, 0], rot: [0, 0, Math.PI / 2] });
    btn.push({ geo: new THREE.CylinderGeometry(0.0040, 0.0040, 0.0020, 10), pos: [-W / 2 - 0.0002, 0.066, 0], rot: [0, 0, Math.PI / 2] });
    btn.push({ geo: new THREE.BoxGeometry(0.010, 0.004, 0.002), pos: [0, 0.011, zF + 0.0005] });
    btn.push({ geo: new THREE.CylinderGeometry(0.0015, 0.0015, 0.002, 6), pos: [0, H - 0.004, zF - 0.004] });
    g.add(new THREE.Mesh(geoBatch(btn), knobM));
    const socket = new THREE.Mesh(new THREE.CylinderGeometry(0.0058, 0.0058, 0.006, 10), alu);
    socket.position.set(0, 0.003, 0); g.add(socket);
    const door = new THREE.Mesh(new THREE.BoxGeometry(0.0016, 0.052, 0.021), knobM);
    door.position.set(W / 2 - 0.0008, 0.036, 0); g.add(door);
    return g;
}

// ── SPECS 등록 (실제 자산 id) — 제조사 공식 치수 ─────────────────────────────
// NANLITE Forza 60B / 60B Ⅱ : 본체 247×134×87mm
[['LIT-005'], ['LIT-006']].forEach(([id]) => {
    SPECS[id] = { w: 0.134, h: 0.087, d: 0.247, bodyW: 0.090,
        zFront: 0.110, zBack: -0.137, yokeDrop: 0.166, beam: 120, src: 'spec' };
});
// Godox AD300Pro (Ⅱ 본체 공용) : 186.9×100.1×89.9mm
SPECS['LIT-009'] = { w: 0.1001, h: 0.0899, d: 0.1869, axisY: 0.064,
    zFront: 0.102, zBack: -0.085, yokeDrop: 0.048, beam: 110, src: 'spec' };
// NANLITE PJ-FMM 프로젝션 어태치먼트(+36° 렌즈) → MOD-004
SPECS['MOD-004'] = { w: 0.160, h: 0.235, d: 0.215, yTop: 0.081, yBot: -0.154,
    goboD: 0.078, goboFrameD: 0.066, lensRingD: 0.132,
    barrelD: 0.117, len: 0.150, beam: 36, src: 'spec' };
// NANLITE FL-11 프레넬 렌즈(+반도어) → MOD-005
SPECS['MOD-005'] = { w: 0.110, h: 0.110, d: 0.135, outerD: 0.110, lensD: 0.085,
    beam: 30, ringD: 0.114, bigW: 0.108, bigL: 0.125, smallW: 0.088, smallL: 0.105,
    open: 0.55, src: 'spec' };
// Teris TSN6CF-Q PLUS 삼각대(+헤드) → TRP-003
SPECS['TRP-003'] = { w: 1.05, h: 1.30, d: 1.05, src: 'spec',
    hBowl: 1.145, hBowlMin: 0.50, hBowlMax: 1.59, spreadD: 1.05, ball: 0.075,
    stages: 2, tubeUp: 0.025, tubeLo: 0.022, twinGap: 0.027, hingeR: 0.058,
    legMin: 0.78, legMax: 1.60,
    yBowl: 0.055, yPlate: 0.100, plateL: 0.132, plateW: 0.062, barLen: 0.400 };
// VALENS PRO-403A A스탠드 → 모든 A스탠드(STD-A 4개) · 작은 A스탠드(STD-AS 2개) · T스탠드(STD-T)
function _aStandSpec(scale) {
    return { w: 1.28 * scale, h: 2.00 * scale, d: 1.28 * scale, src: 'spec',
        hMin: 1.22 * scale, hMax: 3.00 * scale, spreadD: 1.28 * scale,
        tubeA: 0.025, tubeB: 0.030, tubeC: 0.035, legTube: 0.022,
        yHub: 0.37 * scale, spigotD: 0.016, spigotL: 0.070 };
}
['STD-A-001', 'STD-A-002', 'STD-A-003', 'STD-A-004', 'STD-T-001'].forEach(id => { SPECS[id] = _aStandSpec(1.0); });
// 작은 A스탠드는 축소 비율
['STD-AS-001', 'STD-AS-002'].forEach(id => { SPECS[id] = _aStandSpec(0.62); });
// VALENS PRO-40T (진짜 C스탠드형 크롬 스탠드) → 실제 C스탠드 STD-C-001~003
['STD-C-001', 'STD-C-002', 'STD-C-003'].forEach(id => {
    SPECS[id] = { w: 1.04, h: 2.20, d: 1.04, src: 'spec',
        hMin: 1.45, hMax: 3.23, spreadD: 1.04,
        tubeA: 0.025, tubeB: 0.030, tubeC: 0.035, legTube: 0.019, fold: 0,
        legArm: 0.415, legTip: 0.155, bendDeg: 52, legHubR: 0.030,
        yBase: 0.30, legY: [0.130, 0.185, 0.240], spigotD: 0.016, spigotL: 0.070 };
});

// NANLITE PavoSlim 240B 패널 → LIT-003
SPECS['LIT-003'] = { w: 0.6087, h: 0.6021, d: 0.0286, src: 'spec',
    t: 0.0286, border: 0.016, zBack: 0.048, fold: 0, beam: 60 };
// NANLITE MixPanel 150 패널 → LIT-004
// 제조사 실측: 본체 426×370×82mm (마운트 브래킷 포함). 긴 변(가로 0.426)이 수평.
SPECS['LIT-004'] = { w: 0.426, h: 0.370, d: 0.082, src: 'spec',
    border: 0.022, yokeGap: 0.014, yokeDrop: 0.300, beam: 115 };
// GODOX V1 라운드헤드 플래시 → LIT-010
SPECS['LIT-010'] = { w: 0.076, h: 0.197, d: 0.093, src: 'spec',
    headD: 0.076, headLen: 0.080, bodyD: 0.046, yBodyTop: 0.121,
    yPivot: 0.128, zPivot: -0.010, zHeadFront: 0.0565, tilt: 0, swivel: 0, beam: 60 };
// NANLITE NANLINK BOX WS-TB-1 무선 트랜스미터 → MOD-006
SPECS['MOD-006'] = { w: 0.107, h: 0.073, d: 0.044, src: 'spec',
    bodyD: 0.038, chamX: 0.022, chamY: 0.014 };

// NANLITE PavoTube II 6C (10인치 튜브) → LIT-007/008. 250×38×38mm.
['LIT-007', 'LIT-008'].forEach(id => {
    SPECS[id] = { w: 0.250, h: 0.038, d: 0.038, len: 0.250, diffuser: 0.030, beam: 180, src: 'spec' };
});
// DJI RS 4 Pro 짐벌 → GIM-001 (그립 바닥 원점, plate 상면이 카메라 자리)
SPECS['GIM-001'] = { w: 0.2678, h: 0.415, d: 0.2019, src: 'spec', kind: 'gimbal',
    pan: 0, roll: 0, tilt: 0, zCol: -0.050, gripW: 0.044, gripD: 0.040, gripH: 0.115,
    yPan: 0.142, yRoll: 0.270, tiltPos: [0.074, 0.383, -0.030], plate: [-0.095, 0.3915, 0.039] };
// NANLITE FC-500C COB → Forza 500 (LIT-001/002) [사용자 지정 매핑]
['LIT-001', 'LIT-002'].forEach(id => {
    SPECS[id] = { w: 0.2464, h: 0.149, d: 0.3732, bodyW: 0.170, src: 'spec',
        zFront: 0.152, zBack: -0.2212, yokeDrop: 0.245, tilt: 0, beam: 65 };
});
// INSTA360 X3 360캠 → CAM-006 (신규 자산)
SPECS['CAM-006'] = { w: 0.046, h: 0.114, d: 0.0331, bodyD: 0.0240, src: 'spec', cornerR: 0.011,
    lensDomeR: 0.0215, lensCapDeg: 38, lensY: 0.0905, screenW: 0.03416, screenH: 0.04727 };
// PavoTube 소프트박스(긴 사각) → MOD-008 / 프레임 원단 디퓨저·플랙(납작 프레임) → MOD-009
SPECS['MOD-008'] = { w: 0.16, h: 0.62, d: 0.16, kind: 'boxSoft', src: 'est' };
SPECS['MOD-009'] = { w: 0.75, h: 0.90, d: 0.03, kind: 'flag', src: 'est' };

// VALENS VL-3000G 3.2m 이동 배경용 크로스바 → ACC-006 (지름·무게는 실측 추정)
SPECS['ACC-006'] = { w: 3.20, h: 0.05, d: 0.05, src: 'est',
    sections: 4, secL: 0.80, len: 3.20,
    tubeD: 0.025, ferruleD: 0.021, ferruleL: 0.070,
    yDrop: 0.028, spread: 0 };
// STD-AS-001/002 + ACC-006 이 한 씬에 모이면 이 리그로 대체(배경지 제외)
SPECS['ASSY-BGS-001'] = { kind: 'assembly', parts: ['STD-AS-001', 'STD-AS-002', 'ACC-006'],
    h: 2.30, span: 2.90, sections: 4 };

// 서브 부품 스펙 (자산 아님 — 빌더에 넘긴다)
const SPEC_FS60B_REFL = { neckD: 0.077, apertureD: 0.115, depth: 0.120, beam: 45 };

// ── 판별 predicate ──────────────────────────────────────────────────────────
function isForza60B(eq) { return eq && (['LIT-005','LIT-006'].includes(eq.id) || /forza\s*60|fs-?60/i.test(eq.product || '')); }
function isAD300Pro(eq) { return eq && (eq.id === 'LIT-009' || /ad300\s*pro/i.test(eq.product || '')); }
function isFresnelMod(eq) { return eq && (eq.id === 'MOD-005' || /fresnel|프레넬|fl-?11/i.test(eq.product || '')); }
// A스탠드 계열(A·작은A·T) = PRO-403A 모델
function isAStandPro(eq) { return eq && (/^STD-A-/.test(eq.id) || /^STD-AS-/.test(eq.id) || /^STD-T-/.test(eq.id) || /pro-?403a/i.test(eq.product || '')); }
// C스탠드 = PRO-40T 모델
function isCStandPro(eq) { return eq && (/^STD-C-/.test(eq.id) || /pro-?40t/i.test(eq.product || '')); }
function isTerisTripod(eq) { return eq && (eq.id === 'TRP-003' || /tsn6|teris/i.test(eq.product || '')); }
function isPavoSlim(eq) { return eq && (eq.id === 'LIT-003' || /pavoslim/i.test(eq.product || '')); }
function isMixPanel(eq) { return eq && (eq.id === 'LIT-004' || /mixpanel/i.test(eq.product || '')); }
function isV1Flash(eq) { return eq && (eq.id === 'LIT-010' || /godox.*v1|고독스\s*v1|\bV1\b/i.test(eq.product || '')); }
function isNanlink(eq) { return eq && (eq.id === 'MOD-006' || /nanlink|ws-?tb/i.test(eq.product || '')); }
// PavoTube 튜브 조명(PavoSlim 과 구분) → LIT-007/008
function isPavoTube(eq) { return eq && (['LIT-007','LIT-008'].includes(eq.id) || /pavotube/i.test(eq.product || '')); }
// INSTA360 X3 360캠(제품명 우선) → CAM-006 또는 이름 매칭
function isInsta360(eq) { return eq && (eq.id === 'CAM-006' || /insta\s*?360|\bx3\b/i.test(eq.product || '')); }

