# OCI Realtime Speech (Whisper) – Exemplo em Python

Este repositório contém um exemplo de aplicação em Python que captura áudio do microfone usando **PyAudio** e envia o stream em tempo real para o serviço **Oracle Cloud Infrastructure (OCI) Speech – Realtime** utilizando o modelo **WHISPER** para transcrição.

O objetivo deste guia é que qualquer pessoa (Windows, macOS ou Linux) consiga:

1. Instalar o **Miniconda**  
2. Importar o **ambiente Conda pronto** deste projeto  
3. Configurar o arquivo `~/.oci/config` com uma **API Key** criada na Console da Oracle  
4. Executar o script de transcrição em tempo real

---

## Sumário

1. [Pré-requisitos](#pré-requisitos)  
2. [Instalação do Miniconda](#instalação-do-miniconda)  
   - [Windows](#windows)  
   - [macos](#macos)  
   - [linux](#linux)  
3. [Criando e ativando o ambiente Conda](#criando-e-ativando-o-ambiente-conda)  
4. [Configurando o arquivo `config` da OCI](#configurando-o-arquivo-config-da-oci)  
   - [4.1 Gerar API Key na Console da OCI](#41-gerar-api-key-na-console-da-oci)  
   - [4.2 Criar diretório e arquivo `config`](#42-criar-diretório-e-arquivo-config)  
   - [4.3 Exemplo de conteúdo do arquivo `config`](#43-exemplo-de-conteúdo-do-arquivo-config)  
   - [4.4 Testar a configuração](#44-testar-a-configuração)  
5. [Executando o script de transcrição em tempo real](#executando-o-script-de-transcrição-em-tempo-real)  

---

## Pré-requisitos

- Uma conta válida na **Oracle Cloud Infrastructure (OCI)** com acesso à região onde o serviço **AI Speech** está disponível (por exemplo, `sa-saopaulo-1`).   
- Permissão para criar **API Keys** no usuário (acesso ao menu *User settings*).   
- Acesso ao repositório deste projeto (via Git).

---

## Instalação do Miniconda

O **Miniconda** é uma distribuição mínima da Anaconda – ele instala apenas o **conda**, o **Python** e alguns pacotes essenciais. É ideal para criar ambientes isolados para este tipo de projeto.   

### Windows

1. Acesse a página oficial do Miniconda:  
   - Busque por “Miniconda download” ou utilize a página principal de instalação.   
2. Baixe o instalador para **Windows (64-bit)** – normalmente um arquivo `.exe`.
3. Execute o instalador e:
   - Aceite a licença.
   - Escolha **Install for Just Me** (recomendado).
   - Mantenha o diretório padrão (ex.: `C:\Users\SeuUsuario\Miniconda3`).
   - Permita que o instalador **adicione o Miniconda ao PATH** ou, pelo menos, habilite a opção “Register Miniconda as the default Python”.
4. Após a instalação, abra o **Anaconda Prompt** ou o **PowerShell** e teste:
   ```bash
   conda --version
````

Se o comando funcionar, o Miniconda está instalado corretamente.

### macOS

1. A partir da página oficial do Miniconda, baixe o instalador para macOS (`.pkg` ou `.sh`).
2. Opção gráfica (`.pkg`):

   * Execute o arquivo `.pkg` e siga os passos do instalador.
3. Opção linha de comando (`.sh`):

   * Abra o **Terminal** e navegue até a pasta onde o instalador foi baixado.
   * Execute:

     ```bash
     bash Miniconda3-latest-MacOSX-x86_64.sh
     ```

     (ajuste o nome do arquivo se for diferente).
   * Aceite a licença e os padrões sugeridos.
4. Feche e reabra o Terminal, depois teste:

   ```bash
   conda --version
   ```

### Linux

1. Baixe o instalador do Miniconda para Linux (`.sh`) a partir da página oficial.
2. No terminal, vá até a pasta onde o arquivo foi salvo e execute:

   ```bash
   bash Miniconda3-latest-Linux-x86_64.sh
   ```

   (ajuste o nome do arquivo conforme o que foi baixado).
3. Aceite a licença e os caminhos padrão.
4. Feche e reabra o terminal.
5. Teste a instalação:

   ```bash
   conda --version
   ```

---

## Criando e ativando o ambiente Conda

> **Observação:** este passo assume que o repositório possui um arquivo de ambiente Conda, por exemplo `environment.yml`, com todas as dependências necessárias (`pyaudio`, `oci`, `oci-ai-speech-realtime`, etc.).

1. **Clone o repositório** (ajuste a URL):

   ```bash
   git clone https://github.com/seu-usuario/seu-repo.git
   cd seu-repo
   ```

2. **Crie o ambiente** a partir do arquivo de configuração (por exemplo, `environment.yml`):

   ```bash
   conda env create -f environment.yml -n oci-realtime-speech
   ```

   * `-f environment.yml`: arquivo de definição do ambiente.
   * `-n oci-realtime-speech`: nome do ambiente Conda (pode ser alterado se desejar).

3. **Ative o ambiente**:

   * Windows (Prompt/PowerShell):

     ```bash
     conda activate oci-realtime-speech
     ```

   * macOS / Linux:

     ```bash
     conda activate oci-realtime-speech
     ```

4. Verifique se o Python e os pacotes principais estão disponíveis:

   ```bash
   python -c "import oci, pyaudio; print('OK')"
   ```

---

## Configurando o arquivo `config` da OCI

O SDK da OCI (e também a CLI) usa um arquivo de configuração chamado `config` para autenticar chamadas à API.
O local padrão do arquivo é:

* **macOS / Linux:** `~/.oci/config`

  * Exemplo: `/Users/seuusuario/.oci/config`
* **Windows (PowerShell / CMD):**

  * `C:\Users\SeuUsuario\.oci\config`

Se a pasta `.oci` não existir, você irá criá-la.

### 4.1 Gerar API Key na Console da OCI

1. Faça login na **Console da OCI**.
2. No canto superior direito, clique no ícone do seu **perfil (usuário)** e selecione **User settings**.
3. No painel esquerdo (*Resources*), clique em **API keys**.
4. Clique em **Add API key**.
5. Escolha a opção **Generate API key pair**:

   * A Console irá gerar um par de chaves (pública e privada) para você.
6. Clique em **Download Private Key** e salve o arquivo `.pem` em um local seguro na sua máquina, por exemplo:

   * macOS / Linux: `/Users/seuusuario/.oci/oci_api_key.pem`
   * Windows: `C:\Users\SeuUsuario\.oci\oci_api_key.pem`
7. Clique em **Add** para concluir a criação da chave.
8. A Console exibirá um **“Configuration file preview”** (trecho de arquivo de configuração) contendo:

   * `user` – OCID do usuário
   * `fingerprint` – fingerprint da chave criada
   * `tenancy` – OCID da tenancy
   * `region` – região atual (ex.: `sa-saopaulo-1`)
   * `key_file` – caminho para o arquivo `.pem` (que você deve ajustar para o caminho real na sua máquina)

Guarde esse snippet: é exatamente o que será colocado no arquivo `config`.

### 4.2 Criar diretório e arquivo `config`

#### macOS / Linux

1. No terminal, crie o diretório `.oci` se ainda não existir:

   ```bash
   mkdir -p ~/.oci
   ```
2. Salve o arquivo de chave privada baixado (`*.pem`) dentro desse diretório (ou em outro local de sua preferência, mas lembre-se de usar o caminho correto em `key_file`).
3. Crie (ou edite) o arquivo `~/.oci/config`:

   ```bash
   nano ~/.oci/config
   ```

   (pode usar `vi`, `vim` ou outro editor de texto se preferir).

#### Windows

1. Crie o diretório `.oci`:

   ```powershell
   mkdir $Env:UserProfile\.oci
   ```
2. Salve o arquivo `.pem` nesse diretório (ex.: `C:\Users\SeuUsuario\.oci\oci_api_key.pem`).
3. Crie/edite o arquivo `C:\Users\SeuUsuario\.oci\config` com um editor de texto (Notepad, VS Code, etc.).

### 4.3 Exemplo de conteúdo do arquivo `config`

Copie o trecho de **Configuration file preview** gerado na Console e cole no arquivo `config`.
Ele será semelhante a isto (exemplo fictício):

```ini
[DEFAULT]
user=ocid1.user.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
fingerprint=12:34:56:78:9a:bc:de:f0:12:34:56:78:9a:bc:de:f0
tenancy=ocid1.tenancy.oc1..bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
region=sa-saopaulo-1
key_file=/Users/seuusuario/.oci/oci_api_key.pem
```

> **Importante:**
>
> * Ajuste o caminho em `key_file` para o local real onde salvou o arquivo `.pem`.
> * Se quiser ter múltiplos perfis, você pode adicionar mais blocos `[PROFILE_NAME]` no mesmo arquivo.

### 4.4 Testar a configuração

Se você tiver o **OCI CLI** instalado, pode testar rapidamente executando:

```bash
oci os ns get
```

* Se o comando retornar um namespace sem erro, a configuração do `config` e da API Key está correta.

Se estiver usando apenas o SDK em Python, você pode fazer um teste simples dentro do ambiente Conda:

```bash
python -c "import oci, pprint; from oci.config import from_file; print(from_file())"
```

Se não houver erro, o SDK conseguiu ler o `~/.oci/config` corretamente.

---

## Executando o script de transcrição em tempo real

Com tudo configurado (conda + OCI `config` + API Key):

1. Certifique-se de estar na pasta do projeto e com o ambiente ativo:

   ```bash
   cd /caminho/para/seu-repo
   conda activate oci-realtime-speech
   ```

2. Verifique se, dentro do código Python, o `COMPARTMENT_ID` está configurado com o OCID do **compartimento correto** da sua tenancy:

   ```python
   COMPARTMENT_ID = "ocid1.compartment.oc1..xxxxxxxxxxxxxxxxxxxx"
   ```

3. Execute o script (ajuste o nome do arquivo, se necessário):

   ```bash
   python realtime_speech.py
   ```

4. Fale no microfone:

   * O script irá capturar o áudio via PyAudio e enviar para o endpoint WebSocket do **OCI Speech Realtime**.
   * Os resultados de transcrição (parciais e finais) serão exibidos no console/log.

---

