# 🦞 OpenClaw Ubuntu 安装完全指南：在 RK3588 开发板上部署你的私人 AI 助手

> **摘要：** 本文详细记录了在 OrangePi AIpro 20T（RK3588）开发板上安装和配置 OpenClaw 的完整过程，涵盖环境准备、Node.js 安装、OpenClaw 部署、常见问题排查等全流程。适合嵌入式开发者、AI 爱好者和机器人开发者参考。

---

## 一、OpenClaw 是什么？

[OpenClaw](https://github.com/openclaw/openclaw) 是一个**开源的个人 AI 助手平台**，你可以在自己的设备上运行它。它的吉祥物是一只太空龙虾 🦞 Molty。

**核心特性：**

| 特性 | 说明 |
|------|------|
| 🏠 本地优先 | Gateway 运行在你自己的设备上，数据不出局域网 |
| 💬 多渠道接入 | 支持微信、QQ、Telegram、Discord、飞书、WhatsApp 等 20+ 渠道 |
| 🤖 多模型支持 | OpenAI、Anthropic、DeepSeek、Google、xAI 等主流 LLM |
| 🛠️ 可扩展 | 通过 Skills 机制自定义工具和能力 |
| 🔒 安全可控 | 支持 DM 配对、沙箱隔离、权限控制 |
| 📱 多端协同 | macOS、Windows、iOS、Android 都有客户端 |

**简单说：** OpenClaw 就是一个你可以自己部署的"ChatGPT"，而且它能通过微信、QQ 等渠道跟别人对话，还能通过自定义 Skill 控制硬件设备（比如机械臂、智能家居）。

> 🔗 项目地址：https://github.com/openclaw/openclaw
> 📖 官方文档：https://docs.openclaw.ai

---

## 二、为什么要在 RK3588 上跑？

RK3588 是瑞芯微推出的旗舰级 SoC，8 核 ARM（4×A76 + 4×A55），集成 6 TOPS NPU。常见的开发板有：

- OrangePi AIpro 20T
- Radxa Rock 5B
- Firefly Station M3
- Khadas Edge2

**RK3588 跑 OpenClaw 的优势：**

- ✅ 算力充足：8 核 ARM 跑 Node.js 服务绰绰有余
- ✅ 内存充裕：通常 8/16/23GB，完全够用
- ✅ 功耗低：整板功耗 5-15W，7×24 小时运行无压力
- ✅ 接口丰富：USB、GPIO、UART、SPI、I2C，方便对接硬件
- ✅ NPU 加速：6 TOPS 可跑视觉模型，为 AI 助手增加"眼睛"

**典型应用场景：**

- 🤖 机器人语音/文字交互控制
- 🏠 智能家居中控
- 📊 边缘 AI 数据处理
- 🎓 教学实训平台

---

## 三、环境准备

### 3.1 硬件要求

| 项目 | 最低要求 | 推荐配置 |
|------|----------|----------|
| **芯片** | RK3588 / RK3588S | RK3588 |
| **内存** | 4GB | 8GB+ |
| **存储** | 16GB 可用 | 32GB+ |
| **网络** | WiFi 或以太网 | 有线网络更稳定 |
| **电源** | 5V/3A | 原装电源适配器 |

### 3.2 软件要求

| 项目 | 要求 | 说明 |
|------|------|------|
| **操作系统** | Ubuntu 20.04 / 22.04 / Debian 11+ | aarch64 架构 |
| **Node.js** | 22.19+（必须） | OpenClaw 硬性要求 |
| **npm** | 随 Node.js 一起安装 | 或 pnpm / bun |
| **网络** | 能访问 npm 仓库 | 建议配置国内镜像 |

### 3.3 确认你的环境

在终端执行以下命令，确认硬件和系统信息：

```bash
# 查看系统架构（应该是 aarch64）
uname -m

# 查看系统版本
cat /etc/os-release

# 查看内存大小
free -h

# 查看磁盘空间
df -h /

# 查看当前 Node.js 版本（可能未安装）
node -v
```

**参考输出：**

```
$ uname -m
aarch64

$ free -h
               total        used        free      shared  buff/cache   available
Mem:            23Gi       2.6Gi        18Gi        32Mi       2.2Gi        20Gi

$ df -h /
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        59G   33G   23G  60% /
```

> 💡 **Tips：** 内存建议 4GB 以上，磁盘至少 10GB 可用空间。

---

## 四、安装步骤（手把手）

### 4.1 安装 nvm（Node 版本管理器）

OpenClaw 要求 Node.js 22.19+，而 Ubuntu apt 仓库中的 Node.js 版本通常较旧，我们使用 nvm 来管理 Node.js 版本。

```bash
# 安装 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# 让 nvm 生效
source ~/.bashrc
```

安装成功后会看到类似输出：

```
=> Appending nvm source string to /home/username/.bashrc
=> Appending bash_completion source string to /home/username/.bashrc
=> Close and reopen your terminal to start using nvm or run the following to use it now:

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
```

> ⚠️ **注意：** 如果 `curl` 访问 GitHub 超时，请确保网络通畅，或使用代理。

### 4.2 安装 Node.js 22

```bash
# 使用 nvm 安装 Node.js 22（会自动下载 aarch64 版本）
nvm install 22

# 验证安装
node -v    # 应输出 v22.x.x
npm -v     # 应输出 10.x.x
```

**参考输出：**

```
$ nvm install 22
Downloading and installing node v22.22.3...
Downloading https://nodejs.org/dist/v22.22.3/node-v22.22.3-linux-arm64.tar.xz...
######################################################################################## 100.0%
Computing checksum with sha256sum
Checksums matched!
Now using node v22.22.3 (npm v10.9.8)
Creating default alias: default -> 22 (-> v22.22.3)

$ node -v
v22.22.3
```

> 💡 **Tips：** nvm 会自动识别架构并下载对应的 ARM64 版本，无需手动选择。

### 4.3 配置 npm 国内镜像（重要！）

国内网络直接访问 npm 官方仓库速度较慢，建议切换到淘宝镜像：

```bash
npm config set registry https://registry.npmmirror.com

# 确认配置
npm config get registry
# 应输出: https://registry.npmmirror.com
```

> 🔥 **这一步很重要！** 不配置镜像的话，后面的 `npm install` 可能会卡很久甚至超时失败。

### 4.4 安装 OpenClaw

```bash
# 全局安装 OpenClaw
npm install -g openclaw@latest
```

**参考输出：**

```
added 285 packages in 31s
66 packages are looking for funding
  run `npm fund` for details
```

验证安装：

```bash
openclaw --version
# 应输出版本号，如: 2026.6.1
```

### 4.5 初始化配置（Onboarding）

OpenClaw 提供了一个交互式的初始化向导，引导你完成基本配置：

```bash
openclaw onboard
```

向导会依次询问你以下配置，按需选择即可：

#### ① 安全确认

```
I understand this is personal-by-default and shared/multi-user use requires
lock-down. Continue?
→ 选择 Yes
```

这是安全提示，意思是 OpenClaw 默认是个人使用模式。确认即可。

#### ② 选择 AI 模型

```
Model/auth provider
→ OpenAI / Anthropic / xAI / Google / More… / Skip for now
```

- 如果你有 **OpenAI API Key**，选 OpenAI
- 如果你想用 **DeepSeek**，选 More… 查看列表，或先 Skip 后手动配置
- 如果暂时没有 API Key，选 **Skip for now**，后面再配

> 💡 **Tips：** DeepSeek 的 API 兼容 OpenAI 格式，后续可以手动配置。

#### ③ 选择交互渠道

```
Select channel (QuickStart)
→ Telegram / Weixin / WeCom / Skip for now
```

- **推荐先选 Skip for now**，用命令行测试基本功能
- 后续需要微信/QQ 交互时再单独配置

#### ④ 选择搜索引擎

```
Search provider
→ DuckDuckGo / Brave / Exa / Skip
```

推荐选 **DuckDuckGo**，免费且不需要 API Key。

#### ⑤ 安装技能依赖

```
Install missing skill dependencies
→ 可选 clawhub（技能市场），其他按需
```

#### ⑥ 启用 Hooks

```
Enable hooks
→ 推荐选 session-memory（会话记忆）
```

#### ⑦ 启动方式

```
How do you want to hatch your agent?
→ Hatch in Terminal (recommended)
```

推荐选 **Hatch in Terminal**，方便查看日志和调试。

### 4.6 启动 OpenClaw

如果 onboard 最后没有自动启动，手动启动：

```bash
# 前台启动（调试模式，可看日志）
openclaw gateway --port 18789 --verbose

# 或者后台守护进程模式
openclaw gateway start
openclaw gateway status
```

**启动成功标志：**

```
🦞 OpenClaw 2026.6.1
   The only open-source project where the mascot could eat the competition.

openclaw tui - local embedded - agent main - session main
```

### 4.7 测试对话

启动后，在终端直接输入文字跟龙虾对话：

```
你好，你是谁？
```

龙虾会回复你，说明安装成功！🎉

---

## 五、常见问题排查

### 5.1 nvm 安装后提示 `command not found: nvm`

**原因：** `.bashrc` 没有生效

**解决：**

```bash
source ~/.bashrc
# 或者重新打开终端
```

### 5.2 npm install 很慢或超时

**原因：** 国内网络访问 npm 官方仓库慢

**解决：**

```bash
npm config set registry https://registry.npmmirror.com
```

### 5.3 内存不足（OOM Killed）

**症状：** 安装过程中进程被杀

**解决：** 添加 swap 分区

```bash
# 创建 4GB swap 文件
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久生效
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 验证
free -h
```

### 5.4 sharp 模块安装失败

**症状：** `npm install` 时报 sharp 相关错误

**解决：**

```bash
npm install -g openclaw@latest --ignore-scripts
cd $(npm root -g)/openclaw
npm rebuild sharp
```

### 5.5 端口被占用或无法访问

**症状：** 启动成功但浏览器打不开

**解决：**

```bash
# 检查端口是否被占用
lsof -i :18789

# 检查防火墙
sudo ufw allow 18789
# 或
sudo iptables -A INPUT -p tcp --dport 18789 -j ACCEPT
```

### 5.6 OpenClaw 版本过旧

```bash
# 更新到最新版
npm update -g openclaw@latest

# 或者指定版本
npm install -g openclaw@2026.6.1
```

### 5.7 Node.js 版本不对

**症状：** 提示需要 Node 22.19+

**解决：**

```bash
# 查看当前版本
node -v

# 切换到 Node 22
nvm use 22

# 如果没装过
nvm install 22
```

---

## 六、进阶配置

### 6.1 配置 DeepSeek 模型

如果你选择使用 DeepSeek 作为 AI 模型，编辑配置文件：

```bash
# 编辑配置文件
nano ~/.openclaw/openclaw.json
```

添加或修改以下内容：

```json
{
  "agent": {
    "model": "deepseek/deepseek-chat"
  },
  "providers": {
    "deepseek": {
      "apiKey": "sk-your-deepseek-api-key"
    }
  }
}
```

> 💡 DeepSeek API 申请地址：https://platform.deepseek.com

### 6.2 配置微信渠道

编辑 `~/.openclaw/openclaw.json`，添加微信配置：

```json
{
  "channels": {
    "weixin": {
      "enabled": true
    }
  }
}
```

重启 Gateway 生效：

```bash
openclaw gateway restart
```

### 6.3 设置开机自启

```bash
# 安装为 systemd 服务
openclaw onboard --install-daemon

# 或手动启用
systemctl --user enable openclaw-gateway
systemctl --user start openclaw-gateway
```

### 6.4 查看日志

```bash
# 实时查看日志
journalctl --user -u openclaw-gateway -f

# 或者前台启动看日志
openclaw gateway stop
openclaw gateway --port 18789 --verbose
```

---

## 七、项目结构说明

安装完成后，OpenClaw 的相关文件分布在以下位置：

```
~/.openclaw/
├── openclaw.json          # 主配置文件
├── workspace/             # 工作空间
│   ├── AGENTS.md          # Agent 提示词
│   ├── SOUL.md            # 人格设定
│   ├── TOOLS.md           # 工具说明
│   └── skills/            # 自定义技能目录
│       └── <skill-name>/
│           └── SKILL.md   # 技能定义文件
└── data/                  # 数据存储
```

---

## 八、常用命令速查

```bash
# 启动/停止/重启
openclaw gateway start
openclaw gateway stop
openclaw gateway restart
openclaw gateway status

# 前台调试模式
openclaw gateway --port 18789 --verbose

# 查看版本
openclaw --version

# 更新 OpenClaw
npm update -g openclaw@latest

# 诊断工具
openclaw doctor

# 发送测试消息
openclaw message send --target <target> --message "Hello"

# 交互式对话
openclaw agent --message "你好" --thinking high
```

---

## 九、总结

在 RK3588 开发板上安装 OpenClaw 的核心流程就四步：

```
1. 装 nvm          → curl + source
2. 装 Node.js 22   → nvm install 22
3. 装 OpenClaw     → npm install -g openclaw@latest
4. 初始化配置       → openclaw onboard
```

整个过程大约 10-30 分钟（取决于网络速度）。安装完成后，你就拥有了一个跑在自己设备上的私人 AI 助手，可以通过微信、QQ、Telegram 等渠道跟它对话，还能通过 Skills 机制扩展它的能力。

**下一步可以做什么：**

- 🛠️ 开发自定义 Skill，让龙虾控制你的硬件设备
- 🔌 接入微信/QQ 渠道，实现多渠道 AI 助手
- 👁️ 集成视觉模型，实现"看图说话"
- 🤖 对接机器人/机械臂，实现自然语言控制

---

> **作者说：** 本文是我在 OrangePi AIpro 20T（RK3588）上部署 OpenClaw 的真实记录，所有命令和输出都经过实际验证。如果你在安装过程中遇到问题，欢迎在评论区留言交流！🦞

---

**参考链接：**

- [OpenClaw GitHub 仓库](https://github.com/openclaw/openclaw)
- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [nvm 安装指南](https://github.com/nvm-sh/nvm)
- [Node.js 官网](https://nodejs.org)
- [DeepSeek 开放平台](https://platform.deepseek.com)
