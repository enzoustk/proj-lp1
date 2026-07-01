"""Hierarquia de veículos — polimorfismo #1.

A classe base ``Veiculo`` é abstrata; cada subclasse possui atributos próprios
e sobrescreve ``calcular_valor_diaria`` com sua própria regra de negócio
(atende às Observações 2 e 3 do enunciado: subclasses com membros próprios e
comportamento polimórfico relevante).
"""
from abc import ABC, abstractmethod

from .excecoes import DadosInvalidosError


class Veiculo(ABC):
    """Veículo locável genérico. Classe abstrata."""

    def __init__(self, placa, marca, modelo, ano, valor_diaria_base,
                 disponivel=True):
        self.placa = placa
        self.marca = marca
        self.modelo = modelo
        self.ano = ano
        self.valor_diaria_base = valor_diaria_base
        self.disponivel = disponivel

    @classmethod
    def vazio(cls):
        """Instância em branco para ser preenchida via ``console >> veiculo``."""
        return cls(placa="", marca="", modelo="", ano=0, valor_diaria_base=0.0)

    @abstractmethod
    def tipo(self):
        """Nome do tipo de veículo (ex.: 'Carro')."""

    @abstractmethod
    def calcular_valor_diaria(self, dias):
        """Valor total das diárias para ``dias`` — regra própria de cada tipo."""

    # --- leitura/escrita via operadores (template method) ---

    def ler(self, console):
        self.placa = console.texto("Placa").upper()
        self.marca = console.texto("Marca")
        self.modelo = console.texto("Modelo")
        self.ano = console.inteiro("Ano", minimo=1900)
        self.valor_diaria_base = console.decimal("Valor da diária base (R$)",
                                                 minimo=0.0)
        self._ler_especifico(console)
        self.disponivel = True

    @abstractmethod
    def _ler_especifico(self, console):
        """Lê os campos exclusivos da subclasse."""

    def exibir(self):
        status = "disponível" if self.disponivel else "locado"
        return (f"[{self.tipo()}] {self.placa} - {self.marca} {self.modelo} "
                f"({self.ano}) | diária base R$ {self.valor_diaria_base:.2f} "
                f"| {self._exibir_especifico()} | {status}")

    @abstractmethod
    def _exibir_especifico(self):
        """Descrição dos campos exclusivos da subclasse."""

    # --- persistência ---

    def to_dict(self):
        d = {
            "_tipo": self.tipo(),
            "placa": self.placa,
            "marca": self.marca,
            "modelo": self.modelo,
            "ano": self.ano,
            "valor_diaria_base": self.valor_diaria_base,
            "disponivel": self.disponivel,
        }
        d.update(self._dict_especifico())
        return d

    @abstractmethod
    def _dict_especifico(self):
        """Campos exclusivos da subclasse para o JSON."""


class Carro(Veiculo):
    """Carro de passeio. Ar-condicionado acrescenta uma taxa fixa por diária."""

    TAXA_AR = 25.0

    def __init__(self, placa, marca, modelo, ano, valor_diaria_base,
                 numero_portas=4, ar_condicionado=False, disponivel=True):
        super().__init__(placa, marca, modelo, ano, valor_diaria_base, disponivel)
        self.numero_portas = numero_portas
        self.ar_condicionado = ar_condicionado

    def tipo(self):
        return "Carro"

    def calcular_valor_diaria(self, dias):
        adicional = self.TAXA_AR if self.ar_condicionado else 0.0
        return (self.valor_diaria_base + adicional) * dias

    def _ler_especifico(self, console):
        self.numero_portas = console.inteiro("Número de portas", minimo=2)
        self.ar_condicionado = console.confirmar("Possui ar-condicionado?")

    def _exibir_especifico(self):
        ar = "com ar" if self.ar_condicionado else "sem ar"
        return f"{self.numero_portas} portas, {ar}"

    def _dict_especifico(self):
        return {"numero_portas": self.numero_portas,
                "ar_condicionado": self.ar_condicionado}


class Moto(Veiculo):
    """Motocicleta. Cobra um seguro proporcional à cilindrada."""

    def __init__(self, placa, marca, modelo, ano, valor_diaria_base,
                 cilindrada=0, disponivel=True):
        super().__init__(placa, marca, modelo, ano, valor_diaria_base, disponivel)
        self.cilindrada = cilindrada

    def tipo(self):
        return "Moto"

    def calcular_valor_diaria(self, dias):
        # Seguro: R$ 0,02 por cc por diária (motos potentes custam mais).
        seguro = self.cilindrada * 0.02
        return (self.valor_diaria_base + seguro) * dias

    def _ler_especifico(self, console):
        self.cilindrada = console.inteiro("Cilindrada (cc)", minimo=0)

    def _exibir_especifico(self):
        return f"{self.cilindrada} cc"

    def _dict_especifico(self):
        return {"cilindrada": self.cilindrada}


class Caminhao(Veiculo):
    """Caminhão de carga. Adicional por tonelada de capacidade."""

    ADICIONAL_POR_TONELADA = 40.0

    def __init__(self, placa, marca, modelo, ano, valor_diaria_base,
                 capacidade_carga_ton=0.0, eixos=2, disponivel=True):
        super().__init__(placa, marca, modelo, ano, valor_diaria_base, disponivel)
        self.capacidade_carga_ton = capacidade_carga_ton
        self.eixos = eixos

    def tipo(self):
        return "Caminhao"

    def calcular_valor_diaria(self, dias):
        adicional = self.capacidade_carga_ton * self.ADICIONAL_POR_TONELADA
        return (self.valor_diaria_base + adicional) * dias

    def _ler_especifico(self, console):
        self.capacidade_carga_ton = console.decimal("Capacidade de carga (ton)",
                                                     minimo=0.0)
        self.eixos = console.inteiro("Número de eixos", minimo=2)

    def _exibir_especifico(self):
        return f"{self.capacidade_carga_ton:.1f} ton, {self.eixos} eixos"

    def _dict_especifico(self):
        return {"capacidade_carga_ton": self.capacidade_carga_ton,
                "eixos": self.eixos}


# Factory usada pela persistência para reconstruir a subclasse correta.
_REGISTRO = {"Carro": Carro, "Moto": Moto, "Caminhao": Caminhao}


def veiculo_de_dict(d):
    """Reconstrói um Veiculo a partir do dict salvo (usa o campo ``_tipo``)."""
    tipo = d.get("_tipo")
    cls = _REGISTRO.get(tipo)
    if cls is None:
        raise DadosInvalidosError(f"Tipo de veículo desconhecido: {tipo!r}")
    campos = {k: v for k, v in d.items() if k != "_tipo"}
    return cls(**campos)
