import reflex as rx
from rxconfig import config

class State(rx.State):
    """The app state."""
    
def content() -> rx.Component:
    return rx.box(
        rx.color_mode.button(position="top-right")
    )