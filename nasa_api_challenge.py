from datetime import datetime, timedelta
import json
import requests
import shutil
import os


DAYS_APOD = 10  # number of previous days to get APOD pictures
HD = True  # save hd photos (True) or non hd photos (False)
TXT = True  # Print text of


def main():
    # save APOD to img/ directory for DAYS_APOD number of previous days
    # (default = 0 days), print response text? (default=False)
    apod(DAYS_APOD, HD, TXT)

    print("-----------------------------")

    # Print list of names of hazardous asteroids
    print("List of potentially hazardous asteroids:", hazardous_neows())


# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------


def apod(days=0, hd=True, print_txt=False):
    # Select number of previous days APODs to display (default = 0)
    dates, _ = get_dates(num_days=days)
    # insert dates into the api url
    url = f"https://api.nasa.gov/planetary/apod?{dates}api_key=DEMO_KEY"
    # get response, decode it and load it into a list
    apod_list = get_res_decode_n_load(url, print_txt)

    # check if img directory exists - if not create new directory named "img"
    if not os.path.exists("img"):
        os.makedirs("img")

    # loop throgh each APOD day & save the picture in img/ directory
    for item in apod_list:
        get_apod(item, hd)


# ------------------------------------------------------------------------------------------------------------


def get_dates(num_days=0):
    # get todays date
    today = datetime.now()
    # get date num_days ago
    start_date = today - timedelta(days=num_days)

    # format into date string YYYY-MM-DD
    str_today = today.strftime("%Y-%m-%d")
    str_start = start_date.strftime("%Y-%m-%d")

    # return api string snipit of start and end date, and todays date string
    return f"start_date={str_start}&end_date={str_today}&", str_today


# ------------------------------------------------------------------------------------------------------------


def get_res_decode_n_load(url, print_txt=False):
    res = requests.get(url)
    # check status code == 200 (success)
    if res.status_code != 200:
        print(f"Could not connect to URL - Status Code: {res.status_code}")
        exit()

    # text of response
    str = res.content.decode("utf-8")
    # turn the string into a list using json.loads
    list = json.loads(str)

    if print_txt:
        print(json.dumps(list, indent=4))
    return list


# ------------------------------------------------------------------------------------------------------------


def get_apod(item, hd=True):
    # create file name (hd or not) and get url
    if hd:
        url = item["hdurl"]
        file = f'img/apod_{item["date"]}_hd.jpg'
    else:
        url = item["url"]
        file = f'img/apod_{item["date"]}.jpg'

    # check if file exists or not - do not re-write file - exit function
    if os.path.isfile(file):
        print(file, "already exists")
        return

    # get stream response and print status code
    res = requests.get(url, stream=True)
    print(f'APOD : {item["date"]} - Status Code : {res.status_code}')

    # save the "file-like object" in memory to disk using the shutil library
    outfile = open(file, "wb")  # "wb" - write binary
    shutil.copyfileobj(res.raw, outfile)  # raw - binary
    outfile.close()
    print(file, ": saved successfully")


# ------------------------------------------------------------------------------------------------------------


def hazardous_neows(days=0):
    # get start and end dates (todays date) for api and todays date string
    dates, today = get_dates(days)
    # insert start and end dates into api url
    url = f"https://api.nasa.gov/neo/rest/v1/feed?{dates}api_key=DEMO_KEY"
    # get api result, decode it and load into json list (optional print list)
    asteroid_list = get_res_decode_n_load(url)

    # save list of todays asteroids in variable asteroid
    asteroids = asteroid_list["near_earth_objects"][today]
    # initialise empty list of hazardous asteroids
    hazardous_asteroids = []

    # loop through list of asteroids
    for asteroid in asteroids:
        # if asteroid is listed as potentially hazardous - append to list
        if asteroid["is_potentially_hazardous_asteroid"]:
            hazardous_asteroids.append(asteroid["name"])

    # return list of hazardous asteroids
    return hazardous_asteroids


if __name__ == "__main__":
    main()
