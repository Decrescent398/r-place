import reflex as rx
from rxconfig import config

import reflex_google_recaptcha_v2
from reflex_google_recaptcha_v2 import google_recaptcha_v2, GoogleRecaptchaV2State

import os
from dotenv import load_dotenv
from github import Github, Auth
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import AccessDeniedError
import requests
from urllib.parse import urlparse, parse_qs

import asyncio

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

load_dotenv()
RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")
GITHUB_FINE_PAT = os.getenv("GITHUB_FINE_PAT")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")

GITHUB_AUTHORIZATION_BASE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_API_URL = "https://api.github.com/user"

if not reflex_google_recaptcha_v2.is_key_set():
    reflex_google_recaptcha_v2.set_site_key(RECAPTCHA_SITE_KEY)
    reflex_google_recaptcha_v2.set_secret_key(RECAPTCHA_SECRET_KEY)

auth = Auth.Token(GITHUB_FINE_PAT)
gh = Github(auth=auth, lazy=True)
repo = gh.get_repo("Decrescent398/GithubTutorial-rplace-commits-")

class FormState(rx.State):
    dialog_open: bool = False
    form_error: str
    
    username: str = ""
    oauth_token: dict = {}
    oauth_state: str = ""
    github_authorised: bool = False
    oauth_error: str = ""
    
    def set_text(self, value: str):
        self.username = value
    
    def toggle_dialog(self):
        self.dialog_open = not self.dialog_open
        
    def fetch_contributors(self):
        contributors = [contributor.login for contributor in repo.get_contributors()]
        return contributors
    
    def github_login(self):
        github = OAuth2Session(
            GITHUB_CLIENT_ID, 
            redirect_uri=GITHUB_REDIRECT_URI, 
            scope=["read:user", "user:email"]
        )
        
        authorization_url, state = github.authorization_url(GITHUB_AUTHORIZATION_BASE_URL)
        
        self.oauth_state = state
        return rx.redirect(authorization_url)
    
    def get_callback_url(self):
        return rx.call_script(
            "window.location.href",
            callback=FormState.authorize_github_user,
        )
    
    def authorize_github_user(self, callback_url: str):
        
        try:
            parsed_url = urlparse(callback_url)
            query_params = parse_qs(parsed_url.query)
            
            error = query_params.get("error", [None])[0]
            if error:
                self.oauth_error += "Github OAuth Error" + error + "\n"
                return rx.redirect('canvas/access-denied')
            
            code = query_params.get("code", [None])[0]
            returned_state = query_params.get("state", [None])[0]
            
            if not code:
                self.oauth_error += "Missing OAuth Code" + "\n"
                return rx.redirect('canvas/access-denied')
            
            if not returned_state:
                self.oauth_error += "Missing OAuth State" + "\n"
                return rx.redirect('canvas/access-denied')
            
            if returned_state != self.oauth_state:
                self.oauth_error += "OAuth State Mismatch" + "\n"
                self.oauth_error += "Expected:" + self.oauth_state + "\n"
                self.oauth_error += "Returned:" + returned_state + "\n"
                return rx.redirect('canvas/access-denied')
        
            github = OAuth2Session(
                GITHUB_CLIENT_ID, 
                redirect_uri=GITHUB_REDIRECT_URI, 
                scope=["read:user,user:email"]
            )
            
            token = github.fetch_token(
                GITHUB_TOKEN_URL, 
                client_secret=GITHUB_CLIENT_SECRET, 
                authorization_response=callback_url,
                headers={"Accept": "application/json",},
            )
            
            self.oauth_token = token
            
            github = OAuth2Session(
                GITHUB_CLIENT_ID, 
                token=token
            )
            
            response = github.get(GITHUB_USER_API_URL)
            
            if not response.ok:
                self.oauth_error += "Github user API failed:" + response.text + "\n"
                return rx.redirect('canvas/access-denied')
            
            user_info = response.json()
            username = user_info.get('login')
            
            if not username:
                self.oauth_error += "Github username missing" + response.text + "\n"
                return rx.redirect('canvas/access-denied')
            
            self.username = username
            if self.username in self.fetch_contributors():
                self.github_authorised = True
            else:
                self.oauth_error += "Tutorial not finished" + "\n"
                return rx.redirect('canvas/access-denied')
            
            return rx.redirect('/canvas')
        
        except Exception as e:
            self.oauth_error += e + "\n"
            return rx.redirect('canvas/access-denied')
        
    async def handle_submit(self):
        recaptcha_state = await self.get_state(GoogleRecaptchaV2State)
                
        if not recaptcha_state.token_is_valid:
            return rx.window_alert("Invalid reCaptcha!")
        
        if not self.github_authorised:
            return rx.window_alert("User not Found! Finish the tutorial at http://localhost:3000/tutorial to access this site!")
        
        self.toggle_dialog()
        
        await asyncio.sleep(1.5)
        
        return rx.toast.info("Click anywhere to show/hide color picker", position="bottom-right", close_button=True)
        
        
class ColorState(rx.State):
    
    colors: list[str] = [
        "#be4a2f", "#d77643", "#ead4aa", "#e4a672", "#b86f50", "#733e39", "#3e2731", "#a22633", 
        "#e43b44", "#f77622", "#feae34", "#fee761", "#63c74d", "#3e8948", "#265c42", "#193c3e", 
        "#124e89", "#0099db", "#2ce8f5", "#ffffff", "#c0cbdc", "#8b9bb4", "#5a6988", "#3a4466", 
        "#262b44", "#181425", "#ff0044", "#68386c", "#b55088", "#f6757a", "#e8b796", "#c28569",]
    
    color_picker_state: bool = False
    
    x: int = 50
    y: int = 50
    
    def toggle_color_picker(self):
        self.color_picker_state = not self.color_picker_state
        
        
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
                z_index=9999,
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
    
@rx.page(route="/canvas/access-denied", title="Access Denied",)
def error_details():
    return rx.center(
        rx.vstack(
            rx.image(src="/confused_dinosaur.jpeg", height="20vh",),
            rx.text("Access Denied :(", size="7",),
            rx.text("This might have been a github OAuth issue, or you may have not finished the tutorial properly", size="4",),
            rx.code(f"Error: {FormState.oauth_error}", size="4", variant="outline",),
            rx.link("Click here to go to the tutorial page", href="/tutorial", size="4",),
            spacing="4",
        ),
        height="100vh",
    )
    
@rx.page(route="/canvas/callback", title="Authenticating with Github...", on_load=FormState.get_callback_url,)
def callback():
    return rx.center(
        rx.vstack(
            rx.spinner(size="3"),
            rx.text("Authenticating with Github...", size="4"),
            spacing="4",
        ),
        height="100vh",
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
                        rx.button(
                            rx.icon(tag="github"),
                            "Sign in with Github",
                            on_click=FormState.github_login,
                            variant="surface",
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
    return rx.box(
            rx.image(src="/canvas.jpg", width="100%", height="100vh", z_index="999", top="0",),
            width="100%", 
            height="100vh",
            position="fixed",
            on_click=ColorState.toggle_color_picker,
            )

def color_placer():
    return rx.cond(
        ~FormState.dialog_open & ColorState.color_picker_state,
        rx.box(
            rx.script(
                """
                (function(){
                    function init() {
                        const box = document.querySelector('[data-draggable]');
                        if (!box) {
                            setTimeout(init, 50);
                            return;
                        }
                        
                        let dragging = false;
                        let offsetX = 0;
                        let offsetY = 0;
                        
                        const savedLeft = localStorage.getItem('draggable-left');
                        const savedTop = localStorage.getItem('draggable-top');
                        if (savedLeft && savedTop) {
                            box.style.left = savedLeft;
                            box.style.top = savedTop;
                        }
                        
                        document.addEventListener('mousedown', (e) => {
                            const target = e.target.closest('[data-draggable]');
                            if (target) {
                                dragging = true;
                                offsetX = e.clientX - target.offsetLeft;
                                offsetY = e.clientY - target.offsetTop;
                            }
                        });
                        
                        document.addEventListener('mousemove', (e) => {
                            if (dragging && box) {
                                box.style.left = (e.clientX - offsetX) + 'px';
                                box.style.top = (e.clientY - offsetY) + 'px';
                            }
                        });
                        
                        document.addEventListener('mouseup', () => {
                            if (dragging && box) {
                                localStorage.setItem('draggable-left', box.style.left);
                                localStorage.setItem('draggable-top', box.style.top);
                            }
                            dragging = false;
                        });
                    }
                    
                    init();
                })();
                """
            ),
            rx.box(
                rx.grid(
                    rx.foreach(
                        ColorState.colors,
                        lambda color: rx.box(background_color=color, height="4vh", width="2vw", cursor="pointer")
                    ),
                    columns="8",
                    spacing_x="1",
                    spacing_y="1",
                ),
                position="absolute",
                left="50px",
                top="50px",
                height="22vh",
                width="20vw",
                border_radius="12px",
                background_color="#000000",
                padding="15px",
                cursor="grab",
                data_draggable="true",
            ),
            position="fixed",
            z_index="1000",
        ),
    )

def content() -> rx.Component:
    return rx.box(
        verification(),
        navbar(),
        canvas(),
        color_placer(),
        width="100%",
    )