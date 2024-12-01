# YouTube 下载器图形界面

这是一个为 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 开发的图形用户界面，使用 Python 和 tkinter 构建。

[English](README.md)

## 主要特点

- 现代直观的图形用户界面
- 使用树形视图展示可用的视频格式
- MP4格式筛选选项
- 实时下载进度显示：
  - 进度条
  - 下载速度指示器
  - 文件大小信息
- 多线程下载保持界面响应
- 一键选择格式
- 支持高质量视频和音频下载

## 系统要求

- Python 3.6+
- tkinter（通常随Python一起安装）
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) 已安装且可从命令行访问

## 安装方法

1. 确保系统已安装Python
2. 按照 [安装指南](https://github.com/yt-dlp/yt-dlp#installation) 安装yt-dlp
3. 从本仓库下载 `youtube_downloader.py`
4. 运行脚本：
   ```bash
   python youtube_downloader.py
   ```

## 使用方法

1. 启动应用程序
2. 将YouTube网址粘贴到URL输入框
3. 点击"List Formats"查看可用的下载选项
4. 从列表中选择所需格式（会自动填充格式ID）
5. 点击"Download"开始下载
6. 通过进度条和状态指示器监控下载进度

## 详细功能

- **格式列表**：在清晰有序的表格中显示可用格式，包括：
  - 格式ID
  - 编码格式
  - 分辨率
  - 文件大小
  - 附加信息
  
- **MP4过滤器**：可切换只显示MP4格式，方便选择
  
- **进度跟踪**：
  - 完成百分比
  - 当前/总计大小
  - 下载速度
  - 状态消息
  
- **错误处理**：
  - 清晰的错误消息
  - 操作状态指示
  - 优雅的失败处理

## 致谢

这是 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 的图形界面包装器。所有下载功能均由yt-dlp提供。

## 许可证

本项目基于MIT许可证发布。