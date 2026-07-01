"""Pagamento e Locacao.

``Locacao`` é a classe de **estado dinâmico** exigida pelo enunciado: percorre
RESERVADA → PAGA → ATIVA → FINALIZADA (ou CANCELADA) e as transições são
validadas (não se pode retirar um veículo sem pagar, espelhando o exemplo
"pedido pago primeiro" do PDF).
"""
from datetime import date

from .enums import FormaPagamento, StatusLocacao
from .excecoes import TransicaoInvalidaError


class Pagamento:
    """Pagamento de uma locação."""

    def __init__(self, valor, forma, pago=False):
        self.valor = valor
        self.forma = forma  # FormaPagamento
        self.pago = pago

    def confirmar(self):
        self.pago = True

    def exibir(self):
        estado = "pago" if self.pago else "pendente"
        return f"R$ {self.valor:.2f} via {self.forma} ({estado})"

    def to_dict(self):
        return {"valor": self.valor, "forma": self.forma.name, "pago": self.pago}

    @classmethod
    def from_dict(cls, d):
        return cls(d["valor"], FormaPagamento[d["forma"]], d["pago"])


class Locacao:
    """Contrato de locação de um veículo por um cliente, com estado dinâmico."""

    # Multa por dia de atraso = 50% da diária base do veículo.
    FATOR_MULTA_DIARIA = 0.5

    # Tabela de transições permitidas (máquina de estados).
    _TRANSICOES = {
        StatusLocacao.RESERVADA: {StatusLocacao.PAGA, StatusLocacao.CANCELADA},
        StatusLocacao.PAGA: {StatusLocacao.ATIVA, StatusLocacao.CANCELADA},
        StatusLocacao.ATIVA: {StatusLocacao.FINALIZADA},
        StatusLocacao.FINALIZADA: set(),
        StatusLocacao.CANCELADA: set(),
    }

    def __init__(self, id_locacao, veiculo, cliente, data_inicio,
                 data_prevista_devolucao, dias):
        self.id_locacao = id_locacao
        self.veiculo = veiculo
        self.cliente = cliente
        self.data_inicio = data_inicio
        self.data_prevista_devolucao = data_prevista_devolucao
        self.data_real_devolucao = None
        self.dias = dias
        self.status = StatusLocacao.RESERVADA
        self.pagamento = None
        self.multa = 0.0
        # Valor calculado pela interação veículo (polimórfico) x cliente (desconto).
        self.valor_bruto = veiculo.calcular_valor_diaria(dias)
        self.desconto = cliente.calcular_desconto(self.valor_bruto)
        self.valor_total = self.valor_bruto - self.desconto

    # --- máquina de estados ---

    def _validar_transicao(self, novo):
        if novo not in self._TRANSICOES[self.status]:
            raise TransicaoInvalidaError(
                f"Não é possível ir de {self.status} para {novo} "
                f"(locação #{self.id_locacao})."
            )

    def pagar(self, forma):
        self._validar_transicao(StatusLocacao.PAGA)
        self.pagamento = Pagamento(self.valor_total, forma, pago=True)
        self.status = StatusLocacao.PAGA

    def retirar(self):
        # Regra: só retira o veículo após o pagamento.
        self._validar_transicao(StatusLocacao.ATIVA)
        self.status = StatusLocacao.ATIVA

    def finalizar(self, data_real_devolucao):
        self._validar_transicao(StatusLocacao.FINALIZADA)
        self.data_real_devolucao = data_real_devolucao
        self.multa = self._calcular_multa(data_real_devolucao)
        self.valor_total += self.multa
        self.status = StatusLocacao.FINALIZADA
        return self.multa

    def cancelar(self):
        self._validar_transicao(StatusLocacao.CANCELADA)
        self.status = StatusLocacao.CANCELADA

    def _calcular_multa(self, data_real):
        atraso = (data_real - self.data_prevista_devolucao).days
        if atraso <= 0:
            return 0.0
        return atraso * self.veiculo.valor_diaria_base * self.FATOR_MULTA_DIARIA

    # --- exibição ---

    def exibir(self):
        linhas = [
            f"Locação #{self.id_locacao} | {self.status}",
            f"  Veículo : {self.veiculo.placa} ({self.veiculo.tipo()})",
            f"  Cliente : {self.cliente.nome} ({self.cliente.documento()})",
            f"  Período : {self.data_inicio} -> {self.data_prevista_devolucao} "
            f"({self.dias} dia(s))",
            f"  Valor   : R$ {self.valor_total:.2f} "
            f"(bruto R$ {self.valor_bruto:.2f}, desconto R$ {self.desconto:.2f})",
        ]
        if self.multa:
            linhas.append(f"  Multa   : R$ {self.multa:.2f}")
        if self.pagamento:
            linhas.append(f"  Pagto   : {self.pagamento.exibir()}")
        return "\n".join(linhas)

    # --- persistência (referencia veículo/cliente por chave) ---

    def to_dict(self):
        return {
            "id_locacao": self.id_locacao,
            "placa_veiculo": self.veiculo.placa,
            "id_cliente": self.cliente.id_cliente,
            "data_inicio": self.data_inicio.isoformat(),
            "data_prevista_devolucao": self.data_prevista_devolucao.isoformat(),
            "data_real_devolucao": (self.data_real_devolucao.isoformat()
                                    if self.data_real_devolucao else None),
            "dias": self.dias,
            "status": self.status.name,
            "multa": self.multa,
            "valor_total": self.valor_total,
            "pagamento": self.pagamento.to_dict() if self.pagamento else None,
        }

    @classmethod
    def from_dict(cls, d, veiculo, cliente):
        loc = cls(
            d["id_locacao"], veiculo, cliente,
            date.fromisoformat(d["data_inicio"]),
            date.fromisoformat(d["data_prevista_devolucao"]),
            d["dias"],
        )
        loc.status = StatusLocacao[d["status"]]
        loc.multa = d["multa"]
        loc.valor_total = d["valor_total"]
        if d["data_real_devolucao"]:
            loc.data_real_devolucao = date.fromisoformat(d["data_real_devolucao"])
        if d["pagamento"]:
            loc.pagamento = Pagamento.from_dict(d["pagamento"])
        return loc
