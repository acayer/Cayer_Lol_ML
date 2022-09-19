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

    def get_match_ids(self, in_puuid, in_start, in_count):
        # using lol_watcher api because if I try to make the request myself I get 403 error :(
        return self.lol_watcher.match.matchlist_by_puuid(self.region, in_puuid, in_start, in_count)
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
    # COMMENT FROM HERE BECAUSE WE DONT NEED TO WRITE TO FILES AGAIN****************************************************
    # get puuid from summoner name
    # print("Getting puuid from summoner name...")
    # my_puuid = proxy.get_summoner_puuid('Super Lemone')
    # print("done.")
    # print("puuid: ")
    # print(my_puuid)
    #
    # # write my puuid to a txt file
    # fp = open("data_text/my_puuid.txt", 'w')
    # fp.write(my_puuid)
    #
    # # we want my entire match history, but we can only query 100 at a time, so we'll loop until we can't find any more
    # # matches.
    # num_start = 0
    # num_count = 100
    # moreMatches = True
    # while moreMatches:
    #
    #     # get match ids from puuid
    #     print("Getting match ids from summoner " + my_puuid + "...")
    #
    #     # use try and catch 400 Client Error to find when we've reached the end of match history
    #     # try:
    #     my_matchIds = proxy.get_match_ids(my_puuid, num_start, num_count)
    #     # except:
    #
    #     print("done.")
    #     print("Match ids from " + str(num_start) + " to " + str(num_count) + " matches: ")
    #     print(my_matchIds)
    #
    #     # THIS DOESNT WORK BUT I COULDNT KEEP TESTING BECAUSE OF THE REQUEST LIMIT SO ILL FIGURE THIS OUT LATER THE
    #     # CODE LOOPS INFINITELY AT THE MOMENT FYI
    #     # stop when there are no more matches
    #     if my_matchIds == '[]':
    #         moreMatches = False
    #         break
    #
    #     # only overwrite the entire file if it's the first 100 games
    #     if num_start == 0:
    #         # write matchIds to a txt file
    #         f = open("data_text/my_matchIds.txt", 'w')
    #         f.write(str(my_matchIds))
    #     else:
    #         # append matchIds to the txt file
    #         f = open("data_text/my_matchIds.txt", 'a')
    #         f.write(str(my_matchIds))
    #     num_start += 100
    #COMMENT FROM HERE**************************************************************************************************

    # read puuid and matchIds from the files
    f_puuid = open("data_text/my_puuid.txt", 'r')
    read_puuid = f_puuid.read()

    f_matchIds = open("data_text/my_matchIds.txt", 'r')
    read_matchIds = f_matchIds.read()
    print(type(read_matchIds))

    add_this = ""
    match_ids = []
    # parse matchIds string
    # it is of the form:
    # [A, A, A][A, A, A]
    # where A is a match id
    for i in range(0, len(read_matchIds)):
        if read_matchIds[i] == ',' or read_matchIds[i] == '[':
            match_ids.append(add_this)
            add_this = ""
            print("Added " + add_this)
        elif read_matchIds[i] == ']' or read_matchIds[i] == ' ' or read_matchIds[i] == '\'':
            print("ignore this")
        else:
            add_this += read_matchIds[i]
    # print all of the match ids to verify we have a nice, clean list
    for i in match_ids:
        print("Match Id: " + i)

    print("Type of match_ids: " + str(type(match_ids)))
    # get specific matches

    # get specific data from those matches and write to a csv file

    # time for machine learning :^)
