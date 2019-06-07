"""Script to download data from IMDB."""

import re
import json
import urllib.request
import requests
from bs4 import BeautifulSoup


genres_list = [
    "comedy", "action", "adventure", "horror",
    "romance", "sci-fi", "drama", "mystery",
    "fantasy"
]


def parsePageIMDB():
    """Build a JSON with information about titles of IMDB database."""
    headers = {"Accept-Language": "en-US,en;q=0.5"}

    url1 = "https://www.imdb.com/search/title?genres="
    url2 = "&start="
    url3 = "&explore=title_type,genres&ref_=adv_nxt"

    instances = []

    category_titles = 1000
    page_limit = 50

    for genre in genres_list:
        for page_number in range(1, category_titles, page_limit):
            url = url1 + genre + url2 + str(page_number) + url3

            html = requests.get(url, headers=headers).text
            soup = BeautifulSoup(html, "html5lib")

            instances_list = soup.find_all("div", "lister-item mode-advanced")
            for instance in instances_list:
                div1 = instance.find("div", "lister-item-content")

                name = div1.find("a").text
                year = div1.find("span", "lister-item-year text-muted unbold").text
                genres = div1.find("span", "genre").text

                div2 = instance.find("div", "lister-item-image float-left")
                img_path = div2.find("img", "loadlate")["loadlate"]

                instance = {"title": name, "year": year, "genres": genres, "img_path": img_path}
                instances.append(instance)

    with open("./imdb.json", "w") as fout:
        json.dump(instances, fout)

    print(len(instances))


def removeDuplicates():
    """Remove duplicate entries on JSON."""
    with open("./imdb.json", "r") as fout:
        instances = json.load(fout)

    unique_instances = [
        dict(value) for value in {tuple(instance.items()) for instance in instances}]

    with open("./imdb.json", "w") as fout:
        json.dump(unique_instances, fout)

    print(len(unique_instances))


def cleanData():
    """Clean data with some pre defined rules."""
    with open("./imdb.json", "r") as fout:
        instances = json.load(fout)

    invalid = []

    for instance in instances:
        pattern = re.compile(r"\d{4}")
        match = pattern.findall(instance["year"])

        if len(match) > 0:
            instance["year"] = match
            instance["year"] = instance["year"][0]
        else:
            invalid.append(instance)

        instance["genres"] = instance["genres"].strip(" \n").split(",")
        instance["genres"] = [x.strip().lower() for x in instance["genres"]]
        instance["genres"] = [x for x in instance["genres"] if x in genres_list]

        instance["img_path"] = instance["img_path"].replace("0,67,98_", "0,167,242_")
        instance["img_path"] = re.sub(r"U.\d*_", "UX167_", instance["img_path"])

    for item in invalid:
        instances.remove(item)

    with open("./imdb.json", "w") as fout:
        json.dump(instances, fout)

    print(len(instances))


def downloadImages():
    """Download the images and change the path."""
    with open("./imdb.json", "r") as fout:
        instances = json.load(fout)

    instance_id = 1

    invalid = []

    for instance in instances:
        path = "./img/imdb/" + str(instance_id) + ".jpg"

        try:
            urllib.request.urlretrieve(instance["img_path"], path)
        except Exception:
            invalid.append(instance)

        instance["img_path"] = path
        instance_id += 1

    for item in invalid:
        instances.remove(item)

    with open("./imdb.json", "w") as fout:
        json.dump(instances, fout)

    print(len(instances))


if __name__ == "__main__":
    parsePageIMDB()
    removeDuplicates()
    cleanData()
