"""case 复杂流程业务编排。

这里负责协调当前子模块内部的 repository、redis、messaging、状态规则等。
如果某段 case 逻辑已经不适合放在 modular_myapp/case/service.py，
可以移动到这里集中维护。
"""
