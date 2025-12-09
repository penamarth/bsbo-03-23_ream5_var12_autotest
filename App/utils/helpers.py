import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


def generate_id(prefix: str = "") -> str:
    """Генерация уникального ID"""
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}{unique_id}" if prefix else unique_id


def format_duration(seconds: float) -> str:
    """Форматирование длительности в читаемый вид"""
    if seconds < 60:
        return f"{seconds:.2f} сек"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} мин"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} час"


def safe_json_serialize(obj: Any) -> str:
    """Безопасная сериализация в JSON"""
    def default_serializer(o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif hasattr(o, 'to_dict'):
            return o.to_dict()
        elif hasattr(o, '__dict__'):
            return o.__dict__
        else:
            return str(o)
    
    return json.dumps(obj, indent=2, ensure_ascii=False, default=default_serializer)


def parse_datetime(datetime_str: str) -> Optional[datetime]:
    """Парсинг строки даты-времени"""
    try:
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
        return None
    except (ValueError, TypeError):
        return None


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """Вычисление статистики по списку значений"""
    if not values:
        return {
            'count': 0,
            'mean': 0,
            'min': 0,
            'max': 0,
            'sum': 0
        }
    
    return {
        'count': len(values),
        'mean': sum(values) / len(values),
        'min': min(values),
        'max': max(values),
        'sum': sum(values)
    }


def validate_email(email: str) -> bool:
    """Простая валидация email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def get_timestamp() -> str:
    """Получение текущей временной метки"""
    return datetime.now().isoformat()


def human_readable_size(size_bytes: int) -> str:
    """Преобразование размера в байтах в читаемый вид"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"