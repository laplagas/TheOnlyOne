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
| Comando                | Descrição                       |
| ---------------------- | ------------------------------- |
| `ban` / `/ban`         | Bane um membro do servidor      |
| `unban`                | Remove o banimento de um membro |
| `kick` / `/kick`       | Expulsa um membro do servidor   |
| `clear` / `/clear`     | Apaga mensagens de um canal     |
| `timeout` / `/timeout` | Aplica timeout em um membro     |
| `warn` / `/warn`       | Dá aviso a um membro            |
| `warnings` / `/warnings` | Mostra avisos de um membro (com histórico em DB) |
| `mute` / `/mute`       | Silencia um membro              |
| `unmute` / `/unmute`   | Dessilencia um membro           |

### 🎭 Sistemas Automáticos
| Comando                | Descrição                       |
| ---------------------- | ------------------------------- |
| `reaction_role_setup` | Cria painel de reaction roles    |
| `reaction_role_add` | Adiciona emoji e role ao painel |
| `ticket_panel` | Cria painel para abertura de tickets |
| `ticket_add` / `ticket_remove` | Gerencia acesso ao ticket |
| `ticket_close` | Fecha ticket (armazenado em DB) |

### 📊 Utilitários
| Comando                | Descrição                       |
| ---------------------- | ------------------------------- |
| `ping` / `/ping`       | Retorna latência do bot         |
| `userinfo` / `/userinfo` | Info de um usuário            |
| `serverinfo` / `/serverinfo` | Info do servidor             |
| `help` / `/help`       | Lista de comandos              |

> ⚠️ Comandos de moderação exigem permissões apropriadas.

---

## 🎮 Tipos de Comandos

O bot suporta dois tipos de comandos:

* **Prefixados**: `!ban`, `$clear`
* **Slash Commands**: `/ban`, `/timeout`

Os slash commands oferecem melhor experiência com:

* Autocomplete
* Validação automática
* Interface nativa do Discord

---

## 🧱 Estrutura do Projeto

```
TheOnlyOne/
│
├── src/
│   └── theonlyone/
│       ├── app.py
│       ├── utils/
│       │   ├── logger.py          # Sistema de logging
│       │   └── database.py        # BD com prepared statements
│       └── commands/
│           ├── commands.py        # Comandos prefixados
│           ├── slash_commands.py  # Slash commands
│           ├── reaction_roles.py  # Sistema de reaction roles
│           └── tickets.py         # Sistema de tickets
│
├── data/
│   └── bot.db                     # Banco de dados SQLite
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Requisitos

* Python **3.10+**
* `discord.py`
* `python-dotenv`

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
```

---

## ▶️ Execução

```bash
python src/theonlyone/app.py
```

---

## 🛡️ Permissões Necessárias

O bot precisa das seguintes permissões no servidor:

* Banir membros
* Desbanir membros
* Gerenciar mensagens
* Moderar membros (timeout)

---

## 🧩 Arquitetura

O projeto utiliza o sistema de **Cogs do discord.py**, permitindo:

* Separação de responsabilidades
* Fácil adição de novos comandos
* Melhor manutenção do código

Além disso, o projeto conta com:

* Sistema de logging estruturado
* Separação entre comandos prefixados e slash commands
* Tratamento global de erros
* **Banco de dados SQLite com prepared statements** para persistência segura

---

## 💾 Banco de Dados

O bot utiliza **SQLite** com prepared statements para máxima segurança contra injeção de SQL.

### Tabelas:

- **warns**: Histórico de avisos com razão, moderador e data
- **guild_config**: Configurações por servidor (canal de logs, prefixo, etc)
- **reaction_roles**: Mapeamento emoji → role para automação
- **tickets**: Histórico de tickets criados, fechados e por quem
- **users**: Estatísticas de usuários (XP, level, mensagens)

### Uso no código:

```python
from theonlyone.utils.database import db

# Adicionar aviso
db.add_warn(guild_id=123, user_id=456, moderator_id=789, reason="Spam")

# Obter avisos
warns = db.get_warns(guild_id=123, user_id=456)

# Adicionar XP
db.add_xp(guild_id=123, user_id=456, xp=10)

# Obter leaderboard
leaderboard = db.get_leaderboard(guild_id=123, limit=10)
```

---

## 🧩 Arquitetura

---

## 📈 Roadmap

* [x] Sistema de logs
* [x] Slash commands (`/`)
* [ ] Comandos de moderação avançados (mute, warn)
* [ ] Sistema de permissões customizado
* [ ] Histórico de punições

---

## 🤝 Contribuição

Contribuições são bem-vindas!

1. Fork do projeto
2. Crie uma branch (`feature/minha-feature`)
3. Commit (`git commit -m 'feat: nova feature'`)
4. Push
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT — veja o arquivo `LICENSE` para mais detalhes.

---

## 💡 Observação

Este projeto está em desenvolvimento ativo. Mudanças podem ocorrer com frequência.
