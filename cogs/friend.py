import interactions
from embed.friend_list import create_friend_list_embed
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
    async def friend(self, ctx: interactions.CommandContext, *args, **kwargs):
        if len(kwargs)>1:
            await ctx.send("Too many arguments!")
            return
        elif len(kwargs) == 0:
            await ctx.send("Please select an argument `add`, `remove`, or `list`")
            return
        elif len(kwargs) == 1:
            if "add" in kwargs:
                await self.handle_add(ctx, kwargs["add"])
            elif "remove" in kwargs:
                await self.handle_remove(ctx, kwargs["remove"])
            elif "list" in kwargs:
                await self.handle_list(ctx, kwargs["list"])

    async def handle_add(self, ctx, username: str):
        message = await ctx.send(f"Adding {username} to the friend list...")
        user_data = await self.osu.get_user_data(username)
        if user_data:
            if not(await self.database.get_friend_from_channel(user_data["id"], ctx.channel_id._snowflake)):
                await self.database.add_friend(ctx.channel_id._snowflake, user_data)
                await message.reply(f"Added {user_data['username']} to the friend list!")
                # if they arent a main user or a friend you should scan their plays on all beatmaps next TODO
            else:
                await message.reply(f"{user_data['username']} is already in the friend list!")
                return
        else:
            await message.reply(f"Could not find the user {username} on the osu! servers")
            return
        

    async def handle_remove(self, ctx, username: str):
        message = await ctx.send(f"Removing {username} from the friend list...")
        if username.isupper() or username.islower(): # check if contains letters
            user_data = await self.osu.get_user_data(username)
            if user_data:
                if (await self.database.get_friend_from_channel(user_data['id'], ctx.channel_id._snowflake)):
                    await self.database.delete_friend(user_data['id'], ctx.channel_id._snowflake)
                    await message.reply(f"Removed {user_data['username']} from the friend list!")
                else:
                    await message.reply(f"User {user_data['username']} isn't in the friend list, so cannot be removed")
            else:
                await message.reply(f"Could not find the user {username} on the osu! servers, please try using their id")
                return
        else:
            if (await self.database.get_friend_from_channel(username, ctx.channel_id._snowflake)):
                await self.database.delete_friend(username, ctx.channel_id._snowflake)
                await ctx.send(f"Removed {user_data['username']} from the friend list!")

    async def handle_list(self, ctx, username: str):
        message = await ctx.send(f"Generating Friends List...")
        if (await self.database.get_channel_from_username(username)):
            user_data = await self.osu.get_user_data(username)
            channel = await self.database.get_channel_from_username(username)
            friends = await self.database.get_user_friends(channel[0])
            embed = await create_friend_list_embed(user_data, friends)
            await message.reply(embeds=embed)
        else:
            await message.reply(f"User {username} is not a main user")

def setup(client):
    Friend(client)