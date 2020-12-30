
from typing import Literal
import json
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config
from mcstatus import MinecraftServer
import discord
import asyncio
mcserver = MinecraftServer.lookup("45.79.54.32:25565")
RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]
import datetime
from redbot.core.utils.predicates import ReactionPredicate
from redbot.core.utils.menus import start_adding_reactions

class minecraft(commands.Cog):
     """
     TPUN Minecraft cog
     """

     def __init__(self, bot: Red) -> None:
          self.bot = bot
          self.config = Config.get_conf(
               self,
               identifier=None,
               force_registration=True,
          )
    
     async def checks(self, id, empty, ctx):
          print(id)
          channel = self.bot.get_channel(id)
          await asyncio.sleep(60)
          if len(channel.members) == 0:
               empty.set_result('VC is Empty!')
               print("0 members in " + str(channel.name))
               reason = "channel is empty"
               await asyncio.sleep(300)
               await minecraft.delete(self, ctx, reason)
               await empty.set_result("Channel deleted")
          else:
               await minecraft.checks(self, vcName, id, empty, ctx)
     def pred(self, emojis, mess1):
          return ReactionPredicate.with_emojis(emojis, mess1)
     async def emojiSorter(self, ctx, emoji, mess1):
          if emoji == "🎮":
               try:
                    await self.create(ctx, str(ctx.message.author.activity.name))
                    print(str(ctx.message.author.activity.name))
                    await mess1.delete()
               except IndexError:
                    await ctx.send("You can't make a game channel if you aren't playing a game.")
                    print("no activity")
                    await mess1.delete()
          elif emoji == "📱":
               print(str(ctx.author.name) + "'s social channel")
               await self.create(ctx, str(ctx.author.name) + "'s social channel")
               print("social")
               await mess1.delete()
          elif emoji == "❓":
               print(str(ctx.author.name) + "'s pvc")
               await self.create(ctx, str(ctx.author.name) + "'s pvc")
               print("Other")
               await mess1.delete()

     async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int) -> None:
          # TODO: Replace this with the proper end user data removal handling.
          super().red_delete_data_for_user(requester=requester, user_id=user_id)
     @commands.group(name='minecraft')
     async def minecraft(self, ctx):
          pass
     @minecraft.command(name='status')
     async def status(self, ctx):
          status = mcserver.status()
          await ctx.send("The tpun FTB Revelations server has {0} players and replied in {1} ms".format(status.players.online, status.latency))
     @minecraft.command(name='online')
     async def online(self, ctx):
          query = mcserver.query()
          await ctx.send("The tpun FTB Revelations server has the following players online: {0}".format(", ".join(query.players.names)))
     @minecraft.command(name='ip')
     async def ip(self, ctx):
          await ctx.send("The tpun FTB Revelations server ip is 45.79.54.32:25565")

     @commands.group(name='vc')
     async def vc(self, ctx):
          pass
     @vc.command(name='help')
     async def help(self, ctx, arg):
          if arg == '':
               pass
          elif arg == 'create':
               await ctx.send("Creates a voice channel with [name] t!vc create [Name]. You can only have 1 vc. VC deletes after 5 minutes of inactivity. You must join your vc within 1 minute or it will be deleted.")
          elif arg == 'delete':
               await ctx.send("Deletes your personal channel, requires a reason t!delete reason. Channels delete on their own after 5 minutes of being empty.")
     @vc.command(name='create', description='Creates a voice channel with [name] t!vc create [Name]. You can only have 1 vc. VC deletes after 5 minutes of inactivity. You must join your vc within 1 minute or it will be deleted.')
     async def create(self, ctx, arg):
          category = ctx.channel.category
          jsonPath = "/root/discordbot/data/tpunbot/cogs/Minecraft/vcOwners.json"
          run = "true"
          if arg == "":
               await ctx.send("You need to type a voice channel name t!vc create [Name]")
          else:
               #finds out who called the command, saves author as owner
               owner = ctx.author.name
               #save arg as vcName
               vcName = arg
               #opens json file for read
               with open(jsonPath, 'r') as vcOwners:
               #load vcOwners
                    try:
                         x = json.load(vcOwners)
                         #closes json file from read
                         for vcOwnList, vcId in x.items():
                              #check if user has a vc by going through vcOwners
                              if vcOwnList == owner:
                                   await ctx.send("You already have a vc created named {0}".format(str(self.bot.get_channel(vcId).name)))
                                   run = "false"
                         if run == "false":
                              pass
                         else:
                                   #create vc with arg as name
                                   channel = await ctx.guild.create_voice_channel(vcName, category=category)
                                   #create json object nC
                                   nC = {owner : vcId}
                                   x.update(nC)
                                   print(x)
                                   #add vcOwner and vcName to json
                                   await ctx.send("VC created by {0} with name {1}".format(owner, str(self.bot.get_channel(vcId).name)))
                                   print(vcId)
                                   empty = asyncio.Future()
                                   asyncio.ensure_future(self.checks(vcId, empty, ctx))
                    except ValueError:
                         if x == "":
                              x = {}
                         else:
                              pass
               with open(jsonPath, 'w') as vcWrite:
                    try:
                         json.dump(x, vcWrite)
                    except ValueError:
                         print("Json write failed.")
    
     @vc.command(name='delete', description='Deletes your personal channel, can include a reason t!vc delete "reason". Channels delete on their own after 5 minutes of being empty.')
     async def delete(self, ctx, reason = None):
          noVC = "true"
          if reason == None:
               reason = "user deleted their own channel"
          elif reason == "channel is empty":
               noVC = "false"
          run = "false"
          owner = ctx.author.name
          with open('/root/discordbot/data/tpunbot/cogs/Minecraft/vcOwners.json', 'r') as vcOwners:
               try:
                    x = json.load(vcOwners)
                    for vcOwnList, idList in x.items():
                         if vcOwnList == owner:
                              run = "true"
                              vcId = idList
               except ValueError:
                    await ctx.send("Failed to load vc Owners.")
          if run == "true":
               with open('/root/discordbot/data/tpunbot/cogs/Minecraft/vcOwners.json', 'w') as vcWrite:
                    try:
                         channel = self.bot.get_channel(vcId)
                         vcName = str(channel.name)
                         await channel.delete()
                         print("deleted")
                         x.pop(owner, None)
                         json.dump(x, vcWrite)
                         #does a check to see if we delete the last entry in json files. Adds {} to json file because json doesn't play nice with empty files.
                         if x == "":
                              x = "{}"
                         await ctx.send("Succesfully deleted {2}'s voice channel {0} because {1}".format(vcName, reason, owner))
                    except ValueError:
                         await ctx.send("Failed to delete your vc.")
          else:
               if noVC == "true":
                    await ctx.send("You can't delete a VC if you don't have one.")
     @vc.command(name='name', description='Gives you the name of your personal vc, not really useful since your voice channel deletes 5 minutes after being empty.')
     async def name(self, ctx):
          owner = ctx.author.name
          with open('/root/discordbot/data/tpunbot/cogs/Minecraft/vcOwners.json', 'r') as vcOwners:
               try:
                    x = json.load(vcOwners)
                    for vcOwnList, vcNameList in x.items():
                         if vcOwnList == owner:
                             await ctx.send("Your personal vc is named {0}.".format(vcNameList))
                         else:
                             pass
               except ValueError:
                    await ctx.send("You have no vc created use t!vc create [Name] to create one.")
     @vc.command(name="gui", description="Brings up gui for making you own voice channel")
     async def gui(self, ctx):
          #gets channel for bot message
          dsChannel = 793599653387567123
          channel = self.bot.get_channel(dsChannel)
          #vcrole1 = get(creator.guild.roles, id=703562188224331777)
          if ctx.message.channel.id == dsChannel:
               #if any(role.id == 703562188224331777 for role in ctx.message.author.roles):
                    #await creator.remove_roles(vcrole1)
                    #await ctx.send("not important message")
                    #messtag1 = await channel.send('not important') 
                    #await messtag1.delete(delay=None)

                    embed = discord.Embed(color=0xe02522, title='Voice Channel Creator', description= 'Creates a personal voice channel.')
                    embed.set_footer(text='This gui is opened by /vc gui. It allows you to create your own voice channel that will delete itself after 1 minute of being empty on creation or 5 minutes of being empty. You can delete it by using /vc delete <reason>. 🎮 for game channel, 📱 for social channel, ❓ for other channel')
                    embed.timestamp = datetime.datetime.utcnow()

                    mess1 = await channel.send(embed=embed)
                    emojis = ["🎮","❓", "📱"]
                    start_adding_reactions(mess1, emojis)
                    try:
                         result = await ctx.bot.wait_for("reaction_add", timeout=60.0, check=self.pred(emojis, mess1))
                         print(result[0])
                         emoji = str(result[0])
                         await self.emojiSorter(ctx, emoji, mess1)
                    except asyncio.TimeoutError:
                         await channel.send('Voice channel gui timed out.')
                         await mess1.delete()
                    else:
                         pass
                    