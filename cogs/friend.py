import interactions
from embed.osu import create_osu_embed
class Friend(interactions.Extension): # must have commands.cog or this wont work
    def __init__(self, client):
        self.client: interactions.Client = client
        self.osu = client.auth
        self.database = client.database

    @interactions.extension_command(
        name="friend",
        description="add to, remove, or check a main users friend list",
        options= [interactions.Option(
            name="add",
            description="provide the username of the player you want to add",
            type=interactions.OptionType.STRING,
        ),
        interactions.Option(
            name="remove",
            description="provide the username of the player you want to remove",
            type=interactions.OptionType.STRING,
        ),
        interactions.Option(
            name="list",
            description="provide the username of the main user you want to list the friends of",
            type=interactions.OptionType.STRING,
    )],
    )
    async def __test(self, ctx: interactions.CommandContext, *args, **kwargs):
        if len(kwargs)>1:
            await ctx.send("Too many arguments!")
            return
        elif len(kwargs) == 0:
            await ctx.send("Please select an argument `add`, `remove`, or `list`")
            return
        elif len(kwargs) == 1:
            if kwargs["add"] is not None:
                await self.handle_add(ctx, kwargs["add"])
            elif kwargs["remove"] is not None:
                await self.handle_remove(ctx, kwargs["remove"])
            elif kwargs["list"] is not None:
                await self.handle_list(ctx, kwargs["list"])

    async def handle_add(self, ctx, username: str):
        user_data = await self.osu.get_user_data(username)
        if user_data:
            if not(await self.database.get_friend_from_channel(user_data["id"], ctx.channel_id._snowflake)):
                await self.database.add_friend(ctx.channel_id._snowflake, user_data)
                await ctx.send(f"Added {user_data['username']} to the friend list!")
                # if they arent a main user or a friend you should scan their plays on all beatmaps next TODO
            else:
                await ctx.send(f"{user_data['username']} is already in the friend list!")
                return
        else:
            await ctx.send(f"Could not find the user {username} on the osu! servers")
            return

    async def handle_remove(self, username: str):
        pass

    async def handle_list(self, username: str):
        pass

def setup(client):
    Friend(client)