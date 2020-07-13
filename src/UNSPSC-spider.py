import requests
from bs4 import BeautifulSoup
import json
import copy
import multiprocessing
from multiprocessing import Manager
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

def get_header():
    response = requests.get("http://ungm.org.cn/home/ungm/unspsc")
    X_CSRF_TOKEN = BeautifulSoup(response.content,'lxml').find("meta",{"name":"csrf-token"})['content']
    cookie = "; ".join(["=".join(x) for x in response.cookies.items()])
    header = {"X-CSRF-TOKEN":X_CSRF_TOKEN,
        "Cookie": cookie
    }
    return header


def write_data(path, result):
    max_depth = max([len(x) for x in result])
    with open(path,"a") as f:
        title = ["depth"] + ["code,name" for _ in range((max_depth-1)//2)]
        f.write(",".join(title))
        for line in result:
            data = line+["" for _ in range(max_depth-len(line))]
            f.write("\n"+",".join(data).replace(u'\xa0',u''))

def process_res_data(content):
    return json.loads(json.loads(content).get('data'))


def get_root_object(url):
    response = requests.get("http://ungm.org.cn/home/ungm/unspsc")

    response_analyse = BeautifulSoup(response.content,'lxml')

    result = []
    jobs = []
    pool = multiprocessing.Pool(10)
    for root_tag in response_analyse.find('div',{'class':'unspsc1'}).find_all('div',{'onclick':'fun(this)'}):
        root_id = root_tag.get("id")
        sub_text = root_tag.text
        root_list = ["1",root_id,sub_text]
        result.append(root_list)
        # result.extend(get_sub_object(root_id, 2, copy.deepcopy(root_list), get_header()))
        jobs.append(pool.apply_async(get_sub_object, (root_id, 2, copy.deepcopy(root_list), get_header())))
    pool.close()
    pool.join()
    for proc in jobs:
        result.extend(proc.get())
    return result

def get_sub_object(id, depth, last_list, header):   
    result = []
    data = {
        "id": (None, id)
    }
    content = postWithFormdata("http://ungm.org.cn/home/ungm/fun1",data,header).text
    sub_object_data = process_res_data(content)
    for sub_object_item in sub_object_data:
        item_id = sub_object_item.get("id")
        item_name = sub_object_item.get("name")
        res = copy.deepcopy(last_list)+[item_id,item_name]
        res[0] = str(depth)
        result.append(res)
        print(depth,item_id,item_name)
        result.extend(get_sub_object(item_id, depth+1, copy.deepcopy(res), header))
    return result



def postWithFormdata(url, data, headers):
	try:
		response = requests.post(url, files = data, headers = headers)
		return response
	except:
		print(data.get("id")[1]," is wrong")
		return '{"data":"[]"}'


if __name__ == "__main__":


    result = get_root_object("http://ungm.org.cn/home/ungm/unspsc")

    write_data("res.csv", result)
    # print(result)