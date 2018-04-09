import os
import pickle
import discord
import tempfile
import json



with open('serverdict', "rb") as fd:
	guild_dict_convert = pickle.load(fd)

for guildid in guild_dict_convert.keys():
    for channelid in guild_dict_convert[guildid]['raidchannel_dict'].keys():
        for trainerid in guild_dict_convert[guildid]['raidchannel_dict'][channelid]['trainer_dict'].keys():
            if type(guild_dict_convert[guildid]['raidchannel_dict'][channelid]['trainer_dict'][trainerid]['party']) is not __builtins__.dict:
                count = guild_dict_convert[guildid]['raidchannel_dict'][channelid]['trainer_dict'][trainerid].get('count',1)
                party = guild_dict_convert[guildid]['raidchannel_dict'][channelid]['trainer_dict'][trainerid].get('party',[0,0,0,1])
                status = guild_dict_convert[guildid]['raidchannel_dict'][channelid]['trainer_dict'][trainerid].get('status',"maybe")
                party = {"mystic":party[0], "valor":party[1], "instinct":party[2], "unknown":party[3]}
                if status == "maybe":
                    status = {"maybe": count, "coming":0, "here":0, "lobby":0}
                elif status == "omw":
                    status = {"maybe": 0, "coming":count, "here":0, "lobby":0}
                elif status == "waiting":
                    status = {"maybe": 0, "coming":0, "here":count, "lobby":0}
                elif status == "lobby":
                    status = {"maybe": 0, "coming":0, "here":0, "lobby":count}
                guild_dict_convert[guildid]['raidchannel_dict'][channelid]['trainer_dict'][trainerid]['party'] = party
                guild_dict_convert[guildid]['raidchannel_dict'][channelid]['trainer_dict'][trainerid]['status'] = status


with tempfile.NamedTemporaryFile('wb', delete=False) as tf:
	pickle.dump(guild_dict_convert, tf)
	tempname = tf.name
os.rename(tempname, 'serverdict_converted')
