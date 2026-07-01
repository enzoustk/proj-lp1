"""Interface de terminal (CRUD interativo).

Toda exibição usa ``console << obj`` e toda entrada de entidade usa
``console >> obj`` (sobrecarga de ``<<``/``>>``). Erros de regra de negócio
sobem como ``LocadoraError`` e são tratados num único ponto por ação.
"""
from datetime import date

from .clientes import ClientePF, ClientePJ
from .console import console
from .enums import FormaPagamento
from .excecoes import DadosInvalidosError, LocadoraError
from .veiculos import Caminhao, Carro, Moto


class Aplicacao:
    """Laço principal de menus da locadora."""

    def __init__(self, locadora, repositorio):
        self.locadora = locadora
        self.repo = repositorio

    def run(self):
        acoes = {
            "1": self.menu_veiculos,
            "2": self.menu_clientes,
            "3": self.menu_locacoes,
            "4": self.menu_relatorios,
        }
        while True:
            console << f"\n=== {self.locadora.nome} ==="
            console << ("1) Veículos   2) Clientes   3) Locações   "
                       "4) Relatórios   0) Sair")
            op = input("Opção: ").strip()
            if op == "0":
                self.repo.salvar(self.locadora)
                console << "Dados salvos. Até logo!"
                return
            acao = acoes.get(op)
            if acao:
                acao()
            else:
                console << "Opção inválida."

    # --- utilitários ---

    def _executar(self, funcao):
        """Roda uma ação tratando erros de negócio e salvando ao final."""
        try:
            funcao()
            self.repo.salvar(self.locadora)
        except LocadoraError as e:
            console << f"[erro] {e}"

    def _ler_data(self, rotulo):
        bruto = input(f"{rotulo} (dd/mm/aaaa, vazio = hoje): ").strip()
        if not bruto:
            return date.today()
        try:
            d, m, a = (int(x) for x in bruto.split("/"))
            return date(a, m, d)
        except (ValueError, TypeError):
            raise DadosInvalidosError("Data inválida. Use dd/mm/aaaa.")

    def _listar(self, itens, vazio):
        if not itens:
            console << vazio
            return
        for item in itens:
            console << item

    # --- veículos ---

    def menu_veiculos(self):
        while True:
            console << ("\n-- Veículos --  1) Cadastrar  2) Listar  "
                       "3) Buscar  4) Remover  0) Voltar")
            op = input("Opção: ").strip()
            if op == "0":
                return
            elif op == "1":
                self._executar(self._cadastrar_veiculo)
            elif op == "2":
                self._listar(self.locadora.veiculos, "Nenhum veículo cadastrado.")
            elif op == "3":
                self._executar(self._buscar_veiculo)
            elif op == "4":
                self._executar(self._remover_veiculo)
            else:
                console << "Opção inválida."

    def _cadastrar_veiculo(self):
        console << "Tipo:  1) Carro   2) Moto   3) Caminhão"
        tipos = {"1": Carro, "2": Moto, "3": Caminhao}
        cls = tipos.get(input("Opção: ").strip())
        if cls is None:
            raise DadosInvalidosError("Tipo de veículo inválido.")
        veiculo = cls.vazio()
        console >> veiculo            # <<< leitura via operador >>
        self.locadora.cadastrar_veiculo(veiculo)
        console << "Veículo cadastrado:"
        console << veiculo

    def _buscar_veiculo(self):
        placa = input("Placa: ").strip().upper()
        console << self.locadora.buscar_veiculo(placa)

    def _remover_veiculo(self):
        placa = input("Placa: ").strip().upper()
        self.locadora.remover_veiculo(placa)
        console << "Veículo removido."

    # --- clientes ---

    def menu_clientes(self):
        while True:
            console << ("\n-- Clientes --  1) Cadastrar  2) Listar  "
                       "3) Buscar  4) Remover  0) Voltar")
            op = input("Opção: ").strip()
            if op == "0":
                return
            elif op == "1":
                self._executar(self._cadastrar_cliente)
            elif op == "2":
                self._listar(self.locadora.clientes, "Nenhum cliente cadastrado.")
            elif op == "3":
                self._executar(self._buscar_cliente)
            elif op == "4":
                self._executar(self._remover_cliente)
            else:
                console << "Opção inválida."

    def _cadastrar_cliente(self):
        console << "Tipo:  1) Pessoa Física (CPF)   2) Pessoa Jurídica (CNPJ)"
        tipos = {"1": ClientePF, "2": ClientePJ}
        cls = tipos.get(input("Opção: ").strip())
        if cls is None:
            raise DadosInvalidosError("Tipo de cliente inválido.")
        cliente = cls.vazio()
        console >> cliente            # <<< leitura + validação de documento
        self.locadora.cadastrar_cliente(cliente)
        console << "Cliente cadastrado:"
        console << cliente

    def _buscar_cliente(self):
        idc = console.inteiro("Id do cliente", minimo=1)
        console << self.locadora.buscar_cliente(idc)

    def _remover_cliente(self):
        idc = console.inteiro("Id do cliente", minimo=1)
        self.locadora.remover_cliente(idc)
        console << "Cliente removido."

    # --- locações ---

    def menu_locacoes(self):
        acoes = {
            "1": self._nova_locacao, "2": self._pagar, "3": self._retirar,
            "4": self._devolver, "5": self._cancelar,
        }
        while True:
            console << ("\n-- Locações --  1) Nova  2) Pagar  3) Retirar  "
                       "4) Devolver  5) Cancelar  6) Listar  0) Voltar")
            op = input("Opção: ").strip()
            if op == "0":
                return
            elif op == "6":
                self._listar(self.locadora.locacoes, "Nenhuma locação registrada.")
            elif op in acoes:
                self._executar(acoes[op])
            else:
                console << "Opção inválida."

    def _nova_locacao(self):
        console << "Veículos disponíveis:"
        self._listar(self.locadora.veiculos_disponiveis(), "  (nenhum)")
        console << "Clientes:"
        self._listar(self.locadora.clientes, "  (nenhum)")
        placa = input("Placa do veículo: ").strip().upper()
        idc = console.inteiro("Id do cliente", minimo=1)
        dias = console.inteiro("Dias de locação", minimo=1)
        inicio = self._ler_data("Data de início")
        loc = self.locadora.criar_locacao(placa, idc, inicio, dias)
        console << "Locação criada (RESERVADA):"
        console << loc

    def _pagar(self):
        idl = console.inteiro("Id da locação", minimo=1)
        console << "Forma:  1) Dinheiro   2) Cartão   3) Pix"
        formas = {"1": FormaPagamento.DINHEIRO, "2": FormaPagamento.CARTAO,
                  "3": FormaPagamento.PIX}
        forma = formas.get(input("Opção: ").strip())
        if forma is None:
            raise DadosInvalidosError("Forma de pagamento inválida.")
        loc = self.locadora.pagar_locacao(idl, forma)
        console << "Pagamento confirmado:"
        console << loc

    def _retirar(self):
        idl = console.inteiro("Id da locação", minimo=1)
        loc = self.locadora.retirar_veiculo(idl)
        console << "Veículo retirado (locação ATIVA):"
        console << loc

    def _devolver(self):
        idl = console.inteiro("Id da locação", minimo=1)
        data = self._ler_data("Data de devolução")
        multa = self.locadora.devolver_veiculo(idl, data)
        if multa:
            console << f"Devolução com atraso. Multa: R$ {multa:.2f}"
        console << self.locadora.buscar_locacao(idl)

    def _cancelar(self):
        idl = console.inteiro("Id da locação", minimo=1)
        loc = self.locadora.cancelar_locacao(idl)
        console << "Locação cancelada:"
        console << loc

    # --- relatórios ---

    def menu_relatorios(self):
        console << "\n-- Relatórios --"
        console << f"Veículos disponíveis: {len(self.locadora.veiculos_disponiveis())}"
        self._listar(self.locadora.veiculos_disponiveis(), "  (nenhum)")
        console << "Locações em aberto:"
        self._listar(self.locadora.locacoes_ativas(), "  (nenhuma)")
        console << f"Faturamento (locações finalizadas): R$ {self.locadora.faturamento():.2f}"
