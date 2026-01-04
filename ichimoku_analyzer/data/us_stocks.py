"""
미국 주식 데이터 수집 모듈
yfinance를 사용하여 데이터 수집
"""
import pandas as pd
import yfinance as yf
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_us_stock(symbol: str, period: str = '1y') -> Optional[pd.DataFrame]:
    """
    미국 주식 데이터 수집

    Args:
        symbol: 티커 심볼 (예: 'AAPL')
        period: 데이터 기간 ('1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')

    Returns:
        DataFrame with columns: open, high, low, close, volume
        실패 시 None
    """
    try:
        logger.info(f"Fetching US stock data for {symbol}")

        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)

        if df.empty:
            logger.error(f"No data returned for {symbol}")
            return None

        # 컬럼명 소문자로 표준화
        df.columns = df.columns.str.lower()

        # 필요한 컬럼만 선택
        df = df[['open', 'high', 'low', 'close', 'volume']].copy()

        # 결측치 제거
        df.dropna(inplace=True)

        logger.info(f"Successfully fetched {len(df)} rows for {symbol}")
        return df

    except Exception as e:
        logger.error(f"Error fetching {symbol}: {str(e)}")
        return None


def fetch_multiple_us_stocks(symbols: list, period: str = '1y') -> dict:
    """
    여러 미국 주식 데이터를 동시 수집

    Args:
        symbols: 티커 심볼 리스트
        period: 데이터 기간

    Returns:
        {symbol: DataFrame} 딕셔너리
    """
    results = {}

    for symbol in symbols:
        df = fetch_us_stock(symbol, period)
        if df is not None:
            results[symbol] = df

    logger.info(f"Successfully fetched {len(results)}/{len(symbols)} US stocks")
    return results
