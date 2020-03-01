import os
import pickle
import discord
import tempfile
import json
import copy



with open('serverdict', "rb") as fd:
	guild_dict_convert = pickle.load(fd)


for guild in guild_dict_convert:
    configure_dict = copy.deepcopy(guild_dict_convert[guild].get('configure_dict',{}))
    configure_dict['welcome'] = {
        "enabled":guild_dict_convert[guild].get('welcome',False),
        "welcomechan":guild_dict_convert[guild].get('welcomechan',''),
        "welcomemsg":guild_dict_convert[guild].get('welcomemsg','default')
    }
    configure_dict['want'] = {
        "enabled":guild_dict_convert[guild].get('wantset',False),
        "report_channels": guild_dict_convert[guild].get('want_channel_list',[])
    }
    configure_dict['raid'] = {
        "enabled":guild_dict_convert[guild].get('raidset',False),
        'report_channels': guild_dict_convert[guild].get('city_channels',{}),
        "categories":guild_dict_convert[guild].get('categories',None),
        "category_dict":guild_dict_convert[guild].get('category_dict',{})
    }
    configure_dict['exraid'] = {
        "enabled":guild_dict_convert[guild].get('raidset',False),
        'report_channels': guild_dict_convert[guild].get('city_channels',{}),
        "categories":guild_dict_convert[guild].get('categories',None),
        "category_dict":guild_dict_convert[guild].get('category_dict',{}),
        "permissions":"everyone"
    }
    configure_dict['wild'] = {
        "enabled":guild_dict_convert[guild].get('wildset',False),
        'report_channels': guild_dict_convert[guild].get('city_channels',{}),
    }
    configure_dict['counters'] = {
       "enabled":True,
       'auto_levels': ["3","4","5"],
    }
    configure_dict['research'] = {
        "enabled":True,
        'report_channels': guild_dict_convert[guild].get('city_channels',{}),
    }
    configure_dict['archive'] = {
        "enabled":True,
        "category":guild_dict_convert[guild].get('archive',{}).get('category','same'),
        'list':guild_dict_convert[guild].get('archive',{}).get('list',[])
    }
    configure_dict['invite'] = {
        "enabled":True
    }
    configure_dict['team'] = {
        "enabled":guild_dict_convert[guild].get('team',False)
    }
    configure_dict['settings'] = {
        "offset":guild_dict_convert[guild].get('offset',0),
        "regional":guild_dict_convert[guild].get('regional',None),
        "prefix":guild_dict_convert[guild].get('prefix',None),
        "done":guild_dict_convert[guild].get('done',False),
        "config_sessions": {}
    }
    guild_dict_convert[guild]['configure_dict'] = configure_dict
    try:
        del guild_dict_convert[guild]['want_channel_list']
    except:
        pass
    try:
        del guild_dict_convert[guild]['welcomemsg']
    except:
        pass
    try:
        del guild_dict_convert[guild]['city_channels']
    except:
        pass
    try:
        del guild_dict_convert[guild]['categories']
    except:
        pass
    try:
        del guild_dict_convert[guild]['category_dict']
    except:
        pass
    try:
        del guild_dict_convert[guild]['offset']
    except:
        pass
    try:
        del guild_dict_convert[guild]['welcome']
    except:
        pass
    try:
        del guild_dict_convert[guild]['welcomechan']
    except:
        pass
    try:
        del guild_dict_convert[guild]['wantset']
    except:
        pass
    try:
        del guild_dict_convert[guild]['raidset']
    except:
        pass
    try:
        del guild_dict_convert[guild]['wildset']
    except:
        pass
    try:
        del guild_dict_convert[guild]['team']
    except:
        pass
    try:
        del guild_dict_convert[guild]['want']
    except:
        pass
    try:
        del guild_dict_convert[guild]['other']
    except:
        pass
    try:
        del guild_dict_convert[guild]['done']
    except:
        pass


with tempfile.NamedTemporaryFile('wb', delete=False) as tf:
	pickle.dump(guild_dict_convert, tf)
	tempname = tf.name
os.rename(tempname, 'serverdict_converted')
