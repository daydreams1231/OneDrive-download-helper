# OneDrive-download-helper
用于辅助aria2下载OneDrive里的文件

如何使用:
打开Onedrive
按F12，选择 网络
刷新页面后找 https://*.sharepoint.com/personal/*/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream?@a1=*&RootFolder=*&TryNewExperienceSingle=TRUE

示例网址中的 * 仅供参考。具体如何因人而异

复制该网址，记为Link

再在该请求里找到Cookies，复制FedAuth参数的所有值，记为Cookie
***注意只需要FedAuth值，别的不用复制***

现在。运行download.py后按提示输入对应值及保存路径即可，完成后程序会生成一个downlink.txt文件，之后用aria2时补一个参数 --input-file=downlink.txt 即可开始下载
