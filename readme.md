## 使用环境：

  * python 3.6
  * windows
  * 相关包：
    * SQlite3(python 自带)
    * html.parser(python 自带)
    * bs4
    * requests
    * PIL
    * flask
    * lxml
    * maxminddb-geolite2
    * 根据错误提示安装相应的packdage

## 使用方式

  1. 配置params.cfg文件
    配置图片存放路径：database(默认当前目录的images文件夹)<br>
    可以配置的图片网站有 google , flicker , getty , bing<br>
    可以配置的项是：图片的大小 ， 图片的上传日期(flicker 支持) ，页面的数量，每页几张图片，图片的格式等等（具体查看params.cfg）<br>

  2. 配置keyword.txt文件
    在文件中列出搜索图片要用的关键字 ，'#'代表注释掉

  3. 当前目录下 在 python环境的cmd输入
  ```
  python Querykeywords.py params.cfg keyword.txt
  ```
  开始爬取路径并下载图片<br>
  4. 当前目录下 在 python环境的cmd输入
  ```
  python app.py
  ```
  启动简易服务器<br>
  5. 根据提示打开网页(localhost:5000)进行图片下载数目查看


## 目录结构

  * ./images : 存放图片的地方，可以在params.cfg 中进行修改
  * ./images/每个 keyword 对应一个文件夹
  * ./module : 搜索引擎模块
  * ./tempolate : 网页模板
  * ./keyword.txt : 搜索关键字
  * ./params.cfg : 爬虫配置项
  * ./url.db : SQlite3 数据库文件
