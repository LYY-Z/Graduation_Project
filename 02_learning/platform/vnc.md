### 1. 在 PowerShell 连服务器并建立隧道

复制这条命令运行：

```powershell
ssh -p 26589 -L 5802:127.0.0.1:5802 -L 6080:127.0.0.1:6080 robotic_dog@frp-mix.com
```

输入服务器账户密码。连接成功后会看到服务器的命令提示符。**这个 PowerShell 窗口要一直开着**，不要输入 `exit`。

### 2. 启动服务器桌面

在刚才的 PowerShell 窗口里运行：

```bash
~/bin/start-remote-desktop
```

看到 `Remote desktop ready` 就表示桌面服务已就绪。

### 3. 用浏览器打开桌面

在同一台电脑的浏览器打开：

[服务器桌面链接](http://127.0.0.1:5802/vnc.html?host=127.0.0.1&port=6080&path=websockify&autoconnect=true&resize=scale&view_only=false)

http://127.0.0.1:5802/vnc.html?host=127.0.0.1&port=6080&path=websockify&autoconnect=true&resize=scale&view_only=false

VNC密码：6Qw5VTx2

### 4. 退出时

关闭浏览器页面即可。要彻底断开时，在 PowerShell 输入：

```bash
exit
```

下次使用时，从第 1 步重新开始。