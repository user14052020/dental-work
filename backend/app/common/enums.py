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


class StockMovementType(StrEnum):
    OPENING_BALANCE = "opening_balance"
    RECEIPT = "receipt"
    RESERVE = "reserve"
    RELEASE = "release"
    CONSUME = "consume"
    RESTORE = "restore"
    ADJUSTMENT = "adjustment"
    INVENTORY = "inventory"


class ToothSelectionState(StrEnum):
    TARGET = "target"
    MISSING = "missing"


class ToothSurface(StrEnum):
    MESIAL = "mesial"
    DISTAL = "distal"
    VESTIBULAR = "vestibular"
    ORAL = "oral"
    OCCLUSAL = "occlusal"
    INCISAL = "incisal"


class OperationExecutionStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PatientGender(StrEnum):
    MALE = "male"
    FEMALE = "female"


class FaceShape(StrEnum):
    SQUARE = "square"
    OVAL = "oval"
    TRIANGLE = "triangle"


class PaymentMethod(StrEnum):
    CASH = "cash"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    SBP = "sbp"
    OTHER = "other"
