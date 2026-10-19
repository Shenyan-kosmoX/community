# 本地维护与发布

## 两个目标

组织 `.github` 保存主页、理念和视觉素材；本仓库保存公共协作。`community.json` 为身份与入口配置，`content/` 为两份首页源文件。

开发环境：Python 3.12。检查器依赖见 `requirements-dev.txt`。

```powershell
python -m pip install -r requirements-dev.txt
python tools/build.py --profile ../Shenyan-kosmoX-profile
python tools/check.py --profile ../Shenyan-kosmoX-profile
python -m unittest discover -s tests -v
```

`--profile` 指向本地 `.github` 仓库目录，目录名称可不同。两份首页由构建生成，不要只修改生成文件。原创文档中少量跨仓库引用由迁移脚本处理。

## Discussions

首版已启用，复用核验过的三个原生类别：General → 研究问题与想法，Q&A → 方法与复现交流，Ideas → 项目提案。名称与 slug 见配置。其他 GitHub 默认类别存在但不作为主要入口。表单位于 `.github/DISCUSSION_TEMPLATE/<slug>.yml`；若今后改类别名，需要实际核对 slug，而不是仅修改配置。

确认可正常发帖后，更新 `docs/DISCUSSIONS.md` 的状态和实际入口，再将 `discussions_enabled` 改为 true 并重建。类别属于平台设置，复制 YAML 不会自动创建类别。

## API 支持

先由维护者确认实际可用额度、审批责任与私下交付渠道；更新 `docs/RESOURCES.md`。将 `applications_open` 改为 true 后重建，才会把表单放入生效目录。当前只准备流程，不授予额度。

## 标签与分支规则

拟采用少量标签：`kind:reproduction`、`kind:development`、`kind:exploration`、`area:community`、`support:api`、`review:needed`，状态使用 Issue/PR 原生状态和分配人。只在需要的仓库创建，不预建任务市场。

公开仓库首次发布后运行一次 CI，再配置要求 PR 与相应检查。初期只有一位已确认维护者，平台不强制第二人的批准，不假装存在独立审核团队；维护者需在 PR 留下实际判断。待有另一位确认的审核者后再启用强制批准。默认不自动合并。CODEOWNERS 指向实际有写权限的维护者；它不表示独立科学审核完成。

## 修改配置

原始 `community` LICENSE 为 MIT，保持不变。图像有独立来源。科研项目公开前另做范围与许可检查，不能继承本仓库的科学认证或许可证。

本地验证通过不证明远程功能启用。发布需要单独授权，并逐项核对主页、讨论表单、PR 工作流、分支规则和头像。
