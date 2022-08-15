import interactions
from osu_auth.auth import Auth
from database._init_db import Database

class CustomInteractionsClient(interactions.Client):
    def __init__(self, token, **kwargs):
        super().__init__(token, **kwargs)
        self.auth = Auth()
        self.database = Database('database.db')