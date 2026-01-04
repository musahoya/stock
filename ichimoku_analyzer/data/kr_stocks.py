"""
한국 주식 데이터 수집 모듈
pykrx를 사용하여 데이터 수집
"""
import pandas as pd
from pykrx import stock
from datetime import datetime, timedelta
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_kr_stock(symbol: str, days: int = 365) -> Optional[pd.DataFrame]:
    """
    한국 주식 데이터 수집

    Args:
        symbol: 종목코드 (예: '005930' - 삼성전자)
        days: 과거 며칠치 데이터

    Returns:
        DataFrame with columns: open, high, low, close, volume
        실패 시 None
    """
    try:
        logger.info(f"Fetching KR stock data for {symbol}")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        end_str = end_date.strftime('%Y%m%d')
        start_str = start_date.strftime('%Y%m%d')

        df = stock.get_market_ohlcv_by_date(start_str, end_str, symbol)

        if df.empty:
            logger.error(f"No data returned for {symbol}")
            return None

        # 컬럼명 영문 소문자로 표준화
        # pykrx는 한글 컬럼명을 사용하므로 변환 필요
        column_mapping = {
            '시가': 'open',
            '고가': 'high',
            '저가': 'low',
            '종가': 'close',
            '거래량': 'volume'
        }

        df.rename(columns=column_mapping, inplace=True)
        df = df[['open', 'high', 'low', 'close', 'volume']].copy()

        # 결측치 제거
        df.dropna(inplace=True)

        logger.info(f"Successfully fetched {len(df)} rows for {symbol}")
        return df

    except Exception as e:
        logger.error(f"Error fetching {symbol}: {str(e)}")
        return None


def fetch_multiple_kr_stocks(symbols: list, days: int = 365) -> dict:
    """
    여러 한국 주식 데이터를 동시 수집

    Args:
        symbols: 종목코드 리스트
        days: 과거 며칠치 데이터

    Returns:
        {symbol: DataFrame} 딕셔너리
    """
    results = {}

    for symbol in symbols:
        df = fetch_kr_stock(symbol, days)
        if df is not None:
            results[symbol] = df

    logger.info(f"Successfully fetched {len(results)}/{len(symbols)} KR stocks")
    return results


def get_stock_name(symbol: str) -> str:
    """
    종목코드로 종목명 조회

    Args:
        symbol: 종목코드

    Returns:
        종목명
    """
    try:
        name = stock.get_market_ticker_name(symbol)
        return name if name else symbol
    except:
        return symbol
