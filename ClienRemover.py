#ClienRemover.py
#0.1.0: 2017.11.11
#0.2.0: 2018.08.23
import requests
from bs4 import BeautifulSoup as bs

#user information
user_info = {
    'userId': 'your id',#클리앙 아이디 입력
    'userPassword': 'your pw'#클리앙 비밀번호 입력
}

# urls
main_url = 'https://www.clien.net'
login_url = 'https://www.clien.net/service/login'
article_list_url = 'https://www.clien.net/service/mypage/myArticle?&type=articles&po='
comment_list_url = 'https://www.clien.net/service/mypage/myArticle?&type=comments&po='

api = 'https://www.clien.net/service/api'
comment_list_url_param = '/comment?order=date&po=0&ps=10000&writer=prosumer'

# message
m_progress_list = '번째 리스트를 확인중입니다.'
m_program_exit = '==프로그램이 종료되었습니다.=='


# functions
def set_csrf(page, param):
    html = page.text
    soup = bs(html, 'html.parser')
    csrf = soup.find('input', {'name': '_csrf'})
    return {**param, **{'_csrf': csrf['value']}}


def check_end(page):
    soup = bs(page.text, 'html.parser')
    # print(soup)
    if soup.find('div', {'class': 'list_empty'}):
        return False
    return True


# main
with requests.Session() as s:
    # login
    main_page = s.get(main_url)
    user_info = set_csrf(main_page, user_info)

    # request login
    login_req = s.post(login_url, data=user_info)

    # remove comment
    list_no = 0
    while True:
        list_url = comment_list_url + str(list_no)
        list_no += 1

        # check end list
        list_page = s.get(list_url)
        if not check_end(list_page):
            break

        print(str(list_no) + m_progress_list)

        soup = bs(list_page.text, 'html.parser')
        title = soup.select('div.list_title > a')
        for t in title:

            # get comment list on article
            article_url = main_url + t.get('href')
            comment_url = article_url + comment_list_url_param
            comment_delete_api = api + t.get('href')[8:] + '/comment/delete/'
            article_comment_list = s.get(comment_url)
            soup = bs(article_comment_list.text,'html.parser')
            my_comment_list = soup.find_all('div',{'class':'by-me'})

            n = len(my_comment_list)

            for i in my_comment_list:
                commentSn = i.get('data-comment-sn')
                article_page = s.get(article_url)

                # request server to remove comment
                if article_page.status_code == 200: # for non-deleted articles only
                    print(commentSn)
                    remove_req = s.post(comment_delete_api + str(commentSn), data=set_csrf(article_page, {}))

    # remove article
    list_no = 0
    while True:
        list_url = article_list_url + str(list_no)
        list_no += 1

        # check end list
        list_page = s.get(list_url)
        if not check_end(list_page):
            break

        print(str(list_no) + m_progress_list)

        soup = bs(list_page.text, 'html.parser')
        title = soup.select('div.list_title > a.list_subject')
        for t in title:

            # connect to article
            article_url = main_url + t.get('href')
            article_delete_api = api + '/board/' + t.get('href').split('/')[-2] + '/delete'
            article_page = s.get(article_url)

            if article_page.status_code == 200:
                remove_article = {
                    'boardSn': t.get('href').split('/')[-1]
                }
                remove_article = set_csrf(article_page, remove_article)

                print(t.get('href').split('/')[-1])

                # request server to remove article
                remove_req = s.post(article_delete_api, data=remove_article)

# exit
print(m_program_exit)