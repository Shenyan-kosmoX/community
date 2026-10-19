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

先由维护者确认实际可用额度、审批责任与私下交付渠道；更新 `docs/RESOURCES.md`，并移除 `<!-- resource-status:fundraising -->` 筹备标记。将 `applications_open` 改为 true 后重建，才会把表单放入生效目录。当前正在寻求资金支持。

## 标签与分支规则

已创建标签：`kind:reproduction`、`kind:development`、`kind:exploration`、`area:community`、`support:api`、`review:needed`。工作状态使用 Issue/PR 原生状态和分配人。

两个公开仓库已配置 PR 与必要检查，管理员保留绕过权限；当前强制批准数为 0。日常审核由内部成员在 PR 记录意见，平台审批规则随实际成员安排调整。CODEOWNERS 指向具有写权限的维护者。科学审核记录检查人、范围和判断，另见 [审核过程](REVIEW.md)。

## 修改配置

`community.json` 中的维护者配置会生成首页提案联系人、CODEOWNERS 和公共仓库联络。初期联系人为 @wenkuizhao261-pixel；更换时同时更新 GOVERNANCE、项目提案说明和 Discussion 表单，并核对实际权限。开发记录写在项目仓库，公共目录只链接已经发布的文章。

`community` 原创内容使用 MIT。图像按各自来源处理；科研项目分别确定代码、数据和参考材料的许可。

发布后逐项核对主页、讨论表单、PR 工作流、分支规则和头像的实际状态，保留部署记录。正式项目上传规范待两个参考项目提供后再完善。
