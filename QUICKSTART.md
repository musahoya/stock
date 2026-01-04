# 빠른 시작 가이드

## 1분 만에 시작하기

### 1. 설치

```bash
# 1. 저장소 클론 (이미 완료되어 있다면 생략)
git clone <repository-url>
cd stock

# 2. 가상환경 생성 및 활성화
python -m venv ichimoku_env

# Windows
ichimoku_env\Scripts\activate

# Linux/Mac
source ichimoku_env/bin/activate

# 3. 패키지 설치
pip install -r requirements.txt
```

### 2. 대시보드 실행 (추천)

```bash
streamlit run ichimoku_analyzer/dashboard/app.py
```

브라우저가 자동으로 열립니다 (http://localhost:8501)

**대시보드 사용법:**
1. 왼쪽 사이드바에서 시장 선택 (미국/한국/크립토)
2. 분석할 종목 선택
3. "🚀 분석 시작" 버튼 클릭
4. 결과를 순위 테이블로 확인
5. 종목을 선택하여 상세 분석 보기

### 3. 커맨드라인 실행

```bash
# 기본 분석 (미국 주식 기본 종목)
python main.py

# 특정 종목 분석
python main.py --symbols AAPL MSFT GOOGL NVDA

# 한국 주식 분석
python main.py --market kr --symbols 005930 000660

# 결과를 CSV로 저장
python main.py --output my_analysis.csv

# 상위 10개만 보기
python main.py --top 10
```

### 4. Python 스크립트로 사용

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

# 결과 출력
print(f"종목: AAPL")
print(f"점수: {score['total_score']}/48")
print(f"등급: {score['grade']}")
```

### 5. 테스트 실행

```bash
# 시스템 테스트
python test_simple.py
```

## 주요 기능

### 📊 체크리스트 점수 시스템
- 15개 항목, 48점 만점
- 객관적 수치 기반 평가
- A~F 등급 자동 산정

### 📈 지원 시장
- 🇺🇸 미국 주식 (yfinance)
- 🇰🇷 한국 주식 (pykrx)
- 💰 암호화폐 (ccxt - Binance 등)

### 🎯 핵심 지표
- 전환선 (Tenkan-sen)
- 기준선 (Kijun-sen)
- 선행스팬 A/B (Senkou Span A/B)
- 후행스팬 (Chikou Span)
- 구름 (Kumo/Cloud)

## 문제 해결

### 데이터 수집 오류
```bash
# 패키지 업데이트
pip install --upgrade yfinance pykrx ccxt
```

### 한국 주식이 안 되는 경우
```bash
# pykrx 재설치
pip uninstall pykrx
pip install pykrx
```

### Streamlit 오류
```bash
# Streamlit 재설치
pip uninstall streamlit
pip install streamlit
```

## 다음 단계

1. **설정 커스터마이징**: `ichimoku_analyzer/config/settings.py` 수정
2. **체크리스트 조정**: `ichimoku_analyzer/config/checklist_weights.py` 수정
3. **알림 설정**: `.env` 파일에 Telegram 설정 추가
4. **배치 실행**: `ichimoku_analyzer/scripts/daily_batch.py` 사용

## 도움말

- 전체 문서: [README.md](README.md)
- 이슈 리포트: GitHub Issues
- 기능 제안: Pull Request

---

**즐거운 트레이딩 되세요! 📈**
