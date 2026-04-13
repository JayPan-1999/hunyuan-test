# 简单实时消息项目

这是一个最小可运行的 Python SSE 示例项目：

- 浏览器打开页面后会自动订阅 `/events`
- 任意客户端调用 HTTP 接口 `/publish` 发送消息
- 页面会立即更新为最新收到的那条消息
- 不做数据库存储，只保留进程内的最新消息用于新连接初始化

## 运行方式

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

如果你之前切换过 Python 版本，导致虚拟环境里的二进制包版本不匹配，可以先删除 `.venv` 后重新执行上面的命令。

启动后访问：

```text
http://127.0.0.1:8000
```

SSE 地址：

```text
http://127.0.0.1:8000/events
```

发布消息接口：

```text
POST http://127.0.0.1:8000/publish
```

## 测试方式

你可以直接在页面底部输入消息点击发送。

如果你想从别的客户端发消息，可以直接调用 HTTP 接口：

```bash
curl --location 'http://127.0.0.1:8000/publish' \
--header 'Content-Type: application/json' \
--data '{"message":"hello from curl"}'
```

页面订阅的是 SSE，所以浏览器会自动收到新消息并同步显示。
