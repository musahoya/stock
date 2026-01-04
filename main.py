#!/usr/bin/env python3
"""
일목균형표 자동 분석 시스템 - 메인 실행 스크립트
커맨드라인에서 빠른 분석 실행
"""
import argparse
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ichimoku_analyzer.data.fetcher import DataFetcher
from ichimoku_analyzer.indicators.ichimoku import IchimokuCalculator
from ichimoku_analyzer.scoring.checklist import ChecklistScorer
from ichimoku_analyzer.scoring.ranker import StockRanker
from ichimoku_analyzer.config.settings import DEFAULT_SYMBOLS


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="일목균형표 자동 분석 시스템"
    )

    parser.add_argument(
        '--market',
        '-m',
        choices=['us', 'kr', 'crypto'],
        default='us',
        help='시장 타입 (기본: us)'
    )

    parser.add_argument(
        '--symbols',
        '-s',
        nargs='+',
        help='분석할 종목 리스트'
    )

    parser.add_argument(
        '--output',
        '-o',
        type=str,
        help='결과 저장 파일명 (CSV)'
    )

    parser.add_argument(
        '--min-score',
        type=int,
        default=0,
        help='최소 점수 필터'
    )

    parser.add_argument(
        '--top',
        type=int,
        help='상위 N개만 표시'
    )

    args = parser.parse_args()

    # 종목 리스트 설정
    if args.symbols:
        symbols = args.symbols
    else:
        symbols = DEFAULT_SYMBOLS.get(args.market, [])
        print(f"기본 종목 사용: {symbols}")

    if not symbols:
        print("❌ 분석할 종목이 없습니다.")
        return

    print(f"📊 일목균형표 자동 분석 시작")
    print(f"시장: {args.market}")
    print(f"종목 수: {len(symbols)}")
    print("-" * 50)

    # 1. 데이터 수집
    print("📥 데이터 수집 중...")
    fetcher = DataFetcher()
    data_dict = {}

    for i, symbol in enumerate(symbols, 1):
        print(f"  [{i}/{len(symbols)}] {symbol}", end=" ... ")

        df = fetcher.fetch(symbol, args.market)

        if df is not None and fetcher.validate_data(df):
            data_dict[symbol] = df
            print("✅")
        else:
            print("❌")

    if not data_dict:
        print("❌ 수집된 데이터가 없습니다.")
        return

    print(f"✅ {len(data_dict)}/{len(symbols)} 종목 데이터 수집 완료\n")

    # 2. 일목균형표 계산
    print("📊 일목균형표 계산 중...")
    calculator = IchimokuCalculator()

    for symbol in data_dict.keys():
        data_dict[symbol] = calculator.calculate_all(data_dict[symbol])

    print("✅ 일목균형표 계산 완료\n")

    # 3. 점수 계산
    print("🎯 점수 계산 중...")
    scorer = ChecklistScorer()
    score_results = {}

    for symbol, df in data_dict.items():
        score_info = scorer.calculate_score(df)
        score_results[symbol] = score_info

    print("✅ 점수 계산 완료\n")

    # 4. 순위 산정
    print("🏆 순위 산정 중...")
    ranker = StockRanker()
    ranking_df = ranker.rank_stocks(score_results)
    ranking_df = ranker.add_price_info(ranking_df, data_dict)

    # 필터 적용
    if args.min_score > 0:
        ranking_df = ranker.filter_by_score(ranking_df, args.min_score)

    if args.top:
        ranking_df = ranker.get_top_n(ranking_df, args.top)

    print("✅ 순위 산정 완료\n")

    # 5. 결과 출력
    print("=" * 80)
    print("📊 분석 결과")
    print("=" * 80)
    print(ranking_df.to_string(index=False))
    print("=" * 80)

    # 요약 정보
    summary = ranker.generate_summary(ranking_df)
    print("\n📈 요약 정보")
    print(f"  총 종목 수: {summary['total_stocks']}")
    print(f"  평균 점수: {summary['average_score']:.2f}")
    print(f"  최고 득점: {summary['top_stock']} ({summary['top_score']}점)")
    print(f"  등급 분포: {summary['grade_distribution']}")

    # 파일 저장
    if args.output:
        ranking_df.to_csv(args.output, index=False, encoding='utf-8-sig')
        print(f"\n💾 결과 저장: {args.output}")

    print("\n✅ 분석 완료!")


if __name__ == "__main__":
    main()
