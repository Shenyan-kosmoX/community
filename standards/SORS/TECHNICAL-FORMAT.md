# 项目与案例索引

SORS 0.1 · 2026-10-20

索引为已有说明、代码和结果提供稳定位置。整理正文时可先读[项目组织指南](FORMAT.md)，维护索引与脚本时使用本页和配套 JSON Schema。

## 共同约定

项目根目录保存一份 `research.yaml`、`research.yml` 或 `research.json`，内容均使用同一结构。项目索引的 `schema_version` 为字符串 `'0.1'`，`kind` 为 `project`；案例索引同样标记版本，`kind` 为 `case`。JSON Schema 采用 Draft 2020-12。

对象 ID 使用字母、数字、点、下划线和连字符，以字母或数字开头。一个列表内的 ID 唯一；案例内的输入、输出、判据、参照与步骤各有自己的命名空间。引用字段必须对应同一个项目或案例中的已有 ID。YAML 或 JSON 的重复键会产生错误，避免后写内容悄悄覆盖已有声明。

清单允许额外的领域字段；建议把案例的专业扩展集中在 `extensions` 中。共同字段仍按统一类型解释。新增领域检查可按项目需要运行，通用检查器只检查已定义的共同契约。

## 项目索引

以下顶层字段均为必需，列表可以按实际情况为空；`capabilities`、`environments`、`cases` 至少各有一项。详细定义见[项目 Schema](schemas/project.schema.json)。

| 字段 | 内容 |
| --- | --- |
| `project` | `id`、`name`、字符串 `domain`、字符串 `stage`、非空 GitHub 登录名列表 `maintainers` |
| `documents` | `overview`、`research`、`usage`、`validation`、`limitations`、`sources`、`contributing`，均指向非空的项目文档；可共用同一文件 |
| `capabilities` | 每项提供 `id`、`description`，可用 `documentation` 指向文档 |
| `environments` | 每项提供 `id`、`description`、非空 `platforms` 列表；可补 `dependency_files` 和 `setup_steps` |
| `assets` | 每项提供 `id`、`description`，可用 `record` 引用共享代码、模型或输入 |
| `cases` | 每项提供 `id` 和案例索引的 `manifest` 路径 |
| `licensing` | `code_license`、非空文件 `license_file`，以及 `sources` 或 `details` 文档引用 |
| `extensions` | 项目声明的领域扩展列表，每项至少有 `id`，可提供 `version`、`description`、`record` |

`dependency_files` 为实际存在的项目相对路径列表。每个 `setup_steps` 条目提供 `argv` 参数数组，可增加 `cwd` 和 `timeout_seconds`。安装步骤供使用者和项目自己的环境作业采用，结构检查器不会自动安装或切换环境。

环境平台可使用 `linux`、`windows`、`win32`、`macos`、`darwin`；确实与平台无关的入口可使用 `any`。未知平台名称可以登记，显式运行时必须与当前平台一致。

## 案例索引

除 `extensions` 外，下表字段均为必需。计划案例可以提供空的输入、输出、参照、检查和结果列表，并在说明中列出准备中的内容。详细定义见[案例 Schema](schemas/case.schema.json)。

| 字段 | 内容 |
| --- | --- |
| `id`、`project_id`、`title` | 案例身份、所属项目和名称；与项目索引一致 |
| `stage` | `planned`、`in_progress`、`results_available` |
| `question` | `summary`，可增加 `scope` 和 `record` |
| `capability_refs` | 使用的项目能力 ID 列表 |
| `model` | `description`，可用 `record` 指向模型或参数说明 |
| `inputs` | 每项有 `id`、`description`，可附 `record` 与 `availability` |
| `execution` | `environment_ref`、项目内 `cwd`、`steps` 列表 |
| `outputs` | 每项有 `id`、`description`，可附 `format`、预期 `path` 和说明 `record` |
| `references` | 每项有 `id`、`description`，可用 `record` 指向参照材料 |
| `criteria` | 每项有 `id`、`description`、`representation`，可补 `record` |
| `checks` | 每项有 `id`、`method`、`criterion_refs`、`reference_refs`、`output_refs`，可补 `input_refs`、`implementation` 和 `record` |
| `results` | `status`、`records`、`artifacts`；可用字符串 `notes` 介绍现有结果及其生成条件 |
| `limitations` | 项目相对文档路径或材料引用 |
| `extensions` | 可选领域字段对象 |

`criteria.representation` 为 `documented`、`structured` 或 `pending`。`documented` 指向可以阅读的依据；`structured` 可以补充专业指标和数值约定，通用检查器不解释其科学含义；`pending` 说明尚待形成的部分。

`results.status` 为 `observed`、`planned` 或 `unavailable`。`observed` 至少提供一项可取得的 `records` 引用；已有结果可以包含负结果和未解差异。所有实际结果的本地引用必须存在。`outputs.path` 描述未来可能生成的产物，可以暂时不存在；其他材料引用按实际可用性检查。

## 材料引用

共同的 `record` 对象使用下列三种形式之一：

```yaml
# 已随项目提供的材料
record:
  path: docs/method.md
  locator: 参数与单位

# 外部公开来源；自动检查不访问网络
record:
  url: https://doi.org/10.0000/example
  locator: Figure 2

# 未放入本次发行的材料，说明如何取得或重建
record:
  availability: not_bundled
  description: 历史大规模计算的完整场数组。
  retrieval: 按案例运行说明重新生成；本仓库提供摘要与绘图数据。
```

`not_bundled` 形式需要 `description` 与 `retrieval`，不附虚构的本地路径或下载地址。公开来源应使用可解析的 HTTP(S) URL。`locator` 保存章节、图号或数组位置的阅读提示，0.1 检查器不自动判断其专业含义或验证定位点。

索引中的本地路径相对项目根目录，以 `/` 分隔。路径应留在项目中，包括符号链接解析后的实际位置。Markdown 内部链接按该文档的位置解析。项目主文档的本地链接会检查文件是否存在，外链可达性与章节锚点保留为人工核对事项。

## 执行步骤

步骤包括 `id`、`role`、`mode`。`role` 为 `prepare`、`plan`、`run`、`check` 或 `plot`；`mode: command` 提供非空 `argv` 数组，`mode: documented` 提供 `instructions` 材料引用。

```yaml
execution:
  environment_ref: base-python
  cwd: .
  steps:
    - id: compute
      role: run
      mode: command
      argv: [python, scripts/example.py, --output, results/example.json]
      timeout_seconds: 300
      output_refs: [summary]
    - id: inspect
      role: check
      mode: documented
      depends_on: [compute]
      instructions:
        path: docs/example.md
```

步骤可用 `environment_ref` 覆盖默认环境，可用 `cwd` 覆盖案例工作目录；二者都引用项目根目录的同一套定义。`depends_on` 为无环步骤依赖，`input_refs`、`output_refs` 分别引用本案例的输入和输出。超时默认 300 秒，允许显式设置为 1 至 86400 秒。

显式运行须指定案例与步骤，依赖步骤也逐项指定。安装和其他未选择步骤不会随之运行。命令数组以 `shell=False` 执行；其中 `python`、`python3` 使用当前检查器的 Python 解释器，其他可执行程序按当前环境解析。项目自己的环境作业负责准备相应依赖。

执行输出会核对存在性与本次写入痕迹。已有文件原样保留时不会据此认定新运行完成；文件更新仍需要项目自己的数值或内容检查。`role: plan` 成功时报告为 `planned`，保持规划与计算的区别。

## 版本与接续

索引登记当前可用材料。历史输出的生成条件由原始记录说明，新发行的提交号不替代历史计算版本。环境恢复、重跑和新的结果可以逐步补充，原有科学判定保留各自的条件。

0.1 是当前执行契约。将来的不兼容调整通过新的版本与迁移说明发布。原 `schema_version: 1` 起步协议继续保留在[旧项目模板](../../templates/research-project/README.md)中，现有记录可按字段用途迁移到 0.1。

[项目参与规范](SUBMISSION-CONTRACT.md) · [GitHub 自动检查](GITHUB-CHECKS.md)
