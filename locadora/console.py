"""Objeto de E/S de terminal com sobrecarga dos operadores ``<<`` e ``>>``.

Atende ao requisito (i) da atividade: em C++ usaríamos ``cout << obj`` e
``cin >> obj``. Aqui o mesmo idioma é reproduzido em Python sobrecarregando
``__lshift__`` (escrita/exibição) e ``__rshift__`` (leitura):

    console << veiculo            # exibe o veículo no terminal
    console << "texto" << outro   # encadeável, como os streams de C++
    console >> cliente            # lê os dados do cliente do terminal

Qualquer objeto exibível deve expor ``exibir() -> str``; qualquer objeto
legível deve expor ``ler(console)``.
"""
from .excecoes import DadosInvalidosError


class Console:
    """Stream de terminal que imita ``cout``/``cin`` via ``<<`` e ``>>``."""

    def __lshift__(self, obj):
        """Operador de escrita: exibe ``obj`` no terminal e retorna self."""
        if hasattr(obj, "exibir"):
            print(obj.exibir())
        else:
            print(obj)
        return self

    def __rshift__(self, obj):
        """Operador de leitura: preenche ``obj`` a partir do terminal."""
        obj.ler(self)
        return self

    # --- auxiliares de leitura tipada (usados pelos ler() das entidades) ---

    def texto(self, rotulo, obrigatorio=True):
        valor = input(f"{rotulo}: ").strip()
        if obrigatorio and not valor:
            raise DadosInvalidosError(f"'{rotulo}' não pode ser vazio.")
        return valor

    def inteiro(self, rotulo, minimo=None):
        bruto = input(f"{rotulo}: ").strip()
        try:
            valor = int(bruto)
        except ValueError:
            raise DadosInvalidosError(f"'{rotulo}' deve ser um número inteiro.")
        if minimo is not None and valor < minimo:
            raise DadosInvalidosError(f"'{rotulo}' deve ser >= {minimo}.")
        return valor

    def decimal(self, rotulo, minimo=None):
        bruto = input(f"{rotulo}: ").strip().replace(",", ".")
        try:
            valor = float(bruto)
        except ValueError:
            raise DadosInvalidosError(f"'{rotulo}' deve ser um número.")
        if minimo is not None and valor < minimo:
            raise DadosInvalidosError(f"'{rotulo}' deve ser >= {minimo}.")
        return valor

    def confirmar(self, rotulo):
        return input(f"{rotulo} (s/n): ").strip().lower() in ("s", "sim", "y")


# Instância global usada em toda a aplicação (como cout/cin).
console = Console()
