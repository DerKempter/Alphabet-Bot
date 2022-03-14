import os
import discord
import re

import mwclient

from DBHandler import DBHandler

token = os.environ['TOKEN']

client = discord.Client()

dbHandler = DBHandler()


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

    if message.content.startswith('$hello'):
        await message.channel.send('Hello')

    if message.content.startswith('$Add me'.lower()) and 'A to Z'.lower(
    ) in message.content and not dbHandler.check_if_key_exists(userId):
        userName = message.author.name
        dummy_dict = dbHandler.generate_json_dummy(userId, True)
        dbHandler.add_key_value_pair(userId, dummy_dict)
        await message.channel.send(
            f"user {userName} with Id {userId} has been saved!")

    if message.content.startswith('$Add me'.lower()) and 'Z to A'.lower(
    ) in message.content and not dbHandler.check_if_key_exists(userId):
        userName = message.author.name
        dummy_dict = dbHandler.generate_json_dummy(userId, False)
        dbHandler.add_key_value_pair(userId, dummy_dict)
        await message.channel.send(
            f"user {userName} with Id {userId} has been saved!")

    if message.content.startswith('$show Champions'):
        champs = grab_all_champions()
        message_template = ""
        for champion in champs:
            message_template += champion
        await message.channel.send(message_template)

    if message.content.startswith('$show me'):
        value = dbHandler.get_key_value(userId)
        print(value)

    if message.content.startswith('$Current'.lower()):
        if not dbHandler.check_if_key_exists(userId):
            await message.channel.send(
                'You have not yet started the challenge. Do so with `$Add me` and either `A to Z` or `Z to A`'
            )
            return
        value = dbHandler.get_key_value(userId)
        currentChampId = value['currentChamp']
        currentChampTries = value['champs'][str(currentChampId)]['tries']
        currentChamp = dbHandler.champs[currentChampId - 1]
        await message.channel.send(
            f"You're currently at {currentChamp} and have so far had " +
            f"{currentChampTries} Attemps at this Champion")

    if message.content.startswith('$Try'.lower()):
        regex_str = r'#([0-9]{1})'
        finds = re.findall(regex_str, message.content)
        if finds is not None:
            tries = finds[0]
        else:
            tries = 1
        value = dbHandler.get_key_value(userId)
        currentChampId = value['currentChamp']
        value['champs'][str(currentChampId)]['tries'] += int(tries)
        currentChampTries = value['champs'][str(currentChampId)]['tries']
        currentChamp = dbHandler.champs[currentChampId - 1]
        await message.channel.send(
            f"You're currently at {currentChamp} and have now had " +
            f"{currentChampTries} Attemps at this Champion")

    if message.content.startswith('$Rem Try'.lower()):
        value = dbHandler.get_key_value(userId)
        currentChampId = value['currentChamp']
        value['champs'][str(currentChampId)]['tries'] -= 1
        currentChampTries = value['champs'][str(currentChampId)]['tries']
        currentChamp = dbHandler.champs[currentChampId - 1]
        await message.channel.send(
            f"You're currently at {currentChamp} and have now had " +
            f"{currentChampTries} Attemps at this Champion")

    if message.content.startswith('$Finished'.lower()):
        value = dbHandler.get_key_value(userId)
        currentChampId = value['currentChamp']
        currentChamp = dbHandler.champs[currentChampId - 1]
        value['champs'][str(currentChampId)]['tries'] += 1
        value['champs'][str(currentChampId)]['finished'] = True
        currentChampTries = value['champs'][str(currentChampId)]['tries']
        AtoZ = value['isAtoZ']

        nextChampId = get_next_champ(dbHandler.champs, AtoZ, currentChampId,
                                     userId)
        if nextChampId == 0 or nextChampId == len(dbHandler.champs) + 1:
            await message.channel.send(
                'Congratulations! You have completed the challange!')
            return
        else:
            value['currentChamp'] = nextChampId
            nextChamp = dbHandler.champs[nextChampId - 1]
            nextChampTries = value['champs'][str(nextChampId)]['tries']

        await message.channel.send(
            f"You're have finished {currentChamp} with {currentChampTries} Attemps."
        )
        await message.channel.send(
            f"Your new Champion is {nextChamp} with currently {nextChampTries} Attemps."
        )

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


client.run(token)
