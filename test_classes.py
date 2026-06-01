from src.unit_converter.api import Converter


converter = Converter()


# message = converter.groups()
# print(message)


# message = converter.types("length")
# print(message)

# message = converter.history(limit=2)
# print(message)

message = converter.convert("length", "meters feet 5", print_message=True)
print(message)

# message = converter.convert("time", "2019-11-04 days", print_message=True)
# print(message)

# message = converter.manage_group("new_group", "add new_base_unit")
# print(message)

# message = converter.manage_group("new_group", "remove")
# print(message)

# message = converter.manage_type("new_group", "add new_type .00475")
#  print(message)
# message = converter.aliases("new_group", "add new_type nt")
# print(message)

# message = converter.aliases("new_group", "add new_type2 nt2")
# print(message)

# message = converter.change_base("new_group", "new_base_unit")
# print(message)