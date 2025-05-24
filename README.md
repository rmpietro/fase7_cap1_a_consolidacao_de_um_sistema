# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# FASE 7 - Cap 1 - A Consolidação de um Sistema

## Nome do grupo

## 👨‍🎓 Integrantes:

- Gustavo Valtrick - RM559575
- Iago Cotta - RM559655
- Pedro Scofield - RM560589
- Rodrigo Mastropietro - RM560081
- Tiago de Andrade Bastos - RM560467

## 👩‍🏫 Professores:

### Tutor(a)

- <a href="">Leonardo Ruiz Orabona</a>

### Coordenador(a)

- <a href="https://www.linkedin.com/in/profandregodoi/">André Godoi</a>

## 📜 Descrição

### Entrega 1: Aprimoramento do Dashboard da Fase 4

Foi criado um dashboard unificado para expor via interface web, usando streamlit, os programas criados nas fases 1, 2 (Sistema de Gestão de Silos e Modelos de Banco de Dados usados nos demais programas), 3 e 6.

Cada um dos programas e entregáveis está estruturado em uma página individualizada com um submenu próprio para acessar cada uma das funcionalidades.

Nos programas em que se exige conexão com Banco de Dados, um formulário para preenchimento de **usuário e senha do BANCO DE DADOS ORACLE DA FIAP**, será apresentado, sem o qual não será possível prosseguir.
A aplicação criará automaticamente as entidades e DER no Banco de Dados para então importar os dados nesse modelo e então as funcionalidades estarem disponíveis.

As credenciais do Banco de Dados acabm sendo gravadas em um arquivo txt na estrutura da pasta do programa para posterior uso no mesmo programa.

**IMPORTANTE**: A página da Fase 7 implementa e executa corretamente o código criado para o treinamento das imagens, validação e todos os passos entregues, porém feitos no Google Colab. Pode demorar de 30 até 60 minutos (ou mais) para executá-los localmente, mas é possível. As imagens e demais arquivos utilizados estão na estrutura de pastas abaixo de /src/fase6 e por esse motivo o download ou clonagem do repositório pode demorar uns 2 min. Recomendamos executar pelo Google Colab no link já passado ou utilizando as pastas e importando o .ipynb constante dessa mesma estrutura de pastas.

#### Link para o vídeo de apresentação do projeto: <a href="https://www.youtube.com/watch?v=IPauWJaBCb8">Video não listado no Youtube</a>

---

### Entrega 2:

Foi implementada integração com o AWS SNS para envio de mensagens por email para cada nova leitura de sensor sendo realizada no programa entregue na FASE 3. Da mesma forma, uma página para cadastro de assinatura de email e envio de mensagem aberta a todos os subscritos foi colocada para teste.

**OBS.: As credencias da conta utilizada na AWS para esse envio precisam estar em um arquivo .env que deve ser criado na raiz do projeto. Essas chaves serão passadas no mesmo arquivo e em um txt que estarão no upload da área de entrega da atividade no portal on.fiap.com.**

## **Abaixo um exemplo desse arquivo .env:**
```
AWS_REGION=us-east-1
AWS_ACCESS_KEY=<CHAVE AQUI>
AWS_SECRET_KEY=<CHAVE SECRETA AQUI>
```

## **Dependências diretas do projeto:**
(Não estão sendo listadas aquelas utilizadas pelo Google Colab no Notebook da Fase 6 e que são transitivas)
- streamlit
- pandas
- plotly
- oracledb
- requests
- boto3
- numpy
- torch
- torchvision
- opencv-python (cv2)
- pillow (PIL)
- matplotlib
- seaborn
- PyYAML (yaml)

## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

- <b>.github</b>: Nesta pasta ficarão os arquivos de configuração específicos do GitHub que ajudam a gerenciar e automatizar processos no repositório.
- <b>assets</b>: aqui estão os arquivos relacionados a elementos não-estruturados deste repositório, como imagens.
- <b>document</b>: não utilizada nesse projeto
- <b>scripts</b>: não utilizada nesse projeto
- <b>src</b>: Todo o código fonte criado para o desenvolvimento do projeto.
- <b>src/faseX</b>: Pastas que contém o código de cada um dos projetos sendo exibidos em cada uma das páginas do Dashboard.
- <b>src/dashboard</b>: Código do Dashboard. Engloba a página inicial e cada uma das páginas sendo exibidas em arquivos distintos
- <b>README.md</b>: arquivo que serve como guia e explicação geral sobre o projeto (o mesmo que você está lendo agora).

## 🗃 Histórico de lançamentos

- 0.1.0 - 23/05/2025

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
