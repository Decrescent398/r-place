import reflex as rx
from rxconfig import config

from . import tutorial

class State(rx.State):
    """The app state."""
    
def link(text: str, url: str, bool: bool) -> rx.Component:
    return rx.link(
        rx.text(
            text,
            size="2",
            color_scheme="gray",
            ),
        href=url,
        is_external=bool,
        z_index="5",
    )

def navbar() -> rx.Component:
    return rx.menu.root(
        rx.menu.trigger(
            rx.button(
                rx.icon(
                    "align_justify", 
                    stroke_width="2", 
                    size=20,
                ),
                size="2",
                variant="soft",
                color_scheme="gray",
                high_contrast=True,
                radius="large",
                position="fixed",
                top="20px",
                right="20px",
            ),
        ),
        rx.menu.content(
            rx.menu.item(link(text="Tutorial",   url="/tutorial",                                       bool=False,)),
            rx.menu.item(link(text="Repository", url="https://github.com/Decrescent398/rplace-commits", bool=True, )),
            rx.menu.item(link(text="Download",   url="/canvas.jpg",                                     bool=True, )),
            rx.menu.item(link(text="HackClub",   url="https://hackclub.com",                            bool=True, )),
        )
    )
    
def canvas() -> rx.Component:
    return rx.image(src="/canvas.jpg", width="100%", height="100vh", z_index="1", top="0")

def index() -> rx.Component:
    return rx.box(
        navbar(),
        canvas(),
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