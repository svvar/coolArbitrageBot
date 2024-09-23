import asyncio
import random
from datetime import datetime
import io
import os
import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from aiogram import Bot, Dispatcher, types, F, filters
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.methods import SendMediaGroup

from functions import account_checking, downloader, twoFA, market_apps, id_generator

from .states import *
from .callbacks import EditAppsMenuCallback
from .middlewares import LangMiddleware
from .translations import translations as ts, handlers_variants
from . import storage


class ArbitrageBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.dp.update.middleware(LangMiddleware())

        self.http_session = aiohttp.ClientSession()

        self.register_handlers()

    def register_handlers(self):
        self.dp.message(filters.command.Command('start'))(self.start_msg)

        self.dp.message(F.text.lower().in_(handlers_variants('menu_check_accs')))(self.check_account_blocked)
        self.dp.message(F.text.lower().in_(handlers_variants('menu_2fa')))(self.start_2fa)
        self.dp.message(F.text.lower().in_(handlers_variants('menu_tiktok')))(self.tiktok_download_start)
        self.dp.message(F.text.lower().in_(handlers_variants('menu_apps')))(self.apps_menu)
        self.dp.message(F.text.lower().in_(handlers_variants('menu_id')))(self.id_gen_start)

        self.dp.message(F.text.lower().in_(handlers_variants('to_menu')))(self.show_menu)

        self.dp.message(Setup.choosing_lang)(self.set_lang)

        self.dp.message(CheckingAccounts.start_checking)(self.on_account_list)

        self.dp.message(TwoFA.key_input_msg)(self.get_2fa_msg)
        self.dp.message(TwoFA.key_input_callback)(self.get_2fa_msg)
        self.dp.callback_query(TwoFA.key_input_callback)(self.get_2fa_callback)

        self.dp.message(TikTokDownload.url_input)(self.tiktok_download)

        self.dp.callback_query(Apps.info_shown, EditAppsMenuCallback.filter(F.action == 'add'))(self.add_app_request)
        self.dp.callback_query(Apps.info_shown, EditAppsMenuCallback.filter(F.action == 'delete'))(self.delete_app_request)
        self.dp.message(Apps.entering_url)(self.add_app)
        self.dp.callback_query(Apps.selecting_to_delete)(self.delete_app)

        self.dp.message(IdGenerator.need_meta)(self.id_gen_color)
        self.dp.message(IdGenerator.selecting_color)(self.id_gen_sex)
        self.dp.message(IdGenerator.selecting_sex)(self.id_gen_name)
        self.dp.message(IdGenerator.entering_name)(self.id_gen_age)
        self.dp.message(IdGenerator.entering_age)(self.id_gen_final)
        self.dp.message(IdGenerator.generating, F.text.lower().in_(handlers_variants('one_more')))(self.id_generate)

    async def start_msg(self, message: types.Message, state: FSMContext):
        if not await storage.find_user(message.from_user.id):
            await storage.add_user(message.from_user.id)

        await message.answer("Виберіть мову / Выберите язык / Select language:",
                             reply_markup=ReplyKeyboardBuilder()
                             .button(text='🇺🇦 Українська').button(text='🇷🇺 Русский').button(text='🇺🇸 English').as_markup())

        await state.set_state(Setup.choosing_lang)

    async def set_lang(self, message: types.Message, state: FSMContext):
        lang = message.text
        if 'українська' in lang.lower():
            lang = 'ua'
        elif 'русский' in lang.lower():
            lang = 'ru'
        elif 'english' in lang.lower():
            lang = 'en'
        else:
            await message.answer('Неправильно вказана мова, спробуйте ще раз\nНеправильно указан язык, попробуйте еще раз')
            return
        await storage.set_lang(message.from_user.id, lang)
        await self.show_menu(message, state, lang)

    async def show_menu(self, message: types.Message, state: FSMContext, lang: str):

        kb = ReplyKeyboardBuilder()
        kb.button(text=ts[lang]['menu_check_accs'])
        kb.button(text=ts[lang]['menu_2fa'])
        kb.button(text=ts[lang]['menu_tiktok'])
        kb.button(text=ts[lang]['menu_apps'])
        kb.button(text=ts[lang]['menu_id'])
        kb.adjust(2)

        await message.answer(ts[lang]['start_msg'], reply_markup=kb.as_markup(resize_keyboard=True))
        await state.clear()


    async def check_account_blocked(self, message: types.Message, state: FSMContext, lang: str):
        await message.answer(ts[lang]['accs_ask_list'])
        await state.set_state(CheckingAccounts.start_checking)


    async def on_account_list(self, message: types.Message, state: FSMContext, lang: str):
        if message.document:
            with io.BytesIO() as file:
                await message.bot.download(message.document.file_id, file)
                raw_links = file.read().decode('utf-8')
        else:
            raw_links = message.text

        links = account_checking.extract_links(raw_links)

        active, blocked, errors = await account_checking.check_urls(links)

        message_text = ts[lang]['accs_info_msg'].format(len(active), len(blocked), len(errors))
        message_files = []

        if len(active) <= 30:
            message_text += f'\n\n*{ts[lang]["accs_active_label"]}:*\n' + '\n'.join(active)
        else:
            with io.BytesIO() as file:
                file.name = 'active_accounts.txt'
                file.write('\n'.join(active).encode('utf-8'))
                input_file = types.input_file.BufferedInputFile(file.getvalue(), filename=file.name)
                message_files.append(types.InputMediaDocument(media=input_file, caption=ts[lang]["accs_active_label"]))

        if len(blocked) <= 30:
            message_text += f'\n\n*{ts[lang]["accs_banned_label"]}:*\n' + '\n'.join(blocked)
        else:
            with io.BytesIO() as file:
                file.name = 'blocked_accounts.txt'
                file.write('\n'.join(blocked).encode('utf-8'))
                input_file = types.input_file.BufferedInputFile(file.getvalue(), filename=file.name)
                message_files.append(types.InputMediaDocument(media=input_file, caption=ts[lang]["accs_banned_label"]))

        await message.answer(message_text, parse_mode='markdown')

        if message_files:
            await message.bot(SendMediaGroup(chat_id=message.chat.id, media=message_files))
        await state.clear()

    async def rotate_proxy_task(self, rotate_url):
        await self.rotate_proxy(rotate_url)
        scheduler = AsyncIOScheduler()
        scheduler.add_job(self.rotate_proxy, 'interval', minutes=3, args=(rotate_url,))
        scheduler.start()

    async def rotate_proxy(self, rotate_url):
        print('Rotating proxy...')
        try:
            async with self.http_session.get(rotate_url, ssl=False, timeout=15) as response:
                if response.status == 200:
                    print('Proxy rotated')
                    return True
                print('Proxy rotation failed')
                return False
        except asyncio.TimeoutError:
            print('Proxy rotation failed')
            return False

    async def start_2fa(self, message: types.Message, state: FSMContext, lang: str):
        keys = await storage.get_keys(message.from_user.id)
        keys = keys.split(' ') if keys else []
        if keys:
            inline = InlineKeyboardBuilder()
            for key in reversed(keys):
                inline.button(text=key, callback_data=key)
            inline.adjust(1)
            msg = await message.answer(ts[lang]['2fa_select_key'], reply_markup=inline.as_markup())
            await state.set_data({'select_key_msg': msg.message_id})
            await state.set_state(TwoFA.key_input_callback)
        else:
            await message.answer(ts[lang]['2fa_enter_key'])
            await state.set_state(TwoFA.key_input_msg)


    async def get_2fa_callback(self, callback: types.CallbackQuery, state: FSMContext, lang: str):
        key = callback.data
        await state.set_state(TwoFA.fetching_data)
        await callback.answer()

        await self.get_2fa(key, callback.message, state, lang)

    async def get_2fa_msg(self, message: types.Message, state: FSMContext, lang: str):
        key = message.text.strip().replace(' ', '')
        if twoFA.is_base32_encoded(key):
            await storage.add_key(message.from_user.id, key)
            await state.set_state(TwoFA.fetching_data)

            await self.get_2fa(key, message, state, lang)
        else:
            await message.answer(ts[lang]['2fa_wrong_key'])
            await state.clear()

    async def get_2fa(self, key, message: types.Message, state: FSMContext, lang: str):
        state_data = await state.get_data()
        if 'select_key_msg' in state_data:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=state_data['select_key_msg'])

        while await state.get_state() == TwoFA.fetching_data:
            async with self.http_session.get(f'https://2fa.fb.rip/api/otp/{key}') as raw_response:
                response = await raw_response.json()

            if response['ok']:
                state_data = await state.get_data()
                if 'code_message_id' in state_data:
                    await message.bot.edit_message_text(chat_id=message.chat.id,
                                                        message_id=state_data['code_message_id'],
                                                        text=ts[lang]['2fa_code_msg'].format(
                                                            response['data']['otp'], response['data']['timeRemaining']),
                                                        parse_mode='markdown')
                else:
                    code_message = await message.answer(ts[lang]['2fa_code_msg'].format(
                                                            response['data']['otp'], response['data']['timeRemaining']),
                                                        parse_mode='markdown')
                    await state.set_data({'code_message_id': code_message.message_id})
                await asyncio.sleep(2)
            else:
                await message.answer(ts[lang]['wrong_key'])
                break

        state_data = await state.get_data()
        if 'code_message_id' in state_data:
            await message.bot.delete_message(chat_id=message.chat.id,
                                            message_id=state_data['code_message_id'])

    async def tiktok_download_start(self, message: types.Message, state: FSMContext, lang: str):
        await message.answer(ts[lang]['tiktok_ask_url'])
        await state.set_state(TikTokDownload.url_input)

    async def tiktok_download(self, message: types.Message, state: FSMContext, lang: str):
        url = message.text

        # Clearing state early here to make other commands work correctly while downloading tiktok
        await state.clear()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            video_path = await loop.run_in_executor(executor, downloader.save_tiktok_video, url)

        if video_path:
            input_file = types.FSInputFile(video_path)
            await message.answer_document(input_file)
            os.remove(video_path)
        else:
            await message.answer(ts[lang]['tiktok_not_found'])


    async def apps_menu(self, message: types.Message, state: FSMContext, lang: str):
        users_apps = await storage.get_user_apps(message.from_user.id)
        for app in users_apps:
            if await market_apps.check_app(self.http_session, app.url):
                await storage.update_app_status(message.from_user.id, app.name, 'active')
                app.status = 'active'
            else:
                await storage.update_app_status(message.from_user.id, app.name, 'blocked')
                app.status = 'blocked'

        kb = InlineKeyboardBuilder()
        if len(users_apps) < 5:
            kb.button(text=ts[lang]['apps_add_button'], callback_data=EditAppsMenuCallback(action='add').pack())
        if users_apps:
            kb.button(text=ts[lang]['apps_delete_button'], callback_data=EditAppsMenuCallback(action='delete').pack())

        await state.set_state(Apps.info_shown)
        if not users_apps:
            await message.answer(ts[lang]['apps_no_apps'], reply_markup=kb.as_markup())
            return

        msg = ""
        for app in users_apps:
            msg += f"*{app.name}* "
            if app.status == 'active':
                msg += '✅\n'
            else:
                msg += '❌\n'

        await message.answer(msg, reply_markup=kb.as_markup(), parse_mode='markdown')


    async def add_app_request(self, callback: types.CallbackQuery, state: FSMContext, lang: str):
        await callback.answer()

        await self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                         message_id=callback.message.message_id,
                                         text=ts[lang]['apps_ask_url'])

        await state.set_state(Apps.entering_url)

    async def add_app(self, message: types.Message, state: FSMContext, lang: str):
        url = message.text
        if 'play.google.com/store' not in url:
            await message.answer(ts[lang]['apps_bad_url'])
            await state.clear()

        app_name = await market_apps.get_app_name(self.http_session, url)
        if not app_name:
            await message.answer(ts[lang]['apps_already_blocked'])
            await state.clear()
            return
        elif await storage.find_app_by_name(message.from_user.id, app_name):
            await message.answer(ts[lang]['apps_added_yet'])
            await state.clear()
            return

        await storage.add_app(message.from_user.id, url, app_name)
        await message.answer(ts[lang]['apps_add_success'].format(app_name), parse_mode='markdown')
        await state.clear()


    async def delete_app_request(self, callback: types.CallbackQuery, state: FSMContext, lang: str):
        await callback.answer()

        users_apps = await storage.get_user_apps(callback.from_user.id)
        kb = InlineKeyboardBuilder()
        for app in users_apps:
            kb.button(text=app.name, callback_data=app.name)
        kb.adjust(1)

        await self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                         message_id=callback.message.message_id,
                                         text=ts[lang]['apps_choose_delete'], reply_markup=kb.as_markup()
                                         )
        await state.set_state(Apps.selecting_to_delete)

    async def delete_app(self, callback: types.CallbackQuery, state: FSMContext, lang: str):
        app_name = callback.data
        await storage.delete_app(callback.from_user.id, app_name)
        await self.bot.edit_message_text(chat_id=callback.message.chat.id,
                                         message_id=callback.message.message_id,
                                         text=ts[lang]['apps_delete_success'].format(app_name),
                                         parse_mode='markdown')

        await callback.answer()
        await state.clear()

    async def check_apps_task(self):
        scheduler = AsyncIOScheduler()
        await self.check_apps()
        scheduler.add_job(self.check_apps, 'interval', minutes=30)
        scheduler.start()

    async def check_apps(self):
        print('Checking apps...')
        users_apps = await storage.get_all_apps()
        for app in users_apps:
            if app.status == 'blocked':
                continue

            if not await market_apps.check_app(self.http_session, app.url):
                await storage.update_app_status(app.user_id, app.name, 'blocked')
                lang = await storage.get_lang(app.user_id)
                await self.bot.send_message(app.user_id, ts[lang]['apps_blocked_warning'].format(app.name),
                                            parse_mode='markdown')

        print('Apps checked')


    async def _check_apps_2_WIP(self):
        print('Checking apps...')
        users_apps = await storage.get_all_apps()

        to_check = []
        for app in users_apps:
            if app.status == 'blocked':
                continue

            to_check.append(app.url)

        print('Apps checked')


    async def id_gen_start(self, message: types.Message, state: FSMContext, lang: str):
        reply_kb = ReplyKeyboardBuilder()
        reply_kb.button(text=ts[lang]['no_meta'])
        reply_kb.button(text=ts[lang]['random_meta'])
        reply_kb.button(text=ts[lang]['to_menu'])
        reply_kb.adjust(2)

        await message.answer(ts[lang]['ask_meta'], reply_markup=reply_kb.as_markup(resize_keyboard=True))
        await state.set_state(IdGenerator.need_meta)

    async def id_gen_color(self, message: types.Message, state: FSMContext, lang: str):
        meta = message.text
        if meta.lower() == ts[lang]['no_meta'].lower():
            await state.update_data({'meta': False})
        elif meta.lower() == ts[lang]['random_meta'].lower():
            await state.update_data({'meta': True})
        else:
            await message.answer(ts[lang]['repeat_input'])
            return


        reply_kb = ReplyKeyboardBuilder()
        reply_kb.button(text=ts[lang]['color'])
        reply_kb.button(text=ts[lang]['black_white'])
        reply_kb.button(text=ts[lang]['to_menu'])
        reply_kb.adjust(2)

        await message.answer(ts[lang]['select_photo_color'], reply_markup=reply_kb.as_markup(resize_keyboard=True))
        await state.set_state(IdGenerator.selecting_color)

    async def id_gen_sex(self, message: types.Message, state: FSMContext, lang: str):
        color = message.text
        if color.lower() == ts[lang]['color'].lower():
            await state.update_data({'grey': False})
        elif color.lower() == ts[lang]['black_white'].lower():
            await state.update_data({'grey': True})
        else:
            await message.answer(ts[lang]['repeat_input'])
            return


        reply_kb = ReplyKeyboardBuilder()
        reply_kb.button(text=ts[lang]['man'])
        reply_kb.button(text=ts[lang]['woman'])
        reply_kb.button(text=ts[lang]['to_menu'])
        reply_kb.adjust(2)

        await message.answer(ts[lang]['select_sex'], reply_markup=reply_kb.as_markup(resize_keyboard=True))
        await state.set_state(IdGenerator.selecting_sex)

    async def id_gen_name(self, message: types.Message, state: FSMContext, lang: str):
        sex = message.text
        if sex.lower() == ts[lang]['man'].lower():
            await state.update_data({'sex': 'male'})
        elif sex.lower() == ts[lang]['woman'].lower():
            await state.update_data({'sex': 'female'})
        else:
            await message.answer(ts[lang]['repeat_input'])
            return

        kb = ReplyKeyboardBuilder()
        kb.button(text=ts[lang]['to_menu'])
        await message.answer(ts[lang]['enter_name'], reply_markup=kb.as_markup(resize_keyboard=True))
        await state.set_state(IdGenerator.entering_name)


    async def id_gen_age(self, message: types.Message, state: FSMContext, lang: str):
        name = message.text.split(' ')
        if len(name) != 2:
            await message.answer(ts[lang]['repeat_input'])
            return

        await state.update_data({'name': name[0], 'surname': name[1]})

        kb = ReplyKeyboardBuilder()
        kb.button(text=ts[lang]['to_menu'])
        await message.answer(ts[lang]['enter_age'], reply_markup=kb.as_markup(resize_keyboard=True))
        await state.set_state(IdGenerator.entering_age)

    async def id_gen_final(self, message: types.Message, state: FSMContext, lang: str):
        age = message.text
        try:
            age = datetime.strptime(age, '%d.%m.%Y')
            await state.update_data({'day': age.day, 'month': age.month, 'year': age.year})
            await state.set_state(IdGenerator.generating)
            await self.id_generate(message, state, lang)
        except ValueError:
            await message.answer(ts[lang]['repeat_input'])
            return


    async def id_generate(self, message: types.Message, state: FSMContext, lang: str):
        kb = ReplyKeyboardBuilder()
        kb.button(text=ts[lang]['to_menu'])

        await message.answer(ts[lang]['wait_generating'], reply_markup=kb.as_markup(resize_keyboard=True))
        stored_data = await state.get_data()
        account = id_generator.Account(stored_data['name'], stored_data['surname'], stored_data['day'], stored_data['month'], stored_data['year'])

        if stored_data['sex'] == 'male':
            photo_dir = './faces/male'
        else:
            photo_dir = './faces/female'

        photo_path = os.path.join(photo_dir, random.choice(os.listdir(photo_dir)))

        result_path = os.path.join('./faces', f'{account.name}_{account.surname}{message.message_id}.jpg')

        with ProcessPoolExecutor(max_workers=10) as executor:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(executor, id_generator.generate_document, account, photo_path, result_path, stored_data['grey'], stored_data['meta'])

        kb.button(text=ts[lang]['one_more'])

        if os.path.exists(result_path):
            input_file = types.FSInputFile(result_path)
            await message.answer_document(input_file, reply_markup=kb.as_markup(resize_keyboard=True))
            os.remove(result_path)
        else:
            await message.answer(ts[lang]['id_gen_err'], reply_markup=kb.as_markup(resize_keyboard=True))


        # await state.clear()


    async def start_polling(self):
        print("Starting bot")
        await self.dp.start_polling(self.bot)

