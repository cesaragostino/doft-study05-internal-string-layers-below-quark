import matplotlib.pyplot as plt
import networkx as nx

def plot_combined_cosmic_map():
    # Configuración de la figura
    plt.figure(figsize=(16, 12))
    
    # === SUBPLOT 1: DOFT (Arriba) ===
    plt.subplot(2, 1, 1)
    G1 = nx.DiGraph()
    
    # Nodos DOFT
    doft_nodes = [
        "Vacío + Memoria (τ)\n(Engine Core)", 
        "Ola 1: Ladrillos\n(Q=3, S1=2, S2=5)", 
        "Ola 2: Paredes\n(Bariones Estables)", 
        "Ola 3: Edificio\n(Núcleos/Átomos)"
    ]
    G1.add_nodes_from(doft_nodes)
    G1.add_edges_from([(doft_nodes[i], doft_nodes[i+1]) for i in range(len(doft_nodes)-1)])
    
    pos1 = {
        doft_nodes[0]: (0, 0),
        doft_nodes[1]: (2, 0),
        doft_nodes[2]: (4, 0),
        doft_nodes[3]: (6, 0)
    }
    
    # Dibujar DOFT
    nx.draw_networkx_nodes(G1, pos1, node_color='#87CEFA', node_size=5000, node_shape='s', alpha=0.9)
    nx.draw_networkx_labels(G1, pos1, font_size=10, font_weight='bold')
    nx.draw_networkx_edges(G1, pos1, edge_color='gray', arrows=True, arrowsize=30, width=2)
    plt.title("TU MODELO (DOFT): Estructura basada en Memoria y Primos", fontsize=14, pad=20)
    plt.axis('off')
    
    # Anotaciones de Primos en DOFT
    plt.text(1, 0.3, "Salto Primo n=3 (Triángulo)\nOrigen de la Forma", ha='center', color='darkblue', fontsize=9, style='italic')
    plt.text(3, 0.3, "Salto Primo n=2 (Dualidad)\nTensión/Pegamento", ha='center', color='darkblue', fontsize=9, style='italic')
    plt.text(5, 0.3, "Salto Primo n=5 (Cierre)\nEstabilidad/Piel", ha='center', color='darkblue', fontsize=9, style='italic')

    # === SUBPLOT 2: SM + CUERDAS (Abajo) ===
    plt.subplot(2, 1, 2)
    G2 = nx.DiGraph()
    
    # Nodos SM/Cuerdas
    sm_nodes = [
        "Vacío Geométrico 10D\n(Calabi-Yau)", 
        "Modos de Vibración\n(Quarks/Gluones)", 
        "Confinamiento (QCD)\n(Hadronización)", 
        "Materia Nuclear\n(Tabla Periódica)"
    ]
    G2.add_nodes_from(sm_nodes)
    G2.add_edges_from([(sm_nodes[i], sm_nodes[i+1]) for i in range(len(sm_nodes)-1)])
    
    pos2 = {
        sm_nodes[0]: (0, 0),
        sm_nodes[1]: (2, 0),
        sm_nodes[2]: (4, 0),
        sm_nodes[3]: (6, 0)
    }
    
    # Dibujar SM
    nx.draw_networkx_nodes(G2, pos2, node_color='#D8BFD8', node_size=5000, node_shape='o', alpha=0.9)
    nx.draw_networkx_labels(G2, pos2, font_size=10, font_weight='bold')
    nx.draw_networkx_edges(G2, pos2, edge_color='gray', arrows=True, arrowsize=30, width=2)
    plt.title("FÍSICA OFICIAL (Cuerdas + SM): Estructura basada en Geometría", fontsize=14, pad=20)
    plt.axis('off')

    # === PUENTES VISUALES (Conectando conceptualmente) ===
    # Dibujamos líneas que cruzan de arriba a abajo simulando los "Puentes"
    # Esto es un truco visual usando coordenadas relativas de la figura
    
    plt.figtext(0.5, 0.5, "⬇ LOS PUENTES DE RESONANCIA ⬇", ha='center', fontsize=16, weight='bold', color='gold', bbox=dict(facecolor='black', alpha=0.8))

    # Puente 1: Origen
    plt.annotate("", xy=(0.15, 0.1), xycoords='figure fraction', xytext=(0.15, 0.9), textcoords='figure fraction',
                 arrowprops=dict(arrowstyle="<->", color="gold", lw=3, linestyle="--"))
    plt.figtext(0.16, 0.5, "GEOMETRÍA vs MEMORIA\n(Son equivalentes)", color="darkgoldenrod", fontsize=10, rotation=90, va='center')

    # Puente 2: Fase 1 (3 modos)
    plt.annotate("", xy=(0.38, 0.1), xycoords='figure fraction', xytext=(0.38, 0.9), textcoords='figure fraction',
                 arrowprops=dict(arrowstyle="<->", color="gold", lw=3, linestyle="--"))
    
    # Puente 3: Fase 2 (Cierre)
    plt.annotate("", xy=(0.62, 0.1), xycoords='figure fraction', xytext=(0.62, 0.9), textcoords='figure fraction',
                 arrowprops=dict(arrowstyle="<->", color="gold", lw=3, linestyle="--"))

    plt.tight_layout()
    plt.savefig('doft_vs_sm_primos.png')
    print("Imagen 'doft_vs_sm_primos.png' generada con éxito.")

if __name__ == "__main__":
    try:
        plot_combined_cosmic_map()
    except Exception as e:
        print(f"Error generando imagen: {e}")