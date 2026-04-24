# 以下部分是ai写的，AutoRename对应的SafeRename

随着 E社（Eushully）放弃祖传 AGE 引擎，全面转向大名鼎鼎的 Unity 引擎，很多玩家和汉化组都以为迎来了“解包自由”的时代。毕竟 Unity 是全世界被研究得最透彻的引擎。

然而，当大家真正拿到游戏，试图用传统的 AssetStudio 等工具去解包时，却遭遇了迎头痛击：**工具要么直接报错崩溃，要么导出来的全是一堆打不开的乱码文件。**

E社到底施了什么魔法？其实，他们并没有使用什么军工级的底层加密，而是非常巧妙地利用了**文件拼接、版本代差和类型伪装**，打出了一套“防君子不防小人”的组合拳。

本文将把这套组合拳的底层原理彻底扒开，并提供一套傻瓜式的完整解包教程。如果你想做汉化、提取立绘音乐、或者制作 Mod，请务必仔细阅读。

---

## 🕵️ 第一部分：核心原理解析（E社的四大障眼法）

### 障眼法一：假身份证（23字节的伪装头）
如果你用十六进制编辑器打开 `ver00d0.arc`，你会发现它的开头并不是 Unity 标准的标志，而是 `@ARCH000` 加上一串时间戳，总共 **23 个字节**。
这就是 E社 的第一层防御。市面上普通的解包工具一上来看到 `@ARCH000`，直接就懵了，以为是不认识的专属格式，当场报错退出。
**破解法：** 只需要写个脚本（`FixArc.py`），把开头这 23 个字节的“盲肠”切掉，它就会瞬间变回全世界都认识的标准 `.bundle` 文件。

### 障眼法二：连体婴儿（1GB 封包的秘密）
当你切掉伪装头，满心欢喜地把 1GB 大小的 `ver00d1.arc` 塞进工具时，却发现工具只读出了几百 KB 的数据就停了。剩下的 999MB 去哪了？
**真相是：** E社并没有把 1GB 的资源打包成 1 个巨大的文件。他们打包了**几百个标准的小型资源包**，然后写了个脚本，把这几百个包像接火车车厢一样，**首尾相连硬生生拼成了一个巨大的文件**。
工具读完第一个包的结尾，以为文件结束了，直接无视了后面的几百个包。
**破解法：** 我们需要用脚本（`SplitBundles.py`）扫描全文，把这辆长长的火车重新切分成几百节独立的车厢。

### 障眼法三：跨时代的版本碾压（老牌神器为何崩溃）
当你成功切分了包，用以前解包最常用的 **AssetStudio** 去读取时，大概率会遇到 `EndOfStreamException` 报错，甚至软件直接卡死。
这不是因为包坏了，而是因为 E社 这次非常激进，直接使用了目前极新的 **Unity 6（内部版本号 v39）** 引擎！AssetStudio 已经停更很久了，它根本不认识 Unity 6 里面修改过的 3D 模型（MeshRenderer）等数据结构，算错长度导致崩溃。
**破解法：** 淘汰旧工具，全面拥抱现代开源工具 **AssetRipper**。

### 障眼法四：为了保护画质，对引擎撒谎（图片为何变文本）
当你成功导出资源后，你会崩溃地发现：根本找不到 `Texture2D`（图片）和 `AudioClip`（音乐），导出来的全是一堆名为 `TextAsset` 的 `.bytes` 二进制文件。
**这是日本 Galgame 厂商的终极套路：** Unity 为了节省显存，导入图片时默认会强制进行有损压缩，这会导致纯 2D 的高清二次元立绘边缘出现马赛克。
为了保住原画级画质，E社程序员在打包前，**把所有的 `.png` 图片和 `.ogg` 音乐的后缀名，强行改成了 `.bytes`。**
Unity 引擎打包时会想：“这是一个未知的二进制文件，我不认识，那我就把它当成纯文本数据，原封不动地塞进去吧。”
就这样，E社成功骗过了 Unity。游戏运行时，再用代码把这些“文本”强行转换回图片。

---

## 🛠️ 第二部分：实战解包教程（三步走战略）

**准备工作：**
1. 电脑上安装好 **Python 3.x** 环境。
2. 去 GitHub 搜索下载最新版的 **AssetRipper**（Windows x64版本）。

### 第一步：破解 `.arc` 封包（切除伪装与分割车厢）

进入游戏的 `Start\Archives` 文件夹。针对不同类型的 `.arc` 文件，我们需要用两个不同的脚本来处理。

#### 1. 处理启动配置包（`ver00d0.arc`）
这个包通常只有一个伪装头，没有拼接。新建一个 `FixArc.py`，复制以下代码并运行：
```python
import os

def fix_eushully_arc(filename):
    out_filename = filename.replace('.arc', '.bundle')
    print(f"正在处理 {filename} -> {out_filename} ...")
    with open(filename, 'rb') as f_in, open(out_filename, 'wb') as f_out:
        header = f_in.read(23)
        if not header.startswith(b'@ARCH000'):
            print("未检测到伪装头，跳过。")
            return
        # 切除前23字节后，写入剩余全部数据
        while True:
            chunk = f_in.read(8 * 1024 * 1024)
            if not chunk: break
            f_out.write(chunk)
    print(f"处理完成！")

if __name__ == '__main__':
    # 仅处理 d0 包
    if os.path.exists('ver00d0.arc'):
        fix_eushully_arc('ver00d0.arc')
```

#### 2. 处理巨型资源包（`ver00d1.arc` ~ `d3.arc`）
这些 1GB 的大包是“连体婴儿”，需要切分。新建一个 `SplitBundles.py`，复制以下代码并运行：
```python
import os

def split_arc_to_bundles(filename):
    print(f"正在切割 {filename} ...")
    with open(filename, 'rb') as f: data = f.read()
    
    magic = b'UnityFS\x00'
    offsets = []
    idx = 0
    
    while True:
        idx = data.find(magic, idx)
        if idx == -1: break
        offsets.append(idx)
        idx += len(magic)

    if not offsets: return

    out_dir = filename.replace('.arc', '') + "_Bundles"
    os.makedirs(out_dir, exist_ok=True)

    for i in range(len(offsets)):
        start = offsets[i]
        end = offsets[i+1] if i + 1 < len(offsets) else len(data)
        with open(os.path.join(out_dir, f"part_{i:04d}.bundle"), "wb") as f_out:
            f_out.write(data[start:end])
            
    print(f"成功将 {filename} 切分为 {len(offsets)} 个标准 Bundle 包！")

if __name__ == '__main__':
    for file in os.listdir('.'):
        if file.endswith('.arc') and file != 'ver00d0.arc': 
            split_arc_to_bundles(file)
```

### 第二步：使用 AssetRipper 提取资源

1. 打开 **AssetRipper**。
2. 将上一步生成的 `ver00d1_Bundles`（以及 d2, d3）整个文件夹，直接拖进 AssetRipper 的窗口中。
3. 等待右下角日志显示 `Finished processing assets`。
4. 点击软件顶部菜单栏的 **`Export` -> `Export All`**，选择一个空文件夹导出。

### 第三步：基因鉴定，还原图片与音乐

导出的文件散落在 `TextAsset` 文件夹里，全都是 `.bytes`。我们需要读取文件头（Magic Number）来自动识别它们的真实身份并改名。

1. 打开 AssetRipper 导出的文件夹，在右上角搜索框输入 `*.bytes`。
2. 全选搜索出来的所有 `.bytes` 文件，**复制**。
3. 在桌面上新建一个空文件夹（比如叫 `Eushully_Assets`），把文件全**粘贴**进去。
4. 在这个新文件夹里，新建一个 `AutoRename.py`，复制以下代码并运行：
```python
import os

def rename_isolated_bytes():
    print("开始扫描并还原文件格式...\n")
    counts = {'png': 0, 'ogg': 0, 'wav': 0, 'jpg': 0, 'unknown': 0}

    for file in os.listdir('.'):
        if not file.endswith('.bytes'): continue
        try:
            with open(file, 'rb') as f: header = f.read(8)
        except: continue

        # 严格匹配文件头 (Magic Number)
        if header.startswith(b'\x89PNG'): ext, key = ".png", 'png'
        elif header.startswith(b'OggS'): ext, key = ".ogg", 'ogg'
        elif header.startswith(b'RIFF'): ext, key = ".wav", 'wav'
        elif header.startswith(b'\xFF\xD8\xFF'): ext, key = ".jpg", 'jpg'
        else: ext, key = ".unknown", 'unknown' # 无法识别的通常是Lua脚本或配置

        new_name = os.path.splitext(file)[0] + ext
        try:
            if os.path.exists(new_name): os.remove(new_name)
            os.rename(file, new_name)
            counts[key] += 1
        except: pass

    print("🎉 格式还原大功告成！")
    print(f"🖼️ PNG: {counts['png']} | 🎵 OGG: {counts['ogg']} | ❓ 未知(脚本): {counts['unknown']}")

if __name__ == '__main__':
    rename_isolated_bytes()
```
**大功告成！** 一瞬间，所有的高清无码立绘、CG、BGM 就会显出原形，直接双击即可食用！

---

## 🚫 第三部分：关于封包与 Mod 制作的避坑指南

很多玩家成功解包修改了图片后，想重新打包成 `.arc` 塞回游戏，这里要泼一盆冷水：**千万不要这么做！**

### 致命痛点：多米诺骨牌效应
游戏内部有一张写死的“目录表”，记录着每个包在巨大 `.arc` 文件中的精确偏移量（Offset）。
如果你修改了一张高清图，导致你的 `.bundle` 文件比原来大了 1MB，当你把它拼回 `.arc` 时，排在它后面的所有包的物理位置都会被往后推 1MB。但游戏引擎不知道这件事，它还是去原来的位置读，结果读到一堆错位的数据，游戏当场崩溃。

### 现代 Mod 的终极解决方案：内存劫持（Hook）
现在 Unity 游戏的汉化和 Mod 制作，早就淘汰了“硬封包”这种吃力不讨好的做法。主流的做法是使用 **BepInEx (IL2CPP版)** 框架。

**核心思想是：我不改你的硬盘文件，我在内存里“截胡”。**
通过写几十行 C# 插件代码，拦截游戏底层的读取函数。告诉游戏：“当你想要读取 `CG_001.bytes` 的时候，不要去 `.arc` 里找了，直接去我桌面的 Mod 文件夹里读取我已经改好的 `CG_001_改.png`，然后把数据返回给引擎！”

这种方法彻底告别了打包、偏移量、压缩算法等一切烦恼，是目前制作大型汉化和修改的唯一指定王道。希望有志于此的大佬们，可以直接向 BepInEx 插件开发的方向研究。
