"""
A script for testing out pyplot; Going to start by plotting all of the kdas from all of my Nasus games
"""
import matplotlib.pyplot as plt
import Request_Riot_Data


def main():
    print("Please enter your Riot API key: ")
    key = input()
    region = 'na1'
    proxy = Request_Riot_Data.RequestRiotData(key, region)
    # get the KDAs from my Nasus games
    partDto = proxy.get_matches_from_dat('data_text/matches_Super Lemone_Nasus.dat')
    kdas = proxy.compute_kdas(partDto)

    # time for plotting
    plt.plot(kdas, 'ro')
    plt.ylabel("KDA Ratio")
    plt.xlabel("Match No.")
    plt.title("Super Lemone's KDAs from Nasus Matches")
    plt.show()


if __name__ == '__main__':
    main()
