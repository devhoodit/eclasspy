import re
import requests
from bs4 import BeautifulSoup as bs
import os
from urllib.parse import urlparse, parse_qs

class client:
    
    def __init__(self, id: str, password: str):
        self._sessionId = ""
        self.login(id, password)
    
    @property
    def session(self):
        return self._sessionId
    
    def login(self, id: str, password: str) -> int:
        self.id = id
        
        header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br"
        }
        
        data = requests.post("https://eclass.seoultech.ac.kr/ilos/lo/login.acl?returnURL=&usr_id={id}&usr_pwd={password}".format(
            id=id,
            password=password
            ), headers=header)
        
        if len(data.cookies) < 2:
            return 503
        else:
            self._sessionId = data.cookies['LMS_SESSIONID']
            self.wmonId = data.cookies['WMONID']
            return 200
    
    def get_subjects(self) -> list:
        if self._sessionId == "":
            return [400]
        else:
            header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br"
            }
            
            #except useless google assistance cookies
            cookie = {
                "_language_": "ko",
                "WMONID": self.wmonId,
                "LMS_SESSIONID": self._sessionId
            }
            
            data = requests.get("https://eclass.seoultech.ac.kr/ilos/main/main_form.acl", headers=header, cookies=cookie)
            soup = bs(data.text, 'html.parser')
            raw_subject = soup.select(".sub_open")
            subject_list = []
            for index in raw_subject:
                inner_text = index.get_text()
                subject_list.append(inner_text.strip().replace(" ", "").split() + [index["kj"]])
            #subject_name, subject_id, subject_ky
            return subject_list

    def get_all_attend(self) -> list:
        if self._sessionId == "":
            return [400]
        else:
            attend_list = []
            subject_list = self.get_subjects()
            
            cookie = {
                "_language_": "ko",
                "WMONID": self.wmonId,
                "LMS_SESSIONID": self._sessionId
            }
            
            for subejct_name, subject_id, subject_ky in subject_list:
                with requests.session() as s:
                    
                    payload = {
                        "KJKEY": subject_ky
                    }
                    
                    s.post("https://eclass.seoultech.ac.kr/ilos/st/course/eclass_room_submain.acl", cookies=cookie, data=payload)
                    
                    payload = {
                        "returnData": "json",
                        "kj": subject_ky,
                        "encoding": "utf-8"
                    }
                    
                    data = s.post("https://eclass.seoultech.ac.kr/ilos/st/course/attendance_list.acl?ud={userId}&ky={ky}&encoding=utf-8".format(
                        userId=self.id,
                        ky=subject_ky), cookies=cookie)
                    soup = bs(data.text, 'html.parser')
                    raw_attend = soup.select(".attend_box_1")
                    attend = [x.get_text().replace(" ", "").split() for x in raw_attend]
                    attend_list.append([subejct_name, subject_id, attend])
            
            return attend_list
    
    def get_assignment(self, ky, session=requests.session()) -> list:
        if self._sessionId == "":
            return [400]
        else:
            
            cookie = {
                "_language_": "ko",
                "WMONID": self.wmonId,
                "LMS_SESSIONID": self._sessionId
            }
            
            payload = {
                "KJKEY": ky
            }
               
            session.post("https://eclass.seoultech.ac.kr/ilos/st/course/eclass_room_submain.acl", cookies=cookie, data=payload)
            data = session.post("https://eclass.seoultech.ac.kr/ilos/st/course/report_list.acl?start=&display=1&SCH_VALUE=&ud={userId}&ky={ky}&encoding=utf-8".format(
                userId=self.id,
                ky=ky), cookies=cookie)
            
            soup = bs(data.text, 'html.parser')
            data = soup.find_all('tr')[1:]
            assignment_list = []
            
            for index in data:
                soup = bs(str(index), 'html.parser')
                td = soup.find_all('td')
                if len(td) == 1:
                    return []
                id = td[0].get_text().replace(" ","").replace("\r\n", "")
                title = td[2].select('.subjt_top')[0].get_text()
                progress = td[3].get_text().replace(" ","").replace("\r\n", "")
                submit = td[4].select('img')[0]['title']
                score = td[5].get_text().replace(" ","").replace("\r\n", "")
                points = td[6].get_text().replace(" ","").replace("\r\n", "")
                date = td[7].get_text().replace(" ","").replace("\r\n", "")
                assignment_list.append([id, title, progress, submit, score, points, date])
            
            return assignment_list
    
    def get_all_assignment(self) -> list:
        if self._sessionId == "":
            return [400]
        else:
            assign_list = []
            subject_list = self.get_subjects()
            
            for subject_name, subject_id, subject_ky in subject_list:
                with requests.session() as s:
                    data = self.get_assignment(subject_ky, s)
                    assign_list.append([subject_name, subject_id ,data])
            
            return assign_list
    
    def get_notice(self, ky, session=requests.session()) -> list:
        if self._sessionId == "":
            return [400]
        else:
            
            cookie = {
                "_language_": "ko",
                "WMONID": self.wmonId,
                "LMS_SESSIONID": self._sessionId
            }
            
            payload = {
                "KJKEY": ky
            }
            
            session.post("https://eclass.seoultech.ac.kr/ilos/st/course/eclass_room_submain.acl", cookies=cookie, data=payload)
            data = session.post("https://eclass.seoultech.ac.kr/ilos/st/course/notice_list.acl?start=&display=1&SCH_VALUE=&ud={userId}&ky={ky}&encoding=utf-8".format(
                userId=self.id,
                ky=ky), cookies=cookie)
            soup = bs(data.text, 'html.parser')
            
            p = re.compile("[0-9]+")
            
            notice_list = []
            
            for index in soup.find_all("tr")[1:]:
                td = index.find_all('td')
                if len(td) == 1:
                    continue
                div = td[2].find_all('div')
                span = div[1].find_all('span')
                title = div[0].get_text()
                writer = span[0].get_text()
                view = int(p.search(span[1].get_text()).group())
                link =  'https://eclass.seoultech.ac.kr' + str(td[2]['onclick'].split("'")[1::2][0])
                notice_list.append([title, writer, view, link])
            
            return notice_list
        
    def get_all_notice(self) -> list:
        if self._sessionId == "":
            return [400]
        else:
            notice_list = []
            subject_list = self.get_subjects()
            
            for subject_name, subject_id, subject_ky in subject_list:
                with requests.session() as s:
                    data = self.get_notice(subject_ky, s)
                    notice_list.append([subject_name, subject_id, data])
            
            return notice_list

    def get_lecture_materials(self, ky, display=1) -> list:
        """get_lecture_materials(self, ky, display=1)

        Args:
            ky (str): subject_ky
            display (int, optional): display. Defaults to 1.

        Returns:
            list: [title, [filename, attachment download link]]
        """

        header = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
            "Content-Type":	"application/x-www-form-urlencoded",
            "X-Requested-With":	"XMLHttpRequest",
            "Host": "eclass.seoultech.ac.kr",
            "Origin": "https://eclass.seoultech.ac.kr",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }

        cookie = {
            "_language_": "ko",
            "WMONID": self.wmonId,
            "LMS_SESSIONID": self._sessionId
        }

        with requests.session() as s:
            payload = {
                "KJKEY": ky
            }

            s.post("https://eclass.seoultech.ac.kr/ilos/st/course/eclass_room_submain.acl", headers=header, cookies=cookie, data=payload)

            payload = {
                "start": "",
                "display": display,
                "SCH_VALUE": "",
                "ud": self.id,
                "ky": ky,
                "encoding": "utf-8"
            }
            
            data = s.post("https://eclass.seoultech.ac.kr/ilos/st/course/lecture_material_list.acl", headers=header, cookies=cookie, data=payload)

            soup = bs(data.text, 'html.parser')
            data = soup.find_all('tr')[1:]

            a= 1
            file_name = []
            for index in data:
                idxfall = index.find_all('td')
                if len(idxfall) < 3:
                    continue
                td = idxfall[2]
                title = td.select(".subjt_top")[0].get_text()
                link = "https://eclass.seoultech.ac.kr" + td['onclick'].split("'")[1::2][0]
                data = s.get(link, cookies=cookie)
                soup = bs(data.text, 'html.parser')
                data = soup.find_all("script")[18].get_text().split('"')
                pf_st_flag, content_seq = data[9], data[11]

                payload = {
                    "ud": self.id,
                    "ky": ky,
                    "pf_st_flag": pf_st_flag,
                    "CONTENT_SEQ": content_seq,
                    "encoding": "utf-8"
                }

                data = s.post("https://eclass.seoultech.ac.kr/ilos/co/efile_list.acl", cookies=cookie, headers=header, data=payload)
                soup = bs(data.text, 'html.parser')
                data = soup.find_all("a")

                tmp = []
                for raw_link in data:
                    dw_link = raw_link["href"].replace('amp;', '')
                    res = s.get("https://eclass.seoultech.ac.kr" + dw_link, cookies=cookie)
                    res.headers["Content-Disposition"]
                    tmp.append({
                        "name": requests.utils.unquote(res.headers["Content-Disposition"].split(";")[1].split("=")[1]),
                        "link": dw_link
                    })
                    
                
                file_name.append([title, tmp])

            return file_name
    
    def download_lecture_material(self, basepath, subject_id) -> None:
        cookie = {
            "_language_": "ko",
            "WMONID": self.wmonId,
            "LMS_SESSIONID": self._sessionId
        }
        lecture_material_info = self.get_lecture_materials(subject_id)
        if lecture_material_info:
            for index in lecture_material_info:
                title = index[0]
                title = title.replace(":", "")
                lecture_path = os.path.join(basepath, title)
                if not os.path.exists(lecture_path):
                    os.makedirs(lecture_path)
                for info in index[1]:
                    file_name = info["name"]
                    file_link = info["link"]
                    with requests.get("https://eclass.seoultech.ac.kr" + file_link, stream=True, cookies=cookie) as r:
                        r.raise_for_status()
                        with open(os.path.join(lecture_path, file_name), "wb") as f:
                            for chunk in r.iter_content(chunk_size=1024):
                                f.write(chunk)
                
    def download_all_lecture_materials(self, base_path="./"):
        subject_list = self.get_subjects()
        for name, id, subject_id in subject_list:
            tmp_path = os.path.join(base_path, name)
            if not os.path.exists(tmp_path):
                os.makedirs(tmp_path)
            self.download_lecture_material(tmp_path, subject_id)
    
    def download_lecture_material_link(self, path: str, link: str) -> None:
        header = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
            "Content-Type":	"application/x-www-form-urlencoded",
            "X-Requested-With":	"XMLHttpRequest",
            "Host": "eclass.seoultech.ac.kr",
            "Origin": "https://eclass.seoultech.ac.kr",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }

        cookie = {
            "_language_": "ko",
            "WMONID": self.wmonId,
            "LMS_SESSIONID": self._sessionId
        }
        
        ky = parse_qs(urlparse(link).query)['ky'][0]
        
        payload = {
            "KJKEY": ky
        }

        requests.post("https://eclass.seoultech.ac.kr/ilos/st/course/eclass_room_submain.acl", headers=header, cookies=cookie, data=payload)
        
        with requests.get(link, stream=True, cookies=cookie) as r:
            r.raise_for_status()
            with open(path, "wb") as wf:
                for chunk in r.iter_content(chunk_size=1024):
                    wf.write(chunk)
        
