# Roteiro da Demonstração — Sistema Funcionando

Este é o passo a passo para apresentar o **Sistema Funcionando** ao vivo no
terminal. Ele cobre, na ordem, **todos** os requisitos avaliados: polimorfismo,
validações/exceções, regras de negócio, máquina de estados, multa, faturamento
e persistência.

> **Dica:** rode `make smoke` **antes** da apresentação. Ele executa exatamente
> este roteiro de ponta a ponta e confere cada marco — se passar, a demo ao vivo
> vai funcionar. A sequência de teclas está em `scripts/demo_inputs.txt`.

## Preparação (antes de apresentar)

```bash
make clean      # começa com a base vazia
make test       # mostra os 6 testes de regras passando
make run        # inicia a aplicação para a demo ao vivo
```

Legenda: **[digite]** = o que teclar no terminal · **💬** = o que falar.

---

### Parte 1 — Cadastro de veículos (polimorfismo de `Veiculo`)

1. **[digite]** `1` (Veículos) → `1` (Cadastrar) → `1` (Carro)
   - Placa `CAR0001`, VW, Gol, 2022, diária `120`, `4` portas, ar `s`
   - 💬 *"O carro é uma subclasse de `Veiculo`. Repare que ele tem atributos
     próprios (portas, ar) e sua própria regra de diária — o ar soma uma taxa."*
2. **[digite]** `1` (Cadastrar) → `2` (Moto): `MOT0001`, Honda, CB500, 2021,
   diária `90`, cilindrada `500`
3. **[digite]** `1` (Cadastrar) → `3` (Caminhão): `CAM0001`, Volvo, FH, 2020,
   diária `300`, capacidade `10` ton, `3` eixos
   - 💬 *"Mesma classe-mãe, três regras de preço diferentes — isso é o
     polimorfismo #1. Cada `calcular_valor_diaria` é sobrescrito."*
4. **[digite]** `2` (Listar) → mostre os três → `0` (Voltar)

### Parte 2 — Clientes + validação de documento (exceção)

5. **[digite]** `1` (Clientes) → `1` (Cadastrar) → `1` (PF):
   nome `Teste`, tel `000`, **CPF `11111111111`** (inválido), nasc `01/01/2000`
   - 💬 *"O CPF é validado com os dígitos verificadores. Documento inválido
     levanta uma exceção personalizada e o cadastro é recusado."* → aparece
     `[erro] CPF inválido: ...`
6. **[digite]** `1` (Cadastrar) → `1` (PF): `Ana Souza`, `9999`,
   CPF `11144477735`, nasc `10/05/1995`
7. **[digite]** `1` (Cadastrar) → `2` (PJ): `Locadora Corp`, `8888`,
   CNPJ `11222333000181`, razão `ACME LTDA`
   - 💬 *"PF valida CPF e PJ valida CNPJ — polimorfismo #2. E cada tipo tem
     desconto diferente (já já mostramos)."* → `0` (Voltar)

### Parte 3 — Ciclo de vida da locação (máquina de estados)

8. **[digite]** `3` (Locações) → `1` (Nova): veículo `CAR0001`, cliente `1`,
   `3` dias, início `01/01/2025`
   - 💬 *"A locação nasce no estado RESERVADA. O valor (R$ 435) já é o cálculo
     polimórfico do carro com ar."*
9. **[digite]** `3` (Retirar) → locação `1`
   - 💬 *"Tento retirar o veículo sem pagar..."* → `[erro] Não é possível ir de
     Reservada para Ativa`. *"A máquina de estados impede pular o pagamento —
     exatamente o exemplo do enunciado: tem que pagar primeiro."*
10. **[digite]** `2` (Pagar) → locação `1` → `3` (Pix) → estado **PAGA**
11. **[digite]** `3` (Retirar) → locação `1` → estado **ATIVA**
12. **[digite]** `4` (Devolver) → locação `1` → data `06/01/2025`
    - 💬 *"Devolvi 2 dias atrasado. O sistema cobra multa = 2 × 50% da diária =
      R$ 120, total vai para R$ 555, e o veículo volta a ficar disponível."*
      → `Multa: R$ 120.00`, estado **FINALIZADA**

### Parte 4 — Interação entre classes + regras (desconto e disponibilidade)

13. **[digite]** `1` (Nova): veículo `CAM0001`, cliente `2` (PJ), `2` dias,
    início `01/01/2025`
    - 💬 *"Caminhão de 10 ton: diária (300 + 10×40) × 2 = R$ 1400. Cliente PJ
      tem 15% de desconto corporativo → R$ 1190. A operação cruza Veículo +
      Cliente + Locação + Pagamento."*
14. **[digite]** `1` (Nova): tente `CAM0001` de novo (cliente `2`, `1` dia,
    `01/01/2025`)
    - 💬 *"O caminhão já está locado..."* → `[erro] ... não está disponível`.
      *"Regra de disponibilidade impede locar duas vezes o mesmo veículo."*
15. **[digite]** `2` (Pagar) → locação `2` → `2` (Cartão)
16. **[digite]** `6` (Listar) → mostre as duas locações → `0` (Voltar)

### Parte 5 — Relatório e persistência

17. **[digite]** `4` (Relatórios)
    - 💬 *"Faturamento considera só locações finalizadas: R$ 555."*
18. **[digite]** `0` (Sair) → `Dados salvos.`
19. **[digite]** `make run` de novo → `4` (Relatórios)
    - 💬 *"Reabri o programa e os dados continuam lá — tudo é salvo em JSON e
      recarregado no início."* → `0` (Sair)

---

## Encerramento

- Mostre rapidamente o `docs/diagrama_uml.md` (diagrama de classes + de estados).
- 💬 *"Resumindo: 12 classes, 2 hierarquias polimórficas, 6 regras de negócio,
  exceções personalizadas, estado dinâmico na locação, persistência em arquivo e
  sobrecarga dos operadores `<<`/`>>` na entrada/saída."*
