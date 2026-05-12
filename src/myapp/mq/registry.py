"""MQ 拓扑注册表。

这里集中收集各个业务模块暴露出来的 MQ topology。
main.py 只依赖这个注册表，不需要逐个 import case、incident 等业务模块。
"""

from .topology import MQQueueTopology, declare_mq_topology


async def declare_registered_mq_topologies() -> None:
    """声明注册表中收集到的全部 MQ 拓扑。"""
    from myapp.case.messaging import get_case_mq_topologies

    topologies: list[MQQueueTopology] = [
        *get_case_mq_topologies(),
    ]
    await declare_mq_topology(topologies)
