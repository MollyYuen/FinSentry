# FinSentry 第一周起步包

这个起步包只完成 **Skill 1 的离线最小验证**：读取人工核对表转成的样例 CSV，计算同比，运行三条规则，生成 `outputs/screening_result.json`。年报自动解析、Skill 2 检索、DeepSeek、Streamlit 尚未实现；不要把当前输出说成完整系统。

样例数值取自团队提交的《人工计算核验表》，**尚未由本起步包对照原始年报验证**。`source_page` 也是团队表格中的待核页码，`page_verified=false`。正式报告引用页码前，必须打开选定 PDF 核对：PDF 物理页、年报印刷页、表名、单位、合并口径和可比年度。

## 给项目负责人：今晚五步

1. 将本压缩包解压到电脑上，得到一个 `FinSentry` 文件夹；先用 VS Code 的“文件 → 打开文件夹”打开它，跑通下面的离线命令。
2. 在 GitHub 网站建立名为 `FinSentry` 的 **Private** 空仓库。这里**不要勾选**网页上的 Initialize README、.gitignore 或 LICENSE，因为本包已带 README 和 .gitignore。若仓库已创建且有 README，不要再创建第二个，先按下面的“已有仓库”提示处理。
3. 通过 GitHub Desktop 的 `File → Clone repository` 把该空仓库克隆到电脑的**另一个位置**。把解压文件夹**里面的全部内容**复制到克隆所得的 `FinSentry` 文件夹中（不要把整个解压文件夹再套一层）。在 GitHub Desktop 中检查 Changes 列表，再 `Commit to main`、`Push origin`。GitHub 是代码版本备份，不是运行环境，也不是共享数据库。
4. 把 `README.md`、`docs/interface.md`、样例 CSV、预期 JSON 和对应任务书一并发给写代码的队友；让他们把**整套材料**交给 AI 辅助编写自己的模块。AI 不可擅自改变接口。
5. 以后只在你电脑上的**克隆仓库文件夹**继续工作；队友文件先本地验收，通过后复制进去，在 GitHub Desktop `Commit` 再 `Push`。不要把 `.env`、密钥、个人虚拟环境、整份年报或自动生成的索引上传。若已建含 README 的仓库，直接克隆这个仓库，将本包除 README 外的内容复制进去；先比较现有 README，再将本包说明合并进去，不要整份覆盖。

## Windows + Conda：创建独立环境

以下命令在 **Anaconda Prompt** 中通常最稳妥；如果 VS Code 终端已经识别 `conda`，也可直接在 VS Code 终端运行。`finsentry` 是环境名，`FinSentry` 是项目文件夹名；大小写和位置不代表同一个东西。

```powershell
conda create -n finsentry python=3.11 -y
conda activate finsentry
python --version
```

已有同名环境就**不要重复创建**，只需 `conda activate finsentry`。每台需要运行代码的电脑都要各自配置环境；环境不能靠 GitHub 传给对方。不强制全员用 Conda；会用 `venv` 的队友只要 Python 3.11、依赖及命令结果一致也可以。第一版只用 Python 标准库，无额外依赖，所以 `requirements.txt` 暂时没有可安装项。

在 VS Code 中按 `Ctrl+Shift+P` → `Python: Select Interpreter` → 选 `finsentry` 对应的 Python 3.11。若没有显示，重启 VS Code 或选“输入解释器路径”。

## 在项目根目录运行

```powershell
python --version
python run_demo.py --offline
python -m unittest discover -s tests -v
```

预期：屏幕显示 `R1 REVIEW`、`R2 PASS`、`R3 PASS`；生成 `outputs/screening_result.json`；测试显示 `OK`。如 Python 版本不是 3.11，请确认已激活/选择项目环境。

`python run_demo.py --offline` **不是**完整的 DeepSeek 离线仿真；它只验证财务数据和规则。`outputs/screening_result.json` 是运行生成物，`data/sample/expected_screening_result.json` 是团队事先确定的验收答案，两者应完全一致（程序也会自动检查）。

## 成员交付和验收

Python 成员负责将数据读取/规则计算扩展为可读年报的模块；证据检索成员负责返回原文、页码、证据等级。金融和会计成员审定取数、规则及证据。项目负责人维护 `docs/interface.md` 和运行入口。每人提交 **源代码、用到的依赖、运行说明、样例测试结果和已知限制**；不只发截图或 AI 生成的代码片段。

目前可先交压缩包给项目负责人，不要求所有人会 GitHub。接口变更须先在群里确认，由项目负责人更新 `docs/interface.md` 版本，再通知两位代码成员同步；不要悄悄改字段名。

完整验收的顺序：原始数字与来源 → 规则结果与人工表 → 文本证据与页码 → 大模型解释。若数据或页码未核对，报告只能标为待复核。
