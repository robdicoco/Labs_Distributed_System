from dataclasses import dataclass
from typing import List


@dataclass
class Node:
    name: str
    clock: float  # tempo local em segundos


class BerkeleyMaster:
    def __init__(self, master: Node, nodes: List[Node], outlier_limit: float = 5.0):
        """
        :param master: nó mestre
        :param nodes: lista com todos os nós escravos
        :param outlier_limit: limite máximo de diferença em segundos
                              para considerar um nó na média
        """
        self.master = master
        self.nodes = nodes
        self.outlier_limit = outlier_limit

    def collect_times(self):
        """
        Mestre coleta os tempos de todos os nós.
        Em uma implementação real, isso seria feito por mensagens na rede.
        """
        times = [(self.master.name, self.master.clock)]
        for node in self.nodes:
            times.append((node.name, node.clock))
        return times

    def compute_adjustments(self):
        """
        Calcula os ajustes com base na média, ignorando outliers.
        Retorna:
        - média calculada
        - lista de nós válidos
        - lista de outliers
        - ajustes por nó
        """
        collected = self.collect_times()
        master_time = self.master.clock

        valid_nodes = []
        outliers = []

        # Calcula diferença em relação ao mestre
        for name, clock in collected:
            diff = clock - master_time
            if abs(diff) <= self.outlier_limit:
                valid_nodes.append((name, clock, diff))
            else:
                outliers.append((name, clock, diff))

        # Média dos relógios válidos
        avg_time = sum(clock for _, clock, _ in valid_nodes) / len(valid_nodes)

        # Ajuste necessário para cada nó válido
        adjustments = {}
        for name, clock, _ in valid_nodes:
            adjustments[name] = avg_time - clock

        return avg_time, valid_nodes, outliers, adjustments

    def synchronize(self):
        """
        Aplica os ajustes calculados aos nós válidos.
        """
        avg_time, valid_nodes, outliers, adjustments = self.compute_adjustments()

        # Ajusta mestre
        if self.master.name in adjustments:
            self.master.clock += adjustments[self.master.name]

        # Ajusta escravos
        for node in self.nodes:
            if node.name in adjustments:
                node.clock += adjustments[node.name]

        return avg_time, valid_nodes, outliers, adjustments


def print_clocks(title: str, master: Node, nodes: List[Node]):
    print(f"\n{title}")
    print("-" * 40)
    print(f"{master.name}: {master.clock:.2f}")
    for node in nodes:
        print(f"{node.name}: {node.clock:.2f}")


def main():
    # Exemplo de tempos locais
    master = Node("Mestre", 100.0)
    nodes = [
        Node("Nó 1", 102.0),
        Node("Nó 2", 98.0),
        Node("Nó 3", 101.0),
        Node("Nó 4", 150.0),  # outlier
    ]

    berkeley = BerkeleyMaster(master, nodes, outlier_limit=5.0)

    print_clocks("Relógios antes da sincronização", master, nodes)

    avg_time, valid_nodes, outliers, adjustments = berkeley.synchronize()

    print("\nColeta de tempos válidos:")
    for name, clock, diff in valid_nodes:
        print(f"{name}: tempo={clock:.2f}, diferença para o mestre={diff:+.2f}s")

    print("\nOutliers ignorados:")
    if outliers:
        for name, clock, diff in outliers:
            print(f"{name}: tempo={clock:.2f}, diferença para o mestre={diff:+.2f}s")
    else:
        print("Nenhum")

    print(f"\nMédia calculada: {avg_time:.2f}")

    print("\nAjustes aplicados:")
    for name, adjustment in adjustments.items():
        print(f"{name}: ajuste {adjustment:+.2f}s")

    print_clocks("Relógios depois da sincronização", master, nodes)


if __name__ == "__main__":
    main()