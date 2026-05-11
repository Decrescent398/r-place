import reflex as rx

import os
from dotenv import load_dotenv

load_dotenv()
BACKEND = str(os.getenv("BACKEND"))
FRONTEND = str(os.getenv("FRONTEND"))
DB = str(os.getenv("DB"))

config = rx.Config(
    app_name="rplace",
    api_url=BACKEND,
    db_url=DB,
    vite_allowed_hosts=[FRONTEND],
    show_built_with_reflex=False,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(
            theme= rx.theme(
                breakpoints = ["520px", "768px", "1024px", "1280px", "1640px"],
            ),
        ),
    ]
)