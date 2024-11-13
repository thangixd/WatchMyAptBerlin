from modules.job import WBMScrapingJob, DegewoScrapingJob
from config import housing_association


last_data = None

def run_scraping_job(housing_key):
    global last_data

    # Get the configuration for the selected housing association
    config = housing_association[housing_key]

    # Initialize the ScrapingJob using parameters from the dictionary

    job = config[1](config[0], config[2], config[3], config[4], config[5], config[6], config[7], config[8])
    job.run()

    current_data = job.processor.get_data()
    print(current_data)

    if last_data is not None:
        if not current_data.equals(last_data):
            print("Data has changed!")
            print("Differences:")
            print(current_data.compare(last_data))
        else:
            print("No change in data.")

    last_data = current_data

if __name__ == "__main__":
    run_scraping_job('Degewo')
