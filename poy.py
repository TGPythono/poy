import telebot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import random
from time import sleep

# إعدادات بوت تيليجرام
API_TOKEN = '8101669595:AAHBQ6k-n_OzjBhdvwPr99SIXSu3qQQaiWE'
bot = telebot.TeleBot(API_TOKEN)

#====== مراحل المحادثة ======
FB_EMAIL, FB_PASS, SHORT_LINK, MAX_GROUPS, MAX_COMMENTS, MESSAGE_TYPE = range(6)

#====== متغيرات مؤقتة ======
user_data = {}

#====== بدء المحادثة ======
@bot.message_handler(commands=['start'])
def start(update):
    bot.send_message(update.chat.id, "هلا سيد! خل نبدي بجمع معلوماتك. شنو إيميلك أو رقمك على فيسبوك؟")
    bot.register_next_step_handler(update, get_email)

def get_email(message):
    user_data['fb_email'] = message.text
    bot.send_message(message.chat.id, "تمام، هسه شنو كلمة المرور؟")
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    user_data['fb_pass'] = message.text
    bot.send_message(message.chat.id, "ارسلي الكلام الي تريد تنشرة.")
    bot.register_next_step_handler(message, get_link)

def get_link(message):
    user_data['short_link'] = message.text
    bot.send_message(message.chat.id, "كم كروب تريده يدخل؟")
    bot.register_next_step_handler(message, get_groups)

def get_groups(message):
    user_data['max_groups'] = int(message.text)
    bot.send_message(message.chat.id, "وكم تعليق تريده ينشر؟")
    bot.register_next_step_handler(message, get_comments)

def get_comments(message):
    user_data['max_comments'] = int(message.text)
    bot.send_message(message.chat.id, "أخيراً، شنو نوع الرسالة؟ (مثلاً: معلومات انستا)")
    bot.register_next_step_handler(message, get_message_type)

def get_message_type(message):
    user_data['message_type'] = message.text
    bot.send_message(message.chat.id, "بديت التنفيذ، انتظر...")
    run_bot()
    bot.send_message(message.chat.id, "خلص البوت نشر بكل الكروبات!")

#====== تنفيذ البوت بسيلينيوم ======
def run_bot():
    fb_email = user_data['fb_email']
    fb_pass = user_data['fb_pass']
    short_link = user_data['short_link']
    max_groups = user_data['max_groups']
    max_comments = user_data['max_comments']

    comment_templates = [
        f"ما توقعت هذا الشي أبد! شوف بنفسك: {short_link}",
        f"شفت هذا الرابط وصدگ صدمت، جربه: {short_link}",
        f"ما أگدر أشرح، الرابط يوضحلك: {short_link}",
        f"ضروري الكل يشوف هذا الشي: {short_link}"
    ]

    options = Options()
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.facebook.com")
    sleep(3)

    driver.find_element(By.ID, "email").send_keys(fb_email)
    driver.find_element(By.ID, "pass").send_keys(fb_pass)
    driver.find_element(By.NAME, "login").click()
    sleep(5)

    driver.get("https://www.facebook.com/search/groups/?q=")
    sleep(5)
    groups = driver.find_elements(By.XPATH, "//a[contains(@href, '/groups/') and contains(@href, 'public')]")

    visited = set()
    count = 0

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
                    print(f"[+] تم النشر في {group_link} - رابط المنشور: {post_link}")
                    commented += 1
                    if commented >= max_comments:
                        break
                except Exception as e:
                    continue
            count += 1

    print("[✓] انتهى النشر بنجاح!")
    driver.quit()

# تشغيل البوت
bot.polling(none_stop=True)