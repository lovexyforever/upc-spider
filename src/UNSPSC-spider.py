import requests
from bs4 import BeautifulSoup
import json
import copy
# def getRequest(url):
#     response = requests.get(url)
#     response_result = response.content
#     return response_result

# def responseAnalyse(url):
#     response = getRequest(url)
#     response_analyse_result = BeautifulSoup(response,'lxml')
#     return response_analyse_result

# # def firstItemEleAnalyse(url):
# #     response_analyse_result = responseAnalyse(url)
# #     response_analyse_result.find('dev')

def write_data(path, result):
    max_depth = max([len(x) for x in result])
    print(result)
    with open(path,"a") as f:
        for line in result:
            print(line)
            data = line+["" for _ in range(max_depth-len(line))]
            f.write(",".join(data)+'\n')

def process_res_data(content):
    return json.loads(json.loads(content).get('data'))


def get_root_object(url):
    response = requests.get("http://ungm.org.cn/home/ungm/unspsc")

    response_analyse = BeautifulSoup(response.content,'lxml')

    result = []
    for root_tag in response_analyse.find('div',{'class':'unspsc1'}).find_all('div',{'onclick':'fun(this)'}):
        root_id = root_tag.get("id")
        sub_text = root_tag.text
        root_list = [root_id,sub_text]
        result.append(root_list)
        result.extend(get_sub_object(root_id, 1, copy.deepcopy(root_list), response))
    return result

def get_sub_object(id, depth, last_list, response):   
    result = []
    data = {
        "id": (None, id)
    }
    X_CSRF_TOKEN = BeautifulSoup(response.content,'lxml').find("meta",{"name":"csrf-token"})['content']
    cookie = "; ".join(["=".join(x) for x in response.cookies.items()])
    headers = {"X-CSRF-TOKEN":X_CSRF_TOKEN,
        "Cookie": cookie
    }
    content = postWithFormdata("http://ungm.org.cn/home/ungm/fun1",data,headers).text
    sub_object_data = process_res_data(content)
    for sub_object_item in sub_object_data:
        item_id = sub_object_item.get("id")
        item_name = sub_object_item.get("name")
        # print(depth, item_id, item_name)
        res = copy.deepcopy(last_list)+[item_id,item_name]
        result.append(res)
        print(res)
        result.extend(get_sub_object(item_id, depth+1, copy.deepcopy(res), response))
    return result
    # return sub_object_data



def postWithFormdata(url, data, headers):
    return requests.post(url, files = data, headers = headers)


if __name__ == "__main__":


    result = get_root_object("http://ungm.org.cn/home/ungm/unspsc")

    write_data("res.csv", result)
    # print(result)