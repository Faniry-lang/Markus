def get_validation_from_console_input(tool_name, tool_args: dict or {}):
    print(f"Autoriser l'execution de l'outil {tool_name} avec les arguments suivants: {tool_args} ?")
    print("O pour autoriser, N pour refuser")
    autorisation = input()
    while autorisation != "O" and autorisation != "N":
        print("Réponse non valide")
        print("O pour autoriser, N pour refuser")
        autorisation = input()
    if autorisation == "O":
        print("Autorisé!")
        return True
    elif autorisation == "N":
        print("Refusé!")
        return False
    return False
