import os

def split_arc_to_bundles(filename):
    print(f"正在透视扫描 {filename} ...")
    
    # 把整个 1GB 文件读入内存
    with open(filename, 'rb') as f:
        data = f.read()

    # Unity 资源包的标准开头标志 (8个字节，极其稳定)
    magic = b'UnityFS\x00'
    
    offsets = []
    idx = 0
    
    # 寻找所有的 UnityFS 开头
    while True:
        idx = data.find(magic, idx)
        if idx == -1:
            break
        offsets.append(idx)
        idx += len(magic) # 跳过当前标志，继续往后找

    if not offsets:
        print(f"在 {filename} 中没有找到任何 Unity 包！")
        return

    print(f"🎉 破解成功！在 {filename} 中发现了 {len(offsets)} 个隐藏的 Unity 资源包！")
    
    # 创建一个专属文件夹存放切分出来的包
    out_dir = filename.replace('.arc', '') + "_Bundles"
    os.makedirs(out_dir, exist_ok=True)

    # 开始切分并保存
    for i in range(len(offsets)):
        start = offsets[i]
        # 如果是最后一个包，就一直切到文件末尾
        end = offsets[i+1] if i + 1 < len(offsets) else len(data)
        
        bundle_data = data[start:end]
        out_path = os.path.join(out_dir, f"part_{i:04d}.bundle")
        
        with open(out_path, "wb") as f_out:
            f_out.write(bundle_data)
            
    print(f"分割完成！已将 {len(offsets)} 个包保存到 {out_dir} 文件夹中。\n")

if __name__ == '__main__':
    # 扫描当前目录下所有的 .arc 文件
    for file in os.listdir('.'):
        if file.endswith('.arc'):
            split_arc_to_bundles(file)
