import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# 스타일별 룩핀 URL
style_to_url = {
    "스트릿": "https://www.lookpin.co.kr/coordi?style=%EC%8A%A4%ED%8A%B8%EB%A6%BF&storeId=0&sort=trending&styleIds=2&page=1&size=24"
}

# 코디 카드 1개 크롤링
def get_single_coordi(style_url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.get(style_url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    first_card = soup.select_one("a[href^='/coordi/']")
    img = first_card.select_one("img")
    title = img.get("alt", "코디")
    image_url = img.get("src")
    detail_url = "https://www.lookpin.co.kr" + first_card.get("href")

    driver.quit()
    return {"title": title, "image_url": image_url, "detail_url": detail_url}

# 카테고리 분류 키워드
def classify_category(name):
    name = name.lower()
    if any(k in name for k in ["셔츠", "티셔츠", "니트", "아우터", "자켓", "후드"]):
        return "상의"
    elif any(k in name for k in ["팬츠", "바지", "데님", "슬랙스"]):
        return "하의"
    elif any(k in name for k in ["신발", "운동화", "스니커즈", "부츠"]):
        return "신발"
    else:
        return None

# 코디 상세페이지에서 상의/하의/신발 자동 추출
def get_items(detail_url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.get(detail_url)
    time.sleep(4)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cards = soup.select('div.sc-dAlyuH')  # 상품 카드

    categories = {"상의": None, "하의": None, "신발": None}
    for card in cards:
        name_tag = card.select_one(".brand-name")
        price = card.select_one(".price")
        img = card.select_one("img")
        link = card.select_one("a")

        if name_tag and img and link:
            name = name_tag.text.strip()
            cat = classify_category(name)
            if cat and categories[cat] is None:
                categories[cat] = {
                    'name': name,
                    'price': price.text.strip() if price else '-',
                    'image': img.get("src"),
                    'link': link.get("href")
                }

    driver.quit()
    return categories

# Streamlit 화면
st.title("👕 룩핀 코디 기반 착장 1세트 추천")
style = st.selectbox("스타일 선택", list(style_to_url.keys()))

if st.button("코디 추천 받기"):
    with st.spinner("코디 불러오는 중..."):
        coordi = get_single_coordi(style_to_url[style])
        items = get_items(coordi['detail_url'])

    # 2열 구성
    left, right = st.columns([1, 1.2])

    with left:
        st.image(coordi['image_url'], caption=coordi['title'], use_container_width=True)

    with right:
        st.markdown("### 👔 착용 아이템")
        for part in ["상의", "하의", "신발"]:
            info = items.get(part)
            if info:
                st.image(info['image'], width=120)
                st.markdown(f"[{info['name']}]({info['link']})")
                st.markdown(f"💰 {info['price']}")
                st.markdown("---")