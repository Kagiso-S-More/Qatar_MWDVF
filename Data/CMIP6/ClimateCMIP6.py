
from pathlib import Path
from datetime import datetime
import time
import logging
import requests
import xarray as xr

BASE_DIR = Path(r"C:\Users\Kagiso\WaterNetwork\CMIP6")
BASE_URL = "https://ds.nccs.nasa.gov/thredds/ncss/grid/AMES/NEX/GDDP-CMIP6"

MODEL = "ACCESS-CM2"
MEMBER = "r1i1p1f1"

SCENARIOS = ["ssp245", "ssp585"]
VARIABLES = [
    "pr",
    "tasmax",
    "tasmin",
    "hurs",
    "rsds",
    "rlds",
    "sfcWind",
]

YEARS = range(2031, 2071)

BOUNDS = {
    "north": 26.3,
    "south": 24.4,
    "west": 50.7,
    "east": 51.7,
}

MAX_RETRIES = 4
RETRY_DELAY = 10
TIMEOUT = (30, 180)
MIN_FILE_SIZE = 1000

BASE_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = BASE_DIR / "CMIP6_Download_Log.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("CMIP6")


def build_request(scenario, variable, year):
    filename = (
        f"{variable}_day_{MODEL}_{scenario}_{MEMBER}"
        f"_gn_{year}_v2.0.nc"
    )

    url = (
        f"{BASE_URL}/{MODEL}/{scenario}/{MEMBER}/"
        f"{variable}/{filename}"
    )

    params = {
        "var": variable,
        **BOUNDS,
        "horizStride": 1,
        "time_start": f"{year}-01-01T12:00:00Z",
        "time_end": f"{year}-12-31T12:00:00Z",
        "accept": "netcdf3",
    }

    return url, params


def verify_file(filepath, variable, year):
    try:
        if not filepath.exists():
            return False

        if filepath.stat().st_size < MIN_FILE_SIZE:
            return False

        with xr.open_dataset(filepath) as ds:
            if variable not in ds.data_vars:
                return False

            if "time" not in ds.sizes:
                return False

            expected_days = (
                datetime(year + 1, 1, 1)
                - datetime(year, 1, 1)
            ).days

            if ds.sizes["time"] != expected_days:
                return False

            if "lat" not in ds.sizes or "lon" not in ds.sizes:
                return False

            if ds.sizes["lat"] == 0 or ds.sizes["lon"] == 0:
                return False

            data = ds[variable]

            if not data.isel(time=0).notnull().any().item():
                return False

        return True

    except Exception as exc:
        logger.warning(
            "Verification failed for %s: %s",
            filepath.name,
            exc,
        )
        return False


def download_file(session, scenario, variable, year):
    folder = BASE_DIR / MODEL / scenario / variable
    folder.mkdir(parents=True, exist_ok=True)

    output_file = folder / (
        f"Qatar_{MODEL}_{scenario}_{variable}_{year}.nc"
    )

    temporary_file = output_file.with_suffix(".nc.part")

    if verify_file(output_file, variable, year):
        logger.info("SKIPPED | %s", output_file.name)
        return "skipped"

    url, params = build_request(scenario, variable, year)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(
                "DOWNLOADING | %s | Attempt %d/%d",
                output_file.name,
                attempt,
                MAX_RETRIES,
            )

            with session.get(
                url,
                params=params,
                stream=True,
                timeout=TIMEOUT,
            ) as response:
                response.raise_for_status()

                with open(temporary_file, "wb") as file:
                    for chunk in response.iter_content(
                        chunk_size=65536
                    ):
                        if chunk:
                            file.write(chunk)

            if not verify_file(temporary_file, variable, year):
                raise ValueError(
                    "Downloaded file failed NetCDF verification."
                )

            temporary_file.replace(output_file)

            size_kb = output_file.stat().st_size / 1024

            logger.info(
                "SUCCESS | %s | %.1f KB",
                output_file.name,
                size_kb,
            )

            return "downloaded"

        except Exception as exc:
            logger.warning(
                "ERROR | %s | Attempt %d | %s",
                output_file.name,
                attempt,
                exc,
            )

            if temporary_file.exists():
                temporary_file.unlink()

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)

    logger.error("FAILED | %s", output_file.name)
    return "failed"


def main():
    total = (
        len(SCENARIOS)
        * len(VARIABLES)
        * len(YEARS)
    )

    results = {
        "downloaded": 0,
        "skipped": 0,
        "failed": 0,
    }

    failed_files = []

    logger.info("=" * 65)
    logger.info("NASA NEX-GDDP-CMIP6 QATAR DATA DOWNLOAD")
    logger.info("Model: %s", MODEL)
    logger.info("Scenarios: %s", ", ".join(SCENARIOS))
    logger.info("Period: %d–%d", min(YEARS), max(YEARS))
    logger.info("Variables: %s", ", ".join(VARIABLES))
    logger.info("Total files: %d", total)
    logger.info("=" * 65)

    with requests.Session() as session:
        session.headers.update({
            "User-Agent": "Qatar-CMIP6-Research/1.0"
        })

        count = 0

        for scenario in SCENARIOS:
            for variable in VARIABLES:
                for year in YEARS:
                    count += 1

                    logger.info(
                        "PROGRESS | %d/%d | %.1f%%",
                        count,
                        total,
                        count / total * 100,
                    )

                    status = download_file(
                        session,
                        scenario,
                        variable,
                        year,
                    )

                    results[status] += 1

                    if status == "failed":
                        failed_files.append(
                            f"{scenario}, {variable}, {year}"
                        )

                    if status == "downloaded":
                        time.sleep(0.5)

    logger.info("=" * 65)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("Downloaded: %d", results["downloaded"])
    logger.info("Already available: %d", results["skipped"])
    logger.info("Failed: %d", results["failed"])
    logger.info("=" * 65)

    if failed_files:
        failed_path = BASE_DIR / "CMIP6_Failed_Downloads.txt"

        failed_path.write_text(
            "\n".join(failed_files),
            encoding="utf-8",
        )

        logger.warning(
            "Failed download list saved to: %s",
            failed_path,
        )
    else:
        logger.info("All requested files verified successfully.")


if __name__ == "__main__":
    main()
