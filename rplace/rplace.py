import reflex as rx
from rxconfig import config


class State(rx.State):
    """The app state."""


def index() -> rx.Component:
    return rx.box(
        width="100%",
    )


app = rx.App(
    style={
        "html, body, #root": {
            "height": "100%",
            "width": "100%",
            "margin": "0",
            "padding": "0",
            "background_color": "black",
        },
        "::selection": {"background_color": "#4e8cff"},
    },
    theme = rx.theme(
        breakpoints = ["520px", "768px", "1024px", "1280px", "1640px"],
    ),
    stylesheets = [],
)

app.add_page(index, title="r/hack")