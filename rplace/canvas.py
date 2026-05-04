import reflex as rx
from rxconfig import config\
    
import json

class ColorState(rx.State):
    
    colors: list[str] = [
        "#be4a2f", "#d77643", "#ead4aa", "#e4a672", "#b86f50", "#733e39", "#3e2731", "#a22633", 
        "#e43b44", "#f77622", "#feae34", "#fee761", "#63c74d", "#3e8948", "#265c42", "#193c3e", 
        "#124e89", "#0099db", "#2ce8f5", "#ffffff", "#c0cbdc", "#8b9bb4", "#5a6988", "#3a4466", 
        "#262b44", "#181425", "#ff0044", "#68386c", "#b55088", "#f6757a", "#e8b796", "#c28569",]
    
    color_picker_state: bool = False
    color_picker_usage_state: bool = False
    
    x: int = 50
    y: int = 50
    
    color_select: str = "#be4a2f"
    
    def toggle_color_picker(self):
        self.color_picker_state = not self.color_picker_state
        
    def change_color_select(self, color):
        self.color_select = color
        return rx.call_script(f"window.currentColor = {json.dumps(color)};")
        
    def usage_toast(self):
        if self.color_picker_usage_state == False:
            self.color_picker_usage_state = True
            return rx.toast.info("Click anywhere to show/hide color picker and drag", position="bottom-right", close_button=True)
    
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
            rx.menu.item(link(text="Home",       url="..",                                               bool=True, )),
            rx.menu.item(link(text="HackClub",   url="https://hackclub.com",                            bool=True, )),
            color_scheme="red",
            background_color="#000000",
        ),
        data_ui="true",
    )
    
def canvas() -> rx.Component:
    return rx.box(
            rx.el.canvas(id="canvas", style={"display": "block"},),
            rx.script(
            """
                (function(){
                    
                    const PIXEL = 6;
                    
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
                        ctx.drawImage(snap, 0, 0);
                    }
                    
                    function init() {
                        const canvas = document.getElementById("canvas");

                        if (!canvas) {
                            requestAnimationFrame(init);
                            return;
                        }

                        if (canvas.dataset.ready === "1") return;
                        canvas.dataset.ready = "1";

                        const ctx = canvas.getContext("2d");

                        resizeCanvas(canvas, ctx);

                        window.addEventListener("resize", () => resizeCanvas(canvas, ctx));

                        window.currentColor = window.currentColor || "#be4a2f";

                        window.addEventListener("click", (e) => {
                            console.log("clicky");
                            if (e.target.closest("[data-ui]")) return;

                            const rect = canvas.getBoundingClientRect();
                            const x = e.clientX - rect.left;
                            const y = e.clientY - rect.top;
                            if (x < 0 || y < 0 || x > rect.width || y > rect.height) return;

                            const gx = Math.floor(x / PIXEL) * PIXEL;
                            const gy = Math.floor(y / PIXEL) * PIXEL;

                            ctx.fillStyle = window.currentColor;
                            ctx.fillRect(gx, gy, PIXEL, PIXEL);
                        });
                    }
                    init();
                })();
            """
            ),
            width="100%", 
            height="100vh",
            position="fixed",
            top="0",
            left="0",
            z_index="1",
            on_mouse_move=ColorState.usage_toast,
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