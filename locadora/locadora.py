"""Locadora — agregado raiz que orquestra veículos, clientes e locações.

Concentra as operações que envolvem **interação entre múltiplas classes**
(ex.: ``criar_locacao`` liga Veículo + Cliente + Locação e aplica as regras de
disponibilidade, cálculo polimórfico de diária e desconto por tipo de cliente).
"""
from datetime import timedelta

from .enums import StatusLocacao
from .excecoes import EntidadeNaoEncontradaError, VeiculoIndisponivelError
from .locacao import Locacao


class Locadora:
    """Locadora de veículos: mantém o acervo e as locações."""

    def __init__(self, nome="Locadora"):
        self.nome = nome
        self.veiculos = []
        self.clientes = []
        self.locacoes = []
        self._proximo_id_cliente = 1
        self._proximo_id_locacao = 1

    # --- veículos (CRUD) ---

    def cadastrar_veiculo(self, veiculo):
        if self._achar_veiculo(veiculo.placa) is not None:
            raise VeiculoIndisponivelError(
                f"Já existe veículo com a placa {veiculo.placa}.")
        self.veiculos.append(veiculo)
        return veiculo

    def buscar_veiculo(self, placa):
        v = self._achar_veiculo(placa)
        if v is None:
            raise EntidadeNaoEncontradaError(f"Veículo {placa} não encontrado.")
        return v

    def remover_veiculo(self, placa):
        v = self.buscar_veiculo(placa)
        if not v.disponivel:
            raise VeiculoIndisponivelError(
                f"Veículo {placa} está locado e não pode ser removido.")
        self.veiculos.remove(v)

    def veiculos_disponiveis(self):
        return [v for v in self.veiculos if v.disponivel]

    def _achar_veiculo(self, placa):
        return next((v for v in self.veiculos if v.placa == placa), None)

    # --- clientes (CRUD) ---

    def cadastrar_cliente(self, cliente):
        cliente.id_cliente = self._proximo_id_cliente
        self._proximo_id_cliente += 1
        self.clientes.append(cliente)
        return cliente

    def buscar_cliente(self, id_cliente):
        c = next((c for c in self.clientes if c.id_cliente == id_cliente), None)
        if c is None:
            raise EntidadeNaoEncontradaError(
                f"Cliente #{id_cliente} não encontrado.")
        return c

    def remover_cliente(self, id_cliente):
        c = self.buscar_cliente(id_cliente)
        ativa = any(l.cliente is c and l.status in
                    (StatusLocacao.RESERVADA, StatusLocacao.PAGA,
                     StatusLocacao.ATIVA) for l in self.locacoes)
        if ativa:
            raise VeiculoIndisponivelError(
                f"Cliente #{id_cliente} tem locação em aberto.")
        self.clientes.remove(c)

    # --- locações (operações entre múltiplas classes + regras) ---

    def criar_locacao(self, placa, id_cliente, data_inicio, dias):
        veiculo = self.buscar_veiculo(placa)
        cliente = self.buscar_cliente(id_cliente)
        if not veiculo.disponivel:
            raise VeiculoIndisponivelError(
                f"Veículo {placa} não está disponível para locação.")
        data_prevista = data_inicio + timedelta(days=dias)
        loc = Locacao(self._proximo_id_locacao, veiculo, cliente,
                      data_inicio, data_prevista, dias)
        self._proximo_id_locacao += 1
        veiculo.disponivel = False
        self.locacoes.append(loc)
        return loc

    def buscar_locacao(self, id_locacao):
        l = next((l for l in self.locacoes if l.id_locacao == id_locacao), None)
        if l is None:
            raise EntidadeNaoEncontradaError(
                f"Locação #{id_locacao} não encontrada.")
        return l

    def pagar_locacao(self, id_locacao, forma):
        loc = self.buscar_locacao(id_locacao)
        loc.pagar(forma)
        return loc

    def retirar_veiculo(self, id_locacao):
        loc = self.buscar_locacao(id_locacao)
        loc.retirar()
        return loc

    def devolver_veiculo(self, id_locacao, data_real):
        loc = self.buscar_locacao(id_locacao)
        multa = loc.finalizar(data_real)
        loc.veiculo.disponivel = True
        loc.cliente.qtd_locacoes += 1  # conta para o desconto-fidelidade
        return multa

    def cancelar_locacao(self, id_locacao):
        loc = self.buscar_locacao(id_locacao)
        loc.cancelar()
        loc.veiculo.disponivel = True
        return loc

    def locacoes_ativas(self):
        return [l for l in self.locacoes
                if l.status in (StatusLocacao.RESERVADA, StatusLocacao.PAGA,
                                StatusLocacao.ATIVA)]

    def faturamento(self):
        return sum(l.valor_total for l in self.locacoes
                   if l.status == StatusLocacao.FINALIZADA)
