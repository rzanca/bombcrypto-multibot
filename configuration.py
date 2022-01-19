import yaml

class Configuration:
  with open('./config.yaml','r',encoding='utf-8') as open_yml:
    c = yaml.safe_load(open_yml)

  threshold = c['threshold']
  home = c['home']
  telegram = c['telegram']