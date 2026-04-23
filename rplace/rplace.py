#Frontend - 3000, Backend - 8000

import reflex as rx
from rxconfig import config

from . import tutorial, canvas

def mouseEffect() -> rx.Component:
    return rx.grid(
        rx.foreach(
            rx.Var.range(200),
            lambda i: rx.box(height="100%", 
                              width="100%",
                              background_color="#000000", 
                              _hover={"background": "#FBF8EF", 
                                      "transition": "background-color 0.1s ease 0s"}, 
                              style={"transition": "background-color 0.5s ease 0.15s",},)
        ),
        columns="20",
        spacing_x="0",
        spacing_y="0",
        width="100%",
        height="100%",
        z_index="2",
    ),

def content() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading("r/Hack", 
                        font_size="20vw",
                        font_family="Minecart",
                        color="#EC3750", 
                        padding_top="10vw",
                        padding_left="5vw", 
            ),
            rx.spacer(),
            rx.text("Submit PRs to reserve tiles on a grid and change their colors in an effort to create images and compete with other clubs",
                    font_size="2vw",
                    font_family="Phantom Sans",
                    color="#EB525D",
                    padding_top="10vw",
                    padding_left="5vw",
                    padding_right="5vw",
            ),
        ),
        position="fixed",
        top="0",
        left="0",
        height="100%",
        width="100%",
        background_color="transparent",
        z_index="1",
        pointer_events="none",
    )
    
def redirects() -> rx.Component:
    return rx.box(
        rx.hstack(rx.button("Tutorial",
                            on_click=rx.redirect("/tutorial"),
                            font_size="1.7vw",
                            color="#FFFDF1",
                            variant="soft",
                            color_scheme="red",
                            height="5vw",
                            width="10vw",),
                  rx.button("Canvas",
                            on_click=rx.redirect("/canvas"),
                            font_size="1.7vw",
                            color="#FFFDF1",
                            variant="soft",
                            color_scheme="red",
                            height="5vw",
                            width="10vw",),
                  spacing="4",
                ),
        position="fixed",
        padding="3vw",
        justify="center",
        top="67%",
        left="37%",
        z_index="3",
        pointer_events="auto",
    )

def index() -> rx.Component:
    return rx.box(
        content(),
        redirects(),
        mouseEffect(),
        width="100vw",
        height="100vh",
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
    stylesheets = ["fonts.css"],
)

app.add_page(index, title="r/hack")
app.add_page(canvas.content, title="r/hack", route="/canvas")
app.add_page(tutorial.content, title="Tutorial", route="/tutorial")