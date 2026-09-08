# 🏆 高富帅 · 期货策略扫描

每天自动扫描期货主力连续合约，找出同时满足「高」「富」「帅」三个条件的品种。

---

## 📌 策略规则

| 条件 | 名称 | 规则 |
|------|------|------|
| **高** | 增仓 | 今日持仓量比昨日增加 **≥ 20%** |
| **富** | 放量 | 今日成交量 **> 5日平均成交量** 且 **> 20日平均成交量** |
| **帅** | 方向 | 今日价格有涨跌（涨跌幅绝对值 **> 0.1%**） |

> 三个条件需**同时满足**，才算「高富帅」品种。

---

## 📊 数据来源

- **新浪财经期货主力连续合约**
- 使用 [akshare](https://www.akshare.xyz/) 库获取数据
- 扫描 54 个品种（上期所、大商所、郑商所、中金所、广期所）

---

## 🚀 快速开始

### 本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/<你的用户名>/gao-fu-shuai.git
cd gao-fu-shuai

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行扫描
python scan.py

# 4. 打开网页
# 直接用浏览器打开 index.html 即可（需要 data.json 数据文件）
```

### GitHub Pages 自动部署

1. Fork 本仓库到你的 GitHub 账号
2. 进入仓库 **Settings → Pages**
3. Source 选择 **GitHub Actions**
4. 进入 **Actions** 页面，启用 Workflows
5. 每天 15:35（北京时间）自动执行扫描并部署

> 首次部署后，访问 `https://<你的用户名>.github.io/gao-fu-shuai/` 即可查看。

---

## 📁 项目结构

```
.
├── .github/workflows/deploy.yml   # GitHub Actions 自动部署配置
├── index.html                     # 网页入口
├── style.css                      # 样式文件（深色主题）
├── app.js                         # 前端渲染逻辑
├── scan.py                        # Python 数据扫描脚本
├── requirements.txt               # Python 依赖
└── data.json                      # 生成的数据文件（自动创建）
```

---

## 🕐 定时更新

- 每天 **北京时间 15:35** 自动执行
- 自动拉取数据 → 运行策略 → 生成 data.json → 部署到 GitHub Pages
- 周末及节假日不执行（仅工作日运行）

---

## 🛠 技术栈

- **Python** + akshare（数据获取和策略计算）
- **HTML/CSS/JS** 静态页面（深色主题、卡片式布局）
- **GitHub Actions**（定时执行和自动部署）
- **GitHub Pages**（免费静态站点托管）

---

## 📜 License

MIT
