import scrapy


class BikesSpider(scrapy.Spider):
    name = "bikes"
    start_urls = ["https://veliki.com.ua/dir_bikes.htm"]
    custom_settings = {
        'ITEM_PIPELINES': {
            'lab1.pipelines.BikesPipeline': 300
        }
    }

    def parse(self, response):
        for bike_link in response.xpath("//strong[@class=\"name\"]/a/@href")[:20]:
            yield response.follow(bike_link, self.parse_bike_page)

    def parse_bike_page(self, response):
        yield {
            'url': response.url,
            'name': response.xpath(".//*[@itemprop=\"name\"]/text()").extract_first(),
            'price': response.xpath(".//*[@itemprop=\"price\"]/text()").extract_first(),
            'description': " ".join(
                [part.strip() for part in response.xpath(".//div[@class=\"btext editable\"]"
                                                         "/descendant-or-self::*/text()").extract()]),
            'image': response.urljoin(response.xpath("//*[@class=\"main\"]/img/@src").extract_first())
        }
