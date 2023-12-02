import enum


class Status(str, enum.Enum):
    Accepted = "Accepted"
    In_Expedition = "In Expedition"
    Delivered = "Delivered"
