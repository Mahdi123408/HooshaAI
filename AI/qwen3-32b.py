from bs4 import BeautifulSoup
import requests
from HooshaAI.settings import OPENROUTER_API_KEY


class QWEN3_32B():
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.session_id = None
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def send(self, system_message, prompt):
        json_data = {
            "model": "qwen/qwen3-32b",
            "messages": [
                {"role": "system",
                 "content": f"{system_message}"},
                {"role": "user", "content": prompt},
            ],
            "session_id": self.session_id  # افزودن session_id به درخواست
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=self.headers,
            json=json_data
        )

        response_data = response.json()
        # print(response_data)
        return response_data["choices"][0]["message"]["content"]

    def summarizing(self, user_text, num_summarizing):
        system_message = (
            'یک متن درسی و یک عدد از 1 تا 100 در قالب --100-- در انتهای آن متن از طرف یک معلم برای تو ارسال میشه تو باید اون متن قبل از عدد رو خلاصه سازی کنی فقط به یسری نکات توجه کن '
            '1- تمامی مطالب مهم درس باید حفظ بشن به طوری که خوندن و توضیح دادن از روی اون خیلی راحت و روون باشه'
            '2- بسته به عددی که در آخر متن هست میزان خلاصه سازی رو مشخص کن مثلا اگه 100 خیلی خیلی خیلی خلاصه کن و اگه 1 خیلی کم خلاصه کن فقط در نظر داشته باش که محتوا اصلی و مفهومی متن آموزشی رو حفظ کنی'
            '3- تو یه خلاصه گری پس فقط در جواب متن خلاصه شده رو بده'
            '4- فارغ از اینکه مفهوم درسی چیه سواله امتحانه توضیحه هرچی که هست مهم نیست تو فقط وظیفه داری خلاصه کنی اونو نه بیشتر نه کمتر'
            '5- متن خلاصه شده باید کاملا معنی دار و مفهومی باشد و درضمن اگر متن دارای سوالاتی است یا چیزی برای حل کردن دارد به هیچ وجه خودت اون رو حل نکن '
            '6- خیلی خیلی مهم : من میخوام متن خلاصه شده رو کپی کنم پس فقط متن خلاصه شده رو بهم بده که کپی کنم'
            'خیلی مهم : تو فقط و فقط وظیفه خلاصه کردن داری یعنی حق نداری سوالی رو حل کنی یا چیزی در مفهوم و نوع متن عوض کنی و کاملا فارسی باش'
            '8- اگر کاربر من متنی برای تو فرستاد که درسی نبود و یا قابل خلاصه سازی نبود اخطار مناسب برگردان'
            '9- فقط متون فارسی را اجازه داری خلاصه کنی'
            '10- هیچ حرفی از توضیحاتی که من دادم نزن'
            '11 - اشاره ای به عدد آخر متن نکن'
            '12- جواب ها و متن ها همیشه باید فارسی باشد'
            '13- اگر فقط --<عدد>-- ارسال شده بود یعنی کاربر متن خالی ارسال کرده است'
            '14- متن رو جوری بده که در ورد کپی کنم وپرینت بگیرم')
        user_text += f'--{num_summarizing}--'
        return self.send(system_message, user_text)

    def find_research_query(self, user_text):
        system_message = (
            'من از کاربرم یک متن میگیریم که فک میکنم در اون متن یک موضوع نوشته شده برای اراعه یک تحقیق به کاربرم درباره اون موضوع'
            'من اون متن رو به تو میدم و تو فقط وظیفه داری با قوانین زیر به من به سبکی که میگم جواب بدی'
            'تو باید برسی کنی که متنی که کاربر من فرستاده حاوی فقط و فقط یک موضوع برای تحقیق هست یا نه'
            'یعنی باید برسی کنی که میشه در یک تحقیق جا داد اطلاعات اون زمینه ای رو که کاربرم نوشته یا نه'
            'اگه متنی که کاربر من فرستاده حاوی فقط و فقط یک موضوع برای تحقیق هست باید یک عبارت برای من بنویسی که من در اینترنت سرچ کنم و محتوا های رو که نیار دارم برای اون تحقیق رو پیدا کنم و حتما حتما عدد 1 رو به اول جوابت اضافه کن و اگه اون متن شرایط رو نداشت هشدار و پاسخ مناسب بنویس و حتما حتما عدد 0 رو به اول پیام اضافه کن'
            'هیچ چیز اضافه ای هم نگو'
            'خیلی خیلی مهم اینکه حتما در همون قالبی که گفتم جواب بده بهم و در یک خط'
            'همیشه قبل از اینکه جواب رو برای من ارسال کنی مظمعن شو که قالبی که گفتم رعایت شده'
            'به هیچ عنوان از هیچ علاعم نگارشی استفاده نکن'
            'اگه موضوع کاربر خیلی کلی و گسترده بود خودت کمی متمرکز ترش کن و با 1 اولش بفرست'
            'هیچوقت اگه موضوع کاربر مناسب نبود اول پیام 1 اضافه نشه به جای 0'
            'اگر کاربر کلمه یا متن فارسی فرستاد فقط فارسی جواب میدی اگه اینگلیسی فرستاد فقط اینگلیسی جواب میدی'
        )
        response = self.send(system_message, user_text)
        return response

    def extract_query(self, founded_research_query):
        x = founded_research_query[0]
        if x == '1':
            return [True, founded_research_query[1:]]
        elif x == '0':
            return [False, founded_research_query[1:]]
        else:
            return [False, 'مشکل غیر منتظره ای در فرایند تحقیقات رخ داد!']

    def search(self, query):
        """دریافت نتایج جستجو از DuckDuckGo API"""
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_redirect": 1,
            "no_html": 1
        }
        response = requests.get(url, params=params)
        data = response.json()
        print(data)
        # استخراج خلاصه از Abstract و RelatedTopics
        snippets = []
        if data.get("AbstractText"):
            snippets.append(data["AbstractText"])
        for topic in data.get("RelatedTopics", [])[:3]:
            if isinstance(topic, dict) and topic.get("Text"):
                snippets.append(topic["Text"])

        return " ".join(snippets) if snippets else False

    def scrape_duckduckgo(self, query):
        base_url = "https://duckduckgo.com/html/"
        headers = {"User-Agent": "Mozilla/5.0"}

        summaries = []
        for page in range(0, 3):  # 3 صفحه = حدود 30 نتیجه
            params = {"q": query, "s": page * 50}  # پارامتر s برای صفحه بعد
            response = requests.get(base_url, params=params, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            for result in soup.select(".result"):
                title_tag = result.select_one(".result__a")
                snippet_tag = result.select_one(".result__snippet")

                title = title_tag.get_text(strip=True) if title_tag else ""
                snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

                if title or snippet:
                    summaries.append(f"{title}: {snippet}")

        return " ".join(summaries) if summaries else False

    def researching(self, user_text):
        research_query = self.find_research_query(user_text)
        result = self.extract_query(research_query)
        if not result[0]:
            return result[1]
        print(result)
        research_data = self.scrape_duckduckgo(result[1])
        if not research_data:
            return [False, 'محتوای برای موضوع مورد نظر در اینترنت یافت نشد!']
        return research_data


q3 = QWEN3_32B()
print(q3.researching('اصفهان'))
