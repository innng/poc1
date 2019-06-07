"""Script to download data from MyAnimeList."""

import re
import json
import urllib.request
import requests
from time import sleep
from bs4 import BeautifulSoup


genres_list = {
    4: "comedy", 1: "action", 2: "adventure", 14: "horror",
    22: "romance", 24: "sci-fi", 8: "drama", 7: "mystery",
    10: "fantasy"
}


def parsePageMAL():
    """Build a JSON with information about titles of mal database."""
    headers = {"Accept-Language": "en-US,en;q=0.5"}

    url1 = "https://myanimelist.net/anime/genre/"
    url2 = "/?page="

    instances = []

    category_titles = 1000
    page_limit = 100

    genre = 1
    page_number = 1

    for genre in genres_list:
        for page_number in range(1, int(category_titles / page_limit)):
            url = url1 + str(genre) + url2 + str(page_number)

            html = requests.get(url, headers=headers).text
            soup = BeautifulSoup(html, "html5lib")

            while "Too Many Requests" in soup.text:
                print("sleeping")
                sleep(60)

                html = requests.get(url, headers=headers).text
                soup = BeautifulSoup(html, "html5lib")

            instances_list = soup.find_all("div", "seasonal-anime js-seasonal-anime")
            for instance in instances_list:
                name = instance.find("a", "link-title").text
                genres = instance.find("div", "genres-inner js-genre-inner").text
                img_path = instance.find("img", "lazyload")["data-src"]
                year = instance.find("span", "remain-time").text

                instance = {"title": name, "year": year, "genres": genres, "img_path": img_path}
                instances.append(instance)

    with open("./mal.json", "w") as fout:
        json.dump(instances, fout)

    print(len(instances))


def removeDuplicates():
    """Remove duplicate entries on JSON."""
    with open("./mal.json", "r") as fout:
        instances = json.load(fout)

    unique_instances = [
        dict(value) for value in {tuple(instance.items()) for instance in instances}]

    with open("./mal.json", "w") as fout:
        json.dump(unique_instances, fout)

    print(len(unique_instances))


def cleanData():
    """Clean data with some pre defined rules."""
    with open("./mal.json", "r") as fout:
        instances = json.load(fout)

    invalid = []

    for instance in instances:
        pattern = re.compile(r"\d{4}")
        match = pattern.findall(instance["year"])

        if len(match) > 0:
            instance["year"] = match[0]
        else:
            invalid.append(instance)

        instance["genres"] = instance["genres"].split(" \n")
        instance["genres"] = [x.strip(" \n").lower() for x in instance["genres"]]
        instance["genres"] = [x for x in instance["genres"] if x in genres_list.values()]

    for item in invalid:
        instances.remove(item)

    with open("./mal.json", "w") as fout:
        json.dump(instances, fout)

    print(len(instances))


def downloadImages():
    """Download the images and change the path."""
    with open("./mal.json", "r") as fout:
        instances = json.load(fout)

    instance_id = 1

    invalid = []

    for instance in instances:
        path = "./img/mal/" + str(instance_id) + ".jpg"

        try:
            urllib.request.urlretrieve(instance["img_path"], path)
        except Exception:
            invalid.append(instance)

        instance["img_path"] = path
        instance_id += 1

    for item in invalid:
        instances.remove(item)

    with open("./mal.json", "w") as fout:
        json.dump(instances, fout)

    print(len(instances))


if __name__ == "__main__":
    parsePageMAL()
    removeDuplicates()
    cleanData()
