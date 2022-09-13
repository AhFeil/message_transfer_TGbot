"""
tg机器人的所有命令行为（除了start）
查 需要改
"""
import datetime
import platform
import re

from telegram import Update
from telegram.ext import CallbackContext, ContextTypes
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# def extract_urls(update):  # 该怎么传入 update


# 转存
def transfer(update: Update, context: CallbackContext):
    target_file = update.effective_chat.id

    # 提取特定频道信息中的网址，先保证只有转发的才会触发这一条, and 应用这条规则的频道等
    if update.message.forward_from_chat and update.message.forward_from_chat.id == -1001651435712:
        # 有时候AHHH那个也会发纯文本，如果只有 ~。caption，就不能处理纯文本了，还会报错
        string = ''   # 不然异常终止后会销毁string
        try:
            string += update.message.caption
        except:
            string += update.message.text
        print(string)
        url = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
        with open(str(target_file) + '_url' + '.txt', 'a', encoding='utf-8') as f:
            f.write('\n'.join(filter(None, url)) + '\n')
        context.bot.send_message(chat_id=update.effective_chat.id, text='url saved.')
        return 0

    t = str(datetime.datetime.now())
    link = []
    if update.message.text:
        content = update.message.text
        search_link = update.message.entities
        for i in search_link:
            link.append(i.url)
    else:
        content = update.message.caption
        search_link = update.message.caption_entities
        for i in search_link:
            link.append(i.url)
    # print(content)
    element = '\n'
    # 不知道为什么会报错，好像是字符串相加不能有 None ，只对caption报错
    with open(str(target_file) + '.txt', 'a', encoding='utf-8') as f:
        f.write(t.center(80, '-') + '\n' + content + '\n' + element.join(filter(None, link)) + '\n\n')
    context.bot.send_message(chat_id=update.effective_chat.id, text='transfer done.')


# 另存到
def save_as_note(update: Update, context: CallbackContext):
    # 存有信息的文件
    target_file = update.effective_chat.id
    # 根据系统特征选择 要保存的文件
    if  platform.platform()== 'Windows-':
        save_file = '.md'
    elif platform.platform()== 'Linux-':
        save_file = '/var/www/webnote/'
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="where am I?")
    # 读取然后保存
    with open(str(target_file) + '.txt', 'r', encoding='utf-8') as f:
        mysave = f.read()
    with open(str(target_file) + '_url' + '.txt', 'r', encoding='utf-8') as f:
        mysave_url = f.read()
    with open(save_file, 'a', encoding='utf-8') as f:
        f.write(mysave + mysave_url)

    # 制作对话内的键盘，第一个是专门的结构，第二个函数是将这个结构转成
    inline_kb = [
        [
            InlineKeyboardButton('also clear?', callback_data=str('clearall')),
            InlineKeyboardButton('dont clear!', callback_data=str('notclear')),
        ]
    ]
    kb_markup = InlineKeyboardMarkup(inline_kb)

    context.bot.send_message(chat_id=update.effective_chat.id, text="save done.", reply_markup=kb_markup)


# 确认删除转存内容
def sure_clear(update: Update, context: CallbackContext):
    # 制作对话内的键盘，第一个是专门的结构，第二个函数是将这个结构转成
    inline_kb = [
        [
            InlineKeyboardButton('sure to clear', callback_data=str('clearall')),
        ]
    ]
    kb_markup = InlineKeyboardMarkup(inline_kb)

    context.bot.send_message(chat_id=update.effective_chat.id, text="Warning! You are clearing your data", reply_markup=kb_markup)


# 接收按键里的信息并删除转存内容 或回复不删
def clear(update: Update, context: CallbackContext):
    target_file = update.effective_chat.id
    query = update.callback_query
    query.answer()
    if query.data == 'clearall':
        with open(str(target_file) + '.txt', 'r', encoding='utf-8') as f:
            mysave = f.read()
        with open(str(target_file) + '_url' + '.txt', 'r', encoding='utf-8') as f:
            mysave_url = f.read()
        with open(str(target_file) + '.txt', 'a+', encoding='utf-8') as f:
            f.truncate(0)
        with open(str(target_file) + '_url' + '.txt', 'a+', encoding='utf-8') as f:
            f.truncate(0)
        with open(str(target_file) + '_backup' + '.txt', 'w', encoding='utf-8') as f:
            f.write(mysave + mysave_url)
        query.edit_message_text(text=f"Selected option: {query.data}, clear done.")
    elif query.data == 'notclear':
        query.edit_message_text(text="OK, I haven't clear yet")
    else:
        query.edit_message_text(text="This command is not mine")


# 显示最早的一条信息。标准操作，只有两种情况，全空，或者开头是 '-' * 27 ，下面也只考虑这两种情况
# 顺便统计消息数量
def earliest_msg(update: Update, context: CallbackContext):
    n = 2
    target_file = update.effective_chat.id
    first_message = ""
    with open(str(target_file) + '.txt', 'r', encoding='utf-8') as f:
        # 读第一行，空的时候返回信息。换行不算空
        if not f.readline():
            context.bot.send_message(chat_id=update.effective_chat.id, text="You don't have any message.")
            return 0
        # 只读取第一条信息。对f的每一次读取都被记录下来了，第一行被上面读了，下面读到第二个标记，在下面统计的读的是第二个标签之后的
        for line in f:
            if first_message and line[0:27] == '-' * 27:
                # 首次读会有'-' * 27，但临时字符串还没写入，没有。第二次读到'-' * 27，临时字符串前27个和这次的行前27个都是'-' * 27，这就是标志，退出循环
                # 从几行前的注释可知，first_message可省略，也许可以改成try
                break
            first_message += line
        # 统计消息数量
        for line in f:
            if line[0:27] == '-' * 27:
                n += 1
        # 文件指针回到开头读首条数据时间
        f.seek(0)
        first_date = f.read(46)[27:]
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'The number of messages you have saved is {n},\nHere is the earliest message you saved at ' + first_date)
    context.bot.send_message(chat_id=update.effective_chat.id, text=first_message)


# inline
def inline_caps(update: Update, context: CallbackContext):
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)


# 未知命令回复
def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

