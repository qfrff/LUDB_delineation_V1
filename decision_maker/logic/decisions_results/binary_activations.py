from settings import POINTS_TYPES, POINTS_TYPES_COLORS
import matplotlib.pyplot as plt


class BinaryActivations:
    def __init__(self, net_activations, activations_t, type_of_point=POINTS_TYPES.QRS_PEAK, label=""):
        """
        Объект сцены, инкапсулирующий набор активаций бинарной сети
        Args:
            net_activations: (list) список активаций нейросети
            activations_t: (list) координаты (времена) этих активаций, в секундах
            type_of_point: на каком типе точек специализируется эта сеть
            label: (str) строчка c какисм-то пояснением, которая пойдет в лог
        """
        self.net_activations = net_activations
        self.activations_t = activations_t
        self.label = label
        self.type_of_point = type_of_point

    def draw(self, ax, y_max):
        """
        Отрисовка активаций
        Args:
            ax: на какой подрафиг рисовать
            y_max: (float) на какой множитель умножать активацию в точке,
                чтобы смасштаюировать активации с сигналом ЭКГ. Это нужно потому,
                что активации и сигнал имеют разные единицы измерения,
                 а мы хотим отрисовать их в одном графике.

        Returns:

        """
        color = POINTS_TYPES_COLORS[self.type_of_point]
        normed_activations = [self.net_activations[i] * y_max for i in range(len(self.net_activations))]
        # ax.plot(self.activations_t, normed_activations, color=color, label=self.label, alpha=0.5, linewidth=5)
        for i in range(len(self.net_activations)):
            activation = normed_activations[i]
            t = self.activations_t[i]
            ax.plot([t, t], [0, activation], color=color, alpha=0.1, linewidth=0.5,
                    label=self.label if i == 0 else None)


if __name__ == "__main__":
    from settings import LEADS_NAMES, FREQUENCY
    from datasets.LUDB_utils import get_some_test_patient_id, get_signal_by_id_and_lead_mV, get_LUDB_data
    from visualisation_utils import plot_lead_signal_to_ax
    import matplotlib.pyplot as plt
    import math

    # Рисуем сигнал
    LUDB_data = get_LUDB_data()
    patient_id = get_some_test_patient_id()
    lead_name = LEADS_NAMES.i
    signal_mV = get_signal_by_id_and_lead_mV(patient_id, lead_name=lead_name, LUDB_data=LUDB_data)
    fig, ax = plt.subplots()
    plot_lead_signal_to_ax(signal_mV=signal_mV, ax=ax)

    # Генерируем случайную серию "активаций"
    t = [i / FREQUENCY for i in range(len(signal_mV))]
    y_max = max(signal_mV)
    activations = [abs(math.sin(i)) for i in t]

    # Рисуем сгенерированные активации:
    binary_activations = BinaryActivations(net_activations=activations,
                                           activations_t=t,
                                           type_of_point=POINTS_TYPES.QRS_PEAK,
                                           label="тестовые активации")
    binary_activations.draw(ax, y_max=y_max)

    # показываем итог: сигнал и облако активаций поверх него
    ax.legend()
    plt.show()
