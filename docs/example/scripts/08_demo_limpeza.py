"""A limpeza em ação: do texto da página para dados."""
from limpeza import (limpar_texto, parse_data_evento, parse_faixa_salarial,
                     parse_local, parse_preco)

print("--- salários (em centavos)")
for texto in ["R$ 7.000 a R$ 9.500", "R$ 4.500", "R$ 3.200,50",
              "até R$ 11.000", "A combinar"]:
    print(f"{texto!r:26} -> {parse_faixa_salarial(texto)}")

print("--- locais")
for texto in ["Curitiba, PR", "São José dos Pinhais, PR", "Remoto", "Online"]:
    print(f"{texto!r:28} -> {parse_local(texto)}")

print("--- datas dos eventos")
for texto in ["sábado, 17 de outubro de 2026, 14h00",
              "sexta-feira, 6 de novembro de 2026, 08h30",
              "data a confirmar"]:
    print(f"{texto!r:46} -> {parse_data_evento(texto)}")

print("--- preços (em centavos)")
for texto in ["Gratuito", "R$ 40,00", "R$ 120,00 (estudantes: R$ 60,00)"]:
    print(f"{texto!r:38} -> {parse_preco(texto)}")

print("--- espaços e quebras de linha")
print(repr(limpar_texto("  Dev   Python \n Júnior  ")))
print("o float erra:", 0.1 + 0.2, "| os centavos inteiros acertam:", 10 + 20)
