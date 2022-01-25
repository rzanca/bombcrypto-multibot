import time
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
import os

ZIP_REPOSITORY_MAIN_URL = 'https://github.com/rzanca/bombcrypto-multibot/archive/refs/heads/main.zip'
EXTRACT_TO = 'C:/'

if os.name != 'nt':
  EXTRACT_TO = '~/'
FINAL_EXPORTED_PATH = '{}bombcrypto-multibot-main/'.format(EXTRACT_TO)


def downloadfromurl(url):
  print('Baixando a versão atualizada de:\n{}'.format(url))
  http_response = urlopen(url)
  return BytesIO(http_response.read())


def unzipto(extract_to, file_bytes=None):
  print('Extraindo arquivos para: {}'.format(extract_to))
  zip = ZipFile(file_bytes)
  zip.extractall(path=extract_to)


def main():
  try:
    os.replace("telegram.yaml", "./configs_backup/telegram.yaml")
    print('Fazendo backup das configurações do Telegram...')
    os.replace("config.yaml", "./configs_backup/config.yaml")
    print('Fazendo backup das configurações variáveis...')
    time.sleep(2)
    zip_content_bytes = downloadfromurl(ZIP_REPOSITORY_MAIN_URL)
    unzipto(extract_to=EXTRACT_TO, file_bytes=zip_content_bytes)
    time.sleep(2)
    print('Atualizado com sucesso na pasta: {}'.format(FINAL_EXPORTED_PATH))
  except Exception as e:
    print('A atualização do bot apresentou problemas...')
    print('Erro: %s' % (str(e)))
  input('Pressione Enter para continuar...')

main()
