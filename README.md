# 深度拷贝一个网页，将其当前状态保存到本地

## 后端技术栈

-   python3
-   sqlite3
-   flask
-   requests

## 前端技术栈

以一个 chrome 插件存在，[参考地址](https://github.com/chendss/chromeEx)

## 使用说明

-   [下载 chrome 扩展源码](https://github.com/chendss/chromeEx)
-   修改项目中的 _src\assets\custom.js_ 中的**copyUrl**为自己部署的接口地址，编译成插件安装到 chrome 浏览器，将会出现下图 ![](http://p2.so.qhimgs1.com/t02da26a6bdd4522d81.jpg)
-   部署本后台项目
-   点击**复刻**按钮，不一会将会保存本网页到服务器
-   访问根地址即可得到已保存的网页列表 ![](http://p2.so.qhimgs1.com/t02eff7efadccfd639b.jpg)
