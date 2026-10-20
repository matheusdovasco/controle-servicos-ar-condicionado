"""Controle de Serviços de Ar Condicionado - Versão 2
Novidades: ID, editar, excluir, status pago/pendente,
relatório por mês, validação de data e exportação para Excel (CSV).
Os dados ficam salvos no arquivo servicos.json.
"""
import csv
import json
import os
from datetime import datetime

ARQUIVO = "servicos.json"
TIPOS = ["Instalação", "Limpeza", "Manutenção"]


# ---------- Arquivo ----------
def carregar():
    """Lê os serviços salvos e completa dados que faltam (versão 1)."""
    if not os.path.exists(ARQUIVO):
        return []
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        servicos = json.load(f)
    for i, s in enumerate(servicos, start=1):
        s.setdefault("id", i)
        s.setdefault("pago", False)
    return servicos


def salvar(servicos):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(servicos, f, ensure_ascii=False, indent=2)


def proximo_id(servicos):
    return max((s["id"] for s in servicos), default=0) + 1


# ---------- Entradas com validação ----------
def pedir_data():
    while True:
        texto = input("Data (dd/mm/aaaa): ").strip()
        try:
            datetime.strptime(texto, "%d/%m/%Y")
            return texto
        except ValueError:
            print("Data inválida. Exemplo: 25/10/2026")


def pedir_valor():
    while True:
        try:
            return float(input("Valor (R$): ").replace(",", "."))
        except ValueError:
            print("Valor inválido. Exemplo: 150,50")


def pedir_tipo():
    print("Tipo de serviço:")
    for i, tipo in enumerate(TIPOS, start=1):
        print(f"  {i} - {tipo}")
    while True:
        escolha = input("Escolha o número: ").strip()
        if escolha in ("1", "2", "3"):
            return TIPOS[int(escolha) - 1]
        print("Opção inválida.")


def pedir_id():
    try:
        return int(input("ID do serviço: "))
    except ValueError:
        return None


def achar_por_id(servicos, id_servico):
    for s in servicos:
        if s["id"] == id_servico:
            return s
    return None


# ---------- Mostrar ----------
def mostrar(lista):
    if not lista:
        print("Nenhum serviço encontrado.")
        return
    for s in lista:
        status = "Pago" if s["pago"] else "Pendente"
        print(f"[{s['id']}] {s['data']} | {s['cliente']} | {s['telefone']} | "
              f"{s['tipo']} | R$ {s['valor']:.2f} | {status}")


# ---------- Ações ----------
def cadastrar(servicos):
    print("\n--- Novo serviço ---")
    servicos.append({
        "id": proximo_id(servicos),
        "cliente": input("Nome do cliente: ").strip(),
        "telefone": input("Telefone: ").strip(),
        "tipo": pedir_tipo(),
        "data": pedir_data(),
        "valor": pedir_valor(),
        "pago": False,
    })
    salvar(servicos)
    print("Serviço cadastrado com sucesso!")


def buscar(servicos):
    nome = input("Nome do cliente: ").strip().lower()
    mostrar([s for s in servicos if nome in s["cliente"].lower()])


def editar(servicos):
    mostrar(servicos)
    s = achar_por_id(servicos, pedir_id())
    if not s:
        print("Serviço não encontrado.")
        return
    print("Deixe em branco para manter o valor atual.")
    s["cliente"] = input(f"Cliente [{s['cliente']}]: ").strip() or s["cliente"]
    s["telefone"] = input(f"Telefone [{s['telefone']}]: ").strip() or s["telefone"]
    salvar(servicos)
    print("Serviço atualizado!")


def excluir(servicos):
    mostrar(servicos)
    s = achar_por_id(servicos, pedir_id())
    if not s:
        print("Serviço não encontrado.")
        return
    if input(f"Excluir {s['cliente']}? (s/n): ").lower() == "s":
        servicos.remove(s)
        salvar(servicos)
        print("Serviço excluído.")


def marcar_pago(servicos):
    mostrar([s for s in servicos if not s["pago"]])
    s = achar_por_id(servicos, pedir_id())
    if not s:
        print("Serviço não encontrado.")
        return
    s["pago"] = True
    salvar(servicos)
    print("Marcado como pago!")


def relatorio_mensal(servicos):
    mes = input("Mês e ano (mm/aaaa): ").strip()
    do_mes = [s for s in servicos if s["data"][3:] == mes]
    mostrar(do_mes)
    total = sum(s["valor"] for s in do_mes)
    recebido = sum(s["valor"] for s in do_mes if s["pago"])
    print(f"\nTotal do mês: R$ {total:.2f}")
    print(f"Recebido: R$ {recebido:.2f} | A receber: R$ {total - recebido:.2f}")


def exportar_csv(servicos):
    with open("servicos.csv", "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.writer(f, delimiter=";")
        escritor.writerow(["ID", "Data", "Cliente", "Telefone",
                           "Tipo", "Valor", "Pago"])
        for s in servicos:
            escritor.writerow([s["id"], s["data"], s["cliente"], s["telefone"],
                               s["tipo"], f"{s['valor']:.2f}",
                               "Sim" if s["pago"] else "Não"])
    print("Arquivo servicos.csv criado. Abra no Excel!")


# ---------- Menu ----------
def menu():
    servicos = carregar()
    opcoes = {
        "1": ("Cadastrar serviço", cadastrar),
        "2": ("Listar todos", lambda s: mostrar(s)),
        "3": ("Buscar por cliente", buscar),
        "4": ("Editar serviço", editar),
        "5": ("Excluir serviço", excluir),
        "6": ("Marcar como pago", marcar_pago),
        "7": ("Relatório do mês", relatorio_mensal),
        "8": ("Exportar para Excel (CSV)", exportar_csv),
    }
    while True:
        print("\n=== Controle de Serviços v2 ===")
        for numero, (nome, _) in opcoes.items():
            print(f"{numero} - {nome}")
        print("0 - Sair")
        escolha = input("Escolha: ").strip()

        if escolha == "0":
            print("Até logo!")
            break
        if escolha in opcoes:
            opcoes[escolha][1](servicos)
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()
