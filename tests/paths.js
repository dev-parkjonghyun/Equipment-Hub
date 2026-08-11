// 테스트가 쓰는 경로를 한곳에서 관리합니다.
const path = require('path');
const ROOT = path.join(__dirname, '..');
module.exports = {
  ROOT,
  APP: path.join(ROOT, 'dist', 'index.html'),        // 빌드 결과
  SUPA: (f) => path.join(ROOT, 'supabase', f),       // supabase/… 파일
};
