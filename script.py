import feedparser
import hashlib
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree

def get_date(entry):
    if hasattr(entry, "published"):
        return entry.published
    elif hasattr(entry, "updated"):
        return entry.updated
    elif "dc_date" in entry:  # feedparserがRDFのdc:dateを拾う場合あり
        return entry.dc_date
    else:
        return None
        
def generate_rss(feeds, output="index.xml"):
    seen = set()
    items = []

    # 各フィードを取得
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # タイトル+リンクで重複判定
            uid = hashlib.md5((entry.title + entry.link).encode()).hexdigest()
            if uid in seen:
                continue
            seen.add(uid)
            date = get_date(entry) or datetime.utcnow().isoformat()
            items.append({
                "title": entry.title,
                "link": entry.link,
                "published": date
            })
            
    # 新しい順にソート
    items.sort(key=lambda x: x["published"], reverse=True)

    # RSS生成
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = "Custom Aggregated Feed"
    SubElement(channel, "link").text = "https://un-inc.github.io/merged-rss/"
    SubElement(channel, "description").text = "Merged feed without duplicates"
    SubElement(channel, "lastBuildDate").text = datetime.utcnow().isoformat()

    for item in items[:50]:  # 最新50件まで
        entry = SubElement(channel, "item")
        SubElement(entry, "title").text = item["title"]
        SubElement(entry, "link").text = item["link"]
        SubElement(entry, "pubDate").text = item["published"]

    ElementTree(rss).write(output, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    with open("feeds.txt") as f:
        feeds = [line.strip() for line in f if line.strip()]
    generate_rss(feeds)
