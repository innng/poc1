"""
Script for loading files from json into ElasticSearch.

Created in June 7, 2019.
"""

import json
from sys import argv
from elasticsearch_dsl import AttrList, Document, Integer, Keyword, Text
from elasticsearch_dsl.connections import connections


class Data(Document):
    """Represent data to be inserted."""

    title = Keyword()
    year = Integer()
    genres = AttrList()
    img_path = Text()

    class Index:
        """Define a name for data insertion."""

        name = "loader"

    def save(self, **kwargs):
        """Use default implementation of save method."""
        return super(Data, self).save(**kwargs)


class ElasticHelper(object):
    """Init loader of data and creater connections with ElasticSearch."""

    def __init__(self):
        """Init process."""
        self.connection = connections.create_connection(hosts=["elasticsearch:9200"])
        self.index = "loader"
        Data().init()

    def insert_document(self, **kwargs):
        """Define how to insert data."""
        return Data(**kwargs).save()


if __name__ == "__main__":
    elastic_logger = ElasticHelper()

    source_filename = argv[1]

    with open(source_filename, "r") as fp:
        source = json.load(fp)

    for item in source:
        elastic_logger.insert_document(**item)
