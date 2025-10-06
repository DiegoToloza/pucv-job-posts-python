from spiders.api.laborum import LaborumSpider
from pprint import pprint

if __name__ == "__main__":
    spider = LaborumSpider()
    jobs = spider.run()

    print(f"Found {len(jobs)} jobs")
    for job in jobs[:5]:  # Mostrar solo los primeros 5
        pprint(job.to_dict())
