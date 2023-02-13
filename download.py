import json
import sys
import time
from urllib.parse import unquote,quote,urlparse

import requests

print("输入待下载的RenderListDataAsStream链接,它一般为如下形式(注意，为方便理解，该链接已经经过url decode解密，实际输入时解不解密都行。链接里面的中文只是示范，不是实际链接 ! ! ! ):\n\nhttps://文件分享者.sharepoint.com/personal/某些名称/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream?@a1='/personal/某些名称'&RootFolder=/personal/某些名称&TryNewExperienceSingle=TRUE\n")

dir = input()
dir_unquote = unquote(dir)
url_parsed = urlparse(dir_unquote)
url_parsed_query = url_parsed.query.split('&')
# for i in url_parsed_query:
#     if '@a1=' in i:
#         param_a1 = i.split('=')[1].strip("'")
#     elif 'RootFolder=' in i:
#         param_rootfolder = i.split('=')[1]
# print(type(param_rootfolder),type(param_a1))
print('\n你输入的链接经过url decode后为:\n',dir_unquote,'\n一般而言，这个链接不应该出现目录下的文件，如有错误请重启程序重新输入\n\n现在，请输入FedAuth, 它一般在Header里的Cookies中\n')

fed_auth_cookie = {
      "FedAuth": input()
}

print('\nFedAuth已输入，接下来，请输入保存文件的路径(若目录不存在一般会自动创建目录)\nWindows填写样式 C:\\Users\\%USERNAME%\\Desktop\nLinux填写样式 /home/download')
save_path = input()

if save_path == '':
      print('你还没有输入保存路径!')
      sys.exit()
save_path = save_path.rstrip('/').rstrip('\\')

print('\n你下载的文件将被保存至',save_path,'中\n')

dir_decoded = dir_unquote.split('&')
def getFileList(firstLink):
      #因为One Drive需要分好几次才能获取到全部文件，所以这里需要先获取全部的RenderList链接
      links = [firstLink]
      count = 0
      isFinish = False
      #第一个链接
      fetchList = requests.post(url = firstLink, cookies= fed_auth_cookie).json()
      count = count + len(fetchList['Row'])
      print('从第一个链接中发现的文件(夹)数量 :',len(fetchList['Row']))

      while not isFinish:
            if 'NextHref' in fetchList:
                  #继续获取文件列表
                  next_link = dir_decoded[0] + '&' + fetchList['NextHref'].lstrip('?')
                  fetchList = requests.post(url = next_link, cookies= fed_auth_cookie).json()
                  count = count + len(fetchList['Row'])
                  print('从下一个链接中发现的文件(夹)数量 :',len(fetchList['Row']))
                  links.append(next_link)
            else:
                  isFinish = True

      print('获取文件链接完成，在一级目录下共发现 :',count,'个文件\n接下来将获取各个文件链接 （Tips: 所用时长取决于文件数量，一般为 文件数量 * 0.8 (秒) , 请耐心等待!)')
      return links

def fetchFile(uri):
      URIs = getFileList(uri) #存储带查询的文件夹链接
      errorURIs = []
      fileURIs = []

      for arguement in URIs:
            time.sleep(0.8)
            #部分文件在请求时会报错，不会返回json，具体原因未知
            #初步估计是请求时没有编码的原因
            try:
                  _resp = requests.post(arguement, cookies=fed_auth_cookie).json()
                  resp = _resp['Row']
            except:
                  print('发现一个无法解析的链接\n',_resp)
                  errorURIs.append(arguement)
                  continue
            for i in resp:
                  if i['File_x0020_Type'] == '':
                        #为 文件夹
                        URIs.append(dir_decoded[0] + '&RootFolder=' + quote(i['FileRef']) + '&TryNewExperienceSingle=TRUE')
                  else:
                        #为 文件
                        link = "https://" + url_parsed.netloc + quote(i['FileRef'])
                        address_decoded = i['FileRef'].encode('unicode_escape').decode('unicode-escape') # /xxx/xxxx/xxx.xxx
                        _address = address_decoded.split('Documents')[1]
                        fileName = _address.split('/')[-1]
                        address = _address.replace('/' + fileName,'')
                        # global param_a1,param_rootfolder
                        # _param_a1 = param_a1.lstrip('/').split('/')
                        # _param_rootfolder = param_rootfolder.lstrip('/').split('/')
                        # _address = [i for i in _param_rootfolder if i not in _param_a1]
                        # address = '/' + i['FileRef']
                        # for i in _address:
                        #       address += i + '/'
                        if len(save_path + address) > 255:
                              print('\n*************************************\n警告: 发现一个过长的文件目录，这在某些Windows系统下可能出现错误!!!\n*************************************\n')
                        fileURIs.append((link,address.rstrip('/')))
      return {
            'fileURIs' : fileURIs,
            'errorURIs' : errorURIs
      }
def fw(fileName,link,path):
      with open(fileName,'a',encoding = "utf-8") as file:
            if path:
                  file.write(link + '\n dir=' + path + '\n')
            else:
                  file.write(link + '\n')
print('准备运行...')
list = fetchFile(dir)

file = list['fileURIs']
error = list['errorURIs']
print('获取完成!\n总计 :',len(file),'个文件\n另外，有 :',len(error),'个链接在查询文件列表时出现错误')


for link,path in file:
      fw('downlink.txt',link, save_path + path)
for link in error:
      fw('errorlink.txt',link, None)
print('downlink.txt文件写入完成,请在aria2里使用如下链接来下载.\n\naria2c --header="Cookie:FedAuth=' + fed_auth_cookie['FedAuth'] + '" --input-file=downlink.txt --max-concurrent-downloads=1 --max-connection-per-server=4 --max-overall-download-limit=5M\n\n')

