"""
일목균형표 체크리스트 점수 계산 모듈
각 항목을 체크하여 객관적 점수 산출
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

from ..config.checklist_weights import CHECKLIST_ITEMS, TOTAL_POINTS, CHECK_CONDITIONS
from ..config.settings import GRADE_THRESHOLDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChecklistScorer:
    """
    일목균형표 체크리스트 기반 점수 계산
    """

    def __init__(self):
        self.items = CHECKLIST_ITEMS
        self.conditions = CHECK_CONDITIONS
        self.total_points = TOTAL_POINTS
        self.grade_thresholds = GRADE_THRESHOLDS

    def calculate_score(self, df: pd.DataFrame, lookback: int = None) -> Dict:
        """
        전체 체크리스트 점수 계산

        Args:
            df: 일목균형표 지표가 포함된 DataFrame
            lookback: 최근 N일 확인 (None이면 설정값 사용)

        Returns:
            점수 정보 딕셔너리
        """
        if lookback is None:
            lookback = self.conditions['lookback_period']

        if len(df) < 52:  # 일목균형표 계산에 필요한 최소 데이터
            logger.warning("Insufficient data for scoring")
            return self._empty_score()

        # 각 항목 체크
        check_results = {}
        total_score = 0

        # 기본 배치
        check_results['chikou_above_price'] = self._check_chikou_above_price(df, lookback)
        check_results['current_cloud_bullish'] = self._check_current_cloud_bullish(df)
        check_results['future_cloud_bullish'] = self._check_future_cloud_bullish(df)

        # 가격 위치
        check_results['price_above_cloud'] = self._check_price_above_cloud(df)

        # 호전 관련
        check_results['tenkan_kijun_cross'] = self._check_tenkan_kijun_cross(df, lookback)
        check_results['no_kijun_break_after_cross'] = self._check_no_kijun_break_after_cross(df, lookback)
        check_results['kijun_trend'] = self._check_kijun_trend(df, lookback)

        # 지지 확인
        check_results['tenkan_support'] = self._check_tenkan_support(df, lookback)
        check_results['kijun_support'] = self._check_kijun_support(df, lookback)

        # 후행+호전 동시
        check_results['chikou_breakout'] = self._check_chikou_breakout(df, lookback)
        check_results['chikou_and_tenkan_cross'] = (
            check_results['chikou_breakout'] and check_results['tenkan_kijun_cross']
        )

        # 구름 돌파
        check_results['cloud_breakout'] = self._check_cloud_breakout(df, lookback)
        check_results['cloud_support_after_breakout'] = self._check_cloud_support_after_breakout(df, lookback)

        # 특수 패턴
        check_results['thin_cloud_breakout'] = self._check_thin_cloud_breakout(df, lookback)
        check_results['cloud_twist_bottom'] = self._check_cloud_twist_bottom(df, lookback)
        check_results['squeeze_kijun_support'] = self._check_squeeze_kijun_support(df, lookback)

        # 점수 합산
        for key, passed in check_results.items():
            if passed and key in self.items:
                total_score += self.items[key]['weight']

        # 퍼센트 및 등급 계산
        percentage = (total_score / self.total_points) * 100
        grade = self._calculate_grade(percentage)

        # 상세 정보
        details = self._build_details(check_results)

        return {
            'total_score': total_score,
            'max_score': self.total_points,
            'percentage': percentage,
            'grade': grade,
            'checks': check_results,
            'details': details
        }

    def _check_chikou_above_price(self, df: pd.DataFrame, lookback: int) -> bool:
        """후행스팬이 캔들 위"""
        recent = df.tail(lookback)
        displacement = 26

        for i in range(len(recent)):
            idx = recent.index[i]
            idx_pos = df.index.get_loc(idx)

            if idx_pos >= displacement:
                past_idx = df.index[idx_pos - displacement]
                chikou = recent.iloc[i]['chikou_span']
                past_price = df.loc[past_idx, 'close']

                if not pd.isna(chikou) and chikou > past_price:
                    return True

        return False

    def _check_current_cloud_bullish(self, df: pd.DataFrame) -> bool:
        """현재 구름이 양운"""
        latest = df.iloc[-1]
        if pd.isna(latest['senkou_span_a']) or pd.isna(latest['senkou_span_b']):
            return False
        return latest['senkou_span_a'] > latest['senkou_span_b']

    def _check_future_cloud_bullish(self, df: pd.DataFrame) -> bool:
        """앞쪽 구름도 양운 (26일 후)"""
        if len(df) < 26:
            return False

        # 현재 시점에서 26일 선행된 구름 확인
        # 실제로는 최신 데이터의 선행스팬을 확인
        recent = df.tail(26)
        bullish_count = (recent['senkou_span_a'] > recent['senkou_span_b']).sum()

        return bullish_count > len(recent) * 0.7  # 70% 이상 양운

    def _check_price_above_cloud(self, df: pd.DataFrame) -> bool:
        """주가가 구름 위"""
        latest = df.iloc[-1]
        if pd.isna(latest['cloud_top']):
            return False
        return latest['close'] > latest['cloud_top']

    def _check_tenkan_kijun_cross(self, df: pd.DataFrame, lookback: int) -> bool:
        """호전 발생 (전환선이 기준선을 상향 돌파)"""
        recent = df.tail(lookback + 1)

        for i in range(len(recent) - 1):
            curr = recent.iloc[i + 1]
            prev = recent.iloc[i]

            if (prev['tenkan_sen'] <= prev['kijun_sen'] and
                curr['tenkan_sen'] > curr['kijun_sen']):
                return True

        return False

    def _check_no_kijun_break_after_cross(self, df: pd.DataFrame, lookback: int) -> bool:
        """호전 후 기준선 하회 없음"""
        # 먼저 호전이 발생했는지 확인
        recent = df.tail(lookback * 2)
        cross_idx = None

        for i in range(len(recent) - 1):
            curr = recent.iloc[i + 1]
            prev = recent.iloc[i]

            if (prev['tenkan_sen'] <= prev['kijun_sen'] and
                curr['tenkan_sen'] > curr['kijun_sen']):
                cross_idx = i + 1
                break

        if cross_idx is None:
            return False

        # 호전 이후 가격이 기준선 아래로 내려갔는지 확인
        after_cross = recent.iloc[cross_idx:]
        for row in after_cross.itertuples():
            if row.close < row.kijun_sen:
                return False

        return True

    def _check_kijun_trend(self, df: pd.DataFrame, lookback: int) -> bool:
        """기준선이 상승 또는 수평"""
        recent = df.tail(lookback)
        if len(recent) < 2:
            return False

        # 최근 기준선의 기울기 확인
        kijun_values = recent['kijun_sen'].dropna()
        if len(kijun_values) < 2:
            return False

        # 상승 또는 거의 수평 (±0.5% 이내)
        first = kijun_values.iloc[0]
        last = kijun_values.iloc[-1]

        change_pct = ((last - first) / first) * 100 if first != 0 else 0

        return change_pct >= -0.5  # 0.5% 이상 하락하지 않음

    def _check_tenkan_support(self, df: pd.DataFrame, lookback: int) -> bool:
        """전환선 지지"""
        recent = df.tail(lookback)

        for row in recent.itertuples():
            if pd.isna(row.tenkan_sen):
                continue
            if row.low <= row.tenkan_sen <= row.high:
                return True

        return False

    def _check_kijun_support(self, df: pd.DataFrame, lookback: int) -> bool:
        """기준선 지지"""
        recent = df.tail(lookback)

        for row in recent.itertuples():
            if pd.isna(row.kijun_sen):
                continue
            if row.low <= row.kijun_sen <= row.high:
                return True

        return False

    def _check_chikou_breakout(self, df: pd.DataFrame, lookback: int) -> bool:
        """후행스팬 상향 돌파"""
        return self._check_chikou_above_price(df, lookback)

    def _check_cloud_breakout(self, df: pd.DataFrame, lookback: int) -> bool:
        """구름 상향 돌파"""
        recent = df.tail(lookback + 1)

        for i in range(len(recent) - 1):
            curr = recent.iloc[i + 1]
            prev = recent.iloc[i]

            if pd.isna(prev['cloud_top']) or pd.isna(curr['cloud_top']):
                continue

            if prev['close'] <= prev['cloud_top'] and curr['close'] > curr['cloud_top']:
                return True

        return False

    def _check_cloud_support_after_breakout(self, df: pd.DataFrame, lookback: int) -> bool:
        """구름 돌파 후 상단 지지"""
        # 먼저 돌파가 있었는지 확인
        if not self._check_cloud_breakout(df, lookback):
            return False

        # 돌파 후 구름 상단에서 지지 확인
        recent = df.tail(lookback)

        for row in recent.itertuples():
            if pd.isna(row.cloud_top):
                continue
            # 가격이 구름 위에 있고, 저가가 구름 상단 근처
            if row.close > row.cloud_top and row.low <= row.cloud_top * 1.02:
                return True

        return False

    def _check_thin_cloud_breakout(self, df: pd.DataFrame, lookback: int) -> bool:
        """얇은 구름 상향 돌파"""
        recent = df.tail(lookback + 1)
        threshold = self.conditions['thin_cloud_threshold']

        for i in range(len(recent) - 1):
            curr = recent.iloc[i + 1]
            prev = recent.iloc[i]

            if pd.isna(prev['cloud_top']) or pd.isna(curr['cloud_top']):
                continue

            # 구름 두께가 가격의 2% 미만
            cloud_thickness_pct = curr['cloud_thickness'] / curr['close']

            if (cloud_thickness_pct < threshold and
                prev['close'] <= prev['cloud_top'] and
                curr['close'] > curr['cloud_top']):
                return True

        return False

    def _check_cloud_twist_bottom(self, df: pd.DataFrame, lookback: int) -> bool:
        """음→양 교차 바닥"""
        recent = df.tail(lookback * 2)

        for i in range(len(recent) - 1):
            curr = recent.iloc[i + 1]
            prev = recent.iloc[i]

            # 구름 색깔이 음운에서 양운으로 변화
            if prev['cloud_color'] == -1 and curr['cloud_color'] == 1:
                # 저점 갱신 실패 확인 (최근 저가가 이전 저가보다 높음)
                if i > 0:
                    prev_low = recent.iloc[i - 1]['low']
                    if curr['low'] > prev_low:
                        return True

        return False

    def _check_squeeze_kijun_support(self, df: pd.DataFrame, lookback: int) -> bool:
        """협착 후 기준선 지지"""
        recent = df.tail(lookback * 2)
        threshold = self.conditions['squeeze_threshold']

        # 협착 확인 (전환선과 기준선 간격이 좁아짐)
        squeeze_detected = False

        for i in range(len(recent)):
            row = recent.iloc[i]
            if pd.isna(row['tenkan_sen']) or pd.isna(row['kijun_sen']):
                continue

            diff_pct = abs(row['tenkan_sen'] - row['kijun_sen']) / row['close']

            if diff_pct < threshold:
                squeeze_detected = True
                break

        if not squeeze_detected:
            return False

        # 협착 후 기준선 지지 확인
        return self._check_kijun_support(df, lookback)

    def _calculate_grade(self, percentage: float) -> str:
        """퍼센트에 따른 등급 산정"""
        if percentage >= self.grade_thresholds['A'] * 100:
            return 'A'
        elif percentage >= self.grade_thresholds['B'] * 100:
            return 'B'
        elif percentage >= self.grade_thresholds['C'] * 100:
            return 'C'
        elif percentage >= self.grade_thresholds['D'] * 100:
            return 'D'
        else:
            return 'F'

    def _build_details(self, check_results: Dict[str, bool]) -> List[Dict]:
        """체크 결과 상세 정보 생성"""
        details = []

        for key, passed in check_results.items():
            if key in self.items:
                item = self.items[key]
                details.append({
                    'key': key,
                    'name': item['name'],
                    'description': item['description'],
                    'weight': item['weight'],
                    'passed': passed
                })

        return details

    def _empty_score(self) -> Dict:
        """데이터 부족 시 빈 점수 반환"""
        return {
            'total_score': 0,
            'max_score': self.total_points,
            'percentage': 0.0,
            'grade': 'F',
            'checks': {},
            'details': []
        }
