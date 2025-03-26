from delineation import DelineationOnePoint
from datasets.LUDB_utils import get_LUDB_data, get_test_and_train_ids, get_signal_by_id_and_lead_mV, get_one_lead_delineation_by_patient_id
from settings import LEADS_NAMES, POINTS_TYPES, POINTS_TYPES_COLORS, FREQUENCY
from visualisation_utils.plot_one_lead_signal import plot_lead_signal_to_ax
import matplotlib.pyplot as plt
import numpy as np

class PatientContainer:
    
    def __init__(self, true_delinations, our_delineations, signals_list_mV, leads_names_list, patient_id='-1'):
        """
        сигнал отведений пациента + правильная разметка + наша разметка.
        это три вещи, нужные, чтоб для данного пациента наглядтно посмотреть в GUI, насколько хорошо наша модель его разметила.
        класс является служебным для GUI_DekineationComparsion.
        Args:
            true_delinations: список объектов DelineationOnePoint - правильная разметка. Список может содержать от 1 до 12x9 элементов
            our_delineations: список объектов DelineationOnePoint - наша разметка. Список может содержать от 1 до 12x9 элементов
            signals_list_mV: сигналы нескольких отведений
            leads_names_list: имена этих отведений, взятых из LEADS_NAMES
            patient_id: id пациента в датасете
        """
        # реализация хранения данных пациента: сигналы, разметки и id
        self.true_delinations = true_delinations
        self.our_delineations = our_delineations
        self.signals_list_mV = signals_list_mV
        self.leads_names_list = leads_names_list
        self.patient_id = patient_id

class GUI_DelineationComparison:
    """
    Листалка для сравнения разметки с использованием готовой миллиметровки из plot_one_lead_signal.py
    """
    def __init__(self, patient_containers):
        self.patient_containers = patient_containers
        self.current_patient_index = 0
        self.fig, self.ax = plt.subplots(
            len(self.patient_containers[0].leads_names_list), 
            1, 
            figsize=(15, 10)
        )
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.update_plot()

    def _plot_delineation(self, ax, signal, points, is_true_delineation=True):
        """Отрисовка разметки с цветами по типам точек"""
        x_values = np.arange(0, len(signal)) / FREQUENCY  # Для совместимости с plot_lead_signal_to_ax
        
        for point in points:
            color = POINTS_TYPES_COLORS[point.point_type]
            if is_true_delineation:
                # Истинная разметка - точки
                ax.scatter(
                    np.array(point.delin_coords) / FREQUENCY,  # Конвертируем в секунды
                    [signal[int(coord)] for coord in point.delin_coords],
                    color=color, 
                    label=f'True {point.point_type}', 
                    marker='o', 
                    s=50, 
                    zorder=5
                )
            else:
                # Наша разметка - вертикальные линии
                for coord in point.delin_coords:
                    ax.axvline(
                        x=coord / FREQUENCY,  # Конвертируем в секунды
                        color=color, 
                        linestyle='--', 
                        linewidth=1,
                        label=f'Our {point.point_type}', 
                        alpha=0.7, 
                        zorder=4
                    )

    def update_plot(self):
        patient = self.patient_containers[self.current_patient_index]
        
        for i, (lead_name, signal) in enumerate(zip(patient.leads_names_list, patient.signals_list_mV)):
            self.ax[i].clear()
            
            # Используем готовый метод для миллиметровки и сигнала
            plot_lead_signal_to_ax(signal_mV=signal, ax=self.ax[i])
            
            # Отрисовка разметки
            self._plot_delineation(self.ax[i], signal, patient.true_delinations, is_true_delineation=True)
            self._plot_delineation(self.ax[i], signal, patient.our_delineations, is_true_delineation=False)
            
            # Настройка легенды и заголовка
            handles, labels = self.ax[i].get_legend_handles_labels()
            unique_labels = dict(zip(labels, handles))  # Убираем дубли
            self.ax[i].legend(
                unique_labels.values(), 
                unique_labels.keys(), 
                loc='upper right'
            )
            self.ax[i].set_title(f'Patient {patient.patient_id}, Lead {lead_name}')

        plt.tight_layout()
        plt.draw()

    def on_key_press(self, event):

        # обработка нажатий клавиш для листания пациентов
        if event.key == 'right':
            self.current_patient_index = (self.current_patient_index + 1) % len(self.patient_containers)
            self.update_plot()
        elif event.key == 'left':
            self.current_patient_index = (self.current_patient_index - 1) % len(self.patient_containers)
            self.update_plot()

if __name__ == "__main__":

    # загрузка данных LUDB
    LUDB_data = get_LUDB_data()
    test_patient_ids, _ = get_test_and_train_ids(LUDB_data)

    # выбор первых нескольких пациентов и интересующих отведений и типов точек
    patient_ids = test_patient_ids[0:10]  # первые несколько пациентов
    lead_names = [LEADS_NAMES.i, LEADS_NAMES.ii, LEADS_NAMES.iii]
    points_types = [POINTS_TYPES.QRS_PEAK, POINTS_TYPES.QRS_END]

    patient_containers = []

    # создание контейнеров для каждого пациента
    for patient_id in patient_ids:
        # получение сигналов интересующих отведений пациента
        signals_list_mV = []
        for lead_name in lead_names:
            signals_list_mV.append(get_signal_by_id_and_lead_mV(patient_id, lead_name=lead_name, LUDB_data=LUDB_data))

        # создание правильной и случайной (нашей) разметки для пациента
        true_delinations = []
        our_delineations = []
        for lead_name in lead_names:
            for point_type in points_types:

                # истинная разметка
                point_delineation = get_one_lead_delineation_by_patient_id(patient_id, LUDB_data, lead_name=lead_name, point_type=point_type)
                true_delineation_obj = DelineationOnePoint(point_type, lead_name, delin_coords=point_delineation, delin_weights=None)
                true_delinations.append(true_delineation_obj)

                # случайная разметка (пример для теста GUI)
                point_delineation_random = np.random.randint(0, len(signals_list_mV[0]), 5)  # случайные координаты
                delin_weights_random = np.random.rand(5)  # случайные веса
                our_delineation_obj = DelineationOnePoint(point_type, lead_name, delin_coords=point_delineation_random, delin_weights=delin_weights_random)
                our_delineations.append(our_delineation_obj)

        # создание контейнера для пациента и добавление его в список
        container = PatientContainer(true_delinations, our_delineations, signals_list_mV, lead_names, patient_id=str(patient_id))
        patient_containers.append(container)

    # создание и запуск листалки
    gui = GUI_DelineationComparison(patient_containers=patient_containers)
    plt.show()