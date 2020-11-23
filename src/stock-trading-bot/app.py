from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *


#======這裡是呼叫的檔案內容=====
from message import *
from new import *
from Function import *

from crawler.finance_symbol_crawler import *
from crawler.company_financial_information_crawler import *
from crawler.company_news_crawler import *
from crawler.exchange_rate_crawler import *
from crawler.latest_share_price_crawler import *
from crawler.stock_history_price_crawler import *



#======這裡是呼叫的檔案內容=====

#======python的函數庫==========
import tempfile, os
import datetime
import time
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi('wnDXDTaHXLwyjpeP28vluzdHoDxagZppLaHR82VU2NBMgolEhjdpSInJ/77T/Izn4AKDLktTBrPweiohDZuRQmrAzvCJnQ45o+6TyBrWTrGO64WYf2fXqtq/gQrF2BMIx9O+jMFZlOq575Rybt9pbwdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('8834df9400170c9d9136fccf2c11f271')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    if '最新合作廠商' in msg:
        message = imagemap_message()
        line_bot_api.reply_message(event.reply_token, message)
    elif '最新活動訊息' in msg:
        message = buttons_message()
        line_bot_api.reply_message(event.reply_token, message)
    elif '註冊會員' in msg:
        message = Confirm_Template()
        line_bot_api.reply_message(event.reply_token, message)
    elif '旋轉木馬' in msg:
        message = Carousel_Template()
        line_bot_api.reply_message(event.reply_token, message)
    elif '圖片畫廊' in msg:
        message = test()
        line_bot_api.reply_message(event.reply_token, message)
    elif '功能列表' in msg:
        message = function_list()
        line_bot_api.reply_message(event.reply_token, message)
    elif '查詢股價' in msg:
        msg = get_mix_price(msg[4:])
        if str(msg) == 'error symbol':
            pass
        elif str(msg) == 'connect timeout':
            pass
        elif str(msg)[:7] == 'simular':
            pass
        else:
            msg =  'max_price = '+msg[0]+'\n'+'open_price = '+msg[1]+'\n'+'current_price = '+msg[2]+'\n'+'min_price = '+msg[3]
        message = TextSendMessage(text=msg)
        line_bot_api.reply_message(event.reply_token, message)
    elif '查詢匯率' in msg:
        msg = get_exchange_rate(msg[4:])
        if str(msg) == 'connect failed':
            pass
        elif len(msg.columns) == 2:
            msg = str(msg)
        else:
            df_list = []
            for num in range(len(msg.columns)):
                df_list.append(msg.columns[num]+' : '+msg[msg.columns[num]][msg.index[0]])

            msg = df_list[4]+'\n'+df_list[1]+'\n'+df_list[0]+'\n'+df_list[5]+'\n'+df_list[2]+'\n'+df_list[3]
        message = TextSendMessage(text=msg)
        line_bot_api.reply_message(event.reply_token, message)
    elif '查詢新聞' in msg:
        if ',' in msg:
            text = msg[4:].split(',')
            msg = get_company_news_link(text[0],int(text[1]))
            if str(msg) == 'please input company name':
                pass
            elif str(msg)[:4] == '此時段無':
                pass
            else:
                msg = str(msg)[1:-1].replace(',',' ').replace("'",' ')
            msg = str(msg)[1:-1].replace(',',' ').replace("'",' ')
        else:
            msg = get_company_news_link(msg[4:])
            if str(msg) == 'please input company name':
                pass
            elif str(msg)[:4] == '此時段無':
                pass
            else:
                msg = str(msg)[1:-1].replace(',',' ').replace("'",' ')
        message = TextSendMessage(text=msg)
        line_bot_api.reply_message(event.reply_token, message)
    elif '查詢財報' in msg:
        msg = get_company_financial(msg[4:])
        if str(msg) == 'please input symbol':
            pass
        else:
            msg = str(msg.set_index('date').T)
        message = TextSendMessage(text=msg)
        line_bot_api.reply_message(event.reply_token, message)
    else:
        message = TextSendMessage(text=msg)
        line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
