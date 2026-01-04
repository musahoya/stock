"""
일목균형표 지표 계산 모듈
Ichimoku Kinko Hyo (Ichimoku Cloud) indicator calculation
"""
import pandas as pd
import numpy as np
from typing import Tuple
import logging

from ..config.settings import ICHIMOKU_PARAMS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IchimokuCalculator:
    """
    일목균형표 계산 클래스
    """

    def __init__(self, **params):
        """
        Args:
            tenkan_period: 전환선 기간 (기본 9)
            kijun_period: 기준선 기간 (기본 26)
            senkou_b_period: 선행스팬B 기간 (기본 52)
            displacement: 선행/후행 이동 (기본 26)
        """
        self.params = {**ICHIMOKU_PARAMS, **params}
        logger.info(f"IchimokuCalculator initialized with params: {self.params}")

    def calculate_tenkan_sen(self, df: pd.DataFrame) -> pd.Series:
        """
        전환선 (Conversion Line) 계산
        (9일 최고가 + 9일 최저가) / 2

        Args:
            df: OHLCV 데이터

        Returns:
            전환선 Series
        """
        period = self.params['tenkan_period']
        high_max = df['high'].rolling(window=period).max()
        low_min = df['low'].rolling(window=period).min()
        return (high_max + low_min) / 2

    def calculate_kijun_sen(self, df: pd.DataFrame) -> pd.Series:
        """
        기준선 (Base Line) 계산
        (26일 최고가 + 26일 최저가) / 2

        Args:
            df: OHLCV 데이터

        Returns:
            기준선 Series
        """
        period = self.params['kijun_period']
        high_max = df['high'].rolling(window=period).max()
        low_min = df['low'].rolling(window=period).min()
        return (high_max + low_min) / 2

    def calculate_senkou_span_a(self, tenkan_sen: pd.Series, kijun_sen: pd.Series) -> pd.Series:
        """
        선행스팬A (Leading Span A) 계산
        (전환선 + 기준선) / 2, 26일 선행

        Args:
            tenkan_sen: 전환선
            kijun_sen: 기준선

        Returns:
            선행스팬A Series (26일 선행)
        """
        displacement = self.params['displacement']
        span_a = (tenkan_sen + kijun_sen) / 2
        return span_a.shift(displacement)

    def calculate_senkou_span_b(self, df: pd.DataFrame) -> pd.Series:
        """
        선행스팬B (Leading Span B) 계산
        (52일 최고가 + 52일 최저가) / 2, 26일 선행

        Args:
            df: OHLCV 데이터

        Returns:
            선행스팬B Series (26일 선행)
        """
        period = self.params['senkou_b_period']
        displacement = self.params['displacement']

        high_max = df['high'].rolling(window=period).max()
        low_min = df['low'].rolling(window=period).min()
        span_b = (high_max + low_min) / 2

        return span_b.shift(displacement)

    def calculate_chikou_span(self, df: pd.DataFrame) -> pd.Series:
        """
        후행스팬 (Lagging Span) 계산
        현재 종가를 26일 후행

        Args:
            df: OHLCV 데이터

        Returns:
            후행스팬 Series (26일 후행)
        """
        displacement = self.params['displacement']
        return df['close'].shift(-displacement)

    def calculate_cloud_metrics(
        self,
        senkou_span_a: pd.Series,
        senkou_span_b: pd.Series
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        구름 관련 지표 계산

        Args:
            senkou_span_a: 선행스팬A
            senkou_span_b: 선행스팬B

        Returns:
            (cloud_top, cloud_bottom, cloud_color) 튜플
            - cloud_top: 구름 상단
            - cloud_bottom: 구름 하단
            - cloud_color: 1 (양운), -1 (음운)
        """
        cloud_top = pd.Series(
            np.maximum(senkou_span_a, senkou_span_b),
            index=senkou_span_a.index
        )
        cloud_bottom = pd.Series(
            np.minimum(senkou_span_a, senkou_span_b),
            index=senkou_span_a.index
        )

        # 양운(1): span_a > span_b, 음운(-1): span_a <= span_b
        cloud_color = pd.Series(
            np.where(senkou_span_a > senkou_span_b, 1, -1),
            index=senkou_span_a.index
        )

        return cloud_top, cloud_bottom, cloud_color

    def calculate_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        모든 일목균형표 지표 계산

        Args:
            df: OHLCV 데이터 (open, high, low, close, volume)

        Returns:
            일목균형표 지표가 추가된 DataFrame
        """
        try:
            logger.info(f"Calculating Ichimoku indicators for {len(df)} data points")

            # 원본 데이터 복사
            result = df.copy()

            # 기본 지표 계산
            result['tenkan_sen'] = self.calculate_tenkan_sen(df)
            result['kijun_sen'] = self.calculate_kijun_sen(df)

            # 선행스팬 계산
            result['senkou_span_a'] = self.calculate_senkou_span_a(
                result['tenkan_sen'],
                result['kijun_sen']
            )
            result['senkou_span_b'] = self.calculate_senkou_span_b(df)

            # 후행스팬 계산
            result['chikou_span'] = self.calculate_chikou_span(df)

            # 구름 관련 지표
            cloud_top, cloud_bottom, cloud_color = self.calculate_cloud_metrics(
                result['senkou_span_a'],
                result['senkou_span_b']
            )

            result['cloud_top'] = cloud_top
            result['cloud_bottom'] = cloud_bottom
            result['cloud_color'] = cloud_color

            # 구름 두께 계산 (절대값 및 퍼센트)
            result['cloud_thickness'] = cloud_top - cloud_bottom
            result['cloud_thickness_pct'] = (
                result['cloud_thickness'] / result['close'] * 100
            )

            # 추가 유용한 지표들
            result['price_vs_cloud'] = self._calculate_price_vs_cloud(result)
            result['tenkan_kijun_diff'] = result['tenkan_sen'] - result['kijun_sen']
            result['tenkan_kijun_diff_pct'] = (
                result['tenkan_kijun_diff'] / result['close'] * 100
            )

            logger.info("Ichimoku indicators calculated successfully")
            return result

        except Exception as e:
            logger.error(f"Error calculating Ichimoku indicators: {str(e)}")
            raise

    def _calculate_price_vs_cloud(self, df: pd.DataFrame) -> pd.Series:
        """
        가격과 구름의 상대적 위치 계산

        Returns:
            1: 가격이 구름 위
            0: 가격이 구름 내부
            -1: 가격이 구름 아래
        """
        price = df['close']
        cloud_top = df['cloud_top']
        cloud_bottom = df['cloud_bottom']

        return pd.Series(
            np.where(
                price > cloud_top, 1,
                np.where(price < cloud_bottom, -1, 0)
            ),
            index=df.index
        )

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        매매 신호 감지

        Args:
            df: 일목균형표 지표가 포함된 DataFrame

        Returns:
            신호가 추가된 DataFrame
        """
        result = df.copy()

        # 호전 (전환선이 기준선을 상향 돌파)
        result['tenkan_cross_above'] = (
            (result['tenkan_sen'] > result['kijun_sen']) &
            (result['tenkan_sen'].shift(1) <= result['kijun_sen'].shift(1))
        )

        # 역전 (전환선이 기준선을 하향 돌파)
        result['tenkan_cross_below'] = (
            (result['tenkan_sen'] < result['kijun_sen']) &
            (result['tenkan_sen'].shift(1) >= result['kijun_sen'].shift(1))
        )

        # 구름 상향 돌파
        result['cloud_breakout_up'] = (
            (result['close'] > result['cloud_top']) &
            (result['close'].shift(1) <= result['cloud_top'].shift(1))
        )

        # 구름 하향 돌파
        result['cloud_breakout_down'] = (
            (result['close'] < result['cloud_bottom']) &
            (result['close'].shift(1) >= result['cloud_bottom'].shift(1))
        )

        # 구름 색깔 변화
        result['cloud_color_change'] = (
            result['cloud_color'] != result['cloud_color'].shift(1)
        )

        return result
