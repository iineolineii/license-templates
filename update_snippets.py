import json
from collections.abc import Iterable, Iterator
from typing import Required, TypedDict

import httpx


class SimpleLicense(TypedDict, total=False):
    key:      Required[str]
    name:     Required[str]
    url:      Required[str | None]
    spdx_id:  Required[str | None]
    node_id:  Required[str]
    html_url: str


class License(TypedDict):
    key:            str
    name:           str
    spdx_id:        str
    url:            str
    node_id:        str
    html_url:       str
    description:    str
    implementation: str
    permissions:    list[str]
    conditions:     list[str]
    limitations:    list[str]
    body:           str
    featured:       bool


class Snippet(TypedDict):
    body:        str
    description: str
    prefix:      str
    scope:       str


def license_snippet(license: License) -> Snippet:
    body = license["body"].replace("$", "\\$")

    return {
        "body":        body,
        "description": license["description"],
        "prefix":      license["key"],
        "scope":       "license"
    }


def fetch_licenses() -> Iterator[License]:
    simple_licenses: list[SimpleLicense] = json.loads(httpx.get("https://api.github.com/licenses").text)
    for simple_license in simple_licenses:
        if simple_license["url"] is not None:
            license: License = json.loads(httpx.get(simple_license["url"]).text)
            yield license


def get_snippets(licenses: Iterable[License]) -> Iterator[tuple[str, Snippet]]:
    for license in licenses:
        yield license["name"], license_snippet(license)


licenses = fetch_licenses()
snippets = dict(get_snippets(licenses))
print(json.dumps(snippets, indent=4))
