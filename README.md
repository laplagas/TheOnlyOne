# ⚡ TheOnlyOne

> Bot de moderação para Discord focado em simplicidade, controle e extensibilidade.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 📌 Visão Geral

**TheOnlyOne** é um bot para Discord desenvolvido em Python com foco em comandos essenciais de moderação e utilidades básicas.

O projeto foi projetado para ser:

* Simples de usar
* Seguro em permissões
* Fácil de expandir (arquitetura modular com Cogs)

Ideal tanto para aprendizado quanto para uso real em servidores.

---

## 🚀 Funcionalidades

### 🛡️ Moderação

| Comando                  | Descrição                                                    |
| ------------------------ | ------------------------------------------------------------ |
| `ban` / `/ban`           | Bane um membro do servidor                                   |
| `unban` / `/unban`       | Remove o banimento de um membro                              |
| `kick` / `/kick`         | Expulsa um membro do servidor                                |
| `clear` / `/clear`       | Apaga mensagens de um canal                                  |
| `timeout` / `/timeout`   | Aplica timeout em um membro                                  |
| `warn` / `/warn`         | Dá aviso a um membro                                         |
| `warnings` / `/warnings` | Mostra avisos de um membro (com histórico quando disponível) |
| `mute` / `/mute`         | Silencia um membro                                           |
| `unmute` / `/unmute`     | Dessilencia um membro                                        |

### 🎭 Sistemas Automáticos

| Comando                        | Descrição                            |
| ------------------------------ | ------------------------------------ |
| `reaction_role_setup`          | Cria painel de reaction roles        |
| `reaction_role_add`            | Adiciona emoji e role ao painel      |
| `ticket_panel`                 | Cria painel para abertura de tickets |
| `ticket_add` / `ticket_remove` | Gerencia acesso ao ticket            |
| `ticket_close`                 | Fecha ticket                         |

### ⚙️ Comandos Interativos

| Comando       | Tipo           | Descrição                                      |
| ------------- | -------------- | ---------------------------------------------- |
| `/ticket`     | Modal          | Criar ticket com formulário                    |
| `/roles`      | Select Menu    | Escolher roles automaticamente                 |
| `/report`     | Buttons        | Reportar usuário com confirmação               |
| `/selectticket` | Select Menu  | Categorizar ticket (bug, sugestão, etc)        |
| `/banreview`  | Buttons        | Confirmar/cancelar ban com interface visual    |

### 🎨 Embeds e Eventos

| Comando       | Descrição                                      |
| ------------- | ---------------------------------------------- |
| `/embed`      | Criar embed customizado com modal              |
| `/embed_templates` | Ver templates pré-definidos de embeds   |
| `/embed_list` | Listar embeds salvos do servidor               |
| `/reminder`   | Criar um lembrete com modal                    |
| `/reminders`  | Ver todos seus lembretes                       |
| `/event`      | Criar evento para o servidor                   |
| `/events`     | Ver eventos agendados do servidor              |

### 📊 Utilitários

| Comando                      | Descrição               |
| ---------------------------- | ----------------------- |
| `ping` / `/ping`             | Retorna latência do bot |
| `userinfo` / `/userinfo`     | Info de um usuário      |
| `serverinfo` / `/serverinfo` | Info do servidor        |
| `help` / `/help`             | Lista de comandos       |

> Comandos de moderação exigem permissões apropriadas.

---

## 🎮 Tipos de Comandos

O bot suporta múltiplos tipos de comandos:

### 1. Prefixados
* Sintaxe: `$ban`, `$clear`, `$warn`
* Ideal para usuários experientes
* Suporta argumentos dinâmicos

### 2. Slash Commands
* Sintaxe: `/ban`, `/timeout`, `/userinfo`
* Melhor experiência com autocomplete
* Validação automática de tipos
* Interface nativa do Discord

### 3. Componentes Interativos
* **Modals**: Formulários para criar tickets
* **Select Menus**: Dropdowns para escolher roles ou categorias
* **Buttons**: Confirmações com interface visual
* Melhor UX e feedback do usuário

---

## 🧱 Estrutura do Projeto

```
TheOnlyOne/
│
├── src/
│   └── theonlyone/
│       ├── app.py
│       ├── data/
│       │   ├── __init__.py
│       │   └── database.py        # Camada de banco (MySQL opcional)
│       ├── utils/
│       │   ├── logger.py          # Sistema de logging
│       │   └── __init__.py
│       └── commands/
│           ├── __init__.py
│           ├── commands.py        # Comandos com prefixo ($)
│           ├── moderation.py      # Slash commands de moderação (/)
│           ├── info.py            # Slash commands de informação (/)
│           ├── interactions.py    # Modals, buttons, select menus           
│           ├── utilities.py       # Lembretes, eventos, embeds customizados        
│           ├── reaction_roles.py  # Sistema de reaction roles
│           └── tickets.py         # Sistema de tickets
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Requisitos

* Python **3.10+**
* `discord.py`
* `python-dotenv`
* `mysql-connector-python` (opcional)

---

## 📦 Instalação

```bash
git clone <URL-do-repositório>
cd TheOnlyOne
pip install -r requirements.txt
```

---

## 🔐 Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
TOKEN=seu_token_aqui

# Opcional (MySQL)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=senha
DB_NAME=theonlyone
```

---

## ▶️ Execução

```bash
python src/theonlyone/app.py
```

---

## 🛡️ Permissões Necessárias

O bot precisa das seguintes permissões no servidor:

* Banir membros (`ban members`)
* Desbanir membros (`unban members`)
* Expulsar membros (`kick members`)
* Gerenciar mensagens (`manage messages`)
* Moderar membros (`moderate members` - timeout)
* Gerenciar roles (`manage roles` - mute/unmute)
* Gerenciar canais (`manage channels` - tickets)

---

## 🧩 Arquitetura

O projeto utiliza o sistema de **Cogs do discord.py**, permitindo:

* Separação de responsabilidades
* Fácil adição de novos comandos
* Melhor manutenção do código

Além disso:

* Sistema de logging estruturado
* Separação entre comandos prefixados e slash commands
* Tratamento global de erros
* Camada de banco desacoplada

---

## 💾 Banco de Dados

O bot utiliza **MySQL** para persistência de dados.

### Importante

* O banco é **opcional**
* O bot funciona normalmente **sem banco**
* Quando indisponível, os sistemas utilizam fallback em memória (sem persistência)
* Falhas de conexão não derrubam o bot

### Tabelas

* **warns**
* **guild_config**
* **reaction_roles**
* **tickets**
* **users**

### Uso

```python
from theonlyone.data import db

# Sistema de warns
db.add_warn(guild_id=123, user_id=456, moderator_id=789, reason="Spam")
warns = db.get_warns(guild_id=123, user_id=456)
db.clear_warns(guild_id=123, user_id=456)

# Sistema de leveling
db.add_xp(guild_id=123, user_id=456, xp=10)
stats = db.get_user_stats(guild_id=123, user_id=456)
leaderboard = db.get_leaderboard(guild_id=123, limit=10)

# Configurações
db.set_log_channel(guild_id=123, channel_id=789)
log_channel = db.get_log_channel(guild_id=123)

# Reaction Roles
db.add_reaction_role(guild_id=123, message_id=456, channel_id=789, emoji="🎮", role_id=999)

# Tickets
db.create_ticket(guild_id=123, ticket_id=1, user_id=456, channel_id=789)
db.close_ticket(ticket_id=1, closed_by=456)
```

---

## 📈 Roadmap

* [x] Sistema de logs
* [x] Slash commands
* [x] Estrutura de banco (MySQL)
* [x] Integração completa com banco
* [x] Componentes interativos (modals, buttons, select menus)
* [x] Reorganização e consolidação de comandos
* [x] Embeds customizáveis com templates
* [x] Sistema de lembretes e eventos
* [ ] Persistência de lembretes em banco
* [ ] Notificações automáticas de eventos
* [ ] Sistema de permissões customizado
* [ ] Histórico avançado de punições
* [ ] Sistema de auto-moderação (detecção de spam/palavras proibidas)

---

## 🤝 Contribuição

1. Fork do projeto
2. Crie uma branch (`feature/minha-feature`)
3. Commit (`git commit -m 'feat: nova feature'`)
4. Push
5. Abra um Pull Request

---

## 📄 Licença

Licença MIT.

---

## 💡 Observação

Projeto em desenvolvimento ativo.
