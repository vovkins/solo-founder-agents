"""Telegram bot for founder interaction."""

import asyncio
import logging
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config.settings import settings
from src.pipeline import pipeline, PipelineStage, Checkpoint
from src.tools.state import state_manager
from src.tools import get_issue_details, list_open_issues

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for founder interaction."""

    def __init__(self, token: Optional[str] = None):
        """Initialize the bot.

        Args:
            token: Telegram bot token (uses settings if not provided)
        """
        self.token = token or settings.telegram_bot_token
        self.app: Optional[Application] = None
        self.authorized_users = []  # Add authorized user IDs

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user = update.effective_user
        await update.message.reply_html(
            f"👋 Привет, {user.mention_html()}!\n\n"
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
        """Handle /status command."""
        status = pipeline.get_status()

        stage_emoji = {
            PipelineStage.REQUIREMENTS.value: "📋",
            PipelineStage.DESIGN.value: "🎨",
            PipelineStage.IMPLEMENTATION.value: "💻",
            PipelineStage.REVIEW.value: "👀",
            PipelineStage.QA.value: "✅",
            PipelineStage.DOCUMENTATION.value: "📝",
            PipelineStage.COMPLETE.value: "🎉",
        }

        emoji = stage_emoji.get(status["current_stage"], "🔄")

        message = f"{emoji} **Статус проекта**\n\n"
        message += f"📍 Текущая фаза: `{status['current_stage']}`\n"

        if status["state"].get("prd_path"):
            message += f"📄 PRD: `{status['state']['prd_path']}`\n"

        if status["state"].get("pr_urls"):
            message += f"🔀 PRs: {len(status['state']['pr_urls'])}\n"

        # Agent status
        agents = status.get("agents", {})
        if agents:
            message += "\n👥 Агенты:\n"
            for agent_name, agent_state in agents.items():
                status_icon = "🟢" if agent_state.get("status") == "idle" else "🟡"
                message += f"  {status_icon} {agent_name}: {agent_state.get('status', 'idle')}\n"

        await update.message.reply_text(message, parse_mode="Markdown")

    async def issues_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /issues command."""
        issues = list_open_issues()

        if not issues:
            await update.message.reply_text("📭 Нет открытых задач")
            return

        message = "📋 **Открытые задачи:**\n\n"
        for issue in issues[:10]:  # Limit to 10
            labels = ", ".join(issue.get("labels", []))
            message += f"#{issue['number']} — {issue['title']}\n"
            if labels:
                message += f"  🏷️ {labels}\n"
            message += f"  🔗 {issue['url']}\n\n"

        if len(issues) > 10:
            message += f"\n_...и ещё {len(issues) - 10} задач_"

        await update.message.reply_text(message, parse_mode="Markdown")

    async def run_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /run command to start a task."""
        if not context.args:
            await update.message.reply_text(
                "❌ Укажи номер задачи: `/run <номер>`",
                parse_mode="Markdown",
            )
            return

        try:
            issue_number = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Номер задачи должен быть числом")
            return

        # Get issue details
        issue = get_issue_details(issue_number)
        if not issue:
            await update.message.reply_text(f"❌ Задача #{issue_number} не найдена")
            return

        await update.message.reply_text(
            f"🚀 Запускаю задачу #{issue_number}...\n\n"
            f"**{issue['title']}**\n\n"
            "Агенты приступили к работе. Я сообщу о результатах!",
            parse_mode="Markdown",
        )

        # Update state
        state_manager.set_task_status(str(issue_number), "in_progress")

    async def checkpoint_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /checkpoint command."""
        checkpoints = state_manager.state.get("checkpoints", {})

        if not checkpoints:
            await update.message.reply_text("📭 Нет checkpoint'ов для проверки")
            return

        message = "🛑 **Checkpoint'ы:**\n\n"
        for cp_id, cp_data in checkpoints.items():
            status_emoji = {
                "pending_review": "⏳",
                "approved": "✅",
                "rejected": "❌",
            }.get(cp_data.get("status"), "❓")

            message += f"{status_emoji} **{cp_id}**\n"
            message += f"  Статус: `{cp_data.get('status')}`\n"
            if cp_data.get("artifacts"):
                message += f"  Артефакты: {len(cp_data['artifacts'])}\n"
            message += "\n"

        await update.message.reply_text(message, parse_mode="Markdown")

    async def approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /approve command."""
        # Get latest pending checkpoint
        checkpoints = state_manager.state.get("checkpoints", {})
        pending = [
            (cp_id, cp_data)
            for cp_id, cp_data in checkpoints.items()
            if cp_data.get("status") == "pending_review"
        ]

        if not pending:
            await update.message.reply_text("❌ Нет checkpoint'ов ожидающих проверки")
            return

        # Approve the first pending checkpoint
        cp_id, _ = pending[0]
        checkpoint = Checkpoint(cp_id)
        pipeline.approve_checkpoint(checkpoint, " ".join(context.args) if context.args else "")

        await update.message.reply_text(f"✅ Checkpoint `{cp_id}` одобрен!", parse_mode="Markdown")

    async def reject_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /reject command."""
        if not context.args:
            await update.message.reply_text(
                "❌ Укажи причину: `/reject <причина>`",
                parse_mode="Markdown",
            )
            return

        reason = " ".join(context.args)

        # Get latest pending checkpoint
        checkpoints = state_manager.state.get("checkpoints", {})
        pending = [
            (cp_id, cp_data)
            for cp_id, cp_data in checkpoints.items()
            if cp_data.get("status") == "pending_review"
        ]

        if not pending:
            await update.message.reply_text("❌ Нет checkpoint'ов ожидающих проверки")
            return

        cp_id, _ = pending[0]
        checkpoint = Checkpoint(cp_id)
        pipeline.reject_checkpoint(checkpoint, reason)

        await update.message.reply_text(
            f"❌ Checkpoint `{cp_id}` отклонён: {reason}",
            parse_mode="Markdown",
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
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
            "/help — Эта справка\n\n"
            "**Workflow:**\n"
            "1. PM собирает требования → PRD\n"
            "2. Analyst декомпозирует → задачи\n"
            "3. Architect создаёт дизайн\n"
            "4. Developer реализует\n"
            "5. Reviewer проверяет\n"
            "6. QA тестирует\n"
            "7. Tech Writer документирует\n\n"
            "**Checkpoints:**\n"
            "🛑 CP1: После PRD\n"
            "🛑 CP2: После System Design\n"
            "🛑 CP3: После Implementation\n"
            "🛑 CP4: После QA\n"
            "🛑 CP5: Финальный релиз"
        )
        await update.message.reply_text(message, parse_mode="Markdown")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle regular messages."""
        # Check if waiting for input (e.g., requirements gathering)
        current_stage = pipeline.current_stage

        if current_stage == PipelineStage.REQUIREMENTS:
            # PM is collecting requirements
            await update.message.reply_text(
                "📝 Записал! PM анализирует ваши требования..."
            )
        else:
            await update.message.reply_text(
                "💬 Я тебя услышал. Используй /help для списка команд."
            )

    def setup_handlers(self) -> None:
        """Set up bot handlers."""
        self.app = Application.builder().token(self.token).build()

        # Command handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("issues", self.issues_command))
        self.app.add_handler(CommandHandler("run", self.run_command))
        self.app.add_handler(CommandHandler("checkpoint", self.checkpoint_command))
        self.app.add_handler(CommandHandler("approve", self.approve_command))
        self.app.add_handler(CommandHandler("reject", self.reject_command))
        self.app.add_handler(CommandHandler("help", self.help_command))

        # Message handler
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    def run(self) -> None:
        """Run the bot."""
        self.setup_handlers()
        logger.info("Starting Telegram bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


# Bot instance
bot = TelegramBot()


def run_bot() -> None:
    """Run the Telegram bot."""
    bot.run()


if __name__ == "__main__":
    run_bot()
