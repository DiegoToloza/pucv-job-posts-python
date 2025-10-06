from spiders.api.trabajoconsentido import TrabajoConSentidoSpider
from utils.enums import Position
from pprint import pprint

if __name__ == "__main__":
    spider = TrabajoConSentidoSpider()
    all_jobs = []

    # Tomamos hasta 5 posiciones del enum
    positions_to_scrape = list(Position)[:5]

    for position in positions_to_scrape:
        print(f"\n=== Scraping {position.value.upper()} ===")
        offer_urls = spider.get_offer_urls(position) if hasattr(spider, "get_offer_urls") else spider.get_offers(
            f"{spider.base_url}?tags={position.value.replace(' ', ',')}"
        )

        if not offer_urls:
            print(f"No offers found for {position.value}")
            continue

        jobs = []
        for url in offer_urls:
            job = spider.get_job(url, position)
            if job:
                jobs.append(job)
                all_jobs.append(job)

        print(f"Found {len(jobs)} jobs for {position.value}")
        for job in jobs:
            pprint(job.to_dict())

    print(f"\nTOTAL JOBS SCRAPED: {len(all_jobs)}")
