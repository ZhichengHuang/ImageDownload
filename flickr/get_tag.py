import sys
import os
import json
try:
    import flickrapi 
except ImportError:
    print("Import flickrapi error")
    sys.exit(1)
from collections import defaultdict

API_KEY="28ec2097317c948561c7aff0922a2275"
API_SECRET="0af5c27bc03cd4a6"
out_path="d:\\data_flickr"

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


def get_tags(home_url,group_id):
    fl = flickrapi.FlickrAPI(api_key=API_KEY,secret=API_SECRET,format="parsed-json")
    out=defaultdict(list)

    for item in home_url:
        infors=fl.photo.getInfo(item['id'])
        key = str(item['group_id'])+"_"+str(item['id'])
        tags = infors['photo']['tags']
        for tag in tags:
            out[key].append(tag['raw'])

    json.dump(out,open(os.path.join(out_path,str(group_id)+".json"),'w'))


def Process():
    group_ids = ["676823@N25","723938@N21","750028@N22","2723450@N25","696731@N20","725934@N25"]
    for group_id in group_ids:
        home_urls=get_file_home(group_id)
        get_tags(home_urls,group_id)


if __name__=="__main__":
    Process()