"""
일일 정기 배치 실행 스크립트
"""
import schedule
import time
import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ichimoku_analyzer.data.fetcher import DataFetcher
from ichimoku_analyzer.indicators.ichimoku import IchimokuCalculator
from ichimoku_analyzer.scoring.checklist import ChecklistScorer
from ichimoku_analyzer.scoring.ranker import StockRanker
from ichimoku_analyzer.config.settings import DEFAULT_SYMBOLS, ALERT_CONFIG
from ichimoku_analyzer.utils.alerts import send_telegram_alert, format_high_score_alert, format_daily_summary


def run_daily_analysis(market_type: str = 'us'):
    """
    일일 정기 분석 실행

    Args:
        market_type: 시장 타입
    """
    print(f"[{datetime.now()}] 일일 분석 시작 - {market_type}")

    try:
        # 종목 리스트
        symbols = DEFAULT_SYMBOLS.get(market_type, [])

        if not symbols:
            print(f"No symbols configured for market: {market_type}")
            return

        # 데이터 수집
        print("Fetching data...")
        fetcher = DataFetcher()
        data_dict = {}

        for symbol in symbols:
            df = fetcher.fetch(symbol, market_type)
            if df is not None and fetcher.validate_data(df):
                data_dict[symbol] = df

        if not data_dict:
            print("No data collected")
            return

        # 일목균형표 계산
        print("Calculating Ichimoku indicators...")
        calculator = IchimokuCalculator()

        for symbol in data_dict.keys():
            data_dict[symbol] = calculator.calculate_all(data_dict[symbol])

        # 점수 계산
        print("Calculating scores...")
        scorer = ChecklistScorer()
        score_results = {}

        for symbol, df in data_dict.items():
            score_info = scorer.calculate_score(df)
            score_results[symbol] = score_info

        # 순위 산정
        print("Ranking stocks...")
        ranker = StockRanker()
        ranking_df = ranker.rank_stocks(score_results)
        ranking_df = ranker.add_price_info(ranking_df, data_dict)

        # 결과 저장
        results_dir = project_root / 'results'
        results_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = results_dir / f'{market_type}_ranking_{timestamp}.csv'

        ranking_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Results saved: {output_file}")

        # 요약 정보
        summary = ranker.generate_summary(ranking_df)

        # 알림 전송 (설정되어 있는 경우)
        if ALERT_CONFIG['telegram_enabled']:
            # 고득점 종목 알림
            high_score_msg = format_high_score_alert(
                ranking_df,
                ALERT_CONFIG['high_score_threshold']
            )

            if high_score_msg:
                send_telegram_alert(
                    ALERT_CONFIG['telegram_token'],
                    ALERT_CONFIG['telegram_chat_id'],
                    high_score_msg
                )

            # 일일 요약
            summary_msg = format_daily_summary(summary)
            send_telegram_alert(
                ALERT_CONFIG['telegram_token'],
                ALERT_CONFIG['telegram_chat_id'],
                summary_msg
            )

        print(f"[{datetime.now()}] 일일 분석 완료")

    except Exception as e:
        print(f"Error in daily analysis: {str(e)}")
        import traceback
        traceback.print_exc()


def run_all_markets():
    """모든 시장 분석 실행"""
    for market in ['us', 'kr', 'crypto']:
        run_daily_analysis(market)


if __name__ == "__main__":
    # 즉시 한 번 실행
    print("Starting immediate analysis...")
    run_all_markets()

    # 스케줄 설정 (매일 오전 9시)
    schedule.every().day.at("09:00").do(run_all_markets)

    print("Scheduler started. Press Ctrl+C to exit.")

    # 스케줄러 실행
    while True:
        schedule.run_pending()
        time.sleep(60)
