from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

from backend.api.routers import chat
from backend.core.config import settings

# 关闭默认 /docs、/redoc（其 CDN 在国内常加载失败导致白屏）
app = FastAPI(
    title=settings.app_name,
    docs_url=None,
    redoc_url=None,
)

app.include_router(chat.router)

# 国内可访问的 BootCDN（Swagger UI / ReDoc）
_SWAGGER_JS = (
    "https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.17.14/swagger-ui-bundle.min.js"
)
_SWAGGER_CSS = (
    "https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.17.14/swagger-ui.min.css"
)
_REDOC_JS = (
    "https://registry.npmmirror.com/redoc/2.1.3/files/bundles/redoc.standalone.js"
)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{settings.app_name} - Docs",
        swagger_js_url=_SWAGGER_JS,
        swagger_css_url=_SWAGGER_CSS,
    )


@app.get("/redoc", include_in_schema=False)
async def custom_redoc():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{settings.app_name} - ReDoc",
        redoc_js_url=_REDOC_JS,
    )


@app.get("/")
def root():
    return {"message": "服务已启动，请访问 /docs"}
