import json
from collections.abc import Iterable, Iterator
from json import JSONDecodeError
from typing import NotRequired, TypedDict

import httpx


URL = "https://api.github.com/licenses"


class SimpleLicense(TypedDict):
    key:      str
    name:     str
    url:      str
    spdx_id:  str | None
    node_id:  str
    html_url: NotRequired[str]


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


def fetch_simple_licenses(url: str) -> Iterator[SimpleLicense]:
    response = httpx.get(url)
    response.raise_for_status()

    try:
        simple_licenses: list[SimpleLicense] = json.loads(response.text)

    except JSONDecodeError as exc:
        raise TypeError(
            f"Invalid simple licenses response. "
            f"Failed to parse as JSON: {response.text}."
        ) from exc

    if not isinstance(simple_licenses, list):
        raise TypeError(
            f"Invalid simple licenses response. "
            f"Expected type list, got {type(simple_licenses)}: {simple_licenses!r}."
        )

    for no, simple_license in enumerate(simple_licenses, start=1):
        if not isinstance(simple_license, dict):
            raise TypeError(
                f"Invalid simple license №{no}. "
                f"Expected dictionary, got {type(simple_license)}: {simple_license!r}."
            )

        yield SimpleLicense(**simple_license)


def fetch_licenses(simple_licenses: Iterable[SimpleLicense]) -> Iterator[License]:
    for simple_license in simple_licenses:
        response = httpx.get(simple_license["url"])
        response.raise_for_status()

        try:
            license = json.loads(response.text)

        except JSONDecodeError as exc:
            raise TypeError(
                f"Invalid license response for {simple_license['name']!r}. "
                f"Failed to parse as JSON: {response.text}."
            ) from exc

        if not isinstance(license, dict):
            raise TypeError(
                f"Invalid license response for {simple_license['name']!r}. "
                f"Expected dictionary, got {type(license)}: {license!r}."
            )

        yield License(**license)


def get_snippets(licenses: Iterable[License]) -> Iterator[tuple[str, Snippet]]:
    for license in licenses:
        yield license["name"], license_snippet(license)


simple_licenses = fetch_simple_licenses(URL)
licenses = fetch_licenses(simple_licenses)
snippets = dict(get_snippets(licenses))
print(json.dumps(snippets, indent=4))
