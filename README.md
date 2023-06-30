# Haire Airbox 海尔空气盒子
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

海尔空气盒子接入Home Assistant插件

FORK https://github.com/NullYing/haire-airbox

代码来源： https://bbs.hassbian.com/thread-9234-1-1.html
作者： zxl_hass

## 联网

海尔已经放弃了这个产品，app也无法再使用，看了 [IOS源码](https://github.com/ybyao07/airbox) 发现是 EasyLink，根据芯片查到了方案，用了[芯片商提供的IOS示例程序=》完整UI的示例程序](https://mxchip.yuque.com/books/share/8ac5e519-671d-4444-a93d-20e0aadfc793/wac2mm#easylink%E7%A4%BA%E4%BE%8Bapp%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E) 成功配网

注意：

1. 测试了IOS 15.2.1无法正常安装示例程序，没辙了就将代码重新编译了并安装到手机，可以正常使用
2. 安卓版在网上找EasyLink的apk，实测3.2版本可以正常配网
3. IOS程序配网时，需要选择Mode，可能是V2，也可能是Plus，测试了一次成功就没再测试

## 安装
1. HACS安装：在Home Assistant中安装HACS，并添加自定义库，选择集成进行安装。
2. 手动安装：在custom_components目录下创建airbox目录，将文件拷贝到该目录下。

## 配置
传感器和开关：
```yaml
sensor:
  - platform: airbox
    host: 10.19.230.123
    scan_interval: 60
switch:
  - platform: airbox
    host: 10.19.230.123  
    switches:
      iptv_vol:   #这个名字自己随意
        friendly_name: IPTV音量
        command_on:  ''                
        command_off: ''  
      iptv_channel:   #这个名字自己随意
        friendly_name: IPTV频道
        command_on:  ''                
        command_off: '' 
```
红外学码和发吗：


开发者工具>服务里面去调用学码服务（发射红外码同理），host地址填空气盒子的IP地址，点击调用服务，然后空气盒子的PM2.5指示灯会变成红色，按下需要学习的按键，学码成功后，学到的码会出现在通知里，复制之后填到command_on：或command_off：后面，全部学完后重启hass，完成。

## Changelog

1. Fork https://github.com/NullYing/haire-airbox
2. 可以在HACS中通过自定义库进行安装