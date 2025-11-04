from .BaseController import BaseController

class AdminController(BaseController):
    """
    Controlador de seguridad y login
    """

    def verificar_login(self, usuario: str, contrasena: str) -> bool:
        """
        Verifica las credenciales del usuario contra la base de datos
        """

        # 1. Aplicar el hashing: En un proyecto mas realista, la contrasena se hashea aqui
        #    antes de pasarse al DAO para la verificacion
        # contrasena_hasheada = hash_lib.hash_password(contrasena)
        contrasena_hasheada = contrasena # SIMULACION para este ejemplo

        administrador = self.admin_dao.verificar_credenciales(usuario, contrasena_hasheada)

        if administrador:
            print(f"Administrador {usuario} autenticado existosamente")
            return True
        else:
            print(f"Fallo de autenticacion para {usuario}")
            return False
        
    # Aqui se puede anadir un metodo para registrar un nuevo administrador