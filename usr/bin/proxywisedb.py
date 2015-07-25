#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright 2015 Anando Gopal Chatterjee <anandogc@gmail.com>
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


import gnomekeyring as gk
from os.path import expanduser
import json, os

class ProxywiseDB:
    def __init__(self):
        self.keyring_name = 'proxywise'
        self.__keyring_password = 'proxywise'
        self.home = expanduser("~")
        self.config_path = self.home + "/.config/proxywise"
        self.config_file_name = self.config_path + "/config.json"

        if not os.path.exists(self.config_path):
            os.makedirs(self.config_path)

        if not os.path.exists(self.config_file_name):
            config_file = open(self.config_file_name, 'w')
            json.dump(  {
                            "active_profile": None,
                            "ignore_host_list": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
                        }, config_file, sort_keys=True, indent=4, separators=(',', ': '))
            config_file.close()

        if not self.keyring_name in gk.list_keyring_names_sync():
            gk.create_sync(self.keyring_name, self.__keyring_password)

        self.Unlock()

    def Unlock(self):
        gk.unlock_sync(self.keyring_name, self.__keyring_password)

    def Lock(self):
        gk.lock_sync(self.keyring_name)

    def GetProfileIdList(self):
        return gk.list_item_ids_sync(self.keyring_name)

    def GetInfo(self, profile_id):
        return gk.item_get_info_sync(self.keyring_name, profile_id)

    def GetDisplayName(self, profile_id):
        profile_info = gk.item_get_info_sync(self.keyring_name, profile_id)
        return profile_info.get_display_name()

    def GetSecret(self, profile_id):
        profile_info = gk.item_get_info_sync(self.keyring_name, profile_id)
        return profile_info.get_secret()

    def GetAttributes(self, profile_id):
        profile_attr = gk.item_get_attributes_sync(self.keyring_name, profile_id)
        profile_info = gk.item_get_info_sync(self.keyring_name, profile_id)

        attributes = {}
        attributes['name'] = profile_info.get_display_name()
        for attr in profile_attr.items():
            if attr[0] != 'xdg:schema':
                attributes[attr[0]] = attr[1]

        return attributes

    def GetServer(self, profile_id):
        return self.GetAttributes(profile_id)['server']

    def GetPort(self, profile_id):
        return self.GetAttributes(profile_id)['port']

    def GetUser(self, profile_id):
        return self.GetAttributes(profile_id)['user']

    def GetPassword(self, profile_id):
        return self.GetSecret(profile_id)

    def GetIndex(self, profile_id):
        return self.GetAttributes(profile_id)['index']

    def SetDisplayName(self, profile_id, new_display_name):
        #Get info
        info = gk.item_get_info_sync(self.keyring_name, profile_id)
        attributes = self.GetAttributes(profile_id)

        #Change info
        info.set_display_name(new_display_name)

        #Update info
        gk.item_set_info_sync(self.keyring_name, profile_id, info)
        gk.item_set_attributes_sync(self.keyring_name, profile_id, attributes)

    def SetPassword(self, profile_id, new_password):
        #Get info
        info = gk.item_get_info_sync(self.keyring_name, profile_id)
        attributes = self.GetAttributes(profile_id)

        #Change info
        info.set_secret(new_password.encode('ascii', 'ignore'))

        #Update info
        gk.item_set_info_sync(self.keyring_name, profile_id, info)
        gk.item_set_attributes_sync(self.keyring_name, profile_id, attributes)

    def SetAttributes(self, profile_id, attributes):
        gk.item_set_attributes_sync(self.keyring_name, profile_id, attributes)

    def UpdateAttributes(self, profile_id, new_attributes):
        attributes = self.GetAttributes(profile_id)
        for key in new_attributes:
            attributes['key'] = new_attributes[key]

        self.SetAttributes(profile_id, attributes)

    def GetActiveProfile(self):
        config_file = open(self.config_file_name)

        try:
            active_profile = json.load(config_file)["active_profile"]
        except ValueError as e:
            pass

        return active_profile

    def GetIgnoreHostList(self):
        config_file = open(self.config_file_name)
        ignore_host_list = []
        try:
            ignore_host_list = json.load(config_file)["ignore_host_list"]
        except ValueError as e:
            pass

        return ignore_host_list

    def GetPersistentIgnoreHostList(self):
        #return ["localhost", "127.0.0.0/8"]
        return ["localhost"]

    def SetActiveProfile(self, profile_id):
        try:
            config = json.load(open(self.config_file_name))
            config["active_profile"] = profile_id
        except ValueError as e:
            pass

        config_file = open(self.config_file_name, "w")
        json.dump(config, config_file, sort_keys=True, indent=4, separators=(',', ': '))
        config_file.close()

    def SetIgnoreHostList(self, ignore_host_list):
        try:
            config = json.load(open(self.config_file_name))
            config["ignore_host_list"] = ignore_host_list
        except ValueError as e:
            pass

        config_file = open(self.config_file_name, "w")
        json.dump(config, config_file, sort_keys=True, indent=4, separators=(',', ': '))
        config_file.close()

    def AddIgnoreHost(self, host):
        ignore_host_list = self.GetIgnoreHostList()
        ignore_host_list.append(host)
        self.SetIgnoreHostList(ignore_host_list)

    def ExtendIgnoreHostList(self, host_list):
        ignore_host_list = self.GetIgnoreHostList()
        ignore_host_list.extend(host_list)
        self.SetIgnoreHostList(ignore_host_list)

    def RemoveIgnoreHost(self, host):
        ignore_host_list = self.GetIgnoreHostList()
        try:
            ignore_host_list.remove(host)
            self.SetIgnoreHostList(ignore_host_list)
        except ValueError:
            pass



if __name__ == '__main__':

    #keyring = ProxywiseDB()
    """
    for profile_id in keyring.GetIdList():
        print keyring.GetDisplayName(profile_id)
        print "  " + keyring.GetServer(profile_id)
        print "  " + str(keyring.GetPort(profile_id))
        print "  " + keyring.GetPassword(profile_id)
        print "  " + keyring.GetUser(profile_id)
    """

    #keyring.SetIgnoreHostList(["172.00.0/8"])
    #keyring.AppendIgnoreHostList("168.0.0.0/8")
    #keyring.ExtendIgnoreHostList(["abcd", "efgh"])
    #keyring.RemoveIgnoreHost("dwdew")
    #print (keyring.GetIgnoreHostList())
