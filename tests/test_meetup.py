import pytest
from meetup_notifier import parse_event_page, get_events
from meetup_notifier.meetup import parse_events_page
import requests_mock


@pytest.fixture
def event():
    return open("tests/fixtures/event.html").read()


@pytest.fixture
def online_event():
    return open("tests/fixtures/online_event.html").read()


@pytest.fixture
def group_events():
    return open("tests/fixtures/group_events.html").read()


def test_parse_event_page(event):
    meetup_event = parse_event_page(event)
    assert (
        meetup_event.link
        == "https://www.meetup.com/es-ES/python-valencia-meetup/events/300608083/"
    )
    assert meetup_event.name == "Linters en Python (con ejemplo práctico)"
    assert (
        meetup_event.image
        == "https://secure.meetupstatic.com/photos/event/9/2/5/600_520622341.webp?w=750"
    )
    assert meetup_event.description.startswith(
        "Entre las diferentes herramientas que disponemos en python para mejorar la calidad de nuestro código, los linters destacan"
    )
    assert meetup_event.location == "Carrer de Marià Cuber, 17 · València, Va"
    assert (
        meetup_event.location_link
        == "https://www.google.com/maps/search/?api=1&query=39.464138%2C%20-0.334373"
    )
    assert meetup_event.venue == "wayCO Cabanyal | Coworking València"
    assert meetup_event.date.strftime("%Y-%m-%d %H:%M:%S") == "2024-04-30 18:30:00"


def test_parse_online_event(online_event):
    meetup_event = parse_event_page(online_event)
    assert meetup_event.link == "https://www.meetup.com/es-ES/bcnrust/events/303443195/"
    assert meetup_event.name == "15th BcnRust Meetup"
    assert (
        meetup_event.image
        == "https://secure.meetupstatic.com/photos/event/9/9/8/c/600_523599308.webp?w=750"
    )
    assert meetup_event.description.startswith(
        "This time we have been collaborating with Codurance and Heavy Duty Builders"
    )
    assert meetup_event.location == "Online event"
    assert meetup_event.location_link is None
    assert meetup_event.venue is None
    assert meetup_event.date.strftime("%Y-%m-%d %H:%M:%S") == "2024-10-10 18:00:00"


def test_parse_events_page(group_events: str) -> list[str]:
    pages = parse_events_page(group_events)

    assert len(pages) == 2
    assert pages == [
        "https://www.meetup.com/wordpress-valencia-meetup/events/303351475/?eventOrigin=group_events_list",
        "https://www.meetup.com/wordpress-valencia-meetup/events/302311226/?eventOrigin=group_events_list",
    ]


def test_get_events(event, online_event, group_events):
    with requests_mock.Mocker() as m:
        m.get(
            "https://www.meetup.com/es-ES/python-valencia-meetup/events/",
            text=group_events,
        )
        m.get(
            "https://www.meetup.com/wordpress-valencia-meetup/events/303351475/?eventOrigin=group_events_list",
            text=online_event,
        )
        m.get(
            "https://www.meetup.com/wordpress-valencia-meetup/events/302311226/?eventOrigin=group_events_list",
            text=event,
        )

        events = get_events(
            "https://www.meetup.com/es-ES/python-valencia-meetup/events/"
        )
        assert len(events) == 2
        assert events[0].name == "15th BcnRust Meetup"
        assert events[1].name == "Linters en Python (con ejemplo práctico)"
