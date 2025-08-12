# Yara Bot

---

### Visão Geral
Este projeto é um bot para Telegram, chamado Yara Bot, que atua como um assistente de pesquisa. Ele utiliza a API do Groq para acessar o modelo de linguagem Llama 3, proporcionando respostas rápidas e contextuais. Além disso, o bot é capaz de realizar buscas e resumir artigos da Wikipedia.

### Funcionalidades

- **Assistente de IA**: Interage com o modelo Llama 3, mantendo o contexto da conversa para um diálogo mais fluido.
- **Pesquisa na Wikipedia**: O comando `pesquisar <termo>` permite buscar e obter um resumo de artigos da Wikipedia em português.
- **Limpeza de Contexto**: O comando `/reset` apaga o histórico da conversa, sendo útil para começar um novo tópico sem interferências.
- **Controle de Acesso**: O bot opera em modo restrito, respondendo apenas a usuários cujos IDs estão explicitamente listados.

### Tecnologias Utilizadas

- **Python**: Linguagem de programação principal.
- **`python-telegram-bot`**: Biblioteca para a criação e gerenciamento do bot no Telegram.
- **`Groq`**: Plataforma de inferência para modelos de linguagem de grande escala (LLMs), usada para o modelo Llama 3.
- **`requests`**: Biblioteca para fazer requisições HTTP, usada na busca da Wikipedia.
- **`BeautifulSoup`**: Biblioteca para extração de dados de arquivos HTML, usada para analisar o conteúdo da Wikipedia.
- **`logging`**: Módulo para registrar eventos e erros da aplicação.
- **`PicklePersistence`**: Usado para manter o estado da conversa e as configurações do bot entre reinícios.

### Como Usar

Para operar o bot, é necessário ser um usuário com permissão, listado em `AUTHORIZED_USER_IDS` no código-fonte.

**Comandos Suportados:**

- `/start` ou `/ajuda`: Exibe a mensagem de boas-vindas e a lista de comandos disponíveis.
- `/reset`: Limpa o histórico de conversa com a IA.
- `pesquisar <termo>`: Realiza uma busca na Wikipedia pelo termo especificado.
- Qualquer outra mensagem de texto é processada pela IA do Groq.

### Configuração

1.  **Instale as dependências** do Python necessárias para o projeto:
    `pip install python-telegram-bot openai beautifulsoup4 requests`
2.  **Credenciais**:
    - Substitua o placeholder `"Coloque seu token telegram aqui"` pelo token fornecido pelo BotFather no Telegram.
    - Substitua o placeholder `"Coloque seu API groq aqui"` pela sua chave de API do Groq.
    - Adicione o seu ID de usuário do Telegram à lista `AUTHORIZED_USER_IDS`.
3.  **Execute o Bot**:
    `python seu_script.py`
