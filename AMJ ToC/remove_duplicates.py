import pandas as pd
import os

def remove_duplicates(input_file):
    # 生成输出文件名
    file_dir = os.path.dirname(input_file)
    file_name = os.path.basename(input_file)
    name, ext = os.path.splitext(file_name)
    output_file = os.path.join(file_dir, f"{name}_unique{ext}")
    
    # 读取CSV文件
    try:
        print(f"\n正在读取文件: {input_file}")
        df = pd.read_csv(input_file)
        
        # 记录去重前的行数
        original_count = len(df)
        
        # 使用所有列进行去重
        df_unique = df.drop_duplicates()
        
        # 记录去重后的行数
        final_count = len(df_unique)
        
        # 按Volume和Issue排序
        df_unique = df_unique.sort_values(['Volume', 'Issue'])
        
        # 保存去重后的数据到新文件
        df_unique.to_csv(output_file, index=False)
        
        print(f"\n去重完成:")
        print(f"原始数据条数: {original_count}")
        print(f"去重后数据条数: {final_count}")
        print(f"共删除 {original_count - final_count} 条重复数据")
        print(f"去重后的数据已保存至: {output_file}")
        
    except Exception as e:
        print(f"去重过程中出错: {str(e)}")

def main():
    input_file = 'AMJ ToC/amj_articles.csv'
    remove_duplicates(input_file)

if __name__ == '__main__':
    main() 