"""
데이터 수집 통합 모듈
모든 시장의 데이터 수집을 통합 관리
"""
import pandas as pd
from typing import Optional, Dict
import logging

from .us_stocks import fetch_us_stock, fetch_multiple_us_stocks
from .kr_stocks import fetch_kr_stock, fetch_multiple_kr_stocks, get_stock_name
from .crypto import fetch_crypto, fetch_multiple_crypto
from ..config.settings import DATA_FETCH_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """
    통합 데이터 수집 클래스
    모든 시장(미국, 한국, 크립토)의 데이터를 일관된 인터페이스로 제공
    """

    def __init__(self):
        self.config = DATA_FETCH_CONFIG

    def fetch(self, symbol: str, market_type: str = 'us', **kwargs) -> Optional[pd.DataFrame]:
        """
        시장 타입에 따라 적절한 데이터 수집 함수 호출

        Args:
            symbol: 종목 심볼/코드
            market_type: 시장 타입 ('us', 'kr', 'crypto')
            **kwargs: 추가 파라미터

        Returns:
            DataFrame 또는 None
        """
        if market_type == 'us':
            period = kwargs.get('period', self.config['us_stock_period'])
            return fetch_us_stock(symbol, period)

        elif market_type == 'kr':
            days = kwargs.get('days', self.config['kr_stock_days'])
            return fetch_kr_stock(symbol, days)

        elif market_type == 'crypto':
            timeframe = kwargs.get('timeframe', '1d')
            limit = kwargs.get('limit', self.config['crypto_limit'])
            exchange = kwargs.get('exchange', 'binance')
            return fetch_crypto(symbol, timeframe, limit, exchange)

        else:
            logger.error(f"Unknown market type: {market_type}")
            return None

    def fetch_multiple(self, symbols: list, market_type: str = 'us', **kwargs) -> Dict[str, pd.DataFrame]:
        """
        여러 종목의 데이터를 동시 수집

        Args:
            symbols: 종목 리스트
            market_type: 시장 타입
            **kwargs: 추가 파라미터

        Returns:
            {symbol: DataFrame} 딕셔너리
        """
        if market_type == 'us':
            period = kwargs.get('period', self.config['us_stock_period'])
            return fetch_multiple_us_stocks(symbols, period)

        elif market_type == 'kr':
            days = kwargs.get('days', self.config['kr_stock_days'])
            return fetch_multiple_kr_stocks(symbols, days)

        elif market_type == 'crypto':
            timeframe = kwargs.get('timeframe', '1d')
            limit = kwargs.get('limit', self.config['crypto_limit'])
            exchange = kwargs.get('exchange', 'binance')
            return fetch_multiple_crypto(symbols, timeframe, limit, exchange)

        else:
            logger.error(f"Unknown market type: {market_type}")
            return {}

    def get_symbol_name(self, symbol: str, market_type: str = 'us') -> str:
        """
        종목명 조회

        Args:
            symbol: 종목 심볼/코드
            market_type: 시장 타입

        Returns:
            종목명
        """
        if market_type == 'kr':
            return get_stock_name(symbol)
        else:
            return symbol

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        데이터 유효성 검증

        Args:
            df: 검증할 DataFrame

        Returns:
            유효하면 True
        """
        if df is None or df.empty:
            return False

        # 최소 데이터 포인트 확인
        if len(df) < self.config['min_data_points']:
            logger.warning(f"Insufficient data points: {len(df)} < {self.config['min_data_points']}")
            return False

        # 필수 컬럼 확인
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_columns):
            logger.error("Missing required columns")
            return False

        # 결측치 확인
        if df[required_columns].isnull().any().any():
            logger.warning("Data contains null values")
            return False

        return True
