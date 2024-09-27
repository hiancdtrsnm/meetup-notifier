from meetup_notifier import MeetupEvent, get_events
import typer
from typing_extensions import Annotated
from datetime import datetime, timedelta
import requests
from rich.console import Console

app = typer.Typer()
console = Console()


def notify_telegram(event: MeetupEvent, telegram_token: str, telegram_chat_id: str):
    url = f"https://api.telegram.org/bot{telegram_token}/sendPhoto"

    text = (
        f"{time_until_event(event)}\n"
        f"📝 [Apúntate aqui]({event.link})\n"
        f"📍 [{event.venue}]({event.location_link})\n"
        f"🗺️ {event.location}"
    )
    message_payload = {
        "chat_id": telegram_chat_id,
        "caption": text,
        "photo": event.image,
        "parse_mode": "Markdown",
    }

    response = requests.post(url, data=message_payload)
    response.raise_for_status()

    console.print(f"📢 Evento enviado a Telegram: {event.name}")


def time_until_event(event: MeetupEvent):
    now = datetime.now(event.date.tzinfo)  # Use event date timezone
    tomorrow_start = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    day_after_tomorrow_start = (now + timedelta(days=2)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    time_diff = event.date - now
    event_time_str = event.date.strftime("%H:%M")

    if event.date < now:
        return f"❗️ **El evento ya ocurrió** el {event.date.strftime('%Y-%m-%d')} a las {event_time_str} 🕒"
    elif now < event.date < tomorrow_start:
        return f"🎉 **¡El evento es hoy a las** {event_time_str}**!**"
    elif tomorrow_start <= event.date < day_after_tomorrow_start:
        return f"⏰ **¡El evento es mañana a las** {event_time_str}**!**"
    else:
        return f"📅 **El evento será dentro de {time_diff.days} días**"


@app.command()
def notify(
    events_url: str = typer.Argument(..., help="URL de la página de eventos de Meetup"),
    telegram_token: Annotated[str, "Token de Telegram"] = typer.Option(
        help="Token de Telegram",
        envvar="TELEGRAM_TOKEN",
    ),
    telegram_chat_id: Annotated[str, "Chat ID de Telegram"] = typer.Option(
        help="Chat ID de Telegram",
        envvar="TELEGRAM_CHAT_ID",
    ),
):
    if not telegram_token or not telegram_chat_id:
        console.print(
            "❌ Debes proporcionar un token y un chat ID de Telegram para enviar notificaciones"
        )
    events = get_events(events_url)
    for event in events:
        notify_telegram(event, telegram_token, telegram_chat_id)


if __name__ == "__main__":
    typer.run(notify)
