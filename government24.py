# -*- conding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
from collections import OrderedDict
import math

"""
    title_href = title_href.split("'")[1]
    title      = title
    date_index = date_index[0].get_text()
    policy_json= json
"""

def make_policy_url(url):
    make_url = "https://www.gov.kr/portal/gvrnPolicy/view/"+ url +"?srchOrder=&pageIndex=1&policyType=G00301&streamYn=&blgCd=&slgCd=&srchBlgCd=&srchSlgCd=&srchOrgGroup=&srchOriginOrg=&srchPeriodOption=1years&srchStDtFmt=2020.02.27&srchEdDtFmt=2021.02.27&searchField=3&srchTxt=&srchTxt2="
    return make_url

def title_classification(title, gov, policy_detail_data):
    division            = ""
    classification      = ""
    # providing_agency    = ""
    providing_agency_link=""
    original_text       = ""
    data                = ""
    if title == "구분":
        division = gov[0].get_text()
        division = division.replace(" ","")
        data = division.replace("\n","")
        policy_detail_data["division"] = data
        # print(data)
    elif title == "분류":
        classification = gov[0].get_text()
        classification = classification.replace(" ","")
        data = classification.replace("\n","")
        policy_detail_data["classification"] = data
        # print(data)
    elif title == "제공기관":
        providing_agency = gov[0].get_text()
        providing_agency = providing_agency.replace(" ","")
        providing_agency = providing_agency.replace("\n","")
        providing_agency = providing_agency.replace("\t","")
        policy_detail_data["providing_agency"] = providing_agency
        # print(providing_agency)
        providing_agency_link = gov[0].a['href']
        providing_agency_link = providing_agency_link.replace(" ","")
        data = providing_agency_link.replace("\n","")
        policy_detail_data["detail_link"] = data
        # print(data)
    elif title == "원문출처":
        original_text = gov[0].get_text()
        original_text = original_text.replace(" ","")
        data = original_text.replace("\n","")
        policy_detail_data["original_text"] = data
        # print(data)


policy_index_url = 'https://www.gov.kr/portal/gvrnPolicy?srchOrder=&policyType=G00301&streamYn=&blgCd=&slgCd=&srchBlgCd=&srchSlgCd=&srchOrgGroup=&srchOriginOrg=&srchPeriodOption=1years&srchStDtFmt=2020.02.25&srchEdDtFmt=2021.02.25&searchField=3&srchTxt=&srchTxt2=&pageIndex=1'
total_page = requests.get(policy_index_url)
total_page_num = 0
if total_page.status_code == 200:
    html = total_page.text
    soup = BeautifulSoup(html, 'html.parser')
    page = soup.select_one('div.contentsWrap.policy_cont.renew2019 > div > div > div.tabcontainer.ty2 > div > div > ul > li.active > a > span.dd > strong')
    page = page.get_text()
    page = page.replace(" ","")
    page = page.replace("\n","")
    page = page.replace("(","")
    page = page.replace(")","")
    page = page.replace(",","")
    total_page_num = int(page)
else : 
    print(total_page.status_code)  


policy_list_data = OrderedDict()
policy_list_json = []
page_count = 1 
total_page_num = 30#math.ceil(total_page_num / 10)
print(total_page_num)
while page_count <= total_page_num:
    print(total_page_num)
    policy_count_url = 'https://www.gov.kr/portal/gvrnPolicy?srchOrder=&policyType=G00301&streamYn=&blgCd=&slgCd=&srchBlgCd=&srchSlgCd=&srchOrgGroup=&srchOriginOrg=&srchPeriodOption=1years&srchStDtFmt=2020.02.25&srchEdDtFmt=2021.02.25&searchField=3&srchTxt=&srchTxt2=&pageIndex='+str(total_page_num)
    response = requests.get(policy_count_url)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        ul = soup.select_one('div.contentsWrap.policy_cont.renew2019 > div > div > div.tabcontainer.ty2 > div > ul')
        if ul == None:
            print("continue")
            total_page_num -= 1
            continue
        li = ul.select('li')
        try:
            for li_index in li:
                title_index = li_index.select("div.right_detail > dl > dt > a")
                title_href = title_index[0]['href']
                title = title_index[0].get_text()
                title = title.replace(" ","")
                title = title.replace("\n","")
                date_index = li_index.select("div > div > span:nth-child(2)")
                date_index = date_index[0].get_text()
                policy_list_url = make_policy_url(title_href.split("'")[1])
                policy_list_data = {"url":policy_list_url ,"title":title,"date":date_index}
                policy_list_json.append(policy_list_data)
        except:
            print(li)
        #print(json.dumps(policy_list_json, ensure_ascii=False, indent="\t"))
    else : 
        print(response.status_code)
    total_page_num -= 1
with open('policy_list.json', 'w', encoding='UTF-8-sig') as outfile:
    outfile.write(json.dumps(policy_list_json, ensure_ascii=False))
'''
    정부24 데이터
    No/구분/분류/자료유형/제목/제공기관/원문출처/등록일/원문보기링크/수집일시(크롤링 date)
'''
policy_detail_json = []
data_info  = OrderedDict()
policy_list_count = 1
for policy_list in policy_list_json:
    policy_detail_data = OrderedDict()
    #print(policy_list["date"])
    detail_date = policy_list["date"]
    policy_url_response = requests.get(policy_list["url"])
    if policy_url_response.status_code == 200:
        html = policy_url_response.text
        soup = BeautifulSoup(html, 'html.parser')
        name = soup.select_one('div.contentsWrap.policy_cont > div > div > div.tbl-view.gallery-detail > h2')
        ul = soup.select_one('div.contentsWrap.policy_cont > div > div > div.tbl-view.gallery-detail > div.view-title > ul')
        if ul == None:
            print("continue")
            continue
        li = ul.select('li')
        try:
            policy_detail_data["no"] = policy_list_count
            policy_detail_data["title"] = name.get_text()
            policy_detail_data["date"] = detail_date
            for li_index in li:
                gov    = li_index.select('span.gov')
                titles = li_index.select('span.title_s')
                title  = titles[0].get_text()
                # print(title)
                if gov:
                    title_classification(title, gov, policy_detail_data)
        except:
            print(li)
            continue
        policy_detail_json.append(policy_detail_data)
    else:
        print(response.status_code)
    policy_list_count += 1
policy_detail = json.dumps(policy_detail_json, ensure_ascii=False, indent="\t")
policy_detail = policy_detail.replace("\n",'').replace("\t",'')
#print(json.dumps(policy_detail_json, ensure_ascii=False, indent="\t"))
with open('policy_detail.json', 'w', encoding='UTF-8-sig') as outfile:
    outfile.write(json.dumps(policy_detail, ensure_ascii=False))