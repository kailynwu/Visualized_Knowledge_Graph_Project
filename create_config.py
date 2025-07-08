import os
import json

def get_user_input():
    print("欢迎使用配置文件创建向导，请按照提示输入配置信息：")

    # 日志配置
    print("\n=== 日志配置 ===")
    log_level = input("请输入日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL，默认 INFO）: ") or "INFO"
    log_format = input("请输入日志格式（默认 %(asctime)s - %(name)s - %(levelname)s - %(message)s）: ") or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_to_file = input("是否将日志写入文件（y/n，默认 y）: ").lower() == "y"
    if log_to_file:
        # 确保 log 目录存在
        log_dir = "log"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_filename = os.path.join(log_dir, input("请输入日志文件名（默认 graph.log）: ") or "graph.log")
    log_to_console = input("是否将日志输出到控制台（y/n，默认 y）: ").lower() == "y"

    # 生成日志处理器配置
    handlers = []
    if log_to_file:
        handlers.append({
            "class": "logging.FileHandler",
            "filename": log_filename
        })
    if log_to_console:
        handlers.append({
            "class": "logging.StreamHandler"
        })

    logging_config = {
        "level": log_level,
        "format": log_format,
        "handlers": handlers
    }

    # 豆包 API 配置
    print("\n=== 豆包 API 配置 ===")
    doubao_api_url = input("请输入豆包 API 请求地址（默认 https://ark.cn-beijing.volces.com/api/v3/chat/completions）: ") or "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    doubao_api_key = input("请输入豆包 API 密钥: ")

    # Neo4j 数据库配置
    print("\n=== Neo4j 数据库配置 ===")
    neo4j_uri = input("请输入 Neo4j 数据库连接地址（默认 bolt://localhost:7687）: ") or "bolt://localhost:7687"
    neo4j_user = input("请输入 Neo4j 数据库用户名（默认 neo4j）: ") or "neo4j"
    neo4j_password = input("请输入 Neo4j 数据库用户密码: ")

    return {
        "LOGGING_CONFIG": logging_config,
        "DOUBAO_API_URL": doubao_api_url,
        "DOUBAO_API_KEY": doubao_api_key,
        "NEO4J_URI": neo4j_uri,
        "NEO4J_USER": neo4j_user,
        "NEO4J_PASSWORD": neo4j_password
    }

def create_config_file():
    # 获取用户输入
    config_data = get_user_input()

    # 配置目录路径
    config_dir = "/home/kailynwu/文档/可视化知识图谱/config"
    # 配置文件路径
    config_file_path = os.path.join(config_dir, "config.json")

    # 若配置目录不存在则创建
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        print(f"已创建配置目录: {config_dir}")

    # 写入 JSON 配置文件
    with open(config_file_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)
    print(f"已创建配置文件: {config_file_path}")

if __name__ == "__main__":
    create_config_file()
