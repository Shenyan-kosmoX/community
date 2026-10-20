# 研究与工具

想看一个结果，先去案例；想把工具用到自己的问题上，可以从运行说明开始。这里按领域和使用方式整理了社区的项目，每个条目都连接到作者维护的完整文档。

## 按领域找

| 领域 | 项目 |
| --- | --- |
| 光子学 | [Floquet–Maxwell](#project-floquet-maxwell) |
| 时变电磁学 | [Floquet–Maxwell](#project-floquet-maxwell) |
| 生态学 | [EcoDynamics](#project-ecodynamics) |
| 动力系统 | [EcoDynamics](#project-ecodynamics) |
| 写作与表达 | [WeChat Content Studio](#project-wechat-content-studio) |

## 按使用方式找

| 提供形式 | 项目 |
| --- | --- |
| 计算工具箱 | [Floquet–Maxwell](#project-floquet-maxwell) · [EcoDynamics](#project-ecodynamics) |
| Python 库 | [Floquet–Maxwell](#project-floquet-maxwell) · [EcoDynamics](#project-ecodynamics) · [WeChat Content Studio](#project-wechat-content-studio) |
| Agent skill | [WeChat Content Studio](#project-wechat-content-studio) |
| CLI | [WeChat Content Studio](#project-wechat-content-studio) |

<a id="project-floquet-maxwell"></a>

## Floquet–Maxwell

**光子学、时变电磁学** · 计算工具箱、Python 库

材料随时间变化时，光的频率、增长与传播会怎样改变？空间周期与调制图案又能带来什么新的行为？Floquet–Maxwell 以 Legume 的几何、Bloch 模式、电磁场和辐射导出为基础，连接时变材料、Floquet 求解与开放响应。可以先看一个现成案例，再选择自己需要的空间、材料与动力学接口。

MIT开源 · 17类能力与20项研究案例

[进入项目](https://github.com/Shenyan-kosmoX/floquet-maxwell) · [安装与第一次运行](https://github.com/Shenyan-kosmoX/floquet-maxwell/blob/main/docs/sors/RUN.md) · [完整能力地图](https://github.com/Shenyan-kosmoX/floquet-maxwell/blob/main/docs/sors/CAPABILITIES.md) · [全部案例](https://github.com/Shenyan-kosmoX/floquet-maxwell/blob/main/docs/sors/CASES.md)

### 可以开展的工作

| 工作 | 工具与方法 |
| --- | --- |
| 建立图案薄膜与场模型 | 多层二维几何、原生模式与场导出、可保存读回的模态包、物理场与简并子空间比较。 |
| 设计材料调制 | 多区域相位、多时间谐波、连续行波、跨动量耦合、逐晶胞固定随机幅相与非对角介电张量。 |
| 计算动力学与空间场 | 正负频率 Floquet 谱、一周期传播、有限脉冲、长期演化及 E/H/D 场和波包重建。 |
| 研究开放与色散响应 | 共同辐射通道、频率相关记忆浴、Lorentz/Drude 辅助场、左右模态与留数、相干输入、侧带散射和 Green 响应。 |
| 比较方法与数值影响 | 分层收敛、解析薄膜与均匀 PTC、独立时间积分、Meep 和球阵列 T-matrix 等比较路线。 |

全部研究案例连接 LPR 周期阵列、Science Advances 与 Nature Photonics 的调制响应、Minkov–Fan 行波波包、Garg 球阵列、Jin 张量选择规则，以及 Zhang 空间—时间编码的协议迁移。独立基准覆盖导模薄膜、开放色散系统、共同通道、有限 Floquet 散射和直接时变场。各案例保留具体模型、计算结果与原文差异，方便按自己关心的物理问题选择。

### 从一个例子开始

- [偏振与张量耦合](https://github.com/Shenyan-kosmoX/floquet-maxwell/blob/main/cases/jin2025-tensor/CASE.md)：由真实 Legume 场计算不同偏振的耦合结构，观察节点怎样随偏振变化。
- [行波与波包传播](https://github.com/Shenyan-kosmoX/floquet-maxwell/blob/main/sptc_toolbox/results/sptc_baselines/minkov2018_legume/report.md)：比较三个驱动速度下的 W1 波导波包，查看场图、运行参数和文献对照。

<a id="project-ecodynamics"></a>

## EcoDynamics

**生态学、动力系统** · 计算工具箱、Python 库

一个长期稳定的生态系统，为什么也会短期放大扰动？延迟、记忆、物种间作用与持续入侵，会怎样改变群落的恢复和组成？EcoDynamics 把这些问题连接到可复用的模型、积分方法和观测量。你可以从一个二维例子理解计算，再组合接口研究更复杂的群落。

MIT开源 · 9类能力与8项研究案例

[进入项目](https://github.com/Shenyan-kosmoX/ecodynamics) · [安装与第一次运行](https://github.com/Shenyan-kosmoX/ecodynamics/blob/main/docs/sors/RUN.md) · [完整能力地图](https://github.com/Shenyan-kosmoX/ecodynamics/blob/main/docs/sors/CAPABILITIES.md) · [全部案例](https://github.com/Shenyan-kosmoX/ecodynamics/blob/main/docs/sors/CASES.md) · [研究结果](https://github.com/Shenyan-kosmoX/ecodynamics/blob/main/docs/results_index.md)

### 可以开展的工作

| 工作 | 工具与方法 |
| --- | --- |
| 建立群落模型 | gLV、UIM/IIM/VUM 饱和相互作用、平衡与可行性、完整 Jacobian、居民子群落和稀有入侵率。 |
| 分析稳定与扰动 | 指定度量下的反应性、非正规性、有限时间增益和最优扰动；非线性脉冲、阈值事件与物种损失。 |
| 加入时间结构 | 单常时滞、初始历史与跳变传播、延迟谱、指数记忆增广和轨迹。 |
| 研究网络与群落组装 | 随机和配对系综、食物网、互利结构、顺序引入与删除、年龄和删失统计、可恢复的运行账本。 |
| 连接经验参数 | Stein、Friedman 与 Hu 来源的七个微生物群落，保留参数映射、坐标约定及居民与入侵分析。 |

全部研究案例覆盖六篇文献、一个经验群落适配案例和一个解析基础案例。文献部分连接 Yang 的反应性与时滞研究、Qian–Akçay 群落组装、Allesina–Tang 稳定性准则、Tang–Allesina 反应性转变，以及 Pigani 的离散时滞和分布记忆。结果索引提供原图对照与计算报告；变量、时间尺度、扰动度量和抽样方式随各研究说明。

### 从一个例子开始

- [稳定性与瞬态放大](https://github.com/Shenyan-kosmoX/ecodynamics/blob/main/cases/foundation/CASE.md)：用一个二维系统看到渐近稳定与短期放大如何同时出现，适合第一次运行。
- [群落组装](https://github.com/Shenyan-kosmoX/ecodynamics/blob/main/studies/assembly_2020/README.md)：查看顺序入侵和物种替换的已有结果，按固定环境与检查点继续计算。
- [经验微生物群落](https://github.com/Shenyan-kosmoX/ecodynamics/blob/main/studies/reactivity_2023/empirical/README.md)：从来源参数计算平衡、反应性与入侵方向，了解不同群落的变量约定。

<a id="project-wechat-content-studio"></a>

## WeChat Content Studio

**写作与表达** · Agent skill、CLI、Python 库

稿件写完之后，标题层级、图片位置和复制到编辑器的效果，还需要花时间整理。WeChat Content Studio 把这些工作放进一个本地文章项目，保存文字、素材、排版选择和输出。你可以用 CLI 直接操作，也可以让 Agent 调用三个 skill 协助。

MIT 开源 · 0.1.1 源码版 · 3 个 skill

[进入项目](https://github.com/Shenyan-kosmoX/wechat-content-studio) · [安装与第一次运行](https://github.com/Shenyan-kosmoX/wechat-content-studio/blob/main/docs/QUICKSTART.md) · [Skills 使用指南](https://github.com/Shenyan-kosmoX/wechat-content-studio/blob/main/docs/SKILLS.md) · [全部案例](https://github.com/Shenyan-kosmoX/wechat-content-studio/blob/main/cases/first-article/case.yaml)

### 可以开展的工作

| 工作 | 工具与方法 |
| --- | --- |
| 文章与素材 | 支持共同写作、材料整理和完整稿件排版，保存段落计划、素材身份与指定位置。 |
| 预览与交付 | 生成本地正文和预览 HTML，提供富文本、纯文本复制，以及需要补传图片时的插入清单。 |
| 参考风格与个人库 | 分析用户选定的文字与布局样本，生成候选，导入并版本化维护个人风格和预设。 |

首个使用案例通过原创短文和基础排版演示文章创建、检查、渲染与 skill 安装。参考账号模板和个人文章保留在使用者自己的工作区。

### 从一个例子开始

- [排一篇已有稿件](https://github.com/Shenyan-kosmoX/wechat-content-studio/blob/main/docs/QUICKSTART.md)：跟着命令生成本地预览，检查段落层次并复制到公众号编辑器。

### 这个项目提供的 Skills

| Skill | 能帮你做什么 |
| --- | --- |
| [文章创作与排版](https://github.com/Shenyan-kosmoX/wechat-content-studio/blob/main/plugins/wechat-content-studio/skills/wechat-compose-article/SKILL.md) | 整理文字和图片，保留指定内容与位置，生成可复制预览。 |
| [参考风格提取](https://github.com/Shenyan-kosmoX/wechat-content-studio/blob/main/plugins/wechat-content-studio/skills/wechat-distill-style/SKILL.md) | 比较选定文章的写作与排版特点，生成可调整的候选。 |
| [个人风格库管理](https://github.com/Shenyan-kosmoX/wechat-content-studio/blob/main/plugins/wechat-content-studio/skills/wechat-manage-style-library/SKILL.md) | 查看、导入、确认、组合、保存版本与归档。 |

## 继续参与

使用时遇到问题，可以在项目的 Issue 里附上输入、命令和实际结果。想讨论一个还没有定下来的方向，或分享自己做的工具，也欢迎来社区聊聊。

[参与讨论](https://github.com/Shenyan-kosmoX/community/discussions) · [提交自己的项目](https://github.com/Shenyan-kosmoX/community/blob/main/docs/PROJECT-INTAKE.md)
