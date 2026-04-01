"""Telegram bot for founder interaction with PM agent dialog support."""

import asyncio
import logging
import os
import threading
from typing import Optional, List, Dict, Any
from enum import Enum

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config.settings import settings
from src.pipeline import pipeline, Checkpoint
from src.tools.state import state_manager
from src.tools import list_open_issues, create_github_issue
from src.tools.artifact_tools import SaveArtifactTool

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class DialogState(str, Enum):
    """Состояния диалога с пользователем."""
    IDLE = "idle"
    COLLECTING_REQUIREMENTS = "collecting_requirements"
    CONFIRMING_PRD = "confirming_prd"


class TelegramBot:
    """Telegram bot for founder interaction."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.telegram_bot_token
        self.app: Optional[Application] = None
        
        # Auth
        auth_users_str = os.environ.get("AUTHORIZED_USERS", "")
        self.authorized_users: List[int] = []
        if auth_users_str:
            try:
                self.authorized_users = [int(u.strip()) for u in auth_users_str.split(",") if u.strip()]
            except ValueError:
                logger.warning(f"Invalid AUTHORIZED_USERS format: {auth_users_str}")
        logger.info(f"Authorized users: {self.authorized_users}")

        # Dialog state per user
        self.user_states: Dict[int, Dict[str, Any]] = {}
        
        # Active pipelines (issue_number -> thread)
        self.active_pipelines: Dict[str, threading.Thread] = {}

    def is_authorized(self, user_id: int) -> bool:
        if not self.authorized_users:
            logger.warning(f"No authorized users configured. Allowing user {user_id}")
            return True
        return user_id in self.authorized_users

    def get_user_state(self, user_id: int) -> Dict[str, Any]:
        """Get or create user dialog state."""
        if user_id not in self.user_states:
            self.user_states[user_id] = {
                "dialog_state": DialogState.IDLE,
                "requirements_data": {},
                "prd_draft": None,
            }
        return self.user_states[user_id]

    # === COMMANDS ===

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_id = user.id if user else 0
        logger.info(f"/start from User ID: {user_id}")

        if not self.is_authorized(user_id):
            await update.message.reply_text(
                f"⛔ Access denied.\n\n💡 Your Telegram ID: {user_id}\nAdd to AUTHORIZED_USERS env var."
            )
            return

        await update.message.reply_text(
            f"👋 Привет, {user.first_name if user else 'founder'}!\n\n"
            "Я Solo Founder Agents Bot — управляю командой AI-агентов.\n\n"
            "📋 **Команды:**\n"
            "/new — создать новую задачу\n"
            "/status — статус проекта\n"
            "/issues — список задач\n"
            "/run <issue> — запустить задачу\n"
            "/checkpoint — статусы checkpoint'ов\n"
            "/approve — одобрить checkpoint\n"
            "/reject <причина> — отклонить checkpoint\n"
            "/cancel — отменить диалог\n"
            "/help — полная справка",
            parse_mode="Markdown"
        )

    async def new_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Start new task requirements collection."""
        user = update.effective_user
        user_id = user.id if user else 0
        logger.info(f"/new from User ID: {user_id}")

        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔ Access denied")
            return

        state = self.get_user_state(user_id)
        state["dialog_state"] = DialogState.COLLECTING_REQUIREMENTS
        state["requirements_data"] = {}

        await update.message.reply_text(
            "🚀 **Создание новой задачи**\n\n"
            "Расскажи что хочешь создать. Я задам уточняющие вопросы и создам PRD.\n\n"
            "📝 **Опиши свою идею:**\n"
            "- Что за продукт/фича?\n"
            "- Для кого?\n"
            "- Какую проблему решает?",
            parse_mode="Markdown"
        )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_id = user.id if user else 0

        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔ Access denied")
            return

        status = pipeline.get_status()
        stage = status.get('current_stage', 'unknown')
        
        # Map stages to Russian
        stage_names = {
            "idle": "💤 Ожидание",
            "requirements": "📋 Сбор требований",
            "analysis": "🔍 Анализ",
            "architecture": "🏗️ Архитектура",
            "design": "🎨 Дизайн",
            "development": "💻 Разработка",
            "review": "👀 Ревью",
            "testing": "🧪 Тестирование",
            "documentation": "📝 Документация",
            "completed": "✅ Завершено",
        }
        stage_display = stage_names.get(stage, stage)

        message = (
            f"📊 **Статус проекта**\n\n"
            f"📍 Фаза: {stage_display}\n"
            f"📂 Репозиторий: `vovkins/agents-react-native-experiment`\n\n"
            f"Используй /issues чтобы посмотреть задачи"
        )
        await update.message.reply_text(message, parse_mode="Markdown")

    async def issues_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_id = user.id if user else 0

        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔ Access denied")
            return

        issues = list_open_issues()
        if not issues:
            await update.message.reply_text("📭 Нет открытых задач\n\nИспользуй /new чтобы создать новую")
            return

        message = "📋 **Открытые задачи:**\n\n"
        for issue in issues[:10]:
            labels = ", ".join([f"`{l}`" for l in issue.get("labels", [])]) if issue.get("labels") else ""
            message += f"#{issue['number']} — {issue['title']}\n"
            if labels:
                message += f"   🏷️ {labels}\n"
        message += f"\n💡 `/run <номер>` чтобы запустить"
        await update.message.reply_text(message, parse_mode="Markdown")

    async def run_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_id = user.id if user else 0

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

        # Check if already running
        issue_key = str(issue_number)
        if issue_key in self.active_pipelines and self.active_pipelines[issue_key].is_alive():
            await update.message.reply_text(f"⏳ Задача #{issue_number} уже выполняется")
            return

        await update.message.reply_text(
            f"🚀 **Запускаю задачу #{issue_number}**\n\n"
            f"Агенты приступают к работе:\n"
            f"→ PM анализирует требования\n"
            f"→ Architect проектирует\n"
            f"→ Developer реализует\n"
            f"→ QA тестирует\n\n"
            f"Я уведомлю тебя о checkpoint'ах",
            parse_mode="Markdown"
        )
        state_manager.set_task_status(issue_key, "in_progress")

        # Start pipeline in background thread
        chat_id = update.effective_chat.id if update.effective_chat else user_id
        
        def run_pipeline_thread():
            """Run pipeline in background and send updates."""
            import asyncio
            
            # Get PRD content as founder_vision
            founder_vision = "Implement the feature described in docs/prd.md"
            try:
                from src.tools.github_tools import read_file_from_repo
                prd_content = read_file_from_repo("docs/prd.md", "main")
                if prd_content:
                    founder_vision = prd_content[:2000]  # Limit size
            except Exception as e:
                logger.warning(f"Could not read PRD: {e}")

            try:
                # Callback for progress updates
                def on_progress(phase: str, message: str):
                    logger.info(f"Pipeline progress: {phase} - {message}")
                    # Send Telegram update synchronously using run_until_complete
                    async def send_progress():
                        try:
                            await self.app.bot.send_message(
                                chat_id=chat_id,
                                text=f"📊 **{phase.title()}**: {message}",
                                parse_mode="Markdown"
                            )
                        except Exception as e:
                            logger.error(f"Failed to send progress: {e}")
                    # Run in the thread's event loop
                    asyncio.run(send_progress())
                
                # Callback for checkpoints
                def on_checkpoint(checkpoint: Checkpoint, artifacts: list):
                    logger.info(f"Checkpoint reached: {checkpoint}")
                    state_manager.set_checkpoint(
                        checkpoint.value,
                        "pending_review",
                        artifacts
                    )
                    # Send checkpoint notification synchronously
                    async def send_checkpoint():
                        artifact_list = "\n".join([f"  • {a}" for a in artifacts])
                        try:
                            await self.app.bot.send_message(
                                chat_id=chat_id,
                                text=f"🛑 **Checkpoint: {checkpoint.value}**\n\n"
                                     f"Артефакты для проверки:\n{artifact_list}\n\n"
                                     f"✅ `/approve` — одобрить\n"
                                     f"❌ `/reject <причина>` — отклонить",
                                parse_mode="Markdown"
                            )
                        except Exception as e:
                            logger.error(f"Failed to send checkpoint: {e}")
                    # Run in a new event loop (asyncio.run handles loop creation/cleanup)
                    asyncio.run(send_checkpoint())
                
                # Run the pipeline
                result = pipeline.run_full_pipeline(
                    issue_number=issue_number,
                    founder_vision=founder_vision,
                    on_checkpoint=on_checkpoint,
                    on_progress=on_progress,
                )
                
                # Send final result
                async def send_result():
                    if result.get("status") == "complete":
                        pr_urls = result.get("phases", {}).get("implementation", {}).get("pr_url")
                        msg = f"✅ **Задача #{issue_number} завершена!**\n\n"
                        if pr_urls:
                            msg += f"📎 PR: {pr_urls}\n\n"
                        msg += "Все фазы выполнены успешно."
                    else:
                        error = result.get("error", "Unknown error")
                        msg = f"❌ **Ошибка выполнения задачи #{issue_number}**\n\n{error}"
                    
                    try:
                        await self.app.bot.send_message(
                            chat_id=chat_id,
                            text=msg,
                            parse_mode="Markdown"
                        )
                    except Exception as e:
                        logger.error(f"Failed to send result: {e}")
                    
                    state_manager.set_task_status(issue_key, result.get("status", "error"))
                
                asyncio.run(send_result())
                
            finally:
                # Clean up
                if issue_key in self.active_pipelines:
                    del self.active_pipelines[issue_key]

        # Start thread
        thread = threading.Thread(target=run_pipeline_thread, daemon=True)
        self.active_pipelines[issue_key] = thread
        thread.start()

    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Cancel current dialog."""
        user = update.effective_user
        user_id = user.id if user else 0

        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔ Access denied")
            return

        state = self.get_user_state(user_id)
        if state["dialog_state"] == DialogState.IDLE:
            await update.message.reply_text("💤 Нет активного диалога")
            return

        state["dialog_state"] = DialogState.IDLE
        state["requirements_data"] = {}
        state["prd_draft"] = None

        await update.message.reply_text("❌ Диалог отменён")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_id = user.id if user else 0

        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔ Access denied")
            return

        message = (
            "📖 **Справка Solo Founder Agents**\n\n"
            "**Управление задачами:**\n"
            "/new — Создать новую задачу\n"
            "/issues — Открытые задачи\n"
            "/run <номер> — Запустить задачу\n\n"
            "**Мониторинг:**\n"
            "/status — Статус проекта\n"
            "/checkpoint — Checkpoint'ы\n\n"
            "**Управление:**\n"
            "/approve — Одобрить checkpoint\n"
            "/reject <причина> — Отклонить\n"
            "/cancel — Отменить диалог\n\n"
            "**Репозиторий:**\n"
            "github.com/vovkins/agents-react-native-experiment"
        )
        await update.message.reply_text(message, parse_mode="Markdown")

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
        status_emoji = {"pending_review": "⏳", "approved": "✅", "rejected": "❌"}
        
        for cp_id, cp_data in checkpoints.items():
            emoji = status_emoji.get(cp_data.get("status"), "❓")
            message += f"{emoji} **{cp_id}**: `{cp_data.get('status')}`\n"
            if cp_data.get("artifact_url"):
                message += f"   📎 {cp_data['artifact_url']}\n"
        
        message += "\n💡 `/approve` или `/reject <причина>`"
        await update.message.reply_text(message, parse_mode="Markdown")

    async def approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        user_id = user.id if user else 0

        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔ Access denied")
            return

        # Get current checkpoint from state
        state = state_manager.state
        checkpoints = state.get("checkpoints", {})
        
        # Find pending checkpoint
        pending_checkpoint = None
        for cp_id, cp_data in checkpoints.items():
            if cp_data.get("status") == "pending_review":
                pending_checkpoint = cp_id
                break
        
        if not pending_checkpoint:
            await update.message.reply_text("⚠️ Нет checkpoint'ов для одобрения.")
            return
        
        # Approve checkpoint
        state_manager.approve_checkpoint(pending_checkpoint)
        await update.message.reply_text(f"✅ Checkpoint {pending_checkpoint} одобрен! Агенты продолжают работу.")

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

        # Get current checkpoint from state
        state = state_manager.state
        checkpoints = state.get("checkpoints", {})
        
        # Find pending checkpoint
        pending_checkpoint = None
        for cp_id, cp_data in checkpoints.items():
            if cp_data.get("status") == "pending_review":
                pending_checkpoint = cp_id
                break
        
        if not pending_checkpoint:
            await update.message.reply_text("⚠️ Нет checkpoint'ов для отклонения.")
            return
        
        # Reject checkpoint with reason
        state_manager.reject_checkpoint(pending_checkpoint, reason)
        await update.message.reply_text(
            f"❌ Checkpoint {pending_checkpoint} отклонён: {reason}\n\n"
            f"Агенты получат feedback и исправят."
        )

    # === MESSAGE HANDLING ===

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages based on dialog state."""
        user = update.effective_user
        user_id = user.id if user else 0
        text = update.message.text if update.message else ""
        
        logger.info(f"Message from {user_id}: {text[:100]}...")

        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔ Access denied")
            return

        state = self.get_user_state(user_id)
        dialog_state = state["dialog_state"]

        if dialog_state == DialogState.COLLECTING_REQUIREMENTS:
            await self._handle_requirements_input(user_id, text, update)
        elif dialog_state == DialogState.CONFIRMING_PRD:
            await self._handle_prd_confirmation(user_id, text, update)
        else:
            await update.message.reply_text(
                "💬 Я тебя услышал.\n\n"
                "Используй /new чтобы создать задачу\n"
                "Или /help для списка команд"
            )

    async def _handle_requirements_input(self, user_id: int, text: str, update: Update) -> None:
        """Process requirements input from user - step by step dialog."""
        state = self.get_user_state(user_id)
        reqs = state["requirements_data"]
        
        # Step 0: Initial product description
        if "initial_description" not in reqs:
            reqs["initial_description"] = text
            await update.message.reply_text(
                "📝 **Отлично! Теперь уточни детали:**\n\n"
                "1️⃣ Кто целевая аудитория продукта?"
            )
            return
        
        # Step 1: Target audience
        if "target_audience" not in reqs:
            reqs["target_audience"] = text
            await update.message.reply_text(
                "✅ Записал аудиторию.\n\n"
                "2️⃣ Какие ключевые функции обязательны для MVP?"
            )
            return
        
        # Step 2: Key features
        if "key_features" not in reqs:
            reqs["key_features"] = text
            await update.message.reply_text(
                "✅ Записал функции.\n\n"
                "3️⃣ Есть ограничения по стеку/бюджету/срокам?\n"
                "(Напиши 'нет' если ограничений нет)"
            )
            return
        
        # Step 3: Constraints (optional)
        if "constraints" not in reqs:
            reqs["constraints"] = text if text.lower() not in ["нет", "no", "н нету", "-"] else "Нет особых ограничений"
            # All data collected - generate PRD
            await self._generate_prd(user_id, update)

    async def _generate_prd(self, user_id: int, update: Update) -> None:
        """Generate PRD from collected requirements."""
        state = self.get_user_state(user_id)
        reqs = state["requirements_data"]
        
        # Build PRD content from step-by-step collected data
        prd_content = f"""# Product Requirements Document

## 1. Обзор

**Описание:** {reqs.get('initial_description', 'N/A')}

**Статус:** Draft
**Дата:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}

## 2. Целевая аудитория

{reqs.get('target_audience', 'N/A')}

## 3. Ключевые функции

{reqs.get('key_features', 'N/A')}

## 4. Ограничения

{reqs.get('constraints', 'Нет особых ограничений')}

## 5. Технический стек

- Frontend: React Native
- Backend: Node.js
- Styling: Tailwind CSS
- UI Kit: shadcn/ui

## 6. Успешные критерии

- MVP готов к тестированию
- Основные фичи работают
- Код протестирован

---
*Сгенерировано PM Agent*
"""

        state["prd_draft"] = prd_content
        state["dialog_state"] = DialogState.CONFIRMING_PRD

        await update.message.reply_text(
            f"📄 **PRD создан!**\n\n"
            f"{prd_content[:500]}...\n\n"
            f"✅ `/confirm` — сохранить в GitHub\n"
            f"❌ `/cancel` — отменить",
            parse_mode="Markdown"
        )

    async def confirm_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Confirm PRD and save to GitHub."""
        user = update.effective_user
        user_id = user.id if user else 0

        if not self.is_authorized(user_id):
            await update.message.reply_text("⛔ Access denied")
            return

        state = self.get_user_state(user_id)
        
        if state["dialog_state"] != DialogState.CONFIRMING_PRD or not state["prd_draft"]:
            await update.message.reply_text("❌ Нет PRD для подтверждения. Используй /new")
            return

        # Save PRD to GitHub using artifact tools
        try:
            save_tool = SaveArtifactTool()
            result = save_tool._run(
                artifact_type="prd",
                content=state["prd_draft"],
                name="PRD"
            )
            
            # Create GitHub issue for tracking
            issue = create_github_issue(
                title="New Feature Request (from PRD)",
                body=f"Created from PRD dialog.\n\nSee docs/prd.md for details.",
                labels=["feature"]
            )
            
            # Reset state
            state["dialog_state"] = DialogState.IDLE
            state["requirements_data"] = {}
            state["prd_draft"] = None

            await update.message.reply_text(
                f"✅ **PRD сохранён в GitHub!**\n\n"
                f"📄 {result}\n"
                f"📋 Issue #{issue.get('number', 'N/A')} создан\n\n"
                f"Используй /run {issue.get('number', '')} чтобы запустить разработку",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to save PRD: {e}")
            await update.message.reply_text(f"❌ Ошибка сохранения: {str(e)[:100]}")

    async def _handle_prd_confirmation(self, user_id: int, text: str, update: Update) -> None:
        """Handle PRD confirmation dialog."""
        if text.lower() in ["confirm", "да", "yes", "подтверждаю"]:
            await self.confirm_command(update, None)
        elif text.lower() in ["cancel", "нет", "no", "отмена"]:
            await self.cancel_command(update, None)
        else:
            await update.message.reply_text(
                "⚠️ Не понял ответ.\n\n"
                "✅ `/confirm` — сохранить PRD\n"
                "❌ `/cancel` — отменить"
            )

    def setup_handlers(self) -> None:
        self.app = Application.builder().token(self.token).build()
        
        # Commands
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("new", self.new_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("issues", self.issues_command))
        self.app.add_handler(CommandHandler("run", self.run_command))
        self.app.add_handler(CommandHandler("checkpoint", self.checkpoint_command))
        self.app.add_handler(CommandHandler("approve", self.approve_command))
        self.app.add_handler(CommandHandler("reject", self.reject_command))
        self.app.add_handler(CommandHandler("cancel", self.cancel_command))
        self.app.add_handler(CommandHandler("confirm", self.confirm_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        
        # Messages
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
