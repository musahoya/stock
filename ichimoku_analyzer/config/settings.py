"""
일목균형표 분석 시스템 기본 설정
"""
import os
from dotenv import load_dotenv

load_dotenv()

# 일목균형표 기본 파라미터
ICHIMOKU_PARAMS = {
    'tenkan_period': 9,      # 전환선
    'kijun_period': 26,      # 기준선
    'senkou_b_period': 52,   # 선행스팬B
    'displacement': 26       # 선행/후행 이동
}

# 데이터 수집 설정
DATA_FETCH_CONFIG = {
    'us_stock_period': '1y',
    'kr_stock_days': 365,
    'crypto_limit': 365,
    'min_data_points': 100
}

# 캐시 설정
CACHE_CONFIG = {
    'enabled': True,
    'max_age_hours': int(os.getenv('CACHE_MAX_AGE_HOURS', 1)),
    'cache_dir': 'cache'
}

# 알림 설정
ALERT_CONFIG = {
    'telegram_enabled': bool(os.getenv('TELEGRAM_BOT_TOKEN')),
    'telegram_token': os.getenv('TELEGRAM_BOT_TOKEN'),
    'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID'),
    'high_score_threshold': int(os.getenv('HIGH_SCORE_THRESHOLD', 35))
}

# 등급 기준
GRADE_THRESHOLDS = {
    'A': 0.70,  # 70% 이상
    'B': 0.50,  # 50-69%
    'C': 0.35,  # 35-49%
    'D': 0.20,  # 20-34%
    'F': 0.00   # 20% 미만
}

# 시장별 기본 종목
DEFAULT_SYMBOLS = {
    'us': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'JPM'],
    'kr': ['005930', '000660', '035420', '035720', '051910', '005380'],  # 삼성전자, SK하이닉스, NAVER, 카카오, LG화학, 현대차
    'crypto': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT']
}
