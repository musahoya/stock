"""
일목균형표 체크리스트 항목 및 가중치 정의
"""

# 상승 매매 체크리스트 (총 48점 만점)
CHECKLIST_ITEMS = {
    # 기본 배치 (9점)
    'chikou_above_price': {
        'name': '후행스팬이 캔들 위',
        'weight': 3,
        'description': '후행스팬이 26일 전 가격보다 위에 위치'
    },
    'current_cloud_bullish': {
        'name': '현재 구름 양운',
        'weight': 3,
        'description': '현재 선행스팬A > 선행스팬B (양운)'
    },
    'future_cloud_bullish': {
        'name': '앞쪽 구름 양운',
        'weight': 3,
        'description': '26일 선행 구름도 양운'
    },

    # 가격 위치 (3점)
    'price_above_cloud': {
        'name': '주가가 구름 위',
        'weight': 3,
        'description': '현재가가 구름 상단보다 위'
    },

    # 호전 관련 (9점)
    'tenkan_kijun_cross': {
        'name': '호전 발생',
        'weight': 3,
        'description': '전환선이 기준선을 상향 돌파'
    },
    'no_kijun_break_after_cross': {
        'name': '호전 후 기준선 하회 없음',
        'weight': 3,
        'description': '호전 이후 가격이 기준선 아래로 내려가지 않음'
    },
    'kijun_trend': {
        'name': '기준선 상승/수평',
        'weight': 3,
        'description': '기준선이 상승 또는 수평'
    },

    # 지지 확인 (5점)
    'tenkan_support': {
        'name': '전환선 지지',
        'weight': 2,
        'description': '최근 N일 내 전환선에서 지지'
    },
    'kijun_support': {
        'name': '기준선 지지',
        'weight': 3,
        'description': '최근 N일 내 기준선에서 지지'
    },

    # 후행+호전 동시 (6점)
    'chikou_breakout': {
        'name': '후행스팬 상향 돌파',
        'weight': 3,
        'description': '후행스팬이 과거 가격을 상향 돌파'
    },
    'chikou_and_tenkan_cross': {
        'name': '후행+호전 동시 발생',
        'weight': 3,
        'description': '후행스팬 돌파와 호전이 동시에 발생'
    },

    # 구름 돌파 (5점)
    'cloud_breakout': {
        'name': '구름 상향 돌파',
        'weight': 3,
        'description': '가격이 구름을 상향 돌파'
    },
    'cloud_support_after_breakout': {
        'name': '구름 돌파 후 상단 지지',
        'weight': 2,
        'description': '돌파 후 구름 상단에서 지지 확인'
    },

    # 특수 패턴 (6점)
    'thin_cloud_breakout': {
        'name': '얇은 구름 상향 돌파',
        'weight': 2,
        'description': '구름 두께가 가격의 2% 미만일 때 돌파'
    },
    'cloud_twist_bottom': {
        'name': '음→양 교차 바닥',
        'weight': 2,
        'description': '구름 색깔 변화 + 저점 갱신 실패'
    },
    'squeeze_kijun_support': {
        'name': '협착 후 기준선 지지',
        'weight': 2,
        'description': '전환선·기준선 간격 축소 후 지지'
    }
}

# 총점 계산
TOTAL_POINTS = sum(item['weight'] for item in CHECKLIST_ITEMS.values())

# 체크 조건 설정
CHECK_CONDITIONS = {
    'lookback_period': 5,        # 최근 N일 확인
    'cross_lookback': 10,        # 크로스 감지 기간
    'thin_cloud_threshold': 0.02, # 얇은 구름 기준 (2%)
    'squeeze_threshold': 0.03     # 협착 기준 (3%)
}
