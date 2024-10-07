from playwright.async_api import async_playwright, Playwright
import json
import asyncio
import argparse
import logging

class Product():
    def __init__(self, product_id, name, price, description, review_count, category):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.description = description
        self.review_count = review_count
        self.category = category

    def to_json(self):
        return {
                "product_id": int(self.product_id),
                "name": self.name,
                "price": self.price,
                "description": self.description,
                "review_count": int(self.review_count),
                "category": self.category
                }


class WebScraper():

    def __init__(self):
        parser = argparse.ArgumentParser(
                        prog='informDataWebScraper.py',
                        description='Inform Data Web Scraper',
                        epilog='')
        parser.add_argument(
            "-l",
            "--log",
            default="INFO",
            help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        )
        parser.add_argument(
            "-f",
            "--file_path",
            default="data.jsonl",
            help="Set the name of the .jsonl file, defaults to data.jsonl",
        )
        self.args = parser.parse_args()

        logging.basicConfig(filename="webscraper.log",
                            format='%(asctime)s %(message)s',
                            filemode='w')
        self.log = logging.getLogger()
        self.log.setLevel(getattr(logging, self.args.log))

        self.empty_output_file()

    def empty_output_file(self):
        with open(self.args.file_path, 'w'): pass

    def write_product_data(self, a_product: Product):
        with open(self.args.file_path, 'a', encoding ='utf8') as json_file:
            json.dump(a_product.to_json(), json_file, ensure_ascii = False)
            json_file.write('\n')

    async def parse_product_data(self, product_url, product, sub_url):

        product_id = product_url.split("/")[-1]
        name_locator = product.locator('''h4[class="title card-title"]''')
        name = (await name_locator.all_inner_texts())[0]
        price_locator = product.locator('''h4[class="price float-end pull-right"]''')
        price = (await price_locator.all_inner_texts())[0]
        description_locator = product.locator('''p[class="description card-text"]''')
        description = (await description_locator.all_inner_texts())[0]
        review_count_locator = product.locator('''p[class="review-count"]''')
        review_count = (await review_count_locator.all_inner_texts())[0].split(" ")[0]
        category = sub_url.split("/")[-1].title()

        logging.debug(f"{product_id}, {name}, {price}, {description}, {review_count}, {category}")

        a_product = Product(product_id, name, price, description, review_count, category)

        return a_product


    async def run(self, playwright: Playwright):
        start_url = "https://webscraper.io/test-sites/e-commerce/ajax"
        chrome = playwright.chromium
        browser = await chrome.launch(headless=False)
        page = await browser.new_page()
        await page.goto(start_url)

        #grab the categories (Computers, phones)
        links_locator = await page.locator('''a[aria-label="Navigation category"]''').all()

        for link in links_locator:
            logging.debug(f"link: {link}")
            p = await browser.new_page(base_url="https://webscraper.io/")
            url = await link.get_attribute("href")
            if url is not None:
                logging.debug(f"url: {url}")
                await p.goto(url)
                subcategory_locator = await p.locator('''a[aria-label="Navigation subcategory"]''').all()
                subcategory_urls = [await subcategory.get_attribute("href") for subcategory in subcategory_locator]
                # get the subcategories:  Computers->Laptops,Tablets | Phones->Touch
                for sub_url in subcategory_urls:
                    sub_p = await browser.new_page(base_url="https://webscraper.io/")
                    logging.debug(f"sub_url: {sub_url}")
                    await sub_p.goto(sub_url)

                    # get the page number buttons ie pages 1,2,3,4,5,etc. for looking at all products in a subcategory
                    buttons_locator = await sub_p.locator('''div[class="btn-group pagination justify-content-center"]''').locator('''button[class*="btn btn-default page-link page"]''').all()
                    for button in buttons_locator:

                        await button.click()

                        #get the urls for the individual products
                        items = await sub_p.locator('''a[class="title"]''').all()
                        extracted_items = [await item.get_attribute("href") for item in items]
                        logging.debug(extracted_items)

                        for product_url in extracted_items:
                            logging.debug(f'''product_url: {product_url}''')
                            product = await browser.new_page(base_url="https://webscraper.io/")
                            if product_url is not None:
                                logging.debug(f"Navigating to https://webscraper.io{product_url}")
                                await product.goto(product_url)

                                a_product = await self.parse_product_data(product_url, product, sub_url)

                                self.write_product_data(a_product)

                                await product.close()

                    await sub_p.close()

            await p.close()

    async def main(self):
        async with async_playwright() as p:
            await self.run(p)


if __name__ == '__main__':
    web_scraper = WebScraper()
    asyncio.run(web_scraper.main())


