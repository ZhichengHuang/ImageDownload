import sys
import os
import requests
import urllib
import random
from time import sleep
try:
    import flickrapi 
except ImportError:
    print("Import flickrapi error")
    sys.exit(1)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing import Queue,Process
import pickle



API_KEY="28ec2097317c948561c7aff0922a2275"
API_SECRET="0af5c27bc03cd4a6"
out_path="d:\\data_flickr"
#group_id="723938@N21"

def get_file_home(group_id):
    fl = flickrapi.FlickrAPI(api_key=API_KEY,secret=API_SECRET,format="parsed-json")
    home_url=[]
    page_id=1
    while True:
        rsp = fl.groups.pools.getPhotos(group_id=group_id,page=page_id,per_page=500)
        photos = rsp['photos']['photo']
        for photo in photos:
            tmp={
                "owner": photo['owner'],
                "id": photo['id'],
                "url": "https://www.flickr.com/photos/{}/{}".format(photo['owner'],photo['id']),
                "group_id": group_id
            }
            home_url.append(tmp)
        if rsp['photos']['pages']<=page_id:
            break
        page_id+=1
        print("page_id=",page_id)
    return home_url

def get_video_url(home_url,que,group_id):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options=chrome_options,executable_path="c:\\Users\\t-zhihua\\Downloads\\chromedriver.exe")
    out_list=[]
    error_list=[]
    
    for index, item in enumerate(home_url):
        try:
            driver.get(item['url'])
            element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "vjs-tech")))
            item['video_url']=driver.find_element_by_class_name("vjs-tech").get_attribute("src")
            out_list.append(item)
            #download_video(item)
            que.put(item)
            
            
        except Exception as e:
            print(e)
            error_list.append(item)
        if index%100==0:
            # driver.close()
            # driver = webdriver.Chrome(chrome_options=chrome_options,executable_path="c:\\Users\\t-zhihua\\Downloads\\chromedriver.exe")
            print("process {} item".format(index))
    que.put("#")
        
    print("total={},get_video_url={},error_url={}".format(len(home_url),len(out_list),len(error_list)))
    pickle.dump(error_list,open(os.path.join(out_path,str(group_id),"error.pkl"),'wb'))
    #return out_list,error_list

def download_video(que):
    index=0
    
    while True:
        if que.empty():
            sleep(100)
       
        print("que size",que.qsize())
        index+=1
        
        item = que.get()
        if item in ["#",]:
            break
       
        num=random.randint(0,100)
        try:
            res=requests.get(item['video_url'])
            data = res.content
            if data:
                file_dir=os.path.join(out_path,item['group_id'])
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
                file_path = os.path.join(file_dir,item['owner']+"_"+item['id']+"_"+str(num)+".mp4")
                with open(file_path,"wb") as f:
                    f.write(data)
            else:
                print("video down error {}".format(item['video_url']))
        except Exception as e:
            print(e)
            res=requests.get(item['video_url'])
            data = res.content
            if data:
                file_dir=os.path.join(out_path,item['group_id'])
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
            
                file_path = os.path.join(file_dir,item['owner']+"_"+item['id']+"_"+str(num)+".mp4")
                with open(file_path,"wb") as f:
                    f.write(data)
    print("finish download video")
        
        
        

def get_video_file(out_list):
    pass
    #p=Pool(5)
    #p.map(download_video,out_list)


def process_function(group_id):
    q=Queue()
    home_url=get_file_home(group_id)
    p1=Process(target=get_video_url,args=(home_url,q,group_id))
    #get_video_url(home_url)
    c1=Process(target=download_video,args=(q,))
    #get_video_file(out_list)
    p1.start()
    sleep(5)
    c1.start()
    p1.join()
    #pickle.dump(error_list,open(os.path.join(out_path,group_id,"error.pkl"),'wb'))


if __name__=="__main__":
    group_ids=['676823@N25','2723450@N25']
    for item in group_ids:
        process_function(item)