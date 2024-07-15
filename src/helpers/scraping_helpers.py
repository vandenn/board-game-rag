import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BOARD_GAME_RULES_BASE_URL = "https://www.ultraboardgames.com/games.php"


def get_board_game_rules_links_batches():
    """
    From the main directory of board games in UltraBoardGames, get the links
    to all the board game subpages to get the corresponding rules.
    """
    # Send a GET request to fetch the raw HTML content of the base URL
    response = requests.get(BOARD_GAME_RULES_BASE_URL)
    response.raise_for_status()

    # Parse the content of the request with BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all links on the page
    all_links = soup.find_all("a", href=True)

    # Extract unique game subpage links
    unique_subpages = set()
    for link in all_links:
        href = link["href"]
        parsed_href = urlparse(href)
        # We ignore certain subpages since they're not board game subpages.
        ignore_list = ["category/", "blog/", "online-shops/"]
        if (
            # Other conditions to prevent getting irrelevant links.
            parsed_href.path.endswith("/")
            and not any(x in parsed_href.path for x in ignore_list)
            and len(parsed_href.path) > 2
            and parsed_href.path.count("/") == 1
        ):
            unique_subpages.add(urljoin(BOARD_GAME_RULES_BASE_URL, href))

    # Generate the game-rules.php links from the subpage links
    game_rules_links = [
        {
            "name": link.get_text(strip=True).replace("/", "-"),
            "url": urljoin(subpage, "game-rules.php"),
        }
        for subpage in unique_subpages
        for link in all_links
        if link["href"] in subpage
    ]

    # Return the extracted links in batches
    batch_size = 100
    total = len(game_rules_links)
    for offset in range(0, total, batch_size):
        yield game_rules_links[offset : offset + batch_size], offset


def read_rules_from_link(link):
    """
    This function scrapes the main content of the board game rules' page.
    """
    # Send a GET request to fetch the raw HTML content
    response = requests.get(link["url"])
    response.raise_for_status()  # Ensure we notice bad responses

    # Parse the content of the request with BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract the main content where the game rules are located
    content_div = soup.find("div", class_="col-md-12")
    content_text = content_div.get_text(separator="\n", strip=True)

    # Do cleaning of unnecessary headers and footers
    content_text = re.sub(
        r"^(Menu\n|Overview\n|Links\n|Other Games\n|Videos\n)+",
        "",
        content_text,
        flags=re.MULTILINE,
    )
    content_text = re.sub(r"Continue Reading$", "", content_text, flags=re.MULTILINE)

    rules = {"name": link["name"], "url": link["url"], "content": content_text}

    return rules
