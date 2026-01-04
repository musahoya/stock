"""
Streamlit 대시보드 UI 컴포넌트
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List


def display_ranking_table(ranking_df: pd.DataFrame):
    """
    순위 테이블 표시

    Args:
        ranking_df: 순위 DataFrame
    """
    if ranking_df.empty:
        st.warning("분석 결과가 없습니다.")
        return

    # 등급별 색상 매핑
    def color_grade(val):
        color_map = {
            'A': 'background-color: #90EE90',  # 연한 녹색
            'B': 'background-color: #87CEEB',  # 연한 파란색
            'C': 'background-color: #F0E68C',  # 연한 노란색
            'D': 'background-color: #FFA07A',  # 연한 주황색
            'F': 'background-color: #FFB6C1'   # 연한 분홍색
        }
        return color_map.get(val, '')

    # 스타일 적용
    styled_df = ranking_df.style.applymap(
        color_grade,
        subset=['grade']
    ).format({
        'percentage': '{:.2f}%',
        'current_price': '{:.2f}' if 'current_price' in ranking_df.columns else None,
        'price_change_pct': '{:+.2f}%' if 'price_change_pct' in ranking_df.columns else None
    })

    st.dataframe(styled_df, use_container_width=True, height=400)


def display_score_details(score_info: Dict, symbol: str):
    """
    점수 상세 정보 표시

    Args:
        score_info: 점수 정보 딕셔너리
        symbol: 종목 심볼
    """
    st.subheader(f"{symbol} - 상세 분석")

    # 점수 요약
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("총점", f"{score_info['total_score']}/{score_info['max_score']}")

    with col2:
        st.metric("퍼센트", f"{score_info['percentage']:.2f}%")

    with col3:
        grade_color = {
            'A': '🟢', 'B': '🔵', 'C': '🟡', 'D': '🟠', 'F': '🔴'
        }
        st.metric("등급", f"{grade_color.get(score_info['grade'], '')} {score_info['grade']}")

    with col4:
        grade_text = {
            'A': '강력 매수',
            'B': '적극 매수',
            'C': '신중 매수',
            'D': '관망',
            'F': '부적절'
        }
        st.metric("판정", grade_text.get(score_info['grade'], ''))

    st.divider()

    # 체크리스트 상세
    st.subheader("체크리스트 상세")

    details = score_info.get('details', [])

    if details:
        # 통과/실패 분리
        passed_items = [d for d in details if d['passed']]
        failed_items = [d for d in details if not d['passed']]

        # 통과 항목
        st.markdown("### ✅ 통과 항목")
        if passed_items:
            for item in passed_items:
                with st.expander(f"{item['name']} ({item['weight']}점)", expanded=False):
                    st.write(item['description'])
        else:
            st.info("통과한 항목이 없습니다.")

        st.divider()

        # 실패 항목
        st.markdown("### ❌ 미통과 항목")
        if failed_items:
            for item in failed_items:
                with st.expander(f"{item['name']} ({item['weight']}점)", expanded=False):
                    st.write(item['description'])
        else:
            st.success("모든 항목을 통과했습니다!")


def display_ichimoku_chart(df: pd.DataFrame, symbol: str):
    """
    일목균형표 차트 표시 (선택사항)

    Args:
        df: 일목균형표 지표가 포함된 DataFrame
        symbol: 종목 심볼
    """
    st.subheader(f"{symbol} - 일목균형표 차트")

    # 최근 100일 데이터만 표시
    plot_df = df.tail(100).copy()

    fig = go.Figure()

    # 캔들스틱
    fig.add_trace(go.Candlestick(
        x=plot_df.index,
        open=plot_df['open'],
        high=plot_df['high'],
        low=plot_df['low'],
        close=plot_df['close'],
        name='Price',
        increasing_line_color='red',
        decreasing_line_color='blue'
    ))

    # 전환선
    fig.add_trace(go.Scatter(
        x=plot_df.index,
        y=plot_df['tenkan_sen'],
        mode='lines',
        name='전환선 (Tenkan)',
        line=dict(color='red', width=1)
    ))

    # 기준선
    fig.add_trace(go.Scatter(
        x=plot_df.index,
        y=plot_df['kijun_sen'],
        mode='lines',
        name='기준선 (Kijun)',
        line=dict(color='blue', width=1)
    ))

    # 선행스팬A
    fig.add_trace(go.Scatter(
        x=plot_df.index,
        y=plot_df['senkou_span_a'],
        mode='lines',
        name='선행스팬A',
        line=dict(color='green', width=1, dash='dot')
    ))

    # 선행스팬B
    fig.add_trace(go.Scatter(
        x=plot_df.index,
        y=plot_df['senkou_span_b'],
        mode='lines',
        name='선행스팬B',
        line=dict(color='orange', width=1, dash='dot'),
        fill='tonexty',
        fillcolor='rgba(0,250,0,0.1)'
    ))

    # 레이아웃
    fig.update_layout(
        title=f'{symbol} 일목균형표',
        yaxis_title='Price',
        xaxis_title='Date',
        height=600,
        xaxis_rangeslider_visible=False,
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)


def display_summary_stats(ranking_df: pd.DataFrame, summary: Dict):
    """
    요약 통계 표시

    Args:
        ranking_df: 순위 DataFrame
        summary: 요약 정보 딕셔너리
    """
    st.subheader("분석 요약")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("전체 종목 수", summary.get('total_stocks', 0))

    with col2:
        st.metric("평균 점수", f"{summary.get('average_score', 0):.2f}")

    with col3:
        st.metric("최고 득점 종목", f"{summary.get('top_stock', 'N/A')}")

    # 등급 분포
    st.subheader("등급 분포")
    grade_dist = summary.get('grade_distribution', {})

    if grade_dist:
        grade_df = pd.DataFrame([
            {'등급': grade, '종목 수': count}
            for grade, count in sorted(grade_dist.items(), reverse=True)
        ])

        st.bar_chart(grade_df.set_index('등급'))


def display_filter_options():
    """
    필터 옵션 표시

    Returns:
        필터 설정 딕셔너리
    """
    st.sidebar.subheader("필터 옵션")

    min_grade = st.sidebar.selectbox(
        "최소 등급",
        options=['전체', 'A', 'B', 'C', 'D'],
        index=0
    )

    min_score = st.sidebar.slider(
        "최소 점수",
        min_value=0,
        max_value=48,
        value=0,
        step=1
    )

    show_chart = st.sidebar.checkbox("차트 표시", value=False)

    return {
        'min_grade': None if min_grade == '전체' else min_grade,
        'min_score': min_score,
        'show_chart': show_chart
    }


def display_progress(current: int, total: int, message: str = ""):
    """
    진행률 표시

    Args:
        current: 현재 진행 수
        total: 전체 수
        message: 표시할 메시지
    """
    progress = current / total if total > 0 else 0
    st.progress(progress, text=f"{message} ({current}/{total})")
