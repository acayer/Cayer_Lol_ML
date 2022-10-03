"""
This class is used as a wrapper for requesting data from Riot API, reading/writing the data to/from files, and computing
data from the match data to analyse later, such as KDA ratios. This is meant to provide one centralized class for
collecting data sets to use in the project.

"""
import requests as request
import pickle as pickler
from riotwatcher import LolWatcher, ApiError


# The api key invalidates itself 24 hours after it is generated. If the current key is not functional, generate a new
# key at the Riot Developer Portal
# Riot asks not to post api keys to the public, so if you want to use this yourself you must use your own API key by
# entering it to the console
urlBase = "https://na1.api.riotgames.com/lol/"
region = "na1"


class RequestRiotData:
    """
    A class used to request data from Riot API, read/write the data to/from files, and compute additional data from the
    match data to analyze later, such as KDA ratios

    ...

    Attributes
    ----------
    apiKey : str
        A string representing your Riot API key. You must use your own.
    region : str
        A string representing the region of which to search data from, I am using na1 as it's where my games are; refer
        to Riot API if seeking alternate regions
    lol_watcher : LolWatcher
        An instance of a Riot API call wrapper called LolWatcher that is necessary for requesting match data from Riot
        API

    Methods
    -------
    get_summoner_puuid(summoner_name, filename)
        Makes a web request to Riot API for the puuid of a particular summoner and writes it to a file
    get_match_ids(in_puuid, in_start, in_count)
        Makes a web request to Riot API to get a list of match ids from a particular summoner using their puuid. This
        is a helper method used in the write_match_ids_text() method
    write_match_ids_text(my_puuid)
        Writes a list of match ids to a txt file called my_matchIds.txt
    parse_match_ids_text(read_matchIds):
        Parses a string representing a list of match ids
    get_matches_from_summoner_champion(self, matchIds, summoner_name, champion_name):
        Gets a list of participantDto objects from Riot API from particular matches using match ids, for a particular
        summoner and a particular champion, and exclusively matches of gameMode 'CLASSIC' and not gameType 'CUSTOM_GAME'
        ; this list is serialized to a dat file of the form 'data_text/matches_' + summoner_name + '_' + champion_name +
        '.dat'
    get_puuid_from_text(self, filename):
        Gets puuid from a text file
    get_matchIds_from_text(self, filename):
        Gets a list of match ids from a text file
    get_matches_from_dat(self, filename):
        Deserializes .dat file; meant to be used for the file containing the list of participantDto stored from the
        get_matches_from_summoner_champion() method
    compute_kdas(self, in_participantDtos):
        Computes the KDA ratios given a list of participantDto
    """
    apiKey = ""
    region = ""
    lol_watcher = -1

    def __init__(self, apikey, region):
        """
        Parameters
        ----------
        apikey : str
            String representing the your Riot API key to use to make web requests to the Riot API
        region : str
            String representing the region of which to search data from, I am using na1 as it's where my games are;
            refer to Riot API if seeking alternate regions
        """
        self.apiKey = apikey
        self.region = region
        # for requests I can't seem to do
        self.lol_watcher = LolWatcher(self.apiKey)
        # *******************************

    def get_summoner_puuid(self, summoner_name, filename):
        """Makes a web request to Riot API for the puuid of a particular summoner and writes it to a file

        Parameters
        ----------
        summoner_name : str
            String representing the name of the summoner you are searching the puuid for
        filename : str
            String representing the name of the file to write the puuid to; include the file extension .txt to write it
            to a txt file

        Returns
        -------
        void
        """
        url = urlBase + "summoner/v4/summoners/by-name/" + summoner_name + "?api_key=" + self.apiKey
        r = request.get(url).json()
        my_puuid = r["puuid"]
        fp = open(filename, 'w')
        fp.write(my_puuid)

    def get_match_ids(self, in_puuid, in_start, in_count):
        """Makes a web request to Riot API to get a list of match ids from a particular summoner using their puuid. This
         is a helper method used in the write_match_ids_text() method

        Parameters
        ----------
        in_puuid : str
            String representing the puuid of the summoner you are getting the match history of
        in_start : int
            Integer representing which index to retrieve match ids from
        in_count : int
            Integer representing how many match ids to retrieve starting from in_start

        Returns
        -------
        list
            A list of strings representing the match ids
        """
        # get match_ids from riot api and write them to a txt file
        return self.lol_watcher.match.matchlist_by_puuid(self.region, in_puuid, in_start, in_count)

    def write_match_ids_text(self, my_puuid):
        """Writes a list of match ids to a txt file called my_matchIds.txt

        Parameters
        ----------
        my_puuid : str
            String representing the puuid of the summoner you are getting the match history of

        Returns
        -------
        void
        """
        num_start = 0
        num_count = 100
        moreMatches = True
        while moreMatches:
            # get match ids from puuid
            print("Getting match ids from summoner " + my_puuid + "...")

            # use try and catch 400 Client Error to find when we've reached the end of match history
            # try:
            my_matchIds = proxy.get_match_ids(my_puuid, num_start, num_count)
            # except:

            print("done.")
            print("Match ids from " + str(num_start) + " to " + str(num_count) + " matches: ")
            print(my_matchIds)

            # THIS DOESNT WORK BUT I COULDNT KEEP TESTING BECAUSE OF THE REQUEST LIMIT SO ILL FIGURE THIS OUT LATER THE
            # CODE LOOPS INFINITELY AT THE MOMENT FYI
            # stop when there are no more matches
            if my_matchIds == '[]':
                moreMatches = False
                break

            # only overwrite the entire file if it's the first 100 games
            if num_start == 0:
                # write matchIds to a txt file
                f = open("data_text/my_matchIds.txt", 'w')
                f.write(str(my_matchIds))
            else:
                # append matchIds to the txt file
                f = open("data_text/my_matchIds.txt", 'a')
                f.write(str(my_matchIds))
            num_start += 100

    def parse_match_ids_text(self, read_matchIds):
        """Parses a string representing a list of match ids

        Parameters
        ----------
        read_matchIds : str
            A string representing a list of match ids

        Returns
        -------
        list
            A list of strings representing individual match ids
        """
        add_this = ""
        match_ids = []
        # parse matchIds string
        # it is of the form:
        # [A, A, A][A, A, A]
        # where A is a match id
        count = 0
        for i in range(0, len(read_matchIds)):
            if read_matchIds[i] == ',' or read_matchIds[i] == '[':
                match_ids.append(add_this)
                add_this = ""
                print("Added " + add_this)
                count += 1
            elif read_matchIds[i] == ']' or read_matchIds[i] == ' ' or read_matchIds[i] == '\'':
                print("ignore this")
            else:
                add_this += read_matchIds[i]
        # print all of the match ids to verify we have a nice, clean list
        for i in match_ids:
            print("Match Id: " + i)

        print("Type of match_ids: " + str(type(match_ids)))
        print("Number of matches: " + str(count))
        return match_ids

    def get_matches_from_summoner_champion(self, matchIds, summoner_name, champion_name):
        """Gets a list of participantDto objects from Riot API from particular matches using match ids, for a particular
        summoner and a particular champion, and exclusively matches of gameMode 'CLASSIC' and not gameType 'CUSTOM_GAME'
        ; this list is serialized to a dat file of the form 'data_text/matches_' + summoner_name + '_' + champion_name +
        '.dat'

        Parameters
        ----------
        matchIds : list
            A list of strings representing match ids
        summoner_name : str
            A string representing the name of the summoner
        champion_name : str
            A string representing the name of the champion

        Returns
        -------
        void
        """
        matches = []
        # print("M_IDS: " + matchIds[1])
        for j in range(1, len(matchIds)):
            # making the request myself gives me 403 (Forbidden) error so I will use lol_watcher api here
            # url = urlBase + "match/v5/matches/" + j + "?api_key=" + self.apiKey
            # matchDto = request.get(url).json()
            print("j here is: " + matchIds[j])
            matchDto = self.lol_watcher.match.by_id(region, matchIds[j])
            print("MatchDto: " + str(matchDto))
            # only 'CLASSIC' matches on on the current summoner's rift and NOT 'CUSTOME_GAME'
            if matchDto['info']['gameMode'] == 'CLASSIC' and matchDto['info']['mapId'] == 11 and \
                    matchDto['info']['gameType'] != 'CUSTOM_GAME':
                for i in range(0, 9): # matchDto['info']['participants'].__sizeof__()
                    if matchDto['info']['participants'][i]['summonerName'] == summoner_name and \
                            matchDto['info']['participants'][i]['championName'] == champion_name:
                        matches.append(matchDto['info']['participants'][i])
        print("Most recent match participantDto: " + str(matches[0]))
        # return matches
        # serialize the match ParticipantDto objects to a file using pickle
        fw = open('data_text/matches_' + summoner_name + '_' + champion_name + '.dat', 'wb')
        pickler.dump(matches, fw)
        fw.close()
        fw.write(str(matches))

    def get_puuid_from_text(self, filename):
        """Gets puuid from a text file

        Parameters
        ----------
        filename : str
            String representing the name of the file; include the file extension

        Returns
        -------
        str
            A string representing the puuid read from the file
        """
        f_puuid = open(filename, 'r')
        return f_puuid.read()

    def get_matchIds_from_text(self, filename):
        """Gets a list of match ids from a text file

        Parameters
        ----------
        filename : str
            String representing the name of the file; include the file extension

        Returns
        -------
        str
            A string representing the list of match ids
        """
        f_matchIds = open(filename, 'r')
        return f_matchIds.read()

    def get_matches_from_dat(self, filename):
        """Deserializes .dat file; meant to be used for the file containing the list of participantDto stored from the
        get_matches_from_summoner_champion() method

        Parameters
        ----------
        filename : str
            String representing the name of the file; include the file extension

        Returns
        -------
        list
            A list of dictionaries following the format of the participantDto object; see Riot API for more details
        """
        input_matches = open(filename, 'rb')
        eof = False
        while not eof:
            try:
                partDtos = pickler.load(input_matches)
            except EOFError:
                eof = True
        input_matches.close()
        return partDtos

    def compute_kdas(self, in_participantDtos):
        """Computes the KDA ratios given a list of participantDto

        Parameters
        ----------
        in_participantDtos : list
            List of participantDto; see Riot API for more details

        Returns
        -------
        list
            A list of doubles representing the KDA ratios of all of the matches
        """
        out_kdas = []
        counter = 0
        for i in in_participantDtos:
            if i['deaths'] != 0:
                kda = (i['kills'] + i['assists']) / i['deaths']
                out_kdas.append(kda)
            else:
                kda = i['kills'] + i['assists']
                out_kdas.append(kda)
            print("kda " + str(counter) + ": " + str(out_kdas[counter]))
            counter = counter + 1
        return out_kdas


# driver to test/use methods
if __name__ == '__main__':

    # input your key to console
    print("Please enter your Riot API Key: ")
    key = input()

    # init proxy
    reg = "na1"
    proxy = RequestRiotData(key, reg)
    # web requests to riot api to get data and write it to text files
    # proxy.get_summoner_puuid('Super Lemone', "data_text/my_puuid.txt")
    # proxy.write_match_ids_text(proxy.get_puuid_from_text("data_text/my_puuid.txt"))

    # read puuid and matchIds from existing text files
    read_puuid = proxy.get_puuid_from_text("data_text/my_puuid.txt")
    read_matchIds = proxy.get_matchIds_from_text("data_text/my_matchIds.txt")
    match_ids_rd = proxy.parse_match_ids_text(read_matchIds)

    # get specific matches
    sName = 'Super Lemone'
    cName = 'Nasus'
    # web requests to riot api to get data and write it to text files
    # proxy.get_matches_from_summoner_champion(match_ids_rd, sName, cName)
    # read participantDto data from existing dat files
    partDto = proxy.get_matches_from_dat('data_text/matches_Super Lemone_Nasus.dat')

    # let's calculate the KDAs from the participantDto list and store them
    kdas = proxy.compute_kdas(partDto)

    # time for machine learning :^)
