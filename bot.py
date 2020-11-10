# bot.py
import os
import asyncio

import discord
from discord.ext import commands
from discord.utils import get

import random
import time

# Poll Global Variables
poll_message = None
choice1 = -1
choice2 = -1

bot = commands.Bot(command_prefix='?')


def getTimestamp():
    current_time = time.localtime()
    if len(str(current_time.tm_min)) == 1:
        tmin = '0' + str(current_time.tm_min)
    else:
        tmin = str(current_time.tm_min)

    if current_time.tm_hour > 12:
        thour = current_time.tm_hour - 12
        tmin += 'PM'
    elif current_time.tm_hour == 0:
        thour = 12
        tmin += 'AM'
    else:
        thour = current_time.tm_hour
        tmin += 'AM'
        
    stamp = f'{current_time.tm_year}.{current_time.tm_mon}.{current_time.tm_mday}_{thour}.{tmin}'
    return stamp

token_file = open('tokens.txt', 'r')
log_file = open(f'logs/{getTimestamp()}.txt', 'w')

vitup_quotes = open('quotes/vitup_quotes.txt', 'r').readlines()
support_quotes = open('quotes/support_quotes.txt', 'r').readlines()

tokens = token_file.readlines()

TOKEN = tokens[0]
GUILD = tokens[1]

def log(message):
    stamp = getTimestamp()

    print(f'[{stamp}]', message)
    log_file.write(f'[{stamp}]' + ' ' + message + '\n')

def create_pollchart(choice1_prompt, choice1_count, choice2_prompt, choice2_count):
    green_square = '\N{LARGE GREEN SQUARE}'
    red_square = '\N{LARGE RED SQUARE}'

    c1 = choice1_count
    c2 = choice2_count

    # Get rid of bot votes
    if c1 == -1:
        c1 = 0
    if c2 == -1:
        c2 = 0
    if c1 < -1 or c2 <-1:
        raise TooManyPolls
    
    total_count = c1 + choice2_count
    choice1_percent = c1 / total_count
    choice2_percent = c2 / total_count
    
    linechart = []
    for _ in range(int(choice1_percent * 135)):
        linechart.append(green_square)
    for _ in range(int(choice2_percent * 135)):
        linechart.append(red_square)
    if len(linechart) != 135:
        linechart.append(red_square) # Slight edge to RED in some cases but oh whale.
    
    linechart = ''.join(linechart)
    linechart_labeled = f'{linechart}\n\n{green_square} **{choice1_prompt}** : {round(choice1_percent, 2) * 100}%\n{red_square} **{choice2_prompt}** : {round(choice2_percent, 2) * 100}%'
    
    return linechart_labeled


@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    log(f'{bot.user.name} has connected to {guild.name}!')
    log(f'{guild.name}(id: {guild.id})')

    await bot.change_presence(activity=discord.Game(name="BEARISH SENTIMENT"))
    
    global SERVER_NAME
    SERVER_NAME = guild.name

@bot.event
async def on_member_join(member):
    log(f'{member.name} has joined the server!')
    
    
    # In-server Message
    stocks_channel = bot.get_channel(755913947173093500)
    welcome_message = f"Welcome **{member.name}**!"
    message = discord.Embed(title="**[NEW MEMBER]**", description= welcome_message, color=0xffc0cb)
    await stocks_channel.send(embed=message)

    # Random Role
    randrole = ('Partnered Equally', 'Same as everyone', 'Equal Partner')[random.randrange(0, 3)]
    role = discord.utils.get(member.guild.roles, name=randrole)
    await member.add_roles(role)
    
    # DM Message
    await member.create_dm()
    await member.dm_channel.send(
        f'Hey **{member.name}**, welcome to **{SERVER_NAME}**!\nCheck out the different channels and meet some new people!'
    )
    ''' WORK ON LATER
    await member.dm_channel.send(
        f'You have been assigned the **[UNDER CONSTRUCTION]** role. The role that you have recived does not matter!'
    )
    await member.dm_channel.send(
        f'Please take a look at the rules : [UNDER CONSTRUCTION]'
    )
    '''
    


@bot.event
async def on_reaction_add(reaction, user):
    global choice1
    global choice2
    if reaction.emoji == '\N{THUMBS UP SIGN}':
        choice1 +=1
    elif reaction.emoji == '\N{THUMBS DOWN SIGN}':
        choice2 +=1
    '''
    if user == bot.user:
        return
    if reaction.emoji == '\N{THUMBS UP SIGN}':
        test = discord.utils.get(user.guild.roles, name="test")
        await user.add_roles(test)
    '''

@bot.event
async def on_reaction_remove(reaction, user):
    global choice1
    global choice2
    if reaction.emoji == '\N{THUMBS UP SIGN}':
        choice1 -=1
    elif reaction.emoji == '\N{THUMBS DOWN SIGN}':
        choice2 -=1
    '''
    if reaction.message == poll_message and reaction.emoji == '\N{THUMBS UP SIGN}':
        test = discord.utils.get(user.guild.roles, name="test")
        await user.remove_roles(test)
    '''


@bot.command(name='chartbotguideline')
async def showRules(ctx):
    guidelines_list = """
**CHART COMMANDS**
```css\n!cd [ticker]```returns daily chart for given ticker.
```css\n!c3m/!c5m/!c15m [ticker]```returns 3m, 5m, 15m charts for given ticker. respectively.
```css\n!chart2 [ticker]```returns 6-month chart for given ticker.
```css\n!chart_gold```returns the chart for Gold futures.
```css\n!chart_silver```returns the chart for Silver futures.
```css\n!chart_eurusd```returns the chart for EUR/USD Forex.
```css\n!optionchain [ticker]```returns option chain for given ticker.
```css\n!heatmap```returns 1-day heatmap.
```css\n!heatmapw```returns 1-week heatmap.

\n**FinViz COMMANDS**
```css\n!unusualvol```returns top 10 stocks with unusual volume.
```css\n!upgrades```returns analyst upgraded stocks.
```css\n!overbought```returns top most overbought stocks.
```css\n!oversold```returns top most oversold stocks.
```css\n!newhighs```returns the top stocks making new 52-week highs.
```css\n!newlows```returns the top stocks making new 52-week lows.

\n**OTHER COMMANDS**
```css\n!tostock```returns top 20 stock option volume.
```css\n!calendar```returns day economic calander events.
```css\n!insider [ticker]```returns insider information for given ticker.
```css\n!ipolist```returns IPO's for the month.
```css\n!topnews```returns top news from CNBC.

\n**CRYPTO COMMANDS**
```css\n!btc```returns Bitcoin price.
```css\n!eth```returns Ethreum price.

"""
    print(guidelines_list)
    guidelines = discord.Embed(title="**[CHART BOT GUIDELINES]**\n*(updated : 9/20/19)*", description= guidelines_list, color=0x7ec0ee)
    message = await ctx.send(embed = guidelines)

@bot.command(name='botguideline')
async def showRules(ctx):
    guidelines_list = """
**CHART COMMANDS**
```css\n?earnings```returns 'Earnings Whisper' calendar.

**POLL COMMANDS**
```css\n?pollopen [y/n question]```opens poll with given prompt.
```css\n?pollclose```closes poll and returns results.

\n**MISC COMMANDS**
```css\n?bullish```returns 'bullish' image.
```css\n?keepbuying```returns 'keep buying' image.
```css\n?gm```returns 'good morning' image.

"""
    print(guidelines_list)
    guidelines = discord.Embed(title="**[BOT GUIDELINES]**\n*(updated : 9/20/19)*", description= guidelines_list, color=0x7ec0ee)
    message = await ctx.send(embed = guidelines)
    
@bot.command(name='pollopen', help="TEST")          
async def poll(ctx, *, text):
    global choice1
    global choice2
    global poll_message
    
    if choice1 != -1 or choice2 != -1:
        await ctx.send('A poll is already open.')
        return
    
    vote = discord.Embed(title="**[POLL]**", description=f'{text}', color=0x7ec0ee)
    poll_message = await ctx.send(embed = vote)

    for emoji in ('\N{THUMBS UP SIGN}','\N{THUMBS DOWN SIGN}'):
        await poll_message.add_reaction(emoji)

@bot.command(name='pollclose', help="TEST")          
async def poll(ctx):
    global choice1
    global choice2
    
    
    pollchart = create_pollchart('Yes', choice1, 'No', choice2)

    message = await ctx.send('**Ballots are in!**')        
    result = discord.Embed(title="**[POLL RESULTS]**", description= pollchart, color=0xb19cd9)
    message = await ctx.send(embed = result)
    
    choice1 = -1
    choice2 = -1

@bot.command(name='sentopen', help="Opens sentiment poll.")          
async def poll(ctx, *, period):
    if choice1 != -1 or choice2 != -1:
        await ctx.send('A poll is already open.')
        return
    global poll_message
    vote = discord.Embed(title="**[POLL]**", description=f'Are you bullish or bearish for {period}? Vote now!', color=0x7ec0ee)
    image = await ctx.send('https://zehnerdavenport.com/wp-content/uploads/2016/09/ZD-Bull-Bear-05.jpg')

    poll_message = await ctx.send(embed = vote)

    for emoji in ('\N{THUMBS UP SIGN}','\N{THUMBS DOWN SIGN}'):
        await poll_message.add_reaction(emoji)

@bot.command(name='sentclose', help="Closes sentiment poll.")          
async def poll(ctx):
    global choice1
    global choice2

    message = await ctx.send('**Ballots are in!**')
    pollchart = create_pollchart('Bullish', 4, 'Bearish', 0)
    
    result = discord.Embed(title="**[POLL RESULTS]**", description= pollchart, color=0xb19cd9)
    message = await ctx.send(embed = result)
    if choice1 > choice2:
        await bot.change_presence(activity=discord.Game(name="BULLISH SENTIMENT"))
    elif choice2 > choice1:
        await bot.change_presence(activity=discord.Game(name="BEARISH SENTIMENT"))
    elif choice1 == choice2:
        await bot.change_presence(activity=discord.Game(name="NEUTRAL SENTIMENT"))
    choice1 = -1
    choice2 = -1

@bot.command(name='earnings', help="Displays earnings this week.")
async def earnings(ctx):
    await ctx.send("Here are this week's earnings : ")
    await ctx.send("https://cdn.discordapp.com/attachments/755913947173093500/757107425542144010/EiRauxJXcAAv6yP.png")
@bot.command(name='bullish', help="TEST")          
async def bullish(ctx):
    await ctx.send('https://i.imgur.com/h3yvqEH.jpg')
@bot.command(name='gm', help="Displays 'good morning' image.")          
async def goodmorning(ctx):
    await ctx.send('https://tenor.com/view/good-morning-good-vibes-dancing-kid-girl-gif-16219018')
@bot.command(name='keepbuying', help="Displays 'keep buying' image.")          
async def keepbuying(ctx):
    await ctx.send('https://cdn.discordapp.com/attachments/755913947173093500/757304846293532742/MPu5dfM.jpg')
@bot.command(name='buythedip', help="Displays 'buy the dip' gif.") 
async def buydip(ctx):
    await ctx.send('https://tenor.com/view/bitcoin-btd-btfd-btc-buythedip-gif-18083191')
@bot.command(name='buytfdip', help="Displays 'buy the dip' gif.") 
async def buyfdip(ctx):
    await ctx.send('https://i.postimg.cc/XNRVbrJm/buytfdip.png')
@bot.command(name='bearcorrection', help="Displays 'bear correction' image.") 
async def bearcorrection(ctx):
    await ctx.send('https://tradebrains.in/wp-content/uploads/2018/07/stock-market-meme-22.jpg')    
@bot.command(name='support', help="Emotionally supports you.")          
async def emotional_support(ctx):
    global support_quotes
    quote = random.choice(support_quotes)    
    message = discord.Embed(title="**[Therapist Speaks]**", description= quote, color=0xd2b48c)
    await ctx.send(embed=message)
    
@bot.command(name='vitup', help="Flames you.")          
async def vitup_support(ctx):
    global vitup_quotes
    quote = random.choice(vitup_quotes)
    message = discord.Embed(title="**[Bully Speaks]**", description= quote, color=0xd2b48c)

    await ctx.send(embed=message)

@bot.command(name='announce', help="Emotionally supports you.")          
async def announce(ctx, *, text):
    announcement_channel = bot.get_channel(757362655500435526)
    quote = f'{text}'    
    message = discord.Embed(title="**[Announcement]**", description= quote, color=0xffa500)
    message = await announcement_channel.send(embed=message)

@commands.has_role('bot guy')
@bot.command(pass_context=True)
async def changenick(ctx, member: discord.Member, nick):
    await member.edit(nick=nick)
    await ctx.send(f'Nickname was changed for {member.mention}')

# Exception handling
@bot.event
async def on_command_error(ctx, error):
    announcement_channel = bot.get_channel(757427973191237713)
    print(error)
    log(f'{ctx.author} used a command that resulted in an error.')
    error_message = f'**Member** : {ctx.author} \n**Error** : {error}'    
    message = discord.Embed(title="**[Error]**", description= error_message, color=0xFF0000)
    message = await announcement_channel.send(embed=message)

bot.run(TOKEN)
