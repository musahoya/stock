"""
종목 순위 산정 모듈
"""
import pandas as pd
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockRanker:
    """
    종목 점수를 기반으로 순위 산정
    """

    def __init__(self):
        pass

    def rank_stocks(self, score_results: Dict[str, Dict]) -> pd.DataFrame:
        """
        종목들의 점수를 기반으로 순위 산정

        Args:
            score_results: {symbol: score_info} 딕셔너리

        Returns:
            순위가 포함된 DataFrame
        """
        if not score_results:
            logger.warning("No score results to rank")
            return pd.DataFrame()

        # 데이터 정리
        data = []
        for symbol, score_info in score_results.items():
            data.append({
                'symbol': symbol,
                'total_score': score_info['total_score'],
                'max_score': score_info['max_score'],
                'percentage': score_info['percentage'],
                'grade': score_info['grade']
            })

        # DataFrame 생성
        df = pd.DataFrame(data)

        # 점수 순 정렬
        df = df.sort_values('total_score', ascending=False).reset_index(drop=True)

        # 순위 추가
        df['rank'] = range(1, len(df) + 1)

        # 컬럼 순서 조정
        df = df[['rank', 'symbol', 'total_score', 'max_score', 'percentage', 'grade']]

        logger.info(f"Ranked {len(df)} stocks")
        return df

    def filter_by_grade(self, ranking_df: pd.DataFrame, min_grade: str = 'C') -> pd.DataFrame:
        """
        등급으로 필터링

        Args:
            ranking_df: 순위 DataFrame
            min_grade: 최소 등급 ('A', 'B', 'C', 'D')

        Returns:
            필터링된 DataFrame
        """
        grade_order = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'F': 0}
        min_grade_value = grade_order.get(min_grade, 0)

        filtered = ranking_df[
            ranking_df['grade'].map(grade_order) >= min_grade_value
        ].copy()

        logger.info(f"Filtered to {len(filtered)} stocks with grade >= {min_grade}")
        return filtered

    def filter_by_score(self, ranking_df: pd.DataFrame, min_score: int = 20) -> pd.DataFrame:
        """
        최소 점수로 필터링

        Args:
            ranking_df: 순위 DataFrame
            min_score: 최소 점수

        Returns:
            필터링된 DataFrame
        """
        filtered = ranking_df[ranking_df['total_score'] >= min_score].copy()

        logger.info(f"Filtered to {len(filtered)} stocks with score >= {min_score}")
        return filtered

    def get_top_n(self, ranking_df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        """
        상위 N개 종목 추출

        Args:
            ranking_df: 순위 DataFrame
            n: 추출할 개수

        Returns:
            상위 N개 DataFrame
        """
        return ranking_df.head(n)

    def add_price_info(
        self,
        ranking_df: pd.DataFrame,
        price_data: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """
        순위 DataFrame에 가격 정보 추가

        Args:
            ranking_df: 순위 DataFrame
            price_data: {symbol: df} 딕셔너리

        Returns:
            가격 정보가 추가된 DataFrame
        """
        result = ranking_df.copy()

        # 현재가 추가
        result['current_price'] = result['symbol'].map(
            lambda s: price_data[s].iloc[-1]['close'] if s in price_data else None
        )

        # 전일 대비 변화율
        result['price_change_pct'] = result['symbol'].map(
            lambda s: self._calculate_price_change(price_data[s]) if s in price_data else None
        )

        return result

    def _calculate_price_change(self, df: pd.DataFrame) -> float:
        """전일 대비 가격 변화율 계산"""
        if len(df) < 2:
            return 0.0

        current = df.iloc[-1]['close']
        previous = df.iloc[-2]['close']

        return ((current - previous) / previous) * 100

    def generate_summary(self, ranking_df: pd.DataFrame) -> Dict:
        """
        순위 요약 정보 생성

        Args:
            ranking_df: 순위 DataFrame

        Returns:
            요약 정보 딕셔너리
        """
        summary = {
            'total_stocks': len(ranking_df),
            'grade_distribution': ranking_df['grade'].value_counts().to_dict(),
            'average_score': ranking_df['total_score'].mean(),
            'top_stock': ranking_df.iloc[0]['symbol'] if len(ranking_df) > 0 else None,
            'top_score': ranking_df.iloc[0]['total_score'] if len(ranking_df) > 0 else 0
        }

        return summary
