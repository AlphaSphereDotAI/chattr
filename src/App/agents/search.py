from typing import Any, Dict, List

from langchain_community.utilities import SearxSearchWrapper
from pydantic import StrictInt, StrictStr

search = SearxSearchWrapper(searx_host="http://localhost:8080")
search.headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}


def get_search_results(
    query: StrictStr, num_results: StrictInt = 10
) -> List[StrictStr]:
    results: List[Dict[Any, Any]] = search.results(query=query, num_results=num_results)
    links: List[StrictStr] = []
    for result in results:
        if result["link"] is not None:
            print(result["link"])
            links.append(result["link"])
    return links


if __name__ == "__main__":
    print(get_search_results(query="What is the capital of France"))
