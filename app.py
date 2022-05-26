from crawler import WordsCrawler

url = "https://en.wikipedia.org/wiki/Philosopy"
cookies = ""
output_name = "philosopy"

crawler = WordsCrawler(
    url=url,
    cookies_path=cookies,
    output_path=output_name,
    headless=True
)

crawler.run()