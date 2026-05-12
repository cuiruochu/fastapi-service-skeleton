"""case 复杂流程 MQ 封装。

这里适合放当前子模块专用的 exchange、routing key、消息发布函数和拓扑定义。
外部 service 不应该直接操作底层 MQ 连接，而是调用这里暴露的业务函数。
"""
