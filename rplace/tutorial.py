import reflex as rx
from rxconfig import config

class State(rx.State):
    """The app state."""
    
# https://www.florkofcows.com/ - add floating stickers after IP rights
    
def content() -> rx.Component:
    return rx.box(
        rx.el.iframe(
            src="/tutorial/tutorial.html",
            style={
                "width": "100%",
                "height": "100vh",
                "border": "none",
            },
        ),
    )