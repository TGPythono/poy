from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from time import sleep
from datetime import datetime
import random

# جمع البيانات من المستخدم
fb_email = input("اكتب إيميلك أو رقمك على فيسبوك: ")
fb_pass = input("اكتب كلمة السر: ")
short_link = input("اكتب الرابط المختصر الي تريد تنشره: ")
max_groups = int(input("كم عدد الكروبات؟ "))
max_comments = int(input("كم تعليق لكل كروب؟ "))
message_type = input("شنو نوع الرسالة؟ (مثلاً: معلومات انستا): ")

# إعدادات
groups_per_batch = 10
comments_per_batch = max_comments
sleep_between_batches = 3600  # استراحة ساعة

comment_templates = [
    f"ما توقعت هذا الشي أبد! شوف بنفسك: {short_link}",
    f"شفت هذا الرابط وصدگ صدمت، جربه: {short_link}",
    f"ما أگدر أشرح، الرابط يوضحلك: {short_link}",
    f"ضروري الكل يشوف هذا الشي: {short_link}"
]

# إعداد المتصفح
options = Options()
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(options=options)

# تسجيل دخول
driver.get("https://www.facebook.com")
sleep(3)
driver.find_element(By.ID, "email").send_keys(fb_email)
driver.find_element(By.ID, "pass").send_keys(fb_pass)
driver.find_element(By.NAME, "login").click()
sleep(5)

# البحث عن كروبات
driver.get("https://www.facebook.com/search/groups/?q=")
sleep(5)
groups = driver.find_elements(By.XPATH, "//a[contains(@href, '/groups/') and contains(@href, 'public')]")

visited = set()
count = 0

while count < max_groups:
    print(f"[{datetime.now()}] بدء دفعة جديدة...")
    batch_groups = 0
    for group in groups:
        group_link = group.get_attribute("href")
        if group_link and group_link not in visited and count < max_groups:
            visited.add(group_link)
            driver.get(group_link)
            sleep(random.randint(7, 12))
            print(f"[+] دخل الكروب: {group_link}")

            posts = driver.find_elements(By.XPATH, "//div[@aria-posinset]")
            commented = 0
            for post in posts:
                try:
                    comment_area = post.find_element(By.XPATH, ".//div[contains(@aria-label, 'اكتب تعليقًا') or contains(@aria-label, 'Write a comment')]")
                    comment_area.click()
                    sleep(1)
                    text = random.choice(comment_templates)
                    comment_area.send_keys(text)
                    comment_area.send_keys(Keys.RETURN)
                    sleep(random.randint(7, 10))

                    post_link_el = post.find_element(By.XPATH, ".//a[contains(@href, '/posts/')]")
                    post_link = post_link_el.get_attribute("href")
                    print(f"[✓] تم نشر تعليق في: {post_link}")
                    commented += 1
                    if commented >= comments_per_batch:
                        break
                except Exception as e:
                    continue
            count += 1
            batch_groups += 1
            if batch_groups >= groups_per_batch:
                break
    if count < max_groups:
        print(f"[{datetime.now()}] استراحة لمدة ساعة...")
        sleep(sleep_between_batches)

print("[✓] انتهى النشر بكل الدُفعات!")
driver.quit()
