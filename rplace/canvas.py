import reflex as rx
from rxconfig import config

import reflex_google_recaptcha_v2
from reflex_google_recaptcha_v2 import google_recaptcha_v2, GoogleRecaptchaV2State

import os
from dotenv import load_dotenv
from github import Github, Auth

load_dotenv()
RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")
GITHUB_FINE_PAT = os.getenv("GITHUB_FINE_PAT")

if not reflex_google_recaptcha_v2.is_key_set():
    reflex_google_recaptcha_v2.set_site_key(RECAPTCHA_SITE_KEY)
    reflex_google_recaptcha_v2.set_secret_key(RECAPTCHA_SECRET_KEY)

auth = Auth.Token(GITHUB_FINE_PAT)
gh = Github(auth=auth, lazy=True)
repo = gh.get_repo("Decrescent398/GithubTutorial-rplace-commits-")

class FormState(rx.State):
    dialog_open: bool = True
    username: str = rx.LocalStorage(sync=True)
    form_error: str
    
    def set_text(self, value: str):
        self.username = value
    
    def toggle_dialog(self):
        self.dialog_open = not self.dialog_open
        
    def fetch_contributors(self):
        contributors = [contributor.login for contributor in repo.get_contributors()]
        return contributors
        
    def check_valid_user(self):
        if self.username in self.fetch_contributors():
            return True
        return False
    
    async def handle_submit(self, form_data: dict):
        recaptcha_state = await self.get_state(GoogleRecaptchaV2State)
        self.username = form_data.get("username", "")
        
        if self.check_valid_user() == False:
            self.form_error += " Please finish the tutorial at http://localhost:3000/tutorial to access this site!\n"
            return
                
        if not recaptcha_state.token_is_valid:
            self.form_error += "Invalid reCaptcha!"
            return
        
        self.toggle_dialog()
        
        
def spacing():
    return rx.box(height="1vh")
    
def link(text: str, url: str, bool: bool) -> rx.Component:
    return rx.link(
        rx.text(
            text,
            size="2",
            color="#FFFDF1",
            weight="medium",
            ),
        href=url,
        is_external=bool,
        padding="0.3vw",
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
                background="transparent",
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
            rx.menu.item(link(text="Home",       url="..",                                               bool=True, )),
            rx.menu.item(link(text="HackClub",   url="https://hackclub.com",                            bool=True, )),
            color_scheme="red",
            background_color="#000000",
        ),
    )
    
def verification():
    return rx.box(
        # Backdrop
        rx.box(
            position="fixed",
            top="0",
            left="0",
            width="100vw",
            height="100vh",
            background_color="#000000",
            z_index="10",
        ),
        # Card
        rx.box(
            rx.center(
                rx.heading("Welcome to r/Hack", 
                           size="7", 
                           margin_bottom="16px", 
                           color="#EC3750",
                           ),
            ),
            spacing(),
            rx.form(
                rx.flex(
                    rx.center(
                        rx.input(
                            value=FormState.username,
                            on_change=FormState.set_text,
                            id="username",
                            placeholder="Github Username",
                            required=True,
                            color_scheme="red",
                            height="6vh",
                        )
                    ),
                    spacing(),
                    rx.box(
                            rx.center(google_recaptcha_v2()),
                            padding_inline="5px",
                           ),
                    spacing(),
                    rx.center(
                        rx.button(
                            "Submit",
                            type="submit",
                            size="3",
                            variant="soft",
                            color_scheme="red",
                        )
                    ),
                    rx.text(FormState.form_error, align="center"),
                    direction="column",
                    spacing="4",
                ),
                on_submit=FormState.handle_submit,
            ),
            position="fixed",
            top="50%",
            left="50%",
            transform="translate(-50%, -50%)",
            background_color="#000000",
            border="1px solid #333",
            padding="32px",
            border_radius="12px",
            z_index="11",
            min_width="320px",
        ),
        display=rx.cond(FormState.dialog_open, "block", "none"),
    )
    
def canvas() -> rx.Component:
    return rx.image(src="/canvas.jpg", width="100%", height="100vh", z_index="1", top="0")

def content() -> rx.Component:
    return rx.box(
        verification(),
        navbar(),
        canvas(),
        width="100%",
    )