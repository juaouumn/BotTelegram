import logging
import requests
import json
import time
import os
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, PicklePersistence
from openai import OpenAI

# CONFIGURAÇÕES
TELEGRAM_TOKEN = "Coloque seu token telegram aqui"

# LISTA DE USUÁRIOS AUTORIZADOS

AUTHORIZED_USER_IDS = ["Coloque seu id do telegram aqui"] 

# --- CHAVE DE API DO GROQ ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "Coloque seu API groq aqui")

#INICIALIZAÇÃO DOS SERVIÇOS
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

#CLIENTE CONFIGURADO PARA A ROTA DO GROQ
try:
    groq_client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY,
    )
except Exception as e:
    logging.error(f"Não foi possível inicializar o cliente do Groq: {e}")
    groq_client = None

#FUNÇÕES DO BOT

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia a mensagem de boas-vindas."""
    user = update.effective_user
    welcome_msg = (
        f"👋 Olá {user.first_name}! Eu sou a Yara, sua assistente de pesquisas com a IA Llama 3 (via Groq).\n\n"
        "As minhas respostas são super rápidas! Mantenho o contexto da nossa conversa. Se quiser começar de novo, use o comando /reset.\n\n"
        "**Comandos:**\n"
        "  `pesquisar <termo>` - Para buscar na Wikipedia\n"
        "  `/ajuda` - Para ver esta mensagem\n"
        "  `/reset` - Para limpar a memória da conversa"
    )
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

async def reset_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Limpa o histórico de conversa do usuário."""
    if 'history' in context.user_data:
        del context.user_data['history']
    await update.message.reply_text("🤖 O histórico da nossa conversa foi limpo. Podemos começar uma nova!")

async def execute_wikipedia_search(update: Update, query: str) -> None:
    """Busca um termo na Wikipedia."""
    await update.message.reply_text(f"🔎 Pesquisando por '{query}' na Wikipedia...")
    try:
        url = f"https://pt.wikipedia.org/wiki/{query.replace(' ', '_')}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        content = ""
        for paragraph in soup.find_all('p'):
            if len(content.split('\n\n')) >= 4: break
            text = paragraph.get_text().strip()
            if text and len(text) > 50: content += text + "\n\n"
        if not content: raise ValueError("Nenhum conteúdo encontrado")
        resposta = f"📚 *{query.capitalize()}*\n\n{content[:1000]}...\n\n🔗 *Leia mais:* {url}"
        await update.message.reply_text(resposta, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Erro na pesquisa: {e}")
        await update.message.reply_text(f"❌ Não encontrei resultados para '{query}'.\nTente termos mais específicos.")

async def execute_ai_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Função principal da IA. Mantém o histórico e responde usando o Groq."""
    if not groq_client:
        await update.message.reply_text("⚠️ A funcionalidade de IA não está configurada corretamente.")
        return

    question = update.message.text
    await update.message.chat.send_action(action='typing')

    if 'history' not in context.user_data:
        context.user_data['history'] = [
            {"role": "system", "content": "Você é Yara, uma assistente de IA prestativa. Responda sempre em português do Brasil."},
        ]
    
    context.user_data['history'].append({"role": "user", "content": question})

    try:
        model_to_use = "llama3-8b-8192"
        completion = groq_client.chat.completions.create(
            model=model_to_use,
            messages=context.user_data['history'],
            stream=False,
            max_tokens=1024,
            temperature=0.7,
        )
        answer = completion.choices[0].message.content
        context.user_data['history'].append({"role": "assistant", "content": answer})
        await update.message.reply_text(answer.strip())
        
    except Exception as e:
        logging.error(f"Erro na API do Groq: {e}")
        await update.message.reply_text("❌ Ocorreu um erro ao processar a sua pergunta. Verifique a sua chave de API ou tente novamente num instante.")
        context.user_data['history'].pop()

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lida com todas as mensagens de texto, direcionando para a função correta."""
    message_text = update.message.text.lower().strip()
    
    if message_text.startswith('pesquisar '):
        query = update.message.text.strip()[10:]
        if not query:
            await update.message.reply_text("Por favor, digite o que deseja pesquisar.\nEx: pesquisar Python")
            return
        await execute_wikipedia_search(update, query)
        return

    await execute_ai_query(update, context)

async def block_unauthorized_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia uma mensagem de bloqueio para usuários não autorizados."""
    logging.warning(f"Acesso negado para o usuário {update.effective_user.id} ({update.effective_user.username})")
    await update.message.reply_text("❌ Desculpe, você não tem permissão para usar este bot.")

def main() -> None:
    """Configura e inicia o bot com persistência de dados e restrição de acesso."""
    print("A iniciar o bot...")
    
    persistence = PicklePersistence(filepath="yara_bot_persistence")
    application = Application.builder().token(TELEGRAM_TOKEN).persistence(persistence).build()

    # Filtro para permitir apenas usuários da lista AUTHORIZED_USER_IDS
    authorized_filter = filters.User(user_id=AUTHORIZED_USER_IDS)

    # Adiciona os handlers para usuários autorizados
    application.add_handler(CommandHandler("start", start, filters=authorized_filter))
    application.add_handler(CommandHandler("ajuda", start, filters=authorized_filter))
    application.add_handler(CommandHandler("reset", reset_chat, filters=authorized_filter))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & authorized_filter, handle_text))
    
    # Adiciona um handler para bloquear todos os outros usuários
    application.add_handler(MessageHandler(filters.ALL & ~authorized_filter, block_unauthorized_user))
    
    print(f"🤖 Bot está a funcionar com a API Gratuita do Groq (Llama 3). Pressione Ctrl+C para parar.")
    application.run_polling()

if __name__ == "__main__":
    main()
