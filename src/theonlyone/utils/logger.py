import logging

# Configura o logger principal do projeto com nível INFO e formato padrão.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Cria um logger nomeado para ser usado em todo o bot.
logger = logging.getLogger("theonlyone")
