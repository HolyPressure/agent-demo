一、fastapi项目三种启动方式：
1、在本地开发模式中直接使用pycharm中的启动命令启动
2、生产模式下，使用uvicorn命令启动，uvicorn main:app[包模块名称，入口，项目目录下，有子包记得: . ,app 就是这个=fastAPI()] --reload
   如果在uv环境中，前面加上 uv run 
   --reload 在修改文件时会自动重新启动
3、在main.py中定义一个main函数，通过运行main函数来启动
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)

app = FastAPI(...)   # ASGI 应用实例；路由都挂在这个对象上
uvicorn 加载方式：模块路径:变量名  →  本项目 backend.main:app

起 ASGI 服务器加载 app
启动（开发）：
  uv run uvicorn backend.main:app --reload
生产：
  去掉 --reload；按需 --host 0.0.0.0、workers 等
也可用：
  uvicorn.run("backend.main:app", reload=True)
注意：
  --reload 仅开发


含有 __init__.py 的目录，在 Python 里叫「包」（package）。
包也是一种可被 import 的对象，所以在导入系统里它也算一种 module，但日常说「模块」时，多半指单个 .py 文件。


二、路由
1、路由
    @app.post
    @app.get
    @app.delete
    @app.patch
    @app.put
    
    async 定义异步函数，新版的fastapi不加也是异步的???
    async def：协程，适合 await IO
    普通 def：同步函数，FastAPI 会丢到线程池执行，并不会变成异步
    
    路由就是将 路径，请求方法，装饰器下方的函数 组合起来形成一个映射关系
    path:[请求路径/为根]
    tags:[给接口分组的标签]
    summary:[接口的总结概要]
    description:[接口的详细描述]
    response_description:[响应数据的详细描述]
    
    fastapi中返回任意东西都可以，一般是字典/对象，它会自动帮我们转换为json

2、路由分发：
    将整个app看作一个总路由
    在功能模块处，创建分路由: chat = APIRouter(prefix="/chat", tags=["聊天"]), 这里需要导入APIRouter从fastapi
    关联分路由：
    在main.py中加载所有分路由,要导入相关模块,多个多行
    app.include_router(chat.chat)


3、路由参数（参数最好有类型提示）
    请求参数，通过路由路径携带的方式  "/studentsId/{student_id}"

    @chat.get('/studentsId/{student_id}', summary='查询当个学生')
    def find_student(student_id: int):    默认情况下，fastapi提供了数据转换和数据校验供功能
        print()
        return
    分路由一致，但是一个传参一个不传参是不影响的；如果有路由传参可能和其他路由冲突，它是按照顺序来匹配的

    @chat.get('/studentsId', summary='查询所有学生')  
    def find_all_student():    默认情况下，fastapi提供了数据转换和数据校验供功能
        print()
        return

三、项目部署
方式 A：Git + 依赖锁定（很常见）
服务器上：
git pull
uv sync --frozen          # 按 uv.lock 装依赖，可复现

配置环境变量或 .env（密钥不要进仓库）
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000
要点：提交 uv.lock，生产不要 --reload。

你的电脑 ──git push──► Git 仓库（GitHub/Gitee 等）
                              │
                         git pull / git clone
                              ▼
                         云服务器
                    （uv sync + 跑 uvicorn）


方式 B：Docker（生产很常用）
镜像里 uv sync / 拷代码，容器启动命令跑 uvicorn。
你们仓库里目前还没有 Dockerfile，阶段六文档里提过可选 Docker。

开发机 / CI：
  有一份代码 + Dockerfile
       │  docker build（COPY 代码、uv sync 装依赖）
       ▼
  镜像（里面已经有代码和依赖）
       │  推到镜像仓库 / 拷到服务器
       ▼
服务器：
  docker pull 镜像（或 load）
  docker run → 容器里直接起 uvicorn


方式 C：导出 requirements 再 pip（兼容老环境）

uv export --no-dev -o requirements.txt

服务器：
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000

