# Skills.sh 支持说明

## 安装方式

### 方式 1: 通过 skills.sh 生态（通用 Agent）

```bash
npx skills add lancelin111/crawl4ai-skill@crawl4ai-skill
```

### 方式 2: 通过 ClawHub（OpenClaw 专用）

```bash
clawhub install crawl4ai-skill
```

### 方式 3: 通过 PyPI（Python 包）

```bash
pip install crawl4ai-skill
```

---

## 目录结构

```
crawl4ai-skill/
├── SKILL.md                     # 根目录（ClawHub 使用）
├── skills/                      # skills.sh 生态
│   └── crawl4ai-skill/
│       └── SKILL.md            # 技能定义文件
├── package.json                # npm 包配置
├── pyproject.toml              # Python 包配置
└── src/                        # Python 源码
```

---

## 生态对比

| 生态 | 安装命令 | 技能格式 | 用户群 |
|------|----------|----------|--------|
| **ClawHub** | `clawhub install` | SKILL.md（根目录） | OpenClaw |
| **skills.sh** | `npx skills add` | skills/*/SKILL.md | Claude/Copilot/通用 |
| **PyPI** | `pip install` | Python 包 | Python 开发者 |

---

## 验证

### 验证 GitHub 结构

```bash
curl -s https://raw.githubusercontent.com/lancelin111/crawl4ai-skill/main/skills/crawl4ai-skill/SKILL.md | head -10
```

### 验证 package.json

```bash
curl -s https://raw.githubusercontent.com/lancelin111/crawl4ai-skill/main/package.json | jq .
```

---

## 推广策略

### ClawHub（已完成 ✅）
- 发布版本：v1.0.9
- 安全评级：Benign
- 当前安装：0

### skills.sh（新增 ✅）
- GitHub 仓库：公开
- 技能路径：skills/crawl4ai-skill/SKILL.md
- 安装命令：`npx skills add lancelin111/crawl4ai-skill@crawl4ai-skill`

### 下一步
- [ ] 在 Vercel 论坛/Discord 发布
- [ ] 在 skills.sh 社区推广
- [ ] 添加到 awesome-agent-skills 列表
