
##UTILIZADO PARA DEFINIR OS PADROES DE CONFIGURAÇÃO DE ROUTERS DAS UNIDADES, 
# ANTES DE APLICAR VIA SCRIPT AUTOMATIZADO
# DEFINE AS VERIAVEIS POR TERMINAL COM INPUT##
import ipaddress, sys, json, argparse
from pathlib import Path
import tempfile, os

BASE = Path(__file__).resolve().parent
TEMPLATES_DIR = Path(os.environ.get("TPL_DIR") or (BASE / "data"))

class SafeDict(dict):
    def __missing__(self, k):
        return "{" + k + "}"

def listar_templates():
    arquivos = sorted(TEMPLATES_DIR.glob("*.txt"))  # lista *.txt
    if not arquivos:
        raise SystemExit("Nenhum template .txt encontrado em templates/")
    for i, p in enumerate(arquivos, 1):
        print(f"{i}) {p.name}")
    return arquivos


def render_template(path: Path, data: dict) -> str:
    txt = path.read_text(encoding="utf-8")
    return txt.format_map(SafeDict(data))

def derivar_ip_campos(ip: str) -> dict:
    iface = ipaddress.ip_interface(ip)
    ip = iface.ip
    net = iface.network

def run_mkt(dados: dict) -> dict:
    texto = render_template(listar_templates(dados), dados)
    return {
        "status": "ok",
        "preview": texto,                    # conteúdo gerado
        "unidade": dados.get("NOME_PA",""),
        "loja": dados.get("NUM_PA",""),
    }

def carregar_dados_interativo() -> dict:
    # === o que você já faz hoje com input() ===
    dados = {
        "NUM_PA": input("Numero da UNIDADE: ").strip(),
        "NOME_PA": input("Nome da UNIDADE: ").strip(),

    }
    return dados

if __name__ == "__main__":
    # Escolha do template
    templates = listar_templates()
    escolha = int(input("Nº do template: ")) - 1
    tpl = templates[escolha]
  
    # Inputs base (sem duplicar leitura depois)
    dados = {
        "NUM_PA": input("Numero da UNIDADE: ").strip(),
        "NOME_PA": input("Nome da UNIDADE: ").strip(),
        "IDENTIFICACAO": input("IDENTIFICACAO: ").strip(),
        "PARCEIRO": input("PARCEIRO: ").strip(),
        "IP_UNIDADE": input("IP INTERNO DA UNIDADE: ").strip(),
        "IP_VALIDO": input("IP VÁLIDO: ").strip(),
        "GARY_USER": input("User do L2TP GARY: ").strip(),
        "PLANKTON_USER": input("User do L2TP PLANKTON: ").strip(),
        "SENHA_ROUTER": input("Senha do ROUTER: ").strip(),
        "PPPOE_USER": input("User do PPPOE: ").strip(),
        "PPPOE_PASS": input("Senha do PPPOE: ").strip(),
        "VELOCIDADE": input("Velocidade (ex: 50M/10M): ").strip(),
        "VRF": input("VRF: ").strip(),
        "IP_GARY": input("IP_GARY: ").strip(),
        "IP_PLANKTON": input("IP_PLANKTON: ").strip(),
        "AS_LOCAL": input("AS LOCAL: ").strip(),
        "AS_REMOTO": input("AS REMOTO: ").strip(),
    }


    ip_raw = dados["IP_UNIDADE"].split("/")[0].strip()  # ignora /CIDR se vier
    try:
        base = ipaddress.IPv4Address(ip_raw)
        dados["IP_UNIDADE+1"] = str(base + 1)
        dados["IP_UNIDADE-1"] = str(base - 1)
        print(f"✓ IP da UNIDADE+1: {dados['IP_UNIDADE+1']} | IP-1: {dados['IP_UNIDADE-1']}")
    except Exception as e:
        print(f"Aviso: IP inválido para derivação ({e}).")
        # SafeDict manterá {IP_UNIDADE_MAIS_1}/{IP_UNIDADE_MENOS_1} no output


    ip_raw = dados["IP_VALIDO"].split("/")[0].strip()  # ignora /CIDR se vier
    try:
        basev = ipaddress.IPv4Address(ip_raw)
        dados["IP_VALIDO+1"] = str(basev + 1)
        dados["IP_VALIDO-1"] = str(basev - 1)
        print(f"✓ IP VALIDO+1: {dados['IP_VALIDO+1']} | IP-1: {dados['IP_VALIDO-1']}")
    except Exception as e:
        print(f"Aviso: IP inválido para derivação ({e}).")
        # SafeDict manterá {IP_UNIDADE_MAIS_1}/{IP_UNIDADE_MENOS_1} no output



    saida = render_template(tpl, dados)
    print("\n--- Pré-visualização ---\n")
    print(saida)