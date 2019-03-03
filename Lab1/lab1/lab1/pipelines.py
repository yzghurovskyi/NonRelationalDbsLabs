# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from lxml import etree as ET


class Lab1Pipeline(object):
    def process_item(self, item, spider):
        return item


class NewsPipeline(object):
    def __init__(self):
        self.root = ET.Element('data')

    def close_spider(self, spider):
        ET.ElementTree(self.root).write("results/news.xml", pretty_print=True, encoding="utf-16")

    def process_item(self, item, spider):
        page = ET.SubElement(self.root, 'page', url=item["page"])
        for text_fragment in item["text"]:
            if text_fragment:
                text = ET.SubElement(page, 'fragment', type="text")
                text.text = text_fragment
        for image_fragment in item["images"]:
            image_url = ET.SubElement(page, 'fragment', type="image")
            image_url.text = image_fragment


class BikesPipeline(object):
    def __init__(self):
        self.root = ET.Element('bikes')

    def close_spider(self, spider):
        ET.ElementTree(self.root).write("results/bikes.xml", pretty_print=True, encoding="utf-16")

    def process_item(self, item, spider):
        bike = ET.SubElement(self.root, 'bike')
        for key, value in item.items():
            ET.SubElement(bike, key).text = value


