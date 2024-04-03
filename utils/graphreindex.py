import pandas as pd


# 读取原始CSV文件，获取所有节点的列表
def get_nodes_from_csv(csv_file, sep=','):
    df = pd.read_csv(csv_file, sep=sep)
    all_nodes = set(df['from']).union(df['to'])  # 获取所有节点
    return list(all_nodes)


# 创建节点映射字典，将原始节点ID映射到新的节点ID
def create_node_mapping(all_nodes):
    node_mapping = {old_id: new_id for new_id, old_id in enumerate(all_nodes)}
    return node_mapping


# 将原始CSV文件中的节点ID替换为新的节点ID，并生成新的CSV文件
def renumber_nodes_in_csv(input_csv_file, output_csv_file, node_mapping, sep=','):
    df = pd.read_csv(input_csv_file, sep=sep)
    df['from'] = df['from'].map(node_mapping)
    df['to'] = df['to'].map(node_mapping)
    df.to_csv(output_csv_file, index=False)


def reindex_graph(input_csv_file, output_csv_file, sep=','):
    nodes = get_nodes_from_csv(input_csv_file, sep=sep)
    node_mapping = create_node_mapping(nodes)
    renumber_nodes_in_csv(input_csv_file, output_csv_file, node_mapping, sep=sep)
