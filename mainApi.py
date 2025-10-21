

import ipaddress, sys, json, argparse
from pathlib import Path
import tempfile, os

BASE = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE / "data" 

class SafeDict(dict):
    def __missing__(self, k):
        return "{" + k + "}"



def escolher_template(dados: dict) -> Path:
    nome = (dados.get("TEMPLATE") or "").strip()
    if not nome:
        raise SystemExit("O nome do template não foi fornecido.")

    alvo = TEMPLATES_DIR / nome
    if not alvo.exists():
        raise SystemExit(f"Template '{nome}' não encontrado em {TEMPLATES_DIR}.")

    return alvo


def render_template(path: Path, data: dict) -> str:
    txt = path.read_text(encoding="utf-8")
    return txt.format_map(SafeDict(data))

def normalizar_ip_valido(dados: dict, campo: str = "IP_VALIDO"):
    
    valor = (dados.get(campo) or "").strip()
    if not valor:
        return

    try:
        # Detecta se tem máscara
        if "/" in valor:
            rede = ipaddress.ip_network(valor, strict=False)
            dados[campo] = str(rede.network_address)
        else:
            # Apenas valida o IP
            ipaddress.ip_address(valor)
            dados[campo] = valor
    except Exception as e:
        print(f"[WARN] IP inválido em {campo}: {e}", file=sys.stderr)


def derivar_ip_p1_m1(campo_ip: str, prefixo_saida: str, dados: dict):
    """Preenche {prefixo}_P1 e {prefixo}_M1 a partir do dados[campo_ip]."""
    raw = (dados.get(campo_ip) or "").split("/")[0].strip()
    if not raw:
        return
    try:
        base = ipaddress.IPv4Address(raw)
        dados[f"{prefixo_saida}_P1"] = str(base + 1)
        dados[f"{prefixo_saida}_M1"] = str(base - 1)
    except Exception as e:
        print(f"[WARN] IP inválido para derivação em {campo_ip}: {e}", file=sys.stderr)


def derivar_ip_gary_plankton(campo_ip: str, prefixo_saida: str, dados: dict):
    raw = (dados.get(campo_ip) or "").split("/")[0].strip()
    if not raw:
        return
    try:
        ip = ipaddress.IPv4Address(raw)
        ip_int = int(ip)
        #calcula o ultimo octeto como 1
        gary_int = (ip_int & 0xFFFFFF00) | 0x01
        #calcula o penultimo octeto +1 e o ultimo como 1
        plankton_step = ip_int + (1 << 8)                # +256
        plankton_int = (plankton_step & 0xFFFFFF00) | 0x01

        dados[f"{prefixo_saida}_GARY"] = str(ipaddress.IPv4Address(gary_int))
        dados[f"{prefixo_saida}_PLANKTON"] = str(ipaddress.IPv4Address(plankton_int))
    except Exception as e:
        print(f"[WARN] IP inválido para derivação em {campo_ip}: {e}", file=sys.stderr)




def validar_ip_sem_barra(dados: dict, campo: str):
    """Verifica se o campo informado NÃO contém uma barra."""
    valor = (dados.get(campo) or "").strip()
    if valor and "/" in valor:
        raise ValueError(f'O campo "{campo}" nao deve conter mascara de rede "/" \n todos os ips ja sao calculados e derivados automaticamente.')


def run_command(dados: dict, cmd: str) -> dict:
    try:
        validar_ip_sem_barra(dados, "IP_VALIDO")
        validar_ip_sem_barra(dados, "IP_UNIDADE")

        derivar_ip_p1_m1("IP_UNIDADE", "IP_UNIDADE", dados)
        derivar_ip_p1_m1("IP_VALIDO",  "IP_VALIDO",  dados)
        derivar_ip_gary_plankton("IP_UNIDADE", "IP", dados)

        tpl_path = escolher_template(dados)
        preview = render_template(tpl_path, dados)

        # Definir a extensão do arquivo com base no comando
        ext = "rsc" if cmd == "mkt" else "crs"

        # Criar nome do arquivo
        num_pa = dados.get("NUM_PA", "sem_pa")
        identificacao = dados.get("IDENTIFICACAO", "sem_id")
        filename = f"{num_pa}-{identificacao}.{ext}"

        return {
            "status": "ok",
            "preview": preview,                    # conteúdo gerado
            "unidade": dados.get("NOME_PA",""),
            "loja": dados.get("NUM_PA",""),
            "filename": filename,
        }
    except (ValueError, SystemExit) as e:
        return {
            "status": "error",
            "error": str(e),
        }

def carregar_dados_interativo() -> dict:
    # === o que você já faz hoje com input() ===
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
    return {k: input(f"{k}: ").strip() for k in dados}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    normalizar_ip_valido(dados={})
    parser.add_argument("--cmd", default="mkt")
    parser.add_argument("--mode", choices=["auto","interactive","stdin"], default="auto")
    args = parser.parse_args()

    usar_stdin = (args.mode == "stdin") or (args.mode == "auto" and not sys.stdin.isatty())

    if usar_stdin:
        raw = sys.stdin.read() or "{}"
        try:
            dados = json.loads(raw)          # <<< recebe do Node
        except json.JSONDecodeError:
            print(json.dumps({"status": "error", "error": "JSON inválido no stdin"}))
            sys.exit(2)
    else:
        dados = carregar_dados_interativo()  # <<< seu fluxo atual (inputs)

    if args.cmd in ["mkt", "cisco"]:
        result = run_command(dados, args.cmd)
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps({"status":"error","error":f"comando desconhecido: {args.cmd}"}))
        sys.exit(3)


