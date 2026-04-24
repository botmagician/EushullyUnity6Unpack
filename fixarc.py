import os

def fix_eushully_arc(filename):
    # 检查文件是否存在
    if not os.path.exists(filename):
        print(f"找不到文件: {filename}")
        return

    out_filename = filename.replace('.arc', '.bundle')
    print(f"正在处理 {filename} -> {out_filename} ...")

    with open(filename, 'rb') as f_in, open(out_filename, 'wb') as f_out:
        # 读取前 23 个字节
        header = f_in.read(23)
        
        # 验证是不是 E社的伪装头
        if not header.startswith(b'@ARCH000'):
            print(f"警告：{filename} 不是 E社的伪装格式，或者已经被处理过了！")
            return

        print("检测到 @ARCH000 伪装头，正在切除并导出标准 UnityFS 文件...")
        
        # 分块读取剩下的所有数据并写入新文件（防止文件太大撑爆内存）
        chunk_size = 8 * 1024 * 1024 # 每次读 8MB
        while True:
            chunk = f_in.read(chunk_size)
            if not chunk:
                break
            f_out.write(chunk)
            
    print(f"处理完成！快把 {out_filename} 拖进 AssetStudio 吧！\n")

# 批量处理目录下的所有 .arc 文件
if __name__ == '__main__':
    for file in os.listdir('.'):
        if file.endswith('.arc'):
            fix_eushully_arc(file)
