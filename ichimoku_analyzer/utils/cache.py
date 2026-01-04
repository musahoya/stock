"""
데이터 캐싱 유틸리티
"""
import pickle
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCache:
    """
    데이터 캐시 관리 클래스
    """

    def __init__(self, cache_dir: str = 'cache'):
        """
        Args:
            cache_dir: 캐시 디렉토리 경로
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_path(self, symbol: str, market: str) -> Path:
        """
        캐시 파일 경로 생성

        Args:
            symbol: 종목 심볼
            market: 시장 타입

        Returns:
            캐시 파일 경로
        """
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"{market}_{symbol}_{date_str}.pkl"
        return self.cache_dir / filename

    def is_cache_valid(self, cache_path: Path, max_age_hours: int = 1) -> bool:
        """
        캐시 유효성 확인

        Args:
            cache_path: 캐시 파일 경로
            max_age_hours: 최대 유효 시간 (시간)

        Returns:
            유효하면 True
        """
        if not cache_path.exists():
            return False

        cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age = datetime.now() - cache_time

        return age < timedelta(hours=max_age_hours)

    def save_data(self, data, symbol: str, market: str):
        """
        데이터 캐시 저장

        Args:
            data: 저장할 데이터
            symbol: 종목 심볼
            market: 시장 타입
        """
        cache_path = self.get_cache_path(symbol, market)

        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"Cached data saved: {cache_path}")
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")

    def load_data(self, symbol: str, market: str, max_age_hours: int = 1):
        """
        캐시 데이터 로드

        Args:
            symbol: 종목 심볼
            market: 시장 타입
            max_age_hours: 최대 유효 시간

        Returns:
            캐시된 데이터 또는 None
        """
        cache_path = self.get_cache_path(symbol, market)

        if not self.is_cache_valid(cache_path, max_age_hours):
            return None

        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            logger.info(f"Loaded from cache: {cache_path}")
            return data
        except Exception as e:
            logger.error(f"Error loading cache: {str(e)}")
            return None

    def clear_cache(self, older_than_days: int = 7):
        """
        오래된 캐시 파일 삭제

        Args:
            older_than_days: N일 이전 캐시 삭제
        """
        cutoff_time = datetime.now() - timedelta(days=older_than_days)
        deleted_count = 0

        for cache_file in self.cache_dir.glob('*.pkl'):
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)

            if file_time < cutoff_time:
                cache_file.unlink()
                deleted_count += 1

        logger.info(f"Cleared {deleted_count} old cache files")

    def get_cache_size(self) -> str:
        """
        캐시 디렉토리 크기 확인

        Returns:
            크기 문자열 (예: '10.5 MB')
        """
        total_size = sum(
            f.stat().st_size for f in self.cache_dir.glob('**/*') if f.is_file()
        )

        # 적절한 단위로 변환
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total_size < 1024.0:
                return f"{total_size:.1f} {unit}"
            total_size /= 1024.0

        return f"{total_size:.1f} TB"
