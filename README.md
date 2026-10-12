
# Excel Insight

基于 Python、Flask 和 Pandas 开发的 Excel 销售数据分析 Web 应用。

## 功能介绍

- 上传 XLSX 格式的销售数据
- 自动检查必需字段、空值及数值类型
- 计算总销售额和平均每单销售额
- 展示 Excel 前5行数据
- 记录数据校验错误日志
- 使用 pytest 进行自动化测试

## 技术栈

- Python
- Flask
- Pandas
- OpenPyXL
- pytest
- Git

## 安装依赖

```powershell
python -m pip install flask pandas openpyxl pytest
```

## 启动项目

```powershell
python app.py
```

浏览器访问：

http://127.0.0.1:5001

## 运行测试

```powershell
python -m pytest -v
```

当前已有9个自动化测试。

## 项目说明

这是一个本地学习和开发原型，尚未完成生产部署所需的全部安全加固。
