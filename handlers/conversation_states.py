# conversation_states.py
from enum import IntEnum, auto

class ConversationState(IntEnum):
    USERNAME = auto()
    PASSWORD = auto()
    MENU = auto()
    WAITING_FOR_URL = auto()
    WAITING_FOR_USERNAME = auto()
    WAITING_FOR_HASHTAG = auto()
    WAITING_FOR_MEDIA = auto()
    WAITING_FOR_CAPTION = auto()
    WAITING_FOR_UPLOAD_TYPE = auto()
    WAITING_FOR_URL_DOWNLOAD = auto()
    WAITING_FOR_LANGUAGE = auto()
    CODE = auto()
    EMAIL = auto()
    PASSWORD_EMAIL = auto()