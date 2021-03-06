import os
from interactions import CommandContext, Option
import interactions

import mwclient

from DBHandler import DBHandler

bot_token = os.environ['TOKEN']

client = interactions.Client(bot_token)

dbHandler = DBHandler()
guilds = [775065533518708738]


@client.command(
    name="start",
    scope=guilds,
    description="Beginn Challenge.",
    options=[
        Option(
            name="order", 
            type=interactions.OptionType.BOOLEAN, 
            description="Order `A to Z` or `Z to A`",
            required=False)
    ])
async def start(ctx: CommandContext, order: bool):
    print(ctx)
    userId = ctx.author.id
    if dbHandler.check_if_key_exists(userId):
        await ctx.message(
            f"You already registered for the Challenge. View your progress with /Stats"
        )
    else:
        userName = ctx.author.name
        dummy_dict = dbHandler.generate_json_dummy(userId, order)
        dbHandler.add_key_value_pair(userId, dummy_dict)
        await ctx.send(f"user {userName} with Id {userId} has been saved!")


@client.command(
    name="show_all_champions",
    scope=guilds,
    description="display all Champs in alphabetical order"
)
async def show_all_champions(ctx: CommandContext):
    champs = grab_all_champions()
    message_template = ""
    for champion in champs:
        message_template += champion
    await ctx.send(message_template)


@client.command(
    name="current",
    scope=guilds, 
    description="display current champ progression")
async def current(ctx: CommandContext):
    print(ctx)
    userId = ctx.author.id
    if not dbHandler.check_if_key_exists(userId):
        await ctx.send(
            'You have not yet started the challenge. Do so with `/start`')
        return
    value = dbHandler.get_key_value(userId)
    currentChampId = value['currentChamp']
    currentChampTries = value['champs'][str(currentChampId)]['tries']
    currentChamp = dbHandler.champs[currentChampId - 1]
    await ctx.send(
        f"You're currently at {currentChamp} and have so far had {currentChampTries} Attemps at this Champion"
    )


@client.command(
    name="add_remove_attempts",
    scope=guilds,
    description="Add or remove one or multiple failed attempts to the current or one of the next champs",
    options=[
        Option(
            name="amount",
            type=interactions.OptionType.INTEGER,
            description="the Amount of attempts to add or remove to the champion [default: 1]",
            min_value=-10,
            max_value=10,
            required=False,
            default=1),
        Option(
            name="skip",
            type=interactions.OptionType.INTEGER,
            description="The amount of champs to skip from the current [default: 0]",
            required=False,
            default=0)
    ])
async def add_remove_attempts(ctx: CommandContext, amount=1, skip=0):
    value = dbHandler.get_key_value(ctx.author.id)
    currentChampId = value['currentChamp']
    actualChampId = value['currentChamp'] + skip
    value['champs'][str(actualChampId)]['tries'] += int(amount)
    currentChampTries = value['champs'][str(currentChampId)]['tries']
    actualChampTries = value['champs'][str(actualChampId)]['tries']
    currentChamp = dbHandler.champs[currentChampId - 1]
    actualChamp = dbHandler.champs[actualChampId - 1]
    AtoZ = value['isAtoZ']
    skip = skip * AtoZ

    if skip != 1:
        await ctx.send(
            f"You've added another attempts to {actualChamp} and are now at {actualChampTries} Attempts at this Champion"
        )
    await ctx.send(
        f"You're currently at {currentChamp} and have now had {currentChampTries} Attemps at this Champion"
    )
    return


@client.command(
    name="finish_champion",
    scope=guilds,
    description="Add a final attempts to a champion and mark it as finished",
    options=[
        Option(
            name="skip",
            type=interactions.OptionType.INTEGER,
            description="The amount of champs to skip from the current [default: 0]",
            required=False,
            default=0)
    ])
async def finish_champion(ctx: CommandContext, skip: int):
    if skip is None:
        skip = 0
    userId = ctx.author.id
    value = dbHandler.get_key_value(userId)
    currentChampId = value['currentChamp']
    actualChampId = value['currentChamp'] + skip
    actualChamp = dbHandler.champs[actualChampId - 1]
    value['champs'][str(actualChampId)]['tries'] += 1
    value['champs'][str(actualChampId)]['finished'] = True
    actualChampTries = value['champs'][str(actualChampId)]['tries']
    AtoZ = value['isAtoZ']
    skip = skip * AtoZ
    print(f"{skip=}")

    if skip != 0:
        nextChampId = currentChampId
        print(nextChampId, currentChampId)
    else:
        nextChampId = get_next_champ(dbHandler.champs, AtoZ, currentChampId,
                                     userId)
        print(nextChampId, currentChampId)
    if nextChampId == 0 or nextChampId == len(dbHandler.champs) + 1:
        await ctx.send('Congratulations! You have completed the challange!')
        return
    else:
        value['currentChamp'] = nextChampId
        nextChamp = dbHandler.champs[nextChampId - 1]
        print(f"{nextChamp=}, test")
        nextChampTries = value['champs'][str(nextChampId)]['tries']

    print(
        f"You're have finished {actualChamp} with {actualChampTries} Attemps.")
    print(
        f"Your new Champion is {nextChamp} with currently {nextChampTries} Attemps."
    )

    await ctx.send(
        f"You're have finished {actualChamp} with {actualChampTries} Attemps.")
    await ctx.send(
        f"Your new Champion is {nextChamp} with currently {nextChampTries} Attemps."
    )


@client.command(
    name="stats",
    scope=guilds, 
    description="List your current stats",
    options=[
        Option(
            name="finished_champs",
            type=interactions.OptionType.BOOLEAN,
            description="show finished champions",
            required=False,
            default=False),
        Option(
            name="started_champs",
            type=interactions.OptionType.BOOLEAN,
            description="show started champions",
            required=False,
            default=True),
        Option(
            name="winrate",
            type=interactions.OptionType.BOOLEAN,
            description="show winrate across all games",
            required=False,
            default=True)
    ])
async def stats(ctx: CommandContext, done: bool, started: bool, winrate: bool):
    base_str_1, base_str_2, done_str, base_str_3, started_str = dbHandler.grab_player_stats(
        ctx.author)
    print(base_str_1, done_str, base_str_2, started_str)
    await ctx.send(base_str_1)
    if done and done_str != "":
        await ctx.send(base_str_2)
        while len(done_str) > 0:
            to_send = done_str[:1999]
            done_str = done_str[2000:]
            await ctx.send(to_send)
    if started and started_str != "":
        await ctx.send(base_str_3)
        await ctx.send(started_str)
    if winrate:
        winRate_str_1, winRate_str_2 = dbHandler.get_winrate_for_id(ctx.author)
        await ctx.send(winRate_str_1)
        await ctx.send(winRate_str_2)


@client.event
async def on_ready():
		print(dbHandler.keys)
		print(f'We have logged in as {client.me.name}')


@client.event
async def on_message(message):
    userId = message.author.id
    print(message.content)
    if message.author == client.user:
        return

    if message.content.startswith('$show me'):
        value = dbHandler.get_key_value(userId)
        print(value)

    if message.content.startswith('$REMOVE ME NOW'):
        dbHandler.remove_key_value_pair(userId)
        await message.channel.send(
            'You quit the challenge successfully you looser.')


def get_next_champ(champs: list, AtoZ: bool, currentChamp: int, userId: int):
    foundNewChamp = False
    print("testtest")
    if check_if_challenge_is_won(userId):
        return 0
    nextChampId = currentChamp
    while not foundNewChamp and nextChampId >= 1 and nextChampId <= len(
            champs):
        if not dbHandler.check_if_champ_is_finished(userId, nextChampId):
            print(f"return {nextChampId=}")
            return nextChampId
        if AtoZ:
            nextChampId = nextChampId + 1
            print(f"{nextChampId=} = {currentChamp=} + 1")
        else:
            nextChampId = nextChampId - 1
            print(f"{nextChampId=} = {currentChamp=} - 1")


def grab_all_champions():
    site = mwclient.Site('lol.fandom.com', path='/')
    query_response = site.api('cargoquery',
                              limit="max",
                              tables="Champions=Ch",
                              fields="Ch.Name")

    champs = [
        champ_dict['title']['Name']
        for champ_dict in query_response['cargoquery']
    ]

    return champs


def check_if_challenge_is_won(userId):
    return dbHandler.is_user_finished(userId)

client.start()
