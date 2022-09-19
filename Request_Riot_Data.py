# Making my own wrapper class for requesting data from Riot API
import requests as request
from riotwatcher import LolWatcher, ApiError


# The api key invalidates itself 24 hours after it is generated. If the current key is not functional, generate a new
# key at the Riot Developer Portal
# Riot asks not to post api keys to the public, so if you want to use this yourself you must use your own by entering it
# to the console
urlBase = "https://na1.api.riotgames.com/lol/"
region = "na1"


class RequestRiotData:

    apiKey = ""
    region = ""
    lol_watcher = -1

    def __init__(self, apikey, region):
        self.apiKey = apikey
        self.region = region
        # for requests I can't seem to do
        self.lol_watcher = LolWatcher(self.apiKey)
        # *******************************

    def get_summoner_puuid(self, summoner_name):
        url = urlBase + "summoner/v4/summoners/by-name/" + summoner_name + "?api_key=" + self.apiKey
        r = request.get(url).json()
        return r["puuid"]

    def get_match_ids(self, in_puuid):
        # using lol_watcher api because if I try to make the request myself I get 403 error :(
        return self.lol_watcher.match.matchlist_by_puuid(self.region, in_puuid)
        # vvv below is the code that throws 403 error on request vvv
        # url = urlBase + "match/v5/matches/by_puuid/" + in_puuid + "/ids" + "?api_key=" + self.apiKey
        # r = request.get(url)
        # return r.json()


# driver to test methods
if __name__ == '__main__':

    # init proxy
    print("Please enter your Riot API Key: ")
    key = input()
    reg = "na1"
    proxy = RequestRiotData(key, reg)

    # get puuid from summoner name
    print("Getting puuid from summoner name...")
    my_puuid = proxy.get_summoner_puuid('Super Lemone')
    print("done.")
    print("puuid: ")
    print(my_puuid)
    # get match ids from puuid
    print("Getting match ids from summoner " + my_puuid + "...")
    my_matchIds = proxy.get_match_ids(my_puuid)
    print("done.")
    print("Match ids from last 100 matches: ")
    print(my_matchIds)
    # get specific matches

    # get as many as possible?

    # get specific data from those matches and write to a csv file

    # time for machine learning :^)
