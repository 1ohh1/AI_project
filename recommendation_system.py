import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


# Generar productos sintéticos con tres características y una categoría.
rng = np.random.default_rng(42)
categorias = ["Económico", "Estándar", "Premium"]
centros = [(25, 3.2, 35), (60, 4.0, 60), (100, 4.7, 85)]
filas = []

for categoria, centro in zip(categorias, centros):
	muestras = rng.normal(loc=centro, scale=(8, 0.35, 10), size=(100, 3))
	for muestra in muestras:
		filas.append((*muestra, categoria))

productos = pd.DataFrame(
	filas, columns=["precio", "valoracion", "popularidad", "categoria"]
)
caracteristicas = ["precio", "valoracion", "popularidad"]
X = productos[caracteristicas]
y = productos["categoria"]

# Dividir los datos de forma estratificada para conservar las categorías.
X_train, X_test, y_train, y_test = train_test_split(
	X, y, test_size=0.2, random_state=42, stratify=y
)

# Escalar las características antes de calcular las distancias KNN.
modelo = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5))
modelo.fit(X_train, y_train)
print(f"Precisión del modelo: {accuracy_score(y_test, modelo.predict(X_test)):.2%}")


def recommend(precio, valoracion, popularidad, cantidad=5):
	"""Predice una categoría y devuelve productos cercanos de esa categoría."""
	consulta = pd.DataFrame(
		[[precio, valoracion, popularidad]], columns=caracteristicas
	)
	categoria = modelo.predict(consulta)[0]

	# Ordenar los productos de la categoría predicha por distancia normalizada.
	candidatos = productos.loc[productos["categoria"] == categoria].copy()
	escalador = modelo.named_steps["standardscaler"]
	consulta_escalada = escalador.transform(consulta)
	candidatos_escalados = escalador.transform(candidatos[caracteristicas])
	candidatos["distancia"] = np.linalg.norm(
		candidatos_escalados - consulta_escalada, axis=1
	)
	return candidatos.nsmallest(cantidad, "distancia").drop(columns="distancia")


# Ejemplo de uso.
print("Recomendaciones para un producto de precio 58, valoración 4.1 y popularidad 62:")
print(recommend(precio=58, valoracion=4.1, popularidad=62))
