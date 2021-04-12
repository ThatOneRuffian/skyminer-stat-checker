"""Lib to wrap all skyminer functions"""
import urllib.request
import json
import csv

class SkyStats:
    """Class for fetching basic Skywire node stats"""
    def __init__(self, stat_tracking_url, public_key_csv):
        self.fetch_url = stat_tracking_url
        self.public_key_csv = public_key_csv
        self.node_list = []
        self.missing_nodes = []
        self.public_key_length = 65
        self.cached_web_data = {}
        self.decode_public_keys_from_csv()

    def fetch_stat_info(self):
        """Fetch data from the provided data stream url"""
        print("Fetching URL stat data...")
        page_data = urllib.request.urlopen(self.fetch_url)
        data_string = str(page_data.read(), 'UTF-8')
        json_data = json.loads(data_string)
        print("Restructuring data...")
        # restructure data for easier searching
        self.cached_web_data = {}  # clear cache
        for node_stat in json_data:
            self.cached_web_data[node_stat['key']] = {'uptime': node_stat['uptime'],
                                                      'downtime': node_stat['downtime'],
                                                      'percentage': node_stat['percentage'],
                                                      'online': node_stat['online']}

    def decode_public_keys_from_csv(self):
        """Decode csv file and place public keys into the node list"""
        self.node_list = []
        with open(self.public_key_csv, 'r') as public_key_source:
            key_reader = csv.reader(public_key_source, delimiter=',')
            for row in key_reader:
                for item in row:
                    if len(item) >= self.public_key_length:
                        self.node_list.append(item)
                    # else discard

    def assemble_stat_data(self):
        """Assemble data and populate class vars"""
        self.missing_nodes = []
        self.fetch_stat_info()
        self.decode_public_keys_from_csv()

    def get_highest_uptime(self):
        """Return the highest uptime in the data gram"""
        highest_uptime = 0
        for node in self.cached_web_data:
            if "uptime" in self.cached_web_data[node]:
                if self.cached_web_data[node]['uptime'] is not None:
                    if self.cached_web_data[node]['uptime'] > highest_uptime:
                        highest_uptime = self.cached_web_data[node]['uptime']
        return highest_uptime

    def print_node_uptime(self):
        """Function for formatting the stat data output"""
        average_uptime = 0
        separator = "=============================================================================="
        print(separator)
        for local_node in self.node_list:
            if local_node in self.cached_web_data:
                print(local_node, ": ", self.cached_web_data[local_node])
                if 'uptime' in self.cached_web_data[local_node]:
                    if self.cached_web_data[local_node]['uptime'] is not None:
                        average_uptime += self.cached_web_data[local_node]['uptime']

            else:
                self.missing_nodes.append(local_node)
        total_online = len(self.node_list) - len(self.missing_nodes)
        total = len(self.node_list)
        print(f'Stats found for {total_online}/{total} nodes ({(total_online/total)*100}%)')
        print('Average Up Time Percentage For This Month', average_uptime / total)
        print("Highest uptime documented in data feed: ", self.get_highest_uptime())
        print(separator)

        if len(self.missing_nodes) > 0:
            print("The following nodes were missing from the data feed:")
            for missing_local_node in self.missing_nodes:
                print(missing_local_node)
