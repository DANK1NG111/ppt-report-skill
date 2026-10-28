# 给 Agent 的安装协议

当用户把本仓库链接作为安装使用请求发给你时，完成以下流程并继续处理用户的 PPT 任务。需要本地文件读写、命令执行和联网下载依赖能力；普通网页聊天没有这些能力时，说明缺少的能力，不声称已安装。

本仓库地址为 https://github.com/DANK1NG111/ppt-report-skill 。

## 从仓库 URL 到可用 Skill

1. 使用用户给出的仓库 URL 克隆到稳定的用户目录，例如 `~/.local/share/ppt-report-skill`。不要把临时下载目录当长期安装位置。若已存在，先核对 remote；同一仓库直接复用，不覆盖无关目录或本地改动，不自动 git pull。
2. 阅读仓库 `SKILL.md` 和本协议。使用目标 Agent 的原生技能安装能力（如果有）；普通本地 Agent 则使用下面的安装器。不要把依赖装入系统 Python。
3. macOS/Linux 运行 `sh setup.sh --install-system --agent codex`；Claude Code 改成 `--agent claude`；其他 Agent 使用 `--agent generic` 或明确指定 `--skills-dir`。Windows 运行 `powershell -File setup.ps1 --install-system --agent codex`。路径有空格时保持参数引用。
4. 安装器创建独立 `.venv`，安装 Python 依赖，寻找或安装 LibreOffice，真实生成5页中文 PPTX、渲染 PDF/PNG并验证数字，然后注册 Skill。缺少 Python 时入口脚本使用官方 uv 准备 Python 3.12。Linux 自动安装也包含 CJK 字体。macOS 需要已存在 Homebrew 才能自动补 LibreOffice；Windows 对应 winget；无法执行系统安装或权限不足时保留 BLOCKED 回执，Agent 根据实际原因修复后重试。
5. 只有 `.runtime/setup_receipt.json` 的状态为 READY，且 doctor 回执实际生成与渲染通过、技能入口存在，才告诉用户配置完成。注册不覆盖已有无关 Skill。当前会话无法动态发现新 Skill 时，直接读取已注册路径的 SKILL.md继续使用；后续会话按宿主的技能发现机制加载。
6. 用户提供模板时使用其原文件副本；没有模板时使用本项目自制的简洁模板。运行完整生成流程，交付前仍做逐页视觉复核及 PowerPoint 原生打开检查。环境 READY 只表示制作和渲染链路可用。

如果只有仓库 URL 且用户尚未给材料，配置完成后说明已就绪，并请用户提供汇报材料和可选模板。不要为演示虚构用户成果。

## 重试、更新与诊断

重复运行安装器可复用环境；依赖配置变化时自动重新安装，`--refresh` 可强制重新检查依赖。`--agent none` 仅配置环境；`--skills-dir /path/skills` 可用于指定宿主目录。`--venv` 和 `--python` 支持已经可用的解释器。直接调用 `python scripts/setup.py` 需要 Python 3.11+，较旧系统优先使用入口脚本。

```sh
.venv/bin/ppt-report doctor --smoke
.venv/bin/ppt-report create --materials /path/report.md --request /path/request.json --output /path/output/report.pptx
.venv/bin/ppt-report rehearse --receipt /path/output/pipeline_receipt.json
```

Windows 将 `.venv/bin/` 改为 `.venv/Scripts/`。运行安装器不修改 shell profile，不更换用户已有节点、凭据或 Agent 配置。技术日志和状态保存在 `.runtime/`。系统安装需要提权、网络被阻止或渲染引擎安装不可用时，按具体错误处理；不能把只安装 Python 包当作全部就绪。

Codex 用户级入口使用 `~/.agents/skills/ppt-report-skill`，Claude Code 使用 `~/.claude/skills/ppt-report-skill`。支持符号链接时连接到稳定仓库；不支持时写入指向完整仓库的 Skill 入口。入口记录真正的运行目录和虚拟环境，避免从另一个工作目录误用系统 Python。
