#!python3

import pathlib
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from typing import Dict, Any
import json
import sys


def gather_all_history_ids():
    pattern = re.compile(r"art-(\w+)\\x08")

    news_container = (
        "~/Library/Containers/com.apple.news/"
        + "Data/Library/Application Support/com.apple.news/"
        + "com.apple.news.public-com.apple.news.private-production"
    )
    reading_list_file = pathlib.Path(news_container, "history").expanduser().absolute()

    with open(reading_list_file, "r"):
        contents = str(reading_list_file.read_bytes())

    return pattern.findall(contents)


async def visit_and_grab_details(
    session: aiohttp.ClientSession, article_id: str
) -> Dict[str, Any]:
    # Construct the Apple News URL from the ID
    apple_news_url = f"https://apple.news/{article_id}"

    try:
        async with session.get(apple_news_url, timeout=40) as response:
            resp = await response.read()
            html = resp.decode("utf-8")

            # Use BeautifulSoup to extract the URL from the redirectToUrlAfterTimeout function
            soup = BeautifulSoup(html, "html.parser")
            if script_tag := soup.find(
                "script", string=lambda t: "redirectToUrlAfterTimeout" in t
            ):
                url_start_index = script_tag.text.index('"https://') + 1
                url_end_index = script_tag.text.index('"', url_start_index)
                url = script_tag.text[url_start_index:url_end_index]
            else:
                url = None

            # Extract the og:title, og:description, og:image, and author meta tags
            if title_tag := soup.find("meta", property="og:title"):
                title = title_tag["content"]
            else:
                title = None

            if description_tag := soup.find("meta", property="og:description"):
                description = description_tag["content"]
            else:
                description = None

            if image_tag := soup.find("meta", property="og:image"):
                image = image_tag["content"]
            else:
                image = None

            if author_tag := soup.find("meta", {"name": "Author"}):
                author = author_tag["content"]
            else:
                author = None

            return {
                "url": url,
                "title": title,
                "description": description,
                "image": image,
                "author": author,
            }
    except Exception as e:
        return {
            "url": apple_news_url,
            "error_details": str(e),
            "encountered_error": True,
        }


async def fetch_with_semaphore(
    session: aiohttp.ClientSession, article: str, semaphore: asyncio.Semaphore
) -> Dict[str, Any]:
    async with semaphore:
        return await visit_and_grab_details(session, article)


if __name__ == "__main__":
    all_article_ids = gather_all_history_ids()

    # Change this to fetch more at once
    semaphore = asyncio.Semaphore(20)

    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = [
                fetch_with_semaphore(session, article, semaphore)
                for article in all_article_ids
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results

    results = asyncio.run(main())

    json.dump(results, sys.stdout, indent=2, default=str)
