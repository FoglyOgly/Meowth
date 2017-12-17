import os
import pickle
import discord
import tempfile
import json

server_dict_new = {}

with open('serverdict', "rb") as fd:
	server_dict_old = pickle.load(fd)

for server in server_dict_old:
	server_dict_new[server.id] = {}
	for key in server_dict_old[server]:
		try:
			server_dict_new[server.id][key] = server_dict_old[server][key]
		except:
			pass
	server_dict_new[server.id]['raidchannel_dict'] = {}
	server_dict_new[server.id]['want_channel_list']= []
	for channel in server_dict_old[server]['want_channel_list']:
		server_dict_new[server.id]['want_channel_list'].append(channel.id)

	for channel in server_dict_old[server]['raidchannel_dict']:
		server_dict_new[server.id]['raidchannel_dict'][channel.id] = {
			'address': server_dict_old[server]['raidchannel_dict'][channel]['address'],
			'reportcity': server_dict_old[server]['raidchannel_dict'][channel]['reportcity'],
			'trainer_dict' : server_dict_old[server]['raidchannel_dict'][channel]['trainer_dict'],
			'exp': server_dict_old[server]['raidchannel_dict'][channel]['exp'],
			'manual_timer' : server_dict_old[server]['raidchannel_dict'][channel]['manual_timer'],
			'active': server_dict_old[server]['raidchannel_dict'][channel]['active'],
			'raidmessage': server_dict_old[server]['raidchannel_dict'][channel]['raidmessage'].id,
			'raidreport': server_dict_old[server]['raidchannel_dict'][channel]['raidreport'].id,
			'type': server_dict_old[server]['raidchannel_dict'][channel]['type'],
			'pokemon': server_dict_old[server]['raidchannel_dict'][channel]['pokemon'],
			'egglevel': server_dict_old[server]['raidchannel_dict'][channel]['egglevel']
			}

with tempfile.NamedTemporaryFile('wb', delete=False) as tf:
	pickle.dump(server_dict_new, tf)
	tempname = tf.name
os.rename(tempname, 'serverdict_converted')

servercount_old = 0
raidchannelcount_old = 0
servercount_new = 0
raidchannelcount_new = 0

for server in server_dict_old:
	servercount_old += 1
	for channel in server_dict_old[server]['raidchannel_dict']:
		raidchannelcount_old += 1

for server in server_dict_new:
	servercount_new += 1
	for channel in server_dict_new[server]['raidchannel_dict']:
		raidchannelcount_new += 1

print("Old server count: {}".format(str(servercount_old)))
print("New server count: {}".format(str(servercount_new)))
print("Old raid count: {}".format(str(raidchannelcount_old)))
print("New raid count: {}".format(str(raidchannelcount_new)))
