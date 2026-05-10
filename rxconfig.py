import reflex as rx

import os
from dotenv import load_dotenv

load_dotenv()
BACKEND = str(os.getenv("BACKEND"))
FRONTEND = str(os.getenv("FRONTEND"))

config = rx.Config(
    app_name="rplace",
    api_url=BACKEND,
    db_url="sqlite:///reflex.db",
    vite_allowed_hosts=[FRONTEND],
    show_built_with_reflex=False,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)