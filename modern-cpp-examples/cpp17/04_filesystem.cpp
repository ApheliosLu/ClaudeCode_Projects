// ============================================================================
// 04_filesystem.cpp  现代 C++ 示例集 · C++17
// 主题: std::filesystem —— 跨平台文件系统库
// 解决的问题(C++98):
//   遍历目录/查信息/拼接路径是高频需求, 标准库却完全没有 —— 只能调平台
//   API(opendir/readdir 或 FindFirstFile), 换平台整段重写;
//   路径拼接更是手写字符串 + 分隔符('\' vs '/')地狱, 中文路径还常踩编码坑。
// 替代旧写法: opendir/FindFirstFile 等平台 API -> std::filesystem;
//            手拼路径字符串 -> path 的 operator/
// 要点:
//   * fs::path 自动处理平台分隔符与编码;
//   * 错误处理两种: 抛 filesystem_error(默认) 或 传 std::error_code 不抛;
//   * 本示例全程 error_code 版(异常安全、不打断流程);
//   * 头文件 <filesystem>; g++ 9 起无需额外链接库。
// 编译: g++ -std=c++17 -Wall -Wextra 04_filesystem.cpp -o demo
// ============================================================================
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

namespace fs = std::filesystem;

int main()
{
    // 演示目录放在系统临时目录, 结束时自行清理
    fs::path demo_dir = fs::temp_directory_path() / "cpp17_fs_demo";

    std::error_code ec;
    fs::create_directories(demo_dir, ec);          // 多级目录一次建好
    if (ec) {
        std::cout << "创建目录失败: " << ec.message() << '\n';
        // 输出: 创建目录失败: <错误原因>(本程序未走到, 临时目录可正常创建)
        return 1;
    }

    // 写两个文件 —— ofstream 直接吃 path(路径拼接交给 operator/)
    const fs::path report = demo_dir / "report.txt";
    std::ofstream(report) << "hello std::filesystem\n";
    std::ofstream(demo_dir / "data.csv") << "1,2,3\n";

    // ---- 遍历目录(不再写平台专属循环) ----
    std::cout << "目录内容(" << demo_dir.string() << "):\n";
    // 输出: 目录内容(C:\Users\q1209\AppData\Local\Temp\cpp17_fs_demo):
    for (const fs::directory_entry& e : fs::directory_iterator(demo_dir))
        std::cout << "  " << e.path().filename().string()
                  << "  (" << e.file_size() << " B)\n";  // 输出: 每个文件一行(名称 + 字节数)
    // 输出:
    //   data.csv  (7 B)
    //   report.txt  (23 B)

    // ---- 查询属性 ----
    std::cout << "report.txt: exists = " << fs::exists(report)
              << ", 是普通文件 = " << fs::is_regular_file(report)
              << ", 大小 = " << fs::file_size(report) << " B\n";
    // 输出: report.txt: exists = 1, 是普通文件 = 1, 大小 = 23 B
    std::cout << "  扩展名 = " << report.extension().string()
              << " | 主名 = " << report.stem().string()
              << " | 父目录 = " << report.parent_path().string() << '\n';
    // 输出:
    //   扩展名 = .txt | 主名 = report | 父目录 = C:\Users\q1209\AppData\Local\Temp\cpp17_fs_demo

    // ---- 修改时间(与"文件时钟"求差, 得到相对时间) ----
    auto ft    = fs::last_write_time(report);
    auto delta = std::chrono::duration_cast<std::chrono::seconds>(
                     fs::file_time_type::clock::now() - ft).count();
    std::cout << "距上次写入约 " << delta << " 秒\n";
    // 输出(示例, 每次运行数值不同): 距上次写入约 0 秒

    // ---- 收尾: 清理自己创建的演示目录 ----
    fs::remove_all(demo_dir, ec);
    std::cout << "演示目录已清理: " << demo_dir.string() << '\n';
    // 输出: 演示目录已清理: C:\Users\q1209\AppData\Local\Temp\cpp17_fs_demo
    return 0;
}
