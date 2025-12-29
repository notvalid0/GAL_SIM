"""
Galgame对话模拟器主应用
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from .api.dialogue import router as dialogue_router

app = FastAPI(title="GAL-SIM", description="基于LLM的Galgame对话模拟器")

# 挂载API路由
app.include_router(dialogue_router)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="gal_sim/static"), name="static")

# 配置模板目录
templates = Jinja2Templates(directory="gal_sim/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("gal_sim/static/favicon.ico")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)