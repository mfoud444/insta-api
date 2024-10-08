from typing import List, Dict

import os
from pathlib import Path
# Define the session directory relative to the app structure
BASE_DIR = Path(__file__).resolve().parent.parent  # This points to the app root
# SESSION_DIR = BASE_DIR / 'assets' / 'settings'

# Alternatively, you can use os.path as well
SESSION_DIR = os.path.join(BASE_DIR, 'assets', 'settings')

# Create the directory if it doesn't exist (optional)
# SESSION_DIR.mkdir(parents=True, exist_ok=True)
class UserAccount:
    def __init__(self, username_telegram: str, username_instagram: str, chat_id: int, is_active: bool, is_login: bool):
        self.username_telegram = username_telegram
        self.username_instagram = username_instagram
        self.chat_id = chat_id
        self.is_active = is_active
        self.is_login = is_login
        self.uploader = {}

class AccountGroup:
    def __init__(self, name: str, accounts: List[UserAccount]):
        self.name = name
        self.accounts = accounts

class Config:
    def __init__(self):
        self._config = {
            "supabase": {
                "url": "https://fvpmikdmeystnnxnloqe.supabase.co",
                "key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ2cG1pa2RtZXlzdG5ueG5sb3FlIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTY5NDQ1OTYsImV4cCI6MjAxMjUyMDU5Nn0.2M-NejfxfGlU1guyRIfNKL7kE94WysWj_T-NmFXypSg"
            },
            "bot_token": "8052659086:AAEgETCBhOodKd-yVZv6IlC6ZCzmSsWiLbw",
        }
        self.account_groups = self._init_account_groups()

    def _init_account_groups(self) -> List[AccountGroup]:
        return [
            AccountGroup("mfoud", [
                UserAccount("mfoud1", "mfoud555", 11, True, False),
                UserAccount("mfoud444", "mfoud444", 11, True, False)
            ]),
            AccountGroup("yazan", [
                UserAccount("e63_oo", "e.96_5", 11, True, False),
                UserAccount("yazan2", "hhhh", 11, False, False)
            ])
        ]

    def get(self, key: str, default=None):
        return self._config.get(key, default)

    @property
    def supabase(self) -> Dict:
        return self._config.get('supabase', {})

    def get_user_account(self, username_telegram: str) -> UserAccount:
        for group in self.account_groups:
            for account in group.accounts:
                if account.username_telegram == username_telegram:
                    return account
        return None

    def get_all_active_accounts(self) -> List[UserAccount]:
        return [account for group in self.account_groups for account in group.accounts if account.is_active]