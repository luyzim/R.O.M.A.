# R.O.M.A. - Gerador de Configuração de Roteadores

## Descrição

O R.O.M.A. é uma ferramenta para automatizar a criação de configurações de roteadores para novas unidades/lojas. Ele oferece tanto uma interface de linha de comando (CLI) quanto uma interface web para gerar as configurações a partir de templates.

O projeto utiliza uma combinação de Python para a lógica de geração de configuração e Node.js (com Express) para a interface web.

## Funcionalidades

- Geração de configurações para roteadores Mikrotik (MKT) e Cisco.
- Cálculo e derivação de endereços IP.
- Interface web para preenchimento de dados.
- Interface de linha de comando para uso interativo.

## Estrutura do Projeto

- `main.py`: Script principal para uso via linha de comando (interativo).
- `mainApi.py`: Script Python que recebe dados em JSON e gera a configuração. É chamado pelo servidor Node.js.
- `server.js`: Servidor web em Node.js/Express que serve a interface web e a API.
- `data/`: Contém os templates de configuração (`.txt`).
- `public/`: Contém os arquivos da interface web (HTML, JS).
- `routes/`: Contém as rotas da API do Express.

## Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/luyzim/R.O.M.A.git
    cd R.O.M.A
    ```

2.  **Instale as dependências do Node.js:**
    ```bash
    npm install
    ```

## Como Usar

Existem duas formas de usar o R.O.M.A.:

### 1. Interface Web

1.  **Inicie o servidor:**
    ```bash
    node server.js
    ```

2.  Abra o navegador e acesse `http://localhost:3104`.

3.  Escolha o tipo de configuração (MKT ou Cisco), preencha o formulário e a configuração será gerada.

### 2. Linha de Comando (Interativo)

1.  **Execute o script `main.py`:**
    ```bash
    python main.py
    ```

2.  O script solicitará as informações necessárias no terminal para gerar a configuração.

## Como Contribuir

Contribuições são bem-vindas! Se você tiver sugestões, melhorias ou correções de bugs, siga os passos abaixo:

1.  **Faça um Fork** do repositório.
2.  **Crie uma Branch** para sua feature (`git checkout -b feature/nova-feature`).
3.  **Faça o Commit** de suas mudanças (`git commit -m 'Adiciona nova feature'`).
4.  **Faça o Push** para a sua branch (`git push origin feature/nova-feature`).
5.  **Abra um Pull Request**.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
