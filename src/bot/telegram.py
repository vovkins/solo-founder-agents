"""Telegram bot for founder interaction."""

import asyncio
import logging
import os
from typing import Optional, List

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config.settings import settings
from src.pipeline import pipeline, PipelineStage, Checkpoint
from src.tools.state import state_manager
from src.tools import get_issue_details, list_open_issues

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for founder interaction."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.telegram_bot_token
        self.app: Optional[Application] = None
        auth_users_str = os.environ.get("AUTHORIZED_USERS", "")
        self.authorized_users: List[int] = []
        if auth_users_str:
            try:
                self.authorized_users = [int(u.strip()) for u in auth_users_str.split(",") if u.strip()]
            except ValueError:
                logger.warning(f"Invalid AUTHORIZED_USERS format: {auth_users_str}")
        logger.info(f"Authorized users: {self.authorized_users}")

    def is_authorized(self, user_id: int) -> bool:
        if not self.authorized_users:
            logger.warning(f"No authorized users configured. Allowing user {user_id}")
            return True
        return user_id in self.authorized_users

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_id = user.id if user else 0
        logger.info(f"/start from User ID: {user_id}, Username: {user.username if user else 'unknown'}")

        if not self.is_authorized(user_id):
            # Show user ID for setup (plain text to avoid HTML parsing issues)
            await update.message.reply_text(
                f"⛔ Access denied.\n\n💡 Your Telegram ID: {user_id}\nAdd to AUTHORIZED_USERS env var to authorize."
            )
            return

        await update.message.reply_text(
            f"👋 Привет!\n\n"
            "Я Solo Founder Agents Bot — помогаю управлять командой AI-агентов.\n\n"
            "📋 Команды:\n"
            "/status — статус проекта\n"
            "/issues — список открытых задач\n"
            "/run <issue> — запустить задачу\n"
            "/checkpoint — статус checkpoint'ов\n"
            "/approve — одобрить checkpoint\n"
            "/reject <причина> — отклонить checkpoint\n"
            "/help — справка"
        )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_id = user.id if user else 0
        logger.info(f"/status from User ID: {user_id}")

        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔ Access denied")
            return

        status = pipeline.get_status()
        message = f"📊 **Статус проекта**\n\n📍 Текущая фаза: `{status.get('current_stage', 'unknown')}`\n"
        await update.message.reply_text(message, parse_mode="Markdown")

    async def issues_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_id = user.id if user else 0
        logger.info(f"/issues from User ID: {user_id}")

        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔ Access denied")
            return

        issues = list_open_issues()
        if not issues:
            await update.message.reply_text("📭 Нет открытых задач")
            return

        message = "📋 **Открытые задачи:**\n\n"
        for issue in issues[:10]:
            message += f"#{issue['number']} — {issue['title']}\n"
        await update.message.reply_text(message, parse_mode="Markdown")

    async def run_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_id = user.id if user else 0
        logger.info(f"/run from User ID: {user_id}, args: {context.args}")

        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔ Access denied")
            return

        if not context.args:
            await update.message.reply_text("❌ Укажи номер задачи: `/run <номер>`", parse_mode="Markdown")
            return

        try:
            issue_number = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Номер задачи должен быть числом")
            return

        await update.message.reply_text(f"🚀 Запускаю задачу #{issue_number}...\nАгенты приступили к работе!")
        state_manager.set_task_status(str(issue_number), "in_progress")

    async def checkpoint_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_id = user.id if user else 0

        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔ Access denied")
            return

        checkpoints = state_manager.state.get("checkpoints", {})
        if not checkpoints:
            await update.message.reply_text("📭 Нет checkpoint'ов для проверки")
            return

        message = "🛑 **Checkpoint'ы:**\n\n"
        for cp_id, cp_data in checkpoints.items():
            status_emoji = {"pending_review": "⏳", "approved": "✅", "rejected": "❌"}.get(cp_data.get("status"), "❓")
            message += f"{status_emoji} **{cp_id}**: `{cp_data.get('status')}`\n"
        await update.message.reply_text(message, parse_mode="Markdown")

    async def approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_id = user.id if user else 0

        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔ Access denied")
            return

        await update.message.reply_text("✅ Checkpoint одобрен!")

    async def reject_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_id = user.id if user else 0

        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔ Access denied")
            return

        if not context.args:
            await update.message.reply_text("❌ Укажи причину: `/reject <причина>`", parse_mode="Markdown")
            return

        reason = " ".join(context.args)
        await update.message.reply_text(f"❌ Checkpoint отклонён: {reason}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_id = user.id if user else 0

        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔ Access denied")
            return

        message = (
            "📖 **Справка Solo Founder Agents**\n\n"
            "**Команды:**\n"
            "/start — Начать работу\n"
            "/status — Статус проекта\n"
            "/issues — Открытые задачи\n"
            "/run <номер> — Запустить задачу\n"
            "/checkpoint — Статус checkpoint'ов\n"
            "/approve — Одобрить checkpoint\n"
            "/reject <причина> — Отклонить checkpoint\n"
            "/help — Эта справка"
        )
        await update.message.reply_text(message, parse_mode="Markdown")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_id = user.id if user else 0
        text = update.message.text if update.message else ""
        logger.info(f"Message from User ID: {user_id}: {text[:50]}...")

        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔ Access denied")
            return

        await update.message.reply_text("💬 Я тебя услышал. Используй /help для списка команд.")

    def setup_handlers(self) -> None:
        self.app = Application.builder().token(self.token).build()
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("issues", self.issues_command))
        self.app.add_handler(CommandHandler("run", self.run_command))
        self.app.add_handler(CommandHandler("checkpoint", self.checkpoint_command))
        self.app.add_handler(CommandHandler("approve", self.approve_command))
        self.app.add_handler(CommandHandler("reject", self.reject_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    def run(self) -> None:
        self.setup_handlers()
        logger.info("Starting Telegram bot...")
        logger.info(f"Authorized users: {self.authorized_users}")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


bot = TelegramBot()

def run_bot() -> None:
    bot.run()

if __name__ == "__main__":
    run_bot()