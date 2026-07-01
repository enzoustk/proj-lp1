"""Persistência em arquivos JSON.

Salva o estado da locadora em ``data/*.json`` e o recarrega na inicialização
(requisito g). As locações guardam apenas a placa do veículo e o id do cliente;
ao carregar, as referências são religadas aos objetos já reconstruídos.
"""
import json
import os

from .clientes import cliente_de_dict
from .locacao import Locacao
from .locadora import Locadora
from .veiculos import veiculo_de_dict

PASTA_PADRAO = "data"


class Repositorio:
    """Lê e grava a Locadora em arquivos JSON."""

    def __init__(self, pasta=PASTA_PADRAO):
        self.pasta = pasta
        self.arq_veiculos = os.path.join(pasta, "veiculos.json")
        self.arq_clientes = os.path.join(pasta, "clientes.json")
        self.arq_locacoes = os.path.join(pasta, "locacoes.json")

    def salvar(self, loc):
        os.makedirs(self.pasta, exist_ok=True)
        self._gravar(self.arq_veiculos, [v.to_dict() for v in loc.veiculos])
        self._gravar(self.arq_clientes, [c.to_dict() for c in loc.clientes])
        self._gravar(self.arq_locacoes, [l.to_dict() for l in loc.locacoes])

    def carregar(self, nome="Locadora UFRN"):
        loc = Locadora(nome)
        loc.veiculos = [veiculo_de_dict(d) for d in self._ler(self.arq_veiculos)]
        loc.clientes = [cliente_de_dict(d) for d in self._ler(self.arq_clientes)]

        por_placa = {v.placa: v for v in loc.veiculos}
        por_id = {c.id_cliente: c for c in loc.clientes}
        for d in self._ler(self.arq_locacoes):
            veiculo = por_placa.get(d["placa_veiculo"])
            cliente = por_id.get(d["id_cliente"])
            if veiculo is None or cliente is None:
                continue  # registro órfão (veículo/cliente removido): ignora
            loc.locacoes.append(Locacao.from_dict(d, veiculo, cliente))

        # Restaura os contadores de id para não colidir com o que já existe.
        if loc.clientes:
            loc._proximo_id_cliente = max(c.id_cliente for c in loc.clientes) + 1
        if loc.locacoes:
            loc._proximo_id_locacao = max(l.id_locacao for l in loc.locacoes) + 1
        return loc

    @staticmethod
    def _gravar(caminho, dados):
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _ler(caminho):
        if not os.path.exists(caminho):
            return []
        with open(caminho, encoding="utf-8") as f:
            conteudo = f.read().strip()
        return json.loads(conteudo) if conteudo else []
