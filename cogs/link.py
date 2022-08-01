import interactions, asyncio
from embed.osu import create_osu_embed
class Link(interactions.Extension): # must have interactions.Extension or this wont work
    def __init__(self, client):
        self.client: interactions.Client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
            name="link", 
            description="links your discord account to an osu! account",
            options=[interactions.Option(
                name="username",
                description="the username of the osu! account you want to link to",
                type=interactions.OptionType.STRING,
                required=True,
            )
        ]
    )
    async def link(self, ctx: interactions.CommandContext, username: str):
        await ctx.defer()
        discord_id = ctx.author.id._snowflake
        alter_account = False
        if await self.database.get_link(discord_id):
            # Checks if we are modifying an account or adding a new one to the db
            alter_account = True
        
        # get osu account details
        osu_account_data = await self.osu.get_user(username)
        if not(osu_account_data):
            await ctx.send(f"User {username} was not found on osu! - did you write it correctly?")
            return
        
        if alter_account is False:
            await self.database.add_link(discord_id, osu_account_data['id'])
            await ctx.send(f"<@{discord_id}> has been linked to {username}!")
            return
        else:
            await self.database.update_link(discord_id, osu_account_data['id'])
            await ctx.send(f"<@{discord_id}> has been linked to {username}!")
            return


def setup(client):
    Link(client)