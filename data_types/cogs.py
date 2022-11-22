from data_types.interactions import CustomInteractionsClient
import interactions


class Cog(interactions.Extension):
    def __init__(self, client: CustomInteractionsClient):
        self.client = client
        self.osu = client.auth
        self.database = client.database
