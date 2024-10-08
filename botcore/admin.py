from aiogram import Router
from aiogram import types, F, filters
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

import validators
import xlsxwriter
import io
import datetime


from config import ADMINS
from .translations import handlers_variants, translations as ts
from .storageV2 import get_users_dump, get_user_ids_by_lang, get_lang_codes, count_users, count_users_by_code, get_all_user_ids
from .states import AdminMailing, AdminWelcome


def convert_to_buttons(message_text: str) -> list:
    buttons = message_text.split('\n')
    buttons_result = []

    if len(buttons) > 3:
        buttons = buttons[:3]

    for b in buttons:
        name = b.rsplit(' ', 1)[0].strip(" *")
        url = b.rsplit(' ', 1)[1].strip(" *")
        if validators.url(url):
            buttons_result.append((name, url))
        else:
            raise ValueError(url)

    return buttons_result


class AdminPanel:
    def __init__(self, arbitrage_bot):
        self.router = Router()
        self.arbitrage_bot = arbitrage_bot
        self.bot = arbitrage_bot.bot

        self.register_handlers()
    def register_handlers(self):
        self.router.message(filters.command.Command('admin'))(self.enter_admin_panel)

        self.router.message(F.text.lower().in_(handlers_variants('admin_back')))(self.enter_admin_panel)
        self.router.message(F.text.lower().in_(handlers_variants('admin_dump_users')))(self.dump_users)

        self.router.message(F.text.lower().in_(handlers_variants('admin_user_stats')))(self.show_statistics)

        self.router.message(F.text.lower().in_(handlers_variants('admin_setup_mailing')))(self.mailing_start)
        self.router.message(AdminMailing.selecting_lang)(self.mailing_message)
        self.router.message(AdminMailing.entering_message)(self.mailing_asking_links)
        self.router.message(AdminMailing.asking_links, F.text.lower().in_(handlers_variants('admin_skip_links')))(self.mailing_preview)
        self.router.message(AdminMailing.asking_links)(self.mailing_links)
        self.router.message(AdminMailing.process, F.text.lower().in_(handlers_variants('admin_mailing_go_button')))(self.mailing_process)

        self.router.message(F.text.lower().in_(handlers_variants('admin_setup_welcome')))(self.start_message_change)
        self.router.message(AdminWelcome.entering_message)(self.start_message_inline_links)
        self.router.message(AdminWelcome.entering_links, F.text.lower().in_(handlers_variants('admin_skip_links')))(self.start_message_preview)
        self.router.message(AdminWelcome.entering_links)(self.start_message_saving_links)
        self.router.message(AdminWelcome.saving, F.text.lower().in_(handlers_variants('admin_save_button')))(self.start_message_save)

    async def enter_admin_panel(self, message: types.Message, state: FSMContext, lang: str):
        await state.clear()

        if message.from_user.id not in ADMINS:
            await message.answer(ts[lang]['admin_forbidden'])
            return

        admin_kb = ReplyKeyboardBuilder()
        admin_kb.button(text=ts[lang]['admin_user_stats'])
        admin_kb.button(text=ts[lang]['admin_dump_users'])
        admin_kb.button(text=ts[lang]['admin_setup_mailing'])
        admin_kb.button(text=ts[lang]['admin_setup_welcome'])
        admin_kb.button(text=ts[lang]['to_menu'])
        admin_kb.adjust(2)

        await message.answer(text=ts[lang]['admin_panel'], reply_markup=admin_kb.as_markup(resize_keyboard=True))


    async def dump_users(self, message: types.Message, lang: str):
        if message.from_user.id not in ADMINS:
            await message.answer(ts[lang]['admin_forbidden'])
            return

        buffer = io.BytesIO()
        buffer.name = f'bot_users_{datetime.datetime.now().strftime("%m.%d.%Y")}.xlsx'

        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()

        format1 = workbook.add_format({'border': 1})
        format2 = workbook.add_format({'border': 2})

        users = await get_users_dump()
        columns = ['tg_id', 'name', 'surname', 'username', 'tg_language', 'bot_language', 'registered_date']

        for col_num, col_name in enumerate(columns):
            worksheet.write(0, col_num, col_name, format2)

        for i, user in enumerate(users, start=1):
            user_list = [user.tg_id, user.name, user.surname, user.username,
                         user.tg_language, user.bot_language, user.registered_date.strftime('%d.%m.%Y %H:%M:%S')]
            for j, value in enumerate(user_list):
                worksheet.write(i, j, value, format1)

        worksheet.autofit()
        workbook.close()
        buffer.seek(0)

        input_doc = types.BufferedInputFile(buffer.getvalue(), filename=buffer.name)
        await message.answer_document(document=input_doc)

    async def show_statistics(self, message: types.Message, lang: str):
        if message.from_user.id not in ADMINS:
            await message.answer(ts[lang]['admin_forbidden'])
            return

        lang_codes = {code: 0 for code in await get_lang_codes()}
        total_users = await count_users()

        for code in lang_codes:
            lang_codes[code] = await count_users_by_code(code)



        text = ts[lang]['admin_total_users'].format(total_users)
        if lang_codes:
            text += '\n'
            for code, count in lang_codes.items():
                text += '\n'
                text += ts[lang]['admin_lang_users'].format(code, count)

        not_set = await count_users_by_code(None)
        text += '\n' + ts[lang]['admin_no_lang'].format(not_set)

        await message.answer(text)


    async def mailing_start(self, message: types.Message, state: FSMContext, lang: str):
        if message.from_user.id not in ADMINS:
            await message.answer(ts[lang]['admin_forbidden'])
            return

        lang_kb = ReplyKeyboardBuilder()
        lang_kb.button(text='uk')
        lang_kb.button(text='ru')
        lang_kb.button(text='en')
        lang_kb.button(text='ALL')
        lang_kb.button(text=ts[lang]['admin_back'])
        lang_kb.adjust(4)

        await message.answer(ts[lang]['admin_mailing_sel_lang'], reply_markup=lang_kb.as_markup(resize_keyboard=True))
        await state.set_state(AdminMailing.selecting_lang)


    async def mailing_message(self, message: types.Message, state: FSMContext, lang: str):
        if message.text not in ['uk', 'ru', 'en', 'ALL']:
            await message.answer(ts[lang]['admin_mailing_sel_lang'])
            return

        await state.update_data(lang=message.text)

        kb_back = ReplyKeyboardBuilder()
        kb_back.button(text=ts[lang]['admin_back'])

        await message.answer(ts[lang]['admin_mailing_start'], reply_markup=kb_back.as_markup(resize_keyboard=True))

        await state.set_state(AdminMailing.entering_message)


    async def mailing_asking_links(self, message: types.Message, state: FSMContext, lang: str):
        await state.update_data(message_id=message.message_id)

        kb = ReplyKeyboardBuilder()
        # kb.button(text=ts[lang]['admin_mailing_links'])
        kb.button(text=ts[lang]['admin_skip_links'])
        kb.button(text=ts[lang]['admin_back'])
        kb.adjust(1)

        await message.answer(ts[lang]['admin_mailing_links'], reply_markup=kb.as_markup(resize_keyboard=True), parse_mode='markdown')

        await state.set_state(AdminMailing.asking_links)


    async def mailing_links(self, message: types.Message, state: FSMContext, lang: str):
        if message.text:
            try:
                buttons_result = convert_to_buttons(message.text)
                await state.update_data(buttons=buttons_result)
                await state.set_state(AdminMailing.preview)
                await self.mailing_preview(message, state, lang)
            except Exception as e:
                await message.answer(ts[lang]['admin_links_error'] + '\n\n' + str(e))


    async def mailing_preview(self, message: types.Message, state: FSMContext, lang: str):
        data = await state.get_data()
        msg_id = data['message_id']

        if 'buttons' in data:
            url_kb = InlineKeyboardBuilder()
            for text, url in data['buttons']:
                url_kb.button(text=text, url=url)

            url_kb.adjust(1)

            await self.bot.copy_message(chat_id=message.chat.id, from_chat_id=message.chat.id, message_id=msg_id, reply_markup=url_kb.as_markup())
        else:
            await self.bot.copy_message(chat_id=message.chat.id, from_chat_id=message.chat.id, message_id=msg_id)


        ask_mailing_kb = ReplyKeyboardBuilder()
        ask_mailing_kb.button(text=ts[lang]['admin_mailing_go_button'])
        ask_mailing_kb.button(text=ts[lang]['admin_back'])
        ask_mailing_kb.adjust(1)

        await message.answer(ts[lang]['admin_mailing_preview'], reply_markup=ask_mailing_kb.as_markup(resize_keyboard=True))
        await state.set_state(AdminMailing.process)


    async def mailing_process(self, message: types.Message, state: FSMContext, lang: str):
        data = await state.get_data()
        msg_id = data['message_id']
        if data['lang'] == 'ALL':
            users = await get_all_user_ids()
        else:
            users = await get_user_ids_by_lang(data['lang'])

        total = len(users)
        successful = 0
        failed = 0

        if message.from_user.id in users:
            users.remove(message.from_user.id)
            total -= 1

        await message.answer(ts[lang]['admin_mailing_sending'].format(data['lang']), reply_markup=types.ReplyKeyboardRemove())
        progress = await message.answer(ts[lang]['admin_mailing_progress'].format(total, successful, failed))

        mailing_kb = None
        if 'buttons' in data:
            mailing_kb = InlineKeyboardBuilder()
            for text, url in data['buttons']:
                mailing_kb.button(text=text, url=url)
            mailing_kb.adjust(1)

        for user in users:
            try:
                if mailing_kb:
                    await self.bot.copy_message(chat_id=user, from_chat_id=message.chat.id, message_id=msg_id, reply_markup=mailing_kb.as_markup())
                else:
                    await self.bot.copy_message(chat_id=user, from_chat_id=message.chat.id, message_id=msg_id)
                successful += 1
            except (TelegramBadRequest, TelegramForbiddenError) as e:
                failed += 1

            if (successful + failed) % 20 == 0 and (successful + failed) != total:
                await progress.edit_text(ts[lang]['admin_mailing_progress'].format(total, successful, failed))
            if (successful + failed) % total == 0 :
                await progress.edit_text(ts[lang]['admin_mailing_progress'].format(total, successful, failed))



        await message.answer(ts[lang]['admin_mailing_finished'])
        await state.clear()
        await self.enter_admin_panel(message, state, lang)


    async def start_message_change(self, message: types.Message, state: FSMContext, lang: str):
        if message.from_user.id not in ADMINS:
            await message.answer(ts[lang]['admin_forbidden'])
            return

        back_kb = ReplyKeyboardBuilder()
        back_kb.button(text=ts[lang]['admin_back'])

        await message.answer(ts[lang]['admin_welcome_change'], reply_markup=back_kb.as_markup(resize_keyboard=True))
        await state.set_state(AdminWelcome.entering_message)


    async def start_message_inline_links(self, message: types.Message, state: FSMContext, lang: str):
        msg = message.text
        media_id = None
        media_type = None

        if message.photo:
            media_id = message.photo[-1].file_id
            media_type = 'photo'
            msg = message.caption
        elif message.video:
            media_id = message.video.file_id
            media_type = 'video'
            msg = message.caption
        elif message.document:
            await message.answer(ts[lang]['admin_ask_not_document'])
            return

        await state.update_data(msg=msg, media_id=media_id, media_type=media_type)

        kb = ReplyKeyboardBuilder()
        kb.button(text=ts[lang]['admin_skip_links'])
        kb.button(text=ts[lang]['admin_back'])

        await message.answer(ts[lang]['admin_mailing_links'], reply_markup=kb.as_markup(resize_keyboard=True), parse_mode='markdown')
        await state.set_state(AdminWelcome.entering_links)


    async def start_message_saving_links(self, message: types.Message, state: FSMContext, lang: str):
        if message.text:
            try:
                buttons_result = convert_to_buttons(message.text)
                await state.update_data(buttons=buttons_result)
            except Exception as e:
                await message.answer(ts[lang]['admin_links_error'] + '\n\n' + str(e))

        await self.start_message_preview(message, state, lang)


    async def start_message_preview(self, message: types.Message, state: FSMContext, lang: str):
        data = await state.get_data()
        msg = data['msg']
        media_id = data['media_id']
        media_type = data['media_type']

        url_kb = None

        if 'buttons' in data:
            url_kb = InlineKeyboardBuilder()
            for text, url in data['buttons']:
                url_kb.button(text=text, url=url)

            url_kb.adjust(1)

        if url_kb and media_id:
            if media_type == 'photo':
                await message.answer_photo(photo=media_id, caption=msg, reply_markup=url_kb.as_markup())
            elif media_type == 'video':
                await message.answer_video(video=media_id, caption=msg, reply_markup=url_kb.as_markup())
        elif url_kb:
            await message.answer(msg, reply_markup=url_kb.as_markup())
        elif media_id:
            if media_type == 'photo':
                await message.answer_photo(photo=media_id, caption=msg)
            elif media_type == 'video':
                await message.answer_video(video=media_id, caption=msg)
        else:
            await message.answer(msg)


        save_kb = ReplyKeyboardBuilder()
        save_kb.button(text=ts[lang]['admin_save_button'])
        save_kb.button(text=ts[lang]['admin_back'])

        await message.answer(ts[lang]['admin_ask_save'], reply_markup=save_kb.as_markup(resize_keyboard=True))
        await state.set_state(AdminWelcome.saving)

    async def start_message_save(self, message: types.Message, state: FSMContext, lang: str):
        data = await state.get_data()

        msg = data['msg']
        media_id = data['media_id']
        media_type = data['media_type']

        with open('./downloads/admin_welcome/text.txt', 'w') as f:
            f.write(msg if msg else '')

        with open(f'./downloads/admin_welcome/media_id.txt', 'w') as f:
            if media_id:
                f.write(f'{media_type} {media_id}')

        with open('./downloads/admin_welcome/links.txt', 'w') as f:
            if 'buttons' in data:
                for text, url in data['buttons']:
                    f.write(f'{text} {url}\n')

        await message.answer(ts[lang]['admin_welcome_saved'])
        await self.enter_admin_panel(message, state, lang)
        self.arbitrage_bot.load_start_msg()




