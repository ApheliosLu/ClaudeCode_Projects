// ============================================================================
// 03_string_view.cpp  现代 C++ 示例集 · C++17
// 主题: std::string_view —— 只读字符串视图(零拷贝)
// 解决的问题(C++98/11):
//   1) 函数接收"只读字符串", 参数写 const std::string& 时:
//      传入 char* / 字符串字面量 会先隐式构造一个临时 std::string(整串拷贝);
//   2) 想要子串必须 std::string::substr —— 又是整段拷贝, 只想看一眼前缀/后缀
//      却分配了内存;
//   3) 传参"到底会不会拷贝"全看调用方类型, 语义不清晰。
// 替代旧写法: const std::string& / const char* 形参 -> std::string_view
// 铁律(容易踩坑):
//   * string_view 不拥有内存, 只存"指针 + 长度":
//       它引用对象的生命周期必须比它长(不能存临时 string 的 view);
//   * 不保证以 '\0' 结尾 —— 别当 char* 用(printf("%s")、strlen 都不行);
//   * 是"只读"的, 想修改请用 std::string。
// 编译: g++ -std=c++17 -Wall -Wextra 03_string_view.cpp -o demo
// ============================================================================
#include <algorithm>
#include <iostream>
#include <string>
#include <string_view>

// 参数用 string_view: 无论调用方给 string / char* / 字面量, 全都零拷贝
std::size_t count_digits(std::string_view s)
{
    return static_cast<std::size_t>(
        std::count_if(s.begin(), s.end(),
                      [](char c) { return c >= '0' && c <= '9'; }));
}

int main()
{
    // ---- 1. 三种来源零成本接入 ----
    const char*  lit = "abc123xyz";
    std::string  str = "hello 42 world";
    std::string_view v1 = lit;          // 只记录指针和长度
    std::string_view v2 = str;          // 不复制 str 内容
    std::cout << "lit 中数字个数: " << count_digits(v1) << '\n';
    std::cout << "str 中数字个数: " << count_digits(v2) << '\n';

    // ---- 2. 切片 O(1) 不拷贝(对比: string::substr 返回全新 string) ----
    std::string_view full = lit;        // abc123xyz
    std::string_view head = full.substr(0, 3);    // "abc" —— 仍是视图
    std::cout << "前 3 个字符: [" << head << "]\n";

    // ---- 3. 解析场景: remove_prefix 移动"起点", 全程零分配 ----
    std::string_view url = "https://example.com/page";
    url.remove_prefix(8);                          // 去掉 "https://"
    std::string_view host = url.substr(0, url.find('/'));
    std::cout << "host = " << host << '\n';

    // ---- 4. 把"只要前缀/后缀"的检查写成视图, 不再复制 ----
    std::string_view filename = "report.tar.gz";
    // C++20 起有 starts_with/ends_with, 本文件是 C++17, 用 substr 等效实现:
    bool ok = filename.substr(0, 6) == "report" && filename.size() >= 3 &&
              filename.substr(filename.size() - 3) == ".gz";
    std::cout << "文件名以 report 开头且以 .gz 结尾: "
              << (ok ? "是" : "否") << '\n';

    // ---- 5. 悬垂警告(只注释不执行, 看了记住) ----
    // std::string_view dangling = std::string("temp").substr(0, 2);
    //   临时 string 在这一行结束就销毁了, dangling 指向已释放内存 —— UB!
    // 结论: view 只用来"短暂观察", 别存到比源对象活得久的地方。
    return 0;
}
