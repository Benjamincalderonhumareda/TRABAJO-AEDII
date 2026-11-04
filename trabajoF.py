
"""Para Registrar, buscar y eliminar alumno (LISTA SIMPLE)"""
 
class NodoSimple:
    def __init__(self, nombreC, dni, correo):
        self.nombreC = nombreC
        self.dni = dni
        self.correo = correo
        self.sig = None
 
 
class ListaSimple:
    def __init__(self):
        self.cabecera = None
 
    def registrar(self, nombreC, dni, correo):
        nuevo = NodoSimple(nombreC, dni, correo)
        nuevo.sig = self.cabecera
        self.cabecera = nuevo
 
    def buscar(self, dni):
        p = self.cabecera
        while p:
            if p.dni == dni:
                return True
            p = p.sig
        return False
 
    # NUEVO: igual que buscar, pero devuelve el nodo (para mostrar sus datos)
    def obtener(self, dni):
        p = self.cabecera
        while p:
            if p.dni == dni:
                return p
            p = p.sig
        return None
 
    def eliminar(self, dni):
        actual = self.cabecera
        anterior = None
        while actual:
            if actual.dni == dni:
                if anterior is None:
                    self.cabecera = actual.sig
                else:
                    anterior.sig = actual.sig
                return True
            anterior = actual
            actual = actual.sig
        return False
 
 
"""PARA INSERTAR y VER NUEVO TEMA A REPASAR (LISTA DOBLE)"""
class NodoDoble:
    def __init__(self, dato):
        self.dato = dato
        self.sig = None
        self.ant = None
 
 
class ListaDoble:
    def __init__(self):
        self.cabecera = None
        self.cola = None
        self.tam = 0
 
    def insertar_final(self, dato):
        nuevo = NodoDoble(dato)
        if self.cola is None:
            self.cabecera = nuevo
            self.cola = nuevo
        else:
            nuevo.ant = self.cola
            self.cola.sig = nuevo
            self.cola = nuevo
        self.tam += 1

#Ver tema por tema mientras el usuario quiera
    def mostrar(self):
        p = self.cabecera

        if p is None:
            print("Aún no hay temas registrados.")
        else:
            rpta = "Si"

            while rpta == "Si":
                print(f"Tema: {p.dato}")
                p = p.sig

                if p is None:
                    print("No hay más temas.")
                    break

                rpta = input("¿Desea ver el siguiente tema? Si/No: ").strip().capitalize()
 
    def eliminar(self, dato):
        p = self.cabecera
        if p is None:
            return False
        while p:
            if dato == p.dato:
                if p == self.cabecera and p == self.cola:
                    self.cabecera = None
                    self.cola = None
                elif p == self.cabecera:
                    self.cabecera = self.cabecera.sig
                    self.cabecera.ant = None
                elif p == self.cola:
                    self.cola = self.cola.ant
                    self.cola.sig = None
                else:
                    p.ant.sig = p.sig
                    p.sig.ant = p.ant
                self.tam -= 1
                return True
            p = p.sig
        return False
 
 
"""ENVIAR Y RESOLVER DUDA (COLA)"""
class NodoCola:
    def __init__(self, dato):
        self.dato = dato
        self.sig = None
 
 
class ColaSimple:
    def __init__(self):
        self.frente = None
        self.final = None
 
    def is_empty(self):
        return self.frente is None
 
    def encolar(self, dato):
        nuevo = NodoCola(dato)
        if self.is_empty():
            self.frente = nuevo
            self.final = nuevo
        else:
            self.final.sig = nuevo
            self.final = nuevo
 
    def desencolar(self):
        if self.is_empty():
            return None
        dato = self.frente.dato
        if self.frente == self.final:
            self.frente = None
            self.final = None
        else:
            self.frente = self.frente.sig
        return dato
 
 
"""HISTORIAL DE CONSULTAS (PILA)"""
class NodoPila:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None
 
 
class Pila:
    def __init__(self):
        self.cabecera = None
 
    def push(self, dato):
        nuevo = NodoPila(dato)
        nuevo.siguiente = self.cabecera
        self.cabecera = nuevo
 
    def pop(self):
        if self.is_empty():
            return None
        dato = self.cabecera.dato
        self.cabecera = self.cabecera.siguiente
        return dato
 
    def is_empty(self):
        return self.cabecera is None
 
 
# ==========================================
registrar_alumno = ListaSimple()
registar_tema = ListaDoble()
dudas_cola = ColaSimple()
historial_pila = Pila()


# FLUJOS DE MENÚ SEGÚN ROL

def menu_profesor():
    while True:
        print("\n=================================")
        print("     MENÚ PROFESOR               ")
        print("=================================")
        print("1. Registrar alumno")
        print("2. Eliminar alumno")
        print("3. Buscar alumno")
        print("4. Registrar tema a repasar")
        print("5. Responder duda pendiente")
        print("6. Volver al menú principal")
        opc = input("Seleccione una opción: ")

        if opc == "1":
            nombre = input("Nombre completo: ")
            dni = input("DNI: ")
            while len(dni)<8:
                print("El DNI debe tener exactamente 8 dígitos")
                dni=input("Ingrese nuevamente el dni: ")
                print()
            correo = input("Correo: ")
            registrar_alumno.registrar(nombre, dni, correo)
            print("  [✓] Alumno registrado con éxito.")

        elif opc == "2":
            dni = input("Ingrese el DNI del alumno a eliminar: ")
            if registrar_alumno.eliminar(dni):
                print("  Alumno eliminado.")
            else:
                print("  [!] No se encontró ningún alumno con ese DNI.")

        elif opc == "3":
            dni = input("Ingrese DNI a buscar: ")
            alumno = registrar_alumno.buscar(dni)
            if alumno:
                print(f"  [✓] Encontrado: {alumno.nombreC} | DNI: {alumno.dni} | Correo: {alumno.correo}")
            else:
                print("  [!] Alumno no registrado.")

        elif opc == "4":
            tema = input("Nombre del nuevo tema: ")
            registar_tema.insertar_final(tema)
            print("  [✓] Tema agregado al plan de repaso.")

        elif opc == "5":
            duda = dudas_cola.desencolar()
            if duda:
                print(f"\n  [Duda atendida]: '{duda}'")
                historial_pila.push(f"Atendida: {duda}")
                print("  [✓] La duda fue respondida y movida al historial (Pila).")
            else:
                print("  [!] No hay dudas pendientes por responder.")

        elif opc == "6":
            break
        else:
            print("Opción inválida.")


def menu_alumno():
    print("\n--- INICIO DE SESIÓN ALUMNO ---")
    dni = input("Ingrese su DNI para verificar acceso: ")
    alumno = registrar_alumno.buscar(dni)

    if not alumno:
        print("\n  [X] El DNI ingresado no está registrado por ningún profesor. Acceso denegado.")
        return

    print(f"\nBienvenido/a {alumno.nombreC}!")
    
    while True:
        print("\n=================================")
        print("     MENÚ ALUMNO                 ")
        print("=================================")
        print("1. Buscar alumno")
        print("2. Ver temas a repasar")
        print("3. Enviar duda")
        print("4. Ver historial de dudas")
        print("5. Eliminar última duda del historial")
        print("6. Volver al menú principal")
        opc = input("Seleccione una opción: ")

        if opc == "1":
            dni_b = input("Ingrese DNI del alumno a consultar: ")
            a = registrar_alumno.buscar(dni_b)
            if a:
                print(f"  [✓] Alumno: {a.nombreC} | Correo: {a.correo}")
            else:
                print("  [!] No se encontró el alumno.")

        elif opc == "2":
            registar_tema.mostrar()

        elif opc == "3":
            duda = input("Escriba su duda: ")
            dudas_cola.encolar(duda)
            print("  [✓] Duda enviada a la cola del profesor.")

        elif opc == "4":
            historial_pila.mostrar_historial()

        elif opc == "5":
            eliminada = historial_pila.pop()
            if eliminada:
                print(f"  [✓] Se eliminó la duda más reciente del historial: '{eliminada}'")
            else:
                print("  [!] El historial ya está vacío.")

        elif opc == "6":
            break
        else:
            print("Opción inválida.")


# ==========================================
# MENÚ PRINCIPAL
# ==========================================
def SistemaCompleto():
    while True:
        print("\n=================================")
        print("   SISTEMA ACADÉMICO UNIFICADO   ")
        print("=================================")
        print("1. Entrar como PROFESOR")
        print("2. Entrar como ALUMNO")
        print("3. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            menu_profesor()
        elif opcion == "2":
            menu_alumno()
        elif opcion == "3":
            print("\n¡Hasta luego!")
            break
        else:
            print("Opción no válida.")

SistemaCompleto()