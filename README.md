# GitHub Garden

这是自动生成的 GitHub 贡献图记录，不代表真实开发工作。历史日期记录保留实际生成时间，提交信息明确标为 synthetic。不用于论文、项目或工作量证明。

目标账号：YifanLiu-AI。专用仓库：YifanLiu-AI/github-garden。目标服务器：777-hk2。

## 行为

- 默认每天生成一条记录；重复运行不会重复提交同一天。
- `--days 365` 补齐从今天向前 365 个自然日，每日一条。它创建带历史日期的合成提交，不会重写已有历史。
- 时区固定为 Asia/Shanghai / UTC+8。
- 只允许指定专用仓库的 main 分支；工作区有未提交改动就停止。
- 不 force-push、不处理科研仓库、不在源码中保存 token 或私钥。
- 后台定时由 VPS systemd timer 执行；失败可以重试 push。

## 运行方式（仓库及 VPS 尚未部署）

先创建明确说明用途的专用仓库，例如：

```sh
gh repo create YifanLiu-AI/github-garden --public --description 'Explicitly synthetic contribution garden; not genuine development activity'
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
