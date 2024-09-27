import parsel
from dataclasses import dataclass
from datetime import datetime
import requests
import re


@dataclass
class MeetupEvent:
    link: str
    name: str
    description: str
    image: str
    location: str
    location_link: str | None
    venue: str | None
    date: datetime


def parse_event_page(html: str) -> MeetupEvent:
    selector = parsel.Selector(html)

    link = selector.css("head > meta:nth-child(28)::attr(content)").get()
    name = (
        selector.css(
            "#main > div.px-5.w-full.border-b.border-shadowColor.bg-white.py-2.lg\:py-6 > div > h1::text"
        )
        .get()
        .replace("\n", "")
        .split()
    )
    image = selector.css(
        "#main > div.flex.w-full.flex-col.items-center.justify-between.border-t.border-gray2.bg-gray1.pb-6.lg\:px-5 > div.md\:max-w-screen.w-full.bg-gray1 > div > div.flex.flex-grow.flex-col.lg\:mt-5.lg\:max-w-2xl > div.emrv9za > div:nth-child(1) > picture > div > img::attr(src)"
    ).get()
    description = selector.css("#event-details > div.break-words")

    texts = []
    for element in description.xpath(".//p | .//li"):
        text = element.xpath("string(.)").get().strip()
        text = text.replace("\n", " ")
        text = " ".join(text.split())

        if element.root.tag == "li":
            text = f"• {text}"  # Formatting list items with bullet points
        texts.append(text)

    description = "\n".join(texts)

    location_a = selector.css(
        "#event-info > div.bg-white.px-5.pb-3.pt-6.sm\:pb-4\.5.lg\:py-5.lg\:rounded-t-2xl > div:nth-child(1) > div.flex.flex-col > div > div.overflow-hidden.pl-4.md\:pl-4\.5.lg\:pl-5 > a"
    )
    location_link = location_a.css("::attr(href)").get()
    location = (
        selector.css(
            "#event-info > div.bg-white.px-5.pb-3.pt-6.sm\:pb-4\.5.lg\:py-5.lg\:rounded-t-2xl > div:nth-child(1) > div.flex.flex-col > div > div.overflow-hidden.pl-4.md\:pl-4\.5.lg\:pl-5 > div::text"
        )
        .get()
        .replace("\n", "")
        .split()
    )

    pattern = r'"dateTime":"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2})?)"'
    match = re.search(pattern, html)
    date = match.group(1)

    venue = [""]
    if location[0] != "Online":
        venue = location_a.css("::text").get().replace("\n", "").split()

    return MeetupEvent(
        link=link,
        name=" ".join(name),
        description=description,
        image=image,
        location=" ".join(location),
        location_link=location_link,
        venue=" ".join(venue) if venue != [""] else None,
        date=datetime.fromisoformat(date),
    )


def parse_events_page(html: str) -> list[str]:
    selector = parsel.Selector(html)
    events = []
    event_link = selector.css("#event-card-e-1").css("a::attr(href)").get()
    while event_link:
        events.append(event_link)
        event_link = (
            selector.css(f"#event-card-e-{len(events)+1}").css("a::attr(href)").get()
        )

    return events


def get_events(group_url: str) -> list[MeetupEvent]:
    response = requests.get(group_url)
    response.raise_for_status()
    events = parse_events_page(response.text)
    meetup_events = []
    for event in events:
        response = requests.get(event)
        response.raise_for_status()
        meetup_event = parse_event_page(response.text)
        meetup_events.append(meetup_event)

    return meetup_events
