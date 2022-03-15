import os
from discord.ext import commands
from discord.commands import Option

import re

import mwclient

from DBHandler import DBHandler

bot_token = os.environ['TOKEN']

client = commands.Bot()

dbHandler = DBHandler()
guilds = [775065533518708738]


@client.slash_command(guild_ids=guilds, description="Beginn Challenge. ")
async def start(ctx, 
								order: Option(bool, "Order `A to Z` or `Z to A`")
							 ):
    userId = ctx.author.id
    if dbHandler.check_if_key_exists(userId):
        await ctx.respond(f"You already registered for the Challenge. View your progress with /TBD")
    else:
    		userName = ctx.author.name
    		dummy_dict = dbHandler.generate_json_dummy(userId, order)
    		dbHandler.add_key_value_pair(userId, dummy_dict)
    		await ctx.respond(f"user {userName} with Id {userId} has been saved!")

@client.slash_command(guild_ids=guilds, description="display all Champs in alphabetical order")
async def show_champs(ctx):
		champs = grab_all_champions()
		message_template = ""
		for champion in champs:
			message_template += champion
		await ctx.respond(message_template)

@client.slash_command(guild_ids=guilds, description="display current champ progression")
async def current(ctx):
		userId = ctx.author.id
		if not dbHandler.check_if_key_exists(userId):
				await ctx.respond('You have not yet started the challenge. Do so with `/start`')
				return
		value = dbHandler.get_key_value(userId)
		currentChampId = value['currentChamp']
		currentChampTries = value['champs'][str(currentChampId)]['tries']
		currentChamp = dbHandler.champs[currentChampId - 1]
		await ctx.respond(f"You're currently at {currentChamp} and have so far had {currentChampTries} Attemps at this Champion")

@client.slash_command(guild_ids=guilds, description="Add or remove one or multiple failed attempts to the current or one of the next champs")
async def add_remove_attempts(ctx,
									amount: Option(int, "the Amount of attempts to add or remove to the champion [default: 1]", min_value=-10, max_value=10),
									skip: Option(int, "The amount of champs to skip from the current [default: 0]")):
		value = dbHandler.get_key_value(ctx.author.id)
		currentChampId = value['currentChamp']
		actualChampId = value['currentChamp'] + skip
		value['champs'][str(actualChampId)]['tries'] += int(amount)
		currentChampTries = value['champs'][str(currentChampId)]['tries']
		actualChampTries = value['champs'][str(actualChampId)]['tries']
		currentChamp = dbHandler.champs[currentChampId - 1]
		actualChamp = dbHandler.champs[actualChampId - 1]

		if skip > 1:
				await ctx.respond(f"You've added another attempts to {actualChamp} and are now at {actualChampTries} Attempts at this Champion")
		await ctx.respond(f"You're currently at {currentChamp} and have now had {currentChampTries} Attemps at this Champion")
		return

@client.slash_command(guild_ids=guilds, description="Add a final attempts to a champion and mark it as finished")
async def finish_champion(ctx,
												 skip: Option(int, "The amount of champs to skip from the current [default: 0]")):
		value = dbHandler.get_key_value(userId)
		currentChampId = value['currentChamp']
		actualChampId = value['currentChamp'] + skip
		currentChamp = dbHandler.champs[currentChampId - 1]
		currentChamp = dbHandler.champs[actualChampId - 1]
		value['champs'][str(actualChampId)]['tries'] += 1
		value['champs'][str(actualChampId)]['finished'] = True
		currentChampTries = value['champs'][str(currentChampId)]['tries']
		actualChampTries = value['champs'][str(actualChampId)]['tries']
		AtoZ = value['isAtoZ']

		if skip == 0:
				nextChampId = CurrentChampId
		else:
				nextChampId = get_next_champ(dbHandler.champs, AtoZ, currentChampId, userId)
		if nextChampId == 0 or nextChampId == len(dbHandler.champs) + 1:
				await ctx.respond('Congratulations! You have completed the challange!')
				return
		else:
				value['currentChamp'] = nextChampId
				nextChamp = dbHandler.champs[nextChampId - 1]
				nextChampTries = value['champs'][str(nextChampId)]['tries']

		await ctx.respond(f"You're have finished {actualChamp} with {actualChampTries} Attemps.")
		await ctx.respond(f"Your new Champion is {nextChamp} with currently {nextChampTries} Attemps.")
		

@client.event
async def on_ready():
    print(dbHandler.keys)
    print(f'We have logged in as {client.user}')


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


def get_next_champ(champs: [], AtoZ: bool, currentChamp: int, userId: int):
    foundNewChamp = False
    nextChampId = currentChamp
    while not foundNewChamp and nextChampId >= 1 and nextChampId <= len(
            champs):
        if not dbHandler.check_if_champ_is_finished(userId, nextChampId):
            return nextChampId
        if AtoZ:
            nextChampId = currentChamp + 1
        else:
            nextChampId = currentChamp - 1


def grab_all_champions() -> []:
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


client.run(bot_token)
