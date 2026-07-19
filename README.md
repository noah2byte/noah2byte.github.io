# 노아의 DevOps 블로그

[Jekyll](https://jekyllrb.com/) + [Chirpy 테마](https://github.com/cotes2020/jekyll-theme-chirpy) 기반으로 만든 개인 기술 블로그입니다. GitHub Pages로 정적 배포되며, GitHub Actions를 통해 주간 IT 뉴스 다이제스트를 자동으로 수집·게시하는 파이프라인이 추가되어 있습니다.

- 배포 주소: https://noah2byte.github.io

## 아키텍처

```
[글 작성 (_posts, _tabs)]              [주간 뉴스 자동 수집]
        |                                       |
        |                          .github/workflows/weekly-news.yml
        |                          (매주 월요일 00:00 UTC, cron)
        |                                       |
        |                          scripts/geeknews.py  ---> _weekly/geeknews-*.md
        |                          scripts/yozmit.py    ---> _weekly/yozmit-*.md  (continue-on-error)
        |                          scripts/update_weekly_yaml.py ---> _data/weekly.yml
        |                                       |
        |                          git commit & push (github-actions 계정)
        v                                       v
              .github/workflows/pages-deploy.yml
        (main 브랜치 push 또는 Weekly News 워크플로 완료 시 트리거)
                              |
                    bundle exec jekyll build (_site/)
                              |
                    html-proofer로 링크/HTML 검증
                              |
                 actions/deploy-pages -> GitHub Pages 배포
```

- **정적 사이트 생성**: Jekyll(Ruby)이 `_posts`, `_tabs`, `_weekly` 등의 Markdown 콘텐츠와 `_layouts`/`_includes`를 조합해 `_site/`에 정적 HTML을 빌드합니다.
- **테마**: `jekyll-theme-chirpy` 젬을 사용하며, 사이트 전역 설정은 `_config.yml`에서 관리합니다.
- **프런트엔드 자산**: `_javascript`(Rollup으로 번들링) + `_sass`(SCSS)가 `assets/js`, `assets/css`로 컴파일됩니다. 공용 정적 자산(`assets/lib`)은 [`chirpy-static-assets`](https://github.com/cotes2020/chirpy-static-assets) 저장소를 서브모듈로 참조합니다.
- **주간 뉴스 자동화**: `scripts/geeknews.py`가 GeekNews RSS를, `scripts/yozmit.py`가 요즘IT 사이트맵을 각각 파싱해 `_weekly/`에 Markdown 페이지를 생성합니다(요즘IT 수집은 대상 사이트가 종종 405를 반환해 워크플로에서 `continue-on-error`로 감싸져 있습니다). `scripts/update_weekly_yaml.py`가 그 목록을 `_data/weekly.yml`(`geeknews`/`yozmit` 두 키)로 인덱싱하면, `_includes/weekly-digest.html`이 이를 아코디언(`<details>`) 형태로 렌더링합니다.
- **카테고리 구조**: Chirpy 테마의 카테고리 기능은 기본적으로 2단계(`categories[0]`, `categories[1]`)까지만 다루지만, 이 블로그는 글의 `categories` front matter를 3단계(예: `[문제 상황 개선 사례, 천재교육, 모니터링 시스템 역추적기]`)로 씁니다. `_layouts/category.html`을 커스터마이징해서, 하위 카테고리가 있는 카테고리 페이지는 폴더 목록만 보여주고(예: `/categories/천재교육/` → "DevOps 플랫폼 개선", "모니터링 시스템 역추적기" 폴더), 더 내려갈 하위 카테고리가 없는 leaf 페이지에서만 실제 글 목록이 나오는 드릴다운 방식으로 동작합니다. `_tabs/improvements.md`("문제 상황 개선 사례")와 `_tabs/operations.md`("운영 이모저모")가 이 카테고리 트리의 최상위 진입점입니다.
- **CI/CD**: 커밋 메시지 검사(`commitlint.yml`), 주간 뉴스 수집(`weekly-news.yml`), 빌드/검증/배포(`pages-deploy.yml`) 세 개의 GitHub Actions 워크플로가 있습니다. `pages-deploy.yml`은 Jekyll 빌드만 수행하며 `npm run build`는 실행하지 않으므로, `_javascript`를 수정했다면 로컬에서 빌드해 `assets/js/dist` 산출물을 함께 커밋해야 배포에 반영됩니다.

## 디렉터리 구조

```
.
├── _config.yml            # Jekyll/Chirpy 사이트 전역 설정
├── _posts/                # 블로그 글 (YYYY-MM-DD-title.md)
├── _tabs/                 # 사이드바 탭 페이지: About, 경력 & 업무 히스토리, 아키텍쳐,
│                          # 문제 상황 개선 사례(카테고리 트리), 운영 이모저모(카테고리 트리), 게임
│                          # (Categories 탭은 hidden: true 로 사이드바에는 노출되지 않음)
├── _pages/                # 그 외 개별 페이지 (weekly 목록 등)
├── _weekly/                # 자동 생성되는 주간 뉴스 다이제스트 Markdown
├── _data/                 # YAML 데이터 (저자, 연락처, 다국어 문구, 주간 뉴스 인덱스, 게임 목록 등)
├── _layouts/               # 페이지 레이아웃 (post, page, home, category ...)
├── _includes/               # 레이아웃에 삽입되는 부분 템플릿 (헤더, 사이드바, 댓글, TOC 등)
├── _sass/                  # SCSS 스타일
├── _javascript/             # 클라이언트 JS 소스 (Rollup으로 assets/js/dist에 번들링)
├── _plugins/                # Jekyll 커스텀 플러그인 (Ruby 훅, 예: 마지막 수정일 계산)
├── assets/                 # 이미지, 컴파일된 CSS/JS, lib(서브모듈) 등 정적 자산
├── scripts/                # 주간 뉴스 크롤링/집계용 Python 스크립트
│   ├── geeknews.py          # GeekNews RSS -> _weekly/geeknews-*.md 생성
│   ├── yozmit.py            # 요즘IT 사이트맵 크롤링 -> _weekly/yozmit-*.md 생성 (405 응답 시 skip, 워크플로에서 continue-on-error)
│   └── update_weekly_yaml.py # _weekly/*.md 목록을 _data/weekly.yml(geeknews/yozmit)로 인덱싱
├── tools/                  # 저장소 관리용 셸 스크립트 (아래 "실행 방법" 참고)
├── .github/workflows/       # GitHub Actions 워크플로 정의
├── _site/                  # Jekyll 빌드 산출물 (생성 파일, 버전관리 대상 아님 권장)
├── Gemfile / Gemfile.lock  # Ruby(Jekyll) 의존성
└── package.json            # Node 의존성 (Rollup 빌드, Stylelint, commitlint)
```

## 실행 방법

### 요구 사항

- Ruby `3.2.2` (`.ruby-version` 참고), Bundler
- Node.js (Rollup/Stylelint용), npm

### 로컬 개발 서버 실행

```bash
bundle install
npm install

# JS/CSS 자산 빌드
npm run build

# 로컬 서버 기동 (0.0.0.0, --livereload)
bash tools/run
# 또는 직접: bundle exec jekyll s -H 0.0.0.0 -l
```

기본적으로 `http://127.0.0.1:4000` 에서 사이트를 확인할 수 있습니다.

### 프로덕션 빌드 및 검증

```bash
bash tools/test
# 내부적으로 `_config.yml`의 baseurl을 읽어
# JEKYLL_ENV=production bundle exec jekyll b -d _site 로 빌드 후
# html-proofer로 내부 링크/HTML을 검증합니다.
```

### JS 자산 watch 모드

```bash
npm run watch   # _javascript 변경 시 assets/js/dist 자동 재빌드
```

### 주간 뉴스 다이제스트 로컬 실행

```bash
pip install feedparser requests beautifulsoup4 lxml pyyaml python-dateutil

python scripts/geeknews.py          # _weekly/geeknews-<오늘날짜>.md 생성
python scripts/yozmit.py            # _weekly/yozmit-<오늘날짜>.md 생성 (대상 사이트가 405를 반환하면 실패할 수 있음)
python scripts/update_weekly_yaml.py # _data/weekly.yml 갱신
```

### 새 글 작성

`_posts/YYYY-MM-DD-title.md` 형식으로 파일을 추가하고 front matter(`layout: post`, `title`, `categories` 등)를 채웁니다. 사이드바 탭을 추가/수정하려면 `_tabs/*.md`의 front matter(`order`, `icon`, `permalink`)를 참고하세요.

`문제 상황 개선 사례`/`운영 이모저모` 트리에 들어갈 글은 `categories: [상위 탭 제목, 회사/조직명, 시리즈명]` 순서의 3단계로 작성해야 카테고리 드릴다운 페이지에서 올바르게 폴더로 묶입니다(위 "카테고리 구조" 참고). 마지막 단계(시리즈명)가 없으면 해당 회사/조직 페이지에서 폴더 없이 바로 글로 나옵니다.

### 게임 탭에 게임 추가

`_tabs/game.md`는 `_data/games.yml`을 순회하며 카드 그리드를 렌더링합니다. 새 게임을 추가하려면 `_tabs/game.md`를 수정할 필요 없이 `_data/games.yml`에 `title`/`description`/`url`/`category`/`icon` 항목만 추가하면 됩니다.

## 배포 파이프라인

| 워크플로 | 트리거 | 역할 |
| --- | --- | --- |
| `commitlint.yml` | PR 생성 시 | Conventional Commits 형식 커밋 메시지 검사 |
| `weekly-news.yml` | 매주 월요일 00:00 UTC, 수동 실행 | GeekNews RSS + 요즘IT 수집 → `_weekly/` 생성 → `_data/weekly.yml` 갱신 → `main`에 커밋/푸시 |
| `pages-deploy.yml` | `main` push, `weekly-news.yml` 완료, 수동 실행 | Jekyll 빌드 → html-proofer 검증 → GitHub Pages 배포 |

`main` 브랜치에 푸시(또는 주간 뉴스 자동 커밋)가 발생하면 자동으로 빌드·검증·배포까지 이어집니다.

## 기타 관리 스크립트 (`tools/`)

- `tools/init` — Chirpy Starter로 초기화할 때 사용하는 스크립트(예시 글 제거, 워크플로 정리 등). 이미 초기화된 저장소이므로 재실행 불필요.
- `tools/test` — 프로덕션 빌드 + html-proofer 검증.
- `tools/run` — 로컬 개발 서버 실행.
- `tools/release` — Chirpy 테마 자체를 젬으로 배포할 때 쓰는 스크립트(이 블로그 운영에는 사용하지 않음).
