import reflex as rx
from rxconfig import config

from . import tutorial

class State(rx.State):
    """The app state."""
    
def link(text: str, url: str, bool: bool) -> rx.Component:
    return rx.link(
        rx.text(
            text,
            size="6",
            weight="bold",
            style={
                "color": "#EC3750",
                "textDecoration": "underline",
                "textDecorationThickness": "2px",
                }
            ),
        href=url,
        is_external=bool,
    )

def navbar() -> rx.Component:
    return rx.grid(
        rx.image(
            src="/flag-orpheus-top.png",
            width="10em",
            height="auto",
        ),
        rx.hstack(
            link(text="HackClub",   url="https://hackclub.com",                            bool=True, ),
            link(text="Tutorial",   url="/tutorial",                                       bool=False,),
            link(text="Repository", url="https://github.com/Decrescent398/rplace-commits", bool=True, ),
            justify="center",
            spacing="7",
            display=["none", "none", "flex"],
        ),
        rx.color_mode.button(position="top-right"),
        top="0px",
        z_index="5",
        columns="1fr 3fr 1fr",
        align_items="center",
        width="100%",
        style={
            "backdropFilter": "blur(20px), saturate(120%)",
            "WebkitBackdropFilter": "blur(20px), saturate(120%)",
        }
    )

def index() -> rx.Component:
    return rx.box(
        rx.vstack(
          navbar(),
          inset="0",
          z_index="1",
          background_color="transparent",
          width="100%", 
        ),
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
app.add_page(tutorial.content, title="Tutorial", route="/tutorial")