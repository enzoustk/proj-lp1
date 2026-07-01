#!/usr/bin/env python3
"""Ponto de entrada da Locadora de Veículos.

Carrega os dados salvos (se houver) e inicia o menu interativo.
"""
from locadora.console import console
from locadora.menu import Aplicacao
from locadora.repositorio import Repositorio


def main():
    repo = Repositorio()
    locadora = repo.carregar(nome="Locadora UFRN")
    try:
        Aplicacao(locadora, repo).run()
    except (KeyboardInterrupt, EOFError):
        repo.salvar(locadora)
        console << "\nEncerrado. Dados salvos."


if __name__ == "__main__":
    main()
