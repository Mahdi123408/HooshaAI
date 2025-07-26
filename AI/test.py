import requests


class QWEN2_7B_INSTRUCT:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session_id = None  # برای مدیریت مکالمه طولانی

    def ask_openrouter(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        json_data = {
            "model": "qwen/qwen3-32b:free",
            "messages": [
                {"role": "system",
                 "content": "تو فقط و فقط وظیفه داری که متنی که کاربر برای من فرستاده رو من برای تو میفرستم و تو باید به من بگی که آیا کاربر میخواد تاریخ دقیق (امروز) فقط و فقط امروز و حال حاضر رو به طور کلی رو بدونه یا نه جوابت فقط و فقط باید True , False باشه"},
                {"role": "user", "content": prompt},
            ],
            "session_id": self.session_id  # افزودن session_id به درخواست
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=json_data
        )

        response_data = response.json()
        print(response_data)

        # ذخیره session_id برای ادامه مکالمه
        if 'session_id' in response_data:
            self.session_id = response_data['session_id']

        return response_data["choices"][0]["message"]["content"]


# نمونه استفاده
if __name__ == "__main__":
    # کلید API را جایگزین کنید (بهتره از محیطی استفاده بشه)
    API_KEY = "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"

    ai = QWEN2_7B_INSTRUCT(API_KEY)

    # گفتگوی چند مرحله‌ای
    print("پاسخ 1:", ai.ask_openrouter('سلام امروز چندمه؟'))
    print("پاسخ 2:", ai.ask_openrouter('ممنون! حالا ساعت چنده؟'))
    print("پاسخ 3:", ai.ask_openrouter('آیا فردا تعطیله؟'))