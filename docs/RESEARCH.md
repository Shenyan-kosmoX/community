# 研究与工具

这里汇集社区正在维护的科研设施与工作工具。可以从一个科学问题进入，也可以先运行一个例子，看看已有能力怎样连接到自己的研究。

Floquet–Maxwell 与 EcoDynamics 已经公开，均提供 Python 数值库、完整能力目录、研究案例、现有结果和本地运行说明。代码采用 MIT 许可，文献图像与外部材料在各项目中保留自己的来源说明。

## Floquet–Maxwell：从电磁场到时空调制

[进入项目](https://github.com/Shenyan-kosmoX/floquet-maxwell) · [安装与第一次运行](https://github.com/Shenyan-kosmoX/floquet-maxwell/blob/main/docs/sors/RUN.md) · [完整能力地图](https://github.com/Shenyan-kosmoX/floquet-maxwell/blob/main/docs/sors/CAPABILITIES.md) · [全部研究案例](https://github.com/Shenyan-kosmoX/floquet-maxwell/blob/main/docs/sors/CASES.md)

材料随时间变化时，光的频率、增长与传播会怎样改变？空间周期与调制图案又能带来什么新的行为？Floquet–Maxwell 围绕这些问题建设计算工具，以 Legume 的几何、Bloch 模式、电磁场和辐射导出为基础，连接时变材料、Floquet 求解与开放响应。

| 可以开展的工作 | 已有入口与内容 |
| --- | --- |
| 建立图案薄膜与场模型 | 多层二维几何、原生模式与场导出、可保存读回的模态包、物理场与简并子空间比较 |
| 设计材料调制 | 多区域相位、多时间谐波、连续行波、跨动量耦合、逐晶胞固定随机幅相与非对角介电张量 |
| 计算动力学与空间场 | 正负频率 Floquet 谱、一周期传播、有限脉冲、长期演化及 E/H/D 场和波包重建 |
| 研究开放与色散响应 | 共同辐射通道、频率相关记忆浴、Lorentz/Drude 辅助场、左右模态与留数、相干输入、侧带散射和 Green 响应 |
| 比较方法与数值影响 | 分层收敛、解析薄膜与均匀 PTC、独立时间积分、Meep 和球阵列 T-matrix 等比较路线 |

当前目录按 **17 类能力、20 项案例**组织材料。文献案例包括 LPR 周期阵列、Science Advances 与 Nature Photonics 的调制响应、Minkov–Fan 行波波包、Garg 球阵列、Jin 张量选择规则，以及 Zhang 空间—时间编码的协议迁移。独立基准进一步覆盖导模薄膜、开放色散系统、共同通道、有限 Floquet 散射和直接时变场。

初次运行可以选择 [Jin 张量耦合案例](https://github.com/Shenyan-kosmoX/floquet-maxwell/blob/main/cases/jin2025-tensor/CASE.md)，从真实 Legume 场计算不同偏振的耦合结构。关注传播的读者可以进入 [W1 行波案例](https://github.com/Shenyan-kosmoX/floquet-maxwell/blob/main/sptc_toolbox/results/sptc_baselines/minkov2018_legume/report.md)；关注开放响应的读者可以从能力地图选择辐射、散射和 Green 接口。

每个案例说明自己的物理模型、求解路线、计算范围和当前差异。目录中的数字用于帮助浏览；具体问题采用哪些近似、有哪些独立证据，可以沿案例进入对应报告与记录。

## EcoDynamics：群落怎样响应与演化

[进入项目](https://github.com/Shenyan-kosmoX/ecodynamics) · [安装与第一次运行](https://github.com/Shenyan-kosmoX/ecodynamics/blob/main/docs/sors/RUN.md) · [完整能力地图](https://github.com/Shenyan-kosmoX/ecodynamics/blob/main/docs/sors/CAPABILITIES.md) · [全部研究案例](https://github.com/Shenyan-kosmoX/ecodynamics/blob/main/docs/sors/CASES.md)

一个长期稳定的生态系统，为什么也会短期放大扰动？延迟、记忆、物种间作用与持续入侵，会怎样改变群落的恢复和组成？EcoDynamics 把这些问题连接到可复用的模型、积分方法和观测量，帮助研究者从明确的方程与条件出发开展计算。

| 可以开展的工作 | 已有入口与内容 |
| --- | --- |
| 建立群落模型 | gLV、UIM/IIM/VUM 饱和相互作用、平衡与可行性、完整 Jacobian、居民子群落和稀有入侵率 |
| 分析稳定与扰动 | 指定度量下的反应性、非正规性、有限时间增益和最优扰动；非线性脉冲、阈值事件与物种损失 |
| 加入时间结构 | 单常时滞、初始历史与跳变传播、延迟谱、指数记忆增广和轨迹 |
| 研究网络与群落组装 | 随机和配对系综、食物网、互利结构、顺序引入与删除、年龄和删失统计、可恢复的运行账本 |
| 连接经验参数 | Stein、Friedman 与 Hu 来源的七个微生物群落，保留参数映射、坐标约定及居民与入侵分析 |

当前目录按 **9 类能力、8 项案例**组织材料，覆盖六篇文献、一个经验群落适配案例和一个解析基础案例。文献部分连接 Yang 的反应性与时滞研究、Qian–Akçay 群落组装、Allesina–Tang 稳定性准则、Tang–Allesina 反应性转变，以及 Pigani 的离散时滞和分布记忆。

第一次运行可以从 [稳定性与瞬态放大](https://github.com/Shenyan-kosmoX/ecodynamics/blob/main/cases/foundation/CASE.md)开始，用一个二维系统看到渐近稳定与短期放大如何同时出现。已有研究结果可直接从[结果索引](https://github.com/Shenyan-kosmoX/ecodynamics/blob/main/docs/results_index.md)进入。想做较大的组装计算，可以查看[组装案例](https://github.com/Shenyan-kosmoX/ecodynamics/blob/main/studies/assembly_2020/README.md)中的固定环境、检查点与统计说明。

能力和案例分类帮助读者寻找相关工作。不同观测量的检查与适用条件保存在各自报告中，变量、时间尺度、扰动度量和抽样单位也随模型一起说明，方便比较与进一步研究。

## 共同维护一份清楚的研究起点

两个项目使用 [SORS 0.1](../standards/SORS/SORS.md)连接项目说明、代码、运行环境、研究案例和结果。作者可以保留自己的目录与学科习惯；共同清单帮助读者找到材料，也让固定脚本及时发现缺项、断链或环境引用遗漏。

这套组织方式支持直接使用，也支持与 AI 一起阅读和运行。你可以先确定想观察的现象，再沿案例找到输入与方法，修改相关参数，并用已有检查理解变化。遇到新的问题时，一份配置、一条命令和实际结果就能让讨论更快开始。

欢迎贡献新的模型、独立比较、研究案例或使用说明。已有结果中还没有解释清楚的差异，也可能成为很好的共同研究起点。

## 继续整理的工具

团队还在整理研究与表达中使用的 skill、资料工具，以及微信公众号内容整理与排版工具。准备完成后会在这里提供仓库与使用入口。欢迎在讨论区分享自己反复遇到的问题，以及希望一起维护的工具。

[提交自己的项目](PROJECT-INTAKE.md) · [参与讨论](DISCUSSIONS.md)
