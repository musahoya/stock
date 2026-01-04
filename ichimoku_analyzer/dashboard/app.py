"""
일목균형표 자동 분석 시스템 - Streamlit 대시보드
"""
import streamlit as st
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ichimoku_analyzer.data.fetcher import DataFetcher
from ichimoku_analyzer.indicators.ichimoku import IchimokuCalculator
from ichimoku_analyzer.scoring.checklist import ChecklistScorer
from ichimoku_analyzer.scoring.ranker import StockRanker
from ichimoku_analyzer.config.settings import DEFAULT_SYMBOLS
from ichimoku_analyzer.dashboard.components import (
    display_ranking_table,
    display_score_details,
    display_ichimoku_chart,
    display_summary_stats,
    display_filter_options,
    display_progress
)

# 페이지 설정
st.set_page_config(
    page_title="일목균형표 자동 분석 시스템",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """메인 애플리케이션"""

    # 제목
    st.title("📈 일목균형표 자동 분석 시스템")
    st.markdown("""
    **객관적 데이터 기반 일목균형표 분석 시스템**

    차트의 추상성을 배제하고 숫자 기반의 객관적 의사결정을 지원합니다.
    """)

    st.divider()

    # 사이드바 설정
    st.sidebar.header("⚙️ 설정")

    # 시장 선택
    market = st.sidebar.selectbox(
        "시장 선택",
        options=["미국 주식", "한국 주식", "암호화폐"],
        index=0
    )

    market_type_map = {
        "미국 주식": "us",
        "한국 주식": "kr",
        "암호화폐": "crypto"
    }
    market_type = market_type_map[market]

    # 기본 종목 리스트
    default_symbols = DEFAULT_SYMBOLS.get(market_type, [])

    # 종목 선택
    st.sidebar.subheader("종목 선택")

    # 사전 정의 종목 선택
    selected_defaults = st.sidebar.multiselect(
        "기본 종목",
        options=default_symbols,
        default=default_symbols[:5] if len(default_symbols) >= 5 else default_symbols
    )

    # 커스텀 종목 입력
    custom_symbols = st.sidebar.text_area(
        "추가 종목 (줄바꿈으로 구분)",
        placeholder="AAPL\nMSFT\nGOOGL" if market_type == "us" else "005930\n000660"
    )

    # 종목 리스트 합치기
    symbols = selected_defaults.copy()
    if custom_symbols:
        custom_list = [s.strip() for s in custom_symbols.split('\n') if s.strip()]
        symbols.extend(custom_list)

    # 중복 제거
    symbols = list(dict.fromkeys(symbols))

    st.sidebar.info(f"선택된 종목 수: {len(symbols)}")

    # 필터 옵션
    filter_options = display_filter_options()

    # 분석 실행 버튼
    analyze_button = st.sidebar.button("🚀 분석 시작", type="primary", use_container_width=True)

    # 세션 상태 초기화
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'data_dict' not in st.session_state:
        st.session_state.data_dict = None
    if 'score_results' not in st.session_state:
        st.session_state.score_results = None

    # 분석 실행
    if analyze_button:
        if not symbols:
            st.error("종목을 선택해주세요.")
            return

        run_analysis(symbols, market_type, filter_options)

    # 결과 표시
    if st.session_state.analysis_results is not None:
        display_results(filter_options)


def run_analysis(symbols, market_type, filter_options):
    """분석 실행"""

    with st.spinner("데이터 수집 및 분석 중..."):
        try:
            # 진행 상황 표시
            progress_placeholder = st.empty()
            status_placeholder = st.empty()

            # 1. 데이터 수집
            status_placeholder.info("📥 데이터 수집 중...")
            fetcher = DataFetcher()
            data_dict = {}

            for i, symbol in enumerate(symbols):
                progress_placeholder.progress(
                    (i + 1) / len(symbols),
                    text=f"데이터 수집 중... ({i + 1}/{len(symbols)})"
                )

                df = fetcher.fetch(symbol, market_type)

                if df is not None and fetcher.validate_data(df):
                    data_dict[symbol] = df
                else:
                    st.warning(f"⚠️ {symbol}: 데이터 수집 실패")

            if not data_dict:
                st.error("수집된 데이터가 없습니다.")
                return

            st.success(f"✅ {len(data_dict)}/{len(symbols)} 종목 데이터 수집 완료")

            # 2. 일목균형표 계산
            status_placeholder.info("📊 일목균형표 계산 중...")
            calculator = IchimokuCalculator()

            for i, symbol in enumerate(data_dict.keys()):
                progress_placeholder.progress(
                    (i + 1) / len(data_dict),
                    text=f"일목균형표 계산 중... ({i + 1}/{len(data_dict)})"
                )

                data_dict[symbol] = calculator.calculate_all(data_dict[symbol])

            st.success(f"✅ 일목균형표 계산 완료")

            # 3. 점수 계산
            status_placeholder.info("🎯 점수 계산 중...")
            scorer = ChecklistScorer()
            score_results = {}

            for i, (symbol, df) in enumerate(data_dict.items()):
                progress_placeholder.progress(
                    (i + 1) / len(data_dict),
                    text=f"점수 계산 중... ({i + 1}/{len(data_dict)})"
                )

                score_info = scorer.calculate_score(df)
                score_results[symbol] = score_info

            st.success(f"✅ 점수 계산 완료")

            # 4. 순위 산정
            status_placeholder.info("🏆 순위 산정 중...")
            ranker = StockRanker()
            ranking_df = ranker.rank_stocks(score_results)

            # 가격 정보 추가
            ranking_df = ranker.add_price_info(ranking_df, data_dict)

            # 요약 정보
            summary = ranker.generate_summary(ranking_df)

            # 세션 상태에 저장
            st.session_state.analysis_results = ranking_df
            st.session_state.data_dict = data_dict
            st.session_state.score_results = score_results
            st.session_state.summary = summary

            progress_placeholder.empty()
            status_placeholder.empty()

            st.success("🎉 분석 완료!")

        except Exception as e:
            st.error(f"❌ 분석 중 오류 발생: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


def display_results(filter_options):
    """결과 표시"""

    ranking_df = st.session_state.analysis_results
    data_dict = st.session_state.data_dict
    score_results = st.session_state.score_results
    summary = st.session_state.summary

    # 필터 적용
    ranker = StockRanker()
    filtered_df = ranking_df.copy()

    if filter_options['min_grade']:
        filtered_df = ranker.filter_by_grade(filtered_df, filter_options['min_grade'])

    if filter_options['min_score'] > 0:
        filtered_df = ranker.filter_by_score(filtered_df, filter_options['min_score'])

    # 요약 통계
    display_summary_stats(filtered_df, summary)

    st.divider()

    # 순위 테이블
    st.header("📊 분석 결과 - 순위")
    display_ranking_table(filtered_df)

    st.divider()

    # 상세 분석
    st.header("🔍 상세 분석")

    if not filtered_df.empty:
        # 종목 선택
        selected_symbol = st.selectbox(
            "종목 선택",
            options=filtered_df['symbol'].tolist(),
            format_func=lambda x: f"{x} (점수: {score_results[x]['total_score']}, 등급: {score_results[x]['grade']})"
        )

        if selected_symbol:
            # 점수 상세 정보
            display_score_details(score_results[selected_symbol], selected_symbol)

            # 차트 표시 (옵션)
            if filter_options['show_chart']:
                st.divider()
                display_ichimoku_chart(data_dict[selected_symbol], selected_symbol)

    else:
        st.info("필터 조건에 맞는 종목이 없습니다.")

    # 데이터 다운로드
    st.divider()
    st.header("💾 데이터 다운로드")

    col1, col2 = st.columns(2)

    with col1:
        # CSV 다운로드
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 순위 데이터 다운로드 (CSV)",
            data=csv,
            file_name='ichimoku_ranking.csv',
            mime='text/csv'
        )

    with col2:
        # 상세 점수 다운로드
        if st.button("📥 상세 점수 다운로드 (JSON)"):
            import json
            json_data = json.dumps(score_results, indent=2, default=str)
            st.download_button(
                label="다운로드",
                data=json_data,
                file_name='ichimoku_scores.json',
                mime='application/json'
            )


if __name__ == "__main__":
    main()
