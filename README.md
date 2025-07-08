# 可视化知识图谱
## 项目概述
本项目旨在从 DOCX 文件中提取实体和关系，并将这些信息存储到 Neo4j 图数据库中，以便进行知识图谱的可视化和分析。项目通过调用豆包 API 来完成实体和关系的提取，同时提供了日志记录和配置文件管理功能。
# 项目结构
```plaintext
可视化知识图谱/
├── config/
│   └── config.json  # 配置文件
├── log/
│   └── graph.log    # 日志文件
├── create_config.py # 配置文件创建脚本
├── graph.py         # 主程序脚本
└── README.md        # 项目文档
```
## 配置文件说明
配置文件 config/config.json 包含了项目的重要配置信息，以下是各配置项的说明：

```plaintext
{
    "LOGGING_CONFIG": {
        "level": "DEBUG",  # 日志级别，可选值：DEBUG/INFO/WARNING/ERROR/CRITICAL
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 日志格式
        "handlers": [
            {
                "class": "logging.FileHandler",  # 日志处理器：写入文件
                "filename": "log/graph.log"  # 日志文件名
            },
            {
                "class": "logging.StreamHandler"  # 日志处理器：输出到控制台
            }
        ]
    },
    "DOUBAO_API_URL": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",  # 豆包 API 请求地址
    "DOUBAO_API_KEY": "ca8407be-0151-48f1-bdc5-e9982c3a1bf7",  # 豆包 API 密钥
    "NEO4J_URI": "bolt://localhost:7687",  # Neo4j 数据库连接地址
    "NEO4J_USER": "neo4j",  # Neo4j 数据库用户名
    "NEO4J_PASSWORD": "ribbon-toronto-visitor-unique-spend-7125"  # Neo4j 数据库用户密码
}
```
## 运行环境
Python 3.x
依赖库：docx, requests, neo4j, logging
可以使用以下命令安装依赖库：

```bash
pip install python-docx requests neo4j
```
## 配置文件创建
运行 create_config.py 脚本，按照提示输入配置信息，即可创建配置文件：

```bash
python create_config.py
```
## 主程序运行
运行 graph.py 脚本，程序会自动搜索当前目录下的 .docx 和 .doc 文件，并让用户选择要处理的文件：

```bash
python graph.py
```
## 功能模块说明
### 日志记录
项目使用 Python 的 logging 模块进行日志记录，日志级别和格式可以在配置文件中进行配置。日志信息会同时输出到文件 log/graph.log 和控制台。
### 实体和关系提取
使用豆包 API 从 DOCX 文件中提取实体和关系。程序会将提取的信息以 JSON 格式返回，并进行格式修正和错误处理。
### Neo4j 数据库操作
程序提供了将实体和关系写入 Neo4j 数据库的功能，同时支持清空数据库的操作。在写入数据前，用户可以选择是否清空数据库。
### 错误处理
当调用豆包 API 失败时，程序会进行重试，最多重试 3 次。
当解析 API 返回的内容为 JSON 时出错，程序会输出错误信息并进行重试。
当输入的文件序号无效时，程序会提示用户重新输入。
## 注意事项
请确保 Neo4j 数据库已启动，并且配置文件中的数据库连接信息正确。
请确保豆包 API 密钥有效，否则会导致 API 调用失败。
处理大文件时，可能会导致 API 调用时间过长或占用较多内存，请根据实际情况进行调整。