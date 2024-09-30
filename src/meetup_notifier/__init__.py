from .meetup import parse_event_page, get_events
from dataclasses import asdict
import requests
import json

import typer

app = typer.Typer()


@app.command()
def events(events_url: str):
    events = get_events(events_url)
    typer.echo(
        json.dumps([asdict(event) for event in events], default=str, ensure_ascii=False)
    )
    if not events:
        raise typer.Exit(code=1)


@app.command()
def last_event(events_url: str):
    events = get_events(events_url)
    if not events:
        typer.echo("No event found", err=True)
        raise typer.Exit(code=1)
    last_event = events[0]
    typer.echo(json.dumps(asdict(last_event), default=str, ensure_ascii=False))


@app.command()
def parse_event(event_url: str):
    response = requests.get(event_url)
    response.raise_for_status()
    meetup_event = parse_event_page(response.text)
    typer.echo(json.dumps(asdict(meetup_event), default=str, ensure_ascii=False))
