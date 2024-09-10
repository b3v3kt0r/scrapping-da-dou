import time
from typing import Any

import scrapy
from scrapy.http import Response, HtmlResponse
from selenium import webdriver
from selenium.common import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.by import By

from ..config import python_technologies


class VacanciesSpider(scrapy.Spider):
    name = "vacancies"
    allowed_domains = ["jobs.dou.ua"]
    start_urls = ["https://jobs.dou.ua/vacancies/?category=Python"]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason: str):
        self.driver.close()

    def get_detail_page(self, response: Response):
        for vacancy in response.css(".l-vacancy"):
            detail_page_url = vacancy.css(".vt::attr(href)").get()
            self.log(f"Found detail page: {detail_page_url}")
            if detail_page_url:
                yield scrapy.Request(detail_page_url, callback=self.parse_detail)

    def parse(self, response: Response, **kwargs):
        self.driver.get(response.url)

        while True:
            try:
                more_button = self.driver.find_element(
                    By.CSS_SELECTOR, ".more-btn a"
                )
                more_button.click()
                time.sleep(2)
            except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException):
                break

        page_source = self.driver.page_source

        selenium_response = HtmlResponse(
            url=response.url,
            body=page_source,
            encoding="utf-8"
        )

        yield from self.get_detail_page(selenium_response)

    def parse_detail(self, response: Response):

        full_text = response.css(".b-typo *::text").getall()
        full_text = " ".join(full_text).lower()

        found_technologies = [tech for tech in python_technologies if tech.lower() in full_text]

        yield {
            "title": response.css("h1::text").get(),
            "company": response.css(".l-n > a::text").get(),
            "technologies": found_technologies
        }
