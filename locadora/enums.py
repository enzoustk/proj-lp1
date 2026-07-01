"""Enumerações do sistema. (Não contam como parte das 9 classes exigidas.)"""
from enum import Enum


class StatusLocacao(Enum):
    """Estados pelos quais uma locação pode passar."""
    RESERVADA = "Reservada"
    PAGA = "Paga"
    ATIVA = "Ativa"
    FINALIZADA = "Finalizada"
    CANCELADA = "Cancelada"

    def __str__(self):
        return self.value


class FormaPagamento(Enum):
    """Formas de pagamento aceitas pela locadora."""
    DINHEIRO = "Dinheiro"
    CARTAO = "Cartão"
    PIX = "Pix"

    def __str__(self):
        return self.value
