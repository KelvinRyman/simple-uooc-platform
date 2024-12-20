请将所有的权限测试都集中在一个export的函数中：
- 能在前端获取当前登录的用户和相关的信息
- 能通过用户的角色和权限判断用户是否有权限访问某个页面
- 如果用户未登录则只能访问unAuthorizedRoutes中的页面，否则重定向到 login.html
- 如果用户已登录则只能访问authorizedRoutes中的页面，否则重定向到 pages/dashboard.html
- 如果用户已登录但是没有对应的权限则重定向到 pages/dashboard.html

重构register.js，使其实现以下的功能，并引入到register.html：
- 能够像后端api发送注册的请求，注册一个新用户
- 注册成功后重定向到 login.html
- 注册失败则弹出错误信息
- 可以契合jwt的登录逻辑
- 不在token中使用明文保存密码