"""Telegram interface: chat with HOMA, confirm dangerous actions inline."""
import asyncio
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, MessageHandler, filters)

from config import allowed_telegram_ids, settings
from core import memory, scheduler
from core.agent import Agent
from core.logger import StatusReporter
from core.plugin_loader import load_plugins

log = logging.getLogger("homa.telegram")
_registry = load_plugins()
_pending: dict[str, asyncio.Future] = {}
# Currently-running agent task per chat, so /cancel can stop it.
_running: dict[int, asyncio.Task] = {}


def _authorized(update: Update) -> bool:
    allow = allowed_telegram_ids()
    return (not allow) or (update.effective_user and update.effective_user.id in allow)


async def _confirm_cb_factory(app: Application, chat_id: int):
    async def confirm(tool_name: str, args: dict) -> bool:
        loop = asyncio.get_event_loop()
        fut: asyncio.Future = loop.create_future()
        token = f"{chat_id}:{id(fut)}"
        _pending[token] = fut
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Allow", callback_data=f"ok:{token}"),
            InlineKeyboardButton("❌ Deny", callback_data=f"no:{token}"),
        ]])
        await app.bot.send_message(chat_id,
            f"⚠️ Needs confirmation:\n<b>{tool_name}</b>\n<code>{args}</code>",
            reply_markup=kb, parse_mode="HTML")
        try:
            return await asyncio.wait_for(fut, timeout=120)
        except asyncio.TimeoutError:
            return False
        finally:
            _pending.pop(token, None)
    return confirm


async def on_confirm(update: Update, _ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    decision, token = query.data.split(":", 1)
    fut = _pending.get(token)
    if fut and not fut.done():
        fut.set_result(decision == "ok")
    await query.edit_message_text(
        ("✅ Allowed" if decision == "ok" else "❌ Denied") + " — " + query.message.text)


async def cmd_start(update: Update, _ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🕊 HOMA is online.\nSend any command in plain language.\n"
        "/tools — list capabilities\n/cancel — stop the current command\n"
        "/forget — clear this chat's memory")


async def cmd_tools(update: Update, _ctx: ContextTypes.DEFAULT_TYPE) -> None:
    cats = _registry.categories()
    lines = [f"• <b>{c}</b>: {', '.join(n)}" for c, n in cats.items()]
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def cmd_forget(update: Update, _ctx: ContextTypes.DEFAULT_TYPE) -> None:
    n = memory.clear_history(str(update.effective_chat.id))
    await update.message.reply_text(f"🧹 Cleared {n} messages.")


async def cmd_cancel(update: Update, _ctx: ContextTypes.DEFAULT_TYPE) -> None:
    task = _running.get(update.effective_chat.id)
    if task and not task.done():
        task.cancel()
        await update.message.reply_text("⏹ Cancelling the current command…")
    else:
        await update.message.reply_text("Nothing is running right now.")


async def on_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not _authorized(update):
        await update.message.reply_text("🚫 Not authorized.")
        return
    chat_id = update.effective_chat.id
    command = update.message.text
    status = await update.message.reply_text("🧠 Working...")
    confirm = await _confirm_cb_factory(ctx.application, chat_id)
    agent = Agent(_registry, confirm_cb=confirm)
    reporter = StatusReporter()
    task = asyncio.create_task(agent.run(command, reporter, session=str(chat_id)))
    _running[chat_id] = task
    try:
        result = await task
    except asyncio.CancelledError:
        result = "⏹ Command cancelled."
    except Exception as exc:  # noqa: BLE001
        result = f"Error: {exc}"
    finally:
        _running.pop(chat_id, None)
    await status.edit_text(result[:4000])
    log_text = reporter.summary()
    if len(log_text) < 3500:
        await update.message.reply_text(f"<pre>{log_text}</pre>", parse_mode="HTML")


def build_application() -> Application:
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("tools", cmd_tools))
    app.add_handler(CommandHandler("forget", cmd_forget))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CallbackQueryHandler(on_confirm))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    # Let scheduled jobs push their results back into Telegram.
    async def notifier(target: str, text: str):
        try:
            await app.bot.send_message(int(target), text[:4000])
        except Exception as exc:  # noqa: BLE001
            log.warning("notify failed: %s", exc)
    scheduler.set_notifier(notifier)
    return app
