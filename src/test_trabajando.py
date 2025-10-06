from spiders.api.trabajando import TrabajandoSpider
from utils.enums import Position
from pprint import pprint

MAX_PAGES_PER_POSITION = 3
MAX_OFFERS_PER_PAGE = 10

if __name__ == "__main__":
    spider = TrabajandoSpider()
    all_jobs = []

    positions = list(Position)[:5]
    for position in positions:
        print(f"\n=== {position.value.upper()} ===")
        pages = spider.get_pages(position)[:MAX_PAGES_PER_POSITION]
        if not pages:
            print("No pages")
            continue

        jobs_pos = []
        for page in pages:
            offer_urls = spider.get_offers(page)[:MAX_OFFERS_PER_PAGE]
            for url in offer_urls:
                job = spider.get_job(url, position)
                if job:
                    jobs_pos.append(job)
                    all_jobs.append(job)

        print(f"Found {len(jobs_pos)}")
        for job in jobs_pos:
            pprint(job.to_dict())

    print(f"\nTOTAL: {len(all_jobs)}")
