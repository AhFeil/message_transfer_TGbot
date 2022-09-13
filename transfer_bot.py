"""
0.15
添加根据频道只抽取url
自动根据系统切换一些参数，无需部署时手动
保存时询问是否清除，修复bug：A姐发的是纯文本
"""

import os
import logging
import sys
import platform

from telegram.ext import Updater
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import InlineQueryHandler

from TgbotBehavior import transfer, clear, save_as_note, inline_caps, unknown, earliest_msg, sure_clear

system = platform.platform()
if system == 'Windows-':
    os.environ["http_proxy"] = "http://127.0.0.1:7890"
    os.environ["https_proxy"] = "http://127.0.0.1:7890"
elif system == 'Linux-':
    pass
else:
    print("where am I?")

chat_id = ''
bot_token = ''
manage_id = [chat_id, '1111111111']
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

updater = Updater(token=bot_token)
dispatcher = updater.dispatcher


# 回复固定内容
def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"I'm a bot in {system}, please talk to me!")


# 类似路由，接收到 /start 执行哪个函数，
start_handler = CommandHandler('start', start)
# 注册 start_handler ，以便调度
dispatcher.add_handler(start_handler)


# 转存
transfer_handler = MessageHandler((~Filters.command), transfer)
dispatcher.add_handler(transfer_handler)


# 确认删除转存内容
sure_clear_handler = CommandHandler('clear', sure_clear)
dispatcher.add_handler(sure_clear_handler)
# 删除转存内容 或回复不删
dispatcher.add_handler(CallbackQueryHandler(clear))


# 另存到
save_handler = CommandHandler('save', save_as_note)
dispatcher.add_handler(save_handler)


# 显示最早的一条信息
earliest_msg_handler = CommandHandler('emsg', earliest_msg)
dispatcher.add_handler(earliest_msg_handler)


# inline
inline_caps_handler = InlineQueryHandler(inline_caps)
dispatcher.add_handler(inline_caps_handler)


# 关闭机器人
def shutdown(update: Update, context: CallbackContext):
    if str(update.effective_chat.id) in manage_id:
        context.bot.send_message(chat_id=update.effective_chat.id, text="robot will shutdown immediately")
        updater.stop()
        sys.exit(0)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You are not authorized to execute this command")


shutdown_handler = CommandHandler('shutdown', shutdown)
dispatcher.add_handler(shutdown_handler)


# 未知命令回复
# 必须放到最后，会先判断前面的命令，都不是才会执行这个
unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.start_polling()


