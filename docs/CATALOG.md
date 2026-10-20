# 维护研究与工具目录

项目加入组织后，在 `community.json` 的 `projects` 中登记一次。主页、社区入口和完整目录从这里读取名称、介绍和链接；详细方法、结果与开发记录继续放在各项目仓库。

## 添加一个项目

沿用现有项目条目，填写下面这些内容：

| 字段 | 怎样填写 |
| --- | --- |
| `id` | 稳定的英文标识，如 `floquet-maxwell`。名称调整时保留它，目录里的链接就能继续使用。 |
| `name`、`direction` | 项目名称与研究或使用方向。 |
| `use` | 一句话说明读者可以用它完成什么工作。 |
| `summary` | 介绍项目关心的问题，以及工具怎样帮助读者。 |
| `status` | 目前公开版本的情况；数量和功能以项目自身的记录为准。 |
| `url` | 正式项目仓库的完整 GitHub 地址。 |
| `domains` | 一个或多个研究、使用领域。优先复用目录里已有的名称。 |
| `formats` | 一个或多个交付形式，例如计算工具箱、Python 库、Agent skill、CLI。 |
| `featured` | 是否出现在首页精选中。完整目录仍收录其他已公开项目。 |
| `verified` | 确认仓库已公开且入口可用后设为 `true`；准备中的条目留在配置里，暂不出现在页面中。 |
| `links` | 运行说明、能力目录、全部案例、结果、作者记录和 skill 指南的入口。 |
| `capabilities` | 若干主要工作，每项用 `name` 和 `description` 说明。完整能力留在项目文档中。 |
| `case_summary`、`examples` | 概述案例范围，并选择适合开始阅读的例子。每个例子填写 `name`、`description`、`path`。 |
| `skills` | 该项目提供的 skill，每项填写 `id`、`name`、`description`、`path`。 |

目录按领域和形式提供索引。一个项目可以同时属于多个分类，正文只保留一个条目。Skill 写在所属项目下面；读者可以直接进入 skill 的安装与用法，版本和反馈仍由项目维护。

`links` 支持 `run`、`capabilities`、`cases`、`results`、`development`、`skills`。值一般使用仓库内路径，例如 `docs/INSTALL.md`；生成器会根据项目 `url` 和分支拼接地址。尚未写好的作者记录可以暂时省略，准备完成后再补链接。

## 更新页面

在社区仓库根目录运行：

```sh
python tools/build.py --profile ../Shenyan-kosmoX-profile
python tools/check.py --profile ../Shenyan-kosmoX-profile
python -m unittest discover -s tests -v
```

`docs/RESEARCH.md` 是生成结果。修改它的内容时，回到 `community.json` 调整项目条目；页面的公共介绍和分类排版由 `tools/build.py` 管理。

检查脚本能发现重复的项目、无效标识、格式错误的链接和未重新生成的页面。提交前，再打开项目链接，确认目标文档确实存在且内容合适。

## 迁移时

组织迁移工具会更新社区本身的入口，并保留登记的项目地址。逐个确认项目是否也已经转移，再更新对应的 `url`；仓库内相对路径会随新地址一起生成。这样的安排也适用于项目分批转移的情况。
