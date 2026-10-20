# Python 科研项目早期参考包 · Legacy v1

这里保留社区早期的 Python 项目运行协议：`research.json` 使用数值 `schema_version: 1`，配套脚本检查安装、小案例和验证入口。已经采用这一版本的项目，可以继续查阅并维护原有记录。

当前正式接入采用 [SORS 0.1](../../standards/SORS/README.md)。新项目可参考 [EcoDynamics](https://github.com/Shenyan-kosmoX/ecodynamics) 和 [Floquet–Maxwell](https://github.com/Shenyan-kosmoX/floquet-maxwell) 的项目与案例索引，沿用自己的目录和专业文档。

## 从 v1 迁移

SORS 0.1 将项目共用信息和具体案例连接起来：项目清单登记能力、环境、文档与案例入口，每个案例说明问题、模型、运行步骤、检查和结果。原有研究说明、结果和源文件摘要可以直接引用。

| v1 中的内容 | SORS 0.1 中的位置 |
| --- | --- |
| 项目名称、维护者、许可 | `project` 与 `licensing` |
| Python、平台、依赖和安装入口 | `environments` |
| 运行说明、依据、证据与限制文档 | 项目 `documents` 与案例中的引用 |
| smoke / verify 命令 | 案例 `execution.steps`，按用途标记 run / check |
| 参照与预期输出 | 案例 `references`、`outputs`、`criteria` 和 `checks` |
| 已有执行与人工审阅记录 | 案例 `results` 及对应报告 |

迁移时使用字符串 `schema_version: '0.1'`，保留一个根项目清单。可以继续使用 JSON，也可以选择 YAML。详细字段与实际检查命令见[技术附录](../../standards/SORS/TECHNICAL-FORMAT.md)和[自动检查说明](../../standards/SORS/GITHUB-CHECKS.md)。

## 维护已有 v1 项目

本目录原有文件和测试继续保留。使用 v1 时，在已准备的项目根目录填写 `research.json`，并采用原有检查器：

```sh
python tools/research_check.py --root .
```

在独立环境中确认命令后，添加 `--run` 执行安装、小案例与验证。复制旧工作流时需要相应的 `tools/research_check.py` 和 `tools/sensitive_changes.py`；其默认平台为 Linux / Python 3.12。

正式的 SORS 0.1 公共工作流通过固定社区提交号调用，接入方式见[维护说明](../../docs/OPERATIONS.md)。
