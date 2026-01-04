"""
암호화폐 데이터 수집 모듈
ccxt를 사용하여 여러 거래소 데이터 수집
"""
import pandas as pd
import ccxt
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_crypto(
    symbol: str,
    timeframe: str = '1d',
    limit: int = 365,
    exchange_name: str = 'binance'
) -> Optional[pd.DataFrame]:
    """
    암호화폐 데이터 수집

    Args:
        symbol: 심볼 (예: 'BTC/USDT')
        timeframe: 시간 단위 ('1m', '5m', '1h', '1d', '1w')
        limit: 데이터 개수
        exchange_name: 거래소 이름 ('binance', 'upbit', 'coinbase' 등)

    Returns:
        DataFrame with columns: open, high, low, close, volume
        실패 시 None
    """
    try:
        logger.info(f"Fetching crypto data for {symbol} from {exchange_name}")

        # 거래소 객체 생성
        exchange_class = getattr(ccxt, exchange_name)
        exchange = exchange_class()

        # OHLCV 데이터 수집
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

        if not ohlcv:
            logger.error(f"No data returned for {symbol}")
            return None

        # DataFrame 생성
        df = pd.DataFrame(
            ohlcv,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )

        # 타임스탬프를 datetime으로 변환하여 인덱스로 설정
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('date', inplace=True)
        df.drop('timestamp', axis=1, inplace=True)

        # 필요한 컬럼만 선택
        df = df[['open', 'high', 'low', 'close', 'volume']].copy()

        # 결측치 제거
        df.dropna(inplace=True)

        logger.info(f"Successfully fetched {len(df)} rows for {symbol}")
        return df

    except Exception as e:
        logger.error(f"Error fetching {symbol}: {str(e)}")
        return None


def fetch_multiple_crypto(
    symbols: list,
    timeframe: str = '1d',
    limit: int = 365,
    exchange_name: str = 'binance'
) -> dict:
    """
    여러 암호화폐 데이터를 동시 수집

    Args:
        symbols: 심볼 리스트
        timeframe: 시간 단위
        limit: 데이터 개수
        exchange_name: 거래소 이름

    Returns:
        {symbol: DataFrame} 딕셔너리
    """
    results = {}

    for symbol in symbols:
        df = fetch_crypto(symbol, timeframe, limit, exchange_name)
        if df is not None:
            results[symbol] = df

    logger.info(f"Successfully fetched {len(results)}/{len(symbols)} crypto pairs")
    return results


def get_available_exchanges() -> list:
    """
    사용 가능한 거래소 목록 반환

    Returns:
        거래소 이름 리스트
    """
    return ccxt.exchanges
