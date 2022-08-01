import interactions


class Ping(interactions.Extension):  # must have interactions.Extension or this wont work
    def __init__(self, client):
        self.client: interactions.Client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="ping",
        description="toggle user pings for when you get sniped",
        options=[interactions.Option(
            name="pinging",
            description="toggle if you want pinging after being sniped on or off",
            type=interactions.OptionType.BOOLEAN,
            required=True,
        )
        ]
    )
    async def ping(self, ctx, *args, **kwargs):
        await ctx.defer()
        discord_id = ctx.author.id._snowflake
        if not(await self.database.get_link(discord_id)):
            await ctx.send(f"You need to link your osu! account first! Use `/link`")
            return
        pinging = kwargs['pinging']
        if pinging:
            await self.database.update_ping(True, discord_id)
            await ctx.send(f"Pinging has been turned on for <@{discord_id}>")
            return
        await self.database.update_ping(False, discord_id)
        await ctx.send(f"Pinging has been turned off for <@{discord_id}>")
        return

def setup(client):
    Ping(client)
