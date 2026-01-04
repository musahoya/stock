"""
알림 시스템 유틸리티
"""
import requests
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_telegram_alert(
    token: str,
    chat_id: str,
    message: str
) -> bool:
    """
    텔레그램 알림 전송

    Args:
        token: 텔레그램 봇 토큰
        chat_id: 채팅 ID
        message: 전송할 메시지

    Returns:
        성공 여부
    """
    if not token or not chat_id:
        logger.warning("Telegram credentials not configured")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

        logger.info("Telegram alert sent successfully")
        return True

    except Exception as e:
        logger.error(f"Error sending Telegram alert: {str(e)}")
        return False


def format_high_score_alert(results_df, threshold: int = 35) -> Optional[str]:
    """
    고득점 종목 알림 메시지 포맷

    Args:
        results_df: 순위 DataFrame
        threshold: 최소 점수 임계값

    Returns:
        포맷된 메시지 또는 None
    """
    high_score_stocks = results_df[results_df['total_score'] >= threshold]

    if high_score_stocks.empty:
        return None

    message = "🚀 *고득점 종목 발견!*\n\n"

    for _, row in high_score_stocks.iterrows():
        message += f"• *{row['symbol']}*\n"
        message += f"  점수: {row['total_score']}/{row['max_score']} ({row['percentage']:.1f}%)\n"
        message += f"  등급: {row['grade']}\n"

        if 'current_price' in row:
            message += f"  현재가: {row['current_price']:.2f}\n"

        message += "\n"

    return message


def format_daily_summary(summary: dict) -> str:
    """
    일일 요약 알림 메시지 포맷

    Args:
        summary: 요약 정보 딕셔너리

    Returns:
        포맷된 메시지
    """
    message = "📊 *일목균형표 일일 분석 요약*\n\n"

    message += f"총 분석 종목: {summary.get('total_stocks', 0)}\n"
    message += f"평균 점수: {summary.get('average_score', 0):.2f}\n\n"

    if summary.get('top_stock'):
        message += f"🏆 최고 득점: *{summary['top_stock']}*\n"
        message += f"점수: {summary['top_score']}\n\n"

    grade_dist = summary.get('grade_distribution', {})
    if grade_dist:
        message += "등급 분포:\n"
        for grade in ['A', 'B', 'C', 'D', 'F']:
            count = grade_dist.get(grade, 0)
            if count > 0:
                message += f"  {grade}급: {count}개\n"

    return message
