import os
import shutil

def safe_copy_and_rename():
    # 设置输出的独立文件夹名称
    out_dir = "Renamed_Assets"
    
    print(f"开始扫描 .bytes 文件...\n文件将复制并输出到 [{out_dir}] 文件夹中\n")
    
    count_png = 0
    count_ogg = 0
    count_wav = 0
    count_jpg = 0
    count_unknown = 0

    # 遍历当前目录及子目录
    for root, dirs, files in os.walk('.'):
        # 跳过输出文件夹本身，防止无限套娃
        if out_dir in root:
            continue

        for file in files:
            if not file.endswith('.bytes'):
                continue
                
            src_path = os.path.join(root, file)
            
            # 读取文件头 8 个字节
            try:
                with open(src_path, 'rb') as f:
                    header = f.read(8)
            except Exception as e:
                print(f"无法读取文件 {file}: {e}")
                continue

            new_ext = ""
            
            # 严格匹配文件头 (Magic Number)
            if header.startswith(b'\x89PNG'):
                new_ext = ".png"
                count_png += 1
            elif header.startswith(b'OggS'):
                new_ext = ".ogg"
                count_ogg += 1
            elif header.startswith(b'RIFF'):
                new_ext = ".wav"
                count_wav += 1
            elif header.startswith(b'\xFF\xD8\xFF'):
                new_ext = ".jpg"
                count_jpg += 1
            else:
                # 无法识别的文件，安全处理为 .unknown
                new_ext = ".unknown"
                count_unknown += 1

            # 保持原有的子文件夹结构
            rel_dir = os.path.relpath(root, '.')
            target_dir = os.path.join(out_dir, rel_dir)
            os.makedirs(target_dir, exist_ok=True)

            # 生成新的目标路径
            base_name = os.path.splitext(file)[0]
            dest_path = os.path.join(target_dir, base_name + new_ext)

            # 执行复制操作 (shutil.copy2 会保留文件的修改时间等元数据)
            try:
                shutil.copy2(src_path, dest_path)
            except Exception as e:
                print(f"复制失败 {file}: {e}")

    print("🎉 复制并重命名完成！")
    print("-" * 30)
    print(f"🖼️ 成功提取 PNG 图片 : {count_png} 个")
    print(f"🖼️ 成功提取 JPG 图片 : {count_jpg} 个")
    print(f"🎵 成功提取 OGG 音乐 : {count_ogg} 个")
    print(f"🔊 成功提取 WAV 音效 : {count_wav} 个")
    print(f"❓ 未知格式 (.unknown): {count_unknown} 个")
    print("-" * 30)
    print(f"请前往 [{out_dir}] 文件夹查看！")

if __name__ == '__main__':
    safe_copy_and_rename()
