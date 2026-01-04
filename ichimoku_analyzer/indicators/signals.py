"""
일목균형표 매매 신호 감지 모듈
"""
import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalDetector:
    """
    일목균형표 기반 매매 신호 감지
    """

    def __init__(self, lookback: int = 10):
        """
        Args:
            lookback: 신호 감지를 위한 lookback 기간
        """
        self.lookback = lookback

    def detect_all_signals(self, df: pd.DataFrame) -> Dict[str, bool]:
        """
        최근 시점의 모든 매매 신호 감지

        Args:
            df: 일목균형표 지표가 포함된 DataFrame

        Returns:
            신호 딕셔너리
        """
        signals = {}

        # 최근 데이터 확인
        if len(df) < self.lookback:
            logger.warning(f"Insufficient data for signal detection: {len(df)} < {self.lookback}")
            return signals

        recent_df = df.tail(self.lookback)

        # 호전 신호
        signals['tenkan_cross_up'] = self._detect_tenkan_cross_up(recent_df)

        # 역전 신호
        signals['tenkan_cross_down'] = self._detect_tenkan_cross_down(recent_df)

        # 구름 돌파
        signals['cloud_breakout_up'] = self._detect_cloud_breakout_up(recent_df)
        signals['cloud_breakout_down'] = self._detect_cloud_breakout_down(recent_df)

        # 후행스팬 돌파
        signals['chikou_breakout_up'] = self._detect_chikou_breakout_up(df)

        # 전환선/기준선 지지
        signals['tenkan_support'] = self._detect_tenkan_support(recent_df)
        signals['kijun_support'] = self._detect_kijun_support(recent_df)

        # 구름 지지
        signals['cloud_support'] = self._detect_cloud_support(recent_df)

        return signals

    def _detect_tenkan_cross_up(self, df: pd.DataFrame) -> bool:
        """호전: 전환선이 기준선을 상향 돌파"""
        for i in range(len(df) - 1):
            if (df.iloc[i]['tenkan_sen'] <= df.iloc[i]['kijun_sen'] and
                df.iloc[i + 1]['tenkan_sen'] > df.iloc[i + 1]['kijun_sen']):
                return True
        return False

    def _detect_tenkan_cross_down(self, df: pd.DataFrame) -> bool:
        """역전: 전환선이 기준선을 하향 돌파"""
        for i in range(len(df) - 1):
            if (df.iloc[i]['tenkan_sen'] >= df.iloc[i]['kijun_sen'] and
                df.iloc[i + 1]['tenkan_sen'] < df.iloc[i + 1]['kijun_sen']):
                return True
        return False

    def _detect_cloud_breakout_up(self, df: pd.DataFrame) -> bool:
        """구름 상향 돌파"""
        for i in range(len(df) - 1):
            if (df.iloc[i]['close'] <= df.iloc[i]['cloud_top'] and
                df.iloc[i + 1]['close'] > df.iloc[i + 1]['cloud_top']):
                return True
        return False

    def _detect_cloud_breakout_down(self, df: pd.DataFrame) -> bool:
        """구름 하향 돌파"""
        for i in range(len(df) - 1):
            if (df.iloc[i]['close'] >= df.iloc[i]['cloud_bottom'] and
                df.iloc[i + 1]['close'] < df.iloc[i + 1]['cloud_bottom']):
                return True
        return False

    def _detect_chikou_breakout_up(self, df: pd.DataFrame) -> bool:
        """
        후행스팬 상향 돌파
        현재 후행스팬이 26일 전 가격을 상향 돌파
        """
        if len(df) < 30:
            return False

        recent = df.tail(self.lookback)
        displacement = 26

        for i in range(len(recent)):
            idx = recent.index[i]
            idx_pos = df.index.get_loc(idx)

            if idx_pos >= displacement:
                past_idx = df.index[idx_pos - displacement]
                chikou = recent.iloc[i]['chikou_span']
                past_price = df.loc[past_idx, 'close']

                if not pd.isna(chikou) and chikou > past_price:
                    # 이전 시점에서는 아래였는지 확인
                    if idx_pos > displacement:
                        prev_idx = df.index[idx_pos - 1]
                        prev_past_idx = df.index[idx_pos - displacement - 1]
                        prev_chikou = df.loc[prev_idx, 'chikou_span']
                        prev_past_price = df.loc[prev_past_idx, 'close']

                        if not pd.isna(prev_chikou) and prev_chikou <= prev_past_price:
                            return True

        return False

    def _detect_tenkan_support(self, df: pd.DataFrame) -> bool:
        """전환선 지지: 최근 저가가 전환선에 닿았다가 반등"""
        for i in range(len(df)):
            low = df.iloc[i]['low']
            high = df.iloc[i]['high']
            tenkan = df.iloc[i]['tenkan_sen']

            if pd.isna(tenkan):
                continue

            # 전환선이 저가와 고가 사이에 있으면 지지/저항으로 판단
            if low <= tenkan <= high:
                return True

        return False

    def _detect_kijun_support(self, df: pd.DataFrame) -> bool:
        """기준선 지지: 최근 저가가 기준선에 닿았다가 반등"""
        for i in range(len(df)):
            low = df.iloc[i]['low']
            high = df.iloc[i]['high']
            kijun = df.iloc[i]['kijun_sen']

            if pd.isna(kijun):
                continue

            if low <= kijun <= high:
                return True

        return False

    def _detect_cloud_support(self, df: pd.DataFrame) -> bool:
        """구름 지지: 가격이 구름 상단에서 지지"""
        for i in range(len(df)):
            low = df.iloc[i]['low']
            high = df.iloc[i]['high']
            cloud_top = df.iloc[i]['cloud_top']
            cloud_bottom = df.iloc[i]['cloud_bottom']

            if pd.isna(cloud_top) or pd.isna(cloud_bottom):
                continue

            # 구름 상단 또는 하단에서 지지
            if (low <= cloud_top <= high) or (low <= cloud_bottom <= high):
                return True

        return False
