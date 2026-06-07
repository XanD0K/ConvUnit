from convunit import Converter

c = Converter()

# Criar grupo
result = c.convert("time", time_input="5 years 10 months 10 days 8 hours seconds")
print(result)