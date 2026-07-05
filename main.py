from telegram import Bot, MessageEntity
import asyncio

TOKEN = "8654764187:AAGSqHRK59Ood6Z32KktLOpiytlZgWbD24E"
CHAT_ID = 7816353760

# Thay bằng custom_emoji_id thật
EMOJI_SPIRAL = "5368324170671202286"
EMOJI_MONEY  = "5368324170671202287"

async def main():
    bot = Bot(TOKEN)

    text = (
        "A ĐƠN RÚT ĐÃ ĐƯỢC GỬI!\n\n"
        "B Họ và tên: NGUYEN THANH HOP\n"
        "C Ngân hàng: VPBank\n"
        "D STK: 0336293609\n"
        "E Số tiền: 12,000đ\n"
        "F Đang chờ admin duyệt..."
    )

    entities = [
        MessageEntity(
            type=MessageEntity.CUSTOM_EMOJI,
            offset=0,
            length=1,
            custom_emoji_id=EMOJI_SPIRAL,
        ),
        MessageEntity(
            type=MessageEntity.CUSTOM_EMOJI,
            offset=48,
            length=1,
            custom_emoji_id=EMOJI_MONEY,
        ),
    ]

    await bot.send_message(
        chat_id=CHAT_ID,
        text=text,
        entities=entities,
    )

asyncio.run(main())
