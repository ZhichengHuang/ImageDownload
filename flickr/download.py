import sys
import os
import requests
import urllib
try:
    import flickrapi 
except ImportError:
    print("Import flickrapi error")
    sys.exit(1)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from multiprocessing import Pool
import pickle



API_KEY="28ec2097317c948561c7aff0922a2275"
API_SECRET="0af5c27bc03cd4a6"
out_path="d:\\data_flickr"
group_id="723938@N21"

def get_file_home(group_id):
    fl = flickrapi.FlickrAPI(api_key=API_KEY,secret=API_SECRET,format="parsed-json")
    home_url=[]
    page_id=1
    while True:
        rsp = fl.groups.pools.getPhotos(group_id=group_id,page_id=page_id)
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

def get_video_url(home_url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options=chrome_options,executable_path="c:\\Users\\t-zhihua\\Downloads\\chromedriver.exe")
    out_list=[]
    error_list=[]
    for item in home_url:
        try:
            driver.get(item['url'])
            item['video_url']=driver.find_element_by_class_name("vjs-tech").get_attribute("src")
            out_list.append(item)
        except Exception:
            error_list.append(item)
    print("total={},get_video_url={},error_url={}".format(len(home_url),len(out_list),len(error_list)))
    return out_list,error_list

def download_video(item):
    res=requests.get(item['video_url'])
    data = res.content
    if data:
        file_dir=os.path.join(out_path,item['group_id'])
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        file_path = os.path.join(file_dir,item['owner']+"_"+item['id']+".mp4")
        with open(file_path,"wb") as f:
            f.write(data)

def get_video_file(out_list):
    p=Pool(5)
    p.map(download_video,out_list)


def process_function():
    home_url=get_file_home(group_id)
    out_list,error_list=get_video_url(home_url)
    get_video_file(out_list)
    pickle.dump(error_list,open(os.path.join(out_path,group_id,"error.pkl"),'wb'))


if __name__=="__main__":
    process_function()