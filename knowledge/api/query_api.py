import asyncio
from typing import Union

import uvicorn
from fastapi import FastAPI, Depends, BackgroundTasks,Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from knowledge.core.deps import get_query_service
from knowledge.core.paths import get_front_page_dir
from starlette.staticfiles import StaticFiles

from knowledge.schema.query_schema import QueryRequest, QueryResponse, StreamSubmitResponse, HistoryResponse
from knowledge.service.query_service import QueryService
from knowledge.utils.sse_util import create_sse_queue, sse_generator
from knowledge.utils.task_util import get_done_task_list


def register_router(app: FastAPI):
    pass



def create_app():
    #1. 创建FastAPI
    app = FastAPI(
        description="掌柜智库检索流程API",
        version="1.0"
    )

    #2. 处理跨域问题: 其实我们这个项目不需要考虑跨域问题
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # ← 和 credentials=True 冲突
        allow_credentials=False,
        allow_methods=["*"],  # ← 和 credentials=True 冲突
        allow_headers=["*"],  # ← 和 credentials=True 冲突
    )

    #3. 挂载静态文件,也就是指定静态文件的访问路径: 其实就是写静态资源的匹配路径
    # 如果前端的请求路径是 /front/import.html 那么后端就 "挂载的目录" 找import.html
    front_dir = get_front_page_dir()
    app.mount("/front", StaticFiles(directory=front_dir))

    #4. 注册路由
    register_router(app)

    return app

if __name__ == '__main__':
    # 运行FastAPI 服务
    app = create_app()

    uvicorn.run(app, host="0.0.0.0", port=8011)