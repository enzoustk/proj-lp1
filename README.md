# Locadora de Veículos

Trabalho da **Unidade 03** de Linguagem de Programação 1 (LP1) — UFRN.
Aplicação de console que gerencia uma locadora de veículos (CRUD de veículos,
clientes e locações) com foco em **Programação Orientada a Objetos**.

> Linguagem: **Python 3** (somente biblioteca padrão, sem dependências externas).

## Integrantes

| Nome | Matrícula |
|------|-----------|
| Davi Felipe Pinheiro | 20240001420 |
| Enzo Araújo | 20250063249 |

Repositório: https://github.com/enzoustk/proj-lp1

## Como executar

Requer Python 3.8+ (testado no 3.9). Não há nada para instalar.

```bash
make run        # ou: python3 main.py
```

Os dados são salvos em `data/*.json` e recarregados automaticamente na próxima
execução.

### Testes e demonstração

```bash
make test       # roda tests/test_regras.py (regras de negócio)
make smoke      # E2E da apresentação: roda o roteiro inteiro e confere os marcos
make demo       # executa o roteiro automaticamente (saída no terminal)
```

### Apresentação

- `docs/APRESENTACAO.md` — slides (fonte Marp; também legível como markdown).
- `docs/APRESENTACAO.pdf` / `.pptx` / `.html` — slides **renderizados** prontos
  para apresentar (o `.pptx` abre no PowerPoint/Google Slides para editar).
- `docs/ROTEIRO_DEMO.md` — passo a passo da demo ao vivo, com as falas.
- `scripts/demo_inputs.txt` — sequência de teclas usada pelo `make smoke`/`demo`.

### Limpar dados salvos

```bash
make clean
```

## Estrutura

```
proj-lp1/
├── main.py                # ponto de entrada
├── Makefile               # run / test / clean
├── locadora/              # pacote da aplicação
│   ├── enums.py           # StatusLocacao, FormaPagamento
│   ├── excecoes.py        # hierarquia de exceções
│   ├── console.py         # E/S de terminal com operadores << e >>
│   ├── veiculos.py        # Veiculo (abstrata) + Carro/Moto/Caminhao
│   ├── clientes.py        # Cliente (abstrata) + ClientePF/ClientePJ
│   ├── locacao.py         # Pagamento + Locacao (máquina de estados)
│   ├── locadora.py        # agregado raiz / regras de negócio
│   ├── repositorio.py     # persistência JSON
│   └── menu.py            # interface de terminal (CRUD)
├── data/                  # arquivos JSON gerados em runtime
├── docs/
│   ├── diagrama_uml.md    # diagrama de classes (Mermaid — abre no GitHub)
│   └── diagrama_uml.puml  # mesmo diagrama em PlantUML
└── tests/test_regras.py
```

## Como o sistema atende aos requisitos

| Requisito do enunciado | Onde |
|---|---|
| Mín. 9 classes (sem structs) | 12 classes de domínio (ver diagrama) |
| Polimorfismo (≥2 situações) | hierarquias `Veiculo` e `Cliente` |
| ≥5 regras de negócio | 6 regras (abaixo) |
| Operações entre múltiplas classes | `Locadora.criar_locacao` / `devolver_veiculo` |
| Exceções personalizadas + validação | `locadora/excecoes.py` |
| Diagrama de classes UML | `docs/diagrama_uml.*` |
| Salvar em arquivo + carregar no início | `locadora/repositorio.py` (JSON) |
| ≥1 classe com estado dinâmico | `Locacao` (máquina de estados) |
| Sobrecarga dos operadores `>>` e `<<` | `locadora/console.py` |
| Makefile | `Makefile` (alvo `run`) |
| Interação via terminal | `locadora/menu.py` |

> **Adaptações da linguagem:** os requisitos (i) e (j) foram escritos para C++.
> Em Python, a sobrecarga de `>>`/`<<` é feita com `__lshift__`/`__rshift__` no
> objeto `console` (`console << veiculo` exibe, `console >> cliente` lê), e o
> Makefile cumpre o papel de facilitar execução/testes (não há compilação).

### Regras de negócio

1. **Disponibilidade** — não é possível locar um veículo já locado.
2. **Transições de estado** — a locação segue RESERVADA → PAGA → ATIVA →
   FINALIZADA; não se pode retirar o veículo sem pagar nem pular etapas.
3. **Validação de documento** — CPF (com dígitos verificadores) e CNPJ.
4. **Multa por atraso** — devolução após a data prevista cobra
   `dias_atraso × 50% da diária base`.
5. **Cálculo polimórfico** — cada tipo de veículo calcula a diária de forma
   própria (ar-condicionado, seguro por cilindrada, adicional por tonelada).
6. **Desconto por tipo de cliente** — PJ tem desconto corporativo fixo; PF tem
   desconto-fidelidade a partir da 3ª locação.

## Polimorfismo

- **Veículos:** `calcular_valor_diaria` é abstrato em `Veiculo` e sobrescrito em
  `Carro`, `Moto` e `Caminhao`, cada um com sua regra de preço.
- **Clientes:** `validar_documento` e `calcular_desconto` variam entre
  `ClientePF` (CPF / fidelidade) e `ClientePJ` (CNPJ / corporativo).

Cada subclasse tem atributos **e** comportamento próprios, conforme as
Observações 2 e 3 do enunciado.
