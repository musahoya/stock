# 일목균형표 자동 분석 시스템

**차트의 추상성을 배제하고 숫자 기반의 객관적 의사결정을 지원하는 일목균형표 분석 시스템**

## 📋 프로젝트 개요

이 프로젝트는 일목균형표(Ichimoku Kinko Hyo) 지표를 기반으로 주식, 암호화폐 등을 자동으로 분석하여 체크리스트 기반의 객관적 점수를 산출하고, 강도 순으로 정렬된 대시보드를 제공합니다.

### 주요 기능

- ✅ **다중 시장 지원**: 미국 주식, 한국 주식, 암호화폐
- ✅ **자동 데이터 수집**: yfinance, pykrx, ccxt를 통한 실시간 데이터
- ✅ **일목균형표 계산**: 전환선, 기준선, 선행스팬, 후행스팬, 구름
- ✅ **체크리스트 점수 시스템**: 48점 만점의 객관적 점수 (15개 항목)
- ✅ **등급 시스템**: A~F 등급 자동 산정
- ✅ **대화형 대시보드**: Streamlit 기반 웹 인터페이스
- ✅ **커맨드라인 도구**: 빠른 배치 분석

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv ichimoku_env

# 가상환경 활성화
# Windows
ichimoku_env\Scripts\activate
# Linux/Mac
source ichimoku_env/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 대시보드 실행

```bash
streamlit run ichimoku_analyzer/dashboard/app.py
```

브라우저에서 자동으로 열립니다 (기본: http://localhost:8501)

### 3. 커맨드라인 실행

```bash
# 기본 실행 (미국 주식)
python main.py

# 한국 주식 분석
python main.py --market kr

# 특정 종목 분석
python main.py --symbols AAPL MSFT GOOGL

# 결과 CSV 저장
python main.py --output results.csv

# 상위 10개만 표시
python main.py --top 10

# 최소 점수 30점 이상만 필터
python main.py --min-score 30
```

## 📊 체크리스트 항목 (총 48점)

### 기본 배치 (9점)
- 후행스팬이 캔들 위 (3점)
- 현재 구름 양운 (3점)
- 앞쪽 구름 양운 (3점)

### 가격 위치 (3점)
- 주가가 구름 위 (3점)

### 호전 관련 (9점)
- 호전 발생 (3점)
- 호전 후 기준선 하회 없음 (3점)
- 기준선 상승/수평 (3점)

### 지지 확인 (5점)
- 전환선 지지 (2점)
- 기준선 지지 (3점)

### 후행+호전 동시 (6점)
- 후행스팬 상향 돌파 (3점)
- 후행+호전 동시 발생 (3점)

### 구름 돌파 (5점)
- 구름 상향 돌파 (3점)
- 구름 돌파 후 상단 지지 (2점)

### 특수 패턴 (6점)
- 얇은 구름 상향 돌파 (2점)
- 음→양 교차 바닥 (2점)
- 협착 후 기준선 지지 (2점)

## 📈 등급 기준

| 등급 | 점수 범위 | 판정 |
|------|-----------|------|
| A | 70% 이상 (34점+) | 강력 매수 |
| B | 50-69% (24-33점) | 적극 매수 |
| C | 35-49% (17-23점) | 신중 매수 |
| D | 20-34% (10-16점) | 관망 |
| F | 20% 미만 (10점 미만) | 매수 부적절 |

## 🏗️ 프로젝트 구조

```
stock/
├── ichimoku_analyzer/
│   ├── config/
│   │   ├── settings.py              # 기본 설정
│   │   └── checklist_weights.py     # 체크리스트 가중치
│   ├── data/
│   │   ├── fetcher.py              # 데이터 수집 통합
│   │   ├── us_stocks.py            # 미국 주식
│   │   ├── kr_stocks.py            # 한국 주식
│   │   └── crypto.py               # 암호화폐
│   ├── indicators/
│   │   ├── ichimoku.py             # 일목균형표 계산
│   │   └── signals.py              # 매매 신호
│   ├── scoring/
│   │   ├── checklist.py            # 체크리스트 점수
│   │   └── ranker.py               # 순위 산정
│   └── dashboard/
│       ├── app.py                  # Streamlit 메인
│       └── components.py           # UI 컴포넌트
├── main.py                         # CLI 실행 스크립트
├── requirements.txt
└── README.md
```

## 🔧 설정

### 환경 변수 (.env 파일)

```bash
# Telegram 알림 (선택사항)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# 캐시 설정
CACHE_MAX_AGE_HOURS=1

# 점수 임계값
HIGH_SCORE_THRESHOLD=35
```

### 일목균형표 파라미터 (config/settings.py)

```python
ICHIMOKU_PARAMS = {
    'tenkan_period': 9,      # 전환선
    'kijun_period': 26,      # 기준선
    'senkou_b_period': 52,   # 선행스팬B
    'displacement': 26       # 선행/후행 이동
}
```

## 📚 사용 예제

### Python 스크립트

```python
from ichimoku_analyzer.data.fetcher import DataFetcher
from ichimoku_analyzer.indicators.ichimoku import IchimokuCalculator
from ichimoku_analyzer.scoring.checklist import ChecklistScorer

# 데이터 수집
fetcher = DataFetcher()
df = fetcher.fetch('AAPL', market_type='us')

# 일목균형표 계산
calculator = IchimokuCalculator()
df_ichimoku = calculator.calculate_all(df)

# 점수 계산
scorer = ChecklistScorer()
score = scorer.calculate_score(df_ichimoku)

print(f"점수: {score['total_score']}/48")
print(f"등급: {score['grade']}")
```

## 🛠️ 개발 및 확장

### 새로운 데이터 소스 추가

`ichimoku_analyzer/data/` 디렉토리에 새로운 모듈 추가 후 `fetcher.py`에 통합

### 체크리스트 항목 수정

`ichimoku_analyzer/config/checklist_weights.py`에서 항목 추가/수정

### 대시보드 커스터마이징

`ichimoku_analyzer/dashboard/components.py`에서 UI 컴포넌트 수정

## 🐛 문제 해결

### 데이터 수집 오류

```bash
# yfinance 업데이트
pip install --upgrade yfinance

# pykrx 업데이트 (한국 주식)
pip install --upgrade pykrx
```

### 캐시 초기화

```bash
rm -rf cache/
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

버그 리포트, 기능 제안, Pull Request 환영합니다!

## 📧 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

---

**면책 조항**: 이 도구는 교육 및 연구 목적으로 제공됩니다. 투자 결정은 사용자 본인의 책임이며, 이 도구의 분석 결과에 대해 개발자는 어떠한 책임도 지지 않습니다.
