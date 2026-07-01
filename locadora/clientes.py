"""Hierarquia de clientes — polimorfismo #2.

``Cliente`` é abstrata. Pessoa Física e Pessoa Jurídica validam documentos
diferentes (CPF x CNPJ) e aplicam descontos diferentes — comportamento
polimórfico que é, ao mesmo tempo, regra de negócio.
"""
from abc import ABC, abstractmethod

from .excecoes import DocumentoInvalidoError


def _so_digitos(texto):
    return "".join(c for c in texto if c.isdigit())


def _cpf_valido(cpf):
    cpf = _so_digitos(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for tam in (9, 10):
        soma = sum(int(cpf[i]) * (tam + 1 - i) for i in range(tam))
        dig = (soma * 10) % 11 % 10
        if dig != int(cpf[tam]):
            return False
    return True


def _cnpj_valido(cnpj):
    cnpj = _so_digitos(cnpj)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for pesos, tam in ((pesos1, 12), (pesos2, 13)):
        soma = sum(int(cnpj[i]) * pesos[i] for i in range(tam))
        resto = soma % 11
        dig = 0 if resto < 2 else 11 - resto
        if dig != int(cnpj[tam]):
            return False
    return True


class Cliente(ABC):
    """Cliente da locadora. Classe abstrata."""

    def __init__(self, id_cliente, nome, telefone, qtd_locacoes=0):
        self.id_cliente = id_cliente
        self.nome = nome
        self.telefone = telefone
        self.qtd_locacoes = qtd_locacoes

    @classmethod
    def vazio(cls):
        return cls(id_cliente=0, nome="", telefone="")

    @abstractmethod
    def tipo(self):
        """Nome do tipo de cliente (ex.: 'PF')."""

    @abstractmethod
    def documento(self):
        """Documento de identificação (CPF ou CNPJ)."""

    @abstractmethod
    def validar_documento(self):
        """Valida o documento; levanta DocumentoInvalidoError se inválido."""

    @abstractmethod
    def calcular_desconto(self, valor):
        """Valor (R$) de desconto a aplicar sobre ``valor`` — regra própria."""

    # --- leitura/escrita via operadores ---

    def ler(self, console):
        self.nome = console.texto("Nome")
        self.telefone = console.texto("Telefone")
        self._ler_especifico(console)
        self.validar_documento()  # regra de negócio na entrada de dados

    @abstractmethod
    def _ler_especifico(self, console):
        ...

    def exibir(self):
        return (f"[{self.tipo()}] #{self.id_cliente} {self.nome} "
                f"| {self.documento()} | tel {self.telefone} "
                f"| {self.qtd_locacoes} locação(ões)")

    # --- persistência ---

    def to_dict(self):
        d = {
            "_tipo": self.tipo(),
            "id_cliente": self.id_cliente,
            "nome": self.nome,
            "telefone": self.telefone,
            "qtd_locacoes": self.qtd_locacoes,
        }
        d.update(self._dict_especifico())
        return d

    @abstractmethod
    def _dict_especifico(self):
        ...


class ClientePF(Cliente):
    """Pessoa Física. Valida CPF; ganha desconto-fidelidade a partir de 3 locações."""

    DESCONTO_FIDELIDADE = 0.10
    MIN_LOCACOES_FIDELIDADE = 3

    def __init__(self, id_cliente, nome, telefone, cpf="", data_nascimento="",
                 qtd_locacoes=0):
        super().__init__(id_cliente, nome, telefone, qtd_locacoes)
        self.cpf = cpf
        self.data_nascimento = data_nascimento

    def tipo(self):
        return "PF"

    def documento(self):
        return f"CPF {self.cpf}"

    def validar_documento(self):
        if not _cpf_valido(self.cpf):
            raise DocumentoInvalidoError(f"CPF inválido: {self.cpf!r}")

    def calcular_desconto(self, valor):
        if self.qtd_locacoes >= self.MIN_LOCACOES_FIDELIDADE:
            return valor * self.DESCONTO_FIDELIDADE
        return 0.0

    def _ler_especifico(self, console):
        self.cpf = _so_digitos(console.texto("CPF"))
        self.data_nascimento = console.texto("Data de nascimento (dd/mm/aaaa)")

    def _dict_especifico(self):
        return {"cpf": self.cpf, "data_nascimento": self.data_nascimento}


class ClientePJ(Cliente):
    """Pessoa Jurídica. Valida CNPJ; recebe desconto corporativo fixo."""

    DESCONTO_CORPORATIVO = 0.15

    def __init__(self, id_cliente, nome, telefone, cnpj="", razao_social="",
                 qtd_locacoes=0):
        super().__init__(id_cliente, nome, telefone, qtd_locacoes)
        self.cnpj = cnpj
        self.razao_social = razao_social

    def tipo(self):
        return "PJ"

    def documento(self):
        return f"CNPJ {self.cnpj}"

    def validar_documento(self):
        if not _cnpj_valido(self.cnpj):
            raise DocumentoInvalidoError(f"CNPJ inválido: {self.cnpj!r}")

    def calcular_desconto(self, valor):
        return valor * self.DESCONTO_CORPORATIVO

    def _ler_especifico(self, console):
        self.cnpj = _so_digitos(console.texto("CNPJ"))
        self.razao_social = console.texto("Razão social")

    def _dict_especifico(self):
        return {"cnpj": self.cnpj, "razao_social": self.razao_social}


_REGISTRO = {"PF": ClientePF, "PJ": ClientePJ}


def cliente_de_dict(d):
    """Reconstrói um Cliente a partir do dict salvo (campo ``_tipo``)."""
    tipo = d.get("_tipo")
    cls = _REGISTRO.get(tipo)
    if cls is None:
        raise DocumentoInvalidoError(f"Tipo de cliente desconhecido: {tipo!r}")
    campos = {k: v for k, v in d.items() if k != "_tipo"}
    return cls(**campos)
