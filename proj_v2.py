# Nome: David Malheiro Fadul
# Curso: Superior De Tecnologia Em Análise E Desenvolvimento De Sistemas

import os
import json

# As classes JsonModel e descendentes simulam um Django ORM básico
class JsonModel:
    file_path = "data.json"

    def __init__(self, table_name, file_path=None, **kwargs):
        self.table_name = table_name
        self.__dict__.update(kwargs)

    @classmethod
    def _load_data(cls):
        if not os.path.exists(cls.file_path):
            return {}
        with open(cls.file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    @classmethod
    def _save_data(cls, data):
        with open(cls.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, table_name):
        data = cls._load_data()
        if table_name not in data:
            return {}
        return data[table_name]

    def save(self):
        data = self._load_data()

        if self.table_name not in data:
            data[self.table_name] = {}

        if "CPFS" not in data[self.table_name].keys():
            data[self.table_name]["CPFS"] = []
        
        # Verifica se o CPF já está cadastrado
        if "cpf" in self.__dict__ and self.cpf in data[self.table_name]["CPFS"]:
            print(f"CPF {self.cpf} já cadastrado.")
            return
        
        # Adiciona o CPF à lista de CPFs
        if "cpf" in self.__dict__:
            data[self.table_name]["CPFS"].append(self.cpf)

        # Gera um código único para o registro
        code = len(data[self.table_name])
        self.codigo = code

        data[self.table_name][code] = self.__dict__
        self._save_data(data)

        return code
    
    def update(self, old_code):
        data = self._load_data()

        if self.table_name not in data:
            print(f"Tabela {self.table_name} não encontrada.")
            return False

        for key, value in self.__dict__.items():
            if key == "table_name":
                continue
            
            if key not in data[self.table_name][old_code]:
                print(f"O objeto send editado não tem a propriedade {key}")

            data[self.table_name][old_code][key] = value

        self._save_data(data)
        return True

        

    @classmethod
    def delete(cls, table_name, codigo):
        data = cls._load_data()
        if table_name not in data or codigo not in data[table_name]:
            print(f"Registro não encontrado na tabela {table_name}.")
            return False
        
        cpf = data[table_name][codigo].get("cpf")
        data[table_name]["CPFS"].remove(cpf)
        
        del data[table_name][codigo]
        cls._save_data(data)
        
        return True


class Student(JsonModel):
    def __init__ (self):
        super().__init__("alunos")
        self.codigo = None  # Placeholder para código, será gerado automaticamente
        self.nome = None
        self.cpf = None

class Teacher(JsonModel):
    def __init__ (self):
        super().__init__("professores")
        self.codigo = None  # Placeholder para código, será gerado automaticamente
        self.nome = None
        self.cpf = None

class Course(JsonModel):
    def __init__ (self):
        super().__init__("disciplinas")
        self.codigo = None  # Placeholder para código, será gerado automaticamente
        self.nome = None

class Class(JsonModel):
    def __init__ (self):
        super().__init__("turmas")
        self.codigo = None  # Placeholder para código, será gerado automaticamente
        self.codigo_do_professor = None
        self.codigo_da_disciplina = None

class Registration(JsonModel):
    def __init__ (self):
        super().__init__("matriculas")
        self.codigo_da_turma = None
        self.codigo_do_estudante = None


MAIN_DICT = {
    "ALUNOS": Student,
    "PROFESSORES": Teacher,
    "DISCIPLINAS": Course,
    "TURMAS": Class,
    "MATRICULAS": Registration,
}

def wait():
    print("Pressione ENTER para continuar.")
    input()


def gen_menu(menu_header:str, options:list, return_msg:str=None):
    return_msg = return_msg if return_msg else "Sair"

    while True:
        os.system('cls' if os.name == "nt" else 'clear')
        print(menu_header)

        for i, option in enumerate(options, start=1):
            print(f"({i}) {option.title()}")
        print(f"(9) {return_msg}")

        user_input = input("\nInforme a ação desejada: ")
        print("\n")
        
        if user_input == "":
            continue

        if user_input == str(0):
            return 0

        if user_input == str(9):
            return 9

        if (not user_input.upper() in options and not user_input.isdigit()):
            print("Tipo de entrada inválida. Por favor, digite um número válido.")
            wait()
            continue

        if user_input.isdigit():
            user_input = int(user_input)
            idx = user_input - 1
            if not idx in range(len(options)):
                print("Entrada inválida. Por favor, digite um número da Lista.")
                wait()
                continue
            user_option = options[idx]      
        else:
            user_option = user_input.upper()        
    
        return user_option

def check_code(code, db_obj):
    if not code.isdigit():
        print("Código inválido. O código é necessariamente um número inteiro.")
        wait()
        return -1

    model = MAIN_DICT.get(db_obj)
    data = model.load(db_obj.lower())
    
    if not data:
        print(f"Não há {db_obj.lower()} cadastrados")
        wait()
        return -1
    
    if code not in data:
        print(f"Código {code} não encontrado para {db_obj.lower()}.")
        wait()
        return -1

    return data


def include(db_obj, get_obj=False):
    print("===== INCLUSÃO =====\n")
    
    model = MAIN_DICT.get(db_obj)()

    for key in model.__dict__:
        if  key == "codigo" or key == "table_name":
            continue

        print(f"Informe o(a) {key.upper().replace("_", " ")}: ", end=" ")

        value = input()
        value = " ".join([n.strip() for n in value.split()]) # remover mult espaços entre nomes

        if key == "nome":
            # checagem de input básica p/ nomes
            if len(value) == 1 or (len(value) == 0 and not get_obj):
                print("O nome informado é inválido")
                wait()
                return

        elif key == "cpf":
            # checagem de input básica p/ CPF
            value = value.replace(".", "").replace("-", "")
            if len(value) != 11 or not value.isdigit() and not get_obj:
                print("O CPF informado é inválido")
                wait()
                return
    
        wait()      
        setattr(model, key, value)
    
    if get_obj:
        return model
    
    code = model.save()

    if code:
        print(f"{db_obj.title()} cadastrado com sucesso! Código único gerado: {code}")
    else:
        print(f"Erro ao cadastrar {db_obj.lower()}. Verifique os dados informados.")
    
    wait()
    return


def show_list(db_obj):
    print("===== LISTAGEM =====\n")

    model = MAIN_DICT.get(db_obj)
    data = model.load(db_obj.lower())

    if not data:
        print(f"Não há {db_obj.lower()} cadastrados")
        wait()
        return
    
    for key, value in data.items():
        if key == "CPFS":
            continue
        
        print("; ".join([f"{k.upper()}:{v}" for k, v in value.items() if k != "table_name"]))

    wait()
    return


def update(db_obj):
    print("===== EDITAR =====\n")
    print(f"Informe o código do(a) {db_obj.upper()} a ser atualizado:", end=" ")
    old_code = input().strip()

    data = check_code(old_code, db_obj)
    if data == -1:
        return
    
    model = include(db_obj, get_obj=True)
    if not model:
        return
    
    model.update(old_code)


def exclude(db_obj):
    print("===== EXCLUSÃO =====\n")

    print(f"Informe o código do(a) {db_obj.upper()} a ser excluído:", end=" ")
    code = input().strip()

    data = check_code(code, db_obj)
    if data == -1:
        return

    name = data[code].get("nome", "Desconhecido")
    print(f"Você tem certeza que deseja excluir o(a) {db_obj.lower()} '{name}'? (s/N)", end=" ")    
    confirm = input().strip().lower()
    if not confirm == "s" and not confirm == "sim":
        print("Exclusão cancelada.")
        wait()
        return
    
    model = MAIN_DICT.get(db_obj)
    if model.delete(db_obj.lower(), code):
        print(f"{db_obj.title()} com código {code} ({name}) excluído com sucesso!")
    else:
        print(f"Erro ao excluir {db_obj.lower()} com código {code}. Verifique os dados informados.")
    
    wait()
    return


OPPER_DICT = {
    "INCLUIR": include,
    "LISTAR": show_list,
    "ATUALIZAR": update,
    "EXCLUIR": exclude,
}

def main():
    main_header = "----- MENU PRINCIPAL -----\n"
    main_options = list(MAIN_DICT.keys())
    oper_options = list(OPPER_DICT.keys())

    db_obj = None
    curr_menu = "MAIN"
    while True:
        if curr_menu == "MAIN":
            db_obj = gen_menu(main_header, main_options, "Sair")
            if db_obj == 9:
                print("Encerrando o programa...")
                break
            curr_menu = "OPER"
        
        elif curr_menu == "OPER":
            oper = gen_menu(f"----- [{db_obj}] MENU DE OPERAÇÕES -----\n", oper_options, "Voltar ao menu principal")
            if oper == 9:
                curr_menu = "MAIN"
                continue
            
            operation = OPPER_DICT.get(oper)
            if operation:
                operation(db_obj)

if __name__ == "__main__":
    main()
