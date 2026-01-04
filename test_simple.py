#!/usr/bin/env python3
"""
간단한 테스트 스크립트
시스템의 각 모듈을 개별적으로 테스트
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_data_fetcher():
    """데이터 수집 테스트"""
    print("=" * 50)
    print("1. 데이터 수집 테스트")
    print("=" * 50)

    from ichimoku_analyzer.data.fetcher import DataFetcher

    fetcher = DataFetcher()

    # 미국 주식 테스트
    print("\n[미국 주식] AAPL 데이터 수집...")
    df = fetcher.fetch('AAPL', market_type='us')

    if df is not None:
        print(f"✅ 성공: {len(df)}행 수집")
        print(f"데이터 기간: {df.index[0]} ~ {df.index[-1]}")
        print(f"최근 종가: ${df.iloc[-1]['close']:.2f}")
    else:
        print("❌ 실패")

    return df


def test_ichimoku_calculator(df):
    """일목균형표 계산 테스트"""
    print("\n" + "=" * 50)
    print("2. 일목균형표 계산 테스트")
    print("=" * 50)

    from ichimoku_analyzer.indicators.ichimoku import IchimokuCalculator

    calculator = IchimokuCalculator()
    df_ichimoku = calculator.calculate_all(df)

    print(f"\n✅ 일목균형표 계산 완료")
    print(f"생성된 지표 수: {len(df_ichimoku.columns)}")

    # 최근 데이터 출력
    print("\n최근 일목균형표 값:")
    latest = df_ichimoku.iloc[-1]

    print(f"  전환선: {latest['tenkan_sen']:.2f}")
    print(f"  기준선: {latest['kijun_sen']:.2f}")
    print(f"  선행스팬A: {latest['senkou_span_a']:.2f}")
    print(f"  선행스팬B: {latest['senkou_span_b']:.2f}")
    print(f"  구름 색깔: {'양운' if latest['cloud_color'] == 1 else '음운'}")

    return df_ichimoku


def test_checklist_scorer(df_ichimoku):
    """체크리스트 점수 계산 테스트"""
    print("\n" + "=" * 50)
    print("3. 체크리스트 점수 계산 테스트")
    print("=" * 50)

    from ichimoku_analyzer.scoring.checklist import ChecklistScorer

    scorer = ChecklistScorer()
    score_info = scorer.calculate_score(df_ichimoku)

    print(f"\n✅ 점수 계산 완료")
    print(f"  총점: {score_info['total_score']}/{score_info['max_score']}")
    print(f"  퍼센트: {score_info['percentage']:.2f}%")
    print(f"  등급: {score_info['grade']}")

    # 통과 항목
    passed = [d for d in score_info['details'] if d['passed']]
    failed = [d for d in score_info['details'] if not d['passed']]

    print(f"\n  통과 항목: {len(passed)}/{len(score_info['details'])}")

    if passed:
        print("\n  ✅ 통과 항목:")
        for item in passed[:5]:  # 처음 5개만
            print(f"    - {item['name']} ({item['weight']}점)")

    if len(passed) > 5:
        print(f"    ... 외 {len(passed) - 5}개")

    return score_info


def test_ranker():
    """순위 산정 테스트"""
    print("\n" + "=" * 50)
    print("4. 순위 산정 테스트")
    print("=" * 50)

    from ichimoku_analyzer.data.fetcher import DataFetcher
    from ichimoku_analyzer.indicators.ichimoku import IchimokuCalculator
    from ichimoku_analyzer.scoring.checklist import ChecklistScorer
    from ichimoku_analyzer.scoring.ranker import StockRanker

    # 여러 종목 분석
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    print(f"\n종목 분석 중: {symbols}")

    fetcher = DataFetcher()
    calculator = IchimokuCalculator()
    scorer = ChecklistScorer()

    data_dict = {}
    score_results = {}

    for symbol in symbols:
        print(f"  {symbol}...", end=" ")
        df = fetcher.fetch(symbol, 'us')

        if df is not None and fetcher.validate_data(df):
            df_ichimoku = calculator.calculate_all(df)
            score_info = scorer.calculate_score(df_ichimoku)

            data_dict[symbol] = df_ichimoku
            score_results[symbol] = score_info

            print(f"✅ {score_info['total_score']}점 ({score_info['grade']})")
        else:
            print("❌")

    # 순위 산정
    ranker = StockRanker()
    ranking_df = ranker.rank_stocks(score_results)
    ranking_df = ranker.add_price_info(ranking_df, data_dict)

    print("\n✅ 순위 산정 완료")
    print("\n순위 테이블:")
    print(ranking_df.to_string(index=False))

    return ranking_df


def main():
    """메인 테스트 실행"""
    print("\n" + "=" * 50)
    print("일목균형표 자동 분석 시스템 - 테스트")
    print("=" * 50)

    try:
        # 1. 데이터 수집
        df = test_data_fetcher()

        if df is None:
            print("\n❌ 데이터 수집 실패 - 테스트 중단")
            return

        # 2. 일목균형표 계산
        df_ichimoku = test_ichimoku_calculator(df)

        # 3. 점수 계산
        score_info = test_checklist_scorer(df_ichimoku)

        # 4. 순위 산정
        ranking_df = test_ranker()

        print("\n" + "=" * 50)
        print("✅ 모든 테스트 완료!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
