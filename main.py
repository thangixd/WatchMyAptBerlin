from config import housing_association

last_data = None


def run_scraping_job(housing_key):
    global last_data
    config = housing_association[housing_key]

    job = config[1](config[0], config[2], config[3], config[4], config[5], config[6], config[7], config[8])
    job.run()

    current_data = job.processor.get_data()

    current_data = job.processor.clean_data(current_data)
    print(current_data)

    return current_data


if __name__ == "__main__":
    run_scraping_job('Degewo')
