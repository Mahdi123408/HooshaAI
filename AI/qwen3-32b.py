from bs4 import BeautifulSoup
import requests
from HooshaAI.settings import COHERE_API_KEY
import cohere


class Command:
    def __init__(self):
        self.api_key = COHERE_API_KEY
        self.session_id = None
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.co = cohere.ClientV2(self.api_key)
        self.co1 = cohere.Client(COHERE_API_KEY)

    # def send(self, system_message, user_prompt):
    #     json_data = {
    #         "model": "qwen/qwen3-32b",
    #         "messages": [
    #             {"role": "system",
    #              "content": f"{system_message}"},
    #             {"role": "user", "content": user_prompt},
    #         ],
    #         "session_id": self.session_id  # افزودن session_id به درخواست
    #     }
    #
    #     response = requests.post(
    #         "https://openrouter.ai/api/v1/chat/completions",
    #         headers=self.headers,
    #         json=json_data
    #     )
    #
    #     response_data = response.json()
    #     return response_data["choices"][0]["message"]["content"]

    # def send(self, system_message, user_prompt):
    #     API_URL = "https://api.cohere.com/v1/chat"
    #     headers = {
    #         "Content-Type": "application/json",
    #         "Authorization": f"Bearer {COHERE_API_KEY}"
    #     }
    #
    #     data = {
    #         "model": "command-r-plus",
    #         "messages": [
    #             {"role": "system", "content": [{"type": "text", "text": system_message}]},
    #             {"role": "user", "content": [{"type": "text", "text": user_prompt}]},
    #         ],
    #         "max_tokens": 6000,
    #         "temperature": 0.7
    #     }
    #
    #     response = requests.post(API_URL, headers=headers, json=data)
    #     print(response.json())
    #     return response.json()["choices"][0]["message"]["content"]

    def send(self, system_message, user_prompt):

        response = self.co.chat(
            model="command-a-03-2025",
            messages=[{"role": "system", "content": system_message}, {"role": "user", "content": user_prompt}]
        )
        return response.message.content[0].text

    def summarizing(self, user_text, num_summarizing):
        system_message = """You will receive an educational text followed by a number between 1 and 100 in the format --number-- at the end of the text. Your task is to summarize the text before the number. Follow these rules carefully:

1. If the text is in Persian, output the summary in Persian. If the text is in English, output the summary in English.
2. Preserve all important and conceptual points so the summarized text remains clear and easy to understand.
3. The number at the end determines the summarization level:
   - 1 means minimal summarization, keep about 80% to 100% of the original length.
   - 100 means maximum summarization, keep about 10% to 20% of the original length.
In all cases, keep the core meaning.
4. Return only the summarized text with no extra explanations or comments.
5. The type of text does not matter (lesson, question, explanation, etc.); just summarize it.
6. If the text contains questions or exercises, do NOT solve them. Just keep them in the summary.
7. The summarized text must be meaningful, coherent, and well-structured.
8. The output must be clean for copying (no extra symbols, no markdown, no formatting).
9. If the input text is not educational or cannot be summarized, return an appropriate warning message.
10. Only summarize texts in Persian or English. If the text is in any other language, return a warning.
11. Do NOT mention the number at the end of the text in your response.
12. If only the number is sent without any text, return a warning that the input text is empty.\n
"""
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
        for page in range(0, 5):  # 3 صفحه = حدود 30 نتیجه
            params = {"q": query, "s": page * 70}  # پارامتر s برای صفحه بعد
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

    def count_words(self, text):
        if not text:
            return 0
        words = text.strip().split()
        return len(words)

    def research_in_internet(self, user_text):
        research_query = self.find_research_query(user_text)
        print(research_query)
        result = self.extract_query(research_query)
        if not result[0]:
            return [False, result[1]]
        print(result)
        research_data = self.scrape_duckduckgo(result[1])
        if not research_data:
            return [False, 'محتوای برای موضوع مورد نظر در اینترنت یافت نشد!']
        return [True, research_data]

    def researching(self, user_text):
        research_data = self.research_in_internet(user_text)
        if not research_data[0]:
            return [False, research_data[1]]

        prompt = f"""You will receive a raw extracted text from the web. Your task is to rewrite and organize it into a comprehensive, well-structured academic research article following these rules:

1. First, detect the language of the input text (only English or Persian).
2. If the text is in Persian, write the article in Persian. If the text is in English, write it in English.
3. Do not mention the detected language and do not include any explanations about what you did.
4. The output must only contain the research article, starting with a proper title.
5. The article must have a clear academic structure: Title, Introduction, multiple main sections with detailed headings and subheadings, and a Conclusion.
6. Do NOT use any extra symbols such as #, *, :, or markdown formatting.
7. The article MUST be at least the same length as the input text and preferably much longer. If the input is short, expand it significantly by adding clarifications, historical context, botanical characteristics, cultural background, medical uses, and modern scientific insights using the same information from the original text.
8. The final article MUST be a minimum of {self.count_words(research_data[1]) - 100} words (or as close as possible if the input is very short).
9. All sentences must be grammatically correct, formal, and coherent. Fix incomplete or broken sentences and remove any meaningless phrases.
10. Do not add personal opinions or fabricated information beyond what is necessary for elaboration. Use the given data and general accepted scientific or historical context if needed.
11. In Persian output, do not use any English words or foreign terms. In English output, write in clear academic English.
12. Ensure the article uses approximately 70% or more of the original word count from the input and significantly expands it if necessary.
13. Include detailed sections such as: Description of the plant, Morphological characteristics, Medicinal properties in traditional medicine, Active chemical compounds, Modern pharmacological applications, Methods of use, Dosage, Safety and precautions, Historical and cultural significance.
14. Do NOT summarize or compress the text. Elaborate on every concept as much as possible.
15. The final text must resemble a formal academic research paper or an extended educational article.

Input text:
{research_data[1]}
"""

        response = self.co1.generate(
            model="command-r-plus",
            prompt=prompt,
            max_tokens=6000,
            temperature=0.7
        )
        return response.generations[0].text


qo = Command()
