from services.job_service import save_many_jobs
from spiders.api.laborum import LaborumSpider
from spiders.api.trabajando import TrabajandoSpider
from spiders.api.trabajoconsentido import TrabajoConSentidoSpider
from spiders.api.linkedin import LinkedInSpider


def run_spider(spider, name: str):
    print(f"Running {name}")
    jobs = spider.run()
    save_many_jobs(jobs)
    print(f"Finished {name} ({len(jobs)} jobs)")

def run_all_spiders():
    print("Starting scraping")
    try:
        
        run_spider(LinkedInSpider(), "LinkedIn")
        # run_spider(LaborumSpider(), "Laborum")
        # run_spider(TrabajandoSpider(), "Trabajando")
        # run_spider(TrabajoConSentidoSpider(), "TrabajoConSentido")
        print("Finished scraping")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    # Ejecuta una vez y termina
    run_all_spiders()

    # Si luego quieres dejarlo programado, usa schedule:
    # import schedule, time
    # schedule.every().day.at("06:00").do(run_all_spiders)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)
