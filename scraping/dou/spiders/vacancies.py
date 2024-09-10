import scrapy
from scrapy.http import Response

from scraping.dou.config import python_technologies


class VacanciesSpider(scrapy.Spider):
    name = "vacancies"
    allowed_domains = ["jobs.dou.ua"]
    start_urls = ["https://jobs.dou.ua/vacancies/?category=Python"]

    def get_detail_page(self, response: Response, **kwargs):
        for vacancy in response.css(".l-vacancy"):
            detail_page_url = vacancy.css(".vt::attr(href)").get()
            self.log(f"Found detail page: {detail_page_url}")
            if detail_page_url:
                yield scrapy.Request(detail_page_url, callback=self.parse_detail)

    def parse(self, response: Response, **kwargs):
        yield from self.get_detail_page(response, **kwargs)

    def parse_detail(self, response: Response):
        yield {
            "title": response.css("h1::text").get(),
            "company": response.css(".l-n > a::text").get(),
        }
