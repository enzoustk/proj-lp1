#!/usr/bin/env bash
# Smoke test E2E da apresentação.
# Roda o roteiro completo (scripts/demo_inputs.txt) em main.py e confere os
# marcos que serão demonstrados ao vivo, incluindo persistência (reabrir o app).
set -u
cd "$(dirname "$0")/.."

PY=${PYTHON:-python3}
fail=0

limpar() { find data -name '*.json' -delete 2>/dev/null; }

# checar <arquivo> <marcador> <descricao>
checar() {
  if grep -Fq "$2" "$1"; then
    echo "  ok    $3"
  else
    echo "  FALHA $3   (esperava encontrar: $2)"
    fail=1
  fi
}

echo "== Limpando dados anteriores =="
limpar

echo "== Fase 1: executando o roteiro completo =="
out1=$(mktemp)
$PY main.py < scripts/demo_inputs.txt > "$out1" 2>&1

checar "$out1" 'Veículo cadastrado:'                                 'cadastro de veículos (3 tipos / polimorfismo)'
checar "$out1" 'CPF inválido'                                        'validação de documento bloqueia CPF inválido'
checar "$out1" 'Cliente cadastrado:'                                 'cadastro de clientes (PF e PJ)'
checar "$out1" 'Locação criada (RESERVADA)'                          'criação de locação'
checar "$out1" 'Não é possível ir de Reservada para Ativa'           'transição inválida: retirar sem pagar'
checar "$out1" 'Pagamento confirmado:'                               'pagamento da locação'
checar "$out1" 'locação ATIVA'                                       'retirada do veículo'
checar "$out1" 'Multa: R$ 120.00'                                    'multa por atraso na devolução'
checar "$out1" 'Finalizada'                                          'locação finalizada (estado dinâmico)'
checar "$out1" 'não está disponível'                                 'veículo indisponível bloqueia nova locação'
checar "$out1" 'Faturamento (locações finalizadas): R$ 555.00'       'relatório de faturamento'

echo "== Fase 2: reabrindo o app para conferir persistência =="
out2=$(mktemp)
printf '4\n0\n' | $PY main.py > "$out2" 2>&1
checar "$out2" 'Faturamento (locações finalizadas): R$ 555.00'       'dados recarregados do JSON ao reiniciar'

echo "== Limpando dados de teste =="
limpar
rm -f "$out1" "$out2"

if [ "$fail" -eq 0 ]; then
  echo "RESULTADO: smoke E2E da apresentação PASSOU"
else
  echo "RESULTADO: smoke E2E da apresentação FALHOU"
fi
exit "$fail"
