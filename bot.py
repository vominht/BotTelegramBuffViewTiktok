#SOURCE ĐƠN GIẢN, DỄ DÀNG PHÁT TRIỂN
#COPYRIGHT BY BUFFA AKA VMT
import telepot
from telepot.loop import MessageLoop
import subprocess
import shlex
from datetime import datetime, timedelta
import json
import random
import string
import requests
from colorama import Fore, Style
import os

last_time_used = {}
admin_ids = [51454023, 987654321] #admin id ở đây
TOKEN = '' # bot token ở đây


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



#HÀM XỬ LÝ LỆNH
def handle(msg):
    chat_id = msg['chat']['id']
    user_id = msg['from']['id']
    command = msg['text']
    current_time = time.time()

    if command.startswith('/help'):
      message = (
        "*Các Lệnh Hiện Có:*\n"
        "┏━━━━━━━━━━━━━┓\n"
        "┃ /view - Chạy view theo link Tiktok\n"
        "┃ /getkey - Lấy KEY để kích hoạt Plan\n"
        "┃ /plan - Xem plan hiện tại\n"
        "┃ /active - Lệnh kích hoạt tài khoản\n"
        "┗━━━━━━━━━━━━━┛"
      )
      bot.sendMessage(chat_id, message, parse_mode='Markdown')

    #LỆNH ACTIVE PLAN
    elif command.startswith('/active'):
      parts = command.split()
      if len(parts) == 2:
          input_key = parts[1]
          key_type, expire_date = validate_and_remove_key(input_key)
          if key_type == "expired":
              bot.sendMessage(chat_id, f'KEY này đã hết hạn !')
          elif key_type:
              bot.sendMessage(chat_id, f'KEY chính xác, đang cập nhật dữ liệu của bạn.')
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
              bot.sendMessage(chat_id, message)
          else:
              bot.sendMessage(chat_id, 'KEY không tồn tại.')
      else:
          bot.sendMessage(chat_id, 'Vui lòng nhập KEY. Usage: /active [key]')


    #LỆNH KIỂM TRA PLAN
    elif not is_user_authorized(user_id):
        bot.sendMessage(chat_id, 'Bạn không có quyền sử dụng hoặc KEY của bạn đã hết hạn.')
        return


    #LỆNH TẠO KEY CỦA ADMIN
    elif command in ['/gen free', '/gen vip']:
        if user_id not in admin_ids:
            bot.sendMessage(chat_id, "Bạn không có quyền sử dụng lệnh này !")
            return
        new_key = generate_random_key()
        plan_type = "free" if command == '/gen free' else "vip"
        days_to_add = 1 if plan_type == "free" else 7
        expire_date = (datetime.now() + timedelta(days=days_to_add)).strftime("%Y-%m-%d")
        try:
            with open('key.json', 'r') as file:
                keys = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            keys = {}
        keys[new_key] = {"type": plan_type, "expire": expire_date}
        with open('key.json', 'w') as file:
            json.dump(keys, file, indent=4)
        bot.sendMessage(chat_id, f'Key: `{new_key}`\nType: {plan_type}\nExpire date: {expire_date}', parse_mode='Markdown')


    #XỬ LÝ KHI LỆNH KHÔNG DÚNG CÚ PHÁP
    elif command.startswith('/gen'):
        if user_id not in admin_ids:
            bot.sendMessage(chat_id, "Bạn không có quyền sử dụng lệnh này !")
            return
        bot.sendMessage(chat_id, "Cú pháp không chính xác. Sử dụng: /gen free hoặc /gen vip")


    #LỆNH XEM PLAN
    elif command == '/plan':
        plan, expire = find_user_plan(user_id)
        if plan and expire:
            message = (
              "┏━━━━━━━━━━━━━┓\n"
              f"┣➤ UserID: `{user_id}`\n"
              f"┣➤ EXPIRED: {expire}\n"
              f"┣➤ PLAN: {plan}\n"
              "┗━━━━━━━━━━━━━┛"
            )
            bot.sendMessage(chat_id, message, parse_mode='Markdown')
        else:
            bot.sendMessage(chat_id, 'Bạn không có plan !')
    

    #LỆNH XEM LIST KEY CỦA ADMIN
    elif command == '/list':
        if user_id not in admin_ids:
            bot.sendMessage(chat_id, "Bạn không có quyền sử dụng lệnh này !")
            return
        try:
            with open('key.json', 'r') as file:
                keys = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            bot.sendMessage(chat_id, "Không có KEY nào đang tồn tại.")
            return
        message = "`Danh Sách Các KEY:`\n"
        for key, details in keys.items():
            expire = details.get('expire', 'Unknown')
            plan = details.get('type', 'Unknown')
            message += f"Key: `{key}`\nExpire Date: {expire}\nPlan: {plan}\n\n"
        bot.sendMessage(chat_id, message, parse_mode='Markdown')



    #LỆNH CHẠY VIEW
    elif command.startswith('/view'):
        args = command.split()
        plan, expire = find_user_plan(chat_id)
        if len(args) != 3:
            bot.sendMessage(chat_id, 'Usage: /view <link> <số lượng>')
            return
        url, amount = args[1], args[2]
        if plan == "free" and int(amount) > 500:
            bot.sendMessage(chat_id, "Giới hạn chạy view của plan Free là 500 views.")
            return

        if plan == 'free':
            if chat_id in last_time_used:
                time_passed = current_time - last_time_used[chat_id]
                if time_passed < 60:
                    remaining_time = 60 - time_passed
                    bot.sendMessage(chat_id, f"Bạn cần chờ thêm {int(remaining_time)} giây để tiếp tục sử dụng.")
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
        bot.sendMessage(chat_id, response_message)



    #LỆNH LẤY KEY
    elif command == '/getkey':
        new_key = generate_random_key()
        expire_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        save_key(new_key, expire_date, 'free')
      
        url = f"https://web1s.com/st?token=0fb0090f-e188-4d99-b510-0236f65c597a&url=https://connguoihaha.github.io/GetKeyPage/?key={new_key}"
        try:
            response = requests.get(url, allow_redirects=True)
            redirected_url = response.url
            message = (
              "<b>Tạo KEY thành công !!!</b>\n"
              f"Key của bạn là: <a href='{redirected_url}'>Bấm Vào Đây</a>\n"
              "Sau khi lấy KEY thành công, hãy dùng lệnh /active [key bạn vừa lấy] để kích hoạt plan của bạn."
            )
            bot.sendMessage(chat_id, message, parse_mode='HTML')
        except requests.RequestException as e:
            bot.sendMessage(chat_id, f"Error: {e}")






#KHỞI TẠO BOT
bot = telepot.Bot(TOKEN)
bot_info = bot.getMe()
bot_name = bot_info['first_name']
bot_username = bot_info['username']

MessageLoop(bot, handle).run_as_thread()
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

#GIỮ CHO BOT CHẠY
import time
while True:
    time.sleep(10)
