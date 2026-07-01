"""Testes das regras de negócio (asserts puros, sem framework).

Rode com:  make test   ou   python3 -m tests.test_regras
Cobre a lógica não-trivial: máquina de estados, validação de documentos,
multa por atraso, indisponibilidade, cálculo polimórfico e persistência.
"""
import shutil
import tempfile
from datetime import date

from locadora.clientes import ClientePF, ClientePJ
from locadora.enums import FormaPagamento, StatusLocacao
from locadora.excecoes import (DocumentoInvalidoError, TransicaoInvalidaError,
                               VeiculoIndisponivelError)
from locadora.locadora import Locadora
from locadora.repositorio import Repositorio
from locadora.veiculos import Caminhao, Carro, Moto

CPF_OK = "11144477735"
CNPJ_OK = "11222333000181"


def _erra(exc, funcao):
    try:
        funcao()
    except exc:
        return True
    raise AssertionError(f"esperava {exc.__name__}, não levantou")


def test_calculo_polimorfico():
    carro = Carro("AAA0A00", "VW", "Gol", 2022, 100.0, ar_condicionado=True)
    moto = Moto("BBB0B00", "Honda", "CB", 2021, 100.0, cilindrada=1000)
    cam = Caminhao("CCC0C00", "Volvo", "FH", 2020, 100.0, capacidade_carga_ton=5)
    assert carro.calcular_valor_diaria(2) == (100 + 25) * 2      # taxa de ar
    assert moto.calcular_valor_diaria(2) == (100 + 20) * 2       # seguro por cc
    assert cam.calcular_valor_diaria(2) == (100 + 200) * 2       # adic. por ton


def test_validacao_documento():
    assert _erra(DocumentoInvalidoError,
                 lambda: ClientePF(0, "X", "9", cpf="123").validar_documento())
    assert _erra(DocumentoInvalidoError,
                 lambda: ClientePJ(0, "X", "9", cnpj="000").validar_documento())
    ClientePF(0, "Ana", "9", cpf=CPF_OK).validar_documento()      # não levanta
    ClientePJ(0, "ACME", "9", cnpj=CNPJ_OK).validar_documento()


def test_desconto_por_tipo():
    pj = ClientePJ(0, "ACME", "9", cnpj=CNPJ_OK)
    assert pj.calcular_desconto(1000) == 150.0                   # 15% corporativo
    pf = ClientePF(0, "Ana", "9", cpf=CPF_OK)
    assert pf.calcular_desconto(1000) == 0.0                     # sem fidelidade
    pf.qtd_locacoes = 3
    assert pf.calcular_desconto(1000) == 100.0                   # 10% fidelidade


def _cenario():
    loc = Locadora("Teste")
    loc.cadastrar_veiculo(Carro("AAA0A00", "VW", "Gol", 2022, 100.0))
    loc.cadastrar_cliente(ClientePF(0, "Ana", "9", cpf=CPF_OK))
    return loc


def test_maquina_de_estados_e_multa():
    loc = _cenario()
    contrato = loc.criar_locacao("AAA0A00", 1, date(2025, 1, 1), 3)
    assert contrato.status == StatusLocacao.RESERVADA
    assert contrato.valor_total == 300.0                         # 100*3, sem desconto

    # Não pode retirar sem pagar.
    assert _erra(TransicaoInvalidaError, contrato.retirar)

    loc.pagar_locacao(1, FormaPagamento.PIX)
    assert contrato.status == StatusLocacao.PAGA
    loc.retirar_veiculo(1)
    assert contrato.status == StatusLocacao.ATIVA

    # Devolução com 2 dias de atraso: multa = 2 * 100 * 0.5 = 100.
    multa = loc.devolver_veiculo(1, date(2025, 1, 6))            # previsto: 04/01
    assert multa == 100.0
    assert contrato.status == StatusLocacao.FINALIZADA
    assert contrato.valor_total == 400.0
    assert loc.buscar_veiculo("AAA0A00").disponivel is True       # liberou o veículo
    assert loc.faturamento() == 400.0


def test_veiculo_indisponivel():
    loc = _cenario()
    loc.criar_locacao("AAA0A00", 1, date(2025, 1, 1), 2)
    assert _erra(VeiculoIndisponivelError,
                 lambda: loc.criar_locacao("AAA0A00", 1, date(2025, 1, 1), 2))


def test_persistencia_roundtrip():
    pasta = tempfile.mkdtemp()
    try:
        loc = _cenario()
        loc.criar_locacao("AAA0A00", 1, date(2025, 1, 1), 2)
        loc.pagar_locacao(1, FormaPagamento.CARTAO)
        repo = Repositorio(pasta=pasta)
        repo.salvar(loc)

        recarregada = repo.carregar()
        assert len(recarregada.veiculos) == 1
        assert len(recarregada.clientes) == 1
        assert len(recarregada.locacoes) == 1
        l = recarregada.locacoes[0]
        assert l.status == StatusLocacao.PAGA
        assert l.veiculo.placa == "AAA0A00"                      # referência religada
        assert l.cliente.id_cliente == 1
        assert recarregada._proximo_id_locacao == 2              # contador restaurado
    finally:
        shutil.rmtree(pasta)


def main():
    testes = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in testes:
        t()
        print(f"ok  {t.__name__}")
    print(f"\n{len(testes)} testes passaram.")


if __name__ == "__main__":
    main()
