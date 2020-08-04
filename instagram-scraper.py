import requests
import time
import os
import sys
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
from urllib.parse import urlparse

instagramPage = sys.argv[1]
directory = f'./download/{instagramPage}'

def main():
    # use webdriver for react app
    url = f'https://www.instagram.com/{instagramPage}/'
    driver = webdriver.Firefox()
    driver.get(url)

    page = BeautifulSoup(driver.page_source, features = "lxml")
    scrollToBottom(driver)
    page = BeautifulSoup(driver.page_source, features = "lxml")

    posts = page.find_all(class_='v1Nh3')    
    posts.reverse()

    for post in posts:
        # open post
        time.sleep(1)
        postUrl = 'https://www.instagram.com/' + post.find('a')['href']
        print(f'Getting post: {postUrl}')
        driver.get(postUrl)
        postPage = BeautifulSoup(driver.page_source, features = "lxml")
        srcUrl = getSourceUrl(postPage)
        downloadFile(srcUrl)


def downloadFile(url):
    filename = os.path.basename(urlparse(url).path)
    if os.path.isfile(f'{directory}/{filename}'):
        return    
    if not os.path.exists(directory):
        print(f'Creating directory.')
        os.makedirs(directory)
    print(f'Saving file: {filename}')
    response = requests.get(url)
    with open(f'{directory}/{filename}', 'wb') as out_file:
        out_file.write(response.content)

def getSourceUrl(postPage):
    srcUrl = ''
    imagePost = postPage.find(class_='KL4Bh')
    if imagePost is not None:
        srcUrl = imagePost.find('img')['src']
    else:
        videoPost = postPage.find(class_='_5wCQW')
        srcUrl = videoPost.find('video')['src']
    return srcUrl

def scrollToBottom(driver):
    # get scroll height
    last_height = driver.execute_script('return document.body.scrollHeight')
    while True:
        print('Scrolling...')
        # scroll to bottom
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        
        # wait for data to load        
        while True:
            time.sleep(1) # loading too fast can cause 429 No Reason Phrase
            # check if spinner is visible to the user
            result = driver.execute_script('''
                var el = document.getElementsByClassName("ZUqME");
                var rect = el[0].getBoundingClientRect();

                return (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && /* or $(window).height() */
                    rect.right <= (window.innerWidth || document.documentElement.clientWidth) /* or $(window).width() */
                );''')
            if not result:
                break

        # get new scroll height. if no change then end of page has been reached
        new_height = driver.execute_script('return document.body.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height

if __name__ == '__main__':
    main()
