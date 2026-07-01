"""Exceções personalizadas do domínio da locadora.

Todas herdam de ``LocadoraError`` para que a camada de interface (menu) possa
capturar qualquer erro de regra de negócio com um único ``except``.
"""


class LocadoraError(Exception):
    """Exceção base de todos os erros de negócio da aplicação."""


class DadosInvalidosError(LocadoraError):
    """Dado informado pelo usuário é inválido (tipo, faixa ou formato)."""


class DocumentoInvalidoError(LocadoraError):
    """CPF ou CNPJ com formato/dígitos inválidos."""


class VeiculoIndisponivelError(LocadoraError):
    """Tentativa de locar um veículo que não está disponível."""


class TransicaoInvalidaError(LocadoraError):
    """Transição de estado não permitida para uma locação."""


class EntidadeNaoEncontradaError(LocadoraError):
    """Veículo, cliente ou locação não encontrado na locadora."""
