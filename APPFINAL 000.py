import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import sqlite3
import matplotlib.pyplot as plt

class Material:
    def __init__(self, properties):
        self.id = properties[0]
        self.name = properties[1]
        self.properties = {
            'Durete': properties[2],
            'Point_de_fusion': properties[3],
            'Capacite_thermique': properties[4],
            'Densite': properties[5],
            'Module_Elasticite': properties[6],
            'Conductivite_thermique': properties[7],
            'Masse_volumique': properties[8] * 1000 if properties[8] is not None else None,
            'Temperature_ebullition': properties[9],
            'Limite_elasticite': properties[10],
            'Resistance_traction': properties[11],
            'Allongement_rupture': properties[12],
            'Recyclable': properties[13],
            'Resistance_corrosion': properties[14],
            'Prix': properties[15]
        }

    @staticmethod
    def retrieve_material_by_properties(properties):
        try:
            materials = []
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            query = 'SELECT * FROM materiaux WHERE '
            conditions = []
            args = []
            
            for name, min_max in properties.items():
                conditions.append(f'"{name}" > ? AND "{name}" < ?')
                args.extend(min_max)
            
            query += ' AND '.join(conditions)

            cursor.execute(query, args)
            results = cursor.fetchall()
            conn.close()

            for result in results:
                materials.append(Material(result))
        except sqlite3.Error as e:
            messagebox.showerror("Erreur de base de données", f"Une erreur s'est produite: {e}")
        return materials

    @staticmethod
    def retrieve_material_by_name(name):
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM materiaux WHERE Materiaux = ?", (name,))
            result = cursor.fetchone()
            conn.close()
            return Material(result) if result else None
        except sqlite3.Error as e:
            messagebox.showerror("Erreur de base de données", f"Une erreur s'est produite: {e}")
            return None

    @staticmethod
    def add_material_to_db(material_properties):
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            columns = ', '.join(material_properties.keys())
            placeholders = ', '.join(['?' for _ in material_properties])
            query = f'INSERT INTO materiaux ({columns}) VALUES ({placeholders})'

            values = [material_properties[prop] if material_properties[prop] else None for prop in material_properties]
            cursor.execute(query, values)
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Erreur de base de données", f"Une erreur s'est produite: {e}")

class MaterialSearchApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Recherche de Matériaux")
        
        self.properties = {
            "Durete": "Dureté",
            "Point_de_fusion": "Point de fusion",
            "Capacite_thermique": "Capacité thermique",
            "Densite": "Densité",
            "Module_Elasticite": "Module Elasticité",
            "Conductivite_thermique": "Conductivité thermique",
            "Masse_volumique": "Masse volumique",
            "Temperature_ebullition": "Température d'ébullition",
            "Limite_elasticite": "Limite d'élasticité",
            "Resistance_traction": "Résistance à la traction",
            "Allongement_rupture": "Allongement à la rupture",
            "Recyclable": "Recyclable",
            "Resistance_corrosion": "Résistance à la corrosion",
            "Prix": "Prix"
        }

        self.create_main_interface()

    def create_main_interface(self):
        self.label_titre = tk.Label(self, text="Choisissez une option", font=("Helvetica", 16, "bold"))
        self.label_titre.pack(pady=20)

        self.search_button = tk.Button(self, text="Recherche par propriétés", command=self.open_property_search)
        self.search_button.pack(pady=10)

        self.inverse_search_button = tk.Button(self, text="Recherche par matériau", command=self.open_inverse_search)
        self.inverse_search_button.pack(pady=10)

        self.add_material_button = tk.Button(self, text="Ajouter un matériau", command=self.open_add_material)
        self.add_material_button.pack(pady=10)

    def open_property_search(self):
        self.destroy()
        PropertySearchApp().mainloop()


    def open_inverse_search(self):
        self.destroy()
        InverseSearchApp().mainloop()

    def open_add_material(self):
        self.destroy()
        MaterialAdditionApp().mainloop()

class PropertySearchApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Recherche de Matériaux par Propriétés")
        
        self.properties = {
            "Durete": "Dureté",
            "Point_de_fusion": "Point de fusion",
            "Capacite_thermique": "Capacité thermique",
            "Densite": "Densité",
            "Module_Elasticite": "Module Elasticité",
            "Conductivite_thermique": "Conductivité thermique",
            "Masse_volumique": "Masse volumique",
            "Temperature_ebullition": "Température d'ébullition",
            "Limite_elasticite": "Limite d'élasticité",
            "Resistance_traction": "Résistance à la traction",
            "Allongement_rupture": "Allongement à la rupture",
            "Recyclable": "Recyclable",
            "Resistance_corrosion": "Résistance à la corrosion",
            "Prix": "Prix"
        }

        self.create_property_widgets()

        self.label_titre = tk.Label(self, text="Propriétés des Matériaux", font=("Helvetica", 16, "bold"))
        self.label_titre.grid(row=0, column=0, columnspan=5, pady=10)

        self.result_text = tk.Text(self, height=10, width=50)
        self.result_text.grid(row=3, column=0, columnspan=5, padx=10, pady=10)

        # Frame pour les boutons Ajouter et OK
        self.frame_buttons = tk.Frame(self)
        self.frame_buttons.grid(row=2, column=0, columnspan=5, padx=10, pady=5)

        self.add_button = tk.Button(self.frame_buttons, text="Ajouter propriété", command=self.add_spinboxe)
        self.add_button.grid(row=2, column=0, padx=5, pady=10)

        self.search_button = tk.Button(self.frame_buttons, text="Rechercher", command=self.search_materials)
        self.search_button.grid(row=2, column=1, padx=5, pady=10)

        self.calc_mass_button = None
        self.calc_price_button = None
        self.hist_button = None

    def create_property_widgets(self):
        self.spinboxes = []
        self.entries_min = []
        self.entries_max = []
        self.nombre_proprietes = 0

        self.frame_prop = tk.Frame(self)
        self.frame_prop.grid(row=1, column=0, columnspan=5, padx=10, pady=5)

        self.add_spinboxe()

    def add_spinboxe(self):
        i = self.nombre_proprietes + 1

        spinbox = ttk.Combobox(self.frame_prop, values=list(self.properties.keys()), width=15)
        spinbox.grid(row=i, column=0, padx=5, pady=5)
        self.spinboxes.append(spinbox)

        label_min = tk.Label(self.frame_prop, text="Valeur Min:")
        label_min.grid(row=i, column=1, padx=5, pady=5)

        entry_min = tk.Entry(self.frame_prop)
        entry_min.grid(row=i, column=2, padx=5, pady=5)
        self.entries_min.append(entry_min)

        label_max = tk.Label(self.frame_prop, text="Valeur Max:")
        label_max.grid(row=i, column=3, padx=5, pady=5)

        entry_max = tk.Entry(self.frame_prop)
        entry_max.grid(row=i, column=4, padx=5, pady=5)
        self.entries_max.append(entry_max)

        self.nombre_proprietes += 1

    def search_materials(self):
        valeurs_min = [entry.get() for entry in self.entries_min]
        valeurs_max = [entry.get() for entry in self.entries_max]
        proprietes_selectionnees = [spinbox.get() for spinbox in self.spinboxes]
        
        properties = {}
        for i in range(len(proprietes_selectionnees)):
            if valeurs_min[i] and valeurs_max[i]:
                try:
                    properties[proprietes_selectionnees[i]] = [float(valeurs_min[i]), float(valeurs_max[i])]
                    if float(valeurs_min[i]) > float(valeurs_max[i]):
                        messagebox.showerror("Erreur de Valeurs", f"Pour {proprietes_selectionnees[i]}, la valeur minimale doit être inférieure ou égale à la valeur maximale.")
                        return
                except ValueError:
                    messagebox.showerror("Erreur", "Entrer des valeurs numériques.")
                    return
        if properties:
            materials = Material.retrieve_material_by_properties(properties)
            self.display_results(materials)
            if materials:
                self.create_mass_button()
                self.create_price_button(materials)
                self.create_hist_button()
        else:
            messagebox.showinfo("Information", "Veuillez saisir des valeurs pour au moins une propriété.")
    
    def display_results(self, materials):
        self.result_text.delete(1.0, tk.END)
        if materials:
            for material in materials:
                self.result_text.insert(tk.END, f"ID: {material.id}, Nom: {material.name}\n")
                self.result_text.insert(tk.END, "Propriétés:\n")
                for prop_name, value in material.properties.items():
                    self.result_text.insert(tk.END, f"{prop_name}: {value}\n")
                self.result_text.insert(tk.END, "\n")
        else:
            self.result_text.insert(tk.END, "Aucun matériau trouvé avec ces critères de recherche.")

    def create_mass_button(self):
        self.calc_mass_button = tk.Button(self.frame_buttons, text="Calculer la Masse", command=self.calculate_mass)
        self.calc_mass_button.grid(row=2, column=2, padx=5, pady=10)

    def calculate_mass(self):
        volume = simpledialog.askfloat("Calcul de Masse", "Entrez le volume en m³ pour tous les matériaux trouvés :")
        if volume is not None:
            self.result_text.insert(tk.END, "\nMasse Calculée pour le Volume donné:\n")
            materials = self.retrieve_materials()
            if materials:
                for material in materials:
                    density = material.properties['Masse_volumique']
                    mass = volume * density
                    self.result_text.insert(tk.END, f"Matériau: {material.name}, Masse: {mass} kg\n")

    def retrieve_materials(self):
        valeurs_min = [entry.get() for entry in self.entries_min]
        valeurs_max = [entry.get() for entry in self.entries_max]
        proprietes_selectionnees = [spinbox.get() for spinbox in self.spinboxes]
        
        properties = {}
        for i in range(len(proprietes_selectionnees)):
            if valeurs_min[i] and valeurs_max[i]:
                try:
                    properties[proprietes_selectionnees[i]] = [float(valeurs_min[i]), float(valeurs_max[i])]
                except ValueError:
                    messagebox.showerror("Erreur", "Entrer des valeurs numériques.")
        
        if properties:
            return Material.retrieve_material_by_properties(properties)
        else:
            return None

    def create_price_button(self, materials):
        self.calc_price_button = tk.Button(self.frame_buttons, text="Calculer le Prix", command=lambda: self.calculate_price(materials))
        self.calc_price_button.grid(row=2, column=3, padx=5, pady=10)

    def calculate_price(self, materials):
        self.result_text.insert(tk.END, "\nPrix Calculé pour chaque Matériau:\n")
        for material in materials:
            mass = material.properties['Masse_volumique']
            price_per_ton = float(material.properties['Prix'])  # Prix par tonne
            price = mass * price_per_ton / 1000  # Conversion de la masse de kg à tonnes
            self.result_text.insert(tk.END, f"Matériau: {material.name}, Prix: {price} euros\n")

    def create_hist_button(self):
        options = list(self.properties.values())

        self.selected_property = tk.StringVar()
        self.selected_property.set(options[0])

        dropdown = ttk.OptionMenu(self.frame_buttons, self.selected_property, *options)
        dropdown.grid(row=2, column=4, padx=5, pady=10)

        self.hist_button = tk.Button(self.frame_buttons, text="Tracer Histogramme", command=self.plot_histogram)
        self.hist_button.grid(row=2, column=5, padx=5, pady=10)

    def plot_histogram(self):
        selected_property = list(self.properties.keys())[list(self.properties.values()).index(self.selected_property.get())]
        materials = self.retrieve_materials()
        if materials:
            values = [material.properties[selected_property] for material in materials if material.properties[selected_property] is not None]  # Filtrer les valeurs None
            if values:  # Vérifier si des valeurs non None sont disponibles
               plt.figure(figsize=(8, 6))
               plt.hist(values, bins=10, color='blue', edgecolor='black', alpha=0.7)
               plt.xlabel(selected_property)
               plt.ylabel('Nombre de Matériaux')
               plt.title(f'Histogramme de {self.selected_property.get()} des Matériaux')
               plt.grid(True)
               plt.show()
            else:
               messagebox.showinfo("Information", f"Aucune valeur disponible pour la propriété {self.selected_property.get()}.")
        else:
           messagebox.showinfo("Information", "Aucun matériau trouvé avec ces critères de recherche.")


class InverseSearchApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Recherche Inverse de Matériaux")

        self.label = tk.Label(self, text="Sélectionnez un matériau:", font=("Helvetica", 16, "bold"))
        self.label.pack(pady=10)

        self.materials = [
            "verre sodocalcique", "Acier doux", "Acier inoxydable duplex", "Acier inoxydable martensitique",
            "Aérogel", "Aliminium", "Alliage zirconium-niobium", "Argon", "Brique réfractaire", "Bronze",
            "Caoutchouc", "Fer doux", "Fibre de carbone haute qualité", "Granit", "Laine de verre", "Laiton",
            "Le liège", "Nickel", "Polyéthylène", "Polypropylène", "polyurèthane", "Porcelaine",
            "verre borosilicate", "Zamak 3", "Zinc"
        ]

        self.combobox = ttk.Combobox(self, values=self.materials, width=30)
        self.combobox.pack(pady=10)

        self.search_button = tk.Button(self, text="Rechercher", command=self.search_material)
        self.search_button.pack(pady=10)

        self.result_text = tk.Text(self, height=10, width=50)
        self.result_text.pack(pady=10)

    def search_material(self):
        material_name = self.combobox.get()
        if material_name:
            material = Material.retrieve_material_by_name(material_name)
            if material:
                self.display_material_properties(material)
            else:
                messagebox.showinfo("Information", "Matériau non trouvé.")
        else:
            messagebox.showinfo("Information", "Veuillez sélectionner un matériau.")

    def display_material_properties(self, material):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"ID: {material.id}, Nom: {material.name}\n")
        self.result_text.insert(tk.END, "Propriétés:\n")
        for prop_name, value in material.properties.items():
            self.result_text.insert(tk.END, f"{prop_name}: {value}\n")
        self.result_text.insert(tk.END, "\n")

class MaterialAdditionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ajout de Matériau")

        self.properties = [
            "Materiaux","Durete", "Point_de_fusion", "Capacite_thermique", "Densite", "Module_Elasticite",
            "Conductivite_thermique", "Masse_volumique", "Temperature_ebullition", "Limite_elasticite",
            "Resistance_traction", "Allongement_rupture", "Recyclable", "Resistance_corrosion", "Prix"
        ]

        self.entries = {}

        self.label = tk.Label(self, text="Ajouter un Nouveau Matériau", font=("Helvetica", 16, "bold"))
        self.label.pack(pady=10)

        self.frame_entries = tk.Frame(self)
        self.frame_entries.pack(pady=10)

        for prop in self.properties:
            row_frame = tk.Frame(self.frame_entries)
            row_frame.pack()

            label = tk.Label(row_frame, text=prop.replace("_", " "))
            label.pack(side=tk.LEFT)

            entry = tk.Entry(row_frame)
            entry.pack(side=tk.LEFT)
            self.entries[prop] = entry

        self.add_button = tk.Button(self, text="Ajouter", command=self.add_material)
        self.add_button.pack(pady=10)

    def add_material(self):
        material_properties = {}
        for prop, entry in self.entries.items():
            value = entry.get().strip()
            if value:
                if prop == "Materiaux":
                    material_properties[prop] = value
                else:
                    try:
                        material_properties[prop] = float(value)
                    except ValueError:
                        messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides pour les propriétés.")
                        return
            else:
                material_properties[prop] = None

        if not material_properties["Materiaux"]:
            messagebox.showerror("Erreur", "Veuillez entrer un nom pour le matériau.")
            return
        elif all(value is None for prop, value in material_properties.items() if prop != "Materiaux"):
            messagebox.showerror("Erreur", "Veuillez entrer au moins une propriété pour le matériau.")
            return
        
        Material.add_material_to_db(material_properties)
        messagebox.showinfo("Information", "Matériau ajouté avec succès à la base de données.")

        for entry in self.entries.values():
            entry.delete(0, tk.END)

if __name__ == "__main__":
    MaterialSearchApp().mainloop()

