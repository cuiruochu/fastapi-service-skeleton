"""case 子系统自己的 HTTP 入口。

这里适合放只属于复杂 case 能力的 API，例如批量操作、复杂状态流转、
外部系统回调等。
普通简单 CRUD 仍然可以继续放在顶层 layered_myapp/api/case.py。
"""

