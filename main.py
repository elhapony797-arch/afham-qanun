
# -*- coding: utf-8 -*-
import os
import sqlite3

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

# دعم الكتابة العربية
try:
    import arabic_reshaper
    from bidi.algorithm import get_display

    def arabic(text):
        return get_display(arabic_reshaper.reshape(str(text)))
except ImportError:
    def arabic(text):
        return str(text)


Window.clearcolor = (0.94, 0.96, 0.98, 1)


class AfhamQanun(App):

    def build(self):
        self.title = "افهم قانون مع المستشارة أسماء مزنان"

        self.db_path = os.path.join(
            self.user_data_dir, "law_database.db"
        )
        self.create_database()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(9)
        )

        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(105),
            spacing=dp(5)
        )

        header.add_widget(Label(
            text=arabic("افهم قانون"),
            font_size=dp(29),
            bold=True,
            color=(0.05, 0.20, 0.38, 1)
        ))

        header.add_widget(Label(
            text=arabic("مع المستشارة أسماء مزنان"),
            font_size=dp(18),
            color=(0.15, 0.25, 0.35, 1)
        ))

        root.add_widget(header)

        self.search = TextInput(
            hint_text=arabic("ابحث عن قانون أو مادة أو موضوع..."),
            multiline=False,
            size_hint_y=None,
            height=dp(52),
            font_size=dp(16)
        )
        root.add_widget(self.search)

        search_button = Button(
            text=arabic("بحث في المكتبة القانونية"),
            size_hint_y=None,
            height=dp(48),
            background_color=(0.08, 0.30, 0.52, 1)
        )
        search_button.bind(on_press=self.search_law)
        root.add_widget(search_button)

        menu = GridLayout(
            cols=2,
            spacing=dp(7),
            size_hint_y=None
        )
        menu.bind(minimum_height=menu.setter("height"))

        sections = [
            "القانون المدني",
            "قانون العقوبات",
            "الإجراءات الجنائية",
            "القانون الدستوري",
            "قانون الأسرة",
            "القانون التجاري",
            "القانون الإداري",
            "قانون العمل",
            "التشريعات المصرية",
            "المساعد الذكي"
        ]

        for section in sections:
            button = Button(
                text=arabic(section),
                size_hint_y=None,
                height=dp(48),
                font_size=dp(14)
            )
            button.bind(
                on_press=lambda instance, name=section:
                self.open_section(name)
            )
            menu.add_widget(button)

        root.add_widget(menu)

        scroll = ScrollView(
            do_scroll_x=False
        )

        self.output = Label(
            text=arabic(
                "مرحبًا بك في موسوعة افهم قانون.\n\n"
                "اختر أحد الأقسام أو ابحث عن موضوع قانوني.\n\n"
                "الموسوعة قيد إعداد المحتوى القانوني الموثق."
            ),
            color=(0.12, 0.16, 0.22, 1),
            font_size=dp(17),
            halign="right",
            valign="top",
            size_hint_y=None,
            padding=(dp(12), dp(15))
        )

        self.output.bind(
            width=lambda obj, width:
            setattr(obj, "text_size", (width - dp(25), None))
        )
        self.output.bind(
            texture_size=lambda obj, size:
            setattr(obj, "height", size[1] + dp(30))
        )

        scroll.add_widget(self.output)
        root.add_widget(scroll)

        footer = Label(
            text=arabic("موسوعة تعليمية قانونية | مصر"),
            size_hint_y=None,
            height=dp(30),
            font_size=dp(12),
            color=(0.3, 0.3, 0.3, 1)
        )
        root.add_widget(footer)

        return root

    def create_database(self):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS laws (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                section TEXT,
                title TEXT,
                article TEXT,
                explanation TEXT,
                source TEXT
            )
        """)

        connection.commit()
        connection.close()

    def show_text(self, text):
        self.output.text = arabic(text)

    def open_section(self, section):

        if section == "المساعد الذكي":
            self.show_text(
                "المساعد القانوني الذكي\n\n"
                "سيتم ربط هذا القسم بخدمة ذكاء اصطناعي عبر الإنترنت.\n\n"
                "يتطلب ذلك إعداد خدمة اتصال آمنة ومفتاح API "
                "على خادم خارجي."
            )
            return

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT title, article, explanation, source "
            "FROM laws WHERE section=?",
            (section,)
        )

        results = cursor.fetchall()
        connection.close()

        if not results:
            self.show_text(
                section + "\n\n"
                "لم تتم إضافة النصوص القانونية الموثقة "
                "إلى هذا القسم بعد.\n\n"
                "سيتم إدراج مواد التشريعات ومصادرها "
                "وشروحها بعد مراجعتها."
            )
            return

        text = section + "\n\n"

        for title, article, explanation, source in results:
            text += (
                title + "\n\n"
                "النص القانوني:\n" + article + "\n\n"
                "الشرح المبسط:\n" + explanation + "\n\n"
                "المصدر:\n" + source + "\n\n"
                "--------------------\n\n"
            )

        self.show_text(text)

    def search_law(self, instance):

        query = self.search.text.strip()

        if not query:
            self.show_text("اكتب كلمة البحث أولًا.")
            return

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT section, title, article, explanation, source
            FROM laws
            WHERE title LIKE ?
            OR article LIKE ?
            OR explanation LIKE ?
            OR section LIKE ?
        """, tuple(["%" + query + "%"] * 4))

        results = cursor.fetchall()
        connection.close()

        if not results:
            self.show_text(
                "نتائج البحث عن: " + query +
                "\n\nلم يُعثر على نتائج في قاعدة البيانات الحالية."
            )
            return

        text = "نتائج البحث عن: " + query + "\n\n"

        for section, title, article, explanation, source in results:
            text += (
                section + "\n"
                + title + "\n\n"
                + "النص القانوني:\n" + article + "\n\n"
                + "الشرح:\n" + explanation + "\n\n"
                + "المصدر:\n" + source + "\n\n"
                + "--------------------\n\n"
            )

        self.show_text(text)


if __name__ == "__main__":
    AfhamQanun().run()
