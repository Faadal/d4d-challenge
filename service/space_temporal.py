#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
    This class provides a interface to model a range of data
    into a matrix-st model
    
    Created 21/11/2012
    
    @author: Paradigma Labs
"""
from pymongo import *
from datetime import datetime
from datetime import timedelta

class SpaceTemporalModel:
    """
    """
    def __init__(self):
        """
        Load and retieve collection pointer from MongoDB
        """
        self.config = {}
        self.config['db'] = {}
        self.config['db']['host'] = "web40"
        self.config['db']['port'] = 27017
        self.config['db']['db'] = "d4dchallenge"
        self.config['db']['collection'] = "traces"
        self.traces = self.__get_collection(self.config)

    def __get_collection(self, config):
        """
        Return collection from MongoDB with a specific configuration
        """
        connection = Connection(config['db']['host'], config['db']['port'])
        db = connection[config['db']['db']]
        collection = db[config['db']['collection']]
        return collection
        
    def retieve_data_and_create_model(self, date_start, date_end):
        """
        Prerequisite: The date format should be: YYYY:DD:MM:HH, e.g.: 2011:21:12:03
        """
        chunk_ds = date_start.split(":")
        chunk_de = date_end.split(":")
        start = datetime(int(chunk_ds[0]), int(chunk_ds[2]), int(chunk_ds[1]), int(chunk_ds[3]), 0, 0)
        end = datetime(int(chunk_de[0]), int(chunk_de[2]), int(chunk_de[1]), int(chunk_de[3]), 0, 0)
        # Debug prints
        print("Extract data from: %s to %s" % (start, end))
        users = {}
        for item in self.traces.find({'date': {'$gte': start, '$lt':end}}):
            if item['userid'] not in users:
                users[item['userid']] = {}
                users[item['userid']]["trace"] = []
            if item['antenna']["lon"] != -1:
                users[item['userid']]["trace"].append((item['antenna']["lat"], item['antenna']["lon"], item['date']))
        return users

    def create_gephi_node_model(self, from_datetime, to_datetime):
        """
            Prerequisite: from_datetime and to_datetime must be datetime.datetime instances
        """
        result = {}
        print("Building model from [%s] to [%s]" % (from_datetime, to_datetime))
        while from_datetime < to_datetime:
            datetime_window_end = from_datetime + timedelta(hours=1)
            antennas = {}
            print("Querying from [%s] to [%s]" % (from_datetime, datetime_window_end))
            items = self.traces.find({'date': {'$gte': from_datetime, '$lte': datetime_window_end}})
            print("\tFound [%s] items" % items.count())
            for item in items:
                if item['antennaid'] in antennas:
                    antennas[item['antennaid']]['users'].append(item['userid'])
                else:
                    antennas[item['antennaid']] = {'date_start':from_datetime, 
                    'latitude': item['antenna']['lat'], 'longitude': item['antenna']['lon'],
                    'date_end':datetime_window_end, 'users':[item['userid']]}
            for antenna, data in antennas.items():
                if antenna in result:
                    result[antenna].append(data)
                else:
                    result[antenna] = [data]
            from_datetime = datetime_window_end
        return result

    def create_gephi_edge_model(self, from_datetime, to_datetime):
        """
            Prerequisite: from_datetime and to_datetime must be datetime.datetime instances
        """
        result = {}
        print("Building edges model")
        next_datetime = from_datetime + timedelta(hours=1)
        while from_datetime < to_datetime - timedelta(hours=1):
            antennas = {}
            next_datetime_2 = next_datetime + timedelta(hours=1)
            items_t1 = self.traces.find({'date': {'$gte': from_datetime, '$lte': next_datetime}})
            items_t2 = self.traces.find({'date': {'$gte': next_datetime, '$lte': next_datetime_2}})
            items_t2_dict = {}
            for item in items_t2:
                items_t2_dict[item['userid']] = item
            print("Found [%s] users (t1=%s) and [%s] users (t2=%s)" % (items_t1.count(), from_datetime, items_t2.count(), next_datetime_2))
            for item in items_t1:
                userid = item['userid']
                if userid in items_t2_dict:
                    antenna_1 = item['antennaid']
                    antenna_2 = items_t2_dict[userid]['antennaid']
                    if (antenna_1, antenna_2) in antennas:
                        antennas[(antenna_1, antenna_2)]['users'].append(userid)
                    else:
                        antennas[(antenna_1, antenna_2)] = {'date_start':next_datetime,
                        'date_end':next_datetime_2, 'users':[userid]}
            for antenna, data in antennas.items():
                if antenna in result:
                    result[antenna].append(data)
                else:
                    result[antenna] = [data]
            from_datetime = next_datetime
            next_datetime = next_datetime_2

        return result


        
        
        

# stm = SpaceTemporalModel()
# gephi_model = stm.create_gephi_edge_model(datetime(2011, 12, 7, 0, 0), datetime(2011, 12, 7, 2, 0))
# print(gephi_model)
# model = stm.retieve_data_and_create_model("2011:07:12:00", "2011:07:12:12")

# print(model)








