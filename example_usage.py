#!/usr/bin/env python3
"""
일목균형표 분석 시스템 사용 예제
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ichimoku_analyzer.data.fetcher import DataFetcher
from ichimoku_analyzer.indicators.ichimoku import IchimokuCalculator
from ichimoku_analyzer.scoring.checklist import ChecklistScorer
from ichimoku_analyzer.scoring.ranker import StockRanker


def example_1_single_stock():
    """예제 1: 단일 종목 분석"""
    print("=" * 60)
    print("예제 1: 단일 종목 분석 (AAPL)")
    print("=" * 60)

    # 1. 데이터 수집
    fetcher = DataFetcher()
    df = fetcher.fetch('AAPL', market_type='us')

    print(f"\n✅ 데이터 수집 완료: {len(df)}일")
    print(f"기간: {df.index[0].date()} ~ {df.index[-1].date()}")
    print(f"현재가: ${df.iloc[-1]['close']:.2f}")

    # 2. 일목균형표 계산
    calculator = IchimokuCalculator()
    df_ichimoku = calculator.calculate_all(df)

    print(f"\n✅ 일목균형표 계산 완료")

    latest = df_ichimoku.iloc[-1]
    print(f"전환선: ${latest['tenkan_sen']:.2f}")
    print(f"기준선: ${latest['kijun_sen']:.2f}")
    print(f"구름: {'양운' if latest['cloud_color'] == 1 else '음운'}")

    # 3. 점수 계산
    scorer = ChecklistScorer()
    score = scorer.calculate_score(df_ichimoku)

    print(f"\n✅ 점수 계산 완료")
    print(f"총점: {score['total_score']}/48")
    print(f"퍼센트: {score['percentage']:.2f}%")
    print(f"등급: {score['grade']}")

    # 통과 항목
    passed = [d for d in score['details'] if d['passed']]
    print(f"\n통과 항목 ({len(passed)}개):")
    for item in passed:
        print(f"  ✅ {item['name']} ({item['weight']}점)")

    print("\n")


def example_2_multiple_stocks():
    """예제 2: 여러 종목 비교 분석"""
    print("=" * 60)
    print("예제 2: 여러 종목 비교 분석")
    print("=" * 60)

    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']

    print(f"\n분석 종목: {', '.join(symbols)}")

    # 데이터 수집 및 분석
    fetcher = DataFetcher()
    calculator = IchimokuCalculator()
    scorer = ChecklistScorer()

    data_dict = {}
    score_results = {}

    for symbol in symbols:
        print(f"  {symbol}...", end=" ")

        df = fetcher.fetch(symbol, 'us')
        if df is not None:
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

    print("\n" + "=" * 60)
    print("📊 순위 결과")
    print("=" * 60)
    print(ranking_df.to_string(index=False))

    # 요약 정보
    summary = ranker.generate_summary(ranking_df)
    print("\n" + "=" * 60)
    print("📈 요약")
    print("=" * 60)
    print(f"평균 점수: {summary['average_score']:.2f}")
    print(f"최고 득점: {summary['top_stock']} ({summary['top_score']}점)")
    print(f"등급 분포: {summary['grade_distribution']}")

    print("\n")


def example_3_korean_stocks():
    """예제 3: 한국 주식 분석"""
    print("=" * 60)
    print("예제 3: 한국 주식 분석")
    print("=" * 60)

    # 종목 코드: 005930=삼성전자, 000660=SK하이닉스
    symbols = ['005930', '000660']

    fetcher = DataFetcher()
    calculator = IchimokuCalculator()
    scorer = ChecklistScorer()

    for symbol in symbols:
        print(f"\n종목코드: {symbol}")
        print("-" * 40)

        # 종목명 조회
        symbol_name = fetcher.get_symbol_name(symbol, 'kr')
        print(f"종목명: {symbol_name}")

        # 데이터 수집
        df = fetcher.fetch(symbol, market_type='kr')

        if df is not None:
            # 일목균형표 계산
            df_ichimoku = calculator.calculate_all(df)

            # 점수 계산
            score = scorer.calculate_score(df_ichimoku)

            print(f"점수: {score['total_score']}/48 ({score['percentage']:.2f}%)")
            print(f"등급: {score['grade']}")
            print(f"현재가: {df.iloc[-1]['close']:,.0f}원")

    print("\n")


def example_4_crypto():
    """예제 4: 암호화폐 분석"""
    print("=" * 60)
    print("예제 4: 암호화폐 분석")
    print("=" * 60)

    symbols = ['BTC/USDT', 'ETH/USDT']

    fetcher = DataFetcher()
    calculator = IchimokuCalculator()
    scorer = ChecklistScorer()

    for symbol in symbols:
        print(f"\n심볼: {symbol}")
        print("-" * 40)

        try:
            # 데이터 수집
            df = fetcher.fetch(symbol, market_type='crypto')

            if df is not None:
                # 일목균형표 계산
                df_ichimoku = calculator.calculate_all(df)

                # 점수 계산
                score = scorer.calculate_score(df_ichimoku)

                print(f"점수: {score['total_score']}/48 ({score['percentage']:.2f}%)")
                print(f"등급: {score['grade']}")
                print(f"현재가: ${df.iloc[-1]['close']:,.2f}")
        except Exception as e:
            print(f"❌ 오류: {str(e)}")

    print("\n")


def example_5_filtering():
    """예제 5: 필터링 및 고급 기능"""
    print("=" * 60)
    print("예제 5: 필터링 및 고급 기능")
    print("=" * 60)

    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'JPM']

    # 데이터 수집 및 분석
    fetcher = DataFetcher()
    calculator = IchimokuCalculator()
    scorer = ChecklistScorer()

    data_dict = {}
    score_results = {}

    print("\n데이터 수집 및 분석 중...")
    for symbol in symbols:
        df = fetcher.fetch(symbol, 'us')
        if df is not None:
            df_ichimoku = calculator.calculate_all(df)
            score_info = scorer.calculate_score(df_ichimoku)

            data_dict[symbol] = df_ichimoku
            score_results[symbol] = score_info

    # 순위 산정
    ranker = StockRanker()
    ranking_df = ranker.rank_stocks(score_results)
    ranking_df = ranker.add_price_info(ranking_df, data_dict)

    # 1. 등급별 필터링
    print("\n" + "=" * 60)
    print("1. B등급 이상 종목만 필터링")
    print("=" * 60)
    b_grade_stocks = ranker.filter_by_grade(ranking_df, 'B')
    print(b_grade_stocks.to_string(index=False))

    # 2. 점수별 필터링
    print("\n" + "=" * 60)
    print("2. 30점 이상 종목만 필터링")
    print("=" * 60)
    high_score_stocks = ranker.filter_by_score(ranking_df, 30)
    print(high_score_stocks.to_string(index=False))

    # 3. 상위 3개
    print("\n" + "=" * 60)
    print("3. 상위 3개 종목")
    print("=" * 60)
    top_3 = ranker.get_top_n(ranking_df, 3)
    print(top_3.to_string(index=False))

    # 4. CSV 저장
    output_file = 'example_ranking.csv'
    ranking_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n💾 결과 저장됨: {output_file}")

    print("\n")


def main():
    """모든 예제 실행"""
    print("\n" + "=" * 60)
    print("일목균형표 자동 분석 시스템 - 사용 예제")
    print("=" * 60)

    try:
        # 예제 1: 단일 종목
        example_1_single_stock()

        # 예제 2: 여러 종목 비교
        example_2_multiple_stocks()

        # 예제 3: 한국 주식 (선택사항)
        # example_3_korean_stocks()

        # 예제 4: 암호화폐 (선택사항)
        # example_4_crypto()

        # 예제 5: 필터링
        example_5_filtering()

        print("=" * 60)
        print("✅ 모든 예제 완료!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
