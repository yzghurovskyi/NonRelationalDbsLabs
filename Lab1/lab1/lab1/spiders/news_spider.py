import scrapy


class NewsSpider(scrapy.Spider):
    name = "news"
    start_urls = ["http://ridna.ua/"]
    custom_settings = {
        'ITEM_PIPELINES': {
            'lab1.pipelines.NewsPipeline': 300
        }
    }

    def parse(self, response):
        yield {
            'page': response.url,
            'text': [fragment.strip() for fragment in response.xpath(".//p/text()").extract()],
            'images': response.xpath(".//img/@src").extract(),
        }
        for link in response.xpath("//a[@class=\"title\"]/@href")[:20]:
            yield response.follow(link, callback=self.parse_inner_page)

    def parse_inner_page(self, response):
        yield {
            'page': response.url,
            'text': [fragment.strip() for fragment in response.xpath(".//p/text()").extract()],
            'images': response.xpath(".//img/@src").extract(),
        }
