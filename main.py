import discord
print(discord.__version__)
import os
import json
from dotenv import load_dotenv
import re
import requests as req
from bs4 import BeautifulSoup
import mysql.connector
import logging

load_dotenv()

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

host_ip = os.getenv('DB_HOST')
user_id = os.getenv('DB_USER')
password_id = os.getenv('DB_PASS')
database_id = os.getenv('DB_NAME')

mydb = mysql.connector.connect(
  host=host_ip,
  user=user_id,
  password=password_id,
  database=database_id
)

# sql functions

def line_clean(newlines):
    line_set = list()
    for line in newlines:
        str_line = '"' + str(line) + '"'
        line_set.append(str_line)
        
    return line_set


def label_clean(label):
    label_string = '"' + str(label) + '"'
    return label_string


def label_insert(label):
    label_string = label_clean(label)
    
    mycursor = mydb.cursor(buffered=True)
    sql = "INSERT INTO labels_submitted (label) VALUES (%s)" % label_string
    try: 
        mycursor.execute(sql)
    except:
        mydb.rollback()
    
    mydb.commit()
    return


def name_insert(newlines):
    line_set = line_clean(newlines)
    mycursor = mydb.cursor(buffered=True)
    
    for i in range(0,len(line_set)):
        sql = "INSERT IGNORE players_submitted (Players) VALUES (%s)" % line_set[i]
        mycursor.execute(sql)
        
    mydb.commit()
    return


def label_id(label):
    label_string = label_clean(label)
    
    mycursor = mydb.cursor(buffered=True)
    sql = "SELECT * from labels_submitted WHERE label = (%s)" % label_string
    mycursor.execute(sql)
    
    head_rows = mycursor.fetchmany(size=1)
    label_id = head_rows[0][0]
    
    mydb.commit()
    return label_id


def name_id(newlines):
    player_ids = []
    line_set = line_clean(newlines)
    
    mycursor = mydb.cursor(buffered=True)
    
    for i in range(0,len(line_set)):
        sql = "SELECT * from players_submitted WHERE Players = (%s)" % line_set[i]
        mycursor.execute(sql)
        head_rows = mycursor.fetchmany(size=1)
        player_id = head_rows[0][0]
        player_ids.append(player_id)
    
    mydb.commit()
    return player_ids

def player_label_join(label, newlines):
    l_id = label_id(label)
    p_ids = name_id(newlines)
    
    mycursor = mydb.cursor(buffered=True)
    
    for i in range(0,len(p_ids)):
        sql = "INSERT IGNORE playerlabels_submitted (Player_ID, Label_ID) VALUES (%s, %s)" % (p_ids[i], l_id)
        mycursor.execute(sql)
        
    mydb.commit()
    return
  
  
# !predict command color changer 

def plus_minus(var, compare):
    diff_control = '-'
    if(isinstance(var, float)):
        if(var > compare):
            diff_control = '+'
    if(isinstance(var, str)):
        if(str(var)==str(compare)):
            diff_control = '+'
    return diff_control

# discord client events

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
        
    # easter eggs
        
    if "a round of wintertodt is about to begin" in message.content.lower():
        await message.channel.send('Chop chop!')

    
    if message.content.startswith('!meow') or message.content.startswith('!Meow'):
        catResponse = req.get("https://cataas.com/cat?json=true")
        catJSON = catResponse.json()
        catImgURL = "https://cataas.com" + catJSON['url']
        await message.channel.send(catImgURL)

    if message.content.startswith('!poke') or message.content.startswith('!poke'):
        await message.channel.send('Teehee! :3')

    if "25 buttholes" in message.content.lower():
        await message.channel.send('hahahahahaha w0w!')

        
   # channel links
        
    if message.content.startswith('!rules') or message.content.startswith('!Rules'):
        await message.channel.send('<#825137784112807946>')
        
    if message.content.startswith('!issues') or message.content.startswith('!Issues'):
        await message.channel.send('<#822851862016950282>')
        
   # list dm process
        
    if message.content.startswith('!list') or message.content.startswith('!List'):
        msg = "Please send a link to a Pastebin URL containing your name list." + "\n" \
        + "Example: !submit https://pastebin.com/iw8MmUzg" + "\n" \
        + "___________" + "\n" \
        + "Acceptable Formatting:" + "\n" \
        + "Player 1" + "\n" \
        + "Player 2" + "\n" \
        + "Player 3" + "\n" \
        + "Player 4" + "\n" \
        + "Player 5" + "\n" \
        + "___________" + "\n" \
        + "Pastebin Settings:" + "\n" \
        + "Syntax Highlighting: None" + "\n" \
        + "Paste Expiration: 1 Day" + "\n" \
        + "Paste Exposure: Public" + "\n" \
        + "Folder: No Folder Selected" + "\n" \
        + "Password: {leave blank - no password needed}" + "\n" \
        + "Paste Name / Title: {Include your Label Here}" + "\n" 
        await message.author.send(msg)
        
    if message.content.startswith('!submit') or message.content.startswith('!Submit'):
        # get url and raw dataform
        newlines = list()
        res = {}
        paste_url = message.content[8:100]
        data = req.get(paste_url)
        
        # use beautiful soup and other methods to clean the data
        soup = BeautifulSoup(data.content, 'html.parser')
        output = soup.findAll('textarea')
        lines = str(output[0]).strip('<textarea class="textarea">').strip('<"/"').replace('\r','').splitlines()
        
        outputLabel = soup.findAll('title')
        label = str(outputLabel[0]).replace('<title>',"").replace(' - Pastebin.com</title>','')
        
        # regex only confirms lines that are RSN-like
        for line in lines:
            L = re.fullmatch('[\w\d _-]{0,12}', line)
            if L:
                if line != '':
                    newlines.append(line)
                    
        # send data to server
        label_insert(label)
        name_insert(newlines)
        player_label_join(label, newlines)
                    
        # convert cleaned lines into dict : label, into json
        msg = "Paste Information" + "\n" \
        + "_____________________" + "\n" \
        + "Number of Names: " + str(len(newlines)) + "\n" \
        + "Label: " + str(label) + "\n" \
        + "Samples: " + str(newlines[0:10]) + "\n" \
        + "Link: " + str(paste_url) + "\n"

        user = client.get_user(int(os.getenv('SUBMIT_RECIPIENT')))

        await user.send(msg)
      
    # admin commands
        
    if message.content.startswith('!ban') or message.content.startswith('!Ban'):
        msg = "```diff" + "\n" \
                 + "- **Do not attempt to contact the Jmods or Admins in any channel regarding the status of your Runescape account: Doing so will result in an automatic permanent ban.**" + "\n" \
                 + "```\n"
        await message.channel.send(msg)
        
    # links
        
    if message.content.startswith('!website') or message.content.startswith('!Website'):
        await message.channel.send('https://www.osrsbotdetector.com/#/')
        
    if message.content.startswith('!patreon') or message.content.startswith('!Patreon'):
        await message.channel.send('https://www.patreon.com/bot_detector') 
        
    if message.content.startswith('!github core') or message.content.startswith('!github core'):
            await message.channel.send('https://github.com/Ferrariic/Bot-Detector-Core-Files') 
            
    if message.content.startswith('!github plugin') or message.content.startswith('!github plugin'):
            await message.channel.send('https://github.com/Ferrariic/bot-detector') 

    if message.content.startswith('!invite') or message.content.startswith('!Invite'):
        await message.channel.send('https://discord.com/invite/JCAGpcjbfP')
        
    # plugin and database stats

    if message.content.startswith('!stats') or message.content.startswith('!STATS'):
        playersTrackedResponse = req.get("https://www.osrsbotdetector.com/api/site/dashboard/gettotaltrackedplayers")
        otherStatsResponse = req.get("https://www.osrsbotdetector.com/api/site/dashboard/getreportsstats")
        activeInstallsReponse = req.get("https://api.runelite.net/runelite-1.7.4/pluginhub")
        
        playersJSON = playersTrackedResponse.json()
        otherStatsJSON= otherStatsResponse.json()
        activeInstallsJSON = activeInstallsReponse.json()

        playersTracked = playersJSON['players'][0]
        totalBans = otherStatsJSON['bans']
        totalReports = otherStatsJSON['total_reports']
        activeInstalls = activeInstallsJSON['bot-detector']
        
        msg = "```Project Stats:\n" \
                + "Players Analyzed: " + str(playersTracked) + "\n"\
                + "Reports Sent to Jagex: " + str(totalReports) + "\n"\
                + "Resultant Bans: " + str(totalBans) + "\n"\
                + "Active Installs: " + str(activeInstalls) \
                + "```"

        await message.channel.send(msg)
        
    # player stats

    if message.content.startswith('!kc') or message.content.startswith('!KC'):
        playerName = message.content[4:16]

        resp = req.get("https://www.osrsbotdetector.com/api/stats/contributions/" + playerName)
        respJSON = resp.json()

        reports = respJSON['reports']
        bans = respJSON['bans']
        possible_bans = respJSON['possible_bans']

        msg = "```" + playerName + "'s Stats: \n" \
                 + "Reports Submitted: " + str(reports) + "\n" \
                 + "Probable/Pending Bans: " + str(possible_bans) + "\n" \
                 + "Confirmed Bans: " + str(bans) + "```\n"

        await message.channel.send(msg)
        
    #predict method
    
    if message.content.startswith('!predict') or message.content.startswith('!PREDICT'):
          playerName = message.content[9:21]
        
          resp = req.get("https://www.osrsbotdetector.com/api/site/prediction/" + playerName)
          respJSON = resp.json()
          respJSON = respJSON[-1]

          name = respJSON['name']
          prediction = respJSON['prediction']
          player_id = respJSON['id']
          confidence = respJSON['Predicted confidence']
          
          msg = "```diff" + "\n" \
            + "+" + " Name: " + str(name) + "\n" \
            + str(plus_minus(prediction,'Real_Player')) + " Prediction: " + str(prediction) + "\n" \
            + str(plus_minus(confidence, 0.9)) + " Confidence: " + str(confidence) + "\n" \
            + "+" + " ID: " + str(player_id) + "\n" \
            + "```\n"
            
          await message.channel.send(msg)
          
@client.event
async def on_member_join(member):
    pass

client.run(os.getenv('TOKEN'))
