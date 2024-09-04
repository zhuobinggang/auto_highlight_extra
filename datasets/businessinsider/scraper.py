home_to_get_art_links = 'https://www.businessinsider.jp/business/'
home = 'https://www.businessinsider.jp'
import scrapy
global_response = None

def filter_cards(response):
    cards = response.css('div.p-cardList-card')
    available_cards = []
    for card in cards:
        if card.css('a.p-label-primeLabelInner::text').get() is not None: # 是prime
            continue
        if '［編集部］' not in ' '.join(card.css('li.p-cardList-cardAuthor::text').getall()): # 是prime
            continue
        available_cards.append(card)
    return available_cards
    
def links_from_cards(cards):
    links = []
    for card in cards:
        links.append(card.css('h1.p-cardList-cardTitle a::attr(href)').get())
    return links

def links_add_prefix(links):
    global home
    return [home+link for link in links]
    
def get_article_links(response):
    return links_add_prefix(links_from_cards(filter_cards(response)))
    
# ==================== END =====================

fake_art_link = 'https://www.businessinsider.jp/post-292754'

def get_title(response):
    return response.css('li.f-breadcrumb-current::text').get()

def get_date(response):
    return response.css('ul.p-post-bylineInfo li.p-post-bylineDate::text').get()

def get_author(response):
    return response.css('ul.p-post-bylineInfo a::text').get()

def get_category(response):
    return response.css('ul.p-post-bylineInfo span.p-post-bylineCategory a::text').get()

# 获取文章的正文
def get_content(response):
    content = []
    # 提取所有blockquote和p标签
    elements = response.css('div.p-post-content>div>blockquote, div.p-post-content>div>p')
    for element in elements:
        # 提取每个元素中的所有文本，包括strong标签
        content.append(''.join(element.css('::text, strong::text').getall()))
    return ' '.join(content)  # 将所有内容连接成一个字符串

def get_tokenizer():
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained("rinna/japanese-roberta-base", use_fast=False)

# 获取文章的正文
def get_content(tokenizer, response):
    tokens = []
    labels = []
    # 提取所有blockquote和p标签
    elements = response.css('div.p-post-content>div>blockquote, div.p-post-content>div>p')
    for element in elements:
        # 提取文本和strong标签
        strong_texts = element.css('strong::text')
        normal_texts = element.css('::text')
        strong_mixed = element.css('::text, strong::text')
        for text in strong_mixed:
            # 分词
            tokens = tokenizer.tokenize(text.get())
            # 根据文本是否为strong标签分配标签
            if text in strong_texts:  # 检查是否为强调文本
                labels += [1] * len(tokens)  # 强调
            else:
                labels += [0] * len(tokens)  # 非强调
            tokens.extend(tokens)  # 添加tokens
    return tokens, labels  # 返回tokens和对应的标签