import os
import shutil
#借鉴了网上SOF的论坛的方法，因而使用了shutil提高效率

def organize_csv_files(source_folder, target_folder, keywords):
    """
    遍历 source_folder 下所有子目录，找到名字包含关键词的 CSV 文件，
    并将它们复制到 target_folder 下对应关键词命名的文件夹中。
    可以直接输入target_folder以创建它
    

    参数:
        source_folder (str): 源文件夹路径(这是你要搜索的文件夹)。
        target_folder (str): 目标文件夹路径(这是你要放置文件到的文件夹)。
        keywords (list): 关键词列表(搜索有这些关键词的csv)。
    """
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    for keyword in keywords:
        # 在目标文件夹下创建对应关键词的子文件夹
        keyword_folder = os.path.join(target_folder, f"{keyword}")
        os.makedirs(keyword_folder, exist_ok=True)

    # 遍历源文件夹下的所有文件和子文件夹(详见csvWalk.py)
    for root, _, files in os.walk(source_folder):
        # 统计当前文件夹中以 .csv 结尾的文件数量
        csv_files = [file for file in files if file.endswith(".csv")]
        if len(csv_files) != 3:
            print(f"Folder '{root}' does not contain exactly 3 CSV files.")
            continue  # 如果不符合条件，跳过该文件夹
        for file in files:
            if file.endswith(".csv"):
                for keyword in keywords:
                    if keyword in file:
                        # 确定目标文件夹
                        keyword_folder = os.path.join(target_folder, f"{keyword}")
                        # 复制文件到目标文件夹
                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(keyword_folder, file)
                        try:
                            shutil.copy2(src_file, dest_file)
                        except PermissionError as e:
                            print(f"Failed to copy {src_file} to {dest_file}: {e}")
                        break


#示例
if __name__ == "__main__":
    # 默认设置为当前目录层级    
    source_folder = "/Users/sesamekiller/Desktop/gkcx-data"
    
    # 默认设置为当前目录层级
    target_folder = "/Users/sesamekiller/PycharmProjects/Graph2Neo4jDB2.0/data"
    
    # 默认keywords为score, plan, special (这里也可以修改一下默认设置，我就不放到函数里了)
    keywords = input("请输入关键词列表（以逗号分隔）: ").strip().split(",")
    if keywords == [""]: keywords = ["score", "plan", "special"]
    
    organize_csv_files(source_folder, target_folder, keywords)
