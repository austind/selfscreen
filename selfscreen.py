import argparse
from pprint import pprint
import requests
import json
from time import sleep
from random import randint
import logging
from logging.handlers import RotatingFileHandler
import yaml

LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"

root_log = logging.getLogger()
root_log.setLevel(logging.DEBUG)

log = logging.getLogger("selfscreen")
log.setLevel(logging.DEBUG)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", help="Path to YAML config file", type=str)
    parser.add_argument(
        "--randomize",
        "-r",
        help="Delay assessment by a random interval between 0-12 minutes",
        action="store_true",
    )
    parser.add_argument(
        "--log-file",
        "-o",
        help="File path to save debug output. Rotates at 50kb, saves 5 logs",
        type=str,
        dest="log_file",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        help="Do not send any output to stdout or stderr",
        action="store_true",
    )
    args = parser.parse_args()

    if args.log_file:
        handler = RotatingFileHandler(args.log_file, maxBytes=50000, backupCount=5)
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        root_log.addHandler(handler)

    if args.quiet:
        root_log.addHandler(logging.NullHandler())
    else:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        root_log.addHandler(handler)

    if args.randomize:
        sleep_minutes = randint(0, 11)
        sleep_seconds = randint(0, 60)
        log.info(
            f"Waiting {sleep_minutes}m {sleep_seconds}s to randomize assessment timestamp..."
        )
        sleep((sleep_minutes * 60) + sleep_seconds)

    if args.config:
        config_file = args.config
    else:
        config_file = "./config.yml"

    with open(config_file, "r") as fh:
        config = yaml.safe_load(fh)

    login_url = "https://api.selfscreening.org/auth/temp"
    assessment_url = "https://api.selfscreening.org/assessment"

    headers = {
        "Host": "api.selfscreening.org",
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "DNT": "1",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": f"{config['user_agent']}",
        "Content-Type": "application/json",
        "Origin": f"https://{config['selfscreen_domain']}",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": f"https://{config['selfscreen_domain']}/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "sec-gpc": "1",
    }

    session = requests.Session()
    payload = json.dumps(config["login_params"])
    log.info(f"Logging in as '{config['login_params']['lastName']}'...")
    response = session.post(login_url, headers=headers, data=payload)
    if response.ok:
        log.info("Logged in OK")
        data = json.loads(response.content)
        headers["Authorization"] = f"Bearer {data['token']}"
        payload = json.dumps(config["assessment_params"])
        log.info("Submitting assessment...")
        response = session.post(assessment_url, headers=headers, data=payload)
        if response.status_code == 201:
            # success
            log.info("Assessment received and accepted")
        elif (
            response.status_code == 400
            and response.text == "Already submitted assessment today"
        ):
            # duplicate
            log.warning(response.text)
        else:
            # unknown error
            log.error(
                f"Problem submitting assessment. Status code: {response.status_code}"
            )
            log.error(pprint(response.text))

    else:
        # problem logging in
        log.error(f"Problem logging in. Status code: {response.status_code}")
        log.error(pprint(response.text))


if __name__ == "__main__":
    main()
