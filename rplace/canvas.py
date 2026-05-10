import reflex as rx
from rxconfig import config
    
import json
import asyncio
import ntplib
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from typing import Set
from sqlmodel import select
from starlette.responses import JSONResponse
from starlette.requests import Request
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

load_dotenv()
BACKEND = str(os.getenv("BACKEND"))

fastapi_app = FastAPI(title="Pixel Place")

connected_clients: Set[WebSocket] = set()
clients_lock = asyncio.Lock()

clock = ntplib.NTPClient()

class ColorState(rx.State):
    
    colors: list[str] = [
        "#be4a2f", "#d77643", "#ead4aa", "#e4a672", "#b86f50", "#733e39", "#3e2731", "#a22633", 
        "#e43b44", "#f77622", "#feae34", "#fee761", "#63c74d", "#3e8948", "#265c42", "#193c3e", 
        "#124e89", "#0099db", "#2ce8f5", "#ffffff", "#c0cbdc", "#8b9bb4", "#5a6988", "#3a4466", 
        "#262b44", "#181425", "#ff0044", "#68386c", "#b55088", "#f6757a", "#e8b796", "#c28569",]
    
    color_picker_usage_state: bool = False
    color_select: str = "#be4a2f"
        
    def change_color_select(self, color):
        self.color_select = color
        return rx.call_script(f"window.currentColor = {json.dumps(color)};")
        
    def usage_toast(self):
        if self.color_picker_usage_state == False:
            self.color_picker_usage_state = True
            return rx.toast.info("Click anywhere to place pixel, hold to drag color picker ", position="bottom-right", close_button=True)

class TimerState(rx.State):
    
    places_left: str = rx.LocalStorage("10", sync=True)
    last_time: str = rx.LocalStorage(datetime.now(timezone.utc).isoformat(), sync=True)
    
    servers: list[str] = [
        "time.google.com",
        "time.cloudflare.com",
        "time.nist.gov",
        "time.ntp.org",
    ]
    
    def reset_places(self):
        
        for server in self.servers:
            
            try:
                response = clock.request(server, version=3)
            except TimeoutError:
                continue
            
            break

        current_time = datetime.fromtimestamp(response.tx_time, timezone.utc)

        time_prev = datetime.fromisoformat(self.last_time) 
        
        if (time_prev - current_time).total_seconds() > 0:
            self.last_time = rx.LocalStorage(current_time.isoformat(), sync=True)
            self.places_left = 10
            return
        
    def limit_places(self):
        
        self.places_left = str(int(self.places_left) - 1)
        
    def no_places_toast(self):
        
        if int(self.places_left) == 0:
            return rx.toast.info("Out of pixels! Check back in an hour to place more.", position="bottom-right", close_button=True)

class Positions(rx.Model, table=True):
    
    x: int
    y: int
    color: str

@fastapi_app.get("/api/pixels")
async def get_pixels():
    with rx.session() as session:
        rows = session.exec(select(Positions)).all()
        return JSONResponse(
            [{
                "x": row.x,
                "y": row.y,
                "color": row.color
            }for row in rows]
        )
        
async def broadcast(message: dict):
    
    dead = []
    async with clients_lock:
        
        for socket in connected_clients:
            try:
                await socket.send_json(message)
            except Exception:
                dead.append(socket)
                
        for socket in dead:
            connected_clients.discard(socket)
        
@fastapi_app.post("/api/place")
async def place_pixel_request(request: Request):
    
    data = await request.json()

    try:
        x = int(data["x"])
        y = int(data["y"])
        color = str(data["color"])
    except (KeyError, TypeError, ValueError) as e:
        return JSONResponse(
            {
                "ok": False, 
                "error": str(e)
            },
            status_code=400
        )

    with rx.session() as session:
        session.add(
            Positions(
                x=x,
                y=y,
                color=color,
            )
        )
        session.commit()
    
    await broadcast(
        {
            "x": x,
            "y": y,
            "color": color
        }
    )
    
    return JSONResponse(
        {
            "ok": True
        }
    )
    
@fastapi_app.websocket("/api/ws/pixels")
async def pixel_socket(websocket: WebSocket):
    
    await websocket.accept()
    async with clients_lock:
        connected_clients.add(websocket)
        
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        async with clients_lock:
            connected_clients.discard(websocket)

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
                    color="#ffffff", 
                    stroke_width="2", 
                    size=20,
                ),
                size="2",
                variant="soft",
                color_scheme="gray",
                background="#000000",
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
            rx.menu.item(link(text="Home",       url="..",                                               bool=True, )),
            rx.menu.item(link(text="HackClub",   url="https://hackclub.com",                            bool=True, )),
            color_scheme="red",
            background_color="#000000",
        ),
        data_ui="true",
    )
    
def canvas() -> rx.Component:
    return rx.box(
            rx.el.canvas(
                id="canvas", 
                display="block",
                on_click=TimerState.limit_places,
            ),
            rx.script(
            "window.__placesLeft = " + TimerState.places_left.to_string() + ";"
            ),
            rx.script(
            """
            (function(){
                const PIXEL = 6;
                const API = "%s";
                const WS_URL = API.replace(/^http/, "ws") + "/api/ws/pixels";

                window.__pixels = window.__pixels || [];

                function drawPixel(ctx, p) {
                    ctx.fillStyle = p.color;
                    ctx.fillRect(p.x * PIXEL, p.y * PIXEL, PIXEL, PIXEL);
                }
                function repaintAll(ctx) {
                    for (const p of window.__pixels) drawPixel(ctx, p);
                }

                function resizeCanvas(canvas, ctx) {
                    const snap = document.createElement("canvas");
                    snap.width  = canvas.width;
                    snap.height = canvas.height;
                    if (canvas.width && canvas.height) {
                        snap.getContext("2d").drawImage(canvas, 0, 0);
                    }
                    const dpr = window.devicePixelRatio || 1;
                    canvas.width  = window.innerWidth  * dpr;
                    canvas.height = window.innerHeight * dpr;
                    canvas.style.width  = window.innerWidth  + "px";
                    canvas.style.height = window.innerHeight + "px";
                    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
                    ctx.imageSmoothingEnabled = false;
                    repaintAll(ctx);
                }

                async function loadInitial(ctx) {
                    try {
                        const res  = await fetch(API + "/api/pixels");
                        const data = await res.json();
                        window.__pixels = data;
                        repaintAll(ctx);
                    } catch (e) { console.error("failed to load pixels", e); }
                }

                function openSocket(ctx) {
                    let ws;
                    function connect() {
                        ws = new WebSocket(WS_URL);
                        ws.onmessage = (ev) => {
                            try {
                                const p = JSON.parse(ev.data);
                                window.__pixels.push(p);
                                drawPixel(ctx, p);
                            } catch (e) { console.error(e); }
                        };
                        ws.onclose = () => setTimeout(connect, 1000);
                        ws.onerror = () => ws.close();
                    }
                    connect();
                }

                function init() {
                    const canvas = document.getElementById("canvas");
                    if (!canvas) { requestAnimationFrame(init); return; }
                    if (canvas.dataset.ready === "1") return;
                    canvas.dataset.ready = "1";

                    const ctx = canvas.getContext("2d");
                    resizeCanvas(canvas, ctx);
                    window.addEventListener("resize", () => resizeCanvas(canvas, ctx));
                    window.currentColor = window.currentColor || "#be4a2f";

                    loadInitial(ctx).then(() => openSocket(ctx));

                    window.addEventListener("click", (e) => {
                        if (e.target.closest("[data-ui]")) return;
                        const left = Number(window.__placesLeft);
                        if (!Number.isFinite(left) || left <= 0) return;

                        const rect = canvas.getBoundingClientRect();
                        const x = e.clientX - rect.left;
                        const y = e.clientY - rect.top;
                        if (x < 0 || y < 0 || x > rect.width || y > rect.height) return;

                        const cellX = Math.floor(x / PIXEL);
                        const cellY = Math.floor(y / PIXEL);
                        const p = { x: cellX, y: cellY, color: window.currentColor };
                        window.__placesLeft = left - 1;

                        window.__pixels.push(p);
                        drawPixel(ctx, p);

                        fetch(API + "/api/place", {
                            method: "POST",
                            headers: {"Content-Type": "application/json"},
                            body: JSON.stringify(p),
                        }).catch(err => console.error("place failed", err));
                    });
                }
                init();
            })();
            """ % (BACKEND)
            ),
            width="100%", 
            height="100vh",
            position="fixed",
            top="0",
            left="0",
            z_index="1",
            style={"pointerEvents": rx.cond(TimerState.places_left == '0', "none", "auto")},
            on_mouse_move=[ColorState.usage_toast, TimerState.no_places_toast,],
            )

def color_placer():
    return rx.box(
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
                        lambda color: rx.box(
                            background_color=color, 
                            height="4vh",
                            width="2vw", 
                            cursor="pointer",
                            on_click=lambda: ColorState.change_color_select(color),
                            style=rx.match(
                                color,
                                (
                                    ColorState.color_select, 
                                    {"border": "3px solid #E5E7EB", "border_radius": "5px",},
                                ),
                                {},
                            ),
                        ),
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
            z_index="10000",
            data_ui="true",
        ),
    
def content() -> rx.Component:
    return rx.box(
        navbar(),
        canvas(),
        color_placer(),
        width="100%",
    )