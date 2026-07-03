import logging
import requests
import json
import asyncio
import httpx
import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- TÍCH HỢP FLASK ĐỂ TREO 24/7 TRÊN RENDER ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "🔥 Bot Free Fire OB54 Đang Hoạt Động!"

def run_web():
    # Render sẽ cấp một PORT ngẫu nhiên qua biến môi trường
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# --- CẤU HÌNH HỆ THỐNG (ĐÃ CẬP NHẬT CHO OB54) ---
API_BAN_URL = "https://apibanob54.vercel.app/ban?access="  # ← Đã đổi thành ob54
API_CHECK_INFO = "http://203.57.85.58:2035/player-info?uid={uid}&key=@yashapis"
API_GARENA = "https://100067.connect.garena.com/game/account_security/bind:get_bind_info?app_id=100067"
API_REGION = "http://203.57.85.58:2035/region?uid={uid}&key=@yashapis"  # ← Thêm API region

# --- LINK GIF ---
GIF_HU = "https://media1.giphy.com/media/v1.Y2lkPTZjMDliOTUyYzc0NjEwbnRmZnVsMGRyaTFiazYwZzRybm1yamk5dHU5djM3Ym9kdyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/QlQdLBS70XJcZY1fLF/giphy.gif"
GIF_CUTE = "https://media3.giphy.com/media/v1.Y2lkPTZjMDliOTUyZ2x4NTdidXZwNzd3c2ZlcHgwdXpkMXkzdWtwYTd5YzEyb2NuOHdjYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/SvK7Gxcq4QS4fNNjYH/giphy.gif"
GIF_BAN = "https://media3.giphy.com/media/v1.Y2lkPTZjMDliOTUyNnI1OGdlNnUybTY3Y3BwNWgyYnpyZGNpMGR5N3p3NHYwMzNldTIzZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/Xxq7xGRiH0asGf5PXD/giphy.gif"
GIF_LOADING = ""https://media.giphy.com/media/UcMN5lbUI4b5sdTSLu/giphy.gif"
GIF_DONE = "https://media0.giphy.com/media/jst0dxUybUkdH9yTyB/giphy.gif"

TOKEN = "8625237753:AAEHTJk3V9d6-cn4aO4QwbNEdXhikAS0bN8"
OWNER_ID = 8433670203  

admins = {OWNER_ID}
allowed_groups = set()
user_list = set()  # Lưu danh sách user để gửi thông báo

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- HÀM HỖ TRỢ ---
def mask_email(em):
    if not em or em == "null": return "Chưa có"
    if "\~" in em: return em[:3] + "~~" + em.split("\~")[1]
    return em

def mask_phone(ph):
    if not ph or ph == "null": return "Chưa liên kết"
    if len(ph) >= 6: return ph[:3] + "***" + ph[-2:]
    return ph

def is_admin(user_id):
    return user_id in admins or user_id == OWNER_ID

def is_group_allowed(chat_id):
    return chat_id in allowed_groups

async def check_permissions(update: Update):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if update.effective_chat.type == "private":
        user_list.add(user_id)
    else:
        allowed_groups.add(chat_id)  # Tự động nhớ nhóm

    if update.effective_chat.type == "private":
        if not is_admin(user_id):
            await update.message.reply_text("🚫 <b>QUYỀN TRUY CẬP BỊ TỪ CHỐI</b>\n\n❌ Chỉ admin hoặc người được cấp quyền mới được dùng lệnh này\n💡 Liên hệ admin @Baohoazz1 để được cấp quyền", parse_mode="HTML")
            return False
    else:
        if not is_group_allowed(chat_id):
            await update.message.reply_text(f"⚠️ <b>BOT CHƯA ĐƯỢC CẤP QUYỀN TRONG NHÓM NÀY</b>\n\nID Nhóm: <code>{chat_id}</code>", parse_mode="HTML")
            return False
    return True

async def check_user_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return True  # Hiện tại cho phép luôn

# --- LỆNH THÔNG BÁO ---
async def thongbao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    if not context.args:
        await update.message.reply_text("❌ Nhập nội dung: /thongbao [Nội dung]")
        return
    
    msg_to_send = " ".join(context.args)
    full_msg = f"📣 <b>THÔNG BÁO TỪ ADMIN</b>\n━━━━━━━━━━━━━━━\n\n{msg_to_send}\n\n<i>Cảm ơn bạn đã sử dụng dịch vụ!</i>"
    
    targets = user_list.union(allowed_groups)
    success, fail = 0, 0
    
    status_msg = await update.message.reply_text("📤 <b>Đang gửi thông báo...</b>", parse_mode="HTML")
    
    for target in targets:
        try:
            await context.bot.send_message(chat_id=target, text=full_msg, parse_mode="HTML")
            success += 1
            await asyncio.sleep(0.1)
        except:
            fail += 1
            
    await status_msg.edit_text(f"✅ <b>Gửi hoàn tất!</b>\n\nThành công: {success}\nThất bại: {fail}", parse_mode="HTML")

# --- LỆNH START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_permissions(update): return
    msg = (
        "┏━━━━━━━━━━━━━━━━━━┓\n"
        "┃    🌟 <b>BOT FREE FIRE OB54</b> 🌟    ┃\n"
        "┗━━━━━━━━━━━━━━━━━━┛\n\n"
        "👋 <b>Chào mừng bạn đến với Bot By Dev !</b>\n\n"
        "📜 <b>Danh Sách Lệnh:</b>\n"
        "🔹 <code>/ban &lt;token&gt;</code>\n"
        "🔹 <code>/checkinfo &lt;uid&gt;</code>\n"
        "🔹 <code>/checkmxt &lt;token&gt;</code>\n"
    )
    if is_admin(update.effective_user.id):
        msg += (
            "\n⚡ <b>MENU ADMIN:</b>\n"
            "├ <b>Admin:</b> /addadmin, /xoaadmin, /thongbao\n"
            "└ <b>Nhóm:</b> /addnhom, /xoanhom\n"
            "━━━━━━━━━━━━━━━\n"
            "😤 <b>Admin:</b> @......"
        )
    await update.message.reply_text(msg, parse_mode="HTML")

# --- LỆNH BAN ---
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_permissions(update): return
    if not context.args:
        await update.message.reply_text("❌ Dùng: /ban (access_token)")
        return

    token = context.args[0]
    msg_loading = await update.message.reply_animation(animation=GIF_LOADING, caption="🚫 <b>Đang gửi request BAN OB54...</b>", parse_mode="HTML")

    try:
        response = requests.get(f"{API_BAN_URL}{token}", timeout=15)
        try:
            data = response.json()
            success = data.get("success", False)
            err_msg = data.get("message", "Token lỗi hoặc đã die")
        except:
            success = False
            err_msg = "Lỗi phản hồi từ Server OB54"

        try: 
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_loading.message_id)
        except: 
            pass

        if not success:
            cap = f"❌ <b>BAN THẤT BẠI</b>\n\n<blockquote>└ {err_msg}</blockquote>"
            try: await update.message.reply_animation(animation=GIF_HU, caption=cap, parse_mode="HTML")
            except: await update.message.reply_text(cap, parse_mode="HTML")
        else:
            cap = (f"🔥 <b>BAN THÀNH CÔNG OB54</b>\n\n"
                   f"<blockquote>├ 🔑 Token: <code>{token[:10]}******</code>\n"
                   f"├ 🚫 Trạng thái: Đã BAN\n"
                   f"└ 💀 Acc đi bụi tạm 7 ngày rồi 😆</blockquote>\n💀 Credit By BaoHoa 🫵")
            try: await update.message.reply_animation(animation=GIF_BAN, caption=cap, parse_mode="HTML")
            except: await update.message.reply_text(cap, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi hệ thống: <code>{e}</code>", parse_mode="HTML")

# --- LỆNH CHECK INFO ---
async def checkinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        if not is_group_allowed(update.effective_chat.id):
            await update.message.reply_text("❌ Bot Hiện Chưa Được Cấp Quyền Sử Dụng Trong Nhóm Này.")
            return
    else:
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("🚫 Chỉ admin mới được dùng lệnh này trong chat riêng!")
            return

    if not context.args:
        await update.message.reply_html("⚠️ <b>Sai Cú Pháp!</b>\nVui lòng nhập: <code>/checkinfo [uid]</code>")
        return

    uid = context.args[0]
    waiting_msg = await update.message.reply_text(f"⏳ Đang truy xuất thông tin UID: {uid}... (OB54)")

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(API_REGION.format(uid=uid))
            
            if response.status_code == 200:
                data = response.json()
                
                if "error" in data or data.get("status") == "error":
                    await waiting_msg.edit_text(f"❌ <b>Lỗi:</b> {data.get('message', 'Không tìm thấy thông tin')}", parse_mode="HTML")
                    return
                
                name = data.get("name", "Không rõ")
                level = data.get("level", "0")
                exp = data.get("exp", 0)
                likes = data.get("likes", 0)
                region = data.get("region", "N/A")
                create_at = data.get("create_at", "N/A")
                last_login = data.get("last_login", "N/A")
                
                try:
                    info_response = await client.get(API_CHECK_INFO.format(uid=uid))
                    if info_response.status_code == 200:
                        info_data = info_response.json()
                        if not name or name == "Không rõ":
                            name = info_data.get("name", name)
                except:
                    pass

                info_text = (
                    f"🎮 <b>THÔNG TIN NGƯỜI CHƠI OB54</b>\n"
                    f"<blockquote>"
                    f"👤 Tên: <b>{name}</b>\n"
                    f"🆔 UID: <code>{uid}</code>\n"
                    f"🌍 Khu vực: <code>{region}</code>\n"
                    f"⭐ Cấp độ: <code>{level}</code>\n"
                    f"🔥 EXP: <code>{exp:,}</code>\n"
                    f"❤️ Lượt thích: <code>{likes:,}</code>\n"
                    f"📅 Ngày tạo: <code>{create_at}</code>\n"
                    f"⏱ Đăng nhập cuối: <code>{last_login}</code>"
                    f"</blockquote>\n"
                    f"<i>🔄 Phiên bản OB54</i>"
                )
                await waiting_msg.edit_text(info_text, parse_mode="HTML")
            else:
                await waiting_msg.edit_text(f"❌ <b>Lỗi kết nối API!</b>\nMã lỗi: {response.status_code}", parse_mode="HTML")
                
    except httpx.TimeoutException:
        await waiting_msg.edit_text("⏰ <b>Request timeout!</b> Vui lòng thử lại sau.", parse_mode="HTML")
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ <b>Lỗi hệ thống:</b> <code>{str(e)}</code>", parse_mode="HTML")

# --- LỆNH CHECK MXT ---
async def checkmxt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_permissions(update): return
    if not context.args:
        await update.message.reply_text("⚠️ <b>Cách dùng:</b> /checkmxt [Token]", parse_mode="HTML")
        return

    token = context.args[0]
    msg_wait = await update.message.reply_text("🔍 <b>Đang kiểm tra thông tin...</b>", parse_mode="HTML")
    
    try:
        data = requests.get(f"{API_GARENA}&access_token={token}", timeout=15).json()
        email = data.get("email") or "null"
        mobile = data.get("mobile") or "null"
        email_to_be = data.get("email_to_be") or "Không có"
        mobile_to_be = data.get("mobile_to_be") or "Không có"

        res_text = (
            f"📊 <b>KẾT QUẢ CHECK MXT</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<blockquote>🔑 Token: <code>{token[:10]}...</code></blockquote>\n\n"
            f"<blockquote>📧 Email hiện tại: <code>{mask_email(email)}</code>\n"
            f"📱 Mobile: <code>{mask_phone(mobile)}</code></blockquote>\n\n"
            f"<blockquote>📧 Email chờ: {email_to_be}\n📱 Mobile chờ: {mobile_to_be}</blockquote>\n\n"
            f"<blockquote>⏳ Thời gian chờ: {data.get('request_exec_countdown', 0)} giây\n"
            f"📌 Trạng thái: {'✅ Thành công' if data.get('result') == 0 else '❌ Thất bại'}</blockquote>\n\n"
            f"🌺 Credit By <b>@Baohoazz1</b> 🌺"
        )
        await msg_wait.edit_text(res_text, parse_mode="HTML")
    except Exception as e:
        await msg_wait.edit_text(f"❌ Lỗi Check MXT: {str(e)}")

# --- QUẢN LÝ ADMIN & NHÓM ---
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try:
        new_id = int(context.args[0])
        admins.add(new_id)
        await update.message.reply_text(f"✅ Đã thêm Admin: <code>{new_id}</code>", parse_mode="HTML")
    except:
        await update.message.reply_text("❌ Sai cú pháp!")

async def xoa_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try: 
        target_id = int(context.args[0])
        if target_id != OWNER_ID: 
            admins.discard(target_id)
            await update.message.reply_text(f"🗑️ Đã xóa Admin: <code>{target_id}</code>", parse_mode="HTML")
    except:
        await update.message.reply_text("❌ Sai cú pháp!")

async def add_nhom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        gid = int(context.args[0]) if context.args else update.effective_chat.id
        allowed_groups.add(gid)
        await update.message.reply_text(f"✅ Đã thêm nhóm: <code>{gid}</code>", parse_mode="HTML")
    except:
        await update.message.reply_text("❌ Sai cú pháp!")

async def xoanhom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        gid = int(context.args[0]) if context.args else update.effective_chat.id
        allowed_groups.discard(gid)
        await update.message.reply_text(f"🗑️ Đã xóa nhóm: <code>{gid}</code>", parse_mode="HTML")
    except:
        await update.message.reply_text("❌ Sai cú pháp!")

def main():
    # Khởi chạy server ẩn để giữ bot online 24/7
    keep_alive()

    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("checkinfo", checkinfo))
    app.add_handler(CommandHandler("checkmxt", checkmxt))
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CommandHandler("xoaadmin", xoa_admin))
    app.add_handler(CommandHandler("addnhom", add_nhom))
    app.add_handler(CommandHandler("xoanhom", xoanhom))
    app.add_handler(CommandHandler("thongbao", thongbao))

    print("🤖 Bot OB54 đang chạy...")
    app.run_polling()

if __name__ == '__main__':
    main()
