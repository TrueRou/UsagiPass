import asyncio
import tempfile
import zipfile
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from usagipass.app import settings
from usagipass.app.logging import log, Ansi
from usagipass.app.models import Card

screenshots_folder = Path.cwd() / ".data" / "screenshots"
screenshots_folder.mkdir(exist_ok=True)


async def capture_multiple_screenshot(cards: list[Card]) -> tuple[dict[str, str], Path]:
    results = {}
    for card in cards:
        results.update(await capture_card_screenshot(card))

    temp_dir = tempfile.mkdtemp()
    zip_path = Path(temp_dir) / "screenshots.zip"

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for key, value in results.items():
            zipf.write(value, arcname=f"{key}.png")

    return results, zip_path


async def capture_card_screenshot(card: Card) -> dict[str, str]:
    # ID-1 300dpi
    target_width = 638
    target_height = 1012

    params = {
        "front": {
            "path": screenshots_folder / f"{card.card_id}_front.png",
            "url": f"{settings.app_url}cards/{card.uuid}?publish=true&back=false",
        },
        "back": {
            "path": screenshots_folder / f"{card.card_id}_back.png",
            "url": f"{settings.app_url}cards/{card.uuid}?publish=true&back=true",
        },
    }

    results = {}

    async with asyncio.TaskGroup() as group:
        for key, value in params.items():
            task = asyncio.to_thread(_capture_screenshot, value["path"], value["url"], target_width, target_height)
            if result := await group.create_task(task):
                results[f"{card.card_id}_{key}"] = result

    return results


def _capture_screenshot(screenshot_path, url, target_width, target_height) -> str:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument(f"--window-size={target_width},{target_height}")
    chrome_options.add_argument(f"--app={url}")
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        log(f"正在访问: {url}", Ansi.LCYAN)

        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, "img")))

        body_width = driver.execute_script("return document.body.scrollWidth")
        body_height = driver.execute_script("return document.body.scrollHeight")

        driver.set_window_size(2 * target_width - body_width, 2 * target_height - body_height)
        driver.get_screenshot_as_file(str(screenshot_path))
        log(f"截图成功: {screenshot_path}", Ansi.LGREEN)

        return str(screenshot_path)
    except Exception as e:
        log(f"截图过程中出错: {repr(e)}", Ansi.RED)
        return None
    finally:
        driver.quit()
