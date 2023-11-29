import enum

#was necessary to create a seperate file because of circular imports
class Role(str, enum.Enum):
    Client = "Client"
    Premium = "Premium"