import docx
import requests
import json
import logging
import os
from neo4j import GraphDatabase

# 确保 log 目录存在
log_dir = "log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 读取 JSON 配置文件
config_path = "/home/kailynwu/文档/可视化知识图谱/config/config.json"
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

# 配置日志
logging.basicConfig(
    level=getattr(logging, config["LOGGING_CONFIG"]["level"]),
    format=config["LOGGING_CONFIG"]["format"],
    handlers=[
        eval(handler["class"])(**{k: v for k, v in handler.items() if k != "class"})
        for handler in config["LOGGING_CONFIG"]["handlers"]
    ]
)
logger = logging.getLogger(__name__)

# 配置豆包 API 信息
DOUBAO_API_URL = config["DOUBAO_API_URL"]
DOUBAO_API_KEY = config["DOUBAO_API_KEY"]

# 配置 Neo4j 数据库连接
uri = config["NEO4J_URI"]
user = config["NEO4J_USER"]
password = config["NEO4J_PASSWORD"]
driver = GraphDatabase.driver(uri, auth=(user, password))

def read_docx(file_path):
    """读取 DOCX 文件内容"""
    logger.info(f"开始读取 DOCX 文件: {file_path}")
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    result = '\n'.join(full_text)
    logger.info(f"完成读取 DOCX 文件: {file_path}")
    return result

def extract_entities_and_relations(text):
    """使用豆包 API 提取实体和关系"""
    logger.info("开始调用豆包 API 提取实体和关系")
    prompt = f"请从以下文本中提取实体和它们之间的关系，以 JSON 格式输出，示例格式：{{'entities': ['实体1', '实体2'], 'relations': [('实体1', '关系类型', '实体2')]}}。文本：{text}"
    headers = {
        "Content-Type": "application/json",
        # 直接使用 API Key
        "Authorization": f"Bearer {DOUBAO_API_KEY}"
    }
    payload = {
        "model": "doubao-seed-1.6-250615",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    logger.debug(f"请求 URL: {DOUBAO_API_URL}")
    logger.debug(f"请求头: {headers}")
    logger.debug(f"请求体: {payload}")
    max_retries = 3  # 最大重试次数
    retries = 0
    while retries < max_retries:
        try:
            response = requests.post(DOUBAO_API_URL, headers=headers, json=payload)
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            response.raise_for_status()
            result = response.json()
            if 'choices' in result and result['choices']:
                message_content = result['choices'][0]['message']['content']
                # 修正格式问题
                message_content = message_content.replace("(", "[").replace(")", "]").replace("'", "\"")
                try:
                    data = json.loads(message_content)
                    entities = data.get('entities', [])
                    relations = data.get('relations', [])
                    logger.info(f"成功提取实体和关系，实体数量: {len(entities)}, 关系数量: {len(relations)}")
                    return entities, relations
                except json.JSONDecodeError as e:
                    logger.error(f"解析 API 返回的内容为 JSON 时出错: {e}, 内容: {message_content}")
                    retries += 1
                    if retries < max_retries:
                        logger.info(f"第 {retries} 次重试调用豆包 API...")
                    else:
                        logger.error("达到最大重试次数，无法获取有效的 JSON 响应。")
            else:
                logger.error(f"API 响应中缺少预期的 'choices' 结构。完整响应: {result}")
                retries += 1
                if retries < max_retries:
                    logger.info(f"第 {retries} 次重试调用豆包 API...")
                else:
                    logger.error("达到最大重试次数，API 响应结构异常。")
        except requests.RequestException as e:
            # 输出详细的错误信息
            error_info = f"调用豆包 API 时发生请求错误: {e}. 响应内容: {response.text if 'response' in locals() else '无响应内容'}"
            logger.error(error_info)
            retries += 1
            if retries < max_retries:
                logger.info(f"第 {retries} 次重试调用豆包 API...")
            else:
                logger.error("达到最大重试次数，请求失败。")
        except KeyError as e:
            logger.error(f"解析 API 响应时发生 KeyError: {e}")
            retries += 1
            if retries < max_retries:
                logger.info(f"第 {retries} 次重试调用豆包 API...")
            else:
                logger.error("达到最大重试次数，解析响应失败。")
    return [], []

def write_to_neo4j(entities, relations):
    """将实体和关系写入 Neo4j 数据库"""
    logger.info("开始将实体和关系写入 Neo4j 数据库")
    with driver.session() as session:
        # 创建实体节点
        for entity in entities:
            session.run("MERGE (n:Entity {name: $name})", name=entity)
        logger.info(f"成功创建 {len(entities)} 个实体节点")
        # 创建关系
        for relation in relations:
            source, rel_type, target = relation
            # 处理关系类型，将非法字符替换为下划线
            clean_rel_type = ''.join(e for e in rel_type if e.isalnum() or e == '_' or e == ':')
            if not clean_rel_type:
                logger.warning(f"关系类型 {rel_type} 清洗后为空，跳过该关系。")
                continue
            session.run(
                "MATCH (a:Entity {name: $source}), (b:Entity {name: $target}) "
                "MERGE (a)-[r:" + clean_rel_type + "]->(b)",
                source=source, target=target
            )
        logger.info(f"成功创建 {len(relations)} 个关系")
    logger.info("完成将实体和关系写入 Neo4j 数据库")

def clear_neo4j_database():
    """清空 Neo4j 数据库中的所有节点和关系"""
    logger.info("开始清空 Neo4j 数据库")
    with driver.session() as session:
        # 禁用约束以加速删除操作
        session.run("MATCH (n) DETACH DELETE n")
    logger.info("完成清空 Neo4j 数据库")

def main():
    # 指定要搜索的目录，这里使用当前目录，可按需修改
    search_dir = '.'
    supported_files = []
    # 遍历目录，找出所有 .docx 和 .doc 文件
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file.lower().endswith(('.docx', '.doc')):
                file_path = os.path.join(root, file)
                supported_files.append(file_path)

    if not supported_files:
        logger.info("未找到支持的 .docx 或 .doc 文件。")
        return

    print("找到以下支持的文件：")
    for i, file_path in enumerate(supported_files, start=1):
        print(f"{i}. {file_path}")

    while True:
        try:
            choice = input("请输入要处理的文件序号（输入 0 退出）：")
            if choice == '0':
                return
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(supported_files):
                selected_file = supported_files[choice_index]
                logger.info(f"程序启动，处理文件: {selected_file}")
                # 读取 DOCX 文件内容
                text = read_docx(selected_file)
                # 提取实体和关系
                entities, relations = extract_entities_and_relations(text)

                # 询问用户是否清空数据库
                clear_choice = input("是否在写入数据前清空 Neo4j 数据库？(y/n): ").strip().lower()
                if clear_choice == 'y':
                    clear_neo4j_database()

                # 写入 Neo4j 数据库
                write_to_neo4j(entities, relations)
                logger.info(f"完成处理文件: {selected_file}")
                break
            else:
                print("输入的序号无效，请重新输入。")
        except ValueError:
            print("输入无效，请输入有效的数字序号。")

if __name__ == "__main__":
    main()
    logger.info("程序结束")