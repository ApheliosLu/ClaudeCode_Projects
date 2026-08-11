const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = 3000;
const HOST = "localhost";
const PUBLIC_DIR = path.join(__dirname, "public");

const server = http.createServer((req, res) => {
  // 只处理根路径 GET 请求，返回首页
  if (req.url === "/" || req.url === "/index.html") {
    fs.readFile(path.join(PUBLIC_DIR, "index.html"), (err, data) => {
      if (err) {
        res.writeHead(500, { "Content-Type": "text/plain; charset=utf-8" });
        res.end("500 Internal Server Error");
        return;
      }
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(data);
    });
    return;
  }

  // 其他路径（如 /favicon.ico）返回 404
  res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
  res.end("404 Not Found");
});

server.listen(PORT, HOST, () => {
  console.log(`Server is running at http://${HOST}:${PORT}`);
});
