import logging
import os

import requests


class InfluxDBHandler(logging.Handler):
    def __init__(self, influx_url, token, org, bucket):
        super().__init__()
        self.influx_url = influx_url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.write_url = (
            f"{self.influx_url}/api/v2/write?bucket={bucket}&org={org}&precision=ns"
        )
        self.headers = {
            "Authorization": f"Token {self.token}",
            "Content-Type": "text/plain; charset=utf-8",
        }

    def emit(self, record):
        try:
            message = self.format(record).replace('"', '\\"').replace("\n", "\\n")
            timestamp = int(record.created * 1e9)  # Influx expects nanoseconds
            line = (
                f"logs,logger={record.name},level={record.levelname} "
                f'message="{message}" {timestamp}'
            )
            requests.post(self.write_url, data=line, headers=self.headers, timeout=2)
        except Exception as e:
            print(f"Failed to send log to InfluxDB: {e}")


def setup_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file_path = os.getenv("LOG_FILE", "logs/app.log")

    # Create log directory if not exists
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    # Basic file logging
    logging.basicConfig(
        filename=log_file_path,
        level=getattr(logging, log_level),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # InfluxDB configuration from environment variables
    influx_url = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
    influx_token = os.getenv("INFLUXDB_TOKEN")
    influx_org = os.getenv("INFLUXDB_ORG")
    influx_bucket = os.getenv("INFLUXDB_BUCKET")

    if all([influx_token, influx_org, influx_bucket]):
        influx_handler = InfluxDBHandler(
            influx_url=influx_url,
            token=influx_token,
            org=influx_org,
            bucket=influx_bucket,
        )
        influx_handler.setLevel(getattr(logging, log_level))
        influx_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logging.getLogger().addHandler(influx_handler)
    else:
        logging.warning(
            "InfluxDB logging is disabled. Missing required environment variables."
        )

    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized.")
