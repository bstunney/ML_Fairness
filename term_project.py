# spotify api packages
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time

# race classification
#!pip install deepface
#from deepface import DeepFace

# data management
import json
import pandas as pd

# image search
from bing_image_downloader import downloader
import matplotlib.image as mpimg
import os

# data vis
import matplotlib.pyplot as plt

# math
from scipy.stats.stats import pearsonr


def get_playlist_metadata(playlist_id, client_id, client_secret):
    # Create Spotify client
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    try:
        # Get playlist information
        playlist = sp.playlist(playlist_id)

        tracks = []
        for track in playlist["tracks"]["items"]:
            tracks.append({"track_name": track["track"]["name"], "track_id": track["track"]["id"],
                           "artists": [artist["name"] for artist in track["track"]["artists"]],
                           "artist_ids": [artist["id"] for artist in track["track"]["artists"]]})

        return tracks

    except spotipy.SpotifyException as e:
        print(f"Error: {e}")


def search_artist(artist_id, client_id, client_secret):
    # Set up Spotify API credentials
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Search for the artist
    artist = sp.artist(artist_id)


    return {"artist_name": artist["name"],
            "artist_followers": artist["followers"]["total"],
            "artist_genres": artist["genres"],
            "artist_popularity": artist["popularity"]}


def get_playlists(query, client_id, client_secret, item_type="playlist"):
    query += " mix"

    # Set up Spotify API credentials
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Search for the album
    results = sp.search(q=query, type=item_type, limit=50)

    # Check if there are any results
    if not results[item_type + 's']['items']:
        print(f"No {item_type} found with the query: {query}")
        return None

    # get necessary metadata for each playlist
    playlists = []
    c = 0
    for item in results["playlists"]['items']:
        if item["name"][-3:] == "Mix" and item["owner"]["display_name"] == "Spotify" and query.lower() in item[
            "name"].lower() and c < 5:
            playlists.append({"playlist_name": item["name"], "playlist_id": item['id']})
            c += 1

    return playlists


def get_playlist_data(query, client_id, client_secret):
    playlists = get_playlists(query, client_id, client_secret)

    playlist_data = []
    for playlist in playlists:
        tracks_data = []
        playlist_name = playlist["playlist_name"]

        print(playlist_name)
        #print(playlist["playlist_id"])
        print()
        tracks = get_playlist_metadata(playlist["playlist_id"], client_id, client_secret)

        for track in tracks:

            track_artist_ids = track["artist_ids"]
            track_name = track["track_name"]
            print(track["track_name"])

            artist_info = []
            for track_artist_id in track_artist_ids:
                time.sleep(0.01)
                artist_info.append(search_artist(track_artist_id,client_id, client_secret))

            tracks_data.append({"track_name": track_name, "artist_info": artist_info})

        playlist_data.append({"playlist_name": playlist_name, "tracks_data": tracks_data})

    return playlist_data

def artist_labels(artistlst, results):

    with open(os.getcwd() + "/artist_labels.json",
              'r') as openfile:
        # Reading from json file
        results = json.load(openfile)

    artistlabels = results
    for i in range(len(artistlst)):

        if artistlst[i] not in [name[0] for name in artistlabels]:

            artistlabels.append((artistlst[i], image_labeling(artistlst[i])))

            if i % 5 == 0:
                print(len(artistlst) - len(results))
                print("Artist No.:",str(i))
                # Serializing json
                json_object = json.dumps(artistlabels, indent=4)

                # Writing to sample.json
                with open(os.getcwd() + "/artist_labels.json", "w") as outfile:
                    outfile.write(json_object)


    # Serializing json
    json_object = json.dumps(artistlabels, indent=4)

    # Writing to sample.json
    with open(os.getcwd() + "/artist_labels.json", "w") as outfile:
        outfile.write(json_object)

def image_labeling(query):
    print(query)
    downloader.download(query+" musician", limit=5, output_dir='faces', adult_filter_off=True, force_replace=False,
                        timeout=60, verbose=False)
    idx = 0

    while True:
        files = os.listdir(os.getcwd() + "/faces/" + query + " musician")
        try:
            img = mpimg.imread(os.getcwd() + "/faces/" + query + " musician" + "/" + files[idx])
            imgplot = plt.imshow(img)
            plt.show()
        except:
            print()
            print("no image available")
            print()
            return "u"

        print("b: Black")
        print("w: White")
        print("a: Asian")
        print("l: Latino")
        print("i: Indigenous")
        print("o: Other/Mixed")
        print("u: Unknown")
        print("n: Generate new image")
        print()
        val = input("Enter code here: ")

        if val not in ["b","w","a","l","o","n","u","i"]:
            print("Enter valid label, try again")
            val = input("Enter code here: ")
        if val == "n":
            idx += 1
        if val.lower() != "n":
            return val

def get_dummies_data(client_ids, client_secrets, genres):
    # get playlist data for each dummy account and genre

    for genre in genres:

        print("Getting Data for Genre: " + genre)
        print()

        # for each dummy
        for idx in range(len(client_ids)):

            # get spotify client
            client_id = client_ids[idx]
            client_secret = client_secrets[idx]
            print(client_id)

            # Serializing json
            json_object = json.dumps(get_playlist_data(genre, client_id, client_secret), indent=4)

            # Writing to sample.json
            with open(os.getcwd() + "/playlist_data_app" + str(idx+1) + "/" + genre + "_data_" + str(idx+1) +  ".json", "w") as outfile:
                outfile.write(json_object)

def get_genre_counts(genres):

    # load data for each genre
    all_genre_artists = []
    resultslst = []
    for genre in genres:
        # Opening JSON file
        with open(os.getcwd() + "/playlist_data_app" + str(1) + "/" + genre + "_data_" + str(1) + ".json",
                  'r') as openfile:
            # Reading from json file
            results = json.load(openfile)
            resultslst.append(results)

        # get artist names for each genre
        artist_lsts = []
        for i in range(len(results)):
            artists = [item for sublist in [[artist["artist_name"] for artist in track["artist_info"]]
                                            for track in results[i]["tracks_data"]] for item in sublist]
            artist_lsts.append(artists)
        all_genre_artists.append(list(set([item for sublist in artist_lsts for item in sublist])))

    # get flat list of all artists from each genre
    artists = list(set([item for sublist in all_genre_artists for item in sublist]))

    # make dict for artist genre counters
    artist_info = {}
    for artist in artists:
        artist_info[artist] = {}
        for genre in genres:
            artist_info[artist][genre] = 0

                #{"r&b": 0, "rock": 0, "pop": 0, "country": 0}

    for genre in resultslst:
        for playlist in genre:
            for artist in artists:
                artist_info[artist][playlist["playlist_name"]] = 0

    with open(os.getcwd() + "/artist_labels.json",
              'r') as openfile:
        # Reading from json file
        race_results = json.load(openfile)

    # for each genre
    for i in range(len(genres)):

        # get playlist data for each genre
        results = resultslst[i]

        # for each playlist
        for playlist in results:

            # for each track in each playlist
            for track in playlist["tracks_data"]:

                # for each artist on each track in each playlist
                for artist in track["artist_info"]:
                    # add one to the genre counter for each artist in playlist
                    artist_info[artist["artist_name"]][genres[i]] += 1
                    artist_info[artist["artist_name"]][playlist["playlist_name"]] += 1
                    artist_info[artist["artist_name"]]["artist_followers"] = artist["artist_followers"]
                    artist_info[artist["artist_name"]]["artist_genres"] = artist["artist_genres"]
                    artist_info[artist["artist_name"]]["artist_popularity"] = artist["artist_popularity"]

                    artist_info[artist["artist_name"]]["race"] = race_results[[artist[0] for artist in race_results].index(artist["artist_name"])][1]
                    # elif "r&b" not in artist_info[artist["artist_name"]]

    # return genre counter for artists
    return artist_info, artists

def fill_unknowns(results):
    for artist in [artist for artist in results if artist[1] == "u"]:
        print(artist[0])
        val = input("Do you know artist's race? (y/n) ")
        if val == "y":
            race = input("Enter race: ")
            results[[artist[0] for artist in results].index(artist[0])] = [artist[0], race]


    # Serializing json
    json_object = json.dumps(results, indent=4)

    # Writing to sample.json
    with open(os.getcwd() + "/artist_labels.json", "w") as outfile:
        outfile.write(json_object)

def get_df(artist_dct):
    df = pd.DataFrame.from_dict(artist_dct, orient='index')

    df = df.reset_index()
    df.columns = ['name' if x == 'index' else x for x in df.columns]
    df.loc[df['race'] == "a", "race"] = "asian"
    df.loc[df['race'] == "b", "race"] = "black"
    df.loc[df['race'] == "o", "race"] = "other/mixed"
    df.loc[df['race'] == "w", "race"] = "white"
    df.loc[df['race'] == "l", "race"] = "latino"
    df.loc[df['race'] == "bb", "race"] = "black"
    df.loc[df['race'] == "u", "race"] = "unknown"
    df.loc[df['race'] == "i", "race"] = "indigenous"

    df["black_grouped"] = df["r&b"] + df["rap"] + df["hip hop"]
    df["black_grouped_main"] = df["R&B Mix"] + df["Rap Mix"] + df["Hip Hop Mix"]

    return df

def plots(df):

    plt.bar(["race unknown", "race identified"], [len(df[df["race"] == "unknown"]), len(df[df["race"] != "unknown"])])
    plt.xlabel("Race Identification")
    plt.ylabel("No. of Artists")
    plt.title("Race Identification Counts")
    plt.show()

    races = list(set(df["race"]))
    plt.bar(races, [len(df[df["race"] == race]) for race in races])
    plt.xlabel("Race")
    plt.ylabel("No. of Artists")
    plt.title("No. of Artists by Race")
    plt.show()

    indices = []
    for i in range(len(df)):
        if sum(x > 0 for x in [df.iloc[i][genre] for genre in list(df.columns[1:10])]) > 1:
            indices.append(i)
    racedf = df.iloc[indices, :]
    races = list(set(df["race"]))
    races.remove("indigenous")
    plt.bar(races, [len(racedf[racedf["race"] == race]) for race in races], color="green")
    plt.xlabel("Race")
    plt.ylabel("No. of Artists")
    plt.title("No. of Artists Within Multiple Playlist Genres by Race")
    plt.show()

    indices = []
    genrelst = list(df.columns[1:10])
    genrelst.remove("r&b")
    genrelst.remove("hip hop")
    genrelst.remove("rap")
    genrelst.append("black_grouped")

    for i in range(len(df)):
        if sum(x > 0 for x in [df.iloc[i][genre] for genre in genrelst]) > 1:
            indices.append(i)
    racedf = df.iloc[indices, :]
    races = list(set(df["race"]))
    races.remove("indigenous")
    plt.bar(races, [len(racedf[racedf["race"] == race]) for race in races], color="green")
    plt.xlabel("Race")
    plt.ylabel("No. of Artists")
    plt.title("No. of Artists Within Multiple Playlist Genres by Race (rap, hip hop, r&b grouped)")
    plt.show()


    main_playlists = list(df.columns)[10:-5][::5]
    other_playlists = [playlist for playlist in list(df.columns)[10:-5] if playlist not in main_playlists]
    print(other_playlists)

    indices = []
    main_playlists.remove("Rap Mix")
    main_playlists.remove("R&B Mix")
    main_playlists.remove("Hip Hop Mix")
    main_playlists.append("black_grouped")

    for i in range(len(df)):
        if [df.iloc[i][playlist] for playlist in main_playlists].count(1) > 1:
            indices.append(i)
    racedf = df.iloc[indices, :]
    races = list(set(df["race"]))
    races.remove("indigenous")
    print([len(racedf[racedf["race"] == race]) for race in races])
    print(races)



    main_playlists = list(df.columns)[10:-5][::5]
    other_playlists = [playlist for playlist in list(df.columns)[10:-5] if playlist not in main_playlists]


    indices = []
    main_playlists.remove("Rap Mix")
    main_playlists.remove("R&B Mix")
    main_playlists.remove("Hip Hop Mix")
    main_playlists.append("black_grouped")

    for i in range(len(df)):
        if sum(x > 0 for x in [df.iloc[i][playlist] for playlist in main_playlists]) > 1:
            indices.append(i)
    racedf = df.iloc[indices, :]
    races = list(set(df["race"]))
    races.remove("indigenous")
    print([len(racedf[racedf["race"] == race]) for race in races])
    print(races)

    plt.bar(races, [len(racedf[racedf["race"] == race]) for race in races], color="palegreen")
    plt.xlabel("Race")
    plt.ylabel("No. of Artists")
    plt.title("Artists Within Multiple Non-Primary Playlists by Race (rap, hip hop, r&b grouped)")
    plt.show()


    genre_classed = []
    for dfi in range(len(df)):
        #[x > 0 for x in [df.iloc[i][playlist] for playlist in df.columns[10:-6]]]
        genre_classed.append(any([genre.lower() in " ".join([df.columns[10:-6][idx] for idx in [i for i, y in enumerate(
        [x > 0 for x in [df.iloc[dfi][playlist] for playlist in df.columns[10:-6]]]) if y]]).lower() for genre in df.iloc[dfi]["artist_genres"]]))

    df["classed"] = genre_classed

    indices = []
    for i in range(len(df)):
        if df.iloc[i]["classed"] == True:
            indices.append(i)

    racedf = df.iloc[indices, :]
    races = list(set(df["race"]))
    races.remove("indigenous")
    print([len(racedf[racedf["race"] == race]) for race in races])
    print(races)

    plt.bar(races, [len(racedf[racedf["race"] == race]) for race in races], color="lightgreen")
    plt.xlabel("Race")
    plt.ylabel("No. of Artists")
    plt.title("No. of Artists Within Spotify-Identified Genre Playlists by Race")
    plt.show()

    indices = []
    genrelst = list(df.columns[1:10])
    genrelst.remove("r&b")
    genrelst.remove("hip hop")
    genrelst.remove("rap")
    genrelst.append("black_grouped")

    for i in range(len(df)):
        if sum(x > 0 for x in [df.iloc[i][genre] for genre in genrelst]) > 1:
            indices.append(i)

    # racedf = df.iloc[indices, :]
    races = list(set(df["race"]))
    races.remove("indigenous")

    df["multiple"] = False
    df.loc[indices, 'multiple'] = True

    lst = list(df.columns)[1:10]
    lst.append(df.columns[-1])
    lst.append(df.columns[-3])
    lst.append(df.columns[-4])
    lst.append(df.columns[-5])
    lst.append(df.columns[-7])

    corrdf = df[lst]
    print(corrdf.corr())
    plt.matshow(corrdf.corr())
    plt.show()


    race = []
    # get races that have pop tracks
    for i in range(len(df)):
        if df.iloc[i]["pop"] > 0:
            race.append(df.iloc[i]["race"])

    print(set(race))

    # for each race
    for i in range(len(set(race))):
        pop = []
        popularity = []
        followers = []
        for idx in range(len(df)):
            if df.iloc[idx]["pop"] > 0 and df.iloc[idx]["race"] == list(set(race))[i]:
                pop.append(df.iloc[idx]["pop"])
                popularity.append(df.iloc[idx]["artist_popularity"])
                followers.append(df.iloc[idx]["artist_followers"])

        print(pearsonr(popularity,pop))
        plt.scatter(popularity, pop, color = "seagreen")
        plt.xlabel("Artist Popularity")
        plt.ylabel("No. of Pop Songs")
        plt.title("Artist Popularity by No. of Pop Songs for Race: " + list(set(race))[i])
        plt.show()

    vals = []
    genrelst = list(df.columns[10:-6])

    for i in range(len(df)):
        vals.append(sum(x > 0 for x in [df.iloc[i][genre] for genre in genrelst]))

    df["num_playlists"] = vals
    ranked = df.sort_values('num_playlists', ascending=False)[:25]
    print(ranked["num_playlists"])

    races = list(set(df["race"]))
    races.remove("indigenous")

    plt.bar(races, [len(ranked[ranked["race"] == race]) for race in races], color="lightgreen")
    plt.xlabel("Race")
    plt.ylabel("No. of Artists")
    plt.title("No. of Most Diverse Exposured Artists by Race")
    plt.show()

    return None

if __name__ == "__main__":

    # Spotify API credentials for Ben Tunney
    #client_id = 'd3b2ea37fe734d49a7b230ce8103d0e7'
    #client_secret = '366f581b3ccb4e0d82066fb097fd9156'

    #client_ids = ['d3b2ea37fe734d49a7b230ce8103d0e7', "639e6cbc63bb4b82843577d8fb7156d9", "40602de6b3534f65852aed315da036ce", "411b80d05d534045bce04a2c3c878eef"]
    #client_secrets = ['366f581b3ccb4e0d82066fb097fd9156', "09384eb3ac8d4dcfbd1bc373c6e5ef45", "d7ad9f8d0b62427e8e7800c7a056cbca", "fe59da67481d4569908e8491e1b54a12"]
    #genres = ["r&b", "rock", "pop", "country"]

    #client_ids = ["639e6cbc63bb4b82843577d8fb7156d9"]
    #client_secrets = ["09384eb3ac8d4dcfbd1bc373c6e5ef45"]

    genres = ["r&b", "rock", "house", "edm","rap", "hip hop","pop","country","jazz"]
    #get_dummies_data(client_ids, client_secrets, genres)

    with open(os.getcwd() + "/artist_labels.json",
              'r') as openfile:
        # Reading from json file
        results = json.load(openfile)

    artist_dct, artistlst = get_genre_counts(genres)

    df = get_df(artist_dct)