import asyncio
import discord
import inspect
import aiohttp
import utils
import os
import math
import re
import time
import subprocess
import psutil
from discord import Game
from discord.ext import commands
from discord.ext.commands import Bot
from config import emotes
from config import config
from utils.embed import Embeds
from utils import checks
from utils.config import Config
from utils.cog import Cog

class BotOptions(Cog):
    @commands.group(name='bot',
                    description="Manage settings for the bot.",
                    brief="Manage settings for the bot.")
    @checks.is_owner()
    async def manbot(self, ctx):
        if ctx.invoked_subcommand is None:
            emb = Embeds.create_embed(self, ctx,
            "Bot Manager " + emotes.Warn,
            0xffff00,
            "Please issue a valid subcommand!\nAvailable options are:",
            Com1 = ["invite", "Gets the invite URL for the bot.", False],
            Com2 = ["avatar", "Changes the bots Avatar.", False],
            Com3 = ["username", "Changes the bots Username.", False],
            Com4 = ["die", "Shutdown the bot. Running under PM2 will restart the bot instead.", False],
            Com5 = ["update", "Updates the bot. If the bot was not installed using Git, this will just reload all cogs in config.py.", False])
            await ctx.message.channel.send(embed=emb)

    @manbot.command(name='invite',
                description="Gets the bots invite url!",
                brief="Gets the bots invite url!",
                aliases=['Invite'])
    async def invite(self, ctx):
        emb = discord.Embed()
        emb.title = "Invite URL"
        emb.description = "<https://discordapp.com/oauth2/authorize?client_id={0}&scope=bot&permissions=8>".format(str(self.bot.user.id))
        emb.color = 0x00ffff
        emb.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.message.channel.send(embed=emb)

    @manbot.command(name='avatar',
                    description="Changes the bots avatar!",
                    brief="Changes the bots avatar!",
                    aliases=['Avatar'])
    async def avatar(self, ctx, msg=None):
        self.aiosession = aiohttp.ClientSession(loop=self.bot.loop)
        emb = discord.Embed()
        emb.title = "Avatar Changed!"
        emb.color = 0x00ff00
        picture = msg.strip('<>')
        emb.set_thumbnail(url=msg)
        emb.description = "Avatar successfully changed to " + msg

        async with self.aiosession.get(picture) as res:
            await self.bot.user.edit(avatar=await res.read())
            await ctx.message.channel.send(embed=emb)

    @manbot.command(name='username',
                    description="Changes the bots username!",
                    brief="Changes the bots username!",
                    aliases=['Username'])
    async def username(self, ctx, msg):
        emb = discord.Embed()
        emb.title = "Username Changed!"
        emb.color = 0x00ff00
        emb.set_thumbnail(url=self.bot.user.avatar_url)
        emb.description = "Username successfully changed to " + msg
        await self.bot.user.edit(username=msg)
        await ctx.message.channel.send(embed=emb)

    @manbot.command(name='die',
                    description="Shuts down the bot, or restarts it while under pm2.",
                    brief="Shuts down the bot",
                    aliases=['sd', 'shutdown'])
    async def die(self, ctx):
        print(str(ctx.message.author) + " triggered a shutdown!")
        await ctx.message.channel.send(embed=discord.Embed(description=emotes.Done + " " + self.bot.user.name + " is now shutting down... " + ctx.message.author.mention, color=0x0035ff))
        await self.bot.logout()

    @manbot.command(name='update',
                description="Update the bot through git.",
                brief="Update the bot through git.")
    async def update(self, ctx):
        process = subprocess.Popen(['git', 'pull'], stdout=subprocess.PIPE)
        out, err = process.communicate()
        emb = discord.Embed()
        emb.title = "Bot Updater"
        emb.color = 0x00aaff
        msg = ''
        for cog in config.Modules:
                try:
                    self.bot.unload_extension(cog)
                    self.bot.load_extension(cog)
                    msg += '+Successfully reloaded mod {0}\n\n'.format(cog)
                except Exception as e:
                    msg += '-Error reloading mod {0}\n-{1}: {2}\n\n'.format(cog, type(e).__name__, e)
        emb.description = "Bot has updated to the latest commit in repository.\nAll mods in `config.py` have attempted to be reloaded.\nIt is advised that you restart if anything outside the mods folder was updated."
        emb.add_field(name="Cog Loader", value="```diff\n{}```".format(msg), inline=False)
        if len(out.decode('utf8')) <= 500:
            emb.add_field(name="Update Output", value="```http\n{}```".format(out.decode('utf8')), inline=False)
        else:
            emb.add_field(name="Update Output", value="```md\n#Output longer than 500 chars, see text file for output.```", inline=False)
        print("Bot has updated to the latest commit in repository.\nAll mods in `config.py` have attempted to be reloaded.\nIt is advised that you restart if anything outside the mods folder was updated.")
        print(msg)
        print(out.decode('utf8'))
        f = open("output.txt","w+")
        f.write(out.decode('utf8'))
        f.close()
        await ctx.message.channel.send(embed=emb)
        if len(out.decode('utf8')) >=500:
            await ctx.message.channel.send(file=discord.File('output.txt'))
        os.remove('output.txt')

    async def on_message(self, msg:discord.Message):
        self.bot.messages_seen += 1
    
    @commands.command(name='eval',
                description="Owner Only!",
                brief="Owner Only!",
                aliases=['debug', 'Eval', 'Debug'])
    @checks.is_owner()
    async def debug(self, ctx, *, code : str):
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None
        env = {
            'self': self,
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'return': code
        }
        env.update(globals())
        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.message.channel.send(embed=discord.Embed(colour=discord.Colour(0xff0000), title=emotes.Terminal+" Python Eval", description=python.format(type(e).__name__ + ': ' + str(e))))
            return
        await ctx.message.channel.send(embed=discord.Embed(colour=discord.Colour(0x0094ff), title=emotes.Terminal+" Python Eval", description=python.format(result)))

    @commands.command(name='exec',
                description="Owner Only!",
                brief="Owner Only!")
    @checks.is_owner()
    async def exec(self, ctx, *, code : str):
        code = code.strip('``` ')
        python = '```py\n{}\n```'
        result = None
        env = {
            'self': self,
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'return': code
        }
        env.update(globals())
        try:
            result = exec(code, env)
        except Exception as e:
            await ctx.message.channel.send(embed=discord.Embed(colour=discord.Colour(0xff0000), title=emotes.Terminal+" Python Exec", description=python.format(type(e).__name__ + ': ' + str(e))))
            return
        await ctx.message.channel.send(embed=discord.Embed(colour=discord.Colour(0x0094ff), title=emotes.Terminal+" Python Exec", description=python.format(result)))

    @commands.command(name='usereval',
                description="Owner Only!",
                brief="Owner Only!")
    @checks.is_owner()
    async def debug(self, ctx, user:discord.User, *, code : str):
        code = code.strip('` ')
        python = '```py\n{}\n```'
        result = None
        env = {
            'self': self,
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'user': user,
            'return': code
        }
        env.update(globals())
        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.message.channel.send(embed=discord.Embed(colour=discord.Colour(0xff0000), title=emotes.Terminal+" Python Eval", description=python.format(type(e).__name__ + ': ' + str(e))))
            return
        await ctx.message.channel.send(embed=discord.Embed(colour=discord.Colour(0x0094ff), title=emotes.Terminal+" Python Eval", description=python.format(result)))

def setup(bot):
    bot.add_cog(BotOptions(bot))
