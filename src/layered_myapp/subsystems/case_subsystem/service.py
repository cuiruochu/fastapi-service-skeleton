"""case 子系统业务编排。

这里负责协调当前子系统内部的 repository、cache、messaging、状态规则等。
如果某段 case 逻辑已经不适合放在顶层 layered_myapp/services/case.py，
可以移动到这里集中维护。
"""

