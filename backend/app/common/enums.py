from enum import Enum

try:
    from enum import StrEnum
except ImportError:  # pragma: no cover
    class StrEnum(str, Enum):
        pass


class WorkStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class MaterialUnit(StrEnum):
    GRAM = "gram"
    MILLILITER = "milliliter"
    PIECE = "piece"
    PACK = "pack"
    HOUR = "hour"
