## 运维手册

**需要进入应用根目录** `cd ./BlogWeb`

- step1 启用现有的venv环境
`python -m venv venv`

- step2 激活venv环境
`.\venv\Scripts\activate`

- step3 创建数据库表(如果是新的数据库地址则需要执行)
`.\venv\Scripts\python.exe .\venv\Scripts\flask.exe db init`

- step4 更新数据库表
`.\venv\Scripts\python.exe .\venv\Scripts\flask.exe db upgrade`

- 激活调试模式(执行此命令需要重启应用)
`export FLASK_DEBUG=1`

- step5 启动应用
`python myblog.py`