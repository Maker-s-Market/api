import enum


class Status(str, enum.Enum):
    Pending = "Pending"
    Confirmed = "Confirmed"
    Delivered = "Delivered"
    Cancelled = "Cancelled"
    Returned = "Returned"
    Refunded = "Refunded"
