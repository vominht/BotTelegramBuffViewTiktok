#SOURCE ĐƠN GIẢN, DỄ DÀNG PHÁT TRIỂN
#COPYRIGHT BY BUFFA AKA VMT
import subprocess
import shlex
from datetime import datetime, timedelta
import json
import random
import string
import httpx
from colorama import Fore, Style
import os
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import CallbackContext


last_time_used = {}
admin_ids = [5145402317, 987654321] # Đổi thành admin ID của bạn
TOKEN = '' # Đổi thành token của bot Telegram bạn


#HÀM CLEAR SCREEN
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


#HÀM CHECK AUTH
def is_user_authorized(user_id):
  try:
      with open('auth.json', 'r') as file:
          users = json.load(file)
          for user in users:
              if user['user'] == user_id:
                  expire_date = datetime.strptime(user['expire'], '%Y-%m-%d')
                  now = datetime.now()
                  if expire_date > now:
                      return True
                  break
  except Exception as e:
      print(f'Error reading auth.json: {e}')
  return False


#HÀM CHECK KEY
def validate_and_remove_key(input_key):
  try:
      with open('key.json', 'r') as file:
          keys = json.load(file)

      if input_key in keys:
          key_info = keys[input_key]
          key_type = key_info['type']
          expire_date = datetime.strptime(key_info['expire'], "%Y-%m-%d")
          if expire_date >= datetime.now():
              del keys[input_key]
              with open('key.json', 'w') as file:
                  json.dump(keys, file, indent=4)
              return key_type, key_info['expire']
          else:
              return "expired", key_info['expire']
      else:
          return None, None
  except Exception as e:
      print(f'Error: {e}')
      return None


#HÀM CẬP NHẬT AUTH
def update_auth(user_id, expire, plan):
  try:
      try:
          with open('auth.json', 'r') as file:
              users = json.load(file)
      except FileNotFoundError:
          users = []
      found = False
      for user in users:
          if user['user'] == user_id:
              user['expire'] = expire
              user['plan'] = plan
              found = True
              break
      if not found:
          users.append({"user": user_id, "expire": expire, "plan": plan})
      with open('auth.json', 'w') as file:
          json.dump(users, file, indent=4)
  except Exception as e:
      print(f'Error: {e}')


#HÀM LẤY PLAN CỦA USER
def find_user_plan(user_id):
  try:
      with open('auth.json', 'r') as file:
          users = json.load(file)

      for user in users:
          if user['user'] == user_id:
              return user['plan'], user['expire']
      return None, None
  except FileNotFoundError:
      return None, None
  except Exception as e:
      print(f'Error: {e}')
      return None, None


#HÀM TẠO KEY
def generate_random_key():
  key_length = 20
  characters = string.ascii_letters + string.digits  
  random_key = ''.join(random.choice(characters) for _ in range(key_length))
  return random_key


#HÀM LƯU KEY
def save_key(key, expire_date, plan):
  try:
      with open('key.json', 'r') as file:
          keys = json.load(file)
  except (FileNotFoundError, json.JSONDecodeError):
      keys = {}

  keys[key] = {"expire": expire_date, "type": plan}

  with open('key.json', 'w') as file:
      json.dump(keys, file, indent=4)



# Hàm xử lý lệnh /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_message = (
        "*Các Lệnh Hiện Có:*\n"
        "┏━━━━━━━━━━━━━┓\n"
        "┃ /view - Chạy view theo link Tiktok\n"
        "┃ /getkey - Lấy KEY để kích hoạt Plan\n"
        "┃ /plan - Xem plan hiện tại\n"
        "┃ /active - Lệnh kích hoạt tài khoản\n"
        "┗━━━━━━━━━━━━━┛"
    )
    await update.message.reply_text(help_message, parse_mode='Markdown')

# Hàm xử lý lệnh /active
async def active_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_id = update.message.chat_id
    args = context.args

    if len(args) == 1:
        input_key = args[0]
        key_type, expire_date = validate_and_remove_key(input_key)
        if key_type == "expired":
            await update.message.reply_text('KEY này đã hết hạn !')
        elif key_type:
            await update.message.reply_text('KEY chính xác, đang cập nhật dữ liệu của bạn.')
            update_auth(user_id, expire_date, key_type)
            plan, expire = find_user_plan(user_id)
            time.sleep(2)
            message = (
                "┏━━━━━━━━━━━━━┓\n"
                f"┣➤ UserID: {user_id}\n"
                f"┣➤ EXPIRED: {expire_date}\n"
                f"┣➤ PLAN: {plan}\n"
                "┗━━━━━━━━━━━━━┛"
            )
            await update.message.reply_text(message)
        else:
            await update.message.reply_text('KEY không tồn tại.')
    else:
        await update.message.reply_text('Vui lòng nhập KEY. Usage: /active [key]')


# Hàm xử lý lệnh /plan
async def plan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  user_id = update.effective_user.id
  chat_id = update.message.chat_id

  plan, expire = find_user_plan(user_id)
  if plan and expire:
      message = (
        "┏━━━━━━━━━━━━━┓\n"
        f"┣➤ UserID: `{user_id}`\n"
        f"┣➤ EXPIRED: {expire}\n"
        f"┣➤ PLAN: {plan}\n"
        "┗━━━━━━━━━━━━━┛"
      )
      await update.message.reply_text(message, parse_mode='Markdown')
  else:
      await update.message.reply_text('Bạn không có plan !')


# Hàm xử lý lệnh /list
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  user_id = update.effective_user.id
  chat_id = update.message.chat_id

  if user_id not in admin_ids:
      await update.message.reply_text("Bạn không có quyền sử dụng lệnh này !")
      return
  try:
      with open('key.json', 'r') as file:
          keys = json.load(file)
  except (FileNotFoundError, json.JSONDecodeError):
      await update.message.reply_text("Không có KEY nào đang tồn tại.")
      return
  message = "`Danh Sách Các KEY:`\n"
  for key, details in keys.items():
      expire = details.get('expire', 'Unknown')
      plan = details.get('type', 'Unknown')
      message += f"Key: `{key}`\nExpire Date: {expire}\nPlan: {plan}\n\n"
  await update.message.reply_text(message, parse_mode='Markdown')


# Hàm xử lý lệnh /view
async def view_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  user_id = update.effective_user.id
  chat_id = update.message.chat_id
  args = update.message.text.split()

  if len(args) != 3:
      await update.message.reply_text('Usage: /view <link> <số lượng>')
      return

  url, amount = args[1], args[2]
  plan, _ = find_user_plan(user_id)
  current_time = datetime.now()

  if plan == "free" and int(amount) > 500:
      await update.message.reply_text("Giới hạn chạy view của plan Free là 500 views.")
      return

  if plan == 'free':
      if chat_id in last_time_used:
          time_passed = (current_time - last_time_used[chat_id]).total_seconds()
          if time_passed < 60:
              remaining_time = 60 - time_passed
              await update.message.reply_text(f"Bạn cần chờ thêm {int(remaining_time)} giây để tiếp tục sử dụng.")
              return
      last_time_used[chat_id] = current_time
  cmd_to_run = f'screen -dm bash -c {shlex.quote(f"python view.py {shlex.quote(url)} {shlex.quote(amount)}")}'
  subprocess.run(cmd_to_run, shell=True)

  today = datetime.now().strftime('%d-%m-%Y')
  response_message = (
      f'┏━━━━━━━━━━━━━┓\n'
      f'┣➤ UserID: {user_id}\n'
      f'┣➤ URL: {url}\n'
      f'┣➤ SỐ LƯỢNG VIEW: {amount} views\n'
      f'┣➤ TRẠNG THÁI: Thành Công\n'
      f'┣➤ THỜI GIAN: {today}\n'
      f'┣➤ ADMIN: Buffa aka VMT\n'
      f'┗━━━━━━━━━━━━━┛'
  )
  await update.message.reply_text(response_message)


# Hàm xử lý lệnh /getkey
async def getkey_command(update: Update, context: CallbackContext) -> None:
  chat_id = update.effective_chat.id
  new_key = generate_random_key()
  expire_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
  save_key(new_key, expire_date, 'free')

  url = f"https://web1s.com/st?token=0fb0090f-e188-4d99-b510-0236f65c597a&url=https://connguoihaha.github.io/GetKeyPage/?key={new_key}"
  try:
      async with httpx.AsyncClient() as client:
          response = await client.get(url, follow_redirects=True)
          redirected_url = response.url
      message = (
        "<b>Tạo KEY thành công !!!</b>\n"
        f"Key của bạn là: <a href='{redirected_url}'>Bấm Vào Đây</a>\n"
        "Sau khi lấy KEY thành công, hãy dùng lệnh /active [key bạn vừa lấy] để kích hoạt plan của bạn."
      )
      await update.message.reply_text(message, parse_mode='HTML')
  except httpx.RequestError as e:
      await update.message.reply_text(f"Error: {e}")


# Hàm xử lý lệnh /gen [free/vip]
async def gen_command(update: Update, context: CallbackContext) -> None:
  chat_id = update.effective_chat.id
  user_id = update.effective_user.id

  if user_id not in admin_ids:
      await update.message.reply_text("Bạn không có quyền sử dụng lệnh này !")
      return

  command = update.message.text.split()
  if len(command) == 2 and command[1] in ['free', 'vip']:
      new_key = generate_random_key()
      plan_type = "free" if command[1] == 'free' else "vip"
      days_to_add = 1 if plan_type == "free" else 7
      expire_date = (datetime.now() + timedelta(days=days_to_add)).strftime("%Y-%m-%d")
      save_key(new_key, expire_date, plan_type)
      await update.message.reply_text(f'Key: `{new_key}`\nType: {plan_type}\nExpire date: {expire_date}', parse_mode='Markdown')
  else:
      await update.message.reply_text("Cú pháp không chính xác. Sử dụng: /gen free hoặc /gen vip")


# Hàm xử lý lệnh /clearkey
async def clear_expired_keys(update: Update, context: CallbackContext) -> None:
  chat_id = update.effective_chat.id
  user_id = update.effective_user.id

  if user_id not in admin_ids:
      await update.message.reply_text("Bạn không có quyền sử dụng lệnh này !")
      return
  try:
      with open('key.json', 'r') as file:
          keys = json.load(file)

      current_date = datetime.now().strftime('%Y-%m-%d')
      keys = {k: v for k, v in keys.items() if v.get('expire', '') > current_date}

      with open('key.json', 'w') as file:
          json.dump(keys, file, indent=4)

      await update.message.reply_text("Đã xoá tất cả các KEY hết hạn.")
  except (FileNotFoundError, json.JSONDecodeError):
      await update.message.reply_text("Không tìm thấy file hoặc file không hợp lệ.")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("active", active_command))
app.add_handler(CommandHandler("plan", plan_command))
app.add_handler(CommandHandler("list", list_command))
app.add_handler(CommandHandler("view", view_command))
app.add_handler(CommandHandler('getkey', getkey_command))
app.add_handler(CommandHandler('gen', gen_command))
app.add_handler(CommandHandler('clearkey', clear_expired_keys))

bot = telepot.Bot(TOKEN)
bot_info = bot.getMe()
bot_name = bot_info['first_name']
bot_username = bot_info['username']
clear_screen()
print(Fore.RED + '''
██████╗ ██╗   ██╗███████╗███████╗ █████╗        ██████╗  ██████╗ ████████╗
██╔══██╗██║   ██║██╔════╝██╔════╝██╔══██╗       ██╔══██╗██╔═══██╗╚══██╔══╝
██████╔╝██║   ██║█████╗  █████╗  ███████║       ██████╔╝██║   ██║   ██║   
██╔══██╗██║   ██║██╔══╝  ██╔══╝  ██╔══██║       ██╔══██╗██║   ██║   ██║   
██████╔╝╚██████╔╝██║     ██║     ██║  ██║       ██████╔╝╚██████╔╝   ██║   
╚═════╝  ╚═════╝ ╚═╝     ╚═╝     ╚═╝  ╚═╝       ╚═════╝  ╚═════╝    ╚═╝   


''' + Style.RESET_ALL)
connection_message = f"Đã kết nối thành công tới {bot_name} (@{bot_username})"
border = "═" * (len(connection_message) + 4)
print(Fore.LIGHTGREEN_EX + f"╔{border}╗\n║  {connection_message}  ║\n╚{border}╝" + Style.RESET_ALL)

app.run_polling()