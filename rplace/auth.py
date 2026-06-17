import reflex as rx
from rxconfig import config

import os
from dotenv import load_dotenv
from github import Github, Auth
from requests_oauthlib import OAuth2Session
from urllib.parse import urlparse, parse_qs

load_dotenv()

BACKEND = str(os.getenv("BACKEND"))
FRONTEND = str(os.getenv("FRONTEND"))

GITHUB_FINE_PAT = os.getenv("GITHUB_FINE_PAT")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = FRONTEND + str(os.getenv("GITHUB_REDIRECT_URI"))

PRIVILEGED_USERS = os.getenv("PRIVILEGED_USERS").split(',')

GITHUB_AUTHORIZATION_BASE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_API_URL = "https://api.github.com/user"

auth = Auth.Token(GITHUB_FINE_PAT)
gh = Github(auth=auth, lazy=True)
repo = gh.get_repo("Decrescent398/GithubTutorial-rplace-commits-")

class FormState(rx.State):
    
    username: str = ""
    oauth_token: dict = {}
    oauth_state: str = ""
    github_authorised: bool = False
    oauth_error: str = ""
        
    def fetch_contributors(self):
        contributors = [contributor.login for contributor in repo.get_contributors()] + PRIVILEGED_USERS
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
        
    def check_auth(self):
        if not self.github_authorised:
            return rx.redirect("/canvas/access-denied")
    
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
            self.oauth_error += str(e) + "\n"
            return rx.redirect('canvas/access-denied')
    
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
        rx.box(
            position="fixed",
            top="0",
            left="0",
            width="100vw",
            height="100vh",
            background_color="#000000",
            z_index="10",
        ),
        rx.box(
            rx.center(
                rx.heading("Welcome to r/Hack", 
                           size="7", 
                           margin_bottom="16px", 
                           color="#EC3750",
                           ),
            ),
            rx.box(height="1vh"),
            rx.center(
                rx.button(
                    rx.icon(tag="git_branch_plus"),
                    "Sign in with Github",
                    on_click=FormState.github_login,
                    variant="surface",
                    color_scheme="red",
                    height="6vh",
                )
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
    )

def content() -> rx.Component:
    return rx.box(
        verification(),
        width="100%",
    )