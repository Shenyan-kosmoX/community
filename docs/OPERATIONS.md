# 维护社区与项目入口

社区文档、项目索引和自动检查一起维护，能够减少使用者在不同仓库间寻找信息的时间。本页汇总当前入口与实际命令，具体研究方法和验证记录由项目保管。

## 仓库各自负责什么

| 仓库 | 内容 |
| --- | --- |
| [Shenyan-kosmoX/.github](https://github.com/Shenyan-kosmoX/.github) | 组织主页、理念和视觉素材 |
| [Shenyan-kosmoX/community](https://github.com/Shenyan-kosmoX/community) | 参与说明、讨论入口、SORS 规范和公共检查器 |
| [Shenyan-kosmoX/ecodynamics](https://github.com/Shenyan-kosmoX/ecodynamics) | 生态动力学工具、案例和验证记录 |
| [Shenyan-kosmoX/floquet-maxwell](https://github.com/Shenyan-kosmoX/floquet-maxwell) | Floquet–Maxwell 工具、案例和计算结果 |

`community.json` 保存社区身份和入口配置，`content/` 保存两份首页源文件。更新首页内容后，通过构建同步生成文件。

## 本地检查社区内容

开发环境使用 Python 3.12，检查器依赖见 `requirements-dev.txt`。在 community 根目录运行：

```sh
python -m pip install -r requirements-dev.txt
python tools/build.py --profile ../Shenyan-kosmoX-profile
python tools/check.py --profile ../Shenyan-kosmoX-profile
python -m unittest discover -s tests -v
```

`--profile` 指向本地组织 `.github` 仓库，目录名称可以不同。社区工作流 [Community review](../.github/workflows/community-review.yml) 在 Linux / Python 3.12 上检查公开内容、运行检查器测试，并在 PR 中列出需要人工关注的变化。

## 检查 SORS 项目

新接入项目采用 [SORS 0.1](../standards/SORS/README.md)。在 community 目录中指向已经取得的项目源码：

```sh
python standards/SORS/tools/check_project.py --root ../ecodynamics --report /tmp/ecodynamics-sors.json
python standards/SORS/tools/check_project.py --root ../floquet-maxwell --report /tmp/floquet-sors.json
```

以上路径是示例；Windows 下可把报告位置换为本地临时目录。默认只检查结构与引用，报告保留独立的执行和科学审阅状态。

需要检查某个已声明的命令时，先在相应环境安装项目与检查器依赖，再明确选择案例和步骤。例如在首次使用的 Floquet–Maxwell 源码目录尚无同名结果时：

```sh
python standards/SORS/tools/check_project.py --root ../floquet-maxwell --case jin2025-tensor-selection --step small-tensor-map --step plot --run --report /tmp/jin-run.json
```

检查器按依赖顺序执行所选步骤。已有输出需要由项目的运行约定处理；上面的计算入口要求新结果目录。文档化步骤、长时间扫描和特殊软件案例按对应说明执行，运行记录保存在项目中。

## 接入 GitHub 公共检查

[公共工作流](../.github/workflows/sors-project-review.yml) 使用固定版本的社区检查器，默认执行项目结构检查，保存报告，并为 PR 汇总索引、依赖、方法、判据和结果的变化。

首个公开版本固定为社区提交 `68fad7e518b3e96f454e843a47ec9da22e942d55`。项目可以加入以下工作流：

```yaml
name: Project review
on:
  push:
    branches: [main]
  pull_request:
permissions:
  contents: read
jobs:
  structure:
    uses: Shenyan-kosmoX/community/.github/workflows/sors-project-review.yml@68fad7e518b3e96f454e843a47ec9da22e942d55
    with:
      checker-ref: 68fad7e518b3e96f454e843a47ec9da22e942d55
```

工作流引用和 `checker-ref` 一起固定，一起升级。项目工作流中已采用固定 SHA 的官方 Actions：checkout `11d5960a326750d5838078e36cf38b85af677262`、setup-python `a26af69be951a213d495a4c3e4e4022e16d87065`；报告上传使用 upload-artifact `ea165f8d65b6e75b540449e92b4886f43607fa02`。升级通过 PR 说明并检查变更。

公共结构作业在 GitHub 托管 Linux 上运行，超时 10 分钟，仓库权限为只读，checkout 不保留凭据。项目安装与科研代码放在项目自己的测试作业中。工作流使用 `pull_request`，公共测试无需私密凭据。

## 两个参考项目的运行检查

| 项目 | 已配置的 CI |
| --- | --- |
| [EcoDynamics workflows](https://github.com/Shenyan-kosmoX/ecodynamics/tree/main/.github/workflows) | Ubuntu / Windows，Python 3.11 / 3.12；软件测试、lint、打包、基础案例；另有最低依赖与可选加速检查 |
| [Floquet–Maxwell workflows](https://github.com/Shenyan-kosmoX/floquet-maxwell/tree/main/.github/workflows) | Ubuntu，Python 3.12；软件及物理控制、实际 Legume N9 场投影与纯计算绘图 |

平台覆盖以工作流配置和实际运行记录为准。当前运行状态从各仓库 Actions 查看；长期科研结果和可选后端的检查另由案例记录说明。

## 维护讨论与项目目录

Discussions 已启用，主要入口沿用 General、Q&A 和 Ideas，分别用于研究问题、方法交流和项目提案。类别 slug 与链接保存在配置中，表单位于 `.github/DISCUSSION_TEMPLATE/`。调整类别后核对实际发帖入口，再同步文档与配置。

项目公开后，在研究目录加入真实仓库入口，检查 README、案例索引、联系渠道和许可证。新增成果同步到项目能力与案例目录。较大文件采用版本化 Release，记录下载地址、大小和摘要。

日常小改动由内部成员在 PR 审阅。方法或结果有分歧时，保留各自依据，必要时转到 Discussions 并相互链接。仓库规则、要求通过的检查和 CODEOWNERS 随实际成员权限维护，合并前查看当前平台设置。

## 配置、支持计划与早期模板

维护者配置会影响首页联系人、CODEOWNERS 和公共联络。初期联系人为 @wenkuizhao261-pixel；更换时同时更新 GOVERNANCE、项目提案说明和表单，并核对实际写权限。

免费 API 计划仍在寻求资金支持。确认可用额度、负责人与交付渠道后，更新 `docs/RESOURCES.md`，调整筹备标记和 `applications_open`，再重建公开入口。

`templates/research-project/` 保留早期 `schema_version: 1` 的 `research.json` 与检查器，用于已有项目维护和迁移参考；相关回归测试继续保留。当前正式接入使用 SORS 0.1 的项目与案例索引。迁移说明见[模板首页](../templates/research-project/README.md)。

社区原创内容采用 MIT；项目分别说明自有代码、数据和第三方材料的使用条件。发布后核对导航、表单与 Actions，并留下对应版本记录。
