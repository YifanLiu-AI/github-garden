# GitHub Garden

这是自动生成的 GitHub 贡献图记录，不代表真实开发工作。历史日期记录保留实际生成时间，提交信息明确标为 synthetic。不用于论文、项目或工作量证明。

目标账号：YifanLiu-AI。专用仓库：YifanLiu-AI/github-garden。目标服务器：777-hk2。

## 行为

- 每天按固定种子生成 1–12 条合成记录，包含周级波动、每日扰动、较低的周末数量和少量小波峰；重复运行不会无限刷提交。
- `--days 365` 补齐从今天向前 365 个自然日的目标数量。它创建带历史日期的合成提交，不会重写已有历史。
- 已有每日基础记录保留，额外色阶记录放入 `entries/日期/`，仅追加，不删除原贡献。
- 时区固定为 Asia/Shanghai / UTC+8。
- 只允许指定专用仓库的 main 分支；工作区有未提交改动就停止。
- 不 force-push、不处理科研仓库、不在源码中保存 token 或私钥。
- 后台定时由 VPS systemd timer 执行；失败可以重试 push。

## 运行方式

仓库已创建。以下命令仅用于首次部署示例，不要对现有仓库重复执行：

```sh
gh repo create YifanLiu-AI/github-garden --public --description 'Explicitly synthetic contribution garden; not genuine development activity' --source . --remote origin --push
```

VPS 需要 Python 3、Git，以及仅对此仓库有写权限的独立 deploy key。不要复制本机 gh token 或个人 SSH 私钥到服务器。

安装源码到 `/opt/github-garden`，克隆专用仓库到 `/var/lib/github-garden/repo`，并确认它有 main 分支。随后：

```sh
python3 /opt/github-garden/garden.py --worktree /var/lib/github-garden/repo --days 365
install -m 644 /opt/github-garden/github-garden.service /etc/systemd/system/github-garden.service
install -m 644 /opt/github-garden/github-garden.timer /etc/systemd/system/github-garden.timer
systemctl daemon-reload
systemctl enable --now github-garden.timer
systemctl list-timers github-garden.timer
```

Git 提交使用账号专属 noreply 地址 `186058058+YifanLiu-AI@users.noreply.github.com`。GitHub 贡献图更新可能有延迟；脚本跑完不等于图已更新。

暂停：`systemctl disable --now github-garden.timer`。

## 2026-10-07 本次状态

源码及 timer 已准备，Python 语法检查通过。主代理在本地临时 clone 中离线检查：补 3 天新增 3 条，重复运行新增 0 条，工作区干净，提交日期与记录一致。365 日日期范围检查为 2025-10-08 至 2026-10-07，无重复日期。独立子代理完整离线验收：365 日新增 365 条，总提交 366（含初始提交）；重复新增 0 条；dirty 和错误 remote 均拒绝；git fsck 正常。修复无效 days 参数的报错格式，不影响提交逻辑。

已部署到 777-hk2：源码 `/opt/github-garden`，工作区 `/var/lib/github-garden/repo`。365 天基础记录已生成并推送，GitHub API 验收 365/365 天均非零。systemd timer 已启用，每天北京时间 20:10 执行；服务 smoke 为 Result=success、ExecMainStatus=0，重复新增 0 条。专用写入 deploy key 只对本仓库有效，GitHub SSH host key 从官方 meta API 固定；不复制个人私钥或 GitHub token。

用户追加要求颜色扰动，现已增加固定种子的数量变化；完整色阶补齐验收待本轮更新。
